from gpiozero import PWMLED
from time import sleep

# Software PWM: works on any pin
led = PWMLED(17)

while True:
    # Duty cycle value ranges from 0.0 (0%) to 1.0 (100%)
    for duty in range(0, 101, 10):
        led.value = duty / 100.0
        sleep(0.05)
    for duty in range(100, -1, -10):
        led.value = duty / 100.0
        sleep(0.05)
