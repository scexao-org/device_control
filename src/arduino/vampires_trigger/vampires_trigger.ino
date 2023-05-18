
// Here's some constants up front for easy retrieval
#define BAUDRATE 115200
#define TIMEOUT 500 // ms
/* If true, turns LEDs on for visual debugging. The read "L" LED
 will turn on or off when the FLC is enabled/disable. The NeoPixel
 LED will be red when the trigger loop is disabled and green when
 the trigger loop is enabled. */
#define DEBUG_MODE true
// Pin mapping
#define FLC_CONTROL_PIN 4
#define FLC_TRIGGER_PIN 6
#define CAMERA_TRIGGER_PIN 8
#define AUX_PIN_A -1 // unused dig I/O pin
#define AUX_PIN_B -1 // unused dig I/O pin
#define AUX_PIN_C -1 // unused dig I/O pin

#if DEBUG_MODE
#include <Adafruit_NeoPixel.h>
#define LED_PIN 13
#define NEOPIXEL_PIN 40
#define NEOPIXEL_BRIGHTNESS 50
Adafruit_NeoPixel strip(1, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);
#endif

#define ROBUST_DELAY(target) while (micros() - last_loop_finish < target) continue

// FYI C people: Arduino int is 16bit, long is 32 bits.
// We use unsigned long for everything time-related in microseconds.
const unsigned long max_integration_time = 1600000000; // us
// FLC only works for integration times < 1 second
const unsigned long max_flc_integration_time = 1000000; // us
// The time to read a 4 of horizontal lines (which is the minimum)
// TODO is this the readout time or integration time 🤔
const unsigned long min_integration_time = 80; // us

// global variable initialization
unsigned int cmd_code;
unsigned long last_loop_finish;
unsigned long last_reset;
unsigned long dt1;
unsigned long dt2;
unsigned long dt3;
unsigned long dt4;
unsigned long dt5;
unsigned long dt6;
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
    integration_time = min_integration_time;
    pulse_width = 10; // us
    flc_offset = 20; // us

    // set pin modes to output
    pinMode(CAMERA_TRIGGER_PIN, OUTPUT);
    pinMode(FLC_TRIGGER_PIN, OUTPUT);
    pinMode(FLC_CONTROL_PIN, OUTPUT);

    // reset outputs to low
    digitalWrite(CAMERA_TRIGGER_PIN, LOW);
    digitalWrite(FLC_TRIGGER_PIN, LOW);
    digitalWrite(FLC_CONTROL_PIN, LOW);

#if DEBUG_MODE
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, flc_enabled);
    // neopixel setup
    strip.begin();
    strip.setPixelColor(0, NEOPIXEL_BRIGHTNESS, 0, 0);
    strip.show();
#endif
    // start serial connection
    Serial.setTimeout(TIMEOUT);
    Serial.begin(BAUDRATE);

    // reset timer
    last_reset = micros();
}

/* Main arduino loop */
void loop()
{
  // handle serial inputs
  if (Serial.available()) handle_serial();
  // if FLC is enabled use loop with offsets
  if (loop_enabled && flc_enabled) trigger_loop_flc();
  // otherwise use simple loop
  else if (loop_enabled) trigger_loop_noflc()
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
    // This way of testing works around micros() overflowing
    ROBUST_DELAY(dt1);
    digitalWrite(CAMERA_TRIGGER_PIN, HIGH);
    ROBUST_DELAY(dt2);
    digitalWrite(CAMERA_TRIGGER_PIN, LOW);
    ROBUST_DELAY(dt3);

    // Second exposure FLC is active
    digitalWrite(FLC_TRIGGER_PIN, HIGH);
    ROBUST_DELAY(dt4);
    digitalWrite(CAMERA_TRIGGER_PIN, HIGH);
    ROBUST_DELAY(dt5);
    digitalWrite(CAMERA_TRIGGER_PIN, LOW);
    ROBUST_DELAY(dt6);
    // Immediately shut off FLC to maintain DC balance
    digitalWrite(FLC_TRIGGER_PIN, LOW);

    // We take it that way, rather than calling micros() again. Otherwise
    // the loop will be a teensy tiny bit longer than 2 * integration_time.
    last_loop_finish += dt6;

    // Sweep mode
    if (sweep_mode) {
        ++flc_offset;
        if (flc_offset + pulse_width == integration_time) {
            flc_offset = 0;
        }
    }
}

/*
    This loop is much simpler since the FLC trigger timing can be ignored.
    Here each arduino loop comprises a single camera trigger pulse.
*/
void trigger_loop_noflc() {
    digitalWrite(CAMERA_TRIGGER_PIN, HIGH);
    ROBUST_DELAY(pulse_width);
    digitalWrite(CAMERA_TRIGGER_PIN, LOW);
    ROBUST_DELAY(integration_time);
    // We take it that way, rather than calling micros() again. Otherwise
    // the loop will be a teensy tiny bit longer than 2 * integration_time.
    last_loop_finish += integration_time;
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
        is enabled (see trigger_loop_flc for more details)
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
            break;
        case 1: // SET
            // set parameters
            // integration time (us), pulse width (us), flc offset (us), trigger mode
            set(Serial.parseInt(), Serial.parseInt(), Serial.parseInt(), Serial.parseInt());
            // reset loop
            prepareLoop();
            break;
        case 2: // DISABLE
            loop_enabled = false;
#if DEBUG_MODE
            // set neopixel to red
            strip.setPixelColor(0, NEOPIXEL_BRIGHTNESS, 0, 0);
            strip.show();
#endif
            break;
        case 3: // ENABLE
            prepareLoop();
            loop_enabled = true;
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
    Serial.print(integration_time);
    Serial.print(" ");
    Serial.print(pulse_width);
    Serial.print(" ");
    Serial.print(flc_offset);
    Serial.print(" ");
    Serial.println(trigger_mode);
}

void set(int _integration_time, int _pulse_width, int _flc_offset, int _trigger_mode) {
    // argument checking
    if (_integration_time > max_integration_time) {
        Serial.println("ERROR - frequency too low.");
        return;
    } else if (_integration_time < min_integration_time) {
        Serial.println("ERROR - frequency too high");
        return;
    } else if (_flc_offset < 0 || _flc_offset + _pulse_width >= _integration_time) {
        Serial.println("ERROR - invalid FLC offset: must be positive and < width + period");
        return;
    } else if ((_integration_time + _flc_offset > max_flc_integration_time) && (_trigger_mode & 0x1)) {
        Serial.println("ERROR - frequency too low to use FLC");
        return;
    }
    // set global variables
    integration_time = _integration_time;
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
    if (trigger_mode & 0x2) {
        sweep_mode = 1;
    }
    Serial.println("OK");
}

void prepareLoop() {
    // Compute values for loop
    dt1 = flc_offset;
    dt2 = dt1 + pulse_width;
    dt3 = dt1 + integration_time;
    // Second pass
    dt4 = dt3 + flc_offset;
    dt5 = dt4 + pulse_width;
    dt6 = dt4 + integration_time;
    // reset timer
    last_reset = micros();
    last_loop_finish = micros();
}
