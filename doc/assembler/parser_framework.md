# Parser Framework

## Purpose

This document describes the parser framework used by the CHIP-8 assembler.

Unlike traditional assemblers, which hard-code the complete assembly language into a single parser, this project separates the parser implementation from the language definition.

The parser framework is responsible only for parsing according to the grammar definition of an already selected architecture.

The architecture definition specifies the language. Target discovery must select the architecture before the parser framework is invoked.

Together, the selected architecture definition and the parser framework produce the Abstract Syntax Tree (AST).

---

# Design Goals

The parser framework has the following objectives.

- Completely independent of any CHIP-8 architecture.
- Driven entirely by grammar definitions.
- Produce a common AST for all architectures.
- Generate precise diagnostics.
- Be easily extensible.
- Support future architectures without modifying the framework.
- Remain suitable for handwritten recursive-descent parsing.

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
            ┌────────────┴────────────┐
            │                         │
            ▼                         ▼
   Architecture Definition     Parser Framework
            │                         │
            └────────────┬────────────┘
                         ▼
                         AST
```

The parser framework never contains architecture-specific knowledge.

All language rules originate from the architecture definition.

---

# Responsibilities

The parser framework is responsible for

- consuming the token stream,
- validating the syntax against the selected architecture,
- selecting grammar productions,
- constructing AST nodes,
- preserving source locations,
- reporting syntax errors.

It is **not** responsible for

- opcode generation,
- symbol resolution,
- expression evaluation,
- architecture validation beyond the supplied grammar,
- binary output.

---

# Architecture Definition

An architecture definition provides the parser with all information required to recognize a language. It is selected before the parser is initialized.

Typical information includes

- instruction mnemonics,
- directives,
- reserved words,
- operand forms,
- special registers,
- expression grammar,
- lexical extensions.

The parser itself does not know the meaning of any instruction.

---

# Parsing Process

The parser operates in a sequence of well-defined stages.

```
Token Stream
      │
      ▼
Statement Parser
      │
      ▼
Instruction / Directive Parser
      │
      ▼
Operand Parser
      │
      ▼
Expression Parser
      │
      ▼
AST
```

Each stage has a single responsibility.

---

# Parser Components

## Statement Parser

Parses one source line.

Recognizes

- labels,
- instructions,
- directives,
- empty lines.

---

## Instruction Parser

Recognizes instruction mnemonics.

The parser consults the architecture definition to determine

- whether the mnemonic exists,
- expected operand count,
- operand kinds.

---

## Directive Parser

Recognizes assembler directives.

Supported directives are supplied by the active architecture.

Unknown directives result in syntax errors.

---

## Operand Parser

Parses operands independently of any instruction.

Recognized operand categories include

- register operands,
- special registers,
- immediate expressions,
- address expressions,
- indexed operands.

The instruction definition determines which operand kinds are valid.

---

## Expression Parser

Responsible only for parsing expressions.

Evaluation is deferred until semantic analysis.

This allows

- forward references,
- symbolic constants,
- label arithmetic.

---

# Abstract Syntax Tree Construction

The parser constructs a complete AST.

Example

```asm
Loop:
    ADD V0, 1
```

becomes

```
Program
 └── Label
      └── Instruction
            ├── Mnemonic(ADD)
            ├── Register(V0)
            └── Constant(1)
```

The parser never generates machine code.

---

# Error Recovery

Whenever possible, the parser continues after encountering a syntax error.

Recovery typically skips tokens until the next source line.

This allows multiple syntax errors to be reported during a single assembly.

---

# Source Locations

Every AST node records

- filename,
- line,
- column.

These source locations are preserved throughout the remaining compilation stages.

This enables precise diagnostics.

---

# Parser Diagnostics

The parser reports only syntax errors.

Examples include

```
Unknown instruction

Unexpected operand

Unexpected comma

Missing operand

Unexpected end of line

Expected register

Expected expression
```

The parser never reports

- undefined labels,
- duplicate labels,
- range violations,
- address overflows.

These belong to semantic analysis.

---

# Parser Interface

The parser framework exposes a simple interface.

```
Token Stream
        │
        ▼
Parser.parse()
        │
        ▼
AST
```

Errors are reported through the diagnostics subsystem.

The parser never writes directly to the console.

---

# Interaction with the Architecture Definition

The parser frequently queries the architecture definition.

Typical queries include

- Is this a valid mnemonic?
- Is this a directive?
- How many operands are required?
- Which operand kinds are accepted?
- Is this keyword reserved?
- Which grammar rule applies?

The parser framework remains completely generic.

---

# Future Extensions

The framework is designed to support future language features without architectural changes.

Examples include

- macros,
- conditional assembly,
- include files,
- local labels,
- repeat directives,
- user-defined data types.

Such features should be introduced by extending the grammar definitions rather than modifying the parser core whenever possible.

---

# Summary

The parser framework is intentionally architecture-independent.

Its only task is to transform a stream of tokens into an Abstract Syntax Tree according to the architecture definition selected by the target-discovery phase.

The parser framework contains no knowledge of CHIP-8 instructions, directives, or opcode encodings.

Those language-specific details are supplied entirely by the architecture definition.
