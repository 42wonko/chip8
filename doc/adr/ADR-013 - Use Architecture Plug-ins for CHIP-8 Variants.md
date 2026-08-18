# ADR-013 — Use Architecture Plug-ins for CHIP-8 Variants

**Author:** Michael Dlubatz

**Date:** 2026-08-04

**Status:** Proposed

---

# Context

The assembler is intended to support multiple members of the CHIP-8 family.

Initially, only the original COSMAC CHIP-8 architecture will be implemented. Future extensions are expected to include architectures such as

- SUPER-CHIP
- XO-CHIP
- MegaChip

Although these architectures share a common heritage, they are not simply different code generation targets.

Each architecture defines its own assembly language through variations in

- instruction set,
- directives,
- reserved keywords,
- operand forms,
- grammar,
- lexical rules.

Consequently, the selected target architecture determines which language is accepted by the assembler.

Supporting multiple architectures by embedding conditional logic throughout the parser and code generator would increase complexity and make future extensions difficult to maintain.

---

# Decision

Each supported architecture shall be implemented as an independent architecture module.

An architecture module shall define

- the supported instruction set,
- assembler directives,
- reserved keywords,
- grammar definition,
- operand patterns,
- instruction encoding rules,
- architecture-specific limits and constraints.

The parser framework shall remain completely architecture independent.

The target architecture shall be determined before the architecture-specific
parser is selected.

Assembly source may contain a `TARGET` directive. Because the architecture
must already be known before the architecture-specific grammar can be used,
the assembler first performs architecture-independent target discovery.

If a `TARGET` directive is present, the architecture specified by that
directive becomes the effective target.

If no `TARGET` directive is present, the assembler uses a target architecture
supplied externally by the caller.

A source-specified target takes precedence over an externally supplied target.
If neither is available, assembly cannot proceed.

Target discovery does not parse instructions, operands, labels, expressions,
or other architecture-specific constructs. Its sole responsibility is to
determine the target architecture.

After the effective target has been determined, the corresponding
architecture module provides its language definition to the parser framework.

The parser shall recognize only the language defined by the active
architecture.

Instructions or directives not defined by that architecture shall be
reported as syntax errors.

The overall architecture is therefore:

```text
                    Assembly Source
                           │
                           ▼
                 +-------------------+
                 | Target Discovery  |
                 +---------+---------+
                           │
             +-------------+-------------+
             │                           │
       TARGET directive             No TARGET
             │                           │
             ▼                           ▼
       Target from source         External target
             │                           │
             +-------------+-------------+
                           │
                           ▼
                  Effective Target
                           │
                           ▼
                +-----------------------+
                | Architecture Module  |
                +-----------+-----------+
                            │
          Grammar, Instruction Set,
      Directives, Encoding Rules, Limits
                            │
                            ▼
                 +----------------------+
                 |   Parser Framework   |
                 +----------+-----------+
                            │
                            ▼
                           AST
                            │
                            ▼
                    Code Generator
```

Future architectures shall be introduced by adding new architecture modules
rather than modifying the parser framework.

---

# Rationale

The parser framework should implement parsing, not language definition.

The language itself is defined by the selected target architecture.

Target discovery is deliberately separate from both the architecture module
and the parser framework. This makes it possible to support source files
without a target declaration while still allowing source-authored programs
to identify their own architecture.

This approach follows the Open/Closed Principle.

The parser framework remains closed for modification while remaining open for extension through new architecture modules.

Supporting a new CHIP-8 variant therefore becomes an additive process instead of requiring modifications throughout the parser.

---

# Consequences

## Positive

- Clear separation between parser infrastructure and language definitions.
- Parser framework remains architecture independent.
- New architectures can be added without modifying existing parser code.
- Architecture-specific behaviour is isolated in one location.
- Syntax errors are detected using the active language definition.
- Source files may identify their own target architecture.
- External callers can supply a target for source files without a target
  declaration.
- Simplifies long-term maintenance as additional CHIP-8 variants are supported.

## Negative

- Every architecture requires its own module.
- Common functionality must be identified and shared through base classes or reusable components.
- Care must be taken to avoid unnecessary duplication between architecture modules.

---

# Alternatives Considered

## One parser supporting every instruction

Implement a parser that accepts the union of all CHIP-8 instructions and rejects unsupported instructions during semantic analysis.

Rejected.

This approach accepts programs that are not valid in the selected language.

For example,

```asm
PLANE 1
```

would successfully parse when assembling for the original COSMAC architecture.

Since `PLANE` is not part of the COSMAC language, this should be reported as a syntax error during parsing rather than as a semantic error during later processing.

---

## Independent parser implementation for every architecture

Implement a separate parser for every supported CHIP-8 variant.

Rejected.

Most parsing behaviour is common to all architectures.

Duplicating parser implementations would significantly increase maintenance effort and risk inconsistent behaviour.

A shared parser framework with pluggable architecture definitions provides the same flexibility while maximizing code reuse.

---

# Future Evolution

Initially, the assembler will provide a single architecture module implementing the original COSMAC CHIP-8 instruction set.

As additional architectures are implemented, they should inherit common functionality where appropriate while extending or overriding only those language elements that differ from their predecessors.

This approach supports the natural evolution of the CHIP-8 family while preserving a consistent parser framework.

---

# Related ADRs

- ADR-009 — Integrate the Assembler into the Emulator Architecture
- ADR-010 — Use a Parser Framework Driven by Architecture Definitions
- ADR-011 — Use a Two-Pass Assembly Process
- ADR-012 — Represent Source Code as an Abstract Syntax Tree
