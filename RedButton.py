import time
from pynput import keyboard
from Display import Display

display = Display(port="COM9")

counter = 0
combo_active = False
pressed = set()

def update_display():
    display.clear()
    display.print_line("Взорвано чурок: ")
    display.print_line(f"{counter}")
    display.pere()
    display.print_line("Today is great")

def on_press(key):
    global counter, combo_active
    pressed.add(key)

    if (keyboard.Key.ctrl_l in pressed and keyboard.Key.ctrl_r in pressed):
        if not combo_active:
            combo_active = True
            counter += 1
            update_display()

def on_release(key):
    global combo_active
    pressed.discard(key)
    if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
        combo_active = False

update_display()

listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release
)

listener.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    listener.stop()
    display.close()
