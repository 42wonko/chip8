# CHIP-8 Emulator

# Software Requirements and Design Specification (SRDS)

---

**Document ID:** SRDS-CHIP8

**Version:** 1.0 (Draft)

**Status:** Draft

**Date:** 2026-07-01

**Author:** Michael Dlubatz

**Implementation Language:** Python 3.12+

**Reference Development Platform:** Python 3.13.5 on Linux

**GUI Framework:** PyQt6

**License:** MIT License

---

## Abstract

This document specifies the software requirements, architectural design,
coding standards, development process, and implementation constraints
for the CHIP-8 Emulator project.

The SRDS is the authoritative engineering specification for the project.
All implementation shall conform to the requirements and design rules
defined herein.

<div style="page-break-after: always;"></div>

# Revision History

| Version | Date | Author | Description |
|----------|------------|--------|-------------|
| 0.1 | 2026-07-01 | Michael Dlubatz | Initial document structure |
| 1.0 | TBD | Michael Dlubatz | Initial approved specification |

<div style="page-break-after: always;"></div>


# Document Status

Current Status:

> Draft

This document is under active development.

Requirements marked with the keyword **shall** are normative.

Informative notes, rationale and examples are non-normative.

---

# Distribution

This document is maintained together with the project source code.

The canonical copy resides in

```

doc/sdrs/Software_Requirements_and_Design_Specification.md

```

<div style="page-break-after: always;"></div>


# Conventions

The following terminology is used throughout this specification.

| Keyword | Meaning |
|----------|---------|
| **Shall** | Mandatory requirement |
| **Shall not** | Mandatory prohibition |
| **Should** | Strong recommendation |
| **May** | Optional feature |
| **Can** | Statement of capability |

Requirement identifiers are globally unique.

Examples:

```

REQ-ARCH-001
REQ-GUI-012
REQ-EMU-024
RULE-CODE-011

```

Requirement identifiers shall never be reused.

If a requirement is removed, its identifier shall be retired permanently.



# Abbreviations

| Abbreviation | Meaning |
|--------------|---------|
| API | Application Programming Interface |
| CPU | Central Processing Unit |
| GUI | Graphical User Interface |
| PC | Program Counter |
| SP | Stack Pointer |
| ROM | Read Only Memory |
| RAM | Random Access Memory |
| SRDS | Software Requirements and Design Specification |
| UI | User Interface |
| UML | Unified Modeling Language |

<div style="page-break-after: always;"></div>


# Referenced Documents

The following references are informative.

| Reference | Description |
|-----------|-------------|
| CHIP-8 Technical Reference | Cowgod's CHIP-8 Reference |
| Octo Documentation | Octo CHIP-8 Documentation |
| Python Documentation | Python Language Reference |
| PyQt6 Documentation | Qt for Python Documentation |
| NumPy Documentation | NumPy Reference Manual |

Where multiple references disagree, this SRDS shall take precedence.

---

# Table of Contents

<!--
This table of contents is maintained manually.
-->

1. Introduction
2. Overall Architecture
3. Coding Standards
4. Emulator Core
5. Graphical User Interface
6. Debugger and Disassembler
7. Build System
8. Development Process
9. Appendices

---

# List of Figures

*Reserved.*

---

# List of Tables

*Reserved.*

---

# Requirements Traceability Matrix

*Reserved.*

The completed matrix will map every requirement identifier to the
implementation that satisfies it.

Example:

| Requirement | Implementation |
|-------------|----------------|
| REQ-ARCH-001 | Chip8Controller |
| REQ-GUI-007 | MainWindow |
| REQ-EMU-014 | Chip8Machine |

---

# Glossary

A glossary containing all project terminology is maintained in
Appendix A.

---

<div style="page-break-after: always;"></div>

# Chapter 1 — Introduction

---

## 1.1 Purpose

### 1.1.1 Objective

This Software Requirements and Design Specification (SRDS) defines the
functional requirements, non-functional requirements, architectural
constraints, and development rules for the CHIP-8 Emulator project.

The SRDS is the authoritative technical specification for the project.
Its purpose is to ensure that implementation decisions remain
consistent throughout the lifetime of the project and that all
contributors share a common understanding of the system architecture.

### Requirements

**REQ-INTRO-001**

The SRDS shall constitute the normative specification of the project.

**REQ-INTRO-002**

If the implementation and the SRDS disagree, the SRDS shall be
considered authoritative until the discrepancy has been resolved
through a documented design revision.

**REQ-INTRO-003**

Architectural modifications shall be documented in the SRDS before
implementation begins.

### Rationale

Maintaining a normative design specification prevents architectural
drift and preserves the reasoning behind important engineering
decisions.

---

## 1.2 Project Objectives

The project has two primary objectives.

The first objective is the development of a correct implementation of
the original CHIP-8 virtual machine.

The second objective is the demonstration of sound software engineering
practices, including modular architecture, comprehensive documentation,
strong typing, and incremental development.

Both objectives are considered equally important.

### Requirements

**REQ-INTRO-004**

The project shall faithfully emulate the original CHIP-8 virtual
machine.

**REQ-INTRO-005**

Maintainability shall take precedence over implementation speed.

**REQ-INTRO-006**

The architecture shall permit future extensions without requiring
fundamental redesign.

---

## 1.3 Project Scope

Version 1.x includes the following major subsystems.

- Emulator core
- Graphical user interface
- Interactive debugger
- Disassembler
- Memory viewer
- Register viewer
- Stack viewer
- Keyboard visualization
- Execution tracing
- Instruction logging
- Build system
- API documentation

### Requirements

**REQ-SCOPE-001**

Version 1.x shall implement the complete original CHIP-8 instruction
set.

**REQ-SCOPE-002**

Version 1.x shall include an integrated debugger.

**REQ-SCOPE-003**

Version 1.x shall include an integrated disassembler.

**REQ-SCOPE-004**

Version 1.x shall execute on Linux.

---

## 1.4 Out of Scope

The following features are intentionally excluded from Version 1.x.

- Super-CHIP support
- XO-CHIP support
- Save-state functionality
- Snapshot functionality
- Alternative rendering themes
- Advanced audio synthesis
- Network functionality
- Performance optimizations that reduce code readability

The software architecture shall nevertheless permit these features to
be added in future releases.

### Requirements

**REQ-SCOPE-005**

Deferred features shall not influence the implementation of Version
1.x unless required for architectural extensibility.

### Design Rules

**RULE-DESIGN-001**

Feature creep shall be actively avoided throughout the project.

---

## 1.5 Engineering Principles

The following principles govern all design decisions.

### Correctness

Correct emulation has priority over execution speed.

### Simplicity

Simple solutions shall be preferred over unnecessarily complex
alternatives.

Premature optimization shall be avoided.

### Maintainability

The software shall remain understandable, modular, and maintainable
throughout its lifetime.

### Incremental Development

The application shall remain executable after every completed
development milestone.

### Documentation

Documentation is considered an integral part of the implementation.

### Requirements

**REQ-GOAL-001**

The project shall remain runnable after every completed development
milestone.

**REQ-GOAL-002**

All public interfaces shall be documented.

**REQ-GOAL-003**

Every significant implementation decision shall be traceable to a
documented requirement or design rule.

---

## 1.6 Intended Audience

This document is intended for

- developers,
- maintainers,
- reviewers,
- contributors, and
- readers interested in the software architecture.

The SRDS is not intended to serve as a user manual.

---

## 1.7 Terminology

The following terminology is normative.

| Term | Definition |
|------|------------|
| Emulator | The complete software system. |
| Virtual Machine | The emulated CHIP-8 hardware. |
| Instruction | One complete CHIP-8 operation. |
| Opcode | The binary encoding of one instruction. |
| Cycle | Execution of exactly one instruction. |
| Framebuffer | The logical display memory. |
| Debugger | The subsystem used to inspect and control execution. |
| Disassembler | The subsystem that converts opcodes into assembly language. |
| ROM | A program loaded into emulator memory. |

### Requirements

**REQ-TERM-001**

The term *cycle* shall always denote the execution of exactly one
CHIP-8 instruction.

**REQ-TERM-002**

Internal helper operations shall not constitute additional execution
cycles.

**REQ-TERM-003**

Micro-operations performed during instruction execution shall not be
visible to the user.

---

## 1.8 Document Organization

This specification is organized as follows.

- Chapter 1 introduces the project.
- Chapter 2 specifies the software architecture.
- Chapter 3 defines the coding standards.
- Chapter 4 specifies the emulator core.
- Chapter 5 specifies the graphical user interface.
- Chapter 6 specifies the debugger and disassembler.
- Chapter 7 specifies the build system.
- Chapter 8 defines the development process.
- The appendices provide supporting reference material.

---

## Requirements Summary

| ID | Description |
|----|-------------|
| REQ-INTRO-001 | The SRDS is the normative specification. |
| REQ-INTRO-002 | The SRDS takes precedence over the implementation. |
| REQ-INTRO-003 | Architectural changes require prior SRDS updates. |
| REQ-INTRO-004 | Implement the original CHIP-8 virtual machine. |
| REQ-INTRO-005 | Prioritize maintainability. |
| REQ-INTRO-006 | Permit future architectural extensions. |
| REQ-SCOPE-001 | Implement the complete original instruction set. |
| REQ-SCOPE-002 | Provide an integrated debugger. |
| REQ-SCOPE-003 | Provide an integrated disassembler. |
| REQ-SCOPE-004 | Support Linux. |
| REQ-SCOPE-005 | Deferred features shall remain out of scope. |
| RULE-DESIGN-001 | Avoid feature creep. |
| REQ-GOAL-001 | The application shall remain runnable after every milestone. |
| REQ-GOAL-002 | Public interfaces shall be documented. |
| REQ-GOAL-003 | Requirements shall be traceable to the implementation. |
| REQ-TERM-001 | One cycle equals one executed instruction. |
| REQ-TERM-002 | Helper operations are not execution cycles. |
| REQ-TERM-003 | Internal micro-operations shall not be visualized. |


<div style="page-break-after: always;"></div>

# Chapter 2 — Overall Architecture

---

## 2.1 Purpose

This chapter defines the high-level architecture of the CHIP-8 Emulator.

The objective of the architecture is to separate the graphical user
interface from the emulator core while maintaining a clear and
maintainable flow of information throughout the application.

The architecture defined in this chapter is normative.

No implementation shall violate the architectural rules specified herein.

---

## 2.2 Architectural Overview

The application consists of three logical layers.

```
+------------------------------------------------------------+
|                          GUI                               |
|------------------------------------------------------------|
| MainWindow                                                 |
| DisplayWidget                                              |
| RegisterWidget                                             |
| MemoryWidget                                               |
| StackWidget                                                |
| DisassemblyWidget                                          |
+---------------------------▲--------------------------------+
                            │
                            │
+---------------------------┼--------------------------------+
|                     Controller                             |
|------------------------------------------------------------|
| Chip8Controller                                            |
+---------------------------▲--------------------------------+
                            │
                            │
+---------------------------┼--------------------------------+
|                      Emulator                              |
|------------------------------------------------------------|
| Chip8Machine                                                |
| Instruction Decoder                                         |
| Instructions                                                |
| Memory                                                      |
| Timers                                                      |
| Keyboard                                                    |
| Disassembler                                                |
+------------------------------------------------------------+
```

The GUI presents information to the user.

The Controller coordinates communication.

The Emulator contains all virtual hardware and execution logic.

---

### Requirements

**REQ-ARCH-100**

The application shall consist of exactly three architectural layers.

**REQ-ARCH-101**

The three layers shall be

- GUI
- Controller
- Emulator

**REQ-ARCH-102**

Every software component shall belong to exactly one architectural
layer.

---

## 2.3 Layer Responsibilities

### 2.3.1 GUI Layer

The GUI layer is responsible solely for presenting information and
forwarding user input to the Controller.

The GUI shall never modify emulator state directly.

The GUI shall never execute CHIP-8 instructions.

---

### Requirements

**REQ-ARCH-103**

GUI components shall not access emulator objects directly.

**REQ-ARCH-104**

GUI components shall communicate exclusively with the Controller.

---

### 2.3.2 Controller Layer

The Controller coordinates all communication between the GUI and the
Emulator.

It is responsible for

- application startup,
- command dispatch,
- synchronization,
- user interaction,
- GUI updates.

The Controller owns both the GUI and the Emulator.

---

### Requirements

**REQ-ARCH-105**

Exactly one Controller instance shall exist.

**REQ-ARCH-106**

The Controller shall be the only component permitted to communicate
with both the GUI and the Emulator.

---

### 2.3.3 Emulator Layer

The Emulator contains the complete virtual machine.

The Emulator shall have no knowledge of graphical user interface
components.

The Emulator shall be executable independently of the GUI.

---

### Requirements

**REQ-ARCH-107**

The Emulator shall not depend upon GUI components.

**REQ-ARCH-108**

The Emulator shall not import GUI modules.

---

## 2.4 Dependency Rules

Dependencies shall always point downward.

```
GUI
 │
 ▼
Controller
 │
 ▼
Emulator
```

Reverse dependencies are prohibited.

---

### Requirements

**REQ-ARCH-109**

The GUI may depend on the Controller.

**REQ-ARCH-110**

The Controller may depend on the Emulator.

**REQ-ARCH-111**

The Emulator shall not depend upon either the Controller or the GUI.

---

### Design Rules

**RULE-ARCH-100**

Circular dependencies shall not exist.

---

## 2.5 Information Flow

During execution, information flows through the application as follows.

```
User
 │
 ▼
GUI
 │
 ▼
Controller
 │
 ▼
Chip8Machine
 │
 ▼
Machine State Updated
 │
 ▼
Controller
 │
 ▼
GUI Refresh
```

The GUI never observes partially executed instructions.

---

### Requirements

**REQ-ARCH-112**

GUI updates shall occur only after successful completion of an
instruction.

**REQ-ARCH-113**

Intermediate execution states shall not be visible.

---

## 2.6 Object Ownership

Ownership defines lifetime.

```
Chip8Controller
    │
    ├── MainWindow
    │
    └── Chip8Machine
            │
            ├── Memory
            ├── Registers
            ├── Timers
            ├── Keyboard
            └── Framebuffer
```

Objects shall have exactly one owner.

Ownership shall not be shared.

---

### Requirements

**REQ-ARCH-114**

Every runtime object shall have exactly one owner.

**REQ-ARCH-115**

The Controller shall own the MainWindow.

**REQ-ARCH-116**

The Controller shall own the Chip8Machine.

---

## 2.7 Package Organization

The project shall use the following package hierarchy.

```
src/

    chip8/
        __main__.py

    controller/

    emulator/

    gui/

    util/
```

Additional packages may be introduced provided they satisfy the
architectural rules defined in this chapter.

---

### Requirements

**REQ-ARCH-117**

The project shall use the `src` layout.

**REQ-ARCH-118**

Each package shall have a clearly defined responsibility.

---

## 2.8 Design Principles

The architecture is based upon the following principles.

- Separation of concerns
- Single responsibility
- Explicit ownership
- Low coupling
- High cohesion
- Incremental development

These principles guide architectural decisions but do not replace
normative requirements.

---

### Design Rules

**RULE-ARCH-101**

Implementation simplicity shall be preferred over unnecessary
abstraction.

**RULE-ARCH-102**

Future extensibility shall not compromise current readability.

---

## 2.9 Rationale

The selected architecture intentionally isolates the emulator core from
all user interface concerns.

This separation permits

- independent testing,
- future GUI replacement,
- easier maintenance,
- future support for additional virtual machines,
- reduced coupling between components.

The Controller centralizes communication and prevents direct
dependencies between the GUI and the Emulator.

---

## Requirements Summary

| ID | Description |
|----|-------------|
| REQ-ARCH-100 | Three-layer architecture |
| REQ-ARCH-101 | GUI, Controller, Emulator |
| REQ-ARCH-102 | One architectural layer per component |
| REQ-ARCH-103 | GUI shall not access Emulator directly |
| REQ-ARCH-104 | GUI communicates only with Controller |
| REQ-ARCH-105 | Exactly one Controller instance |
| REQ-ARCH-106 | Controller is the communication hub |
| REQ-ARCH-107 | Emulator independent of GUI |
| REQ-ARCH-108 | Emulator shall not import GUI modules |
| REQ-ARCH-109 | GUI may depend on Controller |
| REQ-ARCH-110 | Controller may depend on Emulator |
| REQ-ARCH-111 | Emulator shall not depend on higher layers |
| REQ-ARCH-112 | GUI updates after completed instruction |
| REQ-ARCH-113 | No intermediate machine states |
| REQ-ARCH-114 | Single object ownership |
| REQ-ARCH-115 | Controller owns MainWindow |
| REQ-ARCH-116 | Controller owns Chip8Machine |
| REQ-ARCH-117 | Use the `src` layout |
| REQ-ARCH-118 | One responsibility per package |
| RULE-ARCH-100 | No circular dependencies |
| RULE-ARCH-101 | Prefer simple implementations |
| RULE-ARCH-102 | Preserve readability while remaining extensible |

# Chapter 3 — Coding Standards

---

## 3.1 Purpose

This chapter defines the mandatory coding standards for the CHIP-8
Emulator project.

The purpose of these standards is to ensure that the codebase remains
consistent, readable, maintainable, and suitable for long-term
development.

Unless explicitly stated otherwise, every source file in the project
shall conform to the requirements defined in this chapter.

---

## 3.2 Python Version

The project shall use modern Python language features.

Only language features supported by the minimum required Python version
may be used.

### Requirements

**REQ-CODE-200**

The project shall require Python 3.12 or newer.

**REQ-CODE-201**

The reference development environment shall use Python 3.13.

---

## 3.3 Source File Organization

Each source file shall have a clearly defined purpose.

Large source files should be decomposed into multiple modules whenever
doing so improves readability.

### Requirements

**REQ-CODE-202**

Each source file shall implement one primary responsibility.

**REQ-CODE-203**

Each public class shall reside in its own source file.

**REQ-CODE-204**

Source files shall be organized according to the project package
structure defined in Chapter 2.

---

## 3.4 Documentation

Documentation is considered part of the implementation.

All public interfaces shall be documented using Doxygen-compatible
documentation comments.

Module documentation shall describe the purpose and responsibilities of
the module.

### Requirements

**REQ-CODE-205**

Every source file shall begin with a Doxygen file header.

**REQ-CODE-206**

Every public class shall have a Doxygen class description.

**REQ-CODE-207**

Every public method shall have Doxygen documentation.

**REQ-CODE-208**

Private helper methods should be documented whenever their purpose is
not immediately obvious.

---

## 3.5 Type Hints

Static type annotations shall be used throughout the project.

Type hints improve readability, enable static analysis, and simplify
maintenance.

### Requirements

**REQ-CODE-209**

Every function shall have complete type annotations.

**REQ-CODE-210**

Every method shall have complete type annotations.

**REQ-CODE-211**

Module-level constants shall use explicit type annotations.

**REQ-CODE-212**

Public attributes shall use explicit type annotations.

**REQ-CODE-213**

Local variable annotations should be used whenever they improve
readability.

---

## 3.6 Naming Conventions

Names shall clearly communicate intent.

Abbreviations shall be avoided unless they are universally understood.

### Classes

Class names shall use PascalCase.

Example:

```
Chip8Machine
DisplayWidget
Chip8Controller
```

### Methods and Functions

Method names shall use snake_case.

Example:

```
load_rom()
execute_instruction()
update_display()
```

### Variables

Variables shall use snake_case.

Names shall be descriptive.

Single-letter variable names shall only be used where universally
accepted (e.g. `i`, `x`, `y`).

### Constants

Constants shall use UPPER_CASE.

Example:

```
PROGRAM_START
DISPLAY_WIDTH
MEMORY_SIZE
```

### Private Members

Private members shall begin with a leading underscore.

Example:

```
_machine
_framebuffer
_update_gui()
```

### Requirements

**REQ-CODE-214**

Class names shall use PascalCase.

**REQ-CODE-215**

Functions and methods shall use snake_case.

**REQ-CODE-216**

Constants shall use UPPER_CASE.

**REQ-CODE-217**

Private members shall begin with a leading underscore.

---

## 3.7 Formatting

Source code formatting shall remain consistent throughout the project.

Automatic formatting tools shall be used where practical.

### Requirements

**REQ-CODE-218**

Source files shall be formatted using Ruff.

**REQ-CODE-219**

Static analysis shall be performed using mypy.

**REQ-CODE-220**

Formatting changes shall not alter program behaviour.

### Design Rules

**RULE-CODE-200**

Trailing commas in function parameter lists and function calls shall not
be used unless syntactically required.

**RULE-CODE-201**

Readability shall take precedence over minimizing line count.

---

## 3.8 Imports

Imports shall be grouped in the following order.

1. Standard library
2. Third-party packages
3. Project packages

Each group shall be separated by one blank line.

Wildcard imports are prohibited.

### Requirements

**REQ-CODE-221**

Wildcard imports shall not be used.

**REQ-CODE-222**

Unused imports shall be removed.

---

## 3.9 Error Handling

Errors shall be handled explicitly.

Exceptions shall not be silently ignored.

### Requirements

**REQ-CODE-223**

Exceptions shall either be handled or propagated.

**REQ-CODE-224**

Empty exception handlers are prohibited.

---

## 3.10 Testing

Development shall proceed incrementally.

The project shall remain executable after every completed milestone.

### Requirements

**REQ-CODE-225**

The application shall build successfully after every milestone.

**REQ-CODE-226**

New functionality shall not break existing functionality.

---

## 3.11 Deferred Optimization

Performance optimization is not a goal of Version 1.x.

Optimization shall only be introduced after correctness has been
verified.

### Requirements

**REQ-CODE-227**

Correctness shall take precedence over performance optimization.

### Design Rules

**RULE-CODE-202**

Premature optimization shall be avoided.

---

## 3.12 Future Compatibility

The codebase shall remain extensible.

Architectural flexibility shall be achieved through clear interfaces
rather than unnecessary abstraction.

### Requirements

**REQ-CODE-228**

Future extensions shall not require redesign of the existing
architecture.

---

## Requirements Summary

| ID | Description |
|----|-------------|
| REQ-CODE-200 | Python 3.12 or newer |
| REQ-CODE-201 | Reference environment uses Python 3.13 |
| REQ-CODE-202 | One primary responsibility per source file |
| REQ-CODE-203 | One public class per source file |
| REQ-CODE-204 | Follow project package structure |
| REQ-CODE-205 | Doxygen file header required |
| REQ-CODE-206 | Public classes documented |
| REQ-CODE-207 | Public methods documented |
| REQ-CODE-208 | Document non-obvious private helpers |
| REQ-CODE-209 | Functions require type hints |
| REQ-CODE-210 | Methods require type hints |
| REQ-CODE-211 | Constants require explicit type hints |
| REQ-CODE-212 | Public attributes require explicit type hints |
| REQ-CODE-213 | Local type hints recommended where helpful |
| REQ-CODE-214 | PascalCase class names |
| REQ-CODE-215 | snake_case functions and methods |
| REQ-CODE-216 | UPPER_CASE constants |
| REQ-CODE-217 | Leading underscore for private members |
| REQ-CODE-218 | Ruff formatting |
| REQ-CODE-219 | mypy static analysis |
| REQ-CODE-220 | Formatting shall not change behaviour |
| REQ-CODE-221 | No wildcard imports |
| REQ-CODE-222 | No unused imports |
| REQ-CODE-223 | Exceptions handled or propagated |
| REQ-CODE-224 | No empty exception handlers |
| REQ-CODE-225 | Project builds after every milestone |
| REQ-CODE-226 | New functionality shall not break existing functionality |
| REQ-CODE-227 | Correctness before optimization |
| REQ-CODE-228 | Preserve architectural extensibility |
| RULE-CODE-200 | No trailing commas in parameter or argument lists |
| RULE-CODE-201 | Readability before brevity |
| RULE-CODE-202 | Avoid premature optimization |


# Chapter 4 — Emulator Core

---

## 4.1 Purpose

This chapter specifies the behaviour and architecture of the virtual
CHIP-8 machine.

The emulator core is responsible for representing the complete state of
the virtual machine and executing CHIP-8 instructions according to the
original specification.

The emulator core shall be independent of the graphical user interface
and shall be executable without user interaction.

---

## 4.2 Responsibilities

The emulator core is responsible for

- maintaining the complete virtual machine state,
- executing CHIP-8 instructions,
- loading ROM images,
- managing timers,
- maintaining the framebuffer,
- processing keyboard input,
- providing the current machine state for inspection.

The emulator core is not responsible for

- displaying graphical output,
- processing user interface events,
- rendering widgets,
- loading graphical resources.

---

### Requirements

**REQ-EMU-300**

The emulator core shall maintain the complete state of the virtual
machine.

**REQ-EMU-301**

The emulator core shall not depend upon GUI components.

---

## 4.3 Virtual Machine State

The virtual machine consists of the following logical components.

- Memory
- General-purpose registers
- Index register
- Program counter
- Stack pointer
- Stack
- Delay timer
- Sound timer
- Framebuffer
- Keyboard state

Collectively these components define the complete execution state of
the virtual machine.

---

### Requirements

**REQ-EMU-302**

The virtual machine state shall be completely represented by the
components listed above.

---

## 4.4 Memory

The virtual machine shall provide 4096 bytes of addressable memory.

Program execution begins at address 0x200.

The lower memory region is reserved for interpreter resources.

---

### Requirements

**REQ-EMU-303**

The virtual machine shall provide exactly 4096 bytes of memory.

**REQ-EMU-304**

Program execution shall begin at address 0x0200.

---

## 4.5 Registers

The virtual machine shall contain

- sixteen general-purpose registers,
- one index register,
- one program counter,
- one stack pointer.

---

### Requirements

**REQ-EMU-305**

Sixteen 8-bit general-purpose registers shall be provided.

**REQ-EMU-306**

The index register shall be 16 bits wide.

**REQ-EMU-307**

The program counter shall be 16 bits wide.

**REQ-EMU-308**

The stack pointer shall identify the current stack position.

---

## 4.6 Stack

The virtual machine shall provide a stack capable of storing sixteen
return addresses.

---

### Requirements

**REQ-EMU-309**

The stack shall contain sixteen entries.

---

## 4.7 Timers

The virtual machine shall provide

- one delay timer,
- one sound timer.

Both timers decrement at 60 Hz whenever their value is greater than
zero.

---

### Requirements

**REQ-EMU-310**

The delay timer shall decrement at 60 Hz.

**REQ-EMU-311**

The sound timer shall decrement at 60 Hz.

---

## 4.8 Display

The framebuffer represents the logical display state.

The framebuffer is independent of any graphical representation.

Its contents shall be sufficient to reconstruct the complete display.

---

### Requirements

**REQ-EMU-312**

The logical display shall contain 64 columns and 32 rows.

**REQ-EMU-313**

Framebuffer contents shall be represented independently of the GUI.

---

## 4.9 Keyboard

The virtual machine shall support sixteen hexadecimal keys.

The current key state shall be available to the instruction execution
logic.

---

### Requirements

**REQ-EMU-314**

The keyboard shall consist of sixteen logical keys.

---

## 4.10 Reset

Reset initializes the virtual machine to its defined initial state.

Reset shall

- clear memory,
- clear registers,
- clear the stack,
- clear the framebuffer,
- clear keyboard state,
- initialize the program counter,
- initialize the timers.

---

### Requirements

**REQ-EMU-315**

Reset shall establish a completely defined machine state.

**REQ-EMU-316**

Following reset, execution shall begin at address 0x0200.

---

## 4.11 Program Loading

Programs are loaded into memory beginning at the program start address.

Loading a program does not constitute execution.

---

### Requirements

**REQ-EMU-317**

Programs shall be loaded beginning at address 0x0200.

---

## 4.12 Execution Model

Execution proceeds one instruction at a time.

Each instruction is executed atomically.

No intermediate execution state shall be externally observable.

---

### Requirements

**REQ-EMU-318**

Exactly one instruction shall be executed per execution cycle.

**REQ-EMU-319**

Instruction execution shall be atomic.

---

## 4.13 Instruction Decoder

Instruction decoding is a logical subsystem of the emulator.

The decoder shall interpret the binary opcode and determine the
corresponding CHIP-8 instruction.

The same decoding logic shall be used by both the execution engine and
the disassembler.

---

### Requirements

**REQ-EMU-320**

Instruction decoding shall occur exactly once for each executed
instruction.

**REQ-EMU-321**

Execution and disassembly shall use the same decoding logic.

---

## 4.14 Error Handling

Invalid machine states shall never occur during normal execution.

Invalid ROM data shall not compromise emulator stability.

---

### Requirements

**REQ-EMU-322**

Execution errors shall not leave the virtual machine in an undefined
state.

---

## 4.15 Extensibility

The emulator architecture shall permit future extensions while
preserving compatibility with the original CHIP-8 implementation.

Future instruction sets shall not require redesign of the existing
architecture.

---

### Requirements

**REQ-EMU-323**

Support for future virtual machines shall be achievable through
extension rather than modification whenever practical.

---

## Requirements Summary

| ID | Description |
|----|-------------|
| REQ-EMU-300 | Emulator maintains complete machine state |
| REQ-EMU-301 | Emulator independent of GUI |
| REQ-EMU-302 | Complete virtual machine state defined |
| REQ-EMU-303 | 4096-byte memory |
| REQ-EMU-304 | Program start address 0x0200 |
| REQ-EMU-305 | Sixteen general-purpose registers |
| REQ-EMU-306 | 16-bit index register |
| REQ-EMU-307 | 16-bit program counter |
| REQ-EMU-308 | Stack pointer provided |
| REQ-EMU-309 | Sixteen-level stack |
| REQ-EMU-310 | Delay timer at 60 Hz |
| REQ-EMU-311 | Sound timer at 60 Hz |
| REQ-EMU-312 | 64 × 32 display |
| REQ-EMU-313 | GUI-independent framebuffer |
| REQ-EMU-314 | Sixteen-key keyboard |
| REQ-EMU-315 | Reset establishes defined state |
| REQ-EMU-316 | Reset initializes PC to 0x0200 |
| REQ-EMU-317 | Programs loaded at 0x0200 |
| REQ-EMU-318 | One instruction per execution cycle |
| REQ-EMU-319 | Instruction execution is atomic |
| REQ-EMU-320 | One decode per executed instruction |
| REQ-EMU-321 | Shared decoder for execution and disassembly |
| REQ-EMU-322 | Execution errors preserve machine consistency |
| REQ-EMU-323 | Future extensibility without redesign |


# Chapter 5 — Graphical User Interface

---

## 5.1 Purpose

This chapter specifies the graphical user interface of the CHIP-8
Emulator.

The GUI provides visualization of the virtual machine state and allows
the user to control program execution.

The GUI shall not contain emulator logic.

---

## 5.2 Responsibilities

The GUI is responsible for

- displaying the emulator state,
- accepting user commands,
- presenting debugging information,
- displaying the framebuffer,
- updating widgets after instruction execution.

The GUI is not responsible for

- executing CHIP-8 instructions,
- modifying virtual hardware directly,
- decoding instructions.

---

### Requirements

**REQ-GUI-500**

The GUI shall communicate exclusively with the Controller.

**REQ-GUI-501**

The GUI shall not directly access emulator objects.

---

## 5.3 Main Window

The application shall provide a single main window that contains all
major user interface components.

The layout of the main window shall be defined using Qt Designer.

The corresponding `.ui` file shall be loaded dynamically at runtime.

---

### Requirements

**REQ-GUI-502**

The main window layout shall be defined in a Qt Designer `.ui` file.

**REQ-GUI-503**

The `.ui` file shall be loaded at runtime.

**REQ-GUI-504**

The graphical layout shall not be hard-coded in Python.

---

## 5.4 Display

The emulator display visualizes the current framebuffer.

The display is a passive view of the framebuffer and shall not maintain
its own copy of the emulator state.

Pixel scaling is performed by the display widget.

---

### Requirements

**REQ-GUI-505**

The display shall present the current framebuffer contents.

**REQ-GUI-506**

The display shall preserve the original CHIP-8 aspect ratio.

**REQ-GUI-507**

Display scaling shall not modify the framebuffer.

**REQ-GUI-508**

The default display colors shall be black pixels on a white background.

---

## 5.5 Debug Views

The GUI shall provide views for inspecting the virtual machine state.

These views include

- Registers
- Memory
- Stack
- Disassembly
- Keyboard

The displayed values are read-only unless explicitly stated otherwise.

---

### Requirements

**REQ-GUI-509**

The GUI shall provide a register view.

**REQ-GUI-510**

The GUI shall provide a memory view.

**REQ-GUI-511**

The GUI shall provide a stack view.

**REQ-GUI-512**

The GUI shall provide a disassembly view.

**REQ-GUI-513**

The GUI shall provide a keyboard view.

---

## 5.6 Execution Control

The GUI shall allow the user to control emulator execution.

The following operations shall be available.

- Load ROM
- Reload ROM
- Run
- Pause
- Stop
- Reset
- Single Step

---

### Requirements

**REQ-GUI-514**

The GUI shall provide a command for loading a ROM.

**REQ-GUI-515**

The GUI shall provide a command for reloading the current ROM.

**REQ-GUI-516**

The GUI shall provide Run, Pause, Stop and Reset commands.

**REQ-GUI-517**

The GUI shall provide a Single Step command.

---

## 5.7 Updating

The GUI reflects the current state of the emulator.

Updates occur after instruction execution.

The GUI shall never display intermediate execution states.

---

### Requirements

**REQ-GUI-518**

The GUI shall be refreshed after every successfully executed
instruction.

**REQ-GUI-519**

All GUI widgets shall display a consistent machine state.

---

## 5.8 User Interface Files

Qt Designer files are considered part of the project source.

The GUI implementation shall separate presentation from application
logic.

Python source code may perform widget initialization and signal
connections, but widget layout shall remain in the `.ui` files.

---

### Requirements

**REQ-GUI-520**

All major window layouts shall be stored as Qt Designer `.ui` files.

**REQ-GUI-521**

Application logic shall not be embedded in `.ui` files.

---

## 5.9 Extensibility

The GUI architecture shall permit additional debugger windows and
widgets without redesign of the existing interface.

---

### Requirements

**REQ-GUI-522**

Future GUI extensions shall preserve compatibility with the existing
controller interface.

---

## Requirements Summary

| ID | Description |
|----|-------------|
| REQ-GUI-500 | GUI communicates only with the Controller |
| REQ-GUI-501 | GUI shall not access emulator objects |
| REQ-GUI-502 | Main window designed with Qt Designer |
| REQ-GUI-503 | UI file loaded at runtime |
| REQ-GUI-504 | Layout not hard-coded |
| REQ-GUI-505 | Display shows framebuffer |
| REQ-GUI-506 | Preserve CHIP-8 aspect ratio |
| REQ-GUI-507 | Scaling independent of framebuffer |
| REQ-GUI-508 | Default colors are black on white |
| REQ-GUI-509 | Register view |
| REQ-GUI-510 | Memory view |
| REQ-GUI-511 | Stack view |
| REQ-GUI-512 | Disassembly view |
| REQ-GUI-513 | Keyboard view |
| REQ-GUI-514 | Load ROM |
| REQ-GUI-515 | Reload ROM |
| REQ-GUI-516 | Run/Pause/Stop/Reset |
| REQ-GUI-517 | Single-step execution |
| REQ-GUI-518 | Refresh after every instruction |
| REQ-GUI-519 | Widgets display a consistent machine state |
| REQ-GUI-520 | Window layouts stored as `.ui` files |
| REQ-GUI-521 | Application logic separated from UI files |
| REQ-GUI-522 | GUI remains extensible |

# 6. Code Analysis and Code View

## 6.1 Purpose

The Code View is a debugger component that presents an interpreted view of the CHIP-8 program memory.

Unlike a traditional disassembler, it is not intended to reconstruct the original source program. Instead, it presents the current knowledge about the executable structure of the loaded program while preserving visibility of all program bytes.

The Code View shall therefore distinguish between information that is known with certainty and information that is currently unknown.

The Code View is intended to assist understanding and debugging of CHIP-8 programs rather than reconstructing the original source code.

---

## 6.2 Design Goals

The Code Analysis subsystem shall satisfy the following goals:

- Provide an accurate representation of the program structure.
- Never present assumptions as confirmed knowledge.
- Allow inspection of all program bytes, including regions whose purpose is currently unknown.
- Integrate cleanly into the existing emulator-controller-GUI architecture.
- Minimize the performance impact on the emulator.
- Preserve emulator responsiveness while providing runtime code analysis.
- Support future debugger extensions such as breakpoints and instruction execution tracing.

---

## 6.3 Functional Requirements

### FR-6.3.1 Initial Analysis

Upon loading a ROM, the system shall perform an initial analysis beginning at memory address `0x0200`.

### FR-6.3.2 Runtime Analysis

The system shall improve its knowledge of the program structure during program execution.

### FR-6.3.3 Code View

The Code View shall:

- display the complete contents of the loaded program memory,
- ensure that all program bytes remain visible,
- distinguish between confirmed executable instructions and memory of unknown purpose,
- never present unknown memory as confirmed executable code.

### FR-6.3.4 Instruction Representation

- Executable instructions shall be displayed using the mnemonic generated by the `Instruction` class.
- Unknown memory shall be displayed as raw hexadecimal byte values.

### FR-6.3.5 Consistency

The Code View shall always present a consistent representation of the current analysis state.

---

## 6.4 User Interface Requirements

The Code View shall contain the following columns:

| Column | Description |
|---------|-------------|
| BP | Breakpoint indicator (reserved for future functionality). |
| Addr | Start address of the displayed entry. |
| Bytes | Raw byte values represented by the entry. |
| Interpretation | Instruction mnemonic or hexadecimal byte representation. |
| Status | Classification of the entry (e.g. Code or Unknown). |

Additional requirements:

- The current program counter shall be visually highlighted.
- The Code View shall automatically follow the current instruction during program execution.
- The user shall be able to disable automatic realtime updates.
- The visual representation of the different classifications is implementation-defined.

---

## 6.5 Performance Requirements

### PR-6.5.1

Debugger functionality shall not significantly reduce emulator execution performance.

### PR-6.5.2

The graphical user interface shall update only information whose visible representation has changed.

### PR-6.5.3

Repeated reconstruction of graphical user interface elements shall be avoided whenever possible.

### PR-6.5.4

The user shall be able to suspend automatic realtime updates of the Code View.

### PR-6.5.5

Suspending realtime updates shall not affect emulator execution.

### PR-6.5.6

When realtime updates are re-enabled, the Code View shall be synchronized with the current emulator state.

---

## 6.6 Architectural Requirements

### AR-6.6.1

The emulator shall remain independent of the graphical user interface.

### AR-6.6.2

The Code Analysis subsystem shall remain independent of the graphical user interface.

### AR-6.6.3

The Controller shall coordinate communication between the emulator, the Code Analysis subsystem and the graphical user interface.

### AR-6.6.4

Instruction decoding shall remain the responsibility of the `Instruction` class.

---

## 6.7 Design Principles

### DP-6.7.1 Separation of Responsibilities

Each subsystem shall have a single clearly defined responsibility.

### DP-6.7.2 Conservative Interpretation

The system shall not present uncertain information as confirmed program structure.

### DP-6.7.3 Event-Driven Operation

Analysis and updates shall be triggered by relevant system events rather than continuous polling.

### DP-6.7.4 Responsiveness

Maintaining emulator responsiveness shall take priority over immediate visual updates.

### DP-6.7.5 Minimal Intrusion

Debugger-related functionality shall not modify or interfere with emulator execution semantics.

---
## 6.8 Software Design

### 6.8.1 Overview

The Code Analysis subsystem is responsible for maintaining an interpreted view of the CHIP-8 program memory for presentation in the Code View.

It derives information from the current emulator state without modifying emulator behavior or becoming part of the emulator itself.

The subsystem is coordinated by the Controller and remains independent of both the graphical user interface and the emulator implementation.

---

### 6.8.2 Architecture

The following diagram illustrates the integration of the Code Analysis subsystem into the existing emulator architecture.

```text
                         +----------------------+
                         |      MainWindow      |
                         +----------+-----------+
                                    ^
                                    |
                         +----------+-----------+
                         |      Controller      |
                         +----+-----------+-----+
                              |           |
                              |           |
                              |           v
                              |   +---------------+
                              |   | CodeTableModel|
                              |   +-------+-------+
                              |           |
                              |           v
                              |     QTableView
                              |
                              v
                  +----------------------------+
                  | Code Analysis Subsystem    |
                  +-------------+--------------+
                                |
                                | read-only
                                |
                  +-------------v--------------+
                  |       Chip8Machine         |
                  +-------------+--------------+
                                |
                                v
                          Chip8Memory
```

The `Chip8Machine` remains the sole owner of the emulator state.

The Code Analysis subsystem derives information from the current memory contents but never modifies emulator state.

The Controller coordinates communication between the emulator, the Code Analysis subsystem, and the graphical user interface.

The `CodeTableModel` converts the analysis results into a representation suitable for display by the Qt `QTableView`.

---

### 6.8.3 Responsibilities

#### Chip8Machine

- Own the complete emulator state.
- Execute CHIP-8 instructions.
- Provide read-only access to the current memory contents.

#### Code Analysis Subsystem

- Maintain an interpretation of the current program memory.
- Distinguish executable code from memory of unknown purpose.
- Provide analysis results to the Code View.

#### Controller

- Coordinate emulator execution.
- Invoke the Code Analysis subsystem when required.
- Synchronize the graphical user interface with the emulator and analysis state.

#### CodeTableModel

- Present the analysis results in tabular form.
- Convert the current analysis state into rows displayed by the Code View.
- Notify the Qt view of changes.

---

### 6.8.4 System Integration

The Code Analysis subsystem is integrated into the application through the Controller.

The authoritative source of emulator state is the `Chip8Machine`, including its `Chip8Memory` component.

The Code Analysis subsystem performs read-only analysis of the current memory contents.

Whenever relevant emulator events occur, such as loading a ROM, resetting the emulator, or executing instructions, the Controller determines when the Code Analysis subsystem shall update its internal state and when the graphical user interface shall be refreshed.

The Code Analysis subsystem maintains only derived information describing the current interpretation of program memory.

---

### 6.8.5 Data Flow

The following diagram illustrates the flow of information during normal execution.

```text
Instruction Executed
        │
        ▼
 Chip8Machine
        │
        ▼
   StepResult
        │
        ▼
   Controller
        │
        ├── Update debugger views
        ├── Invoke Code Analysis
        └── Refresh Code View
```

During ROM loading or emulator reset, the Controller performs the corresponding initialization sequence before requesting a complete update of the Code Analysis subsystem and the Code View.

The Code Analysis subsystem shall operate in an event-driven manner. It shall not continuously poll emulator memory or execute independently of the Controller.



# Chapter 7 — Build System

---

## 7.1 Purpose

This chapter specifies the build system, project configuration, and
development tools required for the CHIP-8 Emulator.

The project uses a modern Python-based development environment with
CMake serving as the primary build orchestration tool.

The build system shall provide a consistent interface for building,
running, testing, formatting, static analysis, and documentation
generation.

---

## 7.2 Build Environment

The reference development platform is Linux using Python 3.13.

The project shall remain portable to other operating systems whenever
practical.

### Requirements

**REQ-BUILD-700**

The minimum supported Python version shall be 3.12.

**REQ-BUILD-701**

The reference development environment shall use Python 3.13.

---

## 7.3 Build System

CMake is the primary entry point for all development tasks.

Developers should not be required to remember individual tool commands.

### Requirements

**REQ-BUILD-702**

CMake shall be used as the primary build interface.

**REQ-BUILD-703**

Frequently used development tasks shall be available as CMake targets.

---

## 7.4 Project Configuration

Project metadata shall be maintained in a single location.

The project configuration file defines

- package metadata,
- Python dependencies,
- development dependencies,
- tool configuration.

### Requirements

**REQ-BUILD-704**

Project metadata shall be maintained in `pyproject.toml`.

**REQ-BUILD-705**

Tool configuration shall be maintained in `pyproject.toml` whenever
supported.

---

## 7.5 Documentation

Source code documentation shall be generated automatically.

Documentation generation shall not require manual editing of generated
files.

### Requirements

**REQ-BUILD-706**

API documentation shall be generated using Doxygen.

**REQ-BUILD-707**

If Graphviz is available, call graphs and caller graphs shall be
generated.

---

## 7.6 Static Analysis

Static analysis forms part of the normal development workflow.

Formatting and analysis tools shall be executable through CMake.

### Requirements

**REQ-BUILD-708**

Source formatting shall use Ruff.

**REQ-BUILD-709**

Static type analysis shall use mypy.

**REQ-BUILD-710**

The project shall provide a target that performs all static analysis
steps.

---

## 7.7 Standard Build Targets

The build system shall provide the following targets.

| Target | Purpose |
|---------|---------|
| run | Execute the emulator |
| format | Format Python source files |
| lint | Run static linting |
| typecheck | Run mypy |
| all_checks | Execute all analysis tools |
| docs | Generate documentation |
| clean_python | Remove Python cache files |
| info | Display available build targets |

Additional targets may be introduced provided they remain consistent
with the development workflow.

### Requirements

**REQ-BUILD-711**

The build system shall provide the standard development targets defined
above.

---

## 7.8 Dependencies

The project shall minimize external dependencies.

Dependencies shall be selected according to the following priorities.

1. Correctness
2. Stability
3. Maintainability
4. Community support

### Requirements

**REQ-BUILD-712**

Only dependencies required by the project shall be included.

**REQ-BUILD-713**

Unused dependencies shall be removed.

---

## 7.9 Repository Organization

The source repository shall contain only files required for development,
building, testing, and documentation.

Generated files shall not be committed unless explicitly required.

### Requirements

**REQ-BUILD-714**

Generated files shall be excluded from version control.

---

## Requirements Summary

| ID | Description |
|----|-------------|
| REQ-BUILD-700 | Python 3.12 minimum |
| REQ-BUILD-701 | Python 3.13 reference environment |
| REQ-BUILD-702 | CMake is the primary build interface |
| REQ-BUILD-703 | Common tasks exposed as CMake targets |
| REQ-BUILD-704 | Project metadata in `pyproject.toml` |
| REQ-BUILD-705 | Tool configuration in `pyproject.toml` |
| REQ-BUILD-706 | Doxygen documentation |
| REQ-BUILD-707 | Generate call graphs when Graphviz is available |
| REQ-BUILD-708 | Ruff formatting |
| REQ-BUILD-709 | mypy type checking |
| REQ-BUILD-710 | Provide an `all_checks` target |
| REQ-BUILD-711 | Standard development targets |
| REQ-BUILD-712 | Keep dependencies minimal |
| REQ-BUILD-713 | Remove unused dependencies |
| REQ-BUILD-714 | Do not commit generated files |

# Chapter 8 — Development Process

---

## 8.1 Purpose

This chapter defines the software development process used throughout
the CHIP-8 Emulator project.

The objective is to ensure that development proceeds in a controlled,
incremental, and verifiable manner while maintaining software quality
and architectural consistency.

---

## 8.2 Development Philosophy

Development shall proceed incrementally.

Every completed milestone shall result in a working application.

Large-scale rewrites and speculative development shall be avoided.

Whenever practical, new functionality shall be added in small,
independently verifiable increments.

### Requirements

**REQ-DEV-800**

Development shall proceed in incremental milestones.

**REQ-DEV-801**

The application shall remain executable after every completed
milestone.

---

## 8.3 Milestones

Development milestones define logical stages of project completion.

Each milestone shall have

- a clearly defined objective,
- measurable completion criteria,
- successful verification before proceeding.

Implementation of a new milestone shall not begin until the current
milestone has been completed.

### Requirements

**REQ-DEV-802**

Each milestone shall define explicit completion criteria.

**REQ-DEV-803**

Completed milestones shall not be revisited except to correct defects
or perform approved refactoring.

---

## 8.4 Verification

Every new feature shall be verified before additional functionality is
implemented.

Verification may include

- successful execution,
- code review,
- static analysis,
- documentation review.

### Requirements

**REQ-DEV-804**

New functionality shall be verified before further development
continues.

**REQ-DEV-805**

The project shall pass all configured static analysis tools before a
milestone is considered complete.

---

## 8.5 Documentation

Documentation shall evolve together with the implementation.

Architectural decisions shall be documented before implementation.

API documentation shall be updated whenever public interfaces change.

### Requirements

**REQ-DEV-806**

The SRDS shall be updated before implementing architectural changes.

**REQ-DEV-807**

Public API documentation shall remain synchronized with the source code.

---

## 8.6 Source Control

The complete project shall be maintained under version control.

Each commit should represent a coherent and logically complete change.

Generated files shall not be committed unless explicitly required.

### Requirements

**REQ-DEV-808**

Version control shall be used throughout development.

**REQ-DEV-809**

Each commit should represent one logical change.

---

## 8.7 Refactoring

Refactoring is encouraged when it improves

- readability,
- maintainability,
- modularity,
- consistency.

Refactoring shall not alter externally observable behaviour.

### Requirements

**REQ-DEV-810**

Refactoring shall preserve functional behaviour.

---

## 8.8 Deferred Features

Features outside the scope of the current release shall be documented
rather than implemented prematurely.

Architectural extensibility shall not be confused with implementing
future functionality.

### Requirements

**REQ-DEV-811**

Deferred features shall remain deferred until explicitly scheduled.

### Design Rules

**RULE-DEV-800**

Feature creep shall be actively avoided.

---

## 8.9 Release Criteria

A development version may be considered complete when

- all planned functionality has been implemented,
- all requirements have been satisfied,
- documentation has been updated,
- static analysis succeeds,
- the application executes correctly.

### Requirements

**REQ-DEV-812**

A release shall satisfy all documented requirements applicable to that
version.

---

## Requirements Summary

| ID | Description |
|----|-------------|
| REQ-DEV-800 | Incremental development |
| REQ-DEV-801 | Application remains runnable |
| REQ-DEV-802 | Milestones have completion criteria |
| REQ-DEV-803 | Completed milestones are not reopened unnecessarily |
| REQ-DEV-804 | Verify before continuing |
| REQ-DEV-805 | Static analysis must succeed |
| REQ-DEV-806 | Update SRDS before architectural changes |
| REQ-DEV-807 | Keep API documentation synchronized |
| REQ-DEV-808 | Use version control |
| REQ-DEV-809 | One logical change per commit |
| REQ-DEV-810 | Refactoring preserves behaviour |
| REQ-DEV-811 | Deferred features remain deferred |
| REQ-DEV-812 | Releases satisfy documented requirements |
| RULE-DEV-800 | Avoid feature creep |

# Appendix A — Glossary

---

## Purpose

This appendix defines the terminology used throughout this
specification.

Unless explicitly stated otherwise, the definitions in this appendix
shall apply throughout the entire SRDS.

---

## Terms

| Term | Definition |
|------|------------|
| CHIP-8 | The virtual computer originally developed by Joseph Weisbecker during the 1970s. |
| Emulator | The complete software system implementing the CHIP-8 virtual machine. |
| Virtual Machine | The software representation of the original CHIP-8 hardware. |
| ROM | A CHIP-8 program loaded into emulator memory. |
| Opcode | A 16-bit binary instruction. |
| Instruction | The operation represented by an opcode. |
| Decoder | The subsystem that converts an opcode into an executable instruction. |
| Disassembler | The subsystem that converts an opcode into human-readable assembly language. |
| Controller | The software component coordinating communication between the GUI and the emulator. |
| GUI | The graphical user interface. |
| Framebuffer | The logical display memory containing the current screen image. |
| Display | The graphical representation of the framebuffer. |
| Cycle | Execution of exactly one CHIP-8 instruction. |
| PC | Program Counter. |
| SP | Stack Pointer. |
| I Register | The CHIP-8 index register. |
| Delay Timer | Timer decrementing at 60 Hz. |
| Sound Timer | Timer controlling the audible tone. |

---

## Naming Conventions

Throughout this specification

- *instruction* refers to a logical operation.
- *opcode* refers to its binary encoding.
- *display* refers to the graphical representation.
- *framebuffer* refers to the logical pixel storage.
- *machine* refers to the virtual hardware.
- *emulator* refers to the complete software application.

These terms shall not be used interchangeably.

# Appendix B — CHIP-8 Memory Map

---

## Overview

The CHIP-8 virtual machine provides 4096 bytes of addressable memory.

Memory addresses range from

```
0x000
```

through

```
0xFFF
```

---

## Memory Layout

| Address Range | Purpose |
|---------------|---------|
| 0x000–0x1FF | Reserved for interpreter resources |
| 0x050–0x09F | Default hexadecimal font set |
| 0x200–0xFFF | Program memory |

Programs are loaded beginning at address

```
0x200
```

---

## Notes

The original CHIP-8 interpreter occupied the lower memory region.

Modern emulators generally reserve this area for compatibility,
although they are not required to emulate the original interpreter.

# Appendix C — Keyboard Layout

---

The CHIP-8 keyboard consists of sixteen hexadecimal keys.

Logical layout

```
1 2 3 C
4 5 6 D
7 8 9 E
A 0 B F
```

Recommended PC keyboard mapping

```
1 2 3 4
Q W E R
A S D F
Z X C V
```

| CHIP-8 | PC |
|--------|----|
| 1 | 1 |
| 2 | 2 |
| 3 | 3 |
| C | 4 |
| 4 | Q |
| 5 | W |
| 6 | E |
| D | R |
| 7 | A |
| 8 | S |
| 9 | D |
| E | F |
| A | Z |
| 0 | X |
| B | C |
| F | V |

# Appendix D — Project Directory Structure

---

```
chip8/
│
├── CMakeLists.txt
├── pyproject.toml
├── README.md
├── LICENSE
│
├── doc/
│   ├── Software_Requirements_and_Design_Specification.md
│   └── Doxyfile.in
│
├── src/
│   ├── chip8/
│   │   ├── __main__.py
│   │   └── version.py
│   │
│   ├── controller/
│   ├── emulator/
│   ├── gui/
│   │   └── ui/
│   └── util/
│
├── tests/
│
└── build/
```

The `build/` directory is generated and shall not be committed to
version control.

# Appendix E — References

---

## CHIP-8

Cowgod's CHIP-8 Technical Reference

Octo Documentation

Original CHIP-8 documentation

---

## Python

Python Language Reference

Python Standard Library

---

## Qt

Qt Documentation

PyQt6 Documentation

Qt Designer Manual

---

## Development Tools

CMake Documentation

Doxygen Manual

Graphviz Documentation

Ruff Documentation

mypy Documentation

NumPy Documentation

# Appendix F — Requirement Traceability Matrix

---

The following table links requirements to their implementation.

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| REQ-ARCH-106 | Chip8Controller | Planned |
| REQ-GUI-503 | MainWindow | Implemented |
| REQ-GUI-505 | DisplayWidget | Implemented |
| REQ-EMU-303 | Chip8Memory | Planned |
| REQ-EMU-320 | InstructionDecoder | Planned |

The traceability matrix shall be updated whenever new functionality is
implemented.


