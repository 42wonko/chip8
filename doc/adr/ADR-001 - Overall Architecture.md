# ADR-001 — Overall Architecture

**Author:** Michael Dlubatz

**Date:** 2026-07-01

**Status:** Accepted

---

## Title

Use a three-layer architecture consisting of a Graphical User Interface,
Controller, and Emulator Core.

---

## Context

The CHIP-8 Emulator is intended to serve both as a functional emulator
and as a learning project emphasizing clean software architecture and
maintainability.

Several architectural approaches were considered.

The project requires

- a graphical user interface,
- an emulator core,
- debugging facilities,
- future extensibility,
- separation of responsibilities.

A clear separation between presentation and emulation logic is
considered essential.

---

## Alternatives Considered

### Option 1 — Monolithic Design

The graphical user interface directly manipulates the emulator state.

Advantages

- Simple to implement.
- Minimal number of classes.

Disadvantages

- Tight coupling.
- Difficult testing.
- Poor maintainability.
- Difficult future extensions.

---

### Option 2 — GUI owns the Emulator

The GUI creates and directly controls the emulator.

Advantages

- Slightly cleaner than a monolithic design.

Disadvantages

- GUI becomes responsible for application logic.
- Difficult to replace the user interface.
- Emulator cannot easily operate independently.

---

### Option 3 — Layered Architecture

```
GUI
 │
 ▼
Controller
 │
 ▼
Emulator
```

Advantages

- Clear separation of responsibilities.
- Loose coupling.
- Easier testing.
- Easier maintenance.
- Supports multiple user interfaces.

Disadvantages

- Additional abstraction layer.
- Slightly more implementation effort.

---

## Decision

The project shall use a three-layer architecture.

The layers are

- Graphical User Interface
- Controller
- Emulator Core

Communication shall occur only between adjacent layers.

The GUI shall never directly access emulator objects.

The emulator shall remain completely independent of the GUI.

---

## Rationale

The layered architecture provides the best balance between simplicity,
maintainability, and extensibility.

The Controller acts as the single coordination point for application
logic while allowing the emulator to remain independent of the graphical
presentation.

This separation makes future extensions significantly easier.

Examples include

- a command-line interface,
- automated testing,
- alternative graphical front ends,
- future virtual machine implementations.

---

## Consequences

### Positive

- Clear separation of responsibilities.
- Improved maintainability.
- Easier unit testing.
- GUI and emulator evolve independently.
- Simplified debugging.

### Negative

- Additional classes.
- More indirection.
- Slightly higher initial implementation effort.

---

## References

- SRDS Chapter 2 — Overall Architecture
- REQ-ARCH-100 through REQ-ARCH-110
