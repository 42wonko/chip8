# CHIP-8 Emulator

![CHIP-8 Emulator](./doc/Chip8_Mainwindow.png)

A modern emulator, debugger and code analysis environment for the original CHIP-8 virtual machine, written in Python using PyQt6.

Unlike many CHIP-8 emulators, this project is not primarily intended as a gaming platform. Its main objective is to provide an accurate implementation of the original COSMAC VIP CHIP-8 interpreter together with modern debugging, diagnostics and software analysis facilities.

The emulator emphasizes correctness, maintainability and clean software architecture. Throughout the project, historical CHIP-8 behaviour is preferred over convenience features or later extensions whenever possible.

---

## Table of Contents

* [Design Rationale](#rationale)
* [CHIP-8 Introduction](#introduction)
* [Supported Features](#features)
* [Software Architecture](#architecture)
* [Opcode Reference](#op-codes)
* [GUI Description](#gui-description)
* [Dependencies](#dependencies)
* [Building and Running](#building)
* [Development with CMake](#cmake)
* [Project Status](#status)
* [External Links](#links)

<a name="rationale"></a>

## Design Rationale

The project was started as an exercise in emulator development but gradually evolved into a complete debugging and code analysis environment for the original CHIP-8 virtual machine.

Several design goals influenced the architecture from the beginning.

### Qt Graphical User Interface

The emulator uses a PyQt6 based graphical user interface that provides immediate visual feedback while executing programs.

Besides displaying the original 64×32 pixel framebuffer, the GUI contains an integrated debugger with register view, memory viewer, code view, diagnostics, execution control and configuration dialog.

### Separation of Concerns

The emulator core is completely separated from the graphical user interface.

Peripheral devices such as the display, keyboard and audio output are implemented as independent components with well-defined interfaces. This separation improves maintainability, simplifies testing and allows individual subsystems to evolve independently.

### Clean Software Architecture

The project follows a modular architecture with clearly separated responsibilities.

The controller coordinates the high-level application logic while the emulator core remains independent of the GUI. Configuration, diagnostics, logging, execution tracing and audio are implemented as separate reusable subsystems.

Dependency injection is used throughout the project to avoid unnecessary coupling between components.

### Diagnostics and Logging

Diagnostics, application logging and execution tracing are considered core features rather than development afterthoughts.

The emulator contains a comprehensive diagnostics framework together with configurable application logging and multiple execution trace levels, making it suitable both for development and for investigating emulator behaviour.

### Unit Testing

The emulator core is extensively covered by automated unit tests.

The instruction decoder, memory, stack, timers, framebuffer, keyboard and most individual CHIP-8 instructions are verified independently, allowing internal refactoring without affecting external behaviour.

### Original Behaviour

The emulator aims to reproduce the behaviour of the original COSMAC VIP CHIP-8 interpreter as closely as possible.

Where historical behaviour differs from later CHIP-8 variants or modern emulator conventions, the original implementation is generally preferred.

No Super-CHIP, XO-CHIP or Mega-CHIP extensions are currently implemented.

### Debugging First

The emulator is intentionally designed around debugging rather than maximum execution speed.

After every executed instruction the graphical user interface and the complete internal emulator state remain synchronized. Although this slightly reduces performance, it provides deterministic debugging behaviour and immediate visual feedback during program execution.

For this reason the project should be viewed primarily as a development and learning environment rather than as a gaming emulator.

<a name="features"></a>

## Supported Features

As mentioned before, this emulator is not meant to be a gaming platform. As such the primary goal is understanding, debugging and analysing CHIP-8 software.

### Emulator Core

The emulator implements the complete original CHIP-8 instruction set together with the original hardware architecture.

Features include:

* Complete original CHIP-8 instruction set
* Original COSMAC-compatible instruction behaviour
* 64 × 32 monochrome display
* Hardware delay timer
* Hardware sound timer
* Adjustable CPU clock frequency
* Configurable 4 × 4 CHIP-8 keyboard
* Configurable audio frequency
* Configurable audio output device

No Super-CHIP, XO-CHIP or Mega-CHIP extensions are currently implemented.

---

### Integrated Debugger

The graphical user interface provides an integrated debugger that remains synchronized with the emulator after every executed instruction.

Available features include:

* Start, stop and reset execution
* Single-step execution
* Adjustable execution speed
* Automatic current instruction highlighting
* Automatic code view scrolling
* Real-time register display
* Real-time timer display
* Real-time memory viewer
* Integrated disassembler
* Runtime diagnostics display

Because the debugger is synchronized after every executed instruction, the internal machine state is always immediately visible.

---

### Code Analysis

The emulator contains a built-in static code analysis engine that continuously analyses the loaded program.

Features include:

* Automatic disassembly
* Static control-flow analysis
* Runtime-assisted code discovery
* Dynamic `BNNN` target analysis
* Incremental analysis updates
* Automatic debugger refresh

This allows code that is only discovered during execution to appear automatically in the disassembly view.

---

### Diagnostics

A dedicated diagnostics framework continuously validates emulator operation.

The diagnostics system reports:

* Invalid memory accesses
* Stack overflow and underflow
* Illegal instruction execution
* Invalid program behaviour
* Runtime warnings
* Emulator errors

Diagnostics are displayed directly inside the graphical user interface.

---

### Application Logging

The emulator contains a configurable application logging framework intended primarily for development and debugging.

Supported features include:

* Configurable log file
* Configurable log categories
* Information messages
* Warning messages
* Error messages
* Automatic function entry logging
* Automatic function exit logging
* Nested function indentation

Application logging is entirely independent from execution tracing.

---

### Execution Tracing

Instruction execution can be recorded in a configurable execution trace.

Three trace levels are supported:

* **Basic** — instruction execution
* **Changes** — register, timer, memory and display modifications
* **Full** — complete machine state after every instruction

Execution tracing is designed to simplify emulator verification and debugging.

---

### Audio

The original CHIP-8 sound timer is implemented using a dedicated audio subsystem based on **sounddevice** and **PortAudio**.

Features include:

* Continuous audio stream
* Software volume control
* Configurable output device
* Configurable beep frequency
* Configuration dialog integration
* Test sound generation
* Cross-platform audio backend

The continuous stream design avoids repeatedly opening and closing the audio device and significantly improves reliability on modern Linux systems.

---

### Testing

Correctness is verified through an extensive automated unit test suite.

The project includes tests for:

* Instruction execution
* Memory
* Registers
* Stack
* Timers
* Keyboard
* Framebuffer
* Code analysis
* Emulator integration

All unit tests are executed using **pytest**.

---

### Code Quality

The project is continuously verified using modern Python development tools.

Current quality checks include:

* Ruff linting
* mypy static type checking
* Automated unit tests
* CMake development targets
* Doxygen documentation generation

The project is maintained clean with respect to both Ruff and mypy.

<a name="introduction"></a>

## CHIP-8 Introduction

CHIP-8 is an interpreted programming language originally developed by Joseph Weisbecker during the mid-1970s for the COSMAC VIP computer based on the RCA CDP1802 microprocessor.

Unlike a conventional processor, CHIP-8 is a virtual machine consisting of a small instruction set, 4 KB of memory, sixteen 8-bit general-purpose registers, a monochrome 64 × 32 pixel display, two hardware timers and a hexadecimal 16-key keyboard.

Although extremely simple by modern standards, CHIP-8 remains one of the most popular systems for learning emulator development because its architecture is compact while still containing many of the concepts found in larger computer systems.

Over the years numerous incompatible extensions have been introduced, including Super-CHIP, XO-CHIP and Mega-CHIP.

This emulator intentionally targets the original COSMAC VIP implementation. Where later variants differ from the original interpreter, historical behaviour is generally preferred over newer conventions.

The following section lists every opcode implemented by the emulator.

---

## CHIP-8 Opcode Reference

- **00E0**	clear the screen, in XO-CHIP only selected bit planes are cleared, in MegaChip mode it updates the visible screen before clearing the draw buffer
- **00EE**	return from subroutine to address pulled from stack
- **0nnn**	jump to native assembler subroutine at 0xNNN
- **1nnn**	jump to address NNN
- **2nnn**	push return address onto stack and call subroutine at address NNN
- **3xnn**	skip next opcode if vX == NN (note: on platforms that have 4 byte opcodes, like F000 on XO-CHIP, this needs to skip four bytes)
- **4xnn**	skip next opcode if vX != NN (note: on platforms that have 4 byte opcodes, like F000 on XO-CHIP, this needs to skip four bytes)
- **5xy0**	skip next opcode if vX == vY (note: on platforms that have 4 byte opcodes, like F000 on XO-CHIP, this needs to skip four bytes)
- **6xnn**	set vX to NN
- **7xnn**	add NN to vX
- **8xy0**	set vX to the value of vY
- **8xy1**	set vX to the result of bitwise vX OR vY
- **8xy2**	set vX to the result of bitwise vX AND vY
- **8xy3**	set vX to the result of bitwise vX XOR vY
- **8xy4**	add vY to vX, vF is set to 1 if an overflow happened, to 0 if not, even if X=F!
- **8xy5**	subtract vY from vX, vF is set to 0 if an underflow happened, to 1 if not, even if X=F!
- **8xy6**	set vX to vY and shift vX one bit to the right, set vF to the bit shifted out, even if X=F!
- **8xy7**	set vX to the result of subtracting vX from vY, vF is set to 0 if an underflow happened, to 1 if not, even if X=F!
- **8xyE**	set vX to vY and shift vX one bit to the left, set vF to the bit shifted out, even if X=F!
- **9xy0**	skip next opcode if vX != vY (note: on platforms that have 4 byte opcodes, like F000 on XO-CHIP, this needs to skip four bytes)
- **Annn**	set I to NNN
- **Bnnn**	jump to address NNN + v0
- **Cxnn**	set vx to a random value masked (bitwise AND) with NN
- **Dxyn**	draw 8xN pixel sprite at position vX, vY with data starting at the address in I, I is not changed
- **Ex9E**	skip next opcode if key in the lower 4 bits of vX is pressed (note: on platforms that have 4 byte opcodes, like F000 on XO-CHIP, this needs to skip four bytes)
- **ExA1**	skip next opcode if key in the lower 4 bits of vX is not pressed (note: on platforms that have 4 byte opcodes, like F000 on XO-CHIP, this needs to skip four bytes)
- **Fx07**	set vX to the value of the delay timer
- **Fx0A**	wait for a key pressed and released and set vX to it, in megachip mode it also updates the screen like clear
- **Fx15**	set delay timer to vX
- **Fx18**	set sound timer to vX, sound is played as long as the sound timer reaches zero
- **Fx1E**	add vX to I
- **Fx29**	set I to the 5 line high hex sprite for the lowest nibble in vX
- **Fx33**	write the value of vX as BCD value at the addresses I, I+1 and I+2
- **Fx55**	write the content of v0 to vX at the memory pointed to by I, I is incremented by X+1
- **Fx65**	read the bytes from memory pointed to by I into the registers v0 to vX, I is incremented by X+1

<a name="architecture"></a>
## Software Architecture

The emulator is intentionally organized as a collection of independent
subsystems with clearly defined responsibilities. The goal was to make the
emulator maintainable, testable and easy to extend instead of producing the
smallest possible implementation.

The architecture follows a controller-driven design.

```text
                   +----------------------+
                   |    Chip8Controller   |
                   +----------+-----------+
                              |
          +-------------------+-------------------+
          |                   |                   |
          |                   |                   |
     MainWindow         Chip8Machine      EmulatorConfiguration
          |                   |
          |                   |
          |         +---------+---------+
          |         |         |         |
          |     Memory    Registers   Timers
          |         |         |         |
          |         +---------+---------+
          |                   |
          |             Opcode Executor
          |                   |
          |         +---------+---------+
          |         |                   |
      CodeAnalysis             Diagnostics
          |
      CodeTableModel

Audio (Beeper / AudioDevice)
Application Logging
Execution Tracing
```

The graphical user interface never directly manipulates the emulator.
All interaction is performed through the controller, which coordinates the
individual subsystems.

This separation keeps the emulator core independent from the GUI, simplifies
unit testing and makes future extensions considerably easier.

### Chip8Controller

The controller is responsible for coordinating the application.

Its responsibilities include:

- Loading ROM images
- Starting, stopping and resetting the emulator
- Executing single-step debugging
- Updating the graphical user interface
- Managing CPU and hardware timers
- Emulator configuration
- Audio control
- Diagnostics
- Application logging
- Execution tracing

The controller intentionally contains no emulator logic. All CHIP-8 execution
is delegated to the `Chip8Machine` class.

### Chip8Machine

`Chip8Machine` implements the virtual computer itself.

It owns all emulated hardware components, including

- Memory
- Registers
- Stack
- Timers
- Framebuffer
- Keyboard

The machine executes exactly one CHIP-8 instruction per CPU cycle and has no
knowledge of the graphical user interface.

### Code Analysis

Unlike a traditional emulator, this project contains a static code analysis
engine.

The analyzer

- Disassembles the loaded ROM
- Detects reachable code
- Identifies invalid instructions
- Performs runtime-assisted analysis of indirect `BNNN` jumps
- Updates the disassembly automatically while the emulator executes

This allows the debugger to present an increasingly accurate disassembly even
for programs containing computed jump targets.

### Diagnostics

A central diagnostics framework collects warnings and errors from all emulator
subsystems.

Diagnostics are displayed in the graphical user interface and are also used
during unit testing.

Unlike exceptions, diagnostics allow the emulator to continue execution
whenever possible while still informing the developer of unexpected runtime
conditions.

### Application Logging

Application logging records events generated by the emulator itself.

Supported log messages include

- Information
- Warnings
- Errors
- Automatic function entry tracing
- Automatic function exit tracing

Application logging is intended for debugging the emulator and is completely
independent of execution tracing.

### Execution Tracing

Execution tracing records the behaviour of the emulated CHIP-8 program.

Three trace levels are available.

| Level | Description |
|------|-------------|
| BASIC | Executed instructions |
| CHANGES | Register, timer, memory and display changes |
| FULL | Complete machine state after every instruction |

Keeping execution tracing separate from application logging allows emulator
development and CHIP-8 program analysis to be performed independently.

### Audio

The original implementation used Qt Multimedia.

The current implementation uses the `sounddevice` library, providing reliable
audio output across Linux distributions while remaining independent from the
graphical user interface.

The audio subsystem consists of two layers.

- **Beeper** — Public interface used by the controller.
- **AudioDevice** — Low-level sound generation using `sounddevice`.

Volume, output device and beep frequency can all be configured at runtime.

### Unit Testing

Every emulator subsystem is designed to be testable in isolation.

The project contains comprehensive unit tests covering

- Instruction execution
- Memory
- Registers
- Stack
- Timers
- Framebuffer
- Keyboard
- Code analysis

The emulator core can therefore be validated without launching the graphical
user interface, allowing automated regression testing during development.

<a name="gui-description"></a>

## GUI Description

The graphical user interface combines the emulator, debugger and code analysis tools into a single integrated development environment for CHIP-8 software.

After every executed instruction the display, registers, memory view and disassembler are synchronized with the current state of the virtual machine, making it possible to observe program execution in real time.

![CHIP-8 Emulator](./doc/Chip8_Mainwindow.png)

### Display

The upper-left corner of the window contains the original 64 × 32 monochrome CHIP-8 display.

The display is updated immediately after every drawing instruction and accurately reproduces the behaviour of the original COSMAC VIP framebuffer.

### Registers

The register panel displays the complete processor state:

* General-purpose registers V0–VF
* Program Counter (PC)
* Index Register (I)
* Stack Pointer (SP)
* Delay Timer (DT)
* Sound Timer (ST)
* Current instruction

All register values are updated after every executed instruction.

### Memory View

The memory viewer provides a hexadecimal representation of the complete 4 KB CHIP-8 memory.

Modified memory locations are updated incrementally during execution, avoiding unnecessary refreshes while keeping the display synchronized with the emulator.

### Code View

The integrated disassembler presents the currently loaded program as an assembly listing.

Features include:

* Automatic instruction decoding
* Current instruction highlighting
* Automatic scrolling during execution
* Runtime-assisted code discovery
* Dynamic `BNNN` target analysis

As new code paths are discovered during execution, the disassembly is updated automatically.

### Diagnostics

The diagnostics window displays warnings and errors detected by the emulator.

Typical diagnostics include:

* Invalid memory accesses
* Stack overflow and underflow
* Illegal instruction execution
* Runtime consistency warnings

Diagnostics are generated automatically by the emulator subsystems and remain available until the next reset.

### Emulator Control

The toolbar provides direct access to the most frequently used debugging functions.

Supported operations include:

* Load ROM
* Reload ROM
* Run
* Pause
* Single Step
* Reset
* Configure Emulator
* Configure Keyboard

The CPU execution frequency can be adjusted at runtime, allowing programs to execute at anything from single-step speed to several hundred instructions per second.

### Configuration Dialog

The configuration dialog allows the emulator to be customized without restarting the application.

Available options include:

* Enable or disable sound
* Select the audio output device
* Adjust output volume
* Adjust beep frequency
* Enable or disable application logging
* Configure the application log file
* Enable or disable execution tracing
* Configure the execution trace file
* Select the execution trace level
* Disable display updates for performance testing

All configuration changes take effect immediately after they are applied.

### Keyboard Configuration

The keyboard mapping dialog allows each CHIP-8 key to be assigned to an arbitrary host keyboard key.

This makes the emulator usable on different keyboard layouts without modifying the emulator core.

<a name="building"></a>

<a name="dependencies"></a>

# Dependencies

The emulator is written in Python and targets Python 3.12 or newer.

**WARNING** It has been tested only on Linux, in particular: openSuSe Tumbleweed, Kubuntu and Mint. I have absolutely no idea if it works on anything else.

## Runtime Dependencies

The following Python packages are required to run the emulator.

| Package | Purpose |
|---------|---------|
| PyQt6 | Graphical user interface |
| NumPy | Framebuffer implementation and audio sample generation |
| sounddevice | Audio output |
| PortAudio | Native audio backend used by `sounddevice` |

All Python dependencies are installed automatically when the project is installed using

```bash
pip install -e .
```

### Linux

Most Linux distributions also require the PortAudio runtime library.

Examples:

Ubuntu / Debian

```bash
sudo apt install portaudio19-dev
```

openSUSE

```bash
sudo zypper install portaudio-devel
```

Fedora

```bash
sudo dnf install portaudio-devel
```

---

## Development Dependencies

The following tools are recommended for development.

| Tool | Purpose |
|------|---------|
| CMake | Development workflow |
| pytest | Unit testing |
| Ruff | Linting and formatting |
| mypy | Static type checking |
| Doxygen | API documentation |
| GraphViz | UML and call graphs (optional) |

These tools are not required for simply running the emulator.

# Building and Running

The emulator can be used in two different ways.

* **Python virtual environment** (recommended for most users)
* **CMake build** (recommended for development)

Both methods use exactly the same source tree.

<a name="cmake"></a>

---

## Python Virtual Environment

### 1. Clone the repository

```bash
git clone https://github.com/42wonko/chip8.git
cd chip8
```

---

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

---

### 3. Activate the virtual environment

Linux:

```bash
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

---

### 4. Install the project

```bash
pip install -e .
```

This installs the emulator together with all required runtime dependencies defined in `pyproject.toml`.
The project is installed in editable mode (-e), allowing changes to the source tree to become immediately visible without reinstalling the package.

---

### 5. Run the emulator

```bash
PYTHONPATH=src python -m chip8
```

The `PYTHONPATH` variable points Python to the project's source directory.

---

### 6. Run the unit tests

Install the development dependencies first:

```bash
pip install -e .[dev]
```

Run the tests using the Python interpreter from the active virtual environment:

```bash
python -m pytest
```

For this project, use:

```bash
PYTHONPATH=src python -m pytest
```

---

### 7. Run Ruff

```bash
ruff check src tests
```

---

### 8. Run mypy

```bash
mypy src
```

---

# Development with CMake

The project contains a CMake build configuration that provides convenient targets for development, testing and documentation generation.

### Configure the project

```bash
mkdir build
cd build

cmake ..
```

---

### Build

```bash
cmake --build .
```

Since the project is written entirely in Python, this step primarily configures the development environment and validates the required tools.

---

### Available CMake Targets

Run the emulator:

```bash
cmake --build . --target run
```

Run the complete unit test suite:

```bash
cmake --build . --target test
```

Run the Ruff linter:

```bash
cmake --build . --target lint
```

Automatically format the source tree:

```bash
cmake --build . --target format
```

Run the mypy type checker:

```bash
cmake --build . --target typecheck
```

Generate the Doxygen documentation:

```bash
cmake --build . --target docs
```

Remove Python cache files:

```bash
cmake --build . --target clean_python
```

Display all available targets:

```bash
cmake --build . --target info
```

---

## Why use CMake?

Although the emulator itself is implemented entirely in Python, CMake provides a convenient, platform-independent development front-end.

It offers a single, consistent interface for:

* configuring the development environment
* running the emulator
* executing the complete unit test suite
* static analysis with Ruff
* type checking with mypy
* generating API documentation
* cleaning Python cache files

Using CMake allows the same development workflow to be used on Linux, Windows and other supported platforms without requiring platform-specific scripts.

<a name="status"></a>

# Project Status

The emulator is functionally complete and implements the original COSMAC VIP CHIP-8 virtual machine.

Current implementation status:

| Component | Status |
|-----------|:------:|
| Emulator Core | ✅ Complete |
| Instruction Set | ✅ Complete |
| Debugger | ✅ Complete |
| GUI | ✅ Complete |
| Code Analysis | ✅ Complete |
| Diagnostics | ✅ Complete |
| Application Logging | ✅ Complete |
| Execution Tracing | ✅ Complete |
| Audio | ✅ Complete |
| Unit Tests | ✅ Complete |

The project currently provides

- complete original CHIP-8 instruction set
- integrated debugger
- static and runtime-assisted code analysis
- configurable diagnostics
- configurable application logging
- configurable execution tracing
- runtime configurable audio subsystem
- extensive automated unit test suite

---

## Planned Features

Future development may include

- persistent configuration
- debugger breakpoints
- run-to-cursor support
- memory watchpoints
- integrated CHIP-8 assembler
- regression ROM suite
- optional Super-CHIP support

The primary development goal remains correctness and maintainability rather than adding CHIP-8 extensions.

<a name="links"></a>

# External Links

## CHIP-8 Documentation

- CHIP-8 on Wikipedia  
  https://en.wikipedia.org/wiki/CHIP-8

- CHIP-8 Variant Opcode Table (Gulrak)  
  https://chip8.gulrak.net

- Cowgod's CHIP-8 Technical Reference  
  http://devernay.free.fr/hacks/chip8/C8TECH10.HTM

---

## Project

GitHub Repository

https://github.com/42wonko/chip8

Issue Tracker

https://github.com/42wonko/chip8/issues

---

## Documentation

The project also contains additional documentation inside the `doc/` directory, including

- Software Requirements and Design Specification (SRDS)
- Logger Design
- Instruction Audit
- Configuration Dialog Design
- Doxygen configuration
