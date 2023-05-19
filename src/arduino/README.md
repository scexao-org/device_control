# Arduino Source Code

## VAMPIRES

VAMPIRES uses an [Adafruit Metro M4 express](https://www.adafruit.com/product/3382) for camera and FLC triggering. Physically, this micro-controller is mounted in an enclosure with 6 SMA connectors.

| SMA marker | Dig I/O port | Description |
|-|-|-|
| R1 | 12 | Camera 1 trigger ready input. |
| CT | 10 | Camera trigger output. This is designed to be teed off to both cameras so they receive a simultaneous input. |
| R2 | 8 | Camera 2 trigger ready input. |
| FT | 6 | FLC trigger output. This is designed to connect to the trigger input of the Meadowlark FLC controller. |
| FC | 4 | FLC control output. The FLC will not trigger unless this output is enabled. This is designed to connect to the control input of the Meadowlark FLC controller. |
|    |   | Unused port |

### Deployment

> 📖: Recommended reading
>
> Everything here is distilled down from the tutorials at [adafruit](https://learn.adafruit.com/adafruit-metro-m4-express-featuring-atsamd51)

In order to deploy this code, you'll need to get a copy of the [Arduino IDE](https://www.arduino.cc/en/software). Once that's downloaded, you'll need some extra drivers to connect with our third-party board. Follow the [directions here](https://learn.adafruit.com/adafruit-metro-m4-express-featuring-atsamd51/setup). You'll also need the extra library for the neopixel (the big bright RGB LED)- [directions here](https://learn.adafruit.com/adafruit-neopixel-uberguide/arduino-library-installation).

Once that's done, you should be able to select the board using the appropriate com port (e.g., `/dev/serial/by-id/...`) from Arduino IDE and select "Metro M4 Express (ATSAMD51)" as the board type.

Once everything's connected, you should be able to deploy the code. If successful, there should be no output from the board. If in debug mode, the "L" LED (near the USB port) will indicate whether the FLC is enabled, and the neopixel will turn red or green depending on whether the trigger loop is enabled.

## Near-IR

Ask Vincent.