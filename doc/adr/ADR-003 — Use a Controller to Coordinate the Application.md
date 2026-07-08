# ADR-003 — Use a Controller to Coordinate the Application

**Author:** Michael Dlubatz

**Date:** 2026-07-01

**Status:** Accepted

---

## Title

Use a dedicated Controller as the sole communication layer between the
graphical user interface and the emulator core.

---

## Context

The emulator consists of two fundamentally different subsystems.

The graphical user interface is responsible for user interaction and
visualization.

The emulator core is responsible for maintaining and executing the
virtual machine.

Without a dedicated coordination layer, both subsystems would require
knowledge of each other's internal implementation.

Such coupling would make future changes more difficult and reduce the
modularity of the application.

---

## Alternatives Considered

### Option 1 — GUI Directly Controls the Emulator

The GUI creates the emulator and invokes its methods directly.

Advantages

- Simple implementation.
- Fewer classes.

Disadvantages

- Tight coupling between GUI and emulator.
- Difficult unit testing.
- GUI contains application logic.
- Poor scalability.

---

### Option 2 — Emulator Controls the GUI

The emulator updates GUI widgets directly.

Advantages

- Simple data flow.

Disadvantages

- Emulator depends on GUI classes.
- Violates separation of concerns.
- Prevents headless execution.
- Difficult to maintain.

---

### Option 3 — Dedicated Controller

A Controller owns both the GUI and the emulator.

All communication passes through the Controller.

Advantages

- Loose coupling.
- Clear separation of responsibilities.
- Simplified testing.
- Easier maintenance.
- Supports future user interfaces.

Disadvantages

- Additional abstraction layer.
- Slight increase in implementation complexity.

---

## Decision

A dedicated `Chip8Controller` shall coordinate the entire application.

The Controller shall

- create the emulator,
- create the main window,
- receive user commands,
- invoke emulator operations,
- update the GUI,
- coordinate application startup and shutdown.

The Controller shall be the only component permitted to communicate
with both the GUI and the emulator.

The GUI shall not directly access emulator objects.

The emulator shall not directly access GUI objects.

---

## Rationale

The Controller centralizes application logic while allowing the GUI and
the emulator to evolve independently.

This architecture minimizes coupling and clearly separates user
interface concerns from emulation logic.

It also enables the emulator to operate without a graphical interface,
which simplifies automated testing and allows future interfaces, such as
a command-line front end, to be implemented without modifying the
emulator core.

---

## Consequences

### Positive

- Clear separation of responsibilities.
- Loose coupling between subsystems.
- Improved maintainability.
- Easier automated testing.
- GUI and emulator remain independently replaceable.
- Simplified event handling.

### Negative

- Additional class.
- Slightly more indirect control flow.
- Minor increase in implementation effort.

---

## References

- SRDS Chapter 2 — Overall Architecture
- SRDS Chapter 5 — Graphical User Interface
- REQ-ARCH-103
- REQ-ARCH-104
- REQ-ARCH-105
- REQ-GUI-500
- REQ-GUI-501
