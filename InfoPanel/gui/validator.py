import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class StartupFormData:
    com_port: str    # уже с префиксом "COM", напр. "COM3"
    api_key: str
    city: str

def validate(raw_port: str, raw_api_key: str, raw_city: str) -> tuple[Optional[StartupFormData], Optional[str]]:
    if not all([raw_port, raw_api_key, raw_city]):
        return None, "Все поля обязательны"

    if not re.fullmatch(r"\d+", raw_port):
        return None, "COM порт — только цифры (например: 3)"

    if not re.fullmatch(r"[A-Za-z]+", raw_city):
        return None, "Город — только латинские буквы (например: Moscow)"

    return StartupFormData(
        com_port=f"COM{raw_port}",
        api_key=raw_api_key,
        city=raw_city,
    ), None