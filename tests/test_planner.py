"""Tests for Planner class."""
import pytest
from agent_planner import Planner, Plan, Step


class TestPlannerCreate:
    def test_create_returns_plan(self):
        pl = Planner()
        p = pl.create("my-plan")
        assert isinstance(p, Plan)
        assert p.name == "my-plan"

    def test_create_registers_plan(self):
        pl = Planner()
        pl.create("a")
        pl.create("b")
        assert len(pl.plans) == 2


class TestPlannerDecompose:
    def test_basic_decompose(self):
        pl = Planner()
        p = pl.decompose("Build API", [
            {"id": "design", "description": "Design schema"},
            {"id": "models", "description": "Write models", "depends_on": ["design"]},
            {"id": "endpoints", "description": "Implement endpoints", "depends_on": ["models"]},
            {"id": "tests", "description": "Add tests", "depends_on": ["endpoints"]},
        ])
        assert isinstance(p, Plan)
        assert len(p) == 4
        assert p.name == "Build API"

    def test_decompose_deps_preserved(self):
        pl = Planner()
        p = pl.decompose("task", [
            {"id": "a", "description": "A"},
            {"id": "b", "description": "B", "depends_on": ["a"]},
        ])
        b = p.get_step("b")
        assert b.depends_on == ["a"]

    def test_decompose_missing_id_raises(self):
        pl = Planner()
        with pytest.raises(ValueError):
            pl.decompose("t", [{"description": "no id"}])

    def test_decompose_missing_description_raises(self):
        pl = Planner()
        with pytest.raises(ValueError):
            pl.decompose("t", [{"id": "a"}])

    def test_decompose_with_metadata(self):
        pl = Planner()
        p = pl.decompose("t", [
            {"id": "a", "description": "A", "metadata": {"timeout": 30}},
        ])
        assert p.get_step("a").metadata == {"timeout": 30}


class TestPlannerLinear:
    def test_linear_creates_sequential(self):
        pl = Planner()
        p = pl.linear("pipeline", ["Step A", "Step B", "Step C"])
        assert len(p) == 3
        steps = p.steps
        assert steps[0].id == "step_1"
        assert steps[1].id == "step_2"
        assert steps[2].id == "step_3"
        assert steps[0].depends_on == []
        assert steps[1].depends_on == ["step_1"]
        assert steps[2].depends_on == ["step_2"]

    def test_linear_empty(self):
        pl = Planner()
        p = pl.linear("empty", [])
        assert len(p) == 0

    def test_linear_single_step(self):
        pl = Planner()
        p = pl.linear("single", ["only step"])
        assert len(p) == 1
        assert p.steps[0].depends_on == []

    def test_linear_descriptions_preserved(self):
        pl = Planner()
        descs = ["Alpha", "Beta", "Gamma"]
        p = pl.linear("p", descs)
        for step, desc in zip(p.steps, descs):
            assert step.description == desc
