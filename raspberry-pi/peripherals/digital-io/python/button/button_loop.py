from gpiozero import Button
from time import sleep

#         /
# GND ---* *-- GPIO21

button = Button(21, bounce_time=0.05)

while True:
    if button.is_pressed:
        print("Button: ON")
    else:
        print("Button: OFF")
    sleep(0.5)
