# Contributing

Contributions are welcome! Please follow these guidelines.

## Getting Started

```bash
git clone https://github.com/darshjme-codes/agent-planner
cd agent-planner
pip install -e ".[dev]"
```

## Running Tests

```bash
PYTHONPATH=src python -m pytest tests/ -v
```

## Code Style

- Type annotations required for all public APIs
- Docstrings on all public classes and methods
- No external runtime dependencies

## Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/my-feature`)
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request with a clear description

## Reporting Issues

Open an issue at https://github.com/darshjme-codes/agent-planner/issues with:
- Python version
- Minimal reproduction case
- Expected vs actual behavior
