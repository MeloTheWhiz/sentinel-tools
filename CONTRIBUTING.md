# Contributing to Sentinel Tools

Thank you for your interest in contributing to Sentinel Tools.

Sentinel Tools is currently in early alpha development. Contributions, testing feedback, bug reports, documentation improvements, and feature suggestions are welcome.

---

## Project Goals

Sentinel Tools aims to help users understand the health of their computers through:

- Clear diagnostics
- Stable finding codes
- Health scoring
- Actionable recommendations
- Professional reports
- Cross-platform support

Contributions should support these goals while keeping the project safe, understandable, and maintainable.

---

## Development Setup

Clone the repository:

```bash
git clone https://github.com/MeloTheWhiz/sentinel-tools.git
cd sentinel-tools
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the project in editable mode:

```bash
pip install -e .
```

Install development tools if needed:

```bash
pip install pytest ruff
```

---

## Running Tests

Run the complete test suite:

```bash
pytest
```

Run tests with more detailed output:

```bash
pytest -v
```

All tests should pass before submitting changes.

---

## Code Quality

Run Ruff:

```bash
ruff check .
```

Check formatting:

```bash
ruff format --check .
```

Apply formatting:

```bash
ruff format .
```

---

## Branch Workflow

Create a feature branch from the current development branch:

```bash
git switch develop
git pull
git switch -c feature/short-description
```

Use clear branch names, such as:

```text
feature/cpu-diagnostics
fix/html-report-rendering
docs/testing-guide
```

Avoid making feature changes directly on `main` or `develop`.

---

## Commit Messages

Use concise, descriptive commit messages.

Examples:

```text
Add CPU load diagnostics
Fix HTML report rendering
Document alpha testing process
Refactor storage finding generation
```

Keep each commit focused on one logical change.

---

## Pull Requests

Before opening a pull request:

- Run the full test suite
- Run Ruff checks
- Review your changes with `git diff`
- Update documentation when behavior changes
- Add or update tests for new functionality
- Avoid committing generated reports, caches, or virtual environments

Pull requests should explain:

- What changed
- Why the change was needed
- How it was tested
- Any known limitations

---

## Reporting Bugs

When reporting a bug, include:

- Operating system and version
- Python version
- Sentinel Tools version or commit
- Command that was run
- Expected behavior
- Actual behavior
- Relevant terminal output
- Whether the issue is reproducible

Remove personal or sensitive information before sharing reports or logs.

---

## Suggesting Features

Feature suggestions should explain:

- The problem being solved
- Who benefits from it
- The proposed behavior
- Whether it is platform-specific
- Any safety or privacy concerns

Sentinel Tools should prioritize useful diagnostics over unnecessary complexity.

---

## Safety Principles

Sentinel Tools should default to safe, read-only diagnostics.

Changes that modify the system should:

- Be clearly labeled
- Explain what will change
- Require explicit user confirmation
- Avoid destructive behavior
- Provide recovery guidance where possible

---

## Documentation

Documentation contributions are welcome.

Use clear language and practical examples. Avoid assuming that every reader is an experienced system administrator.

When adding a new diagnostic check, document:

- What it checks
- Why it matters
- Finding codes it can produce
- Severity behavior
- Suggested remediation

---

## License

By contributing to Sentinel Tools, you agree that your contributions will be licensed under the project’s MIT License.
