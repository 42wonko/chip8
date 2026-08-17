# Assembler Development Plan

**Author:** Michael Dlubatz

**Date:** 2026-08-13

**Status:** Proposed

---

## 1. Purpose

This document defines the development strategy for implementing the assembler and integrating it into the existing CHIP-8 emulator application.

The primary objective is to introduce the assembler incrementally without destabilizing or unnecessarily modifying the existing emulator, debugger, GUI, Controller, or other existing subsystems.

The assembler will be implemented under:

`src/assembler/`

The existing application remains the foundation of the system. The assembler is an additional subsystem that is progressively integrated into it.

The development strategy follows these principles:

1. Add new functionality incrementally.
2. Keep the existing emulator operational throughout development.
3. Introduce and test new abstractions before replacing existing implementations.
4. Keep changes to the existing application as small as practical.
5. Permit changes to the ISA subsystem where required for assembler integration.
6. Test every development step independently.
7. Never proceed to the next architectural step with a failing previous step.
8. Preserve existing emulator behavior unless a deliberate change has been specified.
9. Keep the assembler independent of the GUI and emulator.
10. Integrate the assembler into the existing application only after the assembler core is functional and tested.

---

## 2. Development Strategy

The implementation proceeds from the inside out.

The overall progression is:

```text
Phase 0   Establish baseline
    │
    ▼
Phase 1   Assembler foundation
    │
    ▼
Phase 2   ISA integration
    │
    ▼
Phase 3   Target architecture selection
    │
    ▼
Phase 4   Lexer
    │
    ▼
Phase 5   Parser and AST
    │
    ▼
Phase 6   Semantic analysis
    │
    ▼
Phase 7   Code generation
    │
    ▼
Phase 8   Output products
    │
    ▼
Phase 9   Public assembler API
    │
    ▼
Phase 10  Controller integration
    │
    ▼
Phase 11  Diagnostics integration
    │
    ▼
Phase 12  Assembler GUI
    │
    ▼
Phase 13  Emulator integration
    │
    ▼
Phase 14  Save operations
    │
    ▼
Phase 15  Regression ROM suite
    │
    ▼
Phase 16  Full application integration
```

Each phase has its own implementation scope and verification criteria.

---

## 3. Safety and Compatibility Rules

Assembler development must not become a large-scale refactoring of the existing emulator.

The following rules apply throughout the project.

### 3.1 Add Before Replacing

When a new abstraction is required, implement and test it before removing the existing implementation.

### 3.2 No Big-Bang Integration

The assembler must not initially be connected to all existing subsystems simultaneously.

The progression should be:

```text
Assembler core
      │
      ▼
Assembler API
      │
      ▼
Controller
      │
      ▼
GUI
      │
      ▼
Emulator
```

### 3.3 One Architectural Change at a Time

After each architectural change:

```text
Implementation
      │
      ▼
Tests
      │
      ▼
Ruff
      │
      ▼
mypy
      │
      ▼
Regression tests
```

must all pass.

### 3.4 Preserve Existing Behavior

Existing emulator behavior must remain unchanged unless a deliberate architectural or ISA change is being made.

### 3.5 ISA Changes Are Permitted

The ISA subsystem is an explicit exception to the general minimal-change rule.

Changes to the ISA subsystem are allowed where they:

- remove duplication
- provide authoritative instruction information
- improve assembler support
- improve sharing between emulator and assembler
- avoid large changes elsewhere

Such changes must still preserve existing emulator behavior unless a deliberate correction is intended.

---

## 4. Phase 0 — Establish the Baseline

Before implementing the assembler, establish the current state of the project as the reference baseline.

### 4.1 Objectives

Verify that the existing project is healthy before introducing assembler changes.

The baseline must include:

- unit tests
- integration tests
- emulator tests
- debugger tests
- ISA tests
- code-analysis tests
- existing regression ROMs
- Ruff
- mypy

### 4.2 Verification

Run:

```text
pytest
ruff check .
mypy .
```

Run the existing regression ROM suite if available.

The expected state is:

```text
Existing tests       PASS
Regression ROMs      PASS
Ruff                 CLEAN
mypy                 CLEAN
```

### 4.3 Implementation Rule

No assembler implementation should begin until the baseline is known.

If the baseline contains existing failures, those failures must be documented before proceeding.

---

## 5. Phase 1 — Assembler Foundation

Create the basic assembler package without implementing parsing or code generation.

### 5.1 Initial Structure

The initial structure should be limited to concepts actually required at this stage.

```text
src/assembler/
├── __init__.py
├── assembler.py
├── diagnostics.py
├── options.py
├── result.py
└── target.py
```

The exact module boundaries may be adjusted during implementation.

Empty modules must not be created merely to match this proposed structure.

### 5.2 Initial Concepts

Establish the basic concepts:

- `AssemblyRequest`
- `AssemblyResult`
- `AssemblyOptions`
- `Target`
- `Diagnostic`

The assembler may initially return a controlled result without performing real assembly.

### 5.3 Tests

Create:

```text
tests/assembler/
├── test_assembler.py
├── test_diagnostics.py
├── test_options.py
├── test_result.py
└── test_target.py
```

### 5.4 Verification

The following must pass:

- assembler tests
- existing project tests
- Ruff
- mypy

No existing emulator code should need modification during this phase.

---

## 6. Phase 2 — ISA Integration

Integrate the assembler with the existing ISA subsystem.

This is the first phase where modifications to existing project code are expected.

### 6.1 Objective

Avoid creating a second independent instruction-set database in the assembler.

The desired architecture is:

```text
                       ISA
                        │
               ┌────────┴────────┐
               │                 │
               ▼                 ▼
           Emulator          Assembler
               │                 │
               ▼                 ▼
           Execution          Encoding
```

The ISA subsystem should become the authoritative source for information shared by both consumers.

### 6.2 Initial Investigation

Before modifying the ISA subsystem:

1. Identify the current ISA representation.
2. Identify where instruction definitions are stored.
3. Identify how instruction decoding currently obtains instruction information.
4. Identify what information the assembler requires.
5. Identify which existing emulator components depend on the current ISA representation.
6. Determine the smallest ISA change that satisfies the assembler requirements.

No assumed classes or files should be introduced without first verifying that they exist in the current project.

### 6.3 Implementation

Extend the existing ISA representation where necessary.

Do not move the ISA subsystem into the assembler.

Do not make the assembler depend directly on emulator execution classes.

### 6.4 Testing

Before each ISA modification:

```text
Existing ISA tests     PASS
Existing emulator      PASS
```

After each modification:

```text
ISA tests
Emulator tests
Assembler tests
Ruff
mypy
```

must all pass.

---

## 7. Phase 3 — Target Architecture Selection

Implement target selection before implementing the architecture-dependent parser.

### 7.1 Required Behavior

The assembler supports two target-selection mechanisms.

A source may contain a target directive:

```text
TARGET COSMAC
```

If no target directive is present, the caller supplies the target externally.

The source target takes precedence over the externally supplied target.

The processing is therefore:

```text
                    Source
                      │
                      ▼
               Target Discovery
                      │
             ┌────────┴────────┐
             │                 │
        TARGET present     TARGET absent
             │                 │
             ▼                 ▼
       Source target      External target
             │                 │
             └────────┬────────┘
                      │
                      ▼
                Effective Target
```

### 7.2 Required Test Cases

| Source | External Target | Result |
|---|---|---|
| `TARGET A` | A | A |
| `TARGET A` | B | A |
| No TARGET | A | A |
| No TARGET | B | B |
| No TARGET | None | Diagnostic |

### 7.3 Processing Constraint

Target selection must occur before architecture-dependent parsing.

The sequence must therefore be:

```text
Source
  │
  ▼
Target Discovery
  │
  ▼
Target Selection
  │
  ▼
Architecture
  │
  ▼
Parsing
```

---

## 8. Phase 4 — Lexer

Implement lexical analysis.

### 8.1 Likely Files

```text
src/assembler/token.py
src/assembler/lexer.py
```

### 8.2 Responsibilities

The lexer converts source text into tokens.

For example:

```text
LD V0, 42
```

becomes conceptually:

```text
MNEMONIC("LD")
REGISTER("V0")
COMMA
NUMBER(42)
```

Tokens must retain source-location information.

### 8.3 Tests

```text
tests/assembler/test_token.py
tests/assembler/test_lexer.py
```

Tests should include:

- identifiers
- mnemonics
- registers
- numbers
- hexadecimal values
- decimal values
- labels
- punctuation
- directives
- comments
- whitespace
- source locations
- malformed input

---

## 9. Phase 5 — Parser and AST

Implement the architecture-dependent parser and AST.

### 9.1 Likely Files

```text
src/assembler/parser.py
src/assembler/ast.py
```

### 9.2 Processing Sequence

```text
Source
  │
  ▼
Target Selection
  │
  ▼
Architecture Definition
  │
  ▼
Lexer
  │
  ▼
Parser
  │
  ▼
AST
```

### 9.3 AST Responsibilities

The AST represents source structure.

Conceptually:

```text
Program
├── Label
├── Instruction
│   ├── mnemonic
│   └── operands
└── Directive
```

The AST must retain source-location information.

### 9.4 Parser Responsibilities

The parser is responsible for:

- syntactic recognition
- grammar validation
- AST construction
- syntax diagnostics

The parser is not responsible for:

- symbol resolution
- final address assignment
- machine-code generation
- file output
- emulator interaction

### 9.5 Tests

```text
tests/assembler/test_parser.py
tests/assembler/test_ast.py
```

---

## 10. Phase 6 — Semantic Analysis

Implement semantic analysis after the parser produces a stable AST.

### 10.1 Likely Files

```text
src/assembler/semantic.py
src/assembler/symbols.py
```

### 10.2 Responsibilities

Semantic analysis handles:

- symbol definition
- symbol resolution
- duplicate symbols
- undefined symbols
- expression evaluation
- address assignment
- operand validation
- architecture-specific semantic rules
- range checking

### 10.3 Source Mapping

Semantic analysis should preserve information that allows:

```text
Source line → Generated address
```

This is required later for:

- listings
- cross-reference output
- debugger integration

### 10.4 Tests

```text
tests/assembler/test_semantic.py
tests/assembler/test_symbols.py
```

Test:

- labels
- subroutine labels
- variables
- constants
- duplicate definitions
- undefined references
- forward references
- expressions
- address ranges
- architecture restrictions

---

## 11. Phase 7 — Code Generation

Implement machine-code generation.

### 11.1 Likely Files

```text
src/assembler/codegen.py
```

### 11.2 Processing

```text
Validated AST
      │
      ▼
Code Generator
      │
      ▼
Binary ROM Image
```

### 11.3 ISA Usage

Instruction encoding must use the shared ISA representation wherever practical.

Encoding logic must not be duplicated unnecessarily between `src/assembler/` and the ISA subsystem.

### 11.4 Tests

```text
tests/assembler/test_codegen.py
```

Every supported instruction should have encoding tests.

---

## 12. Phase 8 — Output Products

The assembler produces the following products:

1. Binary ROM image
2. Optional listing
3. Optional cross-reference

### 12.1 Likely Files

```text
src/assembler/listing.py
src/assembler/cross_reference.py
```

### 12.2 Listing

The listing generator consumes:

- source
- source locations
- generated addresses
- machine-code bytes
- symbols

Example:

```text
Address   Machine Code   Source
-------   ------------   ----------------
0200      6000           LD V0, 0
0202      6101           LD V1, 1
0204      8014           ADD V0, V1
```

### 12.3 Cross-Reference

The cross-reference generator consumes:

- symbol table
- source locations
- generated addresses
- symbol references

Example:

```text
Symbol       Address    Defined At    References
-----------  ---------  ------------  ----------------
START        0200       line 5        line 18
LOOP         020A       line 10       lines 14, 17
```

### 12.4 Configurability

Output generation must be configurable:

```text
Assembly Options
├── generate_binary
├── generate_listing
└── generate_crossref
```

Listing and cross-reference generation are optional.

### 12.5 Tests

```text
tests/assembler/test_listing.py
tests/assembler/test_cross_reference.py
```

---

## 13. Phase 9 — Public Assembler API

Only after the internal assembler pipeline is working should the public API be finalized.

### 13.1 Desired Interface

Conceptually:

```text
request = AssemblyRequest(...)

result = assembler.assemble(request)
```

The caller must not need to know about lexer, parser, AST, semantic-analysis, or code-generation internals.

### 13.2 Assembly Result

The result should expose, as appropriate:

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

Optional products may be absent when their generation was not requested.

---

## 14. Phase 10 — Controller Integration

Only after the assembler core is stable should it be connected to `Chip8Controller`.

### 14.1 Initial Integration

```text
Controller
    │
    ▼
AssemblyRequest
    │
    ▼
Assembler
    │
    ▼
AssemblyResult
    │
    ▼
Controller
```

Do not load the result into the emulator yet.

### 14.2 Responsibilities

The Controller:

- obtains source from the GUI
- obtains target selection
- obtains output options
- constructs `AssemblyRequest`
- invokes the assembler
- receives `AssemblyResult`
- makes the result available to the GUI

The Controller does not implement assembler logic.

---

## 15. Phase 11 — Diagnostics Integration

Connect assembler diagnostics to the existing diagnostic infrastructure.

### 15.1 Data Flow

```text
Assembler
    │
    ▼
Diagnostic
Source = "Assembler"
    │
    ▼
Controller / Log Manager
    │
    ▼
Assembler Diagnostics View
```

Assembler diagnostics should be displayed in a dedicated assembler diagnostics view rather than the existing general diagnostics view.

The `Source` field of the diagnostic message can be used by the Controller/log manager to route assembler diagnostics appropriately.

### 15.2 Tests

Verify:

- assembler errors appear in the assembler diagnostics view
- emulator diagnostics continue to appear in their existing destination
- diagnostic source information is preserved
- source locations are preserved

---

## 16. Phase 12 — Assembler GUI

Implement the dedicated assembler dialog only after the assembler core and Controller interface are stable.

### 16.1 Existing GUI Change

The existing `MainWindow` receives an **Assembler** button.

Pressing it opens the assembler dialog.

```text
MainWindow
    │
    └── [Assembler]
            │
            ▼
      Assembler Dialog
```

### 16.2 GUI Responsibilities

The assembler dialog provides:

- source editor
- target selector
- output configuration
- Assemble
- Assemble & Load
- Save ROM
- Save Listing
- Save Cross-Reference
- assembler diagnostics view

The GUI must not directly invoke assembler internals.

---

## 17. Phase 13 — Emulator Integration

Implement `Assemble & Load`.

### 17.1 Data Flow

```text
Assembler
    │
    ▼
AssemblyResult
    │
    ▼
Controller
    │
    ▼
Binary ROM Image
    │
    ▼
Existing Emulator Load Mechanism
```

The existing ROM-loading mechanism should be reused.

### 17.2 Failure Behavior

If assembly fails, the currently loaded emulator program remains unchanged.

If assembly succeeds, the generated ROM is passed through the existing emulator loading mechanism.

---

## 18. Phase 14 — Save Operations

Saving generated output products is a required GUI feature.

The GUI provides the filename-selection operation.

The Controller coordinates the save operation.

### 18.1 Save ROM

```text
AssemblyResult
      │
      ▼
Binary Image
      │
      ▼
Save ROM File
```

### 18.2 Save Listing

```text
AssemblyResult
      │
      ▼
Listing
      │
      ▼
Save Listing File
```

### 18.3 Save Cross-Reference

```text
AssemblyResult
      │
      ▼
Cross-Reference
      │
      ▼
Save Cross-Reference File
```

The assembler itself must not open GUI file dialogs.

---

## 19. Phase 15 — Regression ROM Suite

After individual instruction encoding is working, create a complete assembler regression suite.

### 19.1 Purpose

```text
Assembly Source
      │
      ▼
Assembler
      │
      ▼
Generated ROM
      │
      ▼
Expected ROM
      │
      ▼
Byte-for-byte comparison
```

### 19.2 Coverage

The regression suite should eventually cover:

- all instruction families
- labels
- forward references
- backward references
- subroutines
- expressions
- directives
- architecture-specific instructions
- boundary addresses
- invalid programs

---

## 20. Phase 16 — Full Application Integration

The final integration test verifies the complete workflow.

```text
Open Application
       │
       ▼
Open Assembler
       │
       ▼
  Enter Source
       │
       ▼
  Select Target
       │
       ▼
Configure Outputs
       │
       ▼
     Assemble
       │
       ├───────────────┐
       │               │
       ▼               ▼
   Diagnostics       Outputs
                       │
             ┌─────────┼─────────┐
             │         │         │
             ▼         ▼         ▼
           ROM      Listing   Cross-Ref
             │
             ▼
       Assemble & Load
             │
             ▼
          Emulator
```

The complete workflow must be tested using a real assembly program.

---

## 21. Testing Strategy

Testing is continuous throughout development.

The minimum verification after each phase is:

```text
Assembler tests        PASS
Existing tests         PASS
Ruff                   CLEAN
mypy                   CLEAN
```

Where applicable:

```text
ISA tests              PASS
Regression ROMs        PASS
GUI tests              PASS
Integration tests      PASS
```

---

## 22. Test Categories

### 22.1 Unit Tests

Test individual components:

- Lexer
- Parser
- AST
- Symbol Table
- Semantic Analysis
- Code Generator
- Listing Generator
- Cross-Reference Generator

### 22.2 Integration Tests

Test interactions:

```text
Target Selection → Parser
Parser → Semantic Analysis
Semantic Analysis → Code Generator
Code Generator → Output Products
Controller → Assembler
Controller → Emulator
```

### 22.3 Public API Tests

Test the assembler through its public interface rather than its internal implementation.

### 22.4 Regression Tests

Use complete assembly programs and expected ROM images.

### 22.5 Application Tests

Test:

```text
GUI
  │
  ▼
Controller
  │
  ▼
Assembler
  │
  ▼
Controller
  │
  ▼
GUI
```

and eventually:

```text
GUI
  │
  ▼
Controller
  │
  ▼
Assembler
  │
  ▼
ROM
  │
  ▼
Emulator
```

---

## 23. Verification Gate

No phase is complete until its verification gate passes.

The general gate is:

```text
┌─────────────────────────────────────┐
│ New tests                           │
│                 PASS                │
├─────────────────────────────────────┤
│ Existing tests                      │
│                 PASS                │
├─────────────────────────────────────┤
│ Ruff                                │
│                 CLEAN               │
├─────────────────────────────────────┤
│ mypy                                │
│                 CLEAN               │
├─────────────────────────────────────┤
│ Existing emulator behavior          │
│                 UNCHANGED           │
└─────────────────────────────────────┘
```

For ISA changes:

```text
ISA tests
Emulator tests
Assembler tests
```

must all pass.

For GUI changes:

```text
Assembler tests
Controller tests
GUI tests
Existing application tests
```

must pass.

---

## 24. Git and Change Management

Implementation should be performed in small, logically isolated commits.

A possible progression is:

```text
assembler: add foundation
assembler: add target selection
isa: expose assembler instruction information
assembler: add lexer
assembler: add parser
assembler: add AST
assembler: add semantic analysis
assembler: add symbol table
assembler: add code generation
assembler: add listing generation
assembler: add cross-reference generation
assembler: add public API
controller: integrate assembler
controller: route assembler diagnostics
gui: add assembler dialog
gui: add assembler output controls
controller: add assemble-and-load
assembler: add regression ROM suite
```

The exact commit sequence is not mandatory.

Each commit should represent a coherent, testable change.

---

## 25. Proposed Source Structure

The final assembler structure is expected to evolve during implementation.

The current intended structure is:

```text
src/assembler/
├── __init__.py
├── assembler.py
├── request.py
├── result.py
├── options.py
├── target.py
├── targets.py
├── diagnostics.py
├── token.py
├── lexer.py
├── ast.py
├── parser.py
├── symbols.py
├── semantic.py
├── codegen.py
├── listing.py
└── cross_reference.py
```

This is a logical target structure, not a requirement that every module must exist.

Modules should only be created when they represent a meaningful separation of responsibility.

The actual implementation should follow the existing project's conventions.

---

## 26. Proposed Test Structure

The intended test structure is:

```text
tests/assembler/
├── test_assembler.py
├── test_request.py
├── test_result.py
├── test_options.py
├── test_target.py
├── test_diagnostics.py
├── test_token.py
├── test_lexer.py
├── test_ast.py
├── test_parser.py
├── test_symbols.py
├── test_semantic.py
├── test_codegen.py
├── test_listing.py
├── test_cross_reference.py
└── roms/
```

The exact structure may be adjusted to match the project's existing testing conventions.

---

## 27. Documentation Changes During Development

The implementation should be accompanied by updates to the relevant documentation.

The principal assembler documents are:

- `doc/assembler/assembler_design.md`
- `doc/assembler/assembler_gui_integration.md`
- `doc/assembler/assembler_public_api.md`
- `doc/assembler/assembler_development_plan.md`

The Architecture Decision Records should only be changed when an actual architectural decision changes.

The SRDS should only be changed when the system requirements or architecture materially change.

Implementation details should normally be documented in the assembler design and development documents rather than repeatedly modifying the ADRs.

---

## 28. Definition of Completion

The assembler implementation is complete when all of the following are true:

1. The assembler is located under `src/assembler`.
2. Target architecture selection works from either a source directive or external selection.
3. Target selection occurs before architecture-dependent parsing.
4. Supported architecture grammars parse correctly.
5. The AST is generated correctly.
6. Semantic analysis resolves symbols and validates the program.
7. Machine code is generated correctly.
8. All supported instruction encodings are tested.
9. Binary ROM images can be generated.
10. Listing generation works.
11. Cross-reference generation works.
12. Listing generation is configurable.
13. Cross-reference generation is configurable.
14. Diagnostics contain useful source information.
15. The public assembler API is stable.
16. The Controller can invoke the assembler.
17. Assembler diagnostics can be routed to the assembler diagnostics view.
18. The assembler dialog is available from the existing application.
19. ROM images can be saved to files.
20. Listing files can be saved.
21. Cross-reference files can be saved.
22. Successfully assembled ROMs can be loaded into the existing emulator.
23. Failed assembly does not replace the currently loaded ROM.
24. Regression ROMs pass.
25. Existing emulator behavior remains unchanged.
26. Ruff is clean.
27. mypy is clean.
28. The complete application workflow is tested.

---

## 29. Final Development Sequence

The complete sequence is:

```text
01  Establish baseline
        │
02  Assembler foundation
        │
03  ISA integration
        │
04  Target architecture selection
        │
05  Lexer
        │
06  Parser and AST
        │
07  Semantic analysis
        │
08  Code generation
        │
09  Output products
        │
10  Public assembler API
        │
11  Controller integration
        │
12  Diagnostic routing
        │
13  Assembler GUI
        │
14  Save-output operations
        │
15  Assemble & Load
        │
16  Regression ROM suite
        │
17  Full application integration
        │
18  Final cleanup and documentation
```

At every point:

```text
┌─────────────────────┐
│ Implement one step  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Add/update tests    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Existing tests PASS │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Ruff + mypy clean   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Verify behavior     │
└──────────┬──────────┘
           │
           ▼
       Next step
```

The central development principle is:

> **Build the assembler independently, prove each layer independently, and integrate it into the existing application only after the corresponding layer is stable.**
