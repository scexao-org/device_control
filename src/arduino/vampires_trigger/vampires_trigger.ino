// Here's some constants up front for easy retrieval
#define BAUDRATE 115200
#define TIMEOUT 500 // ms
// Pin mapping
#define CAMERA_TRIGGER_PIN 2
#define FLC_CONTROL_PIN 4
#define FLC_TRIGGER_PIN 6
#define AUX_PIN_A -1 // unused dig I/O pin
#define AUX_PIN_B -1 // unused dig I/O pin
#define AUX_PIN_C -1 // unused dig I/O pin

// FYI C people: Arduino int is 16bit, long is 32 bits.
// We use unsigned long for everything time-related in microseconds.
const unsigned long max_integration_time = 1600000000;
const unsigned long max_flc_integration_time = 1000000;
const unsigned long min_integration_time = 8; // 7.2 us line read time
unsigned long last_loop_finish;
unsigned long last_reset;
unsigned long dt1;
unsigned long dt2;
unsigned long dt3;
unsigned long dt4;
unsigned long dt5;
unsigned long dt6;

unsigned long integration_time;
unsigned long pulse_width;
unsigned long flc_offset;
int trigger_mode;
int cmd_code;


int sweep_mode = 0;
int auto_reset_mode = 0;
unsigned long next_reset = 0;
bool loop_enabled = false;

void setup()
{
    // set pin modes to output
    pinMode(CAMERA_TRIGGER_PIN, OUTPUT);
    pinMode(FLC_TRIGGER_PIN, OUTPUT);
    pinMode(FLC_CONTROL_PIN, OUTPUT);
    pinMode(13, OUTPUT);
    digitalWrite(13, loop_enabled);


    // reset outputs to low
    digitalWrite(CAMERA_TRIGGER_PIN, LOW);
    digitalWrite(FLC_TRIGGER_PIN, LOW);
    digitalWrite(FLC_CONTROL_PIN, LOW);

    // start serial connection
    Serial.setTimeout(TIMEOUT);
    Serial.begin(BAUDRATE);

    // reset timer
    last_reset = micros();
}

void set(int _integration_time, int _pulse_width, int _flc_offset, int _trigger_mode)
{
    // argument checking
    if (_integration_time > max_integration_time)
    {
        Serial.println("ERROR - frequency too low.");
        return;
    }
    else if ((_integration_time > max_flc_integration_time) && (_trigger_mode & 0x1)) {
      Serial.println("Error - frequency too low to use FLC");
      return;
    }
    else if (_integration_time < min_integration_time)
    {
        Serial.println("ERROR - frequency too high");
        return;
    }
    else if (_flc_offset < 0 || _flc_offset + _pulse_width >= _integration_time)
    {
        Serial.println("ERROR - invalid FLC offset must be positive and < width+period");
        return;
    }
    // set global variables
    integration_time = _integration_time;
    pulse_width = _pulse_width;
    flc_offset = _flc_offset;
    trigger_mode = _trigger_mode;
    // Use LSB for sweep
    if (trigger_mode & 0x1)
    {
        sweep_mode = 1;
    }
}

void get()
{
    Serial.print(loop_enabled);
    Serial.print(" ");
    Serial.print(integration_time);
    Serial.print(" ");
    Serial.print(flc_offset);
    Serial.print(" ");
    Serial.print(pulse_width);
    Serial.print(" ");
    Serial.println(trigger_mode);
}

void prepareLoop() {
    // Compute values for loop
    dt1 = flc_offset;
    dt2 = dt1 + pulse_width;
    dt3 = integration_time;
    // Asymmetric triggering by triggering the second frame 20 us too late (see below)
    dt4 = dt1 + integration_time + 20; // 20 us for measurable FLC on / FLC off skew
    dt5 = dt2 + integration_time + 20;
    dt6 = dt3 + integration_time;
    // reset timer
    last_reset = micros();
    // last_loop_finish is really when the loop last finished.
    last_loop_finish = micros();
}

void loop()
{
    if (Serial.available()) {
      cmd_code = Serial.parseInt();
        switch (cmd_code) {
            case 0: // GET
                get();
                break;
            case 1: // SET
                // set parameters
                set(Serial.parseInt(), Serial.parseInt(), Serial.parseInt(), Serial.parseInt());
                // reset loop
                prepareLoop();
                break;
            case 2: // DISABLE
                loop_enabled = false;
                digitalWrite(13, LOW);
                break;
            case 3: // ENABLE
                prepareLoop();
                loop_enabled = true;
                digitalWrite(13, HIGH);
                break;
            case 4: // FLC_DISABLE
                digitalWrite(FLC_CONTROL_PIN, LOW);
                break;
            case 5: // FLC_ENABLE
                digitalWrite(FLC_CONTROL_PIN, HIGH);
                break;
            default:
                Serial.println("ERROR - invalid command");
                break;
        }
        // flush input in case there's any leftover data
        Serial.flush();
    }
    // One loop pass covers 2 exposure times with 2 polarizations
    if (loop_enabled)
    {
        // First pola flc_pin LOW
        for (; micros() - last_loop_finish < dt1;) {} // This way of testing works around micros() overflowing
        digitalWrite(CAMERA_TRIGGER_PIN, HIGH);
        for (; micros() - last_loop_finish < dt2;) {}
        digitalWrite(CAMERA_TRIGGER_PIN, LOW);
        for (; micros() - last_loop_finish < dt3;) {}

        // Second pola flc_pin HIGH
        digitalWrite(FLC_TRIGGER_PIN, HIGH);
        for (; micros() - last_loop_finish < dt4;) {}
        digitalWrite(CAMERA_TRIGGER_PIN, HIGH);
        for (; micros() - last_loop_finish < dt5;) {}
        digitalWrite(CAMERA_TRIGGER_PIN, LOW);
        for (; micros() - last_loop_finish < dt6;) {}
        digitalWrite(FLC_TRIGGER_PIN, LOW);

        // Sweep mode
        if (sweep_mode)
        {
            ++flc_offset;
            if (flc_offset + pulse_width == integration_time)
            {
                flc_offset = 0;
            }
        }

        if (auto_reset_mode && (micros() - last_reset) >= 5000000) // 5 sec
        {
            // Sleep for 150 ms
            // EDT framegrabber set to timeout at 100 ms. Force it to timeout.
            for (; micros() - last_loop_finish < dt6 + 150000;) {}
            // Next reset in 5 sec.
            last_reset = micros();
            last_loop_finish = last_reset;
        } // if auto_reset

        last_loop_finish += dt6; // We take it that way, rather than calling micros() again.
                                     // Otherwise the loop will be a teensy tiny bit longer than 2*integration_time.
    } // For FLC / cam trig loop
}