# Assembler GUI Integration

**Author:** Michael Dlubatz

**Date:** 2026-10-02

**Status:** Current implementation

---

## 1. Purpose

This document describes the current integration of the CHIP-8 assembler into the
existing emulator application.

The assembler remains an independent subsystem under:

```text
src/assembler/
```

The integration preserves the existing `Chip8Controller` application boundary. The GUI
does not call parser, semantic-analysis, code-generation, or listing internals directly.

---

## 2. Architectural Principle

The Controller coordinates the GUI, assembler, emulator, and output files:

```text
GUI
 │
 ▼
Chip8Controller
 │
 ├── TargetSelector
 │
 ├── Assembler
 │
 ├── Emulator / Chip8Machine
 │
 └── Output files
```

The assembler does not depend on PyQt6, `MainWindow`, `Chip8Controller`, or
`Chip8Machine`.

The assembler also does not select the emulator machine's ISA. The machine architecture
is selected independently by the application's global configuration.

---

## 3. Current Assembly Flow

The current Controller workflow is:

```text
Assembler GUI
      │
      │ source + external target + AssemblyOptions
      ▼
Chip8Controller.assemble_source()
      │
      ├── clear assembler diagnostics
      ├── ensure/save source file
      ├── TargetSelector.select(source, external_target)
      │
      │       ┌───────────────────────────────┐
      │       │ source TARGET takes precedence│
      │       │ over external target          │
      │       └───────────────────────────────┘
      │
      ├── create Assembler(selected_target)
      ├── Assembler.assemble(source, options)
      │
      ▼
AssemblyResult
      │
      ├── diagnostics
      ├── binary_image
      └── listing
      │
      ▼
Chip8Controller
      ├── save ROM image
      └── save listing when generated
```

`TargetSelector` is an application-level component. It is deliberately outside the
`Assembler`.

---

## 4. Target Selection

The GUI supplies an externally selected `Target` to the Controller. The Controller uses
`TargetSelector` to determine the effective assembler target.

The rules are:

| Source | External target | Result |
|---|---|---|
| Contains one valid `TARGET` directive | Any | Source target is selected |
| No `TARGET` directive | Valid external target | External target is selected |
| No `TARGET` directive | `None` | Assembly is rejected with a target-selection diagnostic |
| Multiple `TARGET` directives | Any | Assembly is rejected |
| Unknown target name | Any | Assembly is rejected |

A selected assembler target determines which `Assembler` instance and ISA are supplied
to the assembly operation.

This target selection **does not change the ISA of `Chip8Machine`**. Emulator machine
architecture is selected independently by the application's machine configuration.

---

## 5. Source and File Ownership

The GUI supplies the current source text to the Controller.

The Controller owns assembler source-file association and output-file association. The
assembler itself does not read or write source, ROM, or listing files.

On a successful source save, the Controller associates:

```text
source.asm  → source.ch8
           → source.lst
```

The output files are written only after successful assembly. A failed assembly does not
overwrite an existing ROM image.

---

## 6. Assembly Options

The GUI can request optional output products through `AssemblyOptions`:

```python
AssemblyOptions(
    generate_listing=False,
    generate_cross_reference=False,
)
```

Binary generation is always part of a successful assembly.

Listing generation is optional. Cross-reference generation is subordinate to listing
generation: when enabled, cross-reference information is appended to the listing.
There is no separate cross-reference result or cross-reference file in the current
implementation.

---

## 7. Diagnostics

Assembler diagnostics use a dedicated `AssemblerDiagnosticsReporter` and remain separate
from ordinary application diagnostics.

Assembler diagnostics include source locations where applicable. The Controller passes
the resulting `AssemblyResult.diagnostics` to the assembler dialog.

The assembler dialog displays diagnostic messages and supports navigation to the source
location.

When a diagnostic has a source location, activating it:

1. locates the corresponding source line and column;
2. positions a `QTextCursor` there;
3. selects the token under the cursor;
4. focuses the source editor; and
5. ensures the cursor/selection is visible.

Both keyboard activation and mouse double-click activation are supported.

The source editor's VI-mode implementation is not involved in diagnostic navigation,
so navigation works in VI-disabled mode and in both VI insert and normal modes.

---

## 8. Output Products

The current assembler produces these output products:

1. binary ROM image (`AssemblyResult.binary_image`);
2. optional listing text (`AssemblyResult.listing`); and
3. optional cross-reference information appended to the listing.

The current `AssemblyResult` does not expose a separate symbol-table, source-mapping,
or cross-reference field. Symbols and references are internal assembler data used during
semantic analysis, code generation, and listing generation.

---

## 9. Separation from the Emulator

The assembler is not part of `Chip8Machine` and is not invoked by the emulator execution
engine.

The Controller coordinates the relationship between assembly and emulator operation.

This allows the assembler target selection to remain independent from the machine ISA
configuration.

---

## 10. Future Architecture Work

The project contains separate proposed design documents for a generic parser framework,
architecture definitions, and architecture plug-ins for CHIP-8 variants.

Those designs are not prerequisites for the current COSMAC assembler integration and are
not claimed as implemented by this document.
