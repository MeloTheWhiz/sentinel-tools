# Sentinel Tools

<div align="center">

## Cross-Platform System Diagnostics & Health Assessment Toolkit

Professional system inspection, health scoring, diagnostics, and reporting.

**Current Status:** 🚧 Early Alpha (v0.2.0-alpha)

</div>

---

## Overview

Sentinel Tools is a Python-based system diagnostics and health assessment toolkit designed to help users, IT professionals, consultants, and system administrators better understand the health of their systems.

Rather than simply displaying raw system information, Sentinel Tools analyzes collected data, identifies potential issues, assigns a health score, and produces professional reports with actionable recommendations.

The project is being developed with a long-term goal of supporting multiple operating systems while maintaining a modular architecture.

---

## Current Platform

✅ Arch Linux

Future support:

- Ubuntu
- Debian
- Fedora
- openSUSE
- Windows
- macOS
- FreeBSD

---

## Features

## Health Assessment

- Overall Health Score
- Severity Levels
- Stable Finding Codes
- System Summary

---

## Diagnostics

- Failed system services
- Failed user services
- Journal analysis
- Package database verification
- Orphan package detection
- NetworkManager health
- Time synchronization
- Root filesystem usage

---

## Reporting

Generate:

- Text reports
- JSON reports
- HTML reports

Features include:

- Report redaction
- Severity filtering
- Finding-code filtering

---

## Installation

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

Install:

```bash
pip install -e .
```

Verify:

```bash
sentinel-tools --help
```

---

## Example Commands

Health

```bash
sentinel-tools health
```

Storage

```bash
sentinel-tools storage
```

Security

```bash
sentinel-tools security
```

Generate HTML report

```bash
sentinel-tools report \
    --format html \
    --output report.html
```

Generate JSON report

```bash
sentinel-tools report \
    --format json \
    --output report.json
```

Generate Text report

```bash
sentinel-tools report \
    --format text \
    --output report.txt
```

---

## Current Findings

| Code | Meaning |
|------|---------|
| SVC001 | NetworkManager inactive |
| SVC002 | Time synchronization inactive |
| STR001 | Root filesystem critical |
| STR002 | Root filesystem warning |

---

## Development

Run tests

```bash
pytest
```

Run Ruff

```bash
ruff check .
ruff format --check .
```

---

## Roadmap

Upcoming work includes:

- CPU diagnostics
- Battery health
- SMART improvements
- Security scoring
- Historical reports
- HTML dashboard redesign
- Cross-platform support

---

## Contributing

The project is currently in active alpha development.

Bug reports, suggestions, testing feedback, and pull requests are welcome.

---

## Author

**Carmelo A. Acevedo**

GitHub: [MeloTheWhiz](https://github.com/MeloTheWhiz)

---

## License

Sentinel Tools is released under the [MIT License](LICENSE).
