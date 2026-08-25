from gpiozero import Button
from time import sleep

#         /
# GND ---* *-- GPIO21

button = Button(21, bounce_time=0.05)

try:
    while True:
        if button.is_pressed:
            print("Button is currently held down")
        else:
            print("Button is open")
        sleep(0.5)
except KeyboardInterrupt:
    print("\nExiting program.")
