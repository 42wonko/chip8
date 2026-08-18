# ADR-012 — Represent Source Code as an Abstract Syntax Tree

**Author:** Michael Dlubatz

**Date:** 2026-08-04

**Status:** Proposed

---

# Context

The assembler consists of several distinct processing phases:

- Lexical analysis
- Parsing
- Symbol collection
- Expression evaluation
- Code generation

Each phase requires access to the structure of the source program but has different responsibilities.

Without a common intermediate representation, every phase would need to parse or interpret the source independently, resulting in duplicated logic and tight coupling between parser and code generator.

Furthermore, future project goals include integration into the existing CHIP-8 emulator and debugger. This opens the possibility of future features such as

- source-level debugging,
- source navigation,
- code analysis,
- syntax highlighting,
- refactoring tools,
- symbol browsers,
- cross-reference generation.

These features require a structured representation of the source program that is independent of machine code generation.

---

# Decision

The parser shall produce an Abstract Syntax Tree (AST) representing the complete source program.

The AST shall become the primary intermediate representation used by all subsequent phases of the assembler.

The parser shall have no knowledge of symbol resolution or code generation.

Likewise, later phases shall operate exclusively on the AST and shall not perform any parsing.

The overall processing pipeline becomes:

```text
             Source Code
                  │
                  ▼
              Tokenizer
                  │
                  ▼
                Parser
                  │
                  ▼
                  AST
        ┌─────────┼─────────┐
        ▼         ▼         ▼
    Pass 1   Static Analysis  ...
        │
        ▼
   Symbol Table
        │
        ▼
     Pass 2
        │
        ▼
   Machine Code
```

The AST shall remain immutable after parsing.

Subsequent processing stages may attach analysis information to auxiliary data structures but shall not modify the syntactic structure represented by the AST.

---

# Rationale

The AST forms a clean architectural boundary between syntax analysis and all later processing phases.

Each subsystem has a single responsibility:

- The tokenizer converts characters into tokens.
- The parser converts tokens into syntax.
- Pass 1 analyses the syntax and constructs the symbol table.
- Pass 2 translates the syntax into machine code.

This separation reduces coupling and makes each phase independently testable.

It also allows new processing stages to be introduced without modifying the parser.

---

# Consequences

## Positive

- Clean separation between parsing and code generation.
- No later phase depends on parser internals.
- Source code is parsed exactly once.
- AST can be reused by multiple processing stages.
- Simplifies unit testing of parser and code generator.
- Provides a foundation for future IDE and debugger functionality.
- Makes additional analysis passes easy to implement.

## Negative

- The AST must remain in memory throughout the assembly process.
- Additional implementation effort is required to define the AST node hierarchy.

---

# Alternatives Considered

## Generate machine code directly during parsing

Rejected.

This couples parsing with code generation and prevents reuse of the parsed program structure.

---

## Reparse the source for each processing stage

Rejected.

Parsing is comparatively expensive and would duplicate work while increasing implementation complexity.

---

## Use a linear intermediate instruction list

Instead of constructing a tree, the parser could emit a flat sequence of intermediate instructions.

Rejected.

Although sufficient for simple code generation, a linear representation loses important syntactic information and provides little support for future tooling such as source analysis or IDE integration.

The AST preserves the original program structure while remaining independent of code generation.

---

# Implications for Future Development

The AST is intended to become the central data structure shared by the assembler.

Future components such as

- source-level debugger,
- symbol browser,
- syntax checker,
- optimizer,
- code formatter,
- language server,

should consume the AST rather than reparsing the original source.

---

# Related ADRs

- ADR-009 — Integrate the Assembler into the Emulator Architecture
- ADR-010 — Use a Parser Framework Driven by Architecture Definitions
- ADR-011 — Use a Two-Pass Assembly Process
- ADR-013 — Use Architecture Plug-ins for CHIP-8 Variants
