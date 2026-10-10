# Parser Architecture

**Status:** Proposed architecture, with the `Parser` / `ClassicParser` foundation implemented.

This document describes the shared parser design. The current source code and tests are authoritative where implementation details differ from this design description.

## Purpose

The assembler uses a hand-written parser hierarchy. `Parser` contains common grammar machinery, and concrete architecture parsers specialize instruction-mnemonic recognition. The design does not use an `ArchitectureDefinition` object or a grammar-driven parser framework.

The Controller selects the effective assembler target before constructing the assembler. It supplies an ISA and a parser that correspond to that target. The same ISA instance is shared by the concrete parser and the `Assembler`.

## Responsibilities

The base `Parser` owns common syntax handling:

- token stream and current position;
- labels and source lines;
- common directives;
- comma-separated operands;
- expressions, parentheses, and indirect expressions;
- AST construction;
- source locations and parser errors.

A concrete architecture parser determines whether an instruction mnemonic is part of the selected target's assembler language. It should not duplicate the supported mnemonic list or depend on `InstructionId`.

The ISA abstraction exposes assembler mnemonic knowledge through `assembler_mnemonics() -> frozenset[str]`.

## Parsing and Semantic Validation

The parser rejects an unsupported mnemonic as a syntax error. It parses operands using the common grammar, without determining whether their combination is valid for that instruction.

Semantic analysis remains responsible for:

- validating operand signatures and types;
- evaluating expressions;
- resolving symbols;
- checking operand ranges and addresses;
- producing semantic diagnostics.

For example, an unsupported mnemonic is rejected by the architecture-specific parser. A recognized mnemonic with an invalid operand type is rejected by semantic analysis.

## Parser Lifecycle

`Assembler` receives a parser instance through constructor injection. For each assembly operation it lexes the source, supplies the token list to the injected parser, and invokes `parse()`. The parser resets its position when a new token stream is supplied so that repeated assembly operations do not leak parser state.

The parser is therefore reusable, but the caller must supply a fresh token stream for each parse operation. Reuse between assembly calls is distinct from recovery within one source file; both behaviors are required.

## Statement-Boundary Error Recovery

Within a source file, a parser error in one statement must not prevent the parser from checking later statements. After reporting the error, the parser must synchronize at the next statement boundary (the end of the malformed statement) and resume parsing. For the current line-oriented language, the next source line is the normal synchronization point. End-of-input is also a valid boundary.

Recovery must make progress: it must consume input or reach end-of-input, so the same malformed token cannot cause an infinite recovery loop. The parser must preserve the source location and diagnostic for each detected error and continue collecting subsequent parser diagnostics.

The AST produced during recovery is partial and must not be treated as a valid program. If any parser errors were reported, the assembler must retain those diagnostics and stop the compilation pipeline before semantic analysis and code generation. This prevents a partial AST from producing a binary image that could be mistaken for a successful assembly. The recovery requirement does not prescribe a particular AST representation for malformed statements; an explicit error node is optional if the implementation can otherwise preserve the required diagnostics and continue safely.

The current implementation stops at the first `ParserError`; statement-boundary recovery remains implementation work. The existing reuse regression test covers a later assembly call after a failed call, not multiple errors within a single source file.

## Initial Hierarchy

```text
Parser
  └── ClassicParser
        └── InstructionSetArchitecture
              └── assembler_mnemonics()
```

The diagram indicates the parser's dependency on the ISA interface; it does not mean the ISA inherits from the parser.

## Target and Machine Isolation

The Controller creates the assembler's ISA/parser pair based on the selected assembler target. This pair is separate from the ISA configured on `Chip8Machine`. Selecting an assembler target must not change the machine's architecture or the machine interface.

## Extension Strategy

Add a concrete parser when a future target requires a different set of accepted instruction mnemonics or other target-specific syntax. Reuse the base parser's common machinery and override only the target-specific behavior that actually differs. Do not introduce a generic instruction-definition or architecture-definition abstraction without a demonstrated need.
