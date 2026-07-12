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
- [x] Disable realtime display updates

### Audio

- [x] CHIP-8 beep emulation
- [x] Runtime enable/disable
- [x] Volume control
- [x] Configuration dialog integration

### Infrastructure

- [x] StepResult incremental GUI updates
- [x] Memory range update optimization
- [x] Emulator configuration object
- [x] Diagnostics subsystem
- [x] Static analyzer recursion detection
- [x] Runtime-assisted `BNNN` analysis
- [x] Runtime discovery of additional code paths

---

## Remaining Features

### Code Analysis

- [ ] Create a dedicated test ROM that executes `BNNN`
- [ ] Improve static handling of `BNNN`
- [ ] Distinguish unreachable code from unknown data where possible
- [ ] Generate labels for discovered subroutine entry points
- [ ] Display generated labels in the Code View

### Debugger

- [ ] Improve debugger highlighting using code analysis information
- [ ] Highlight current subroutine entry point
- [ ] Highlight active execution path

### Diagnostics

#### Diagnostics View

- [ ] Filter diagnostics by severity
- [ ] Filter diagnostics by source
- [ ] Double-click a diagnostic to jump to the corresponding address

#### Analyzer Diagnostics

- [ ] Warn about unreachable code
- [ ] Warn about suspicious control-flow patterns

---

### Emulator Diagnostics

#### Emulator logging

- [ ] Log emulator events to a file
- [ ] Configurable log file location
- [ ] Configurable log level

#### Emulator debug trace

- [ ] Function call trace
- [ ] Optional instruction-level emulator trace

#### CHIP-8 program trace

- [ ] Instruction trace
- [ ] Register dump
- [ ] Optional memory access logging
- [ ] Trace output to file

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

### Audio

- [ ] Configurable beep frequency
- [ ] Alternative waveforms (optional)

---

## Post-1.0 Architectural Refactoring

### Instruction Decoder

There are currently three independent instruction decoders:

- CPU execution
- Static code analyzer
- Disassembler

Replace them with a single shared decoder.

- [ ] Introduce a canonical instruction decoder
- [ ] Decode every instruction exactly once
- [ ] Share decoded instructions between CPU, analyzer and disassembler
- [ ] Eliminate duplicated opcode decoding logic
- [ ] Centralize instruction metadata

### Code Analyzer

- [ ] Refactor opcode dispatch to use shared instruction metadata

### Controller

- [ ] Continue splitting `controller.py` into logical modules
- [ ] Restrict controller responsibilities to orchestration

### GUI

- [ ] Further separate controller and view responsibilities

### Architecture

- [ ] Continue dependency injection of shared services
- [ ] Keep subsystems independent of the GUI
- [ ] Avoid optional collaborators when dependencies are required

### Performance

- [ ] Cache decoded instructions
- [ ] Profile analyzer performance on large ROM collections
- [ ] Reduce unnecessary GUI refreshes

---

## Testing

- [ ] Create dedicated analyzer test ROMs
- [ ] Add regression tests for recursive CALL detection
- [ ] Add regression tests for maximum stack-depth diagnostics
- [ ] Add regression tests for `BNNN`

---

## Project Status

Core emulator:                ██████████ 100%

GUI:                          ██████████ 100%

Debugger:                     █████████░  95%

Audio:                        █████████░  95%

Code analysis:                █████████░  95%

Diagnostics & tracing:        ███░░░░░░░  30%

Overall project completion: ~95%

