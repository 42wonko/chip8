# ADR-007 — Use `pyproject.toml` as the Single Source of Project Configuration

**Author:** Michael Dlubatz

**Date:** 2026-07-01

**Status:** Accepted

---

## Title

Use `pyproject.toml` as the authoritative source for project metadata
and tool configuration.

---

## Context

The project uses several development tools, including

- Python packaging,
- Ruff,
- mypy,
- PyQt6,
- CMake,
- Doxygen.

Many of these tools permit configuration in dedicated configuration
files.

Examples include

- `ruff.toml`
- `mypy.ini`
- `setup.cfg`
- `setup.py`

Using multiple configuration files distributes project information
across the repository and increases the likelihood of inconsistent
settings.

The project therefore requires a single authoritative location for
project metadata and tool configuration whenever supported.

---

## Alternatives Considered

### Option 1 — One Configuration File per Tool

Each development tool maintains its own configuration file.

Advantages

- Matches each tool's historical defaults.
- Familiar to many developers.

Disadvantages

- Configuration becomes fragmented.
- Increased maintenance effort.
- Greater risk of inconsistent settings.
- Project metadata duplicated across files.

---

### Option 2 — Use `setup.py`

Maintain project metadata using the traditional `setup.py` mechanism.

Advantages

- Long-established approach.
- Supported by older tooling.

Disadvantages

- Superseded by modern Python packaging standards.
- Requires executable Python code for configuration.
- Less declarative.

---

### Option 3 — Use `pyproject.toml`

Maintain project metadata and tool configuration in
`pyproject.toml` whenever supported.

Advantages

- Single configuration file.
- Modern Python standard.
- Declarative format.
- Easier maintenance.
- Widely supported by current development tools.

Disadvantages

- Some tools still require separate configuration files.
- Contributors must be familiar with TOML syntax.

---

## Decision

`pyproject.toml` shall be the authoritative source for

- project metadata,
- package information,
- Python dependencies,
- optional development dependencies,
- Ruff configuration,
- mypy configuration,
- additional supported tool configuration.

Configuration shall not be duplicated across multiple files unless
required by a tool that does not support `pyproject.toml`.

CMake shall read project information from `pyproject.toml` where
practical rather than maintaining duplicate metadata.

---

## Rationale

Maintaining project configuration in a single location reduces
duplication and simplifies maintenance.

Modern Python tooling increasingly adopts `pyproject.toml` as the
standard configuration mechanism.

Using this file as the canonical source ensures that project metadata,
dependencies, and development tool configuration remain synchronized.

This decision also aligns with the project's broader design philosophy
of maintaining a single source of truth for shared information.

---

## Consequences

### Positive

- Single authoritative configuration file.
- Reduced duplication.
- Easier maintenance.
- Modern Python packaging.
- Consistent project metadata.

### Negative

- Some tools may still require separate configuration files.
- Contributors should understand TOML syntax.

---

## References

- SRDS Chapter 7 — Build System
- REQ-BUILD-704
- REQ-BUILD-705
