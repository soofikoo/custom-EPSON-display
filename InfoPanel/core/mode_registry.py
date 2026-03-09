from enum import Enum
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from InfoPanel.core.modes import Mode


class AppMode(str, Enum):
    CLOCK = "clock"
    WEATHER = "weather"
    SUN = "sun"
    AUTO_SWITCH = "auto_switch_mode"

    @classmethod
    def values(cls) -> list[str]:
        return [m.value for m in cls]


class ModeRegistry:
    def __init__(self) -> None:
        self._modes: Dict[AppMode, "Mode"] = {}

    def register(self, key: AppMode, mode: "Mode") -> None:
        self._modes[key] = mode

    def get(self, key: AppMode) -> "Mode":
        if key not in self._modes:
            raise KeyError(f"Режим '{key}' не зарегистрирован")
        return self._modes[key]

    def get_by_name(self, name: str) -> "Mode":
        try:
            return self.get(AppMode(name))
        except ValueError:
            raise ValueError(f"Неизвестный режим: '{name}'. Доступные: {AppMode.values()}")

    def all_modes(self) -> Dict[AppMode, "Mode"]:
        return dict(self._modes)