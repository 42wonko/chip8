# Assembler Design

**Author:** Michael Dlubatz

**Date:** 2026-08-13

**Status:** Proposed

---

## 1. Purpose

This document defines the overall architecture of the CHIP-8 assembler.

The assembler is designed as an independent subsystem of the existing CHIP-8 emulator project while remaining suitable for later integration into the existing emulator and debugger GUI.

The assembler implementation is located under:

```text
src/assembler/
```

The design separates source-language processing from target-specific architecture definitions, semantic analysis, and machine-code generation.

The design also establishes the output products produced by the assembler and the information required for later GUI and debugger integration.

---

## 2. Design Goals

The assembler shall:

- support multiple CHIP-8 architectures
- provide a grammar-driven parser framework
- select the target architecture before parsing
- support target selection from either the source or an external caller
- produce an explicit AST
- separate parsing from semantic analysis
- separate semantic analysis from code generation
- use the existing ISA subsystem where appropriate
- minimize changes to the existing emulator
- permit changes to the ISA subsystem where necessary for assembler integration
- provide comprehensive diagnostics
- support configurable output products
- provide information suitable for future debugger integration
- remain independent of the GUI
- remain independently testable

---

## 3. Architectural Context

The assembler is part of the existing CHIP-8 emulator project.

The existing project contains:

```text
src/
├── audio/
├── chip8/
├── controller/
├── emulator/
├── gui/
└── performance/
```

The assembler is added as:

```text
src/
└── assembler/
```

The assembler is deliberately not placed under `src/chip8/`.

The existing emulator and debugger architecture remains intact.

The assembler is integrated through the existing Controller architecture.

---

## 4. Overall Architecture

The assembler is divided into the following major processing stages:

```text
Assembly Source
      │
      ▼
Target Discovery
      │
      ▼
Target Selection
      │
      ▼
Architecture Definition
      │
      ▼
Parsing
      │
      ▼
Abstract Syntax Tree
      │
      ▼
Semantic Analysis
      │
      ▼
Code Generation
      │
      ▼
Assembly Output Products
```

The target architecture must be established before parsing because the selected architecture determines the language accepted by the parser.

The parser therefore cannot be architecture-independent at the language level, even though the parser framework itself is generic.

---

## 5. Target Architecture Selection

The assembler supports two mechanisms for determining the target architecture.

### 5.1 Target Directive

The source may contain a target directive:

```assembly
TARGET XO-CHIP
```

When such a directive is present, it identifies the target architecture for the source.

### 5.2 External Target

If the source does not contain a target directive, the caller must provide the target architecture externally.

This is required to support existing assembly source that does not contain target directives.

The effective target is determined as follows:

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
```

The source target takes precedence when present.

If neither a source target nor an external target is available, assembly cannot proceed.

---

## 6. Architecture Definition

The architecture definition describes the assembly language accepted for the selected target.

It may contain information such as:

- instruction mnemonics
- directives
- registers
- operands
- keywords
- reserved words
- expression forms
- architecture-specific constructs
- instruction encoding information
- architecture-specific semantic rules

The architecture definition is supplied to the parser framework.

The parser framework does not contain hard-coded definitions for individual architectures.

Conceptually:

```text
+---------------------------+
| Architecture Definition   |
+-------------+-------------+
              │
              ▼
+---------------------------+
| Parser Framework          |
+-------------+-------------+
              │
              ▼
+---------------------------+
| Abstract Syntax Tree      |
+---------------------------+
```

---

## 7. Architecture-Specific Language

An assembler is inherently tied to its target hardware.

The selected architecture therefore defines the language accepted by the parser.

For example:

```assembly
TARGET COSMAC

PLANE 1
```

is a syntax error because `PLANE` does not exist in the COSMAC assembly language.

The same construct may be valid for an architecture that defines `PLANE`.

This is a syntax distinction, not a semantic distinction.

The assembler does not first parse an architecture-independent language and subsequently determine whether the target supports the instruction.

The selected architecture participates directly in parsing.

---

## 8. Parser Framework

The parser framework provides generic parsing machinery.

It is driven by the grammar and architecture definition of the selected target.

The framework is responsible for:

- tokenization
- grammar processing
- syntactic recognition
- construction of AST nodes
- syntax diagnostics
- source-location tracking

The framework is not responsible for:

- machine-code generation
- symbol resolution
- final address assignment
- emulator interaction
- GUI interaction

---

## 9. Architecture Implementation Strategy

The different CHIP-8 architectures are closely related.

Many architectures extend the original COSMAC CHIP-8 instruction set with additional instructions or modified behavior.

An object-oriented architecture model may therefore use inheritance where appropriate.

Conceptually:

```text
             Base Architecture
                    │
          ┌─────────┼─────────┐
          │         │         │
          ▼         ▼         ▼
       COSMAC    SUPER-CHIP  XO-CHIP
```

This is an implementation option rather than a mandatory class hierarchy.

The architecture model should be selected based on the actual relationships between the supported architectures.

The parser framework remains independent of the specific implementation mechanism.

---

## 10. Abstract Syntax Tree

The parser produces an Abstract Syntax Tree.

The AST represents the structure of the source program independently of machine-code output.

```text
Source
  │
  ▼
Parser
  │
  ▼
 AST
  │
  ▼
Semantic Analysis
```

The AST should contain sufficient source-location information to allow diagnostics and later source-to-address mapping.

The AST should not contain GUI objects or emulator state.

---

## 11. Semantic Analysis

Semantic analysis operates on the AST.

It is responsible for information that cannot be determined solely from the grammar.

Responsibilities include:

- symbol definition
- symbol resolution
- expression evaluation
- address calculation
- validation of references
- validation of operands
- detection of duplicate symbols
- detection of undefined symbols
- validation of architectural restrictions
- preparation of information required for code generation

The distinction between syntax and semantics remains important.

An unknown instruction for the selected architecture is a syntax error.

An undefined label referenced by an otherwise valid instruction is a semantic error.

---

## 12. Symbol Table

Semantic analysis produces a symbol table.

The symbol table contains information about symbols such as:

- labels
- subroutine labels
- variables
- constants
- addresses
- source locations

Conceptually:

```text
Symbol Table
├── name
├── value/address
├── type
└── source location
```

The symbol table is also an important input to later output generation.

---

## 13. Source Mapping

The assembler should maintain a mapping between generated addresses and source locations.

Conceptually:

```text
Source line       Address
-----------       -------
10                0x200
11                0x202
12                0x204
13                0x206
```

This mapping is useful for:

- listing generation
- cross-reference generation
- debugger integration
- source-aware disassembly
- address-to-source navigation

Source mapping should therefore be treated as assembler metadata rather than as a GUI-specific feature.

---

## 14. Code Generation

Code generation converts the validated semantic representation into machine code.

```text
Validated AST
      │
      ▼
Code Generator
      │
      ▼
Binary ROM Image
```

Architecture-specific encoding information is obtained from the ISA and architecture subsystems.

Encoding logic should not be embedded in the parser.

The code generator is not responsible for:

- displaying output
- writing GUI files
- loading emulator memory
- interacting with Qt

---

## 15. ISA Integration

The existing ISA subsystem was designed with assembler integration in mind.

Changes to the ISA subsystem are therefore permitted where necessary to provide a clean common representation for the emulator and assembler.

Such changes should avoid requiring large changes elsewhere in the existing project.

The goal is to share authoritative instruction-set information where practical rather than duplicating it between the emulator and assembler.

The assembler should nevertheless remain independent of the emulator's execution implementation.

---

## 16. Assembly Output Products

The assembler produces several possible output products.

The primary product is:

- **Binary ROM image**

Optional products are:

- **Listing file**
- **Cross-reference information**

The assembler also produces metadata used internally and by other application components:

- diagnostics
- symbol table
- source mapping

The distinction is:

```text
                         Assembler
                             │
                             ▼
                      Assembly Result
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   Binary Image          Listing            Cross-Reference
        │                    │                    │
        ▼                    ▼                    ▼
     ROM/File              File                 File
```

The listing and cross-reference products are configurable.

---

## 17. Binary ROM Image

The binary ROM image is the fundamental machine-code output.

It contains the generated bytes for the selected architecture.

The assembler produces the image independently of its eventual destination.

The application may:

- load it into the emulator
- save it to a file
- inspect it
- pass it to another subsystem

The assembler does not decide which of these operations occurs.

---

## 18. Listing File

A listing file combines source information with generated machine-code information.

A listing may contain:

```text
Address   Machine Code   Source
-------   ------------   ----------------
0200      6000           LD V0, 0
0202      6101           LD V1, 1
0204      8014           ADD V0, V1
0206      1206           JP LOOP
```

The exact format is defined separately.

Listing generation is configurable.

The listing generator uses:

- AST information
- source locations
- generated addresses
- machine-code bytes
- symbol information

The listing is an assembler output product and is not generated by the GUI.

---

## 19. Cross-Reference Output

The assembler should provide cross-reference information covering at least:

- labels
- subroutine labels
- variables
- addresses
- definition source lines
- references to symbols

Conceptually:

```text
Symbol       Address    Defined At    References
-----------  ---------  ------------  ----------------
START        0200       line 5        line 18
LOOP         020A       line 10       lines 14, 17
DRAW         0220       line 22       line 30
```

Cross-reference information may be:

- included in the listing
- generated as a separate output product

The implementation should support both possibilities without requiring the semantic-analysis subsystem to change.

---

## 20. Configurable Output Generation

Output generation is controlled by assembly options.

Conceptually:

```text
Assembly Options
├── generate_binary       = true
├── generate_listing      = false
└── generate_crossref     = false
```

The binary image is the primary assembly result.

Listing and cross-reference generation are optional.

The configuration is part of the assembly request.

The GUI provides the user interface for selecting these options.

---

## 21. Output Generation Pipeline

The output products are generated from the validated assembly representation.

```text
                 Semantic Analysis
                        │
             ┌──────────┴──────────┐
             │                     │
             ▼                     ▼
       Symbol Table          Source Mapping
             │                     │
             └──────────┬──────────┘
                        │
                        ▼
                  Code Generation
                        │
                        ▼
                 Binary ROM Image
                        │
                        ├───────────────┐
                        │               │
                        ▼               ▼
                   Listing        Cross-Reference
```

The binary image is generated by the code-generation stage.

The listing and cross-reference generators consume the information produced during assembly.

This keeps output generation separate from the parser and semantic-analysis implementation.

---

## 22. Assembly Result

The assembler exposes the products and metadata of an assembly operation through an assembly result.

Conceptually:

```text
AssemblyResult
├── status
├── diagnostics
├── binary_image
├── listing
├── cross_reference
├── symbols
└── source_mapping
```

Not every field necessarily contains data.

For example:

- `binary_image` is present after successful code generation
- `listing` is present only when requested
- `cross_reference` is present only when requested
- `symbols` may be available after semantic analysis
- `source_mapping` is available when generated

The exact API representation is defined by `assembler_public_api.md`.

---

## 23. Diagnostics

Diagnostics are generated throughout the assembly pipeline.

Examples include:

- lexical errors
- syntax errors
- invalid instructions
- invalid operands
- undefined symbols
- duplicate symbols
- invalid expressions
- address-range errors
- architecture-specific errors
- code-generation errors

Diagnostics should contain source-location information wherever possible.

Conceptually:

```text
Diagnostic
├── severity
├── message
├── source
├── line
├── column
├── source range
└── diagnostic code
```

The assembler does not display diagnostics.

The diagnostics are returned through the assembly result and are handled by the application.

---

## 24. GUI Independence

The assembler must remain independent of the GUI.

The assembler must not depend on:

- PyQt6
- widgets
- dialogs
- editor models
- `MainWindow`
- GUI-specific models
- GUI event handling

The GUI communicates with the assembler through the Controller and public assembler API.

---

## 25. Emulator Independence

The assembler must remain independent of emulator execution state.

The assembler must not directly access:

- `Chip8Machine`
- `Chip8Memory`
- emulator registers
- timers
- keyboard
- framebuffer
- debugger state

The Controller decides whether a generated ROM image is loaded into the emulator.

---

## 26. Application Integration

The high-level application architecture is:

```text
                         Chip8Controller
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
       MainWindow           Emulator            Assembler
                                                     │
                                                     ▼
                                            Assembly Result
```

The assembler is therefore a peer subsystem of the emulator from the Controller's perspective.

The assembler does not become a child component of `Chip8Machine`.

---

## 27. Assembly Request

The Controller supplies the assembler with an assembly request.

Conceptually:

```text
AssemblyRequest
├── source
├── source_name
├── external_target
└── assembly_options
```

The request contains all information required to perform an assembly operation.

The assembler must not retrieve this information directly from the GUI.

---

## 28. GUI Integration

The assembler GUI is provided as a dedicated dialog within the existing application.

The existing main window receives an **Assembler** button.

```text
Existing MainWindow
┌─────────────────────────────────────────────┐
│                                             │
│ [ Assembler ]                               │
│                                             │
└─────────────────────────────────────────────┘
                     │
                     ▼
             Assembler Dialog
```

The assembler dialog provides:

- source editing
- target selection
- output configuration
- assembly controls
- assembler diagnostics
- generated-output controls

The exact visual design is specified separately.

---

## 29. Assembler Dialog

A functional concept for the dialog is:

```text
+-------------------------------------------------------------+
| Target: [ COSMAC CHIP-8                         ▼ ]        |
+-------------------------------------------------------------+
|                                                             |
|                    Source Editor                            |
|                                                             |
|                                                             |
+-------------------------------------------------------------+
| Output                                                      |
| [✓] Binary ROM   [ ] Listing   [ ] Cross-Reference         |
+-------------------------------------------------------------+
| Diagnostics                                                 |
|                                                             |
+-------------------------------------------------------------+
| Assemble | Assemble & Load | Save ROM                     |
| Save Listing | Save Cross-Reference                       |
+-------------------------------------------------------------+
```

The exact controls and layout remain subject to detailed GUI design.

---

## 30. Data Flow Through the Application

The complete application-level data flow is:

```text
                         User
                          │
                          ▼
                  Assembler Dialog
                          │
             source + target + options
                          │
                          ▼
                   Chip8Controller
                          │
                          ▼
                  AssemblyRequest
                          │
                          ▼
                      Assembler
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
        Assembly Result          Diagnostics
              │
       ┌──────┼───────────┐
       │      │           │
       ▼      ▼           ▼
     ROM    Listing   Cross-Reference
       │      │           │
       └──────┼───────────┘
              │
              ▼
        Chip8Controller
              │
       ┌──────┼───────────────┐
       │      │               │
       ▼      ▼               ▼
      GUI   Output Files   Emulator
```

---

## 31. File Output

The assembler itself produces output data.

The application controls where that data is stored.

The GUI is responsible for obtaining filenames from the user.

The Controller coordinates the actual save operation.

This prevents filesystem and GUI concerns from leaking into the assembler core.

---

## 32. Debugger Integration

The assembler should preserve enough information to support future source-level debugging.

Important information includes:

- symbols
- source locations
- generated addresses
- instruction boundaries
- source-to-address mappings

Conceptually:

```text
Assembly
   │
   ├── ROM Image
   ├── Symbols
   └── Source Mapping
           │
           ▼
       Controller
           │
           ▼
        Debugger
```

Possible future functionality includes:

- source-level breakpoints
- source-line highlighting
- symbol lookup
- source-aware stepping
- source-to-address navigation
- address-to-source navigation

---

## 33. Relationship to Existing Code Analysis

The assembler and existing static code-analysis subsystem have different responsibilities.

The assembler starts from source and produces machine code.

The code-analysis subsystem starts from machine code and determines the structure of the program.

Where useful, the two may eventually exchange information through explicit interfaces.

Assembler-produced symbols and source mappings may improve source-aware code analysis and debugging.

The assembler should not directly depend on the implementation of `CodeAnalysis`.

---

## 34. Development Constraints

The assembler implementation should minimize changes to the existing project.

Changes are expected primarily in:

```text
src/assembler/
```

and, where necessary:

```text
src/isa/
```

or the actual existing ISA subsystem location.

The ISA subsystem is explicitly allowed to evolve because it was designed with assembler integration in mind.

Changes elsewhere in the existing project should be limited to the interfaces necessary for integration.

---

## 35. Testing Strategy

Each assembler subsystem should be independently testable.

Tests should cover at least:

- target discovery
- target selection
- lexical analysis
- syntax parsing
- AST construction
- semantic analysis
- symbol resolution
- expression evaluation
- code generation
- output generation
- diagnostics
- listing generation
- cross-reference generation
- public API behavior

Integration tests should additionally verify:

- Controller-to-assembler communication
- assembler-to-Controller result flow
- ROM loading
- output-file generation
- diagnostic routing

GUI tests should verify the assembler dialog independently from the assembler implementation wherever practical.

---

## 36. Summary

The assembler is a separate subsystem located under `src/assembler`.

Its architecture is based on a clear separation between:

```text
Target Selection
      │
      ▼
Architecture Definition
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
Code Generation
      │
      ▼
Output Generation
```

The assembler produces a binary ROM image as its primary output and optionally produces:

- a listing file
- cross-reference information

The generation of listing and cross-reference products is configurable.

Symbols and source mappings are retained as assembler metadata and provide the foundation for listing generation, cross-reference generation, and future debugger integration.

The assembler remains independent of the GUI and emulator.

The existing `Chip8Controller` coordinates communication between the assembler, GUI, emulator, diagnostics infrastructure, and future debugger integration.

The existing GUI is extended with an **Assembler** button that opens a dedicated assembler dialog.

The assembler dialog provides source editing, target selection, output configuration, assembly controls, and a dedicated assembler diagnostics view.

Generated ROM images can either be loaded into the emulator or saved to a file.

Listing and cross-reference products can be saved independently.

This design keeps the assembler modular and independently testable while allowing it to become a fully integrated part of the existing CHIP-8 emulator and debugger application.
