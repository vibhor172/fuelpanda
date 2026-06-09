"""Base application exception rendered to a consistent error envelope."""
from typing import Any


class AppException(Exception):
    """All domain errors subclass this. Rendered by the global handler in main.py."""

    code: str = "APP_ERROR"
    http_status: int = 400
    message: str = "Application error"

    def __init__(
        self,
        message: str | None = None,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.message
        self.details = details
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        body: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.details is not None:
            body["details"] = self.details
        return {"error": body}
