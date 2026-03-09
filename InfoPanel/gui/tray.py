import os
import sys
import threading

from PIL import Image
from pystray import Icon, MenuItem, Menu

from InfoPanel.core.commands import CommandBus
from InfoPanel.core.mode_registry import AppMode

if getattr(sys, 'frozen', False):
    _base_dir = os.path.dirname(sys.executable)
else:
    _base_dir = os.path.dirname(os.path.abspath(__file__))

ICON_PATH = os.path.join(_base_dir, 'icon.ico')


class TrayIcon:
    _MENU_LABELS = {
        AppMode.CLOCK:       "Clock",
        AppMode.WEATHER:     "Weather",
        AppMode.SUN:         "Sun",
        AppMode.AUTO_SWITCH: "AutoSwitch",
    }

    def __init__(self, bus: CommandBus) -> None:
        self._bus = bus
        self._icon = self._build_icon()

    def _make_handler(self, command: str):
        def handler(icon, item):
            self._bus.send(command)
        return handler

    def _on_exit(self, icon, item) -> None:
        self._bus.send("exit")
        icon.stop()

    def _build_icon(self) -> Icon:
        image = Image.open(ICON_PATH)

        mode_items = [
            MenuItem(label, self._make_handler(mode.value))
            for mode, label in self._MENU_LABELS.items()
        ]

        return Icon(
            "InfoPanelCOM",
            image,
            menu=Menu(*mode_items, MenuItem("Exit", self._on_exit)),
        )

    def run(self, stop_event: threading.Event) -> None:
        self._icon.run()
        stop_event.set()