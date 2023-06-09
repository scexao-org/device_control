
// Here's some constants up front for easy retrieval
#define BAUDRATE 115200
#define TIMEOUT 500 // ms
/* If true, turns LEDs on for visual debugging. The read "L" LED
 will turn on or off when the FLC is enabled/disable. The NeoPixel
 LED will be red when the trigger loop is disabled and green when
 the trigger loop is enabled. */
#define DEBUG_MODE false
// Pin mapping
#define CAMERA_TRIGGER_PIN 12
#define CAMERA_ONE_READY 10
#define CAMERA_TWO_READY 6
#define FLC_TRIGGER_PIN 8
#define FLC_DEADLOCK_PIN 4
#define FLC_RETURN_PIN 2

#if DEBUG_MODE
#include <Adafruit_NeoPixel.h>
#define LED_PIN 13
#define NEOPIXEL_PIN 40
#define NEOPIXEL_BRIGHTNESS 10
Adafruit_NeoPixel strip(1, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);
#endif

// FYI C people: Arduino int is 16bit, long is 32 bits.
// We use unsigned long for everything time-related in microseconds.
// FLC only works for integration times < 1 second
const unsigned long max_flc_integration_time = 1000000; // us
// The maximum integration time is 5 minutes
const unsigned long max_integration_time = 300000000; // us
// For FLC check, length of test pulse (10 ms)
const unsigned long flc_test_width = 10000; // us
// settings
unsigned long trig_delay;
unsigned long integration_time;
unsigned long pulse_width;
unsigned long flc_offset;
unsigned int trigger_mode;
bool sweep_mode;
bool loop_enabled;
bool flc_enabled;
bool camera_one_ready;
bool camera_two_ready;

/*
    Setup function runs every USB reset. Note: this includes when a serial
    DTR low signal is sent, which can be the case for some terminal emulators.
*/
void setup()
{    // variable resets
    sweep_mode = false;
    loop_enabled = false;
    flc_enabled = false;
    trig_delay = 0; // us
    pulse_width = 10; // us
    flc_offset = 20; // us

    // set pin modes
    pinMode(CAMERA_TRIGGER_PIN, OUTPUT);
    pinMode(FLC_TRIGGER_PIN, OUTPUT);
    pinMode(FLC_DEADLOCK_PIN, OUTPUT);
    pinMode(FLC_RETURN_PIN, INPUT);
    pinMode(CAMERA_ONE_READY, INPUT);
    pinMode(CAMERA_TWO_READY, INPUT);

    // reset outputs to low
    digitalWrite(CAMERA_TRIGGER_PIN, LOW);
    digitalWrite(FLC_TRIGGER_PIN, LOW);
    digitalWrite(FLC_DEADLOCK_PIN, LOW);

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
    unsigned long start_time;
    camera_one_ready = camera_two_ready = false;
    // First exposure FLC is relaxed
    digitalWrite(FLC_TRIGGER_PIN, LOW);
    
    
    // delaying this way works around integer overflow
    for (start_time = micros(); micros() - start_time < flc_offset + trig_delay;) continue;
    // Send camera trigger pulse
    digitalWrite(CAMERA_TRIGGER_PIN, HIGH);
    for (start_time = micros(); micros() - start_time < pulse_width;) continue;
    digitalWrite(CAMERA_TRIGGER_PIN, LOW);
    
    // wait for both cameras to have sent their trigger ready pulses
    // note that since the output is a pulse, we use |= as a tripwire
    // so all subsequent loops are True, even when the pulse goes back LOW
    for (start_time = micros(); micros() - start_time < max_flc_integration_time - pulse_width;) {
      camera_one_ready |= digitalRead(CAMERA_ONE_READY);
      camera_two_ready |= digitalRead(CAMERA_TWO_READY);
      if (camera_one_ready && camera_two_ready) break;
    }

    // In the case that we short-circuited, let's disable the loop
    // as a means of signalling the failure.
    if (!camera_one_ready || !camera_one_ready) disable_loop();
    
    // Sleep 60 micros to create +/- 30 timing jitter.
    for (start_time = micros(); micros() - start_time < 60;) continue;

    // start second half- reset variables
    camera_one_ready = camera_two_ready = false;
    // Second exposure FLC is active
    digitalWrite(FLC_TRIGGER_PIN, HIGH);
    for (start_time = micros(); micros() - start_time < flc_offset + trig_delay;) continue;
    // Send camera pulse
    digitalWrite(CAMERA_TRIGGER_PIN, HIGH);
    for (;micros() - start_time < pulse_width + flc_offset + trig_delay;) continue;
    digitalWrite(CAMERA_TRIGGER_PIN, LOW);
    // This time we need to add a short-circuit to avoid over-exciting the FLC
    for (;micros() - start_time < max_flc_integration_time;) {
      camera_one_ready |= digitalRead(CAMERA_ONE_READY);
      camera_two_ready |= digitalRead(CAMERA_TWO_READY);
      if (camera_one_ready && camera_two_ready) break;
    }
    // Immediately shut off FLC to maintain DC balance
    digitalWrite(FLC_TRIGGER_PIN, LOW);
    // In the case that we short-circuited, let's disable the loop
    // as a means of signalling the failure.
    if (!camera_one_ready || !camera_one_ready) disable_loop();

    // Sweep mode - increase offset until 1 ms offset
    if (sweep_mode) {
        flc_offset += 1;
        if (flc_offset > 1000) {
          disable_loop();
        }
    }
}

/*
    This loop is much simpler since the FLC trigger timing can be ignored.
    Here each arduino loop comprises a single camera trigger pulse.
*/
void trigger_loop_noflc() {
    unsigned long start_time;
    // reset ready flags
    camera_one_ready = camera_two_ready = false;
    // initiate pulse
    digitalWrite(CAMERA_TRIGGER_PIN, HIGH);
    for (start_time = micros(); micros() - start_time < pulse_width;) continue;
    digitalWrite(CAMERA_TRIGGER_PIN, LOW);
    // wait for both cameras to have sent their trigger ready pulses
    // note that since the output is a pulse, we use |= as a tripwire
    // so all subsequent loops are True, even when the pulse goes back LOW
    for (;micros() - start_time < max_integration_time;) {
      camera_one_ready |= digitalRead(CAMERA_ONE_READY);
      camera_two_ready |= digitalRead(CAMERA_TWO_READY);
      if (camera_one_ready && camera_two_ready) break;
    }
    // In the case that we short-circuited, let's disable the loop
    // as a means of signalling the failure.
    if (!camera_one_ready || !camera_one_ready) disable_loop();
}

void disable_loop() {
  loop_enabled = false;
#if DEBUG_MODE
  // set neopixel to red
  strip.setPixelColor(0, NEOPIXEL_BRIGHTNESS, 0, 0);
  strip.show();
#endif
}

void enable_loop() {
  loop_enabled = true;
#if DEBUG_MODE
  // set neopixel to green
  strip.setPixelColor(0, 0, NEOPIXEL_BRIGHTNESS, 0);
  strip.show();
#endif
}

void disable_flc() {
  flc_enabled = false;
  digitalWrite(FLC_DEADLOCK_PIN, LOW);
#if DEBUG_MODE
    digitalWrite(LED_PIN, LOW);
#endif
}

void enable_flc() {
  flc_enabled = true;
  digitalWrite(FLC_DEADLOCK_PIN, HIGH);
#if DEBUG_MODE
    digitalWrite(LED_PIN, HIGH);
#endif
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
    4 - FLC check
        This command will send a test pulse to the FLC controller to see
        if it is active.
*/
void handle_serial() {
    unsigned int cmd_code = Serial.parseInt();
    switch (cmd_code) {
        case 0: // GET
            get();
            break;
        case 1: // SET
            // set parameters
            // delay (us), pulse width (us), flc offset (us), trigger mode
            set(Serial.parseInt(), Serial.parseInt(), Serial.parseInt(), Serial.parseInt());
            Serial.println("OK");
            break;
        case 2: // DISABLE
            disable_loop();
            Serial.println("OK");
            break;
        case 3: // ENABLE
            enable_loop();
            Serial.println("OK");
            break;
        case 4: // FLC CHECK
            check_flc();
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
    Serial.print(trig_delay);
    Serial.print(" ");
    Serial.print(pulse_width);
    Serial.print(" ");
    Serial.print(flc_offset);
    Serial.print(" ");
    Serial.println(trigger_mode);
}

void set(int _trig_delay, int _pulse_width, int _flc_offset, int _trigger_mode) {
    // argument checking
    if (_trig_delay < 0) {
      Serial.println("ERROR - invalid delay: must be >= 0");
    }
    if (_flc_offset < 0 || _flc_offset > 1000) {
        Serial.println("ERROR - invalid FLC offset: must be between 0 and 1000");
        return;
    }
    if (_pulse_width < 0 || _pulse_width > 1000) {
      Serial.println("ERROR - invalid pulse width: must be between 0 and 1000");
      return;
    }
    if ((_trigger_mode & 0x1) && (_flc_offset + _trig_delay >= max_flc_integration_time)) {
      Serial.println("ERROR - invalid delay or FLC offset: both must add up to less than 1s");
    }
    // set global variables
    trig_delay = _trig_delay;
    pulse_width = _pulse_width;
    flc_offset = _flc_offset;
    trigger_mode = _trigger_mode;
    // `trigger_mode` LSB is FLC flag
    if (trigger_mode & 0x1) {
      enable_flc();
    } else {
      disable_flc();
    }
    // 'trigger_mode' 2nd bit is sweep mode flag
    sweep_mode = trigger_mode & 0x2;
}

/* 
  Sends a pulse to the FLC controller and waits for
  input on the return.
*/
void check_flc() {
    bool flc_return = false;
    unsigned long start_time;
    // send short (1 ms) high signal to FLC controller
    digitalWrite(FLC_TRIGGER_PIN, LOW);
    digitalWrite(FLC_DEADLOCK_PIN, HIGH);
    digitalWrite(FLC_TRIGGER_PIN, HIGH);
    for (start_time = micros(); micros() - start_time < flc_test_width;) {
      // check for any activity on the B flc control line from the controller
      flc_return |= digitalRead(FLC_RETURN_PIN);
    }
    // trigger low
    digitalWrite(FLC_TRIGGER_PIN, LOW);
    // continue to check for activity for the second half of the on/off cycle
    for (start_time = micros(); micros() - start_time < flc_test_width;) {
      flc_return |= digitalRead(FLC_RETURN_PIN);
    }
    // deadlock off
    digitalWrite(FLC_DEADLOCK_PIN, LOW);
    Serial.println(flc_return);
}
