"""Tests for PlanExecutor class."""
import pytest
from agent_planner import Plan, Step, Planner, PlanExecutor


def make_plan(*step_ids):
    """Create a plan with given IDs (no deps)."""
    p = Plan("test")
    for sid in step_ids:
        p.add_step(Step(id=sid, description=f"Step {sid}"))
    return p


class TestPlanExecutorInit:
    def test_basic_init(self):
        p = make_plan("a")
        ex = PlanExecutor(p, {})
        assert ex.plan is p

    def test_wrong_type_raises(self):
        with pytest.raises(TypeError):
            PlanExecutor("not-a-plan", {})

    def test_handlers_copied(self):
        p = make_plan("a")
        h = {"a": lambda s: 1}
        ex = PlanExecutor(p, h)
        h["b"] = lambda s: 2
        assert "b" not in ex.handlers  # not mutated


class TestRunStep:
    def test_run_step_no_handler_marks_done(self):
        p = make_plan("a")
        ex = PlanExecutor(p)
        result = ex.run_step("a")
        assert result is True
        assert p.get_step("a").status == "done"

    def test_run_step_with_handler(self):
        p = make_plan("a")
        calls = []
        ex = PlanExecutor(p, {"a": lambda s: calls.append(s.id) or "ok"})
        result = ex.run_step("a")
        assert result is True
        assert "a" in calls
        assert p.get_step("a").result == "ok"

    def test_run_step_handler_exception_marks_failed(self):
        p = make_plan("a")
        ex = PlanExecutor(p, {"a": lambda s: (_ for _ in ()).throw(RuntimeError("boom"))})
        result = ex.run_step("a")
        assert result is False
        step = p.get_step("a")
        assert step.status == "failed"
        assert "RuntimeError" in step.error

    def test_run_step_already_done_returns_true(self):
        p = make_plan("a")
        p.get_step("a").status = "done"
        ex = PlanExecutor(p)
        assert ex.run_step("a") is True

    def test_run_step_already_failed_returns_false(self):
        p = make_plan("a")
        p.get_step("a").status = "failed"
        ex = PlanExecutor(p)
        assert ex.run_step("a") is False

    def test_run_step_unknown_id_raises(self):
        p = make_plan("a")
        ex = PlanExecutor(p)
        with pytest.raises(KeyError):
            ex.run_step("nonexistent")


class TestRun:
    def test_run_simple_plan(self):
        pl = Planner()
        p = pl.linear("pipeline", ["A", "B", "C"])
        order = []
        handlers = {
            "step_1": lambda s: order.append("step_1"),
            "step_2": lambda s: order.append("step_2"),
            "step_3": lambda s: order.append("step_3"),
        }
        ex = PlanExecutor(p, handlers)
        summary = ex.run()
        assert order == ["step_1", "step_2", "step_3"]
        assert summary["done"] == 3
        assert p.is_complete

    def test_run_parallel_steps(self):
        p = Plan("parallel")
        p.add_step(Step("a", "A"))
        p.add_step(Step("b", "B"))
        p.add_step(Step("c", "C", depends_on=["a", "b"]))
        executed = []
        handlers = {
            "a": lambda s: executed.append("a"),
            "b": lambda s: executed.append("b"),
            "c": lambda s: executed.append("c"),
        }
        ex = PlanExecutor(p, handlers)
        summary = ex.run()
        assert summary["done"] == 3
        assert "c" in executed
        assert executed.index("c") > executed.index("a")
        assert executed.index("c") > executed.index("b")

    def test_run_with_failure(self):
        p = make_plan("a", "b")
        ex = PlanExecutor(p, {"a": lambda s: (_ for _ in ()).throw(ValueError("fail"))})
        summary = ex.run()
        assert summary["failed"] >= 1

    def test_run_no_handlers(self):
        pl = Planner()
        p = pl.linear("t", ["x", "y"])
        ex = PlanExecutor(p)
        summary = ex.run()
        assert summary["done"] == 2

    def test_run_returns_summary_dict(self):
        p = make_plan("x")
        ex = PlanExecutor(p)
        result = ex.run()
        assert isinstance(result, dict)
        assert "done" in result
        assert "total" in result
