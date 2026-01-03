from display_helper import DisplayHelper

dis = DisplayHelper("COM8")

dis.clear()

dis.print_text("1")
print(dis.get_cursor_position())
dis.print_text("123456789123456789123")
print(dis.get_cursor_position())

dis.print_data()


