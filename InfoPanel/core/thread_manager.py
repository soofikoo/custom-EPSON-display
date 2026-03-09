import threading
from typing import Callable


class ThreadManager:
    def __init__(self, stop_event: threading.Event) -> None:
        self._stop_event = stop_event
        self._threads: list[threading.Thread] = []

    def add(self, target: Callable[[threading.Event], None], *, daemon: bool = True) -> None:
        thread = threading.Thread(
            target=target,
            args=(self._stop_event,),
            daemon=daemon,
        )
        self._threads.append(thread)

    def start_all(self) -> None:
        for t in self._threads:
            t.start()

    def join_all(self) -> None:
        for t in self._threads:
            t.join()

    def run(self) -> None:
        self.start_all()
        self.join_all()
