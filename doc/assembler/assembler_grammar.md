# CHIP-8 Assembler Grammar

## Purpose

This document defines the formal grammar of the CHIP-8 assembly language.

The grammar serves as the language specification for the supported CHIP-8 architectures and forms the contract between the architecture definitions and the parser framework.

The architecture-specific grammar is used only after the target architecture has been selected. Target selection itself is handled by a small architecture-independent target-discovery phase.

The grammar intentionally describes the architecture-specific language independently of any parser implementation. The parser framework interprets the selected grammar definition and produces a common Abstract Syntax Tree (AST).

---

# Design Goals

The grammar has been designed to satisfy the following goals.

- Simple enough for hand-written recursive-descent parsers.
- Independent of parser implementation.
- Suitable for grammar-driven parser generation.
- Architecture-specific.
- Easy to extend for future CHIP-8 variants.
- Produces high-quality diagnostics.
- Supports forward references.
- Supports two-pass assembly.

---

# Overall Language Structure

A source file consists of a sequence of source lines.

```
Source File
    │
    ├── Source Line
    ├── Source Line
    ├── Source Line
    └── ...
```

Each source line may contain

- a label,
- an instruction,
- a directive,
- a comment,
- or any valid combination thereof.

---

# Lexical Elements

The lexer converts the character stream into a sequence of tokens.

Parsing operates exclusively on these tokens.

The lexer is responsible for

- source locations,
- comments,
- literals,
- identifiers,
- keywords,
- punctuation,
- whitespace handling.

---

# Character Set

The assembler accepts UTF-8 encoded source files.

Instruction mnemonics, directives and identifiers are restricted to the ASCII character set.

String literals may contain arbitrary UTF-8 characters.

---

# Whitespace

Whitespace is insignificant except where required to separate adjacent tokens.

The following characters are treated as whitespace.

- space
- horizontal tab

Whitespace never appears inside tokens.

---

# Newlines

Each physical source line terminates with a newline token.

Newlines delimit assembler statements and provide source locations for diagnostics.

---

# Comments

Comments begin with a semicolon.

Example

```asm
LD V0, 10      ; initialize counter
```

Everything following the semicolon until the end of the line is ignored.

Comments are discarded by the lexer.

---

# Identifiers

Identifiers are used for

- labels
- EQU symbols
- future macro names

Syntax

```
UppercaseLetter
    followed by

Letters
Digits
Underscore
```

Regular expression

```
[A-Z][A-Za-z0-9_]*
```

Examples

```
Loop
Sprite
DelayTimer
DrawSprite
Table1
Font_Data
```

---

# Reserved Words

Reserved words cannot be used as identifiers.

Reserved words include

- instruction mnemonics
- directives
- special registers
- future language keywords

The exact reserved-word list depends on the selected target architecture.

---

# Registers

General purpose registers

```
V0
V1
...
VF
```

Grammar

```
Register ::= V HexDigit
```

---

# Special Registers

The grammar recognizes the following predefined register names.

```
I
DT
ST
K
F
B
```

Their meaning depends on the instruction being assembled.

---

# Numeric Literals

The assembler supports three integer formats.

Decimal

```
123
```

Hexadecimal

```
0x7B
```

Binary

```
0b01111011
```

Bare hexadecimal values are not permitted.

---

# Character Literals

Examples

```asm
'A'
'0'
'\n'
'\\'
'\''
'\x41'
```

Character literals evaluate to an unsigned byte.

---

# String Literals

Examples

```asm
"Hello"
"CHIP-8"
```

Strings are primarily intended for the DB directive.

---

# Separators

```
,
:
[
]
(
)
```

---

# Program Grammar

```
Program

    ::= Line*

Line

    ::= [ Label ]
        [ Statement ]
        [ Comment ]
        NewLine
```

---

# Labels

```
Label

    ::= Identifier ":"
```

Examples

```asm
Loop:
Start:
DrawSprite:
```

---

# Statements

Exactly one statement may appear on a source line.

```
Statement

    ::= Instruction
     |  Directive
```

---

# Instructions

Instructions consist of

- mnemonic
- operand list

```
Instruction

    ::= Mnemonic
        [ OperandList ]
```

---

# Operand Lists

```
OperandList

    ::= Operand

     | Operand "," Operand

     | Operand "," Operand "," Operand
```

The parser validates the required operand count using the selected architecture definition.

---

# Operands

Operands are classified into semantic categories.

```
Operand

    ::= Register
     | SpecialRegister
     | AddressExpression
     | ImmediateExpression
     | IndexedOperand
```

---

# Indexed Operands

```
[I]
```

is currently the only indexed operand supported.

Future architectures may introduce additional indexed addressing modes.

---

# Expressions

Expressions are intentionally simple.

```
Expression

    ::= Primary
     | Primary "+" Primary
     | Primary "-" Primary
```

Primary

```
Primary

    ::= Number
     | Identifier
```

Expressions are evaluated during Pass 2.

---

# Directives

The COSMAC architecture defines the following architecture-specific directives.

```
ORG
DB
DW
EQU
```

Future architectures may introduce additional architecture-specific directives.

The parser recognizes only directives defined by the selected architecture.

---

# TARGET Directive

`TARGET` is a special, architecture-independent declaration used to select the target architecture before the architecture-specific parser is invoked.

Example

```asm
TARGET COSMAC
```

The target-discovery phase examines the source for this declaration. It does not parse the remainder of the assembly language.

If a target declaration is present, its architecture is used. If no target declaration is present, the externally supplied target is used. A source target takes precedence over the external target.

Only one target declaration may be present in a source file. Multiple target declarations are reported as a target-selection error during target discovery.

The selected target determines

- grammar,
- instruction set,
- architecture-specific directives,
- reserved words,
- operand forms, and
- encoding rules.

`TARGET` itself is not part of an architecture-specific grammar.

---

# Architecture-Specific Grammar

The parser framework itself does not define any instruction mnemonics.

Instead, every target architecture contributes its own language definition.

This language definition specifies

- instruction mnemonics
- operand patterns
- directives
- reserved words
- lexical extensions

The parser framework interprets this definition to perform syntax analysis.

---

# Syntax Validation

Only constructs defined by the selected target architecture are considered part of the language.

Example

```asm
TARGET COSMAC

PLANE 1
```

Target discovery first selects COSMAC. The COSMAC parser then reports a syntax error because `PLANE` is not part of the COSMAC language.

No AST node is generated for invalid statements.

---

# Semantic Validation

Semantic analysis begins only after successful parsing.

Typical semantic checks include

- duplicate labels
- undefined symbols
- value ranges
- expression evaluation
- address overflow

Semantic analysis never performs syntax checking.

---

# Summary

The grammar is intentionally architecture-dependent.

Rather than defining a single universal CHIP-8 language, each supported architecture contributes its own language definition.

The parser framework remains architecture-independent while enforcing the exact language specified by the selected target.
