# CHIP-8 Assembler

## Overview

The CHIP-8 assembler is an integrated subsystem of the CHIP-8 Emulator project.

Unlike a standalone assembler, it is designed from the beginning to become part of the emulator, debugger, disassembler, and future integrated development environment (IDE). The assembler shares architectural concepts, coding conventions, diagnostics, and configuration management with the rest of the project.

The implementation follows the same design philosophy as the emulator:

- clean architecture
- explicit separation of responsibilities
- dependency injection
- comprehensive diagnostics
- extensive unit testing
- architecture-specific implementations where appropriate
- future extensibility without sacrificing readability

The assembler is intended to support multiple CHIP-8 architectures while presenting a consistent programming interface to the rest of the application.

## Current Implementation Status

The current implementation has one supported assembler target: `COSMAC`. Target selection is performed by `TargetSelector` in the Controller before the `Assembler` is created.

The lexer and parser are hand-written. `Parser` contains common grammar machinery, and `ClassicParser` specializes instruction-mnemonic recognition for the Classic target. The Controller selects the target and supplies the matching ISA/parser pair to `Assembler`.

The ISA abstraction is the authoritative source of assembler mnemonic knowledge through `assembler_mnemonics()`. The parser rejects unsupported mnemonics and recovers at statement boundaries to collect additional parser diagnostics. If parsing reports errors, semantic analysis and code generation are not run. Semantic analysis validates operand signatures, types, symbol references, expressions, and ranges. Lexical recovery remains future work; the first `LexerError` stops tokenization. No `ArchitectureDefinition` object is part of the accepted design.

---

# Documentation Structure

This directory contains the complete design documentation for the assembler subsystem.

| Document | Purpose |
|----------|---------|
| **README.md** | Overview of the assembler subsystem |
| **assembler_design.md** | Overall assembler architecture, processing pipeline, component responsibilities, and integration with the existing emulator |
| **assembler_grammar.md** | Complete lexical and syntactical definition of the assembler language |
| **parser_framework.md** | Shared parser base and architecture-specific parser hierarchy |
| **architecture_definitions.md** | Historical rejected proposal, superseded by ADR-014 |
| **ast.md** | Abstract Syntax Tree design |
| **semantic_analysis.md** | Symbol table construction, expression evaluation, and semantic analysis |
| **assembler_public_api.md** | Public interface between the assembler subsystem and the rest of the application |

The documents describe both the current implementation and proposed extensions. ADR-014 records the accepted parser direction. `architecture_definitions.md` is retained only as a historical, superseded proposal; it is not an implementation plan.

---

# Design Philosophy

The assembler is intentionally designed as a sequence of well-defined phases.

The effective assembler target must be known before the matching ISA and parser are constructed. `TargetSelector` performs target selection in the Controller before the `Assembler` is created.

```text
Source + External Target
          │
          ▼
Controller / TargetSelector
          │
          ▼
    Effective Target
          │
          ├───────────────┐
          ▼               ▼
   Matching ISA     Concrete Parser
          │          (Parser subclass)
          └───────┬───────┘
                  ▼
              Assembler
                  │
                  ▼
                Lexer
                  │
                  ▼
       Concrete Parser (uses shared Parser base)
                  │
                  ▼
                 AST
                  │
                  ▼
          Semantic Analysis
                  │
                  ▼
           Code Generation
                  │
                  ▼
             Binary Output
```

Each phase has a single responsibility and communicates with the next phase through well-defined interfaces.

This separation improves:

- maintainability
- testability
- diagnostics
- future extensibility
- architecture-specific implementation
- integration with the existing emulator and debugger

---

# Target Architecture Selection

The assembler supports two ways of determining the target architecture.

A source file may explicitly specify its target architecture using a target directive.

For example:

```assembly
TARGET XO-CHIP
```

A source file may also contain no target directive. In that case, the target architecture is supplied externally by the caller.

This allows the assembler to process both:

- source written specifically for this project, where a target directive can be used
- existing or externally supplied source that does not contain a target directive

The effective target architecture must be established before the architecture-specific parser is selected.

The target selection process is therefore:

```text
                 Assembly Source
                        │
                        ▼
                Target Discovery
                        │
             ┌──────────┴──────────┐
             │                     │
       TARGET present         TARGET absent
             │                     │
             ▼                     ▼
       Source target         External target
             │                     │
             └──────────┬──────────┘
                        │
                        ▼
                 Effective Target
                        │
                 ┌──────┴──────┐
                 ▼             ▼
                ISA      Concrete Parser
                 │             │
                 └──────┬──────┘
                        ▼
                  Shared Parser
```

If the source contains a target directive, the source-specified target is used.

If the source does not contain a target directive, the externally supplied target is used.

The external target is therefore an important part of the assembler API. It allows callers to assemble source for which no target directive is present.

For integration into the emulator GUI, the GUI will provide an external target selection mechanism, such as a drop-down or combo box. This selection supplies the target architecture when the source does not specify one.

---

# Architecture Support

Unlike high-level programming languages, an assembler is inherently tied to the target hardware.

Consequently, each supported CHIP-8 architecture defines its own language.

Examples include:

- COSMAC CHIP-8
- SUPER-CHIP
- XO-CHIP
- MegaChip

These architectures are closely related, but they may introduce new instructions, directives, registers, operands, or other language constructs.

The selected target determines the concrete parser. The parser uses the ISA interface to recognize supported instruction mnemonics.

For example:

```assembly
TARGET COSMAC

PLANE 1
```

The above program produces a syntax error because `PLANE` does not exist in the COSMAC assembly language.

Likewise:

```assembly
TARGET XO-CHIP

PLANE 1
```

may be syntactically valid if `PLANE` is defined by the XO-CHIP architecture.

This distinction is intentional.

The assembler is a hardware-specific programming language implementation. It is not a hardware-independent language that is subsequently compiled for different target platforms.

An instruction that does not exist in the selected architecture is therefore not treated as a valid language construct that happens to be semantically unsupported. It is a syntax error in the language defined by that architecture.

---

# Parser Architecture

The accepted parser design is described in ADR-014. `Parser` owns common grammar machinery, and `ClassicParser` provides Classic-target mnemonic recognition. The ISA exposes the accepted mnemonic set through `assembler_mnemonics()`; the parser does not duplicate that list or depend on `InstructionId`.

The Controller selects the effective target and constructs a matching ISA/parser pair before creating the `Assembler`. `Assembler` receives the parser instance through dependency injection and supplies each source's token stream before parsing.

Parsing recognizes whether a mnemonic belongs to the selected target language. Semantic analysis remains responsible for operand signatures and types, expression evaluation, symbol resolution, and range validation. `ArchitectureDefinition` and the generic grammar-driven parser framework described in older material are not part of the accepted design.

---

# Abstract Syntax Tree

The parser produces an Abstract Syntax Tree (AST).

The AST represents the syntactic structure of the source program independently of the final machine-code representation.

```text
Assembly Source
      │
      ▼
Target / Architecture Selection
      │
      ▼
ISA + Concrete Parser
      │
      ▼
Shared Parser Base
      │
      ▼
     AST
      │
      ▼
Semantic Analysis
      │
      ▼
Code Generation
```

The AST provides the boundary between parsing and subsequent processing.

Parsing is responsible for recognizing the source language and constructing the AST.

Parsing does not perform code generation.

Parsing does not resolve symbols.

Parsing does not generate machine code.

These responsibilities belong to later phases.

---

# Semantic Analysis

Semantic analysis operates on the AST produced by the parser.

Its responsibilities include:

- symbol definition
- symbol resolution
- expression evaluation
- address calculation
- validation of references
- validation of operand relationships
- detection of errors that cannot be determined from syntax alone

The parser determines whether the source conforms to the syntax of the selected architecture.

Semantic analysis determines whether a syntactically valid program is internally consistent and can be assembled.

This distinction is important because syntax and semantic validation have different responsibilities.

For example, an instruction that does not exist in the selected architecture is rejected during parsing.

A valid instruction referring to an undefined label is syntactically valid but produces a semantic error during semantic analysis.

---

# Code Generation

Code generation is separated from parsing and semantic analysis.

Its responsibility is to translate the validated AST into machine code for the selected target architecture.

Architecture-specific encoding information is supplied by the ISA and architecture subsystems rather than being embedded in the parser.

This separation allows:

- parser tests to operate independently of code generation
- semantic-analysis tests to operate on ASTs
- code-generation tests to concentrate on machine-code encoding
- architecture-specific encoding rules to remain localized

The code-generation stage consumes the result of semantic analysis and produces the binary representation required by the selected target architecture.

---

# Proposed Multi-Architecture Design

Additional architectures can reuse the shared parser base and provide concrete parser subclasses when their accepted instruction language differs.

A new architecture provides the definitions required by the parser and code-generation stages.

Conceptually:

```text
                         Assembler
                             │
              +--------------+--------------+
              │                             │
              ▼                             ▼
     Parser Base                    Code Generator
              │                             │
       +------+------+                +-----+------+
       │             │                │            │
       ▼             ▼                ▼            ▼
    COSMAC       XO-CHIP           COSMAC      XO-CHIP
 Architecture   Architecture      Encoding     Encoding
 Definition     Definition        Definition   Definition
```

The exact class structure used to implement architecture support is defined separately in the architecture design documentation.

The architecture-specific implementation may use inheritance where appropriate because the various CHIP-8 architectures are closely related extensions of the original COSMAC instruction set.

This is an implementation mechanism rather than a requirement that all architectures must share one class hierarchy.

---

# Separation of Parsing and Code Generation

Parsing and code generation are explicitly separate responsibilities.

Parsing determines the structure of the source program and produces the AST.

Semantic analysis validates that structure and resolves information required for assembly.

Code generation converts the validated representation into machine code.

```text
Source
  │
  ▼
Parsing
  │
  ▼
AST
  │
  ▼
Semantic Analysis
  │
  ▼
Validated AST
  │
  ▼
Code Generation
  │
  ▼
Machine Code
```

This separation is important for both architecture extensibility and future GUI integration.

The GUI can, for example, display parser and semantic diagnostics without requiring machine-code generation to have succeeded.

---

# Integration into the Emulator

The assembler is not intended to exist as an isolated tool.

Instead, it will become an integral part of the existing emulator application.

The assembler remains a separate subsystem under:

```text
src/
└── assembler/
```

It should therefore not be moved into the existing `src/chip8/` package.

The existing application architecture should require only limited changes outside the assembler subsystem.

The ISA subsystem is an intentional exception.

The ISA subsystem was designed with assembler integration in mind, so changes to the ISA subsystem are acceptable where they improve the common representation used by the emulator and assembler without requiring substantial changes elsewhere in the project.

Future GUI integration will include functionality such as:

- source editor integration
- target architecture selection
- assembly invocation
- assembler diagnostics
- navigation between source and machine code
- integration with the debugger
- integration with disassembly
- symbol-aware debugging

The exact GUI implementation is outside the scope of the assembler's internal architecture.

The assembler therefore exposes a public API through which the existing Controller can invoke assembly operations without directly depending on the parser, AST, semantic-analysis, or code-generation implementation.

---

# Relationship to the Emulator

The assembler and emulator remain separate subsystems.

```text
                  Controller
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
    Emulator       Assembler     Diagnostics
        │              │
        └──────────────┼──────────────┘
                       │
                       ▼
                       GUI
```

Neither subsystem depends on the internal implementation details of the other.

Only well-defined public interfaces are shared.

The assembler may share ISA-level information with the emulator where this is appropriate.

In particular, the existing ISA subsystem may be extended to provide information required by both the emulator and assembler.

Changes to the ISA subsystem are acceptable when they support this shared responsibility and do not require large changes throughout the rest of the emulator.

Outside of the ISA subsystem, the assembler should minimize changes to the existing project.

The assembler should not depend on implementation details of:

- `Chip8Machine`
- GUI models
- debugger implementation
- Controller implementation
- emulator execution state

Likewise, the existing emulator should interact with the assembler only through clearly defined interfaces.

---

# Development Principles

The assembler follows the same engineering principles as the rest of the project.

- Architecture before implementation.
- Documentation before coding.
- Test-driven development where practical.
- Clear separation of responsibilities.
- Small, independently testable components.
- Extensive diagnostics.
- Strong type checking.
- Clean linting.
- Consistent coding style across the entire project.
- Minimal changes to existing emulator components.
- Reuse of existing project infrastructure where appropriate.
- Keep assembler-specific implementation under `src/assembler`.
- Allow the ISA subsystem to evolve where this benefits assembler integration.
- Keep parsing separate from semantic analysis.
- Keep parsing and semantic analysis separate from code generation.
- Establish the target architecture before parsing.
- Make target-specific mnemonic recognition explicit through concrete parsers and the ISA's `assembler_mnemonics()` interface.

---

# Intended Audience

These documents are intended for:

- project maintainers
- future contributors
- reviewers
- developers implementing the assembler
- developers extending the assembler to additional CHIP-8 architectures
- developers integrating the assembler into the emulator and debugger GUI
