# ADR-004 — Use a Shared Instruction Decoder

**Author:** Michael Dlubatz

**Date:** 2026-07-01

**Status:** Accepted

---

## Title

Use a single instruction decoder for both instruction execution and
disassembly.

---

## Context

The emulator executes CHIP-8 instructions while also providing an
integrated disassembler for debugging.

Both subsystems interpret exactly the same 16-bit opcode.

Maintaining separate decoding logic for execution and disassembly would
duplicate functionality and introduce the risk of inconsistent behaviour
whenever the instruction set is modified.

The project therefore requires a solution that provides a single,
authoritative interpretation of every opcode.

---

## Alternatives Considered

### Option 1 — Independent Decoders

The execution engine and the disassembler each maintain their own
instruction decoder.

Advantages

- Independent implementations.
- Simple conceptual separation.

Disadvantages

- Duplicate decoding logic.
- Increased maintenance effort.
- Risk of inconsistent opcode interpretation.
- Changes must be implemented twice.

---

### Option 2 — Shared Decoder

A single decoder interprets an opcode.

Both the execution engine and the disassembler use the same decoding
logic.

Advantages

- One authoritative implementation.
- No duplicated opcode tables.
- Consistent execution and disassembly.
- Easier maintenance.
- Reduced testing effort.

Disadvantages

- Decoder becomes a shared dependency.
- Requires careful interface design.

---

## Decision

The emulator shall implement exactly one instruction decoder.

The decoder shall

- decode raw CHIP-8 opcodes,
- identify the instruction,
- extract instruction operands,
- provide decoded information for execution,
- provide decoded information for disassembly.

Neither the execution engine nor the disassembler shall implement
independent opcode decoding logic.

---

## Rationale

Instruction decoding is a single logical operation.

Duplicating this operation provides no architectural benefit while
significantly increasing maintenance effort.

A shared decoder guarantees that execution and disassembly always agree
on the meaning of an opcode.

This approach also simplifies verification because every opcode decoder
requires testing only once.

---

## Consequences

### Positive

- Single source of truth.
- No duplicated decoding logic.
- Consistent execution and disassembly.
- Easier maintenance.
- Reduced implementation effort.
- Simplified testing.

### Negative

- The decoder becomes a central component.
- Decoder interface must remain stable.

---

## References

- SRDS Chapter 4 — Emulator Core
- SRDS Chapter 6 — Debugger and Disassembler
- REQ-EMU-320
- REQ-EMU-321
- REQ-DBG-605
- REQ-DBG-606
