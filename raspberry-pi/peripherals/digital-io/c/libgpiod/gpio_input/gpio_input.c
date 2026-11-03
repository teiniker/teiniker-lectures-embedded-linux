#include <gpiod.h> // Include libgpiod library!
#include <signal.h>
#include <stdio.h>
#include <unistd.h>

// Circuit: GPIO27 --[Button]--> GND

// GPIO chip of the 40-pin header (Pi 5 with current kernels, Pi 4 and older)
const char *CHIP_PATH = "/dev/gpiochip0";
const unsigned int PIN_BUTTON = 27;    // line offset = BCM GPIO number

static volatile sig_atomic_t running = 1;

// Called on Ctrl+C so that we can release the line before exit
static void stop(int signum)
{
    (void)signum;
    running = 0;
}

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
    // direction ..(GPIOD_LINE_DIRECTION_INPUT, GPIOD_LINE_DIRECTION_OUTPUT)
    // bias ..(GPIOD_LINE_BIAS_DISABLED, GPIOD_LINE_BIAS_PULL_UP, GPIOD_LINE_BIAS_PULL_DOWN) => up
    struct gpiod_line_request *button = request_line(CHIP_PATH, PIN_BUTTON,
                                           GPIOD_LINE_DIRECTION_INPUT,
                                           GPIOD_LINE_BIAS_PULL_UP, "gpio_input");
    if (!button)
    {
        perror("request_line"); return 1;
    }

    signal(SIGINT, stop);

    while(running)
    {
        enum gpiod_line_value value = gpiod_line_request_get_value(button, PIN_BUTTON);

        if(value == GPIOD_LINE_VALUE_INACTIVE)
        {
            printf("ON\n");
        }
        else if(value == GPIOD_LINE_VALUE_ACTIVE)
        {
            printf("OFF\n");
        }
        else
        {
            perror("gpiod_line_request_get_value"); break;
        }
        usleep(100000);     // microseconds
    }

    gpiod_line_request_release(button);
    return 0;
}
