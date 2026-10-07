# ADR-008 — Prefix Implementation Classes with `Chip8`

**Author:** Michael Dlubatz

**Date:** 2026-07-01

**Status:** Accepted

---

## Title

Prefix implementation classes with `Chip8` to identify the virtual
machine they implement.

---

## Context

Version 1.x of the project implements only the original CHIP-8 virtual
machine.

Future versions may support additional systems, including

- Super-CHIP (SCHIP),
- XO-CHIP,
- other CHIP-8 variants.

Several core classes represent virtual machine components.

Examples include

- Machine
- Memory
- Display
- Keyboard
- Instruction Decoder

Using generic class names would make future implementations ambiguous
and increase the likelihood of naming conflicts.

The project therefore requires a naming convention that clearly
identifies the virtual machine implemented by a class while allowing
future extensions without disruptive refactoring.

---

## Alternatives Considered

### Option 1 — Generic Class Names

Examples

```
Machine
Memory
Keyboard
Display
InstructionDecoder
```

Advantages

- Short class names.
- Less typing.

Disadvantages

- Ambiguous in multi-system projects.
- Future implementations require renaming.
- Increased risk of naming conflicts.

---

### Option 2 — Namespace Separation Only

Examples

```
chip8.machine.Machine
superchip.machine.Machine
```

Advantages

- Short class names.
- Separation by package.

Disadvantages

- Class names remain ambiguous when imported.
- Requires aliases in many source files.
- Reduced readability outside the package context.

---

### Option 3 — Prefix Implementation Classes

Examples

```
Chip8Machine
Chip8Memory
Chip8Display
Chip8Keyboard
Chip8InstructionDecoder
```

Advantages

- Immediately identifies the implemented system.
- Supports additional virtual machines naturally.
- Avoids future renaming.
- Improves readability.

Disadvantages

- Slightly longer class names.

---

## Decision

Implementation classes representing components of the original CHIP-8
virtual machine shall be prefixed with `Chip8`.

Examples include

```
Chip8Machine
Chip8Memory
Chip8Cpu
Chip8Display
Chip8Keyboard
Chip8Stack
Chip8InstructionDecoder
```

Classes that are independent of any specific virtual machine shall not
use the prefix.

Examples include

```
MainWindow
DisplayWidget
Chip8Controller
RomLoader
SettingsDialog
```

---

## Rationale

The naming convention clearly distinguishes implementation classes from
application infrastructure.

It also provides a straightforward migration path for future support of
additional virtual machines.

For example, a future implementation could introduce

```
SuperChipMachine
SuperChipDisplay
SuperChipInstructionDecoder
```

without modifying or renaming the existing CHIP-8 implementation.

This approach preserves backward compatibility while keeping the code
base easy to navigate.

The additional verbosity is considered a reasonable trade-off for the
improved clarity and extensibility.

---

## Consequences

### Positive

- Clear identification of implementation classes.
- Straightforward support for additional virtual machines.
- Improved readability.
- Avoids disruptive future renaming.
- Consistent naming throughout the emulator core.

### Negative

- Longer class names.
- Slightly more verbose source code.

---

## References

- SRDS Chapter 3 — Coding Standards
- SRDS Chapter 4 — Emulator Core
- REQ-CODE-303
- REQ-ARCH-109
