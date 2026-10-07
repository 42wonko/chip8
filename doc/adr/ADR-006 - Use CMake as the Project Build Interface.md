# ADR-006 — Use CMake as the Project Build Interface

**Author:** Michael Dlubatz

**Date:** 2026-07-01

**Status:** Accepted

---

## Title

Use CMake as the unified interface for building, running, documenting,
and maintaining the project.

---

## Context

The CHIP-8 Emulator is implemented entirely in Python.

Unlike compiled languages, Python projects do not require a traditional
build system.

However, the project makes use of several development tools, including

- Ruff,
- mypy,
- Doxygen,
- Graphviz,
- PyQt6,
- CMake.

Developers typically invoke these tools individually from the command
line.

This results in numerous tool-specific commands that must be remembered
and documented.

The project therefore requires a single, consistent entry point for all
development activities.

---

## Alternatives Considered

### Option 1 — Invoke Tools Individually

Developers execute each tool directly.

Examples include

```
python -m chip8
ruff check
ruff format
mypy
doxygen
```

Advantages

- No additional infrastructure.
- Common approach for Python projects.

Disadvantages

- Multiple unrelated commands.
- Difficult to remember.
- Tool-specific knowledge required.
- Inconsistent workflow.

---

### Option 2 — Shell Scripts

Provide shell scripts for common development tasks.

Advantages

- Easy to implement.
- Familiar on Unix-like systems.

Disadvantages

- Platform dependent.
- Difficult to extend cleanly.
- Logic becomes distributed across multiple scripts.

---

### Option 3 — CMake

Use CMake to orchestrate all development tasks.

Examples include

```
cmake --build . --target run
cmake --build . --target format
cmake --build . --target lint
cmake --build . --target typecheck
cmake --build . --target all_checks
cmake --build . --target docs
```

Advantages

- Single, consistent interface.
- Platform independent.
- Easily extensible.
- Self-documenting through the `info` target.
- Integrates naturally with IDEs.

Disadvantages

- Additional CMake configuration.
- Less common for Python projects.

---

## Decision

CMake shall serve as the primary development interface.

Common development tasks shall be implemented as CMake targets.

Individual development tools shall remain responsible for their
specialized functionality.

CMake shall coordinate their execution.

---

## Rationale

Although the project is written in Python, development involves much
more than executing the application.

Formatting, static analysis, documentation generation, cleanup, and
execution are recurring development tasks.

Providing a single interface improves consistency and reduces the amount
of tool-specific knowledge required from contributors.

The chosen approach also mirrors workflows commonly found in larger C++
projects, making the development process predictable and easy to
document.

---

## Consequences

### Positive

- Single entry point for development.
- Consistent workflow.
- Platform-independent task execution.
- Easy integration with IDEs.
- Straightforward addition of future development tasks.

### Negative

- Requires familiarity with CMake.
- Additional maintenance of the CMake configuration.

---

## References

- SRDS Chapter 7 — Build System
- REQ-BUILD-702
- REQ-BUILD-703
- REQ-BUILD-711
