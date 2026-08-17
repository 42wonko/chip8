# Semantic Analysis

## Purpose

This document describes the semantic analysis phase of the CHIP-8 assembler.

Semantic analysis validates the meaning of a syntactically correct program before machine code generation begins.

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

Forward references are fully supported.

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

requires word-sized values.
```

The `TARGET` declaration is not semantically validated here. Target discovery has already determined the effective architecture before parsing begins. Unknown or conflicting target declarations are reported by the target-discovery phase.

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

Every diagnostic contains

- filename,
- line,
- column,
- diagnostic category,
- descriptive message.

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
- include files,
- expression functions.

These features should integrate into the existing semantic analysis pipeline without changing the parser.

---

# Summary

Semantic analysis transforms a syntactically correct AST into a semantically complete representation of the program.

It resolves symbols, evaluates expressions, assigns addresses, validates operand values and prepares the program for machine code generation while remaining completely independent of parsing and opcode encoding.
