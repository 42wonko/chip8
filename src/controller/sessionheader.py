from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class SessionHeader:
    """
    @brief Information written at the beginning of a logging or tracing session.
    """
    title: str
    application: str
    version: str
    python_version: str
    timestamp: datetime
    logging: str | None = None
    trace_level: str | None = None
