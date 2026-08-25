from gpiozero import Button
from signal import pause

# pull_up=True is enabled by default, 50ms software debounce
button = Button(21, bounce_time=0.05)  

def on_pressed():
    print("Button: ON")

def on_released():
    print("Button: OFF")

button.when_pressed = on_pressed
button.when_released = on_released

print("Ready. Press the button (Ctrl+C to exit)...")
pause()  # Keep the script running to wait for events
