class Chip8Error(RuntimeError):
    """Base class for emulator errors."""


class CallStackUnderflowError(Chip8Error):
    """RET executed with an empty call stack."""
