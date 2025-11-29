import serial

class DisplayHelper:
    def __init__(self, display_name : str, baudrate : int =9600, code : str = "RU"):
        self.display_name = display_name
        self.baudrate = baudrate
        self.code = code
        self.display = serial.Serial(port= display_name, baudrate=baudrate)

    def send_byte(self, byte):
        self.display.write(bytearray([byte]))

    def write_text(self, text):
        if self.code == "RU":
            self.send_byte(text.encode('cp866'))

    def set_code(self, code):
        if self.code == "RU":
            self.send_byte(b'\x1B\x74\x11')

    def print_line_endl(self, line):
        ...

    def print_line(self, line):
        ...

    def clear(self):
        self.send_byte(b'\x0C')

    def reset(self):
        self.send_byte(b'\x1B\x40')