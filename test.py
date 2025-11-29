import serial
import requests
import time
from datetime import datetime

# Настройка COM-порта
ser = serial.Serial("COM6", 9600, timeout=1)

def send_bytes(b):
    ser.write(bytearray(b))

# Очистка дисплея
def clear():
    send_bytes([0x0C])   # FF (form feed)

# Сброс дисплея
def reset():
    send_bytes([0x1B, 0x40])  # ESC @

clear()

# Установить кодировку 17 (или пробовать 18, 19)
ser.write(b'\x1B\x74\x11')   # ESC t 17

# Вывести русскую строку

def printLine(text):
    asc = text.encode('cp866')
    ser.write(text.encode('cp866'))

def pere():
    ser.write(bytearray([0x1F, 0x24, 0x01, 0x02]))

while True:
    now = datetime.now()
    line1 = now.strftime("%H:%M")
    line2 = now.strftime("%d.%m.%Y")

    clear()
    printLine(line1)            # пишем в первую строку
    # ЯВНО ПЕРЕМЕЩАЕМ КУРСОР В НАЧАЛО ВТОРОЙ СТРОКИ
    pere()
    printLine(line2)            # пишем вторую строку

    time.sleep(60)



