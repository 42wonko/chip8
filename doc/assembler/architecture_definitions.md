# Architecture Definitions

## Purpose

This document defines the architecture definition model used by the CHIP-8 assembler.

An architecture definition describes an entire assembly language.

The parser framework does not contain knowledge of individual CHIP-8 architectures. Instead, it obtains all language-specific information from the architecture definition selected after target discovery.

The architecture definition and parser framework work together to produce the Abstract Syntax Tree (AST), but the architecture must be selected before the parser can be used.

---

# Design Goals

The architecture definition model has the following objectives.

- Completely describe a CHIP-8 assembly language.
- Remain independent of parser implementation.
- Allow future architectures to be added without modifying the parser framework.
- Promote reuse between related architectures.
- Provide a single authoritative source for language rules.
- Clearly separate syntax from code generation.

---

# Overall Architecture

```
                 Source File
                      │
                      ▼
                    Lexer
                      │
                      ▼
                Token Stream
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
 Parser Framework        Architecture Definition
        │                           │
        └─────────────┬─────────────┘
                      ▼
                      AST
```

The parser framework performs the parsing.

The architecture definition specifies the language being parsed.

---

# Responsibilities

An architecture definition specifies

- instruction set
- assembler directives
- reserved words
- operand forms
- expression grammar
- special registers
- lexical extensions
- language version

An architecture definition does **not**

- generate machine code,
- evaluate expressions,
- resolve labels,
- perform semantic analysis,
- emit diagnostics.

---

# Language Definition

Each supported architecture defines a complete language.

Examples include

- COSMAC CHIP-8
- SUPER-CHIP
- XO-CHIP
- MegaChip

Each language consists of

- lexical elements,
- grammar,
- instruction set,
- directives,
- reserved identifiers.

The parser accepts only constructs belonging to the currently selected language.

---

# Architecture Selection

The target architecture is selected before the architecture-specific parser is invoked.

There are two sources for the target:

- a `TARGET` directive in the source, or
- an externally supplied target, such as the target selected by the assembler GUI.

A source target takes precedence over the external target. If the source contains no target directive, the external target is used. If neither is available, assembly cannot proceed.

The assembler therefore performs an architecture-independent target-discovery step before selecting the architecture definition. Target discovery recognizes only the target declaration; it does not parse the remainder of the assembly language.

Example:

```asm
TARGET COSMAC

PLANE 1
```

Target discovery selects COSMAC. The COSMAC architecture definition is then supplied to the parser framework, and `PLANE` produces a syntax error because it is not part of the COSMAC language.

---

# Instruction Definitions

Every instruction definition specifies

- mnemonic
- operand count
- operand types
- operand ordering
- optional syntax variants

Example (conceptual)

```
Mnemonic

    LD

Forms

    LD Vx, Byte

    LD Vx, Vy

    LD I, Address

    LD DT, Vx

    LD ST, Vx

    LD F, Vx

    LD B, Vx

    LD [I], Vx

    LD Vx, [I]
```

Each instruction form is treated as an independent grammar production.

---

# Operand Types

The architecture definition classifies operands into semantic categories.

Examples include

```
Register

Address

Immediate Byte

Immediate Nibble

Expression

Label

Indexed Register

Special Register

Special Destination
```

Instruction definitions reference these operand categories instead of individual tokens.

---

# Reserved Words

Each architecture defines its own reserved words.

Typical reserved words include

- mnemonics,
- directives,
- register names,
- predefined symbols.

Reserved words cannot be used as identifiers.

---

# Directives

The architecture definition specifies every supported assembler directive.

For the COSMAC language these include

```
TARGET

ORG

DB

DW

EQU
```

Future architectures may introduce additional directives.

---

# Expression Grammar

The architecture definition specifies

- supported operators,
- precedence,
- associativity,
- literal forms.

Future architectures may extend the expression language without affecting the parser framework.

---

# Lexical Extensions

Architectures may introduce additional lexical constructs.

Examples might include

- new keywords,
- additional literals,
- new operand syntax.

These extensions remain local to the architecture.

---

# Inheritance

Many CHIP-8 architectures extend previous architectures rather than replacing them.

The implementation should therefore encourage reuse.

Conceptually

```
COSMAC
    │
    ▼
SUPER-CHIP
    │
    ▼
XO-CHIP
    │
    ▼
MegaChip
```

Derived architectures inherit the language definition of their parent architecture and extend or modify it where necessary.

Typical extensions include

- new instructions,
- additional directives,
- new operand forms,
- modified instruction semantics.

The parser framework is unaffected by these extensions.

---

# Versioning

Each architecture definition should contain version information.

Examples

```
COSMAC CHIP-8

SUPER-CHIP 1.0

XO-CHIP

MegaChip
```

This information may be used by diagnostics, listings, or future IDE functionality.

---

# Future Architectures

Adding support for a new CHIP-8 architecture should normally require

1. creating a new architecture definition,
2. registering the architecture,
3. implementing the corresponding code generator.

No parser modifications should be required unless the language introduces genuinely new grammatical constructs.

---

# Relationship to Semantic Analysis

The architecture definition specifies

- which statements are syntactically valid,
- which operand forms exist,
- which directives are legal.

Semantic analysis determines

- symbol values,
- expression evaluation,
- duplicate symbols,
- undefined labels,
- range checking.

The architecture definition therefore defines the language, while semantic analysis validates programs written in that language.

---

# Relationship to Code Generation

The architecture definition specifies the syntax of instructions.

The code generator specifies how those instructions are encoded.

Keeping these responsibilities separate allows the parser to remain independent of the binary encoding process.

---

# Summary

Architecture definitions describe complete CHIP-8 assembly languages.

They provide all language-specific information required by the parser framework while remaining independent of parsing, semantic analysis, and code generation.

This separation allows new architectures to be added by extending the language definition rather than modifying the parser itself.
