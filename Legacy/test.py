import time
from datetime import datetime
from display_helper import Display

display = Display("COM8") # настройка com-порта

while True:
    now = datetime.now()
    line1 = now.strftime("%H:%M")
    line2 = now.strftime("%d.%m.%Y")

    display.clear()
    display.print_line_endl(line1)            # пишем в первую строку
    display.print_line_endl(line2)            # пишем вторую строку

    time.sleep(60)



