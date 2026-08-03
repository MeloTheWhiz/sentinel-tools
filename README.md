# Sentinel Tools

Sentinel Tools is an open-source command-line toolkit for system diagnostics, health assessment, safe maintenance, and shareable reports.

The project began as an Arch Linux utility and is being redesigned around a shared platform layer for Linux, Windows, macOS, and FreeBSD.

> **Development status:** Sentinel Tools is alpha software. Arch Linux currently has the most complete diagnostic support. The cross-platform `system-info` foundation is under active development.

## Current capabilities

### Cross-platform foundation

- Automatic operating-system detection
- Shared platform interface
- Shared CPU, memory, disk, and system-information models
- Initial Linux implementation
- Initial Windows implementation
- Initial macOS implementation
- Initial FreeBSD implementation
- Unified `system-info` command

### Arch Linux diagnostics

- System health diagnostics and scoring
- Security inspection
- Network diagnostics
- Storage diagnostics
- Failed service detection
- Journal error analysis
- Package database checks
- Guided update and cleanup commands
- Read-only AUR and foreign-package audit
- Text, JSON, and HTML reports
- Optional report redaction
- Plugin-based diagnostic checks

## Platform support

| Capability | Arch Linux | Other Linux | Windows | macOS | FreeBSD |
|---|---:|---:|---:|---:|---:|
| Platform detection | Yes | Initial | Initial | Initial | Initial |
| `system-info` | Yes | Initial | Initial | Initial | Initial |
| CPU information | Yes | Initial | Initial | Initial | Initial |
| Memory information | Yes | Initial | Initial | Initial | Initial |
| Mounted storage information | Yes | Initial | Initial | Initial | Initial |
| Health diagnostics | Yes | No | No | No | No |
| Security diagnostics | Yes | No | No | No | No |
| Network diagnostics | Yes | No | No | No | No |
| Storage diagnostics | Yes | No | No | No | No |
| Reports | Yes | No | No | No | No |
| AUR audit | Optional | No | No | No | No |

“Initial” means that the platform implementation and shared models exist, but they still require testing on real systems and additional platform-specific diagnostics.

## Requirements

For the current tester installation:

- Python 3.11 or newer
- Git
- `pipx` recommended for users
- Arch Linux for the complete diagnostic command set

Standalone executables and native platform packages are planned for future releases.

## Recommended tester installation

Clone the repository:

```bash
git clone https://github.com/MeloTheWhiz/sentinel-tools.git
cd sentinel-tools
```

Switch to the current development branch when testing unreleased v0.3 work:

```bash
git switch feature/v0.3-platform-core
```

Install `pipx` on Arch Linux:

```bash
sudo pacman -S --needed python-pipx
pipx ensurepath
```

Close and reopen the terminal if `pipx` requests it.

Install Sentinel Tools:

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

## Updating a tester installation

From the cloned repository:

```bash
git pull
pipx reinstall sentinel-tools
```

## Quick start

Display platform-neutral system information:

```bash
sentinel-tools system-info
```

Open the interactive menu:

```bash
sentinel-tools menu
```

Run the Arch Linux health assessment:

```bash
sentinel-tools health
```

Run individual Arch Linux diagnostics:

```bash
sentinel-tools security
sentinel-tools network
sentinel-tools storage
```

Inspect registered diagnostic checks:

```bash
sentinel-tools checks
```

Run the read-only AUR audit:

```bash
sentinel-tools aur
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

Create a redacted JSON report at a chosen location:

```bash
sentinel-tools report \
    --format json \
    --redact \
    --output ~/Documents/sentinel-report.json
```

Filter reports by severity or finding code:

```bash
sentinel-tools report --severity warning
sentinel-tools report --finding-code JRN001
```

Default report destinations are:

```text
~/sentinel-tools-report.txt
~/sentinel-tools-report.json
~/sentinel-tools-report.html
```

Always review a report before sharing it. Redaction reduces exposure but should not be treated as a guarantee that every sensitive value has been removed.

## Maintenance commands

Update Arch Linux and supported package sources:

```bash
sentinel-tools update
```

Run guided cleanup:

```bash
sentinel-tools clean
```

Maintenance and some diagnostic operations may request administrator access. Read every prompt before approving a command.

## Privacy and safety

Diagnostic output may contain sensitive local information, including:

- Hostnames
- Usernames
- Home-directory paths
- Local and public IP addresses
- MAC addresses
- Wi-Fi network names
- Listening ports
- Service names
- Hardware identifiers
- Log messages

Do not publish raw terminal output or unreviewed reports.

Sentinel Tools prefers read-only inspection and guided actions, but no diagnostic utility can guarantee that a computer is secure, healthy, or fault-free. Keep backups and test alpha releases on systems where recovery is possible.

See [SECURITY.md](SECURITY.md) for security reporting and project safety guidance.

## Developer setup

Clone the repository:

```bash
git clone https://github.com/MeloTheWhiz/sentinel-tools.git
cd sentinel-tools
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the project and development dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run validation:

```bash
python -m ruff format --check .
python -m ruff check .
pytest -q
```

At the current v0.3 platform-core checkpoint, the project has 140 passing automated tests.

## Project architecture

The application is being separated into shared and platform-specific layers:

```text
Command-line interface
        |
        v
SentinelApp
        |
        +---- Shared models
        |
        +---- Platform detector
                 |
                 +---- LinuxPlatform
                 +---- WindowsPlatform
                 +---- MacOSPlatform
                 +---- FreeBSDPlatform
        |
        +---- Diagnostic engine
        +---- Health scoring
        +---- Reports
        +---- Plugins
```

Platform-specific code collects information differently on each operating system while returning the same shared model types.

## Project documentation

- [CHANGELOG.md](CHANGELOG.md) — notable release changes
- [ROADMAP.md](ROADMAP.md) — planned development
- [CONTRIBUTING.md](CONTRIBUTING.md) — contributor guidance
- [SECURITY.md](SECURITY.md) — security policy
- [docs/TESTING.md](docs/TESTING.md) — testing instructions

Additional architecture, platform-support, command, and development-history documentation is planned.

## Roadmap summary

Current v0.3 goals:

- Complete the shared platform foundation
- Test Linux, Windows, macOS, and FreeBSD implementations on real systems
- Move platform-neutral reporting onto shared models
- Remove remaining Linux assumptions from reusable code
- Preserve Arch-specific functionality behind explicit platform checks

Longer-term goals include:

- Hardware inventory
- GPU and battery information
- Cross-platform networking
- Cross-platform security checks
- Native packages and standalone executables
- Interactive terminal interface
- Graphical desktop interface

See [ROADMAP.md](ROADMAP.md) for more detail.

## Contributing

Bug reports, tests, documentation improvements, platform testing, and code contributions are welcome.

Before submitting changes:

```bash
python -m ruff format --check .
python -m ruff check .
pytest -q
```

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## License

Sentinel Tools is licensed under the [MIT License](LICENSE).
