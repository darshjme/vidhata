"""Tests for Plan class."""
import pytest
from agent_planner import Step, Plan


def make_step(id_, deps=None):
    return Step(id=id_, description=f"Step {id_}", depends_on=deps)


class TestPlanInit:
    def test_empty_plan(self):
        p = Plan("my-plan")
        assert p.name == "my-plan"
        assert len(p) == 0

    def test_plan_with_steps(self):
        steps = [make_step("a"), make_step("b")]
        p = Plan("p", steps=steps)
        assert len(p) == 2

    def test_invalid_name_raises(self):
        with pytest.raises(ValueError):
            Plan("")


class TestPlanAddStep:
    def test_add_step_fluent(self):
        p = Plan("p")
        result = p.add_step(make_step("a"))
        assert result is p  # fluent

    def test_duplicate_id_raises(self):
        p = Plan("p")
        p.add_step(make_step("a"))
        with pytest.raises(ValueError, match="Duplicate"):
            p.add_step(make_step("a"))

    def test_wrong_type_raises(self):
        p = Plan("p")
        with pytest.raises(TypeError):
            p.add_step("not-a-step")


class TestPlanNextSteps:
    def test_no_deps_all_ready(self):
        p = Plan("p")
        p.add_step(make_step("a"))
        p.add_step(make_step("b"))
        ready = p.next_steps()
        assert len(ready) == 2

    def test_dep_blocks_step(self):
        p = Plan("p")
        p.add_step(make_step("a"))
        p.add_step(make_step("b", deps=["a"]))
        ready = p.next_steps(set())
        ids = [s.id for s in ready]
        assert "a" in ids
        assert "b" not in ids

    def test_dep_satisfied(self):
        p = Plan("p")
        p.add_step(make_step("a"))
        p.add_step(make_step("b", deps=["a"]))
        ready = p.next_steps({"a"})
        ids = [s.id for s in ready]
        assert "b" in ids

    def test_running_step_not_returned(self):
        p = Plan("p")
        s = make_step("a")
        s.status = "running"
        p.add_step(s)
        assert p.next_steps() == []

    def test_done_step_not_returned(self):
        p = Plan("p")
        s = make_step("a")
        s.status = "done"
        p.add_step(s)
        # next_steps with no args auto-derives completed from done steps
        assert p.next_steps() == []

    def test_auto_derive_completed_from_done(self):
        p = Plan("p")
        s1 = make_step("a")
        s1.status = "done"
        s2 = make_step("b", deps=["a"])
        p.add_step(s1)
        p.add_step(s2)
        ready = p.next_steps()
        assert any(s.id == "b" for s in ready)


class TestPlanIsComplete:
    def test_empty_plan_not_complete(self):
        p = Plan("p")
        assert p.is_complete is False

    def test_all_done(self):
        p = Plan("p")
        s = make_step("a")
        s.status = "done"
        p.add_step(s)
        assert p.is_complete is True

    def test_partial_done(self):
        p = Plan("p")
        s1 = make_step("a")
        s1.status = "done"
        p.add_step(s1)
        p.add_step(make_step("b"))
        assert p.is_complete is False


class TestPlanIsFailed:
    def test_no_failure(self):
        p = Plan("p")
        p.add_step(make_step("a"))
        assert p.is_failed is False

    def test_failed_step(self):
        p = Plan("p")
        s = make_step("a")
        s.status = "failed"
        p.add_step(s)
        assert p.is_failed is True


class TestPlanSummary:
    def test_summary_counts(self):
        p = Plan("p")
        s1, s2, s3 = make_step("a"), make_step("b"), make_step("c")
        s1.status = "done"
        s2.status = "failed"
        p.add_step(s1)
        p.add_step(s2)
        p.add_step(s3)
        sm = p.summary()
        assert sm["done"] == 1
        assert sm["failed"] == 1
        assert sm["pending"] == 1
        assert sm["total"] == 3


class TestPlanToDict:
    def test_to_dict_keys(self):
        p = Plan("p")
        p.add_step(make_step("a"))
        d = p.to_dict()
        assert "name" in d
        assert "steps" in d
        assert "summary" in d
        assert "is_complete" in d
        assert "is_failed" in d
