import serial

class DisplayHelper:
    def __init__(self, display_name : str, baudrate : int =9600, code : str = "RU"):
        self.__display = serial.Serial(port= display_name, baudrate=baudrate)
        self.__display_name = display_name
        self.__baudrate = baudrate
        self.__code = code

        self.__row = 0
        self.__column = 0
        self.__max_row_size = 1
        self.__max_column_size = 19

        self.__data = [[' ' for _ in range(0, self.__max_column_size + 1)] for _ in range(0, self.__max_row_size + 1)]

        self.__reset()
        self.set_code(self.__code)

    def __send_byte(self, byte):
        """Send a byte to the display"""
        self.__display.write(bytearray(byte))

    def __write_text(self, text):
        """Write a text to the display with the selected encoding"""
        if self.__code == "RU":
            self.__send_byte(text.encode('cp866'))
        elif self.__code == "JP":
            self.__send_byte(text.encode('shift_jis'))
        elif self.__code == "EU":
            self.__send_byte(text.encode('ascii'))

    def set_code(self, code):
        """Set the code of the display:\n
        RU - RUSSIAN CP866 encoding\n
        JP - JAPANESE Katakana encoding\n
        EU - ENGLISH default ASCII encoding\n

        other throw ValueError"""
        if code == "RU":
            self.__code = "RU"
            self.__send_byte(b'\x1B\x74\x11')
        elif code == "JP":
            self.__code = "JP"
            self.__send_byte(b'\x1B\x74\x01')
            self.__send_byte(b'\x1B\x52\x08')
        elif code == "EU":
            self.__code = "EU"
            self.__send_byte(b'\x1B\x74\x00')
        else:
            raise ValueError(f"Invalid code: '{code}'. Supported: 'RU', 'JP', 'EU'")

    def print_text(self, text):
        size_text = len(text)
        #TODO
        if self.__column + size_text - 1 > self.__max_column_size:
            self.__set_data(text[:self.__max_column_size - self.__column + 1])
            self.__row = (self.__row + 1) % (self.__max_row_size + 1)
            self.__column = (self.__column + 1) % (self.__max_column_size + 1)
            self.__column = self.__column + size_text - self.__max_column_size - 1
        else:
            self.__set_data(text)
            if self.__column + size_text > self.__max_column_size:
                self.__column = 0
                self.__row = (self.__row + 1) % (self.__max_row_size + 1)
            else:
                self.__column = self.__column + size_text


        self.__write_text(text)

    def print_line_endl(self, line):
        self.print_line(line)
        self.set_cursor_position((self.__row + 1) % (self.__max_row_size + 1), 0)

    def print_line(self, line):
        line_size = len(line)
        if line_size + self.__column > self.__max_column_size:
            raise ValueError("Too many columns")
        else:
            self.__set_data(line)
            self.__write_text(line)
            self.__column += line_size


    def clear(self):
        """Clear the display"""
        self.__row = 0
        self.__column = 0
        self.__send_byte(b'\x0C')

    def __reset(self):
        """Reset all parameters of the display (after check encoding)"""
        self.__row = 0
        self.__column = 0
        self.__send_byte(b'\x1B\x40')

    def set_cursor_position(self,row,column):
        if row > self.__max_row_size or column > self.__max_column_size:
            raise ValueError("Too many rows or columns")
        else:
            row_shift = 0x0 + row + 1
            column_shift = 0x0 + column + 1

            self.__row = row
            self.__column = column
            self.__send_byte([0x1F, 0x24, column_shift, row_shift])

    def get_cursor_position(self):
        print(len(self.__data[0]))
        return self.__row, self.__column

    def __set_data(self,data):
        data_size = len(data)

        if self.__row > self.__max_row_size or self.__column + data_size - 1 > self.__max_column_size:
            raise ValueError("Too many rows or columns")

        for column in range(0, data_size):
            self.__data[self.__row][column + self.__column] = data[column]

    def print_data(self):
        print(self.__data)