import serial
import time

class Display:
    # Настройка COM-порта
    def __init__(self, port="COM9", baudrate=9600):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(0.1)
        self.reset()
        self.set_cp866()
        self.clear()

    def send_bytes(self, b):
        self.ser.write(bytearray(b))

    # Очистка дисплея
    def clear(self):
        self.send_bytes([0x0C])

    # Сброс дисплея
    def reset(self):
        self.send_bytes([0x1B, 0x40])

    # Установить кодировку 17 (или пробовать 18, 19)
    def set_cp866(self):
        self.ser.write(b'\x1B\x74\x11')

    # Вывести русскую строку
    def print_line(self, text):
        self.ser.write(text.encode('cp866'))

    #Перенос строки
    def pere(self):
        self.send_bytes([0x1F, 0x24, 0x01, 0x02])

    def close(self):
        self.ser.close()
