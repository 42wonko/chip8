# Architectural Decision Records

This directory contains the Architectural Decision Records (ADRs) for
the CHIP-8 Emulator project.

An ADR documents an important architectural decision together with the
reasoning that led to it.

Unlike the Software Requirements and Design Specification (SRDS), which
defines **what** the software shall do, an ADR explains **why** a
particular architectural decision was made.

Each ADR is immutable once accepted.

If a decision changes, a new ADR shall be created that supersedes the
previous one.

## ADR Format

Every ADR follows the same structure.

- Title
- Status
- Context
- Alternatives Considered
- Decision
- Rationale
- Consequences

## Naming

ADRs are numbered sequentially.

Example

```
ADR-001-overall-architecture.md
```

The number never changes.

The title may evolve for clarity.

## Status Values

- Proposed
- Accepted
- Superseded
- Deprecated

## Accepted decisions

- **ADR-014** — Use Inherited Architecture-Specific Parsers (supersedes ADR-010 and the parser-framework/language-definition portions of ADR-013).

## Proposed decisions

- **ADR-015** — Expand Included Assembly Sources Before Target Selection (proposed; records architecture-independent INCLUDE expansion, path resolution, source provenance, and the single-TARGET rule across expanded source).
