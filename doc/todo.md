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
- [x] Application logging
- [x] Configurable application log file
- [x] Optional function tracing
- [x] BufferedFileSink abstraction

### Code Analysis

- [x] Static code analyzer
- [x] Runtime-assisted `BNNN` code analysis
- [x] Dynamic code discovery
- [x] Incremental code analysis
- [x] Automatic Code View updates
- [x] Duplicate runtime target suppression

### Execution Tracing

- [x] Execution tracing infrastructure
- [x] TraceRecord execution model
- [x] ExecutionTraceReporter
- [x] BASIC instruction trace
- [x] Program counter
- [x] Configurable trace file
- [x] Cycle-based trace numbering

### Emulator logging

- [x] Log emulator events to a file
- [x] Configurable log file location
- [x] Configurable log level

### Emulator debug trace

- [x] Function call trace

---

## Remaining Features

### Execution Tracing

#### CHANGES trace level

- [ ] Register changes
- [ ] Timer changes
- [ ] Memory writes
- [ ] Display update events
- [ ] Keyboard events
- [ ] Sound transitions

#### FULL trace level

- [ ] Complete register dump
- [ ] I register
- [ ] Stack pointer
- [ ] Delay timer
- [ ] Sound timer

---

## Known Issues

### Audio

- [ ] Investigate intermittent audio stoppage on some Linux systems
    - Works reliably on openSUSE Tumbleweed
    - Stops after several seconds on some Linux Mint systems
    - Emulator continues to run; only audio stops
    - Restarting the emulator restores audio

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

Diagnostics & tracing:        ██░░░░░░░░  20%

Development tools:            ░░░░░░░░░░   0%

Overall project completion: ~95%

