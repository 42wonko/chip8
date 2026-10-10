# Assembler Public API

**Author:** Michael Dlubatz

**Date:** 2026-10-02

**Status:** Current implementation

---

# 1. Purpose

This document defines the public interface of the currently implemented CHIP-8 assembler.

The assembler is used by the application Controller and is independently testable. The
assembler implementation itself has no dependency on PyQt6, the GUI, or `Chip8Machine`.

The architecture described here reflects the current implementation. The parser uses the shared `Parser` base and the concrete parser selected by the Controller. The target-specific parser/ISA design is described in ADR-014.

---

# 2. Design Goals

The current API shall:

- separate assembly from GUI code
- receive the target instruction-set architecture from the caller
- support assembler diagnostics with source locations
- provide configurable listing and cross-reference generation
- return generated binary data and diagnostics through a stable result object
- remain independently testable

Target discovery and target selection are application-level responsibilities of
`Chip8Controller`. The `Assembler` receives the already selected ISA.

---

# 3. Public Components

The principal public assembler interfaces are:

```text
Assembler
AssemblyOptions
AssemblyResult
AssemblerDiagnosticsReporter
```

The assembler also consumes the project-wide ISA abstraction:

```text
InstructionSetArchitecture
```

Supporting classes such as the lexer, parser, AST, symbol table, semantic-analysis
components, code generator, and listing generator are implementation components and
are not part of the application-level assembler boundary.

---

# 4. Assembler

The assembler represents the assembly engine for one selected instruction-set
architecture.

```python
class Assembler:
```

## Construction

```python
Assembler(
    diagnostics: AssemblerDiagnosticsReporter,
    isa: InstructionSetArchitecture,
    parser: Parser,
)
```

`diagnostics` receives assembler progress and diagnostic messages.

`isa` supplies instruction-set and address-space information used during assembly. `parser` is the parser instance selected for the same target. The Controller creates both dependencies and supplies the same ISA instance to the parser and assembler.

The assembler does not select the emulator's `Chip8Machine` architecture and does not
interact with the machine.

---

## Public Methods

### assemble()

```python
assemble(
    source: str,
    options: AssemblyOptions | None = None,
) -> AssemblyResult
```

Assembles the supplied source text using the ISA supplied at construction time.

If `options` is omitted, the default `AssemblyOptions` are used.

The method does not read source files and does not write output files. File ownership
belongs to the Controller.

---

# 5. AssemblyOptions

`AssemblyOptions` controls optional assembler output products.

```python
@dataclass(frozen=True, slots=True)
class AssemblyOptions:
    generate_listing: bool = False
    generate_cross_reference: bool = False
```

Binary generation is always performed for a successful assembly. Listing generation
is optional. Cross-reference information is generated only as part of a listing, so
`generate_cross_reference=True` has no independent output when listing generation is
disabled.

---

# 6. AssemblyResult

The result returned by `Assembler.assemble()` is:

```python
@dataclass(slots=True)
class AssemblyResult:
    success: bool
    diagnostics: tuple[Diagnostic, ...] = ()
    binary_image: bytes | None = None
    listing: str | None = None
```

### success

`True` when assembly completed successfully. `False` when assembly failed.

### diagnostics

Structured assembler diagnostics. Error diagnostics retain their source locations so
that the Controller and GUI can navigate back to the corresponding source text.

### binary_image

Generated machine-code bytes for a successful assembly.

### listing

The generated listing text when listing generation was requested. Otherwise `None`.

Cross-reference information is appended to this listing when requested. It is not a
separate `AssemblyResult` field or separate output product in the current implementation.

---

# 7. Assembler Diagnostics

Assembler diagnostics use the existing diagnostics infrastructure through a dedicated
assembler reporter:

```python
AssemblerDiagnosticsReporter
```

The reporter supports:

```python
info(message, location=None)
warning(message, location=None)
error(message, location=None)
```

Assembler diagnostics carry a `SourceLocation` when the message refers to a specific
source position. They are retained in the `AssemblyResult` as well as reported through
the assembler diagnostics collection used by the GUI.

The current `AssemblerDiagnostic` contains:

```text
severity
source
message
location
```

The `location` is a source line/column location; a filename is not currently stored in
`AssemblerDiagnostic` because the Controller owns the current assembler source file.

---

# 8. Assembly Workflow

The application-level workflow is:

```text
Assembler GUI
     │
     ▼
Chip8Controller
     │
     ├── select target
     ├── create Assembler with selected ISA
     │
     ▼
Assembler
     │
     ├── lex
     ├── parse
     ├── collect symbols/references
     ├── resolve instructions and operands
     ├── generate binary image
     └── optionally generate listing/cross-reference
     │
     ▼
AssemblyResult
     │
     ▼
Chip8Controller
     ├── save ROM
     └── save listing
```

The Controller, not the `Assembler`, owns file I/O and application-level target selection.

---

# 9. Thread Safety

The assembler makes no guarantee of concurrent use. Separate assembler instances should
be used if concurrent assembly is required in the future.

---

# 10. Error Handling

Expected assembly failures are represented by `AssemblyResult(success=False)` and
assembler diagnostics.

The current implementation catches lexer, parser, and semantic-analysis errors and
returns their diagnostics with source locations. Unexpected internal errors are not
part of the normal assembler error-reporting contract.
