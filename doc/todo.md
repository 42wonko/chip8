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
- [x] Configuration dialog integration

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

### FULL trace level

- [x] Complete register dump
- [x] I register
- [x] Stack pointer
- [x] Delay timer
- [x] Sound timer

### Testing

- [x] Unit tests updated for logging/tracing architecture
- [x] All unit tests passing
- [x] Ruff clean
- [x] mypy clean

---

## Remaining Features

### Execution Tracing

The execution tracing framework is complete. Remaining work extends 
the amount of information recorded.

#### CHANGES trace level

- [ ] Keyboard events
- [ ] Sound transitions


#### Remaining integration

- [ ] Review trace output for readability and consistency

---

### Diagnostics

The diagnostics framework is complete.

Remaining work:

- [ ] Add diagnostics to remaining subsystems
- [ ] Review diagnostic coverage
- [ ] Add additional runtime diagnostics where useful

---

### Application Logging

The logging framework is complete.

Remaining work:

- [ ] Instrument remaining subsystems
- [ ] Improve logging coverage
- [ ] Add additional developer-relevant log messages where appropriate
- [ ] Add indentation to application tracing
- [ ] Add automatic leave message for application tracing


---

## Known Issues

### Audio

- [ ] Investigate intermittent audio playback on some Linux systems
    - Works reliably on Qt 6.9.x / PipeWire 1.4.x
    - Playback stops after several seconds on Qt 6.6.x / PipeWire 1.0.x
    - Emulator continues to run; only audio is affected
    - Restarting the emulator restores audio
    - Investigation suggests a Qt Multimedia backend compatibility issue
    - readData() stops being called after playback stalls

---

## Future Enhancements

### Configuration

- [ ] Persist configuration between sessions
- [ ] Remember last ROM directory
- [ ] Remember window geometry

### Debugger

- [ ] Breakpoints
- [ ] Run to cursor
- [ ] Go to address
- [ ] Follow memory writes
- [ ] Search for byte sequence in ROM
- [ ] Highlight modified memory cells

### Audio

- [ ] Configurable beep frequency
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

## Major Refactoring

### Instruction Decoder

- [ ] Unify the three independent instruction decoders
    - Emulator execution
    - Static code analyzer
    - Debugger / disassembler
- [ ] Introduce a shared instruction decoder
- [ ] Centralize opcode metadata and decoding logic

---

## Project Status

Core emulator:                ██████████ 100%

GUI:                          ██████████ 100%

Debugger:                     ██████████ 100%

Audio:                        █████████░  95%

Code analysis:                ██████████ 100%

Diagnostics:                  █████████░  90%

Application logging:          █████████░  90%

Execution tracing:            █████████░  90%

Development tools:            ░░░░░░░░░░   0%

Overall project completion: ~97%
