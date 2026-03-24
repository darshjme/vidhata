"""Step: a single unit of work in an execution plan."""

from __future__ import annotations
from typing import Any


VALID_STATUSES = {"pending", "running", "done", "failed"}


class Step:
    """A single plan step with dependency tracking."""

    def __init__(
        self,
        id: str,
        description: str,
        depends_on: list[str] | None = None,
        metadata: dict | None = None,
    ) -> None:
        if not id or not isinstance(id, str):
            raise ValueError("Step id must be a non-empty string")
        if not description or not isinstance(description, str):
            raise ValueError("Step description must be a non-empty string")

        self.id = id
        self.description = description
        self.depends_on: list[str] = list(depends_on) if depends_on else []
        self.metadata: dict = dict(metadata) if metadata else {}
        self.status: str = "pending"
        self.result: Any = None
        self.error: str | None = None

    def is_ready(self, completed: set[str] | None = None) -> bool:
        """Return True if all dependencies are satisfied."""
        completed = completed or set()
        return all(dep in completed for dep in self.depends_on)

    def to_dict(self) -> dict:
        """Serialize step to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "depends_on": self.depends_on,
            "metadata": self.metadata,
            "status": self.status,
            "result": self.result,
            "error": self.error,
        }

    def __repr__(self) -> str:
        return f"Step(id={self.id!r}, status={self.status!r})"
