# ADR-009 — Integrate the Assembler into the Emulator Architecture

**Author:** Michael Dlubatz

**Date:** 2026-08-04

**Status:** Proposed

---

# Context

The CHIP-8 project currently consists of an emulator, debugger and graphical user interface.

The project is being extended with an integrated assembler that allows users to develop, assemble, debug and execute CHIP-8 assembly language programs within a single application.

The assembler is intended to become a permanent subsystem of the project rather than an external utility.

Although integrated into the application, the assembler shall remain reusable as an independent software component. It shall therefore not depend on any graphical user interface components.

---

# Decision

The assembler shall be integrated into the existing application architecture as a peer subsystem of the emulator.

The application Controller shall coordinate both the emulator and the assembler.

The emulator and assembler shall remain completely independent of each other.

The GUI shall communicate with both subsystems exclusively through the Controller.

The assembler shall expose a well-defined public API suitable for

- graphical user interfaces,
- automated unit tests,
- integration tests,
- future command-line tools,
- future scripting interfaces.

The overall application architecture therefore becomes:

```text
                           User
                             │
                             ▼
                      +--------------+
                      |     GUI      |
                      +------+-------+
                             │
                             ▼
                     +----------------+
                     |   Controller   |
                     +---+--------+---+
                         │        │
                         │        │
                         ▼        ▼
                 +------------+  +------------+
                 |  Emulator  |  | Assembler  |
                 +------------+  +------------+
```

The Controller remains the single coordination point of the application.

Neither subsystem shall call into the other directly.

---

# Rationale

The emulator and assembler solve fundamentally different problems.

The emulator executes machine code.

The assembler translates source code into machine code.

Keeping both subsystems independent

- improves modularity,
- simplifies testing,
- allows independent evolution,
- enables reuse of the assembler outside the GUI,
- preserves the existing controller-based architecture.

---

# Consequences

## Positive

- Clear separation of responsibilities.
- Existing emulator architecture remains largely unchanged.
- Controller continues to coordinate all application workflows.
- Assembler is reusable outside the graphical user interface.
- Unit testing of emulator and assembler remains independent.
- Future source-level debugging can be implemented without coupling assembler internals to emulator internals.

## Negative

- The Controller coordinates one additional subsystem.
- New interfaces between Controller and Assembler are required.

---

# Alternatives Considered

## External assembler executable

Implement the assembler as a separate application.

Rejected because it complicates source-level debugging, increases deployment complexity and requires inter-process communication.

---

## Integrate assembler into the emulator

Embed the assembler directly inside the emulator subsystem.

Rejected because assembling source code and executing machine code are separate responsibilities with different lifecycles.

Such coupling would unnecessarily increase complexity.

---

# Related ADRs

- ADR-001 — Overall Architecture
- ADR-003 — Use a Controller to Coordinate the Application

The following ADRs describe the internal architecture of the assembler subsystem.

- ADR-010 — Parser Framework Driven by Architecture Definitions
- ADR-011 — Use a Two-Pass Assembly Process
- ADR-012 — Represent Source Code as an Abstract Syntax Tree
- ADR-013 — Use Architecture Plug-ins for CHIP-8 Variants
