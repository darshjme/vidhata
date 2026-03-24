"""Tests for Step class."""
import pytest
from agent_planner import Step


class TestStepInit:
    def test_basic_creation(self):
        s = Step(id="s1", description="Do something")
        assert s.id == "s1"
        assert s.description == "Do something"
        assert s.depends_on == []
        assert s.metadata == {}
        assert s.status == "pending"
        assert s.result is None
        assert s.error is None

    def test_with_depends_on(self):
        s = Step("s2", "Step 2", depends_on=["s1"])
        assert s.depends_on == ["s1"]

    def test_with_metadata(self):
        s = Step("s1", "Step 1", metadata={"priority": 1})
        assert s.metadata == {"priority": 1}

    def test_invalid_id_raises(self):
        with pytest.raises(ValueError):
            Step(id="", description="Test")

    def test_invalid_description_raises(self):
        with pytest.raises(ValueError):
            Step(id="s1", description="")

    def test_depends_on_copy(self):
        deps = ["a", "b"]
        s = Step("s1", "desc", depends_on=deps)
        deps.append("c")
        assert s.depends_on == ["a", "b"]  # not mutated


class TestStepIsReady:
    def test_no_deps_always_ready(self):
        s = Step("s1", "desc")
        assert s.is_ready() is True
        assert s.is_ready(set()) is True
        assert s.is_ready({"x"}) is True

    def test_dep_not_completed(self):
        s = Step("s2", "desc", depends_on=["s1"])
        assert s.is_ready(set()) is False
        assert s.is_ready({"other"}) is False

    def test_dep_completed(self):
        s = Step("s2", "desc", depends_on=["s1"])
        assert s.is_ready({"s1"}) is True

    def test_multiple_deps_all_required(self):
        s = Step("s3", "desc", depends_on=["s1", "s2"])
        assert s.is_ready({"s1"}) is False
        assert s.is_ready({"s2"}) is False
        assert s.is_ready({"s1", "s2"}) is True

    def test_none_completed_uses_empty_set(self):
        s = Step("s2", "desc", depends_on=["s1"])
        assert s.is_ready(None) is False


class TestStepToDict:
    def test_to_dict_structure(self):
        s = Step("s1", "Do it", depends_on=["a"], metadata={"k": "v"})
        d = s.to_dict()
        assert d["id"] == "s1"
        assert d["description"] == "Do it"
        assert d["depends_on"] == ["a"]
        assert d["metadata"] == {"k": "v"}
        assert d["status"] == "pending"
        assert d["result"] is None
        assert d["error"] is None

    def test_to_dict_after_mutation(self):
        s = Step("s1", "desc")
        s.status = "done"
        s.result = 42
        d = s.to_dict()
        assert d["status"] == "done"
        assert d["result"] == 42
