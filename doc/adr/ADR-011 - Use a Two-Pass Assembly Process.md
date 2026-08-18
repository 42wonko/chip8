# ADR-011 — Use a Two-Pass Assembly Process

**Author:** Michael Dlubatz

**Date:** 2026-08-04

**Status:** Proposed

---

# Context

The assembler supports symbolic labels, forward references, constants, expressions and assembler directives such as `ORG`, `EQU`, `DB` and `DW`.

Source code may legitimately reference symbols before they are defined.

Example:

```asm
        JP      Main

Table:  DB      1,2,3

Main:   LD      V0, 0
```

At the time the first instruction is parsed, the address of `Main` is not yet known.

Similarly, expressions may reference constants that are defined later in the source file.

Attempting to generate machine code while parsing would therefore require deferred fix-ups or back-patching throughout the implementation.

As additional architectures are introduced, this complexity would continue to increase.

---

# Decision

The assembler shall be implemented as a classical two-pass assembler.

The parser shall execute once and construct a complete Abstract Syntax Tree (AST).

Subsequent processing shall operate exclusively on the AST.

The assembly process shall consist of the following phases:

```
Source File
     │
     ▼
Lexer
     │
     ▼
Parser
     │
     ▼
AST
     │
     ├───────────────┐
     ▼               │
Pass 1               │
(Symbol Collection)  │
     │               │
     ▼               │
Symbol Table         │
     │               │
     └──────┬────────┘
            ▼
         Pass 2
     (Code Generation)
            │
            ▼
       Machine Code
```

### Pass 1

The first pass traverses the AST and

- builds the symbol table,
- assigns addresses to labels,
- evaluates constant definitions where possible,
- processes assembler directives affecting program layout,
- determines instruction addresses.

No machine code is generated during this pass.

### Pass 2

The second pass traverses the AST again and

- resolves symbol references,
- evaluates expressions,
- validates operand ranges,
- generates machine code,
- reports unresolved symbols.

---

# Rationale

Separating symbol resolution from code generation significantly simplifies the implementation.

The parser remains responsible only for recognizing the language.

Pass 1 becomes responsible for constructing the symbol table.

Pass 2 becomes responsible for generating machine code.

Each phase has a single well-defined responsibility.

The resulting architecture is easier to understand, test and maintain than an implementation that attempts to generate code during parsing.

---

# Consequences

## Positive

- Naturally supports forward references.
- Clean separation between parsing, symbol resolution and code generation.
- No back-patching logic is required.
- Expressions can reference symbols defined later in the source file.
- Additional analysis phases can be inserted between Pass 1 and Pass 2 without modifying the parser.
- The AST becomes reusable by future tooling such as source-level debugging, static analysis and IDE features.

## Negative

- The complete AST must be retained until assembly has completed.
- Source files are traversed twice after parsing.
- Slightly higher memory usage than a single-pass assembler.

---

# Alternatives Considered

## Single-pass assembler

Generate machine code immediately while parsing.

Rejected.

A single-pass assembler requires complex back-patching or restrictions on forward references.

It also couples parsing and code generation, making both phases more difficult to maintain.

---

## Parser performs code generation

Allow the parser to emit machine code directly.

Rejected.

Parsing is a syntactic activity.

Generating machine code is a translation activity.

Combining both responsibilities violates the architectural separation adopted for this project.

---

## Multiple parsing passes

Reparse the source file during Pass 2.

Rejected.

The parser already produces a complete AST.

Reparsing the source file would duplicate work while providing no architectural benefit.

---

# Related ADRs

- ADR-009 — Integrate the Assembler into the Emulator Architecture
- ADR-010 — Use a Parser Framework Driven by Architecture Definitions
- ADR-012 — Represent Source Code as an Abstract Syntax Tree
- ADR-013 — Use Architecture Plug-ins for CHIP-8 Variants
