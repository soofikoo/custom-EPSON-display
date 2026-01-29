import queue
import re
import threading
import time
from datetime import datetime
import tkinter as tk

from queue import Queue

import requests
from PIL import Image, ImageDraw
from pystray import Icon, MenuItem, Menu

from display_helper import Display


class AppInfoPanel:
    def __init__(self):
        self.__command_queue = Queue()
        self.__gui = GuiInfoPanel(self.__command_queue)
        self.__info_panel = None
        self.__display = None
        self.__com_port = None
        self.__api_key = None
        self.__city = None

    def __ask_input(self):
        root = tk.Tk()
        root.title("Input")
        root.geometry("300x400")
        root.attributes("-topmost", True)

        com_var = tk.StringVar()
        api_key_var = tk.StringVar()
        city_var = tk.StringVar()

        label = tk.Label(root, text="Введите номер COM порта устройства:", font=("Arial", 12))
        label.pack(pady=(20, 5))
        com = tk.Entry(root, textvariable=com_var, font=("Arial", 14))
        com.pack(pady=20, padx=20)
        com.focus_set()

        label = tk.Label(root, text="Введите город:", font=("Arial", 12))
        label.pack(pady=(20, 5))
        city = tk.Entry(root, textvariable=city_var, font=("Arial", 14))
        city.pack(pady=20, padx=20)

        label = tk.Label(root, text="Введите api key:", font=("Arial", 12))
        label.pack(pady=(20, 5))
        api_key = tk.Entry(root, textvariable=api_key_var, font=("Arial", 14))
        api_key.pack(pady=20, padx=20)

        error_label = tk.Label(root, text="", fg="red")
        error_label.pack()

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
                error_label.config(text="Номер порта должен содержать только числа и все поля должны быть заполнены")
                return

            self.__com_port = values[0]
            self.__api_key = values[1]
            self.__city = values[2]

            root.destroy()

        btn = tk.Button(root, text="OK", command=on_ok, font=("Arial", 12))
        btn.pack()

        root.mainloop()

    def __loop(self):
        while True:
            try:
                command = self.__command_queue.get_nowait()
                print("Команда:", command)
                self.__info_panel.set_mode(command)
            except queue.Empty:
                pass

            time.sleep(1)

    def start(self):
        self.__ask_input()

        self.__display = Display("COM"+self.__com_port)

        self.__info_panel = InfoPanel(self.__display, self.__api_key, self.__city)

        t1 = threading.Thread(target=self.__gui.run_icon,daemon=True)
        t2 = threading.Thread(target=self.__loop,daemon=True)
        t3 = threading.Thread(target=self.__info_panel.start,daemon=True)
        t1.start()
        t2.start()
        t3.start()
        t1.join()
        t2.join()
        t3.join()

class GuiInfoPanel:
    def __init__(self, command_queue : Queue):
        self.__icon = self.create_icon()
        self.__command_queue = command_queue

    def create_image(self):
        image = Image.new('RGB', (64, 64), "black")
        draw = ImageDraw.Draw(image)
        draw.rectangle((16, 16, 48, 48), fill="white")
        return image

    def on_clock(self,icon, item):
        self.__command_queue.put("clock")

    def on_weather(self,icon, item):
        self.__command_queue.put("weather")

    def on_exit(self,icon, item):
        self.__command_queue.put("exit")
        icon.stop()

    def create_icon(self) -> Icon:
        return Icon(
            "MyApp",
            self.create_image(),
            menu=Menu(
                MenuItem("Clock", self.on_clock),
                MenuItem("Weather", self.on_weather),
                MenuItem("Exit", self.on_exit)
            ),
        )

    def run_icon(self):
        self.__icon.run()


class InfoPanel:
    def __init__(self, display : Display, api_key_weather : str = None, weather_city : str = None ,mode : str = "clock"):
        self.__display = display
        self.__api_key = api_key_weather
        self.__mode = mode
        self.__change = True

        if api_key_weather is not None and weather_city is not None:
            self.__weather_service = WeatherService(api_key_weather, weather_city)
        else:
            self.__weather_service = None

    def set_mode(self, mode : str):
        if mode == "weather" or mode == "clock":
            self.__mode = mode
            self.__change = True
        else:
            raise ValueError("Invalid mode, must be 'weather' or 'clock'")


    def start(self):
        self.__display.clear()
        last_minute = -1
        while True:
            minutes = datetime.now().minute

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

            if self.__change:
                self.__change = False
            time.sleep(1)

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


class WeatherService:
    URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self, api_key : str, city : str = "Samara"):
        self.__api_key = api_key
        self.__city = city

    def get_weather(self) -> dict:
        params = {
            "q": self.__city,
            "appid": self.__api_key,
            "units": "metric",
            "lang": "ru"
        }

        response = requests.get(self.URL, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        return {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"]
        }

if __name__ == "__main__":
    app = AppInfoPanel()
    app.start()