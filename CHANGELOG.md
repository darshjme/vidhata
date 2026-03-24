# Changelog

All notable changes to `agent-planner` are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [1.0.0] — 2026-03-24

### Added
- `Step`: single unit of work with dependency tracking, status, result, and error fields
- `Plan`: ordered execution plan with dependency-aware `next_steps()`, `is_complete`, `is_failed`, `summary()`
- `Planner`: factory with `create()`, `decompose()`, and `linear()` methods
- `PlanExecutor`: dependency-order executor with per-step handlers and failure capture
- Zero external dependencies (stdlib only)
- Full type annotations (Python 3.10+)
- 57 pytest tests with 100% feature coverage
