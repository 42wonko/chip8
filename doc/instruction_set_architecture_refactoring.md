# Table of Contents

- [Instruction Set Architecture Refactoring](#instruction-set-architecture-refactoring)
  - [Purpose](#purpose)
  - [Motivation](#motivation)
  - [Design Goals](#design-goals)
  - [Architectural Principles](#architectural-principles)
    - [Single Source of Truth](#single-source-of-truth)
    - [Behaviour over Interpretation](#behaviour-over-interpretation)
    - [Separation of Concerns](#separation-of-concerns)
    - [Open for Extension](#open-for-extension)
  - [Target Architecture](#target-architecture)
  - [Instruction Set Architecture](#instruction-set-architecture)
    - [Responsibilities](#responsibilities)
    - [Construction](#construction)
    - [Decoding](#decoding)
    - [Instruction Identifiers](#instruction-identifiers)
  - [Instruction](#instruction)
    - [Responsibilities](#responsibilities-1)
    - [Stored Information](#stored-information)
    - [Public Interface](#public-interface)
  - [Subsystem Integration](#subsystem-integration)
    - [Emulator](#emulator)
    - [Static Code Analyzer](#static-code-analyzer)
    - [Debugger / Disassembler](#debugger--disassembler)
    - [Future Assembler](#future-assembler)
  - [Migration Strategy](#migration-strategy)
    - [Phase 1 — Introduce the ISA Layer](#phase-1--introduce-the-isa-layer)
    - [Phase 2 — Migrate the Debugger / Disassembler](#phase-2--migrate-the-debugger--disassembler)
    - [Phase 3 — Migrate the Static Code Analyzer](#phase-3--migrate-the-static-code-analyzer)
    - [Phase 4 — Migrate Emulator Execution](#phase-4--migrate-emulator-execution)
    - [Phase 5 — Remove Obsolete Logic](#phase-5--remove-obsolete-logic)
  - [Testing Strategy](#testing-strategy)
  - [Future Extensions](#future-extensions)
  - [Out of Scope](#out-of-scope)
  - [Progress Checklist](#progress-checklist)

---

# Instruction Set Architecture Refactoring

## Purpose

This document describes the refactoring of the CHIP-8 emulator towards a centralized **Instruction Set Architecture (ISA)** design.

The primary objective of this refactoring is to establish a single authoritative implementation of the CHIP-8 instruction set. All knowledge about instruction encoding, decoding, execution semantics, formatting, and control-flow semantics shall reside exclusively within the ISA layer.

The ISA layer becomes the architectural boundary between the generic emulator infrastructure and the CHIP-8 instruction set. Components such as the emulator, static code analyzer, debugger, disassembler, and future assembler shall interact exclusively with the ISA instead of implementing their own instruction decoding or opcode interpretation.

This document describes the motivation, design goals, target architecture, migration strategy, and implementation plan for this refactoring.

---

## Motivation

The current implementation has evolved over time and now contains multiple independent implementations of instruction decoding and instruction set semantics.

Opcode decoding currently exists in several subsystems, including:

- Emulator execution
- Static code analysis
- Disassembly and formatting

Although these implementations perform different tasks, they all interpret the same machine instructions independently. This results in duplicated knowledge about the CHIP-8 instruction set throughout the project.

The duplication has several disadvantages:

- instruction set semantics must be maintained in multiple locations.
- Adding or modifying instructions requires changes in several independent subsystems.
- Supporting additional CHIP-8 variants becomes increasingly difficult.
- Behaviour between emulator, debugger and code analyzer can diverge over time.
- Maintenance effort grows with every extension of the instruction set.

The purpose of this refactoring is to eliminate this duplication by introducing a single architectural component that models the complete instruction set.

---

## Design Goals

The refactoring shall satisfy the following design goals.

### Single Source of Truth

All knowledge about the CHIP-8 instruction set shall reside exclusively within the Instruction Set Architecture.

No other subsystem shall decode opcodes or interpret instruction set semantics.

### Separation of Responsibilities

The emulator shall execute instructions without possessing any knowledge of opcode encoding.

The static code analyzer shall perform generic control-flow analysis without interpreting opcode values.

The debugger and disassembler shall obtain assembly representations directly from decoded instructions instead of implementing independent formatting logic.

Future assembler implementations shall use the same ISA definitions as the emulator.

### Extensibility

The architecture shall support future CHIP-8 variants by replacing or extending the ISA implementation rather than modifying individual subsystems.

Supporting Classic CHIP-8, CHIP-48, Super-CHIP or XO-CHIP shall require only the introduction of a corresponding ISA implementation.

### Maintainability

Instruction behaviour shall be implemented exactly once.

Changes to an instruction shall automatically affect every subsystem using the ISA.

### Incremental Migration

The existing emulator shall remain functional throughout the refactoring.

The ISA shall initially coexist with the existing implementation until each subsystem has been migrated.

Existing functionality shall remain unchanged during the migration.

---

# Architectural Principles

The following principles govern the design of the ISA.

## Single Source of Truth

The ISA shall contain the complete definition of the instruction set.

## Behaviour over Interpretation

Subsystems shall invoke operations provided by decoded instructions rather than interpreting opcode values.

## Separation of Concerns

The ISA owns instruction set semantics.

The emulator owns machine execution.

The static code analyzer owns graph traversal.

The debugger owns presentation.

## Open for Extension

Support for additional CHIP-8 variants shall be achieved by implementing additional ISA classes rather than modifying existing subsystems.

---

# Target Architecture

The refactoring introduces a new architectural layer named the **Instruction Set Architecture (ISA)**.

The ISA represents a complete executable definition of a specific CHIP-8 instruction set. It is responsible for decoding machine instructions and providing the complete semantics of every instruction supported by that architecture.

All instruction-specific knowledge is centralized within the ISA. The remaining subsystems operate exclusively on decoded `Instruction` objects and therefore remain independent of opcode encoding and instruction set semantics.

The architecture consists of two principal classes:

- `InstructionSetArchitecture`
- `Instruction`

`InstructionSetArchitecture` acts as a service object that implements the behaviour of the instruction set.

`Instruction` is an immutable value object representing one decoded instruction currently stored in memory.

The overall architecture is illustrated below.

```text
                     +--------------------------------+
                     | InstructionSetArchitecture      |
                     |--------------------------------|
                     | decode()                       |
                     | execute()                      |
                     | format()                       |
                     | analyze()                      |
                     +---------------+----------------+
                                     ^
                                     |
                  derives            |
                                     |
          +--------------------------+-------------------------+
          |                                                    |
+----------------------------+                  +----------------------------+
| ClassicInstructionSet...   |                  | SuperChipInstructionSet... |
+----------------------------+                  +----------------------------+

                     produces

                            |
                            ▼

                  +------------------------+
                  | Instruction            |
                  |------------------------|
                  | address                |
                  | opcode                 |
                  | id                     |
                  | x                      |
                  | y                      |
                  | n                      |
                  | nn                     |
                  | nnn                    |
                  +------------------------+
```

The ISA becomes the only component that possesses knowledge about opcode encoding and instruction set semantics.

The emulator, static code analyzer, debugger, disassembler and future assembler interact exclusively with the services provided by the ISA.

No subsystem outside the ISA shall decode opcodes or interpret instruction set semantics.

---

# Instruction Set Architecture

The ISA internally dispatches instruction services using `InstructionId`.

Execution, formatting and static analysis are implemented independently and therefore use separate dispatch tables.

The choice of dispatch mechanism is an implementation detail and is not part of the architectural contract.

## Responsibilities

`InstructionSetArchitecture` represents a complete executable definition of a CHIP-8 instruction set.

It is the sole authority for instruction decoding and instruction set semantics.

Its responsibilities are to

- decode machine instructions,
- construct immutable `Instruction` objects,
- execute decoded instructions,
- format decoded instructions,
- provide static control-flow information for decoded instructions,
- provide a single authoritative implementation of the instruction set.

No other subsystem shall decode opcodes or interpret instruction set semantics.

---

## Construction

The ISA owns the semantics of the instruction set and therefore requires access to the emulated machine.

```python
machine = Chip8Machine(...)

isa = ClassicInstructionSetArchitecture(machine)
```

The machine instance is retained by the ISA and is used by instruction execution handlers to modify emulator state.

The ISA intentionally has no dependency on the static code analyzer, debugger, disassembler or assembler.

Those components invoke ISA services but are not owned by the ISA.

---

## Decoding

The ISA exposes a single public decoding function.

```python
instruction = isa.decode(address, opcode)
```

The decoder is responsible for

- validating the instruction encoding,
- identifying the instruction,
- assigning the corresponding `InstructionId`,
- extracting all operands,
- constructing the immutable `Instruction` object.

The decoder performs no execution and no formatting.

Its sole responsibility is to transform a 16-bit opcode into a decoded instruction.

Every decoded instruction is created exclusively by the ISA.

---

## Instruction Identifiers

Every decoded instruction is assigned a symbolic `InstructionId`.

Instruction identifiers uniquely identify complete instruction encodings rather than mnemonic families.

For example,

- `SE Vx, NN`
- `SE Vx, Vy`

are represented by different instruction identifiers.

Instruction identifiers are used internally by the ISA to dispatch instruction execution, formatting and static analysis.

The numeric representation of an instruction identifier is considered an implementation detail.

Source code outside the ISA shall never depend on numeric identifier values.

---

## Execution

Instruction execution is performed by the ISA.

```python
step_result = isa.execute(instruction)
```

Execution semantics are selected internally by the ISA using the instruction's `InstructionId`.

The dispatch mechanism is an implementation detail and is not visible outside the ISA.

Execution returns a `StepResult`, allowing the emulator and runtime code analysis to continue operating without architectural changes.

---

## Formatting

Assembly language formatting is provided by the ISA.

```python
text = isa.format(instruction)
```

The debugger and disassembler shall obtain textual instruction representations exclusively through this interface.

No subsystem outside the ISA shall generate assembly mnemonics.

---

## Static Analysis

Static control-flow information is provided by the ISA.

```python
next_states = isa.analyze(instruction, work_item)
```

The analyzer remains responsible for graph traversal, simulated call-stack management and code classification.

Instruction-specific control-flow semantics are implemented exclusively by the ISA.

---

# Instruction

## Responsibilities

An `Instruction` represents one decoded instruction located at a specific memory address.

Unlike the ISA, an `Instruction` contains **no behaviour**. It is an immutable value object that stores the decoded representation of a single machine instruction.

Its purpose is to transfer decoded instruction information between the various subsystems of the emulator without exposing opcode encoding or instruction set semantics.

Every `Instruction` instance is created exclusively by the ISA.

---

## Stored Information

Every decoded instruction contains the following information.

| Member | Description |
| ------- | ----------- |
| `address` | Address of the instruction in memory |
| `opcode` | Original 16-bit opcode |
| `id` | Symbolic instruction identifier (`InstructionId`) |
| `x` | X register operand |
| `y` | Y register operand |
| `n` | Lowest nibble |
| `nn` | Immediate byte |
| `nnn` | Immediate address |

These fields are extracted during decoding and remain immutable for the lifetime of the instruction.

The symbolic `InstructionId` uniquely identifies the decoded instruction and serves as the dispatch key for all ISA services.

Every legal CHIP-8 instruction encoding has its own unique `InstructionId`.

Instruction identifiers represent complete instructions rather than mnemonic families. For example,

- `SE Vx, NN`
- `SE Vx, Vy`

are represented by different instruction identifiers.

---

## Public Interface

The `Instruction` class intentionally exposes no behavioural operations.

Instruction execution, formatting and static analysis are services provided by the ISA.

Typical usage therefore becomes

```python
instruction = isa.decode(address, opcode)

step_result = isa.execute(instruction)

text = isa.format(instruction)

next_states = isa.analyze(instruction, work_item)
```

This separation ensures that decoded instructions remain immutable data objects while all instruction set semantics remain centralized within the ISA.

---

# Subsystem Integration

## Emulator

The emulator is responsible for fetching instructions from memory and advancing the program counter.

Instruction decoding and execution semantics are delegated entirely to the ISA.

The emulator execution loop therefore becomes conceptually equivalent to:

```python
opcode = fetch_word(pc)

instruction = isa.decode(pc, opcode)

isa.execute(instruction)
```

The emulator neither interprets opcode values nor performs instruction decoding.

Its responsibilities are limited to:

- fetching instruction words,
- invoking the ISA decoder,
- executing the decoded instruction,
- managing the execution cycle.

This separation removes all opcode-specific logic from the emulator.

---

## Static Code Analyzer

The static code analyzer performs generic control-flow analysis.

It no longer contains knowledge about individual CHIP-8 instructions.

Instructions are decoded through the ISA.

```python
instruction = isa.decode(address, opcode)
```

The analyzer then requests the control-flow semantics of the decoded instruction.

```python
next_states = isa.analysis(instruction, work_item)
```

The returned control-flow information is used to construct the program's control-flow graph.

The analyzer remains responsible for

- work-list management,
- traversal of the control-flow graph,
- simulated call-stack management,
- detection of recursive call paths,
- runtime discovery of BNNN targets,
- code/data classification.

Instruction-specific behaviour is entirely delegated to the ISA.

---

## Debugger / Disassembler

The debugger and disassembler operate exclusively on decoded instructions.

Instruction formatting is provided by the instruction itself.

```python
text = isa.format(instruction)
```

Formatting logic is therefore implemented exactly once within the ISA.

No subsystem outside the ISA generates assembly mnemonics or interprets opcode values.

---

## Future Assembler

Although assembler implementation is outside the scope of this refactoring, the architecture has been designed to support it.

The assembler shall target the same ISA implementation used by the emulator.

This guarantees that

- instruction encoding,
- operand validation,
- instruction syntax,

remain consistent across assembler, emulator and debugger.

Supporting additional CHIP-8 variants shall require only the implementation of a corresponding ISA.

---

# Migration Strategy

The refactoring shall be performed incrementally.

At every stage the emulator shall remain fully functional. Existing functionality shall continue to operate while individual subsystems are migrated to the new ISA.

The migration intentionally introduces the ISA alongside the existing implementation. Existing decoding logic shall only be removed after every subsystem has been successfully migrated.

---

## Phase 1 — Introduce the ISA Layer

Create the `InstructionSetArchitecture` class hierarchy and integrate it into the project without affecting existing functionality.

The ISA shall become the single location responsible for instruction decoding.

Initially, the existing emulator shall continue to use its current implementation.

**Deliverables**

- Introduce the `InstructionSetArchitecture` base class.
- Implement the Classic CHIP-8 ISA.
- Implement `decode(address, opcode)`.
- Introduce the `Instruction` runtime object.
- Verify that the new decoder produces correct decoded instructions.

---

## Phase 2 — Migrate the Debugger / Disassembler

Replace all instruction formatting logic by the ISA.

The debugger and disassembler shall obtain formatted assembly text exclusively through decoded `Instruction` objects.

**Deliverables**

- Replace existing formatting logic.
- Remove duplicate mnemonic generation.
- Verify identical debugger output.

---

## Phase 3 — Migrate the Static Code Analyzer

Replace opcode interpretation inside the static code analyzer.

The analyzer shall perform only generic graph traversal while obtaining instruction-specific control-flow information from decoded instructions.

**Deliverables**

- Decode instructions through the ISA.
- Replace opcode matching by `isa.analysis(...)`.
- Preserve existing BNNN runtime target discovery.
- Preserve existing diagnostics.
- Verify identical code analysis results.

---

## Phase 4 — Migrate Emulator Execution

Replace instruction execution inside the emulator.

Execution semantics shall become part of the ISA.

The emulator shall no longer interpret opcode values.

**Deliverables**

- Decode instructions through the ISA.
- Replace opcode dispatch with `isa.execute(instruction)`.
- Preserve emulator behaviour.
- Preserve debugger behaviour.
- Preserve execution tracing.

---

## Phase 5 — Remove Obsolete Logic

After every subsystem has been migrated, remove the previous implementations.

At the completion of this phase, the ISA shall become the only implementation of the CHIP-8 instruction set.

**Deliverables**

- Remove obsolete opcode decoding.
- Remove obsolete instruction formatting.
- Remove obsolete execution dispatch.
- Remove obsolete control-flow decoding.
- Remove redundant helper functions.
- Remove duplicated instruction set semantics.

---

# Testing Strategy

The refactoring shall preserve the observable behaviour of the emulator throughout every migration phase.

After each completed phase, the following conditions shall be verified.

## Functional Verification

- Emulator behaviour shall remain unchanged.
- Debugger behaviour shall remain unchanged.
- Static code analysis shall produce identical results.
- Instruction formatting shall remain unchanged.
- Runtime BNNN target discovery shall remain fully functional.

## Code Quality

After every migration step:

- all unit tests shall pass,
- Ruff shall remain clean,
- mypy shall remain clean.

## Regression Testing

Once the regression ROM suite has been implemented, it shall become the primary verification tool for this refactoring.

All supported ROMs shall execute identically before and after each migration step.

---

# Future Extensions

The ISA has been designed to support future extensions without requiring modifications to existing subsystems.

Possible future extensions include:

- Classic CHIP-8
- CHIP-48
- Super-CHIP
- XO-CHIP

Supporting an additional instruction set shall require only the implementation of a corresponding `InstructionSetArchitecture`.

No changes shall be required to the emulator, debugger, static code analyzer or assembler.

Additional tooling, such as disassemblers, optimizers or documentation generators, shall likewise consume decoded `Instruction` objects instead of interpreting machine code directly.

---

# Out of Scope

The following topics are explicitly outside the scope of this refactoring.

- Functional changes to the emulator.
- Behavioural changes to existing CHIP-8 instructions.
- Performance optimization.
- Introduction of additional CHIP-8 variants.
- Assembler implementation.
- Regression ROM suite implementation.

These items may be addressed by future development efforts but are not considered part of this refactoring.

---

# Progress Checklist

- [ ] Introduce the ISA layer
- [ ] Migrate debugger / disassembler
- [ ] Migrate static code analyzer
- [ ] Migrate emulator execution
- [ ] Remove obsolete decoding logic

