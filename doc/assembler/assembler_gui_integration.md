# Assembler GUI Integration

**Author:** Michael Dlubatz

**Date:** 2026-08-13

**Status:** Proposed

---

## 1. Purpose

This document defines the strategy for integrating the assembler into the existing CHIP-8 emulator and debugger application.

The assembler is implemented as an independent subsystem under:

```text
src/assembler/
```

The goal of the integration is to make the assembler available through the existing application and GUI without coupling the assembler implementation to Qt, the GUI, or the emulator's internal state.

The integration must preserve the existing application architecture, in particular the role of `Chip8Controller` as the component coordinating the GUI, emulator, diagnostics, and other application subsystems.

---

## 2. Scope

This document covers:

- integration of the assembler into the existing application
- responsibilities of the GUI
- responsibilities of the Controller
- communication between the GUI and assembler
- communication between the assembler and emulator
- target architecture selection
- assembly requests
- assembly results
- assembly output products
- output-product configuration
- saving generated output to files
- loading generated ROM images into the emulator
- diagnostic data flow
- dedicated assembler diagnostics
- future integration with the debugger
- ownership and lifetime of assembly-related data

This document does **not** define:

- the internal parser implementation
- the assembly language grammar
- the AST structure
- semantic analysis algorithms
- machine-code encoding rules
- the detailed visual design of the source editor

Those subjects are defined by the other assembler design documents.

---

## 3. Architectural Principle

The assembler is a subsystem of the existing application, not a separate application.

The GUI must not communicate directly with the assembler implementation.

The Controller provides the application-level boundary between the GUI and the assembler.

The basic relationship is:

```text
GUI
 │
 ▼
Chip8Controller
 │
 ▼
Assembler
```

The assembler returns its result to the Controller:

```text
GUI
 │
 ▼
Chip8Controller
 │
 ▼
Assembler
 │
 ▼
AssemblyResult
 │
 ▼
Chip8Controller
 │
 ├──► GUI
 │
 ├──► Emulator
 │
 └──► Output Files
```

This preserves the existing Controller-based application architecture.

---

## 4. Existing Application Architecture

The existing application uses `Chip8Controller` to coordinate the major application subsystems.

The relevant architecture is:

```text
                         Chip8Controller
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
          MainWindow        Emulator         Diagnostics
                               │
                               ▼
                         Chip8Machine
```

The assembler is added as another subsystem coordinated by the Controller:

```text
                         Chip8Controller
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
       MainWindow           Emulator            Assembler
                                                    │
                                                    ▼
                                            AssemblyResult
```

The assembler does not become part of `Chip8Machine`.

Likewise, `Chip8Machine` does not invoke the assembler.

The Controller coordinates interaction between them.

---

## 5. Assembler Boundary

The assembler exposes an application-independent interface.

The assembler must not depend on:

- PyQt6
- `MainWindow`
- GUI models
- `Chip8Controller`
- `Chip8Machine`
- debugger implementation
- emulator execution state

The assembler receives source and assembly configuration and produces an assembly result.

Conceptually:

```text
AssemblyRequest
       │
       ▼
   Assembler
       │
       ▼
AssemblyResult
```

The exact Python class and method names are implementation details and are defined by `assembler_public_api.md`.

---

## 6. Assembly Request

The Controller creates an assembly request based on the current GUI state.

Conceptually, an assembly request contains:

```text
AssemblyRequest
├── source
├── source_name
├── external_target
└── assembly_options
```

### 6.1 Source

`source` contains the complete assembly source currently being assembled.

The assembler does not obtain the source directly from the GUI.

The GUI provides the source to the Controller, and the Controller places it into the assembly request.

### 6.2 Source Name

`source_name` identifies the source for diagnostics and other user-visible information.

It may be:

- a filename
- a document name
- an editor buffer name
- another suitable source identifier

The assembler should not require the source to exist as a file.

### 6.3 External Target

`external_target` contains the target architecture selected outside the source.

It is used when the source contains no target directive.

The target-selection rules are:

```text
                 Source
                   │
                   ▼
            Target Discovery
                   │
             ┌─────┴─────┐
             │           │
       Target found   No target
             │           │
             ▼           ▼
       Source target   External target
             │           │
             └─────┬─────┘
                   │
                   ▼
            Effective Target
```

The assembler must therefore be able to receive an externally selected target even when the source itself does not contain a target directive.

---

## 7. Target Selection in the GUI

The GUI must provide a mechanism for selecting the target architecture.

A combo box or drop-down list is appropriate.

Conceptually:

```text
Target: [ COSMAC CHIP-8 ▼ ]
```

The exact visual design is not specified by this document.

The important architectural requirement is that the selected target is application state and is passed to the Controller when an assembly request is created.

The GUI does not decide whether the source target or externally selected target is ultimately effective.

That decision belongs to the assembler's target-selection logic.

---

## 8. Source Target Directive

A source file may contain a target directive.

For example:

```assembly
TARGET XO-CHIP
```

When a target directive is present, the source-specified target is used.

The GUI's externally selected target remains available as the fallback target when no target directive is present.

The assembler therefore handles the following cases:

| Source | External Target | Effective Target |
|---|---|---|
| Contains target directive | Any | Source target |
| No target directive | Selected | External target |
| No target directive | None | Assembly cannot proceed |

The last case must produce a diagnostic explaining that no target architecture is available.

---

## 9. Assembly Processing Flow

The complete application-level flow is:

```text
User
 │
 ▼
Assembler GUI
 │
 │ source + selected target + output options
 ▼
Chip8Controller
 │
 │ AssemblyRequest
 ▼
Assembler
 │
 ├── Target discovery
 │
 ├── Target selection
 │
 ├── Parsing
 │
 ├── AST construction
 │
 ├── Semantic analysis
 │
 └── Code generation
 │
 ▼
AssemblyResult
 │
 ▼
Chip8Controller
 │
 ├──► GUI diagnostics
 │
 ├──► GUI output information
 │
 ├──► Emulator
 │
 └──► Output files
```

The assembler performs no GUI operations during this process.

---

## 10. Assembly Output Products

The assembler can produce several distinct output products.

The primary output products are:

1. **Binary ROM image**
2. **Listing file**
3. **Cross-reference information**

The assembler also produces metadata required by the application and by the output products, including:

- symbols
- source mappings
- diagnostics

These metadata products are distinct from the generated files.

Conceptually:

```text
                         Assembler
                             │
                             ▼
                      Assembly Result
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
          ROM Image       Listing       Cross-Reference
              │              │              │
              │              │              │
              ▼              ▼              ▼
        Emulator /       Output File    Output File
        ROM File
```

The listing and cross-reference products are optional.

Their generation must therefore be configurable through assembly options.

---

## 11. Binary ROM Image

The binary ROM image is the primary machine-code output of the assembler.

It contains the bytes generated for the selected target architecture.

The binary image can have two destinations:

```text
                     Binary ROM Image
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
        Load into Emulator         Save to File
```

Loading the image into the emulator and saving the image to a file are separate application operations.

The assembler generates the image but does not decide which destination is used.

---

## 12. Listing File

The assembler may generate a listing file containing the source program together with the generated addresses and machine-code representation.

A listing may conceptually contain information such as:

```text
Address   Machine Code   Source
-------   ------------   ----------------
0200      6000           LD V0, 0
0202      6101           LD V1, 1
0204      8014           ADD V0, V1
0206      1206           JP LOOP
```

The exact listing format is defined separately by the assembler design.

Listing generation is configurable.

If listing generation is disabled, the assembler does not need to generate a listing product.

The GUI should provide an option to enable or disable listing generation.

A generated listing can be:

- displayed in the assembler GUI
- saved to a file

The exact combination of these capabilities is a GUI design decision.

---

## 13. Cross-Reference Information

The assembler should provide cross-reference information connecting symbols and source locations with generated addresses.

The cross-reference information should support at least:

- labels
- subroutine labels
- variables/symbols
- addresses
- source line numbers
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

- included in the listing file
- generated as a separate output product

The final format is not yet fixed.

The architecture must nevertheless treat cross-reference generation as a distinct configurable output capability.

---

## 14. Output Configuration

Generation of optional output products is controlled by assembly options.

Conceptually:

```text
Assembly Options
├── generate_binary       = true
├── generate_listing      = false
└── generate_crossref     = false
```

The binary ROM image is the fundamental assembly product.

Listing and cross-reference generation are optional.

The configuration must be available to the assembler independently of the GUI.

The GUI provides the user interface for configuring these options.

The Controller transfers the selected configuration to the assembler as part of the `AssemblyRequest`.

---

## 15. Assembly Result

The assembler returns an `AssemblyResult`.

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

The exact representation is defined by `assembler_public_api.md`.

### 15.1 Status

The result indicates whether assembly succeeded.

At minimum, the result must distinguish between:

- successful assembly
- assembly failure

### 15.2 Diagnostics

Diagnostics contain errors, warnings, and other messages generated during assembly.

They must contain enough information for the GUI to identify the corresponding source location.

### 15.3 Binary Image

On successful assembly, the result contains the generated machine-code image.

### 15.4 Listing

If listing generation was requested, the result contains the generated listing.

### 15.5 Cross-Reference

If cross-reference generation was requested, the result contains the generated cross-reference information.

### 15.6 Symbols

The result may contain the resolved symbol table.

Symbols are important for future debugger integration and source-aware disassembly.

### 15.7 Source Mapping

The result may contain mappings between source locations and generated addresses.

This information is particularly useful for future debugger integration.

---

## 16. Saving Generated Output

Generated output products can be saved to files by the application.

The assembler does not directly control file dialogs or other GUI operations.

The Controller coordinates the operation.

The general flow is:

```text
Assembler
    │
    ▼
AssemblyResult
    │
    ▼
Chip8Controller
    │
    ▼
Assembler GUI
    │
    │ user selects output filename
    ▼
Controller
    │
    ▼
Output File
```

The Controller may use the output data from the `AssemblyResult` to write:

- ROM image files
- listing files
- cross-reference files

The exact file formats and extensions are defined by the assembler design.

---

## 17. Loading an Assembled Program

The Controller may provide an operation such as:

```text
Assemble
Assemble and Load
```

For an assemble-and-load operation, the data flow is:

```text
Source Editor
     │
     ▼
Chip8Controller
     │
     ▼
Assembler
     │
     ▼
AssemblyResult
     │
     ├── failure ─────► GUI diagnostics
     │
     └── success
             │
             ▼
        Binary ROM Image
             │
             ▼
          Emulator
```

The assembler does not call `Chip8Machine` directly.

---

## 18. Diagnostic Data Flow

The existing application already contains a diagnostics infrastructure and a diagnostics view.

Assembler diagnostics should not simply be treated as ordinary emulator diagnostics.

The assembler GUI should contain a dedicated diagnostics view.

The existing diagnostic infrastructure can nevertheless be reused.

The assembler identifies its diagnostics using the diagnostic `Source` field.

Conceptually:

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
    ├──► Existing application diagnostics
    │
    └──► Assembler diagnostics
                 │
                 ▼
          Assembler Dialog
          Diagnostics View
```

The Controller and log manager are responsible for routing assembler diagnostics to the assembler-specific diagnostics view.

This avoids duplicating the application's diagnostic infrastructure while keeping assembler diagnostics separate from unrelated emulator diagnostics.

---

## 19. Diagnostic Source Locations

Assembler diagnostics must retain source-location information.

For example:

```text
main.asm:14:5: error: unknown mnemonic 'PLANE'
```

The GUI should be able to use this information to:

- display the diagnostic
- highlight the affected source
- position the editor at the relevant line
- position the cursor at the relevant column where possible

The assembler does not need to know how the GUI performs these operations.

It only provides the diagnostic information.

---

## 20. Successful Assembly

A successful assembly produces a binary ROM image and, depending on configuration, optional additional output products.

The Controller receives these products as part of the `AssemblyResult`.

The binary image is not automatically loaded into the emulator by the assembler.

Instead:

```text
Assembler
    │
    ▼
AssemblyResult
    │
    ▼
Chip8Controller
    │
    ├──► Save ROM
    ├──► Save Listing
    ├──► Save Cross-Reference
    └──► Load ROM into Emulator
```

This prevents the assembler from becoming coupled to emulator state or filesystem/UI operations.

---

## 21. Failed Assembly

If assembly fails, no valid binary image is available for loading into the emulator.

The Controller passes the diagnostics to the assembler GUI.

```text
Assembler
    │
    ▼
AssemblyResult
    │
    ├── status = failure
    │
    └── diagnostics
             │
             ▼
       Chip8Controller
             │
             ▼
       Assembler Dialog
             │
             ▼
      Diagnostics View
```

The currently loaded emulator program should not be replaced merely because an assembly attempt failed.

This prevents an unsuccessful edit from destroying the currently executable program.

---

## 22. Successful Reassembly

A successful assembly produces a new set of output products.

The Controller decides whether the new binary image replaces the currently loaded program.

This decision is outside the assembler.

This allows different workflows, for example:

```text
Edit → Assemble → Inspect
```

or:

```text
Edit → Assemble → Load → Debug
```

or:

```text
Edit → Assemble → Save ROM
```

or:

```text
Edit → Assemble → Save Listing
```

without changing the assembler implementation.

---

## 23. Source Editor

The source editor belongs to the GUI.

It is not part of the assembler subsystem.

The editor maintains the current source text and passes a snapshot of that text to the Controller when an assembly operation is requested.

```text
Source Editor
      │
      │ source text
      ▼
Chip8Controller
      │
      ▼
AssemblyRequest
```

The assembler should not maintain ownership of the editor's mutable document.

An assembly operation works on a defined source snapshot.

This ensures that the result corresponds to the exact source submitted for assembly.

---

## 24. Assembly Session

The application may maintain an assembly session representing the current source document and its most recent assembly result.

Conceptually:

```text
Assembly Session
├── source
├── source name
├── selected target
├── assembly options
├── last assembly result
└── generated products
```

The exact implementation of an assembly session is not yet fixed.

The concept is useful because the GUI will eventually need to display information associated with the current source and its latest assembly.

---

## 25. Source-to-Machine-Code Mapping

The assembler should preserve sufficient information to associate generated addresses with source locations.

Conceptually:

```text
Source line       Address
-----------       -------
10                0x200
11                0x202
12                0x204
13                0x206
```

This information can later be used by the debugger.

For example:

```text
Debugger
   │
   ▼
Program Address 0x204
   │
   ▼
Source Mapping
   │
   ▼
Source line 12
```

This capability should therefore be considered during the assembler design even if the initial GUI does not expose it.

---

## 26. Symbol Information

The assembler may expose resolved symbols as part of the assembly result.

For example:

```text
START = 0x200
LOOP  = 0x20A
DRAW  = 0x220
```

This information can eventually be used by:

- debugger
- disassembler
- source editor
- memory views
- code analysis
- diagnostics

The assembler remains responsible only for producing the information.

The Controller and other application components determine how it is used.

---

## 27. Future Debugger Integration

The assembler is expected to become an important source of debugging information.

A future integration may provide:

```text
Assembly Source
      │
      ▼
Assembler
      │
      ├── Binary ROM Image
      ├── Symbols
      └── Source Mapping
             │
             ▼
         Controller
             │
             ▼
          Debugger
```

This would allow the debugger to associate emulator addresses with assembly source locations.

Possible future capabilities include:

- source-level breakpoints
- source-line highlighting
- symbol lookup
- source-aware stepping
- source-to-address navigation
- address-to-source navigation

These features are outside the initial assembler implementation but influence the design of the assembly result.

---

## 28. GUI Responsibilities

The assembler GUI is responsible for presentation and user interaction.

It is responsible for:

- displaying assembly source
- allowing source editing
- displaying the selected target
- initiating assembly operations
- configuring optional output products
- displaying assembler diagnostics
- displaying assembly status
- displaying generated output information
- allowing the user to save the generated ROM image
- allowing the user to save the generated listing
- allowing the user to save the generated cross-reference information
- allowing the user to load a successful assembly into the emulator
- presenting future source/debug information

It is not responsible for:

- parsing
- target resolution
- semantic analysis
- symbol resolution
- machine-code generation
- direct manipulation of emulator internals
- constructing listing or cross-reference information

---

## 29. Controller Responsibilities

`Chip8Controller` coordinates the assembler with the rest of the application.

Its responsibilities include:

- receiving assembly requests from the GUI
- constructing `AssemblyRequest`
- invoking the assembler
- receiving `AssemblyResult`
- routing assembler diagnostics
- making generated output products available to the GUI
- coordinating saving of generated output
- making generated program images available to the emulator
- coordinating loading of assembled programs
- maintaining application-level assembly state where required
- coordinating future debugger integration

The Controller must not duplicate assembler logic.

It acts as an application coordinator rather than an assembler implementation.

---

## 30. Assembler Responsibilities

The assembler subsystem is responsible for:

- target discovery
- target selection
- lexical analysis
- parsing
- AST construction
- semantic analysis
- symbol resolution
- code generation
- generation of diagnostics
- generation of the binary ROM image
- generation of the listing when requested
- generation of cross-reference information when requested
- generation of symbols and source mappings

The assembler is not responsible for:

- GUI interaction
- Qt widgets
- editor state
- emulator state
- loading programs into memory
- starting or stopping execution
- displaying diagnostics
- selecting output filenames
- writing GUI-controlled output files

---

## 31. Data Ownership

The ownership boundaries are:

```text
GUI
 │
 ├── owns editor presentation
 ├── owns user interaction
 └── owns output-file selection dialogs
          │
          ▼
Controller
 │
 ├── coordinates application state
 ├── coordinates subsystem communication
 ├── routes diagnostics
 └── coordinates output and emulator operations
          │
          ├──────────────► Assembler
          │
          └──────────────► Emulator
```

The assembler owns the data structures associated with assembly processing and generated output products.

The emulator owns machine state.

The GUI owns presentation state.

The Controller coordinates these components.

No subsystem should modify another subsystem's internal state directly.

---

## 32. Output File Handling

Output file selection is a GUI operation.

The GUI presents the appropriate file-selection dialog and obtains the destination path from the user.

The Controller then performs or coordinates the actual output operation.

The assembler does not open GUI file dialogs.

Conceptually:

```text
Assembler GUI
      │
      │ Save ROM
      ▼
Controller
      │
      │ destination path
      ▼
Assembly Result / Output Writer
      │
      ▼
ROM File
```

The same pattern applies to listing and cross-reference files.

---

## 33. Error Handling

Errors are returned through defined result objects rather than raised directly into the GUI layer.

The assembler may internally use exceptions where appropriate, but errors crossing the assembler public API should be represented in a form suitable for application-level diagnostics.

The Controller converts the assembly result into the application's diagnostic flow.

The assembler GUI presents the diagnostics to the user.

File-system errors encountered while saving output are application-level errors and should be reported separately from assembly diagnostics.

---

## 34. Assembler Dialog

The assembler is integrated into the existing GUI through a dedicated dialog window.

The existing main application window receives an **Assembler** button.

Conceptually:

```text
Existing MainWindow
┌─────────────────────────────────────────────┐
│                                             │
│ [ Assembler ]                               │
│                                             │
└─────────────────────────────────────────────┘
                     │
                     │ click
                     ▼
             Assembler Dialog
```

Pressing the button opens the assembler dialog.

The assembler dialog contains the assembler-specific GUI.

This approach avoids redesigning the existing main application window while providing the assembler with a dedicated workspace.

---

## 35. Assembler Dialog Layout

The exact visual design is not yet fixed.

The dialog should provide, at minimum, the following functional areas:

```text
+-------------------------------------------------------------+
| Target: [ COSMAC CHIP-8                         ▼ ]        |
+-------------------------------------------------------------+
|                                                             |
|                    Source Editor                            |
|                                                             |
|                                                             |
+-------------------------------------------------------------+
| Diagnostics                                                 |
|                                                             |
|                                                             |
+-------------------------------------------------------------+
| Assemble | Assemble & Load | Save ROM                     |
| Save Listing | Save Cross-Reference                       |
+-------------------------------------------------------------+
```

The dialog should also provide controls for enabling or disabling optional output products.

For example:

```text
Output:
[✓] Binary ROM
[ ] Listing
[ ] Cross-Reference
```

The exact widgets and layout remain subject to detailed GUI design.

---

## 36. Relationship to Existing GUI

The existing GUI is extended rather than replaced.

The existing `MainWindow` receives an **Assembler** button.

Pressing the button opens a new assembler dialog window.

The assembler dialog is responsible for the assembler-specific workflow.

The existing main window remains responsible for the emulator and debugger workflow.

The relationship is therefore:

```text
Existing Application
│
├── MainWindow
│     │
│     └── [Assembler]
│             │
│             ▼
│       Assembler Dialog
│             │
│             ├── Source Editor
│             ├── Target Selection
│             ├── Output Configuration
│             └── Diagnostics
│
├── Emulator
│
├── Debugger
│
└── Controller
```

The assembler dialog and the existing main window communicate through the Controller.

The assembler dialog does not communicate directly with the emulator.

---

## 37. Future Extensions

The architecture should allow future functionality without requiring a redesign of the assembler.

Potential extensions include:

- multiple source documents
- project management
- include files
- generated listing files
- symbol browser
- source-level debugger integration
- source-aware disassembly
- address-to-source navigation
- source-to-address navigation
- automatic reassembly
- build configurations
- architecture-specific assembler options
- assembler output inspection
- binary export
- ROM loading and execution
- integrated cross-reference browsing

These features are not requirements for the initial implementation.

---

## 38. Design Constraints

The integration must satisfy the following constraints:

1. The assembler remains under `src/assembler`.
2. The assembler must not depend on Qt.
3. The assembler must not depend directly on `Chip8Machine`.
4. The GUI must not depend directly on assembler implementation classes.
5. The Controller remains the application-level coordinator.
6. The target architecture must be established before parsing.
7. A source target directive takes precedence over the externally supplied target.
8. An external target must be available when no source target directive is present.
9. Assembly failure must not replace the currently loaded emulator program.
10. The assembler must be usable independently of the emulator's execution state.
11. The assembler result should provide sufficient information for future debugger integration.
12. Changes to the existing emulator should be kept to a minimum.
13. Changes to the ISA subsystem are permitted where required for clean assembler integration.
14. Binary ROM generation is always available as the primary assembly product.
15. Listing generation is configurable.
16. Cross-reference generation is configurable.
17. Generated output products can be saved independently of loading a ROM into the emulator.
18. Assembler diagnostics are presented in a dedicated assembler diagnostics view.
19. The existing diagnostic infrastructure may be reused to route assembler diagnostics.
20. The existing main window provides access to the assembler through an **Assembler** button.
21. The assembler workflow is contained in a dedicated dialog window.

---

## 39. Summary

The assembler is integrated into the existing CHIP-8 application as an independent subsystem.

The central data flow is:

```text
Assembler GUI
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
      ▼
AssemblyResult
      │
      ├──► Diagnostics
      │
      ├──► Binary ROM Image ─────► Emulator
      │
      ├──► Listing ──────────────► File
      │
      ├──► Cross-Reference ──────► File
      │
      ├──► Symbols
      │
      └──► Source Mapping
```

The assembler remains independent of the GUI and emulator.

The Controller coordinates communication between the subsystems.

The target architecture is established before parsing.

The source target directive takes precedence over an externally selected target.

The assembler produces a binary ROM image as its primary output and can optionally produce a listing and cross-reference output.

The GUI provides controls for selecting the target architecture, configuring optional output products, assembling the source, saving generated files, and loading a successful ROM image into the emulator.

Assembler diagnostics are presented in a dedicated diagnostics view within the assembler dialog while using the existing application's diagnostic infrastructure and routing mechanisms.

The existing main window is extended with an **Assembler** button that opens the dedicated assembler dialog.

This architecture provides a clean boundary between the assembler and the existing application while allowing the assembler to become a fully integrated part of the CHIP-8 emulator and debugger environment.
