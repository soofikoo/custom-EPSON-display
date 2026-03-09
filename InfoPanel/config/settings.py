from dataclasses import dataclass
from typing import Optional

from InfoPanel.core.services import SettingsService


@dataclass(frozen=True)
class AppSettings:
    com_port: str
    api_key: str
    city: str

class SettingsManager:
    def __init__(self) -> None:
        self._service = SettingsService()

    def load(self) -> Optional[AppSettings]:
        if not self._service.load():
            return None
        return AppSettings(
            com_port=self._service.com_port,
            api_key=self._service.api_key,
            city=self._service.city,
        )

    def save(self, settings: AppSettings) -> None:
        self._service.change_settings(settings.com_port, settings.city, settings.api_key)
        self._service.save()