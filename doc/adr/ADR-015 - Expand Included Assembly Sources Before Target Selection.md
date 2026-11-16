# ADR-015 — Expand Included Assembly Sources Before Target Selection

**Author:** Michael Dlubatz

**Date:** 2026-11-05

**Status:** Accepted

**Related ADRs:** ADR-009, ADR-011, ADR-012, ADR-014

---

## Context

The assembler currently receives source text and an already selected ISA/parser pair. The Controller owns source-file association, target selection, and assembler construction. Supporting source files through an `INCLUDE` directive requires file access and recursive source expansion, but must not move file I/O into `Assembler` or introduce architecture-specific include handling into the parser hierarchy.

Target selection must inspect the complete source program, including included files. The existing language rule permits only one `TARGET` declaration. This restriction applies to the complete expanded source: a second declaration is an error even when it names the same target.

Included source also introduces a need to retain the physical origin of each expanded source line so that diagnostics can identify the file and line where the source was written. At the same time, existing code-generation and listing logic uses line numbers in the expanded source stream.

The application requires a configurable include search directory. When no global include directory is configured, include paths should be relative to the file containing the directive. A configured directory must be authoritative rather than silently falling back to another directory.

## Decision

1. The Controller coordinates source preprocessing before target selection and before construction of the target-specific ISA, parser, and `Assembler`.
2. INCLUDE processing is architecture-independent and is not implemented separately by concrete parsers or assembler variants.
3. The accepted directive form is `INCLUDE "filename"`. The filename is double-quoted, and the directive occupies its own source line. The directive may appear wherever a source-level directive may appear. Its expanded contents replace the directive at that exact position.
4. Included files may themselves contain INCLUDE directives. Expansion is recursive and preserves source order.
5. Include path resolution follows these rules:
   - An absolute filename in an INCLUDE directive is used directly, regardless of the configured `IncludePath`.
   - An absolute `IncludePath` is used directly as the include root for relative INCLUDE filenames.
   - A relative `IncludePath` is resolved relative to the directory of the main assembly source file.
   - If `IncludePath` is empty, an include filename is resolved relative to the directory of the file containing that INCLUDE directive.
   - When `IncludePath` is non-empty, every relative INCLUDE filename is resolved against that configured directory, including nested includes. There is no fallback to the including file's directory.
6. Missing include files, malformed INCLUDE directives, and circular inclusion are errors. Circular inclusion detection uses the resolved file identity and reports the inclusion chain or relevant source locations.
7. The expanded source retains provenance for each line: the expanded-source line used by existing assembly/listing logic, the originating filename, the original source line, and the column.
8. Target discovery examines the complete expanded source before selecting the assembler. Exactly one source `TARGET` declaration is permitted. Any second declaration is an error, regardless of whether it names the same target. If there is no source declaration, the existing external-target/default-selection behaviour remains unchanged.
9. The Controller obtains the configured include directory from `EmulatorConfiguration.assembler_include_path`. The setting is persisted under `assembler/include_path` and is edited through the assembler dialog.
10. The `Assembler` continues to receive source text, options, diagnostics, an ISA, and an injected parser. It does not open source files or resolve INCLUDE directives.
11. The selected ISA/parser pair remains independent of the ISA configured on `Chip8Machine`. No `ArchitectureDefinition` abstraction is introduced.

## Rationale

Preprocessing before target selection ensures that a TARGET declaration in any included file participates in the same validation as a declaration in the main file. Keeping preprocessing in the Controller preserves the existing application boundary and the public assembler API's file-I/O independence.

A single configured include root gives deterministic behaviour for projects that share include files. The empty-setting rule remains convenient for self-contained source trees because nested includes are resolved relative to the file that contains each directive.

Separating expanded line numbers from original source provenance preserves existing code-generation and listing assumptions while making diagnostics useful for included files.

## Consequences

### Positive

- INCLUDE works consistently for every assembler target.
- Target selection sees the complete source program.
- The existing single-TARGET rule is preserved and applies across file boundaries.
- The assembler and parser remain independent of filesystem access.
- Nested include diagnostics can identify their original files and lines.
- Include search behaviour is deterministic and configurable.

### Negative

- The Controller's assembly workflow gains a source-preprocessing responsibility.
- Source-location data must distinguish expanded positions from original file positions.
- Include processing must handle filesystem errors, recursive expansion, and cycle detection.
- The source editor initially remains associated with the main file; diagnostics originating in included files may require future GUI navigation support to open those files directly.

## Alternatives Considered

### INCLUDE handling inside each concrete parser

Rejected. It would duplicate filesystem and recursive expansion behaviour across architecture-specific parsers and would occur too late for target discovery in included files.

### INCLUDE handling inside `Assembler`

Rejected. The current public API deliberately keeps source-file ownership and target selection in the Controller. Making `Assembler` read files would blur that boundary and make target selection occur before included TARGET declarations could be validated.

### Resolve nested includes relative to the including file even when IncludePath is configured

Rejected. A non-empty IncludePath is the configured include root and must be authoritative. Silent per-file fallback would make include resolution dependent on incidental file layout.

### Permit repeated identical TARGET declarations

Rejected. The existing language rule permits only one TARGET declaration. The rule applies to the expanded source, and identical repeated declarations are still multiple declarations.

## Related Documents

- SRDS, Chapter 7 — Assembler
- `assembler/assembler_grammar.md`
- `assembler/assembler_design.md`
- `assembler/assembler_gui_integration.md`
- `assembler/semantic_analysis.md`
