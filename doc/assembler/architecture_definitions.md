# Architecture Definitions — Superseded Proposal

**Status:** Rejected design proposal; superseded by ADR-014.

This document is retained as historical design material. The `ArchitectureDefinition` model described here is not part of the accepted assembler architecture and must not be treated as an implementation requirement.

ADR-014 selects a shared `Parser` base class with concrete architecture-specific parser subclasses. The selected ISA exposes assembler mnemonic knowledge through `assembler_mnemonics()`. The Controller supplies the matching ISA and parser to `Assembler`; the parser uses the ISA abstraction rather than a separate architecture-definition object.

The accepted responsibility boundary is:

- **Parser:** common syntax and target-specific mnemonic recognition.
- **ISA:** authoritative assembler mnemonic knowledge and instruction-set operations.
- **Semantic analysis:** operand-signature/type validation, symbol resolution, expression evaluation, and range checks.
- **Controller:** target selection and construction of the matching ISA/parser pair.
- **Machine:** retains its independently configured ISA; assembler target selection does not change it.

The older proposal's grammar-definition object, generic grammar-driven parser framework, and architecture-definition plug-in model are rejected. For the accepted design, see `parser_framework.md` and ADR-014.
