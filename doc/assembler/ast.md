# Abstract Syntax Tree

## Purpose

This document defines the Abstract Syntax Tree (AST) used internally by the CHIP-8 assembler.

The AST is the output of the parser framework and the input to semantic analysis. The parser is invoked only after the effective target architecture has been selected.

It represents the syntactic structure of a CHIP-8 assembly program while remaining independent of machine code generation.

The AST intentionally preserves the structure of the source program without performing semantic evaluation.

---

# Design Goals

The AST has the following objectives.

- Represent every syntactically valid program.
- Be independent of the parser implementation.
- Be independent of code generation.
- Preserve complete source location information.
- Be easy to traverse.
- Be easily extensible for future architectures.
- Support detailed diagnostics.

---

# Position in the Compilation Pipeline

```
Assembly Source
     │
     ▼
Target Discovery
     │
     ▼
Effective Target
     │
     ▼
Lexer / Parser Framework
     │
     ▼
Abstract Syntax Tree
     │
     ▼
Semantic Analysis
     │
     ▼
Code Generation
```

The AST forms the interface between parsing and semantic analysis.

---

# General Principles

The AST stores syntax only.

It does **not** contain

- resolved labels,
- instruction encodings,
- generated addresses,
- symbol values,
- evaluated expressions.

Those belong to later compilation stages.

---

# Root Node

Every source file produces exactly one root node.

```
Program
```

The Program node owns every statement in source order.

```
Program
 ├── Statement
 ├── Statement
 ├── Statement
 └── ...
```

---

# Statement Nodes

Every source line containing a statement produces one statement node.

Possible statement types include

```
Instruction

Architecture-specific Directive

Label

Empty Statement
```

The architecture-independent `TARGET` declaration is handled during target discovery and is not represented as a normal architecture-specific directive node in the AST.

Future versions may introduce

```
Macro Definition

Conditional Assembly

Include Statement
```

---

# Label Node

Represents a label declaration.

Example

```asm
Loop:
```

AST

```
Label
    name = "Loop"
```

The Label node contains only the identifier.

Its address is assigned during semantic analysis.

---

# Instruction Node

Represents one instruction.

Example

```asm
ADD V0, 1
```

AST

```
Instruction
    mnemonic = ADD

    operands
        Register(V0)
        Constant(1)
```

The Instruction node stores only the parsed syntax.

It does not know its opcode.

---

# Directive Node

Represents assembler directives.

Examples

```asm
ORG 200

DB 1,2,3

DW 0x1234

TARGET COSMAC
```

Each directive owns its parsed operands.

Directive semantics are evaluated later.

---

# Operand Nodes

Operands are represented by dedicated node types.

Typical operand nodes include

```
RegisterOperand

ImmediateOperand

AddressOperand

IdentifierOperand

IndexedOperand

SpecialRegisterOperand
```

Using separate node types simplifies semantic analysis and diagnostics.

---

# Expression Nodes

Expressions are stored as trees.

Example

```asm
Table+4
```

AST

```
BinaryExpression(+)

    Identifier(Table)

    Constant(4)
```

Evaluation is deferred until semantic analysis.

---

# Literal Nodes

Literal values are represented explicitly.

Examples

```
IntegerLiteral

CharacterLiteral

StringLiteral
```

The parser stores the literal exactly as written.

Conversion to binary occurs later.

---

# Source Locations

Every node records

- filename,
- line,
- column.

Example

```
Instruction

    line = 42

    column = 5
```

Source locations remain attached throughout the compilation pipeline.

---

# Parent/Child Relationships

The AST forms a tree.

```
Program
    │
    ├── Statement
    │       │
    │       ├── Operand
    │       └── Operand
    │
    ├── Statement
    │
    └── ...
```

Child ordering always matches the original source.

---

# Ownership

Every node owns its children.

Nodes never have multiple parents.

This guarantees that the AST remains a true tree.

---

# Mutability

The parser constructs the AST.

Subsequent compilation stages should avoid modifying its structure.

Semantic analysis should attach additional information separately rather than rewriting AST nodes.

This keeps parsing and semantic analysis clearly separated.

---

# Error Nodes

The parser may optionally insert dedicated error nodes.

Example

```
Program

    ├── Instruction

    ├── ErrorNode

    └── Instruction
```

This allows parsing to continue after syntax errors while preserving source structure.

---

# Visitor Pattern

Compilation stages should traverse the AST using visitors.

Typical visitors include

```
Semantic Analyzer

Code Generator

Listing Generator

Pretty Printer

AST Dumper
```

Each visitor performs one well-defined task.

---

# AST Example

Source

```asm
Loop:

    LD V0, 10

    ADD V0, 1

    JP Loop
```

AST

```
Program

 ├── Label
 │      name = Loop
 │
 ├── Instruction
 │      mnemonic = LD
 │      operands
 │          Register(V0)
 │          Constant(10)
 │
 ├── Instruction
 │      mnemonic = ADD
 │      operands
 │          Register(V0)
 │          Constant(1)
 │
 └── Instruction
        mnemonic = JP
        operands
            Identifier(Loop)
```

Notice that the label reference remains an identifier.

It has not yet been resolved to an address.

---

# Interaction with Semantic Analysis

Semantic analysis traverses the AST to

- build the symbol table,
- resolve identifiers,
- evaluate expressions,
- verify operand ranges,
- calculate addresses.

The AST itself remains unchanged.

---

# Interaction with Code Generation

Code generation traverses the analyzed AST.

It converts instructions into machine code while using information produced by semantic analysis.

The code generator never performs parsing.

---

# Summary

The AST is the central intermediate representation of the assembler.

It completely represents the syntactic structure of the source program while remaining independent of semantic analysis and machine code generation.

Its stability and clear structure allow the parser, semantic analyzer and code generator to evolve independently while sharing a common representation of the source program.
