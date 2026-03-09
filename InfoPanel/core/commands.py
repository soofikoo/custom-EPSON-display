import queue
import threading
import logging
from queue import Queue
from typing import Optional

from InfoPanel.core.info_panel import InfoPanel

logger = logging.getLogger(__name__)

EXIT_COMMAND = "exit"


class CommandBus:
    def __init__(self) -> None:
        self._queue: Queue[str] = Queue()

    def send(self, command: str) -> None:
        self._queue.put(command)

    def receive(self, timeout: float = 0.5) -> Optional[str]:
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

class CommandListener:
    def __init__(self, bus: CommandBus, panel: InfoPanel) -> None:
        self._bus = bus
        self._panel = panel

    def start(self, stop_event: threading.Event) -> None:
        while not stop_event.is_set():
            command = self._bus.receive(timeout=0.5)
            if command is None:
                continue

            logger.debug("Получена команда: %s", command)

            if command == EXIT_COMMAND:
                stop_event.set()
                break

            try:
                self._panel.set_mode(command)
            except ValueError as e:
                logger.warning("Неизвестная команда: %s", e)