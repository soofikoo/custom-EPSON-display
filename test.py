import time
from datetime import datetime
from Display import Display

display = Display(port="COM8") # настройка com-порта

while True:
    now = datetime.now()
    line1 = now.strftime("%H:%M")
    line2 = now.strftime("%d.%m.%Y")

    display.clear()
    display.print_line(line1)            # пишем в первую строку
    # ЯВНО ПЕРЕМЕЩАЕМ КУРСОР В НАЧАЛО ВТОРОЙ СТРОКИ
    display.pere()
    display.print_line(line2)            # пишем вторую строку

    time.sleep(60)



