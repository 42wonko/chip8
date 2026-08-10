# CHIP-8 Emulator TODO

## Completed

### Emulator Core

- [x] Complete CHIP-8 instruction set
- [x] Hardware timers (60 Hz)
- [x] Adjustable CPU clock frequency
- [x] Keyboard input
- [x] Display emulation

### GUI

- [x] Register display
- [x] Memory view
- [x] Code view
- [x] Current instruction highlighting
- [x] Automatic debugger scrolling
- [x] Incremental GUI updates
- [x] Diagnostics view
- [x] Runtime code discovery refresh

### Audio

- [x] CHIP-8 beep emulation
- [x] Runtime enable/disable
- [x] Volume control
- [x] Beeper frequency control
- [x] Configuration dialog integration
- [x] sounddevice / PortAudio backend
- [x] Continuous audio stream
- [x] Callback-based waveform generation
- [x] Square wave generation
- [x] Phase accumulator waveform continuity
- [x] Stereo output
- [x] Audio output device selection
- [x] Runtime audio device switching
- [x] Audio backend isolated in AudioDevice
- [x] Audio unit tests

### Infrastructure

- [x] Emulator configuration object
- [x] StepResult incremental GUI updates
- [x] Memory range update optimization
- [x] Diagnostics framework
- [x] DiagnosticReporter
- [x] Application logging framework
- [x] ApplicationLogger
- [x] ApplicationLogReporter
- [x] Configurable application log file
- [x] Optional function tracing
- [x] BufferedFileSink abstraction
- [x] LogManager
- [x] Execution tracing infrastructure
- [x] TraceRecord execution model
- [x] ExecutionTracer
- [x] ExecutionTraceReporter
- [x] BASIC instruction trace
- [x] Program counter tracing
- [x] Configurable trace file
- [x] Cycle-based trace numbering
- [x] Controller integration
- [x] Chip8Machine integration
- [x] Trace remaining emulator state changes where appropriate

### Code Analysis

- [x] Static code analyzer
- [x] Runtime-assisted `BNNN` code analysis
- [x] Dynamic code discovery
- [x] Incremental code analysis
- [x] Automatic Code View updates
- [x] Duplicate runtime target suppression

### Emulator Logging

- [x] Log emulator events to a file
- [x] Configurable log file location
- [x] Configurable log level
- [x] Controller instrumentation
- [x] CodeAnalysis instrumentation

### Emulator Debug Trace

- [x] Function call trace

### CHANGES trace level

- [x] Register changes
- [x] Timer changes
- [x] Memory writes
- [x] Display update events
- [x] Keyboard events

### FULL trace level

- [x] Complete register dump
- [x] I register
- [x] Stack pointer
- [x] Delay timer
- [x] Sound timer

### Testing

- [x] Unit tests updated for logging/tracing architecture
- [x] Audio subsystem unit tests
- [x] All unit tests passing
- [x] Ruff clean
- [x] mypy clean

### Diagnostics

The diagnostics framework is complete.

- [x] Add diagnostics to remaining subsystems
- [x] Review diagnostic coverage
- [x] Add additional runtime diagnostics where useful

---

### Application Logging

Remaining work:

- [x] Instrument remaining subsystems
- [x] Improve logging coverage
- [x] Add additional developer-relevant log messages where appropriate
- [x] Add indentation to application tracing
- [x] Add automatic leave message for application tracing

### Deployment

- [x] Create installable Python package
- [x] Update pyproject.toml package metadata
- [x] Define runtime dependencies
- [x] Define development dependencies
- [x] Verify clean virtual environment installation
- [x] Document installation procedure
- [x] Document supported Python versions
- [x] Test installation on a second system

---

### Configuration

- [x] Persist configuration between sessions
- [x] Remember last ROM directory
- [x] Remember window geometry

---

### Debugger

- [x] Breakpoints
- [x] Run to cursor
- [x] Step over sub-routine call
- [x] Step into sub-routine
- [x] Highlight modified memory cells

---

## Major Refactoring

### Instruction Decoder

- [x] Unify the three independent instruction decoders
- [x] Inventory every place opcode decoding currently occurs
- [x] Design a unified decoded-instruction representation
- [x] Introduce centralized opcode metadata
- [x] Migrate disassembler
- [x] Migrate static analyzer
- [x] Migrate emulator execution
- [x] Remove obsolete decoding logic

---
## Remaining Features

### Remaining integration

- [ ] Review trace output for readability and consistency

---

## Known Issues

---

## Future Enhancements

### Debugger

- [ ] Go to address / Set PC
- [ ] Follow memory writes
- [ ] Search for byte sequence in ROM

### Audio

- [ ] Alternative waveforms (optional)

### Testing

- [ ] Create a regression ROM suite
- [ ] Document expected behaviour of each regression ROM
- [ ] Package regression ROMs with the project

### Development Tools

#### CHIP-8 Assembler

- [ ] Two-pass assembler
- [ ] Labels and forward references
- [ ] Symbol table
- [ ] Expressions and constants
- [ ] `DB` directive
- [ ] `DW` directive
- [ ] `ORG` directive
- [ ] `EQU` directive
- [ ] Binary, decimal and hexadecimal literals
- [ ] Character and string literals
- [ ] Generate CHIP-8 ROM images
- [ ] Listing file generation
- [ ] Error reporting with source line numbers

---



## Project Status

Core emulator:                ██████████ 100%

GUI:                          ██████████ 100%

Debugger:                     ██████████ 100%

Audio:                        ██████████ 100%

Code analysis:                ██████████ 100%

Diagnostics:                  ██████████ 100%

Application logging:          ██████████ 100%

Execution tracing:            ██████████ 100%

Development tools:            ░░░░░░░░░░   0%

Overall project completion: ~98%
