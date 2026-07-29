# Sentinel Tools Alpha Testing Guide

Thank you for testing Sentinel Tools.

This guide explains how to install the project, run its diagnostics, generate reports, and submit useful feedback during the alpha phase.

---

## Important Notice

Sentinel Tools is early alpha software.

Although the project is designed to favor safe, read-only diagnostics, bugs and incomplete behavior are still possible. Test on a non-critical system whenever possible.

Do not share reports publicly without reviewing them for private or sensitive information.

---

## Supported Environment

Current primary platform:

- Arch Linux

Recommended environment:

- Python 3.11 or newer
- Git
- A terminal
- A system using systemd

Other Linux distributions may run parts of the project, but they are not yet officially supported.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/MeloTheWhiz/sentinel-tools.git
cd sentinel-tools
```

Switch to the alpha testing branch when instructed:

```bash
git switch develop
git pull
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install Sentinel Tools:

```bash
pip install -e .
```

Confirm that the command is available:

```bash
sentinel-tools --help
```

---

## Record the Test Environment

Before testing, collect the following information:

```bash
uname -a
python --version
cat /etc/os-release
```

Also record:

- Desktop environment or window manager
- Whether the system is physical hardware or a virtual machine
- Whether NetworkManager is used
- Filesystem type
- Any unusual system configuration

Remove hostnames, usernames, IP addresses, serial numbers, and other sensitive information before sharing output.

---

## Basic Smoke Test

Run:

```bash
sentinel-tools --help
```

Confirm that:

- The command starts without crashing
- Help text is readable
- Available commands are listed

Run the health command:

```bash
sentinel-tools health
```

Confirm that:

- A health result appears
- The score is within the expected range
- Findings are understandable
- No traceback appears

---

## Diagnostic Commands

Test the available commands individually:

```bash
sentinel-tools health
sentinel-tools storage
sentinel-tools security
sentinel-tools network
sentinel-tools report
```

For each command, record:

- Whether it completed
- How long it took
- Whether the output was understandable
- Whether any result appeared incorrect
- Whether a traceback or warning appeared

---

## Report Testing

Generate a text report:

```bash
sentinel-tools report \
    --format text \
    --output report.txt
```

Generate a JSON report:

```bash
sentinel-tools report \
    --format json \
    --output report.json
```

Generate an HTML report:

```bash
sentinel-tools report \
    --format html \
    --output report.html
```

Confirm that:

- Each file is created
- Each file is not empty
- The text report is readable
- The JSON report is valid JSON
- The HTML report opens correctly in a browser
- Findings are consistent between formats
- Sensitive information is handled appropriately

Validate the JSON report with:

```bash
python -m json.tool report.json >/dev/null
```

No output means the JSON syntax is valid.

---

## Automated Tests

Install development tools if necessary:

```bash
pip install pytest ruff
```

Run the test suite:

```bash
pytest -v
```

Run code-quality checks:

```bash
ruff check .
ruff format --check .
```

Record the complete summary, including the number of passed, failed, skipped, or errored tests.

---

## Things to Look For

Pay particular attention to:

- Incorrect health scores
- Duplicate findings
- Missing finding codes
- Confusing severity labels
- Empty or malformed reports
- HTML pages that appear blank
- Commands that require unexpected privileges
- Long delays or apparent hangs
- Incorrect storage percentages
- False service warnings
- Private information appearing in reports
- Unclear recommendations
- Unhandled exceptions or tracebacks

---

## Reporting a Bug

Include:

- A clear title
- Operating system and version
- Python version
- Sentinel Tools branch or commit
- Exact command used
- Expected result
- Actual result
- Steps to reproduce
- Relevant sanitized terminal output
- Whether the issue happens every time

Example:

```text
Title:
HTML report opens as a blank page in Firefox

Environment:
Arch Linux
Python 3.14.6
Firefox 152

Command:
sentinel-tools report --format html --output report.html

Expected:
A visible health report

Actual:
The file is created, but Firefox displays a blank page

Reproducible:
Yes
```

---

## Privacy and Sanitization

Before sharing output, remove or replace:

- Usernames
- Hostnames
- Home-directory paths
- IP addresses
- MAC addresses
- Wi-Fi network names
- Drive serial numbers
- Device identifiers
- Email addresses
- Tokens, keys, and passwords

Never include authentication secrets in a bug report.

---

## Feedback Questions

Useful feedback includes answers to questions such as:

- Was installation straightforward?
- Were the commands easy to discover?
- Did the health score seem reasonable?
- Were finding descriptions understandable?
- Were recommendations useful?
- Did reports look professional?
- Was anything confusing or misleading?
- What feature felt most valuable?
- What important diagnostic was missing?

---

## Cleaning Up

Deactivate the virtual environment:

```bash
deactivate
```

Remove the local test copy when finished:

```bash
cd ..
rm -rf sentinel-tools
```

Only run the removal command after confirming that the directory contains no work you need to keep.

---

## Thank You

Alpha testing helps identify real-world problems that automated tests cannot always detect.

Clear, reproducible, and privacy-conscious feedback is especially valuable.
