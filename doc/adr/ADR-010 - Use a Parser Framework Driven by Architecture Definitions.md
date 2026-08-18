# ADR-010 — Use a Parser Framework Driven by Architecture Definitions

**Author:** Michael Dlubatz

**Date:** 2026-08-04

**Status:** Proposed

---

# Context

The assembler is intended to support multiple members of the CHIP-8 family, including the original COSMAC CHIP-8 architecture and future extensions such as SUPER-CHIP, XO-CHIP and MegaChip.

Although these architectures share a common ancestry, they are not identical languages.

Each architecture defines its own

- instruction set,
- directives,
- reserved keywords,
- operand formats,
- expression rules,
- grammar.

For example, instructions such as `PLANE` exist in XO-CHIP but are not part of the original COSMAC CHIP-8 language.

Because an assembler directly represents the programming language of a specific processor architecture, language features that are not defined by the selected target architecture are not part of the language.

Consequently, they should be rejected during parsing rather than during later semantic analysis.

The parser should therefore not contain architecture-specific logic or large conditional statements for every supported target.

---

# Decision

The assembler shall be implemented as a generic parser framework driven entirely by an architecture definition.

Each supported architecture shall provide its own grammar definition describing

- reserved words,
- mnemonics,
- directives,
- operand patterns,
- lexical rules,
- grammar productions.

The parser framework shall remain architecture independent.

The target architecture must be determined before the architecture-specific
assembly language can be parsed.

Assembly source may contain a `TARGET` directive. Because the architecture
must already be known before the architecture-specific parser can be selected,
the assembler performs a small architecture-independent target-discovery
operation before normal parsing.

If a `TARGET` directive is present, the architecture specified by that
directive becomes the effective target.

If no `TARGET` directive is present, the assembler uses a target architecture
supplied externally by the caller.

A source-specified target takes precedence over an externally supplied target.
If neither is available, assembly cannot proceed.

Target discovery does not parse the assembly language. It only determines
whether a target declaration is present and, if so, which architecture it
specifies.

After the effective target has been determined, the corresponding
architecture definition supplies its grammar to the parser framework.

The parser then recognizes only the language defined by that grammar.

Tokens or productions that are not defined by the active grammar are treated
as syntax errors.

The parser framework therefore produces an Abstract Syntax Tree (AST) only
after the target architecture and its grammar have been selected.

```
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
              Architecture Definition
                           │
                           ▼
                 Parser Framework
                           │
                           ▼
                          AST
```

---

# Rationale

This architecture cleanly separates the parser implementation from the definition of individual assembly languages.

Adding support for a new architecture requires providing a new grammar definition rather than modifying the parser implementation.

The parser remains reusable, while the supported language is determined
entirely by the selected architecture.

The explicit target-discovery stage also prevents the parser from having to
guess which architecture a source program belongs to. For source files
without a target declaration, the caller is responsible for supplying the
target architecture.

This approach also reflects the nature of assembly language.

Unlike high-level languages, an assembler is defined by its target architecture.

Selecting a target architecture therefore determines the language that is accepted by the parser.

Instructions that do not belong to that language are syntax errors.

---

# Consequences

## Positive

- Parser implementation is independent of any particular architecture.
- New architectures can be added without modifying parser logic.
- Architecture-specific conditional code is minimized.
- Syntax errors are detected immediately during parsing.
- Grammar definitions become explicit project artifacts.
- The parser remains reusable for all supported CHIP-8 architectures.

## Negative

- Every supported architecture requires its own grammar definition.
- Grammar definitions must be maintained alongside opcode definitions.
- Target discovery must remain independent of the architecture-specific
  grammar.
- Callers assembling source without a `TARGET` directive must supply an
  external target architecture.

---

# Alternatives Considered

## Single grammar with semantic validation

Implement one parser that recognizes the union of all CHIP-8 variants and rejects unsupported instructions during semantic analysis.

Rejected.

This approach accepts programs that are not valid for the selected target language.

For example, the statement

```
PLANE 1
```

would successfully parse when assembling for the original COSMAC architecture and would only be rejected later during semantic analysis.

Since `PLANE` is not part of the COSMAC CHIP-8 language, this is considered a syntax error rather than a semantic error.

---

## Separate parser implementation for every architecture

Implement a completely independent parser for every CHIP-8 variant.

Rejected.

Although possible, this would duplicate the majority of parser logic and increase maintenance effort.

The parser implementation should be shared while the language definition is supplied by the selected architecture.

---

# Related ADRs

- ADR-009 — Integrate the Assembler into the Emulator Architecture
- ADR-011 — Use a Two-Pass Assembly Process
- ADR-012 — Represent Source Code as an Abstract Syntax Tree
- ADR-013 — Use Architecture Plug-ins for CHIP-8 Variants
