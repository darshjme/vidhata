# agent-planner

**Task decomposition and execution planning for AI agents.**

Complex agent tasks need structured breaking-down. Without it, agents attempt everything at once, lose track of progress, and can't recover from partial failures.

```
"build a REST API"  →  design schema → write models → implement endpoints → add tests
```

## Installation

```bash
pip install agent-planner
```

## Quickstart: Multi-Step API Build Plan

```python
from agent_planner import Planner, PlanExecutor

# 1. Create a planner
planner = Planner()

# 2. Decompose a complex task into dependency-ordered steps
plan = planner.decompose("Build REST API", [
    {"id": "schema",    "description": "Design database schema"},
    {"id": "models",    "description": "Write ORM models",         "depends_on": ["schema"]},
    {"id": "endpoints", "description": "Implement API endpoints",   "depends_on": ["models"]},
    {"id": "auth",      "description": "Add authentication",        "depends_on": ["models"]},
    {"id": "tests",     "description": "Write test suite",          "depends_on": ["endpoints", "auth"]},
    {"id": "docs",      "description": "Generate API documentation", "depends_on": ["endpoints"]},
])

print(f"Plan: {plan.name} ({len(plan)} steps)")
# Plan: Build REST API (6 steps)

# 3. Define handlers for each step (callables that receive the Step object)
def run_schema(step):
    print(f"  [schema] Designing tables...")
    return {"tables": ["users", "posts", "tokens"]}

def run_models(step):
    print(f"  [models] Writing SQLAlchemy models...")
    return {"files": ["models/user.py", "models/post.py"]}

def run_endpoints(step):
    print(f"  [endpoints] Implementing CRUD endpoints...")
    return {"routes": ["/users", "/posts"]}

def run_auth(step):
    print(f"  [auth] Setting up JWT middleware...")
    return {"middleware": "JWTBearer"}

def run_tests(step):
    print(f"  [tests] Writing pytest suite...")
    return {"coverage": "92%"}

def run_docs(step):
    print(f"  [docs] Generating OpenAPI spec...")
    return {"url": "/docs"}

handlers = {
    "schema":    run_schema,
    "models":    run_models,
    "endpoints": run_endpoints,
    "auth":      run_auth,
    "tests":     run_tests,
    "docs":      run_docs,
}

# 4. Execute in dependency order (parallel-safe ordering)
executor = PlanExecutor(plan, handlers)
summary = executor.run()

print(f"\nResult: {summary}")
# Result: {'pending': 0, 'running': 0, 'done': 6, 'failed': 0, 'total': 6}

print(f"Complete: {plan.is_complete}")
# Complete: True

# 5. Inspect step results
for step in plan.steps:
    print(f"  {step.id}: {step.status} → {step.result}")
```

## Linear Plans

For simple sequential pipelines:

```python
plan = planner.linear("Deploy Pipeline", [
    "Run unit tests",
    "Build Docker image",
    "Push to registry",
    "Deploy to staging",
    "Run smoke tests",
    "Promote to production",
])
# Each step auto-depends on the previous one.
```

## Core API

### `Step`

```python
Step(
    id="step-id",
    description="What this step does",
    depends_on=["other-step-id"],   # optional
    metadata={"timeout": 30},        # optional
)

step.is_ready(completed: set[str]) -> bool  # True if deps satisfied
step.to_dict() -> dict
step.status   # "pending" | "running" | "done" | "failed"
step.result   # set by executor on success
step.error    # set by executor on failure
```

### `Plan`

```python
plan = Plan("name")
plan.add_step(step)                          # fluent, validates duplicate IDs
plan.next_steps(completed=None) -> list[Step]  # ready-to-run steps
plan.is_complete   # bool: all steps done
plan.is_failed     # bool: any step failed
plan.summary()     # {"pending":0, "done":6, "total":6, ...}
plan.to_dict()
```

### `Planner`

```python
planner = Planner()
planner.create("name") -> Plan                        # empty plan
planner.decompose("task", [{id, description, ...}]) -> Plan
planner.linear("name", ["desc1", "desc2"]) -> Plan    # sequential
```

### `PlanExecutor`

```python
executor = PlanExecutor(plan, handlers={step_id: callable})
executor.run() -> dict          # executes all steps, returns summary
executor.run_step(step_id) -> bool  # execute single step
```

**Handler signature:** `def my_handler(step: Step) -> Any` — return value stored in `step.result`.

## Error Handling

```python
def risky_handler(step):
    raise ValueError("Database connection failed")

executor = PlanExecutor(plan, {"db": risky_handler})
executor.run()

db_step = plan.get_step("db")
print(db_step.status)   # "failed"
print(db_step.error)    # "ValueError: Database connection failed\n..."
print(plan.is_failed)   # True
```

## Why agent-planner?

| Without                          | With                              |
|----------------------------------|-----------------------------------|
| Attempt everything at once       | Structured dependency ordering    |
| No progress tracking             | Step-level status: pending/running/done/failed |
| Can't recover from failures      | Failed steps captured with errors  |
| Unclear execution order          | Explicit `depends_on` graph        |
| Hard to inspect state            | `summary()`, `to_dict()`, `is_complete` |

## License

MIT © Darshankumar Joshi
