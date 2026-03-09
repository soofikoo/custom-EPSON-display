import time
from abc import abstractmethod, ABC
from datetime import datetime
from typing import Dict

import requests

from InfoPanel.core.services import WeatherService, SunService
from display_helper import Display


class Mode(ABC):
    def __init__(self, display: Display):
        self._display = display

    @abstractmethod
    def apply(self, last_mode: "Mode"):
        pass


class ClockMode(Mode):
    def __init__(self, display: Display):
        super().__init__(display)
        self._last_update = 0

    def print_date(self):
        self._display.print_line_endl(datetime.now().strftime("%d.%m.%Y"))

    def print_clock(self):
        self._display.print_line_endl(datetime.now().strftime("%H:%M"))

    def apply(self, last_mode: Mode):
        minutes = datetime.now().minute
        if minutes != self._last_update or not isinstance(last_mode, ClockMode):
            self._display.clear()
            self.print_date()
            self.print_clock()
            self._last_update = minutes


class WeatherMode(Mode):
    def __init__(self, display: Display, weather_service: WeatherService):
        super().__init__(display)
        self._weather_service = weather_service
        self._last_update = None

    def apply(self, last_mode: Mode):
        if self._weather_service is None:
            self._display.clear()
            self._display.print_line_endl("Нет api key")
            return

        if ((self._last_update is not None and self._last_update != datetime.now().date())
                or not isinstance(last_mode, WeatherMode)):

            try:
                data = self._weather_service.get_weather()
            except requests.RequestException:
                self._display.clear()
                self._display.print_line_endl("Ошибка API")
                return

            temperature = data["temperature"]
            city = data["city"]

            self._display.clear()
            self._display.print_line_endl(city)
            self._display.print_line_endl(str(temperature))


class SunMode(Mode):
    def __init__(self, display: Display, sun_service: SunService, change_period: int = 4):
        super().__init__(display)
        self._sun_service = sun_service
        self._last_update = None
        self._change_period = change_period
        self._last_mode = 0

    def _print_sunrise(self, data):
        sunrise = datetime.fromisoformat(data["sunrise"])
        sunset = datetime.fromisoformat(data["sunset"])

        self._display.print_line_endl(f"Восход: {sunrise.time().strftime("%H:%M")}")
        self._display.print_line_endl(f"Закат: {sunset.time().strftime("%H:%M")}")

    def _print_day_stats(self, data):
        delta_day_length = int(data["day_length"]) - int(data["day_length_past"])

        minutes = (delta_day_length % 3600) // 60
        if delta_day_length > 0:
            self._display.print_line_endl(f"День больше на {minutes}мин")
            self._display.print_line_endl("чем неделю назад")
        else:
            self._display.print_line_endl(f"День короче на {minutes}мин")
            self._display.print_line_endl("чем неделю назад")

    def apply(self, last_mode: Mode):
        if self._sun_service is None:
            self._display.print_line_endl("Сервис не доступен")
            return

        if not isinstance(last_mode, SunMode):
            self._last_mode = 0

        now = time.time()
        if ((self._last_update is not None and self._last_update + self._change_period < now)
                or not isinstance(last_mode, SunMode)):

            try:
                data = self._sun_service.get_sun_info()
            except requests.RequestException:
                self._display.clear()
                self._display.print_line_endl("Ошибка API")
                return

            self._display.clear()
            if self._last_mode % 2:
                self._print_day_stats(data)
            else:
                self._print_sunrise(data)

            self._last_update = now
            self._last_mode += 1


class AutoSwitchMode(Mode):
    def __init__(self, display: Display, modes: Dict[str, Mode], change_period: int = 10):
        super().__init__(display)
        self._modes = modes
        self._modes_index = list(self._modes.keys())
        self._change_period = change_period
        self._current_mode = self._modes.get(self._modes_index[0])
        self._last_update = 0
        self._last_mode_index: int = 0
        self._last_mode: Mode = self._modes.get(self._modes_index[-1])

    def apply(self, last_mode: Mode):
        now = time.time()

        if not isinstance(last_mode, AutoSwitchMode):
            self._current_mode = self._modes.get(self._modes_index[0])
            self._last_mode_index = 0
            self._last_update = 0
            self._last_mode = self._modes.get(self._modes_index[-1])

        if self._last_update + self._change_period < now:
            self._last_mode_index += 1
            self._last_update = now

            size = len(self._modes_index)

            self._last_mode = self._current_mode
            self._current_mode = self._modes.get(self._modes_index[self._last_mode_index % size])

        self._current_mode.apply(self._last_mode)
        self._last_mode = self._current_mode
