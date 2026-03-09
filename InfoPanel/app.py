import threading

from display_helper import Display
from InfoPanel.core.services import WeatherService, SunService
from InfoPanel.core.modes import ClockMode, WeatherMode, SunMode, AutoSwitchMode

from config.settings import AppSettings, SettingsManager
from core.commands import CommandBus
from core.commands import CommandListener
from core.info_panel import InfoPanel
from core.mode_registry import ModeRegistry, AppMode
from core.thread_manager import ThreadManager
from gui.startup import StartupDialog
from gui.tray import TrayIcon


def _build_registry(display: Display, settings: AppSettings) -> ModeRegistry:
    weather_service = WeatherService(settings.api_key, settings.city) if settings.api_key and settings.city else None
    sun_service = SunService(settings.city) if settings.city else None

    registry = ModeRegistry()
    modes_for_auto = {
        AppMode.CLOCK:   ClockMode(display),
        AppMode.WEATHER: WeatherMode(display, weather_service),
        AppMode.SUN:     SunMode(display, sun_service),
    }

    for key, mode in modes_for_auto.items():
        registry.register(key, mode)

    registry.register(AppMode.AUTO_SWITCH, AutoSwitchMode(display, modes_for_auto))
    return registry


def _resolve_settings() -> AppSettings:
    manager = SettingsManager()
    settings = manager.load()
    if settings:
        return settings

    result = StartupDialog().ask()
    if result is None:
        raise SystemExit("Настройка отменена пользователем")

    settings = AppSettings(
        com_port=result.com_port,
        api_key=result.api_key,
        city=result.city,
    )
    manager.save(settings)
    return settings


class App:
    def start(self) -> None:
        settings = _resolve_settings()

        display = Display(settings.com_port)
        registry = _build_registry(display, settings)

        bus = CommandBus()
        panel = InfoPanel(display, registry)

        stop_event = threading.Event()
        threads = ThreadManager(stop_event)

        threads.add(TrayIcon(bus).run)
        threads.add(CommandListener(bus, panel).start)
        threads.add(panel.start)

        threads.run()