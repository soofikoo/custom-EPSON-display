import serial

class Display:
    """Class for working with serial display"""
    def __init__(self, display_name : str, baudrate : int =9600, code : str = "RU", max_row_size : int = 1, max_col_size : int = 19):
        self.__display = serial.Serial(port= display_name, baudrate=baudrate)
        self.__display_name = display_name
        self.__baudrate = baudrate
        self.__code = code

        self._max_row_size = max_row_size
        self._max_column_size = max_col_size

        self._row = 0
        self._column = 0

        self._reset()
        self.set_code(self.__code)

    def close(self):
        """Close the serial display after work"""
        self.__display.close()

    def __send_byte(self, byte : bytes):
        """Send a byte to the display"""
        self.__display.write(bytearray(byte))

    def __write_text(self, text : str):
        """Write a text to the display with the selected encoding"""
        if self.__code == "RU":
            self.__send_byte(text.encode('cp866'))
        elif self.__code == "JP":
            self.__send_byte(text.encode('shift_jis'))
        elif self.__code == "EU":
            self.__send_byte(text.encode('ascii'))

    def set_code(self, code : str):
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

    def clear(self):
        """Clear the display"""
        self._row = 0
        self._column = 0
        self.__send_byte(b'\x0C')

    def _reset(self):
        """Reset all parameters of the display (after check encoding)"""
        self._row = 0
        self._column = 0
        self.__send_byte(b'\x1B\x40')

    def print_line_endl(self, line : str):
        """Print a line of text with line break"""
        self.print_line(line)
        self.set_cursor_position((self._row + 1) % (self._max_row_size + 1), 0)

    def print_line(self, line : str):
        """Print a line of text"""
        line_size = len(line)
        if line_size + self._column > self._max_column_size:
            raise ValueError("Too many columns")
        else:
            self.__write_text(line)
            self._column += line_size

    def set_cursor_position(self, row : int, column : int):
        """
        Set the cursor position of the display
        :param row: row number
        :param column: column number
        """
        if row > self._max_row_size or column > self._max_column_size:
            raise ValueError("Too many rows or columns")
        else:
            row_shift = 0x0 + row + 1
            column_shift = 0x0 + column + 1

            self._row = row
            self._column = column
            self.__send_byte(bytes([0x1F, 0x24, column_shift, row_shift]))

    def get_cursor_position(self):
        """Return the cursor position of the display"""
        return self._row, self._column

class DisplayWithBuffer(Display):
    """Class for working with serial display and save data in lines"""
    def __init__(self, display_name : str, baudrate : int =9600, code : str = "RU", max_row_size : int = 1, max_col_size : int = 19):
        super().__init__(display_name,baudrate,code,max_row_size,max_col_size)
        self.__data = [[' ' for _ in range(0, self._max_column_size + 1)] for _ in range(0, self._max_row_size + 1)]

    def clear(self):
        super().clear()
        self.__clear_data()

    def reset(self):
        super()._reset()
        self.__clear_data()

    def print_line(self, line):
        super().print_line(line)
        self.__set_data(line)

    def __set_data(self, data : str):
        """Update the data in lines"""
        data_size = len(data)
        if self._row > self._max_row_size or self._column + data_size - 1 > self._max_column_size:
            raise ValueError("Too many rows or columns")

        for column in range(0, data_size):
            self.__data[self._row][column + self._column] = data[column]

    def __clear_data(self):
        """Clear the data in lines"""
        self.__data = [[' ' for _ in range(0, self._max_column_size + 1)] for _ in range(0, self._max_row_size + 1)]

    def print_data(self):
        """Print the data"""
        for row in range(0, self._max_row_size+1):
            print(self.__data[row])