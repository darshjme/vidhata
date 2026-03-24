"""PlanExecutor: runs a plan step by step in dependency order."""

from __future__ import annotations
from typing import Callable
import traceback

from .plan import Plan
from .step import Step


class PlanExecutor:
    """Executes a plan by invoking registered handlers for each step."""

    def __init__(self, plan: Plan, handlers: dict[str, Callable] | None = None) -> None:
        if not isinstance(plan, Plan):
            raise TypeError(f"Expected Plan, got {type(plan).__name__}")
        self.plan = plan
        self.handlers: dict[str, Callable] = dict(handlers) if handlers else {}

    def run_step(self, step_id: str) -> bool:
        """Execute a single step by ID. Marks it done or failed. Returns True on success."""
        step = self.plan.get_step(step_id)

        if step.status == "done":
            return True
        if step.status == "failed":
            return False

        step.status = "running"
        handler = self.handlers.get(step_id)

        if handler is None:
            # No handler — mark as done with a note
            step.status = "done"
            step.result = None
            return True

        try:
            result = handler(step)
            step.status = "done"
            step.result = result
            return True
        except Exception as exc:
            step.status = "failed"
            step.error = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"
            return False

    def run(self) -> dict:
        """Execute all steps in dependency order. Returns final plan summary."""
        completed: set[str] = {s.id for s in self.plan.steps if s.status == "done"}
        max_iterations = len(self.plan.steps) * 2 + 1  # Safety valve

        iterations = 0
        while not self.plan.is_complete and iterations < max_iterations:
            iterations += 1
            ready = self.plan.next_steps(completed)

            if not ready:
                # No steps ready — either done or stuck (failed dependency)
                break

            for step in ready:
                success = self.run_step(step.id)
                if success:
                    completed.add(step.id)

        return self.plan.summary()

    def __repr__(self) -> str:
        return f"PlanExecutor(plan={self.plan.name!r}, handlers={len(self.handlers)})"
