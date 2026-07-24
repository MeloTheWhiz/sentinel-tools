# Sentinel Tools

Sentinel Tools is a command-line toolkit for **safe Arch Linux maintenance, system diagnostics, health scoring, and shareable reports**.

> **Alpha software:** Sentinel Tools 0.1.x currently supports Arch Linux only. Windows, macOS, additional Linux distributions, and FreeBSD are planned. Test on non-critical systems and review reports before sharing them.

## Features

- System health diagnostics and a score from 0 to 100
- Security, network, and storage checks
- Text, JSON, and HTML reports
- Optional redaction of sensitive report data
- Guided Arch Linux updates and cleanup
- Plugin-based diagnostic checks
- Interactive menu and direct CLI commands

## Requirements

- Arch Linux or an Arch-based distribution
- Python 3.11 or newer
- Git
- `pipx` for the recommended tester installation

## Recommended installation for testers

`pipx` installs Sentinel Tools into an isolated environment. Testers do **not** need to create or manage a Python virtual environment.

### 1. Install Git and pipx

```bash
sudo pacman -S --needed git python-pipx
pipx ensurepath
```

Close and reopen the terminal if requested.

### 2. Clone the repository

```bash
git clone https://github.com/MeloTheWhiz/sentinel-tools.git
cd sentinel-tools
git switch feature/v0.2-release-prep
```

Replace `USERNAME` with the repository owner's GitHub username.

### 3. Install Sentinel Tools

```bash
pipx install .
```

Verify the installation:

```bash
sentinel-tools --version
sentinel-tools --help
```

A shorter command is also installed:

```bash
sentinel --help
```

## Quick start

```bash
sentinel-tools menu
sentinel-tools health
sentinel-tools checks
sentinel-tools security
sentinel-tools network
sentinel-tools storage
```

## Reports

Create a text report:

```bash
sentinel-tools report
```

Create a redacted HTML report:

```bash
sentinel-tools report --format html --redact
```

Choose a destination:

```bash
sentinel-tools report --format json --redact --output ~/Documents/sentinel-report.json
```

Filter findings:

```bash
sentinel-tools report --severity warning
sentinel-tools report --finding-code JRN001
```

Default reports are saved in the user's home directory:

- `~/sentinel-tools-report.txt`
- `~/sentinel-tools-report.json`
- `~/sentinel-tools-report.html`

Review every report before posting it publicly, even when `--redact` is used.

## Maintenance commands

```bash
sentinel-tools update
sentinel-tools clean
```

Maintenance commands may request administrator access through `sudo`. Read each prompt before approving a change.

## Updating a tester installation

From the cloned repository:

```bash
git pull
pipx reinstall sentinel-tools
```

## Uninstalling

```bash
pipx uninstall sentinel-tools
```

The configuration file may remain at:

```text
~/.config/sentinel-tools/config.toml
```

## Developer setup

```bash
git clone https://github.com/MeloTheWhiz/sentinel-tools.git
cd sentinel-tools
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run validation:

```bash
ruff format --check .
ruff check .
pytest -q
```

## Reporting test results

Include the following in a GitHub issue:

- Sentinel Tools version: `sentinel-tools --version`
- Distribution and kernel: `uname -a`
- Desktop environment or window manager
- Exact command used
- Expected behavior
- Actual behavior and full error output
- A reviewed, redacted report when relevant

Never post passwords, tokens, private keys, serial numbers, or an unreviewed report.

## Platform status

| Platform | Status |
|---|---|
| Arch Linux | Alpha testing |
| Other Linux distributions | Planned |
| Windows | Planned |
| macOS | Planned |
| FreeBSD | Planned |

## Safety

Sentinel Tools prefers inspection and guided actions, but no diagnostic utility can guarantee that a system is secure or fault-free. Keep backups, review commands, and test alpha releases on systems where recovery is possible.
