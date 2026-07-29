# Changelog

All notable changes to Sentinel Tools will be documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning.

---

## [0.2.0] - 2026-07-29

### Added

- System health scoring from 0 to 100
- Severity levels and stable issue codes
- Central issue catalog with explanations and recommendations
- Text, JSON, and HTML report generation
- Optional report redaction
- Report filtering by severity and issue code
- Journal analysis
- Storage diagnostics
- Failed system service detection
- Failed user service detection
- Security and network diagnostics
- Diagnostic check registry
- Plugin loading and example plugin integration
- Read-only AUR and foreign package security audit
- AUR update detection through `yay`
- Binary AUR package warnings
- Interactive menu and direct CLI commands
- Short `sentinel` command alias
- Repair registry foundation for future guided repairs
- Expanded automated test coverage

### Changed

- Reorganized command handling through the application layer
- Improved CLI help text and command structure
- Improved exception handling and test behavior
- Improved health scoring for journal findings
- Improved internal project structure
- Expanded documentation and tester installation instructions
- Expanded the project roadmap for additional operating systems

### Safety

- The AUR audit is read-only and does not build, install, update, or remove packages.
- Maintenance commands remain explicit and may request confirmation or administrator access.

---

## [0.1.1]

### Added

- Initial command-line interface
- Basic diagnostic checks
- Modular Python package layout
- Pytest test suite
