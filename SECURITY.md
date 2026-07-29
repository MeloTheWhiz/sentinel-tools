# Security Policy

## Security Philosophy

Sentinel Tools is designed with a **read-first** philosophy.

Its primary purpose is to inspect and assess system health without making unexpected modifications to a user's system.

Whenever possible, diagnostics should be:

- Read-only
- Transparent
- Reproducible
- Explainable

---

## Supported Versions

Currently, only the latest development version is actively supported.

| Version | Supported |
|----------|-----------|
| v0.2.x-alpha | ✅ Yes |
| Earlier versions | ❌ No |

---

## Reporting Security Issues

If you discover a security issue in Sentinel Tools, please do **not** open a public issue immediately.

Instead:

1. Gather the relevant details.
2. Include steps to reproduce the issue.
3. Describe the potential impact.
4. Contact the maintainer privately.

Please include:

- Sentinel Tools version
- Operating system
- Python version
- Relevant terminal output
- Sanitized logs (remove sensitive information)

---

## Privacy

Sentinel Tools attempts to minimize the collection of sensitive information.

Reports should avoid exposing:

- Passwords
- Authentication tokens
- SSH private keys
- Browser cookies
- Personal documents
- Email contents
- Encryption keys

Users are encouraged to review generated reports before sharing them publicly.

---

## Safety Principles

Sentinel Tools follows these principles:

- Diagnostics should default to read-only.
- Potentially destructive operations must require explicit user confirmation.
- Recommendations should explain why they are suggested.
- Reports should avoid unnecessary personal information.
- Errors should fail safely and provide useful diagnostics.

---

## Responsible Disclosure

If a vulnerability could impact users or expose sensitive information:

- Do not publish exploit details immediately.
- Allow time for investigation and remediation.
- Coordinate disclosure with the project maintainer whenever possible.

---

## Future Security Goals

As Sentinel Tools evolves, planned improvements include:

- Report sanitization improvements
- Configurable privacy levels
- Digital signatures for releases
- Automated security testing
- Dependency vulnerability scanning
- Secure plugin validation
- Optional encrypted report storage

---

## Third-Party Software

Sentinel Tools relies on trusted third-party software where appropriate.

Examples include:

- Python
- systemd
- Git
- pytest
- Ruff

The project should avoid unnecessary dependencies and regularly review existing ones.

---

## Contact

Security-related questions, concerns, or vulnerability reports should be directed to the project maintainer through GitHub or another published contact method.

---

Security is an ongoing process. Improving the safety, transparency, and reliability of Sentinel Tools is a continuous goal.
