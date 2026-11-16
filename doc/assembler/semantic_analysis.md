# Semantic Analysis

## Purpose

This document describes the semantic analysis phase of the CHIP-8 assembler.

Semantic analysis validates the meaning of a syntactically correct program before machine code generation begins.

## Current Implementation Status

This document describes the intended semantic-analysis responsibilities. The current implementation differs from that design in several explicitly tracked areas:

- The implemented semantic pipeline is built around `SymbolCollector`, `ExpressionEvaluator`, `InstructionResolver`, and the code generator.
- Forward label references are supported because labels are collected before instruction resolution.
- Forward `EQU` references are not currently supported: an `EQU` expression must resolve using symbols already defined when that `EQU` is processed.
- `ORG`, `DB`, `DW`, and `EQU` are implemented. `DW` operands are validated after symbol collection so they can refer to forward labels; each value must be in the range `0x0000` through `0xFFFF`.
- Target discovery and validation are performed by `TargetSelector` in the Controller before the assembler is invoked. The complete expanded source may contain at most one `TARGET` declaration; a second declaration is an error even if it names the same target.
- INCLUDE expansion is performed by Controller-side preprocessing before target discovery and is independent of the selected architecture.
- `SourceLocation` contains the expanded-source line and column and optional original filename and physical line. The Controller's include processor also supplies a per-expanded-line `SourceOrigin` mapping used during target discovery and listing generation.
- The current implementation performs address accounting and semantic validation before code generation; code generation remains responsible for emitting bytes.

These notes identify implementation status and do not redefine the intended language or future architecture.

Its primary responsibilities are

- symbol table construction,
- label resolution,
- expression evaluation,
- operand validation,
- address assignment,
- semantic diagnostics.

Semantic analysis operates exclusively on the Abstract Syntax Tree (AST).

---

# Design Goals

The semantic analyzer shall

- be completely independent of parsing,
- be completely independent of machine code generation,
- perform all semantic validation,
- preserve source location information,
- generate precise diagnostics,
- support forward references,
- support future language extensions.

---

# Position in the Compilation Pipeline

```
            Parser
               │
               ▼
              AST
               │
               ▼
      Semantic Analysis
               │
               ▼
      Annotated AST / Symbol Table
               │
               ▼
        Code Generation
```

The semantic analyzer never performs parsing and never emits machine code. Target selection has already been completed before semantic analysis begins.

---

# Responsibilities

Semantic analysis is responsible for

- constructing the symbol table,
- assigning addresses,
- resolving forward references,
- evaluating expressions,
- validating operand ranges,
- validating architecture-specific directive arguments,
- detecting duplicate symbols,
- detecting undefined symbols,
- producing semantic diagnostics.

It is **not** responsible for

- parsing,
- opcode encoding,
- binary output,
- optimization.

---

# Symbol Table

The symbol table contains every symbol defined during assembly.

Examples include

- labels,
- EQU symbols,
- predefined symbols,
- future macro names.

Each symbol contains

- name,
- value,
- symbol kind,
- source location.

---

# Symbol Definition

Labels become symbols.

Example

```asm
Loop:
```

creates

```
Loop

    address = current program counter
```

---

# EQU Symbols

Example

```asm
ScreenWidth: EQU 64
```

creates

```
ScreenWidth

    value = 64
```

Unlike labels, EQU symbols are constants.

---

# Address Assignment

Semantic analysis assigns an address to every instruction and data object.

The program counter is updated according to

- instruction size,
- DB,
- DW,
- ORG,
- future directives.

Addresses are assigned before code generation begins.

---

# Forward References

Forward label references are supported. Forward references to `EQU` symbols are not currently supported.

Example

```asm
JP Loop

...

Loop:
```

The parser records the identifier.

Semantic analysis resolves it using the completed symbol table.

---

# Expression Evaluation

Expressions are evaluated after symbol resolution.

Example

```asm
ORG Table + 16
```

Evaluation may require

- constants,
- labels,
- arithmetic operators.

Evaluation always produces an integer value.

---

# Operand Validation

The semantic analyzer validates operand values.

Examples include

```
Nibble

0..15

Byte

0..255

Address

0..4095
```

The parser does not perform these checks.

---

# Directive Validation

Architecture-specific directive arguments are validated semantically.

Examples

```
ORG

requires an address expression.

DB

requires byte-sized values.

DW

requires a label and at least one numeric expression. Each expression must resolve to an unsigned 16-bit value (`0x0000` through `0xFFFF`). Each value occupies two bytes in big-endian order, so address assignment advances by two bytes per operand. DW values are checked after symbol collection to permit forward label references.
```

The `TARGET` declaration is not semantically validated here. Target discovery has already determined the effective architecture before parsing begins. Unknown target names and multiple TARGET declarations are reported by the target-discovery phase. The single-declaration rule applies to the complete expanded source, including all included files.

---

# Duplicate Symbols

Example

```asm
Loop:

...

Loop:
```

Produces

```
Duplicate symbol

Loop
```

The first definition remains available for diagnostics.

---

# Undefined Symbols

Example

```asm
JP MissingLabel
```

Produces

```
Undefined symbol

MissingLabel
```

---

# Constant Evaluation

Character literals

```asm
'A'
```

become

```
65
```

Binary

```asm
0b1010
```

becomes

```
10
```

Hexadecimal

```asm
0x20
```

becomes

```
32
```

---

# Data Expansion

Semantic analysis expands data directives into semantic objects.

Example

```asm
DB "ABC"
```

becomes

```
41 42 43
```

The code generator later emits these bytes.

---

# Semantic Diagnostics

Typical diagnostics include

- duplicate labels,
- undefined labels,
- value out of range,
- integer overflow,
- invalid expression,
- invalid directive argument,
- invalid operand value.

Every assembler diagnostic contains a source location with expanded-source line and column, plus its severity, source/category information, and descriptive message. When INCLUDE preprocessing supplied provenance, the location also carries the original filename and physical line. This allows diagnostics from nested included files to identify their actual source while preserving expanded-source coordinates for downstream processing.

---

# Interaction with Code Generation

After successful semantic analysis

- every symbol has a value,
- every expression has been evaluated,
- every address has been assigned,
- every operand has been validated.

The code generator therefore performs only encoding.

---

# Future Extensions

The semantic analysis framework should be designed to accommodate future language features, including

- macros,
- local labels,
- namespaces,
- conditional assembly,
- expression functions.

These features should integrate into the existing semantic analysis pipeline without changing the parser.

---

# Summary

Semantic analysis transforms a syntactically correct AST into a semantically complete representation of the program.

It resolves symbols, evaluates expressions, assigns addresses, validates operand values and prepares the program for machine code generation while remaining completely independent of parsing and opcode encoding.
