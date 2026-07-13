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
- [x] Diagnostics view

### Audio

- [x] CHIP-8 beep emulation
- [x] Runtime enable/disable
- [x] Volume control
- [x] Configuration dialog integration

### Infrastructure

- [x] StepResult incremental GUI updates
- [x] Memory range update optimization
- [x] Emulator configuration object
- [x] Diagnostics framework
- [x] Static code analyzer
- [x] Runtime-assisted `BNNN` code analysis
- [x] Incremental code analysis updates
- [x] Duplicate runtime target suppression

---

## Remaining Features

### Emulator Diagnostics

#### Emulator logging

- [ ] Log emulator events to a file
- [ ] Configurable log file location
- [ ] Configurable log level

#### Emulator debug trace

- [ ] Function call trace
- [ ] Optional instruction-level emulator trace
- [ ] Optional analyzer trace
    - Runtime `BNNN` target discovery
    - Incremental code analysis
    - Call graph exploration
    - Recursion detection

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
- [ ] Search for byte sequence in ROM

### Audio

- [ ] Configurable beep frequency
- [ ] Alternative waveforms (optional)

### Testing

- [ ] Create a regression ROM suite
- [ ] Document the expected behavior of each test ROM
- [ ] Package the regression ROMs with the project

### Development Tools

#### CHIP-8 Assembler

- [ ] Two-pass assembler
- [ ] Labels and forward references
- [ ] Symbol table
- [ ] Expressions and constants
- [ ] `DB` directive for arbitrary byte data
- [ ] `DW` directive for 16-bit data
- [ ] `ORG` directive
- [ ] `EQU` directive
- [ ] Binary (`0b`), decimal and hexadecimal (`0x`) literals
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
