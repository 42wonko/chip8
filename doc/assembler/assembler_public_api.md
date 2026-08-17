# Assembler Public API

**Author:** Michael Dlubatz

**Date:** 2026-08-04

**Status:** Draft

---

# 1. Purpose

This document defines the public API of the CHIP-8 assembler.

The API is the only interface used by:

- the emulator GUI
- the debugger
- future IDE functionality
- command-line tools
- unit tests

The remaining implementation details of the assembler are internal and shall not be accessed directly.

---

# 2. Design Goals

The API shall:

- hide all implementation details
- be independent of the parser implementation
- be independent of the target architecture implementation
- support diagnostics
- support future extensions
- provide a stable interface to the remainder of the project

---

# 3. Public Components

The assembler subsystem exposes only the following classes.

```text
Assembler
AssemblerConfiguration
AssemblyResult
Diagnostic
DiagnosticCollection
```

Everything else is considered internal.

---

# 4. Assembler

The assembler represents the complete assembly engine.

```python
class Assembler:
```

Responsibilities:

- assemble source files
- accept an externally supplied target architecture when required
- perform target discovery and target selection
- return diagnostics
- generate binary output

---

## Public Methods

### assemble()

```python
assemble(
    source: str,
    filename: str | None = None
) -> AssemblyResult
```

Assembles a source string.

Returns an `AssemblyResult`.

---

### assemble_file()

```python
assemble_file(
    filename: Path
) -> AssemblyResult
```

Reads and assembles a source file.

---

### configuration()

```python
configuration() -> AssemblerConfiguration
```

Returns the current configuration.

---

### set_configuration()

```python
set_configuration(
    configuration: AssemblerConfiguration
)
```

Changes the assembler configuration.

---

# 5. AssemblerConfiguration

The configuration object controls the behavior of the assembler.

```python
class AssemblerConfiguration:
```

---

## Properties

```text
target_architecture: str | None
case_sensitive_labels
generate_listing
generate_symbol_table
enable_warnings
```

`target_architecture` is the externally supplied fallback target. It may be omitted when the source is expected to contain a `TARGET` directive.

For example:

```text
target_architecture = COSMAC
```

If the source contains `TARGET XO-CHIP`, the source target takes precedence over the configured fallback target. If neither source nor configuration supplies a target, assembly fails with a target-selection diagnostic.

Future architectures can be added without changing the public API.

---

# 6. AssemblyResult

The result object returned by every assembly.

```python
class AssemblyResult:
```

---

## Properties

```text
success
binary
diagnostics
symbols
listing
```

### success

Boolean indicating whether assembly succeeded.

### binary

Generated machine code.

Type:

```python
bytes
```

### diagnostics

Collection of warnings and errors.

### symbols

Optional symbol table.

### listing

Optional assembly listing.

---

# 7. Diagnostic

Represents one assembler message.

```python
class Diagnostic:
```

---

## Properties

```text
severity
filename
line
column
message
```

---

## Severity

```text
Information
Warning
Error
```

---

# 8. DiagnosticCollection

Container holding all diagnostics produced during assembly.

```python
class DiagnosticCollection:
```

---

## Operations

```python
add()
errors()
warnings()
has_errors()
clear()
```

---

# 9. Public Workflow

Typical usage:

```text
Application
      │
      ▼
Assembler
      │
      ▼
AssemblyResult
      │
      ├── Binary
      ├── Diagnostics
      ├── Symbols
      └── Listing
```

---

# 10. Integration with the Controller

The controller owns the assembler subsystem.

```text
Chip8Controller
        │
        ├── Emulator
        ├── GUI
        ├── Diagnostics
        └── Assembler
```

Neither the GUI nor the emulator access parser internals directly.

All interaction occurs through the `Assembler` class.

---

# 11. Thread Safety

The assembler is intended to be used as a normal application component.

No assumptions are made regarding concurrent use.

If concurrent assembly is required in the future, separate assembler instances shall be created.

---

# 12. Error Handling

Assembly failures are reported through diagnostics rather than exceptions.

Exceptions are reserved for unexpected internal failures such as:

- file I/O failures
- corrupted architecture definitions
- internal consistency errors

Syntax errors, undefined labels, invalid operands, and similar user errors shall always be returned as diagnostics.

---

# 13. Future Extensions

The public API has been intentionally designed to remain stable as new functionality is added.

Future additions may include:

- multiple source files
- include files
- macro expansion
- conditional assembly
- library support
- relocatable object files

These features shall be added without breaking the existing API.
