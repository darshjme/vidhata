"""Planner: factory for creating and composing Plans."""

from __future__ import annotations

from .plan import Plan
from .step import Step


class Planner:
    """Creates and manages execution plans."""

    def __init__(self) -> None:
        self._plans: list[Plan] = []

    def create(self, name: str) -> Plan:
        """Create and register an empty plan."""
        plan = Plan(name)
        self._plans.append(plan)
        return plan

    def decompose(self, task: str, steps: list[dict]) -> Plan:
        """Build a plan from a list of step dicts with keys: id, description, depends_on?.

        Args:
            task: Human-readable task name (used as plan name).
            steps: List of dicts with 'id', 'description', and optional 'depends_on'.

        Returns:
            Fully constructed Plan.
        """
        plan = Plan(task)
        for spec in steps:
            if "id" not in spec or "description" not in spec:
                raise ValueError(
                    f"Each step dict must have 'id' and 'description'. Got: {spec!r}"
                )
            step = Step(
                id=spec["id"],
                description=spec["description"],
                depends_on=spec.get("depends_on"),
                metadata=spec.get("metadata"),
            )
            plan.add_step(step)
        self._plans.append(plan)
        return plan

    def linear(self, name: str, descriptions: list[str]) -> Plan:
        """Create a sequential plan where each step depends on the previous.

        Step IDs are auto-assigned as 'step_1', 'step_2', etc.

        Args:
            name: Plan name.
            descriptions: List of step descriptions in order.

        Returns:
            Linear Plan.
        """
        plan = Plan(name)
        prev_id: str | None = None
        for i, desc in enumerate(descriptions, start=1):
            step_id = f"step_{i}"
            depends_on = [prev_id] if prev_id else []
            step = Step(id=step_id, description=desc, depends_on=depends_on)
            plan.add_step(step)
            prev_id = step_id
        self._plans.append(plan)
        return plan

    @property
    def plans(self) -> list[Plan]:
        return list(self._plans)

    def __repr__(self) -> str:
        return f"Planner(plans={len(self._plans)})"
