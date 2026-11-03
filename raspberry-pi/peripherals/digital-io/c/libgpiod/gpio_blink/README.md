# Example: Blink LED

```c
#include <gpiod.h>
#include <stdio.h>
#include <unistd.h>

// Circuit: GPIO17 --[R]--[LED]--> GND

// GPIO chip of the 40-pin header (Pi 5 with current kernels, Pi 4 and older)
const char *CHIP_PATH = "/dev/gpiochip0";
const unsigned int PIN_LED = 17;    // line offset = BCM GPIO number

// Request a single GPIO line from the kernel.
// Returns NULL on error (errno is set).
static struct gpiod_line_request *request_line(const char *chip_path, unsigned int offset,
                                               enum gpiod_line_direction direction,
                                               enum gpiod_line_bias bias,
                                               const char *consumer)
{
    struct gpiod_line_request *request = NULL;

    // Open the GPIO chip (character device of the kernel)
    struct gpiod_chip *chip = gpiod_chip_open(chip_path);
    if (!chip)
        return NULL;

    // Line settings: direction, bias, initial output value
    struct gpiod_line_settings *settings = gpiod_line_settings_new();
    // Line config: which settings apply to which line(s)
    struct gpiod_line_config *line_cfg = gpiod_line_config_new();
    // Request config: consumer name (shown by `gpioinfo`)
    struct gpiod_request_config *req_cfg = gpiod_request_config_new();

    if (settings && line_cfg && req_cfg)
    {
        gpiod_line_settings_set_direction(settings, direction);
        gpiod_line_settings_set_bias(settings, bias);
        gpiod_line_settings_set_output_value(settings, GPIOD_LINE_VALUE_INACTIVE);

        if (gpiod_line_config_add_line_settings(line_cfg, &offset, 1, settings) == 0)
        {
            gpiod_request_config_set_consumer(req_cfg, consumer);
            request = gpiod_chip_request_lines(chip, req_cfg, line_cfg);
        }
    }

    // The configuration objects and the chip are no longer needed
    if (req_cfg)  gpiod_request_config_free(req_cfg);
    if (line_cfg) gpiod_line_config_free(line_cfg);
    if (settings) gpiod_line_settings_free(settings);
    gpiod_chip_close(chip);

    return request;
}

int main(void)
{
    struct gpiod_line_request *led = request_line(CHIP_PATH, PIN_LED,
                                        GPIOD_LINE_DIRECTION_OUTPUT,
                                        GPIOD_LINE_BIAS_AS_IS, "blink");
    if (!led)
    {
        perror("request_line"); return 1;
    }


    for (int i=0; i<10; i++)
    {
        gpiod_line_request_set_value(led, PIN_LED, GPIOD_LINE_VALUE_ACTIVE);
        usleep(500000);     // microseconds
        gpiod_line_request_set_value(led, PIN_LED, GPIOD_LINE_VALUE_INACTIVE);
        usleep(500000);
    }

    // Give the line back to the kernel
    gpiod_line_request_release(led);
    return 0;
}
```

Differences to the WiringPi version:
* There is no global setup function. We open a **GPIO chip** (`/dev/gpiochip0`) and
  address the pins as **line offsets** of that chip (on the Pi equal to the BCM numbers).
* A line has to be **requested** from the kernel before use. The request is built
  from three objects: line settings (direction, initial value, bias, ...), a line
  config (which settings apply to which lines) and a request config (consumer name).
  The helper function `request_line()` hides these steps, so that `main()` stays
  as short as the WiringPi version.
* While our program holds the request, no other program can use the line.
  `gpioinfo` shows the line as used by consumer `"blink"`.
* `gpiod_line_request_release()` gives the line back to the kernel.

To build the example, you can either call the compiler manually:

```bash
$ gcc -Wall -o blink blink.c -lgpiod
$ ./blink
```

or with the help of CMake:
```bash
$ cmake -S . -B build
$ cd build/
$ make
$ ./blink
```

No `sudo` is needed: members of the `gpio` group may access `/dev/gpiochip*`.

*Egon Teiniker, 2025-2026, GPL v3.0*
