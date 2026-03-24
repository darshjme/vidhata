"""Plan: an ordered, dependency-aware execution plan."""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from .step import Step


class Plan:
    """An ordered execution plan composed of Steps."""

    def __init__(self, name: str, steps: list[Step] | None = None) -> None:
        if not name or not isinstance(name, str):
            raise ValueError("Plan name must be a non-empty string")
        self.name = name
        self._steps: list[Step] = []
        self._step_index: dict[str, Step] = {}

        for step in (steps or []):
            self.add_step(step)

    def add_step(self, step: Step) -> "Plan":
        """Add a step; raises ValueError on duplicate ID. Returns self for chaining."""
        if not isinstance(step, Step):
            raise TypeError(f"Expected Step, got {type(step).__name__}")
        if step.id in self._step_index:
            raise ValueError(f"Duplicate step ID: {step.id!r}")
        self._steps.append(step)
        self._step_index[step.id] = step
        return self

    def get_step(self, step_id: str) -> Step:
        """Get a step by ID; raises KeyError if not found."""
        if step_id not in self._step_index:
            raise KeyError(f"Step not found: {step_id!r}")
        return self._step_index[step_id]

    @property
    def steps(self) -> list[Step]:
        return list(self._steps)

    def next_steps(self, completed: set[str] | None = None) -> list[Step]:
        """Return all pending steps whose dependencies are satisfied."""
        completed = completed or set()
        # Auto-derive completed from done steps if not provided
        if not completed:
            completed = {s.id for s in self._steps if s.status == "done"}
        return [
            s for s in self._steps
            if s.status == "pending" and s.is_ready(completed)
        ]

    @property
    def is_complete(self) -> bool:
        """True if every step is done."""
        return bool(self._steps) and all(s.status == "done" for s in self._steps)

    @property
    def is_failed(self) -> bool:
        """True if any step has failed and no retry path exists."""
        failed_ids = {s.id for s in self._steps if s.status == "failed"}
        if not failed_ids:
            return False
        # Check if any non-failed step depends on a failed step (blocked)
        # If failed steps block remaining pending steps, plan cannot complete
        remaining_pending = [s for s in self._steps if s.status == "pending"]
        if not remaining_pending:
            return True  # nothing left, something failed
        # If we have failed steps, plan is failed
        return True

    def summary(self) -> dict:
        """Return counts by status."""
        counts: dict[str, int] = {"pending": 0, "running": 0, "done": 0, "failed": 0}
        for s in self._steps:
            counts[s.status] = counts.get(s.status, 0) + 1
        counts["total"] = len(self._steps)
        return counts

    def to_dict(self) -> dict:
        """Serialize plan to dictionary."""
        return {
            "name": self.name,
            "steps": [s.to_dict() for s in self._steps],
            "summary": self.summary(),
            "is_complete": self.is_complete,
            "is_failed": self.is_failed,
        }

    def __len__(self) -> int:
        return len(self._steps)

    def __repr__(self) -> str:
        return f"Plan(name={self.name!r}, steps={len(self._steps)})"
