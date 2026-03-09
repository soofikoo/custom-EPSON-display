import threading

from display_helper import Display
from InfoPanel.core.modes import Mode
from InfoPanel.core.mode_registry import ModeRegistry, AppMode


class InfoPanel:
    def __init__(self, display: Display, registry: ModeRegistry) -> None:
        self._display = display
        self._registry = registry
        self._current_mode: Mode = registry.get(AppMode.CLOCK)
        self._last_mode: Mode = self._current_mode

    def set_mode(self, name: str) -> None:
        self._current_mode = self._registry.get_by_name(name)

    def start(self, stop_event: threading.Event) -> None:
        self._display.clear()
        while not stop_event.is_set():
            self._current_mode.apply(self._last_mode)
            self._last_mode = self._current_mode
            stop_event.wait(0.5)
