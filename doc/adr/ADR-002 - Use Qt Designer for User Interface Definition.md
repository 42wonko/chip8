# ADR-002 — Use Qt Designer for User Interface Definition

**Author:** Michael Dlubatz

**Date:** 2026-07-01

**Status:** Accepted

---

## Title

Use Qt Designer `.ui` files to define the graphical user interface.

---

## Context

The emulator provides a graphical user interface based on PyQt6.

The application contains multiple windows and a large number of widgets,
including menus, toolbars, dialogs, debugger views, and the emulator
display.

Two fundamentally different approaches were considered.

The first constructs the entire interface programmatically using Python.

The second defines the visual layout using Qt Designer and loads the
generated `.ui` files dynamically at runtime.

---

## Alternatives Considered

### Option 1 — Construct the Interface in Python

Every widget is created, configured, and positioned using Python code.

Advantages

- No additional UI files.
- Complete control from Python.

Disadvantages

- Large amounts of repetitive code.
- Difficult visual editing.
- Layout changes require source code modifications.
- Poor separation of presentation and application logic.

---

### Option 2 — Use Qt Designer

Window layouts are created visually using Qt Designer.

The resulting `.ui` files are loaded dynamically during application
startup.

Advantages

- Visual interface design.
- Cleaner Python implementation.
- Better separation of presentation and logic.
- Easier maintenance.
- Supports rapid GUI iteration.

Disadvantages

- Requires Qt Designer.
- `.ui` files become part of the project source.

---

## Decision

All major application windows shall be designed using Qt Designer.

The graphical layout shall be stored in `.ui` files.

The `.ui` files shall be loaded dynamically at runtime using PyQt6.

Python source code shall contain only

- application logic,
- widget initialization,
- signal connections,
- runtime configuration.

Widget layout shall not be hard-coded.

---

## Rationale

Qt Designer provides a clear separation between presentation and
application logic.

It allows the graphical interface to be modified without changing the
Python implementation.

An additional benefit is the ability to reuse the existing interface
developed for the original C++ implementation.

Only minor adjustments are required to adapt the existing `.ui` files
for the Python version, significantly reducing development effort while
preserving a proven user interface design.

---

## Consequences

### Positive

- Cleaner Python code.
- Easier GUI maintenance.
- Visual interface editing.
- Reduced development effort.
- Reuse of existing UI resources.
- Better separation of concerns.

### Negative

- Qt Designer becomes part of the development workflow.
- Developers should understand the `.ui` file format.
- Runtime loading introduces a small startup overhead.

---

## References

- SRDS Chapter 5 — Graphical User Interface
- REQ-GUI-502
- REQ-GUI-503
- REQ-GUI-504
- REQ-GUI-520
- REQ-GUI-521

