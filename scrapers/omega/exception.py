from typing import Literal


class OmegaException(Exception):
    def __init__(self, severity: Literal['fatal', 'error', 'warning', 'info', 'abort'], message: str):
        self.severity = severity
        # self.omega = omega
        self.message = message

        super().__init__(self.message)


class OmegaAbort(Exception):
    def __init__(self) -> None:
        super().__init__("Process Aborted")
