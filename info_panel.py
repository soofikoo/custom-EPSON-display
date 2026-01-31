import queue
import re
import threading
import time
from datetime import datetime
import tkinter as tk

from queue import Queue
from time import sleep

from PIL import Image
from pystray import Icon, MenuItem, Menu

from display_helper import Display
from info_services import WeatherService, SettingsService


class AppInfoPanel:
    def __init__(self):
        self.__command_queue = Queue()
        self.__gui = GuiInfoPanel(self.__command_queue)
        self.__command_listener = None
        self.__info_panel = None
        self.__display = None
        self.__com_port = None
        self.__api_key = None
        self.__city = None
        self.__settings = SettingsService()
        self.__thread_gui = None
        self.__thread_command_loop = None
        self.__thread_info_panel = None
        self.__stop_event = threading.Event()

    def __ask_input(self):
        root = tk.Tk()
        root.title("Настройки")
        root.geometry("360x200")
        root.resizable(False, False)
        root.attributes("-topmost", True)

        try:
            root.iconbitmap("icon.ico")
        except Exception as _:
            pass

        root.columnconfigure(1, weight=1)

        com_var = tk.StringVar()
        api_key_var = tk.StringVar()
        city_var = tk.StringVar()

        tk.Label(root, text="COM порт:", font=("Arial", 11)) \
            .grid(row=0, column=0, padx=10, pady=(20, 5), sticky="w")

        com = tk.Entry(root, textvariable=com_var, font=("Arial", 12))
        com.grid(row=0, column=1, padx=10, pady=(20, 5), sticky="ew")
        com.focus_set()

        tk.Label(root, text="Город:", font=("Arial", 11)) \
            .grid(row=1, column=0, padx=10, pady=5, sticky="w")

        city = tk.Entry(root, textvariable=city_var, font=("Arial", 12))
        city.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        tk.Label(root, text="API key:", font=("Arial", 11)) \
            .grid(row=2, column=0, padx=10, pady=5, sticky="w")

        api_key = tk.Entry(
            root,
            textvariable=api_key_var,
            font=("Arial", 12),
            show="*"
        )
        api_key.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        error_label = tk.Label(root, text="", fg="red", font=("Arial", 10))
        error_label.grid(row=3, column=0, columnspan=2, pady=5)

        def validate_input(values: list) -> bool:
            if len(values) != 3:
                return False

            if re.fullmatch(r"\d+", values[0]) is None:
                return False
            return True

        def on_ok():
            values = [
                com.get(),
                api_key.get(),
                city_var.get()
            ]

            if not validate_input(values):
                error_label.config(
                    text="COM порт — только цифры, все поля обязательны"
                )
                return

            self.__com_port = "COM"+values[0]
            self.__api_key = values[1]
            self.__city = values[2]

            root.destroy()

        btn_frame = tk.Frame(root)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=15)

        tk.Button(btn_frame, text="OK", width=10, command=on_ok) \
            .pack(side="left", padx=5)

        tk.Button(btn_frame, text="Отмена", width=10, command=root.destroy) \
            .pack(side="left", padx=5)

        root.bind("<Return>", lambda e: on_ok())
        root.bind("<Escape>", lambda e: root.destroy())

        root.mainloop()

    def start(self):
        if not self.__settings.load():
            self.__ask_input()

            self.__settings.change_settings(self.__com_port, self.__city, self.__api_key)
            self.__settings.save()

        else:
            self.__settings.load()

            self.__com_port = self.__settings.com_port
            self.__api_key = self.__settings.api_key
            self.__city = self.__settings.city

        self.__display = Display(self.__com_port)

        self.__info_panel = InfoPanel(self.__display, self.__api_key, self.__city)
        self.__command_listener = CommandListenerInfoPanel(self.__command_queue, self.__info_panel)
        self.__thread_gui = threading.Thread(target=self.__gui.run_icon,args=(self.__stop_event,),daemon=True)
        self.__thread_command_loop = threading.Thread(target=self.__command_listener.start,args=(self.__stop_event,),daemon=True)
        self.__thread_info_panel = threading.Thread(target=self.__info_panel.start,args=(self.__stop_event,),daemon=True)
        self.__thread_gui.start()
        self.__thread_command_loop.start()
        self.__thread_info_panel.start()
        self.__thread_gui.join()
        self.__thread_command_loop.join()
        self.__thread_info_panel.join()


class InfoPanel:
    def __init__(self, display : Display, api_key_weather : str = None, weather_city : str = None ,mode : str = "clock"):
        self.__display = display
        self.__api_key = api_key_weather
        self.__city = weather_city
        self.__mode = mode
        self.__change = True
        self.__last_change = None
        self.__last_mode = "weather"
        self.__change_period = 30

        if api_key_weather is not None and weather_city is not None:
            self.__weather_service = WeatherService(api_key_weather, weather_city)
        else:
            self.__weather_service = None

    def set_mode(self, mode : str):
        if mode == "weather" or mode == "clock" or mode == "auto_switch_mode":
            self.__mode = mode
            self.__change = True
        else:
            raise ValueError("Invalid mode, must be 'weather' or 'clock'")

    def start(self, stop_event : threading.Event):
        self.__display.clear()
        last_minute = -1
        while not stop_event.is_set():
            minutes = datetime.now().minute
            seconds = datetime.now().second
            now_time = time.time()
            match self.__mode:
                case "clock":
                    if minutes != last_minute or self.__change:
                        self.__display.clear()
                        self.print_date()
                        self.print_clock()
                        last_minute = minutes
                case "weather":
                    if self.__change:
                        self.__display.clear()
                        self.print_weather()
                case "auto_switch_mode":
                    if self.__last_change is None:
                        self.__last_change = time.time()
                    if now_time > self.__last_change + self.__change_period:
                        self.__change = True
                    if self.__last_mode == "weather":
                        if minutes != last_minute or self.__change:
                            self.__display.clear()
                            self.print_date()
                            self.print_clock()
                            last_minute = minutes
                            if self.__change:
                                self.__last_mode = "clock"
                                self.__last_change = now_time
                    if self.__last_mode == "clock":
                        if self.__change:
                            self.__display.clear()
                            self.print_weather()
                            self.__last_mode = "weather"
                            self.__last_change = now_time

            if self.__change:
                self.__change = False
            sleep(0.5)

    def print_weather(self):
        if self.__weather_service is not None:
            data = self.__weather_service.get_weather()
            temperature = data["temperature"]
            city = data["city"]

            self.__display.print_line_endl(city)
            self.__display.print_line_endl(str(temperature))
        else:
            self.__display.print_line_endl("Нет api key")

    def print_date(self):
        self.__display.print_line_endl(datetime.now().strftime("%d.%m.%Y"))

    def print_clock(self):
        self.__display.print_line_endl(datetime.now().strftime("%H:%M"))


class CommandListenerInfoPanel:
    def __init__(self, command_queue: Queue, info_panel : InfoPanel):
        self.__command_queue = command_queue
        self.__info_panel = info_panel

    def start(self, stop_event : threading.Event):
        while not stop_event.is_set():
            try:
                command = self.__command_queue.get(timeout=0.5)
                print("Команда:", command)
                if command == "exit":
                    stop_event.set()
                    break

                self.__info_panel.set_mode(command)
            except queue.Empty:
                continue

class GuiInfoPanel:
    def __init__(self, command_queue : Queue):
        self.__icon = self.__create_icon()
        self.__command_queue = command_queue

    def __on_clock(self,icon, item):
        self.__command_queue.put("clock")

    def __on_weather(self,icon, item):
        self.__command_queue.put("weather")

    def __on_auto_switch(self,icon, item):
        self.__command_queue.put("auto_switch_mode")

    def __on_exit(self,icon, item):
        self.__command_queue.put("exit")
        icon.stop()

    def __create_icon(self) -> Icon:
        icon_image = Image.open("icon.ico")
        return Icon(
            "InfoPanelCOM",
            icon_image,
            menu=Menu(
                MenuItem("Clock", self.__on_clock),
                MenuItem("Weather", self.__on_weather),
                MenuItem("AutoSwitch", self.__on_auto_switch),
                MenuItem("Exit", self.__on_exit)
            ),
        )

    def run_icon(self, stop_event : threading.Event):
        self.__icon.run()
        stop_event.set()

if __name__ == "__main__":
    app = AppInfoPanel()
    app.start()