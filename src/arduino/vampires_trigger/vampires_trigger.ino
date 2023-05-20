
// Here's some constants up front for easy retrieval
#define BAUDRATE 115200
#define TIMEOUT 500 // ms
/* If true, turns LEDs on for visual debugging. The read "L" LED
 will turn on or off when the FLC is enabled/disable. The NeoPixel
 LED will be red when the trigger loop is disabled and green when
 the trigger loop is enabled. */
#define DEBUG_MODE true
// Pin mapping
#define CAMERA_TRIGGER_PIN 12
#define CAMERA_ONE_READY 10
#define CAMERA_TWO_READY 6
#define FLC_TRIGGER_PIN 8
#define FLC_CONTROL_PIN 4

#if DEBUG_MODE
#include <Adafruit_NeoPixel.h>
#define LED_PIN 13
#define NEOPIXEL_PIN 40
#define NEOPIXEL_BRIGHTNESS 50
Adafruit_NeoPixel strip(1, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);
#endif

// This way of testing works around micros() overflowing
#define ROBUST_DELAY(target) while (micros() - last_loop_finish < target) continue

// FYI C people: Arduino int is 16bit, long is 32 bits.
// We use unsigned long for everything time-related in microseconds.
// FLC only works for integration times < 1 second
const unsigned long max_flc_integration_time = 1000000; // us

// global variable initialization
unsigned int cmd_code;
unsigned long last_loop_finish;
// settings
unsigned long integration_time;
unsigned long pulse_width;
unsigned long flc_offset;
unsigned int trigger_mode;
bool sweep_mode;
bool loop_enabled;
bool flc_enabled;

/*
    Setup function runs every USB reset. Note: this includes when a serial
    DTR low signal is sent, which can be the case for some terminal emulators.
*/
void setup()
{    // variable resets
    sweep_mode = false;
    loop_enabled = false;
    flc_enabled = true;
    pulse_width = 10; // us
    flc_offset = 20; // us

    // set pin modes
    pinMode(CAMERA_TRIGGER_PIN, OUTPUT);
    pinMode(FLC_TRIGGER_PIN, OUTPUT);
    pinMode(FLC_CONTROL_PIN, OUTPUT);
    pinMode(CAMERA_ONE_READY, INPUT);
    pinMode(CAMERA_TWO_READY, INPUT);

    // reset outputs to low
    digitalWrite(CAMERA_TRIGGER_PIN, LOW);
    digitalWrite(FLC_TRIGGER_PIN, LOW);
    digitalWrite(FLC_CONTROL_PIN, LOW);

#if DEBUG_MODE
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, flc_enabled);
    // neopixel setup
    strip.begin();
    strip.setPixelColor(0, 0, 0, NEOPIXEL_BRIGHTNESS);
    strip.show();
#endif
    // start serial connection
    Serial.setTimeout(TIMEOUT);
    Serial.begin(BAUDRATE);
}

/* Main arduino loop */
void loop()
{
  // handle serial inputs
  if (Serial.available()) handle_serial();
  // if FLC is enabled use loop with offsets
  if (loop_enabled && flc_enabled) trigger_loop_flc();
  // otherwise use simple loop
  else if (loop_enabled) trigger_loop_noflc();
}

/*
    This function triggers in two passes, first with the FLC off
    then again with the FLC on. Therefore one micro-controller loop is
    two exposures.

    The first exposure will not start until `flc_offset` time has passed.
    This is so there is enough time for the FLC to fully relax before beginning
    the exposure.

    After the completion of the first exposure, the FLC is triggered. The second
    exposure will not start until `flc_offset` has passed, ensuring the FLC
    has enough time to fully activate. At the end of this exposure the FLC LOW
    signal is instantly sent to assure as close to a 50% duty cycle as possible,
    which is *necessary* for FLCs.

    If sweep mode is enabled, the FLC offset will be incremented by 1 us in this loop.
    This allows testing
*/
void trigger_loop_flc() {
    // First exposure FLC is relaxed
    digitalWrite(FLC_TRIGGER_PIN, LOW);
    ROBUST_DELAY(flc_offset);
    digitalWrite(CAMERA_TRIGGER_PIN, HIGH);
    ROBUST_DELAY(flc_offset + pulse_width);
    digitalWrite(CAMERA_TRIGGER_PIN, LOW);
    // ROBUST_DELAY(dt3);
    while (!digitalRead(CAMERA_ONE_READY) || !digitalRead(CAMERA_TWO_READY)) continue;
    last_loop_finish = micros();
    // Second exposure FLC is active
    digitalWrite(FLC_TRIGGER_PIN, HIGH);
    ROBUST_DELAY(flc_offset);
    digitalWrite(CAMERA_TRIGGER_PIN, HIGH);
    ROBUST_DELAY(flc_offset + pulse_width);
    digitalWrite(CAMERA_TRIGGER_PIN, LOW);
    for (integration_time = 0; integration_time < max_flc_integration_time, integration_time += micros();) {
        if (!digitalRead(CAMERA_ONE_READY) || !digitalRead(CAMERA_TWO_READY)) break;
    }
    // Immediately shut off FLC to maintain DC balance
    digitalWrite(FLC_TRIGGER_PIN, LOW);
    if (!digitalRead(CAMERA_ONE_READY) || !digitalRead(CAMERA_TWO_READY)) {
        loop_enabled = false;
    }
    // ROBUST_DELAY(dt6);

    // We take it that way, rather than calling micros() again. Otherwise
    // the loop will be a teensy tiny bit longer than 2 * integration_time.
    last_loop_finish = micros();

    // Sweep mode
    // if (sweep_mode) {
    //     ++flc_offset;
    //     if (flc_offset + pulse_width == integration_time) {
    //         flc_offset = 0;
    //     }
    // }
}

/*
    This loop is much simpler since the FLC trigger timing can be ignored.
    Here each arduino loop comprises a single camera trigger pulse.
*/
void trigger_loop_noflc() {
    digitalWrite(CAMERA_TRIGGER_PIN, HIGH);
    ROBUST_DELAY(pulse_width);
    digitalWrite(CAMERA_TRIGGER_PIN, LOW);
    while (!digitalRead(CAMERA_ONE_READY) || !digitalRead(CAMERA_TWO_READY)) continue;
    last_loop_finish = micros();
}

/*
    Parse the input serial command, which is documented here.

    <cmd_number> [<args>...]\n

Note: sending serial commands happens in-between exposures, so this
should *in theory* not disrupt a running trigger loop. To be tested.

Commands:
    0 - GET
        This command returns the settings for the current loop:
        (loop_enabled, integration_time, pulse_width, flc_offset, trigger_mode)
    1 - SET
        This command will update the loop settings from the provided values
        (integration_time_us, pulse_width_us, flc_offset_us, trigger_mode)
        Note that trigger mode is an integer whose LSB determines whether
        the FLC is enabled and whose 2nd bit determines whether sweep mode
        is enabled (see trigger_loop_flc for more details about sweep mode)
    2 - DISABLE
        This command will disable the trigger loop.
    3 - ENABLE
        This command will enable the trigger loop.
*/
void handle_serial() {
    cmd_code = Serial.parseInt();
    switch (cmd_code) {
        case 0: // GET
            get();
            Serial.println("OK");
            break;
        case 1: // SET
            // set parameters
            // pulse width (us), flc offset (us), trigger mode
            set(Serial.parseInt(), Serial.parseInt(), Serial.parseInt());
            Serial.println("OK");
            // reset loop
            prepareLoop();
            break;
        case 2: // DISABLE
            loop_enabled = false;
            Serial.println("OK");
#if DEBUG_MODE
            // set neopixel to red
            strip.setPixelColor(0, NEOPIXEL_BRIGHTNESS, 0, 0);
            strip.show();
#endif
            break;
        case 3: // ENABLE
            prepareLoop();
            loop_enabled = true;
            Serial.println("OK");
#if DEBUG_MODE
            // set neopixel to green
            strip.setPixelColor(0, 0, NEOPIXEL_BRIGHTNESS, 0);
            strip.show();
#endif
            break;
        default:
            Serial.println("ERROR - invalid command");
            break;
    }
    // flush stream in case there's any leftover data
    Serial.flush();
}

void get() {
    Serial.print(loop_enabled);
    Serial.print(" ");
    Serial.print(pulse_width);
    Serial.print(" ");
    Serial.print(flc_offset);
    Serial.print(" ");
    Serial.println(trigger_mode);
}

void set(int _pulse_width, int _flc_offset, int _trigger_mode) {
    // argument checking
    if (_flc_offset < 0 || _flc_offset > 1000) {
        Serial.println("ERROR - invalid FLC offset: must be between 0 and 1000");
        return;
    }
    // set global variables
    pulse_width = _pulse_width;
    flc_offset = _flc_offset;
    trigger_mode = _trigger_mode;
    // `trigger_mode` LSB is FLC enable
    flc_enabled = trigger_mode & 0x1;
    digitalWrite(FLC_CONTROL_PIN, flc_enabled);
#if DEBUG_MODE
    digitalWrite(LED_PIN, flc_enabled);
#endif

    // 'trigger_mode' 2nd bit is sweep mode enable
    sweep_mode = trigger_mode & 0x2;
}

void prepareLoop() {
    // Compute values for loop
    last_loop_finish = micros();
}
