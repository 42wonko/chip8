# ADR-014 — Architecture-Specific Assembler Parsers

**Status:** Accepted
**Date:** 2026-10-08
**Supersedes:** ADR-010
**Related:** ADR-011, ADR-012, ADR-013

---

## Context

The assembler was originally intended to support multiple CHIP-8 architectures with architecture-dependent parsing. The previous design recorded in ADR-010 proposed a generic parser framework driven by an `ArchitectureDefinition`.

The current implementation evolved differently.

The Controller already performs target discovery and selects the effective assembler target before constructing the `Assembler`. The selected target is therefore already known before parsing begins. The Controller also selects the instruction-set architecture (ISA) used by the assembler.

The current parser, however, is architecture-independent. It accepts any identifier-shaped mnemonic as an instruction and leaves instruction recognition to semantic analysis. This means that the parser does not currently enforce the language of the selected architecture.

This is inconsistent with the intended architecture-dependent assembler design.

The current ISA abstraction already provides architecture-specific assembler knowledge, including operand signatures, instruction sizes, assembler operands, and instruction creation. The ISA therefore represents an appropriate source of assembler instruction knowledge.

The machine architecture used by `Chip8Machine` is a separate concern. Selecting an assembler target must not change the machine's ISA or alter the `Chip8Machine` interface.

The previous `ArchitectureDefinition` proposal is unnecessarily broad for the architecture now being adopted. Introducing such an abstraction would add another representation of architecture knowledge without being required to achieve architecture-specific parsing.

---

## Decision

The assembler shall use **architecture-specific parser classes**.

The parser architecture shall use inheritance:

```text
Parser
  └── ClassicParser
```

`Parser` provides the common parsing machinery and grammar constructs. `ClassicParser` provides the architecture-specific instruction recognition required by the COSMAC assembler language.

Future architectures may introduce additional parser subclasses as required.

The parser shall receive the selected ISA through its constructor so that architecture-specific instruction recognition can use the same ISA instance used by the assembler.

The Controller shall select the matching ISA and parser for the selected assembler target.

The resulting assembly flow is:

```text
Source
  │
  ▼
TargetSelector
  │
  ▼
Target
  │
  ├───────────────┐
  ▼               ▼
ISA          Parser instance
  │               │
  │          ClassicParser
  │               │
  └───────┬───────┘
          ▼
       Assembler
          │
        Lexer
          │
        Tokens
          │
          ▼
        Parser
          │
          ▼
          AST
          │
          ▼
   Semantic analysis
          │
          ▼
    Code generation
```

The `Assembler` shall receive a complete parser instance rather than constructing the parser itself.

Conceptually:

```python
Assembler(
    diagnostics,
    isa,
    parser,
)
```

The parser shall be reusable for multiple assembly operations. The parser shall therefore accept its token stream separately from construction and reset its per-source parsing state when a new token stream is supplied.

Conceptually:

```python
parser.set_tokens(tokens)
parser.parse()
```

---

## ISA and mnemonic knowledge

The parser shall not depend directly on `InstructionId` or on the internal representation of ISA instructions.

`InstructionId` represents machine-level instruction identities and is not a one-to-one representation of assembler mnemonics. It is therefore not an appropriate parser-facing abstraction.

The `InstructionSetArchitecture` interface shall instead expose the assembler mnemonics supported by the selected architecture.

The intended interface is:

```python
def assembler_mnemonics(self) -> frozenset[str]:
    ...
```

The concrete ISA implementation shall provide the architecture-specific mnemonic set.

The parser shall use this ISA API to determine whether an identifier is a valid instruction mnemonic for the selected architecture.

This keeps assembler-language knowledge inside the ISA implementation and prevents the parser from maintaining a duplicate list of architecture instructions.

---

## Responsibility boundaries

The architecture-specific parser is responsible for **architecture-level syntax recognition**.

In particular, it shall determine whether an instruction mnemonic belongs to the selected assembler language.

The parser shall continue to provide the common syntactic machinery required to parse:

* labels;
* expressions;
* literals;
* identifiers;
* parenthesized expressions;
* indirect expressions;
* operands;
* source locations;
* directives supported by the current assembler;
* parser diagnostics.

The parser is not responsible for determining whether a particular combination of operands is valid for an otherwise valid mnemonic.

Operand validation remains a semantic-analysis responsibility.

Semantic analysis shall continue to use the existing ISA API:

```python
isa.assembler_operand_signatures(
    mnemonic,
    operand_count,
)
```

This preserves the existing separation:

```text
Parser
  → Is this mnemonic part of the selected architecture?

Semantic analysis
  → Are these operands valid for this mnemonic?

Code generation
  → How is this valid instruction encoded?
```

Semantic validation shall initially remain in place even after architecture-specific parser recognition is introduced. This provides defensive validation and avoids unnecessarily changing established semantic-analysis responsibilities.

---

## Parser inheritance

The existing parser shall be treated as the source of the common parser functionality.

The first implementation step shall extract the current parser into the base/subclass arrangement without intentionally changing its existing parsing behaviour.

The base `Parser` shall contain common parsing mechanisms.

`ClassicParser` shall supply the architecture-specific instruction recognition.

The architecture-specific parser should not duplicate the generic operand parsing implementation merely because instruction recognition becomes architecture-specific.

The exact inheritance hierarchy for future architectures is deliberately not fixed beyond the initial:

```text
Parser
  └── ClassicParser
```

Future parser relationships shall be decided when an additional architecture is actually introduced.

---

## Parser instance injection

The `Assembler` shall receive a parser instance rather than a parser factory.

This makes the parser itself the concrete representation of the selected assembler language while keeping parser construction outside the assembly engine.

The Controller is responsible for constructing a matching ISA and parser and supplying them to the assembler.

The same ISA instance shall be supplied to both the parser and assembler.

This prevents the parser and semantic/code-generation stages from accidentally operating against different architecture descriptions.

---

## Target selection and emulator separation

Target selection remains an application-level Controller responsibility.

The selected assembler target determines:

* the assembler ISA;
* the assembler parser;
* the architecture-specific assembler language.

It does **not** determine or modify the ISA used by `Chip8Machine`.

The `Chip8Machine` interface shall remain unchanged by this decision.

The assembler architecture and emulator architecture therefore remain separate:

```text
Assembler target
    │
    ├── assembler ISA
    └── assembler parser


Emulator configuration
    │
    └── Chip8Machine ISA
```

---

## Rejected alternatives

### ArchitectureDefinition

The `ArchitectureDefinition` abstraction proposed by ADR-010 is rejected.

Architecture-specific parsing does not require a separate generic architecture-definition object. The existing ISA abstraction already owns architecture-specific instruction knowledge and can expose the limited assembler-facing information required by the parser.

Introducing `ArchitectureDefinition` would add another architectural abstraction and another potential source of duplicated instruction knowledge without providing a necessary benefit at this stage.

### Generic parser driven by ArchitectureDefinition

The generic grammar-driven parser framework described by ADR-010 is rejected as the implementation direction.

The parser shall instead use normal class inheritance, with architecture-specific parser subclasses.

### Parser-side InstructionId knowledge

The parser shall not import or inspect `InstructionId`.

Machine-level instruction identifiers do not correspond one-to-one with assembler mnemonics and therefore do not form an appropriate parser vocabulary.

### Duplicated mnemonic lists in each parser

A parser shall not contain its own independent hard-coded copy of the architecture's assembler mnemonic vocabulary.

The parser obtains this information through the ISA abstraction.

### Architecture changes to Chip8Machine

The assembler architecture change shall not be used as a reason to modify the `Chip8Machine` interface or its architecture-selection mechanism.

---

## Consequences

### Positive consequences

* The parser becomes explicitly architecture-aware as originally intended.
* Invalid instruction mnemonics can be rejected during parsing rather than being accepted as generic identifiers and rejected later.
* The Controller has a clear responsibility for selecting the matching ISA and parser.
* The parser does not need to know about `InstructionId`.
* The ISA remains the source of architecture-specific instruction knowledge.
* The semantic-analysis layer retains responsibility for operand-form validation.
* Parser construction is separated from the `Assembler`.
* The same ISA instance can be shared by parsing, semantic analysis, and code generation.
* Additional architectures can introduce architecture-specific parser classes without changing `Chip8Machine`.

### Negative consequences

* The parser becomes dependent on the ISA abstraction.
* The `Assembler` constructor gains a parser dependency.
* The existing parser API must change to support parser-instance injection and token-stream reset.
* Parser state must be managed carefully when a parser instance is reused.
* Future architectures may require additional parser subclasses and potentially additional architecture-specific parser behaviour.
* Some existing parser tests will need to be updated because parser construction and instruction recognition will change.

---

## Migration strategy

The change shall be implemented incrementally.

### Step 1 — Establish the parser hierarchy

Extract the existing parser implementation into the agreed `Parser` / `ClassicParser` structure without intentionally changing parsing behaviour.

### Step 2 — Add ISA mnemonic knowledge

Add the assembler-mnemonic API to the ISA abstraction and implement it for the current COSMAC ISA.

### Step 3 — Make `ClassicParser` architecture-aware

Inject the ISA into `ClassicParser` and use the ISA mnemonic API when recognizing instructions.

### Step 4 — Inject the parser into `Assembler`

Change the `Assembler` to receive a parser instance and provide the token stream to it for each assembly operation.

### Step 5 — Select matching ISA and parser in the Controller

Extend the existing target-based assembler construction so that the selected target determines both the ISA and parser.

### Step 6 — Add and update tests

Tests shall verify at minimum:

* valid COSMAC mnemonics are accepted;
* unknown mnemonics are rejected by the parser;
* the selected ISA is used by the parser;
* parser state does not leak between successive token streams;
* the Controller supplies matching ISA and parser instances;
* existing valid assembly behaviour remains unchanged;
* semantic operand validation remains effective.

### Step 7 — Documentation reconciliation

Current implementation documentation shall be updated once the implementation is complete.

The existing ADRs shall not be modified. ADR-010 remains as a historical record of the superseded decision.

---

## Relationship to previous decisions

This ADR supersedes **ADR-010** because the implementation direction for architecture-specific parsing has changed.

ADR-010 remains unchanged as a historical record.

This decision does not invalidate the broader objective of separating architecture-specific assembler behaviour from common assembler infrastructure. Where ADR-013 addresses that broader separation, it remains applicable unless explicitly contradicted by this ADR.

ADR-011 and ADR-012 remain unaffected.

---

## Implementation status

At acceptance of this ADR:

* target selection in the Controller already exists;
* target-specific ISA selection already exists for the implemented COSMAC target;
* the current parser is still architecture-independent;
* the current parser is still constructed internally by `Assembler`;
* assembler mnemonic exposure through the ISA is not yet implemented;
* architecture-specific parser classes are not yet implemented.

This ADR therefore records the **accepted target architecture for the next implementation phase**, not a claim that all components described above already exist.

