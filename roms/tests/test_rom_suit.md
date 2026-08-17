# CHIP-8 Regression ROM Test Suite

## Purpose

The regression ROM suite consists of small, deterministic CHIP-8 programs designed to exercise specific emulator behaviour.

Unlike external CHIP-8 games, these ROMs are intentionally under our control. Each ROM has a narrow purpose and a predictable execution path, making it suitable for regression testing after changes to the emulator core, instruction execution, code analysis, debugging, logging or tracing.

The ROMs are intentionally simple. They do not attempt to provide visual output or user-facing functionality unless that behaviour is itself the subject of the test.

---

## ROM 1 — Basic Arithmetic Loop

### Test code

```text
60 01 61 02 80 14 70 01 12 08 12 08
```

### Disassembly

```text
200 6001  LD V0, 01
202 6102  LD V1, 02
204 8014  ADD V0, V1
206 7001  ADD V0, 01
208 1208  JP 208
20A 1208  JP 208
```

### Purpose

Tests basic register manipulation, arithmetic and unconditional branching.

The ROM performs:

1. Load `1` into `V0`.
2. Load `2` into `V1`.
3. Add `V1` to `V0`.
4. Add `1` to `V0`.
5. Enter an infinite loop.

After the initial setup, `V0` reaches `4` and then increases by one on every iteration of the loop.

### Expected behaviour

After the first four instructions:

```text
V0 = 04
V1 = 02
PC  = 208
```

The emulator then repeatedly executes:

```text
208: 1208
```

`V0` continues increasing and eventually wraps around from `FF` to `00`.

### Instructions exercised

* `6XNN` — `LD VX, NN`
* `8XY4` — `ADD VX, VY`
* `7XNN` — `ADD VX, NN`
* `1NNN` — `JP NNN`

---

## ROM 2 — Conditional Skip

### Test code

```text
60 00 30 00 61 01 61 02 70 01 30 03 12 02 12 0E
```

### Disassembly

```text
200 6000  LD V0, 00
202 3000  SE V0, 00
204 6101  LD V1, 01
206 6102  LD V1, 02
208 7001  ADD V0, 01
20A 3003  SE V0, 03
20C 1202  JP 202
20E 120E  JP 20E
```

### Purpose

Tests conditional skipping and the interaction between a skip instruction and a loop.

The first `SE` is initially true, so the first `LD V1, 01` is skipped. The program then increments `V0` and returns to the comparison.

On subsequent iterations the first `SE` is false, so `V1` is first set to `01` and then immediately to `02`.

When `V0` reaches `03`, the second `SE` becomes true and skips the backward jump.

### Expected behaviour

The program eventually reaches:

```text
20E: 120E
```

and remains there indefinitely.

Expected final state includes:

```text
V0 = 03
V1 = 02
PC  = 20E
```

### Instructions exercised

* `6XNN` — `LD VX, NN`
* `3XNN` — `SE VX, NN`
* `7XNN` — `ADD VX, NN`
* `1NNN` — `JP NNN`

---

## ROM 3 — Subroutine Call and Return

### Test code

```text
22 06 60 01 12 0A 61 02 00 EE
```

### Disassembly

```text
200 2206  CALL 206
202 6001  LD V0, 01
204 120A  JP 20A
206 6102  LD V1, 02
208 00EE  RET
```

### Purpose

Tests subroutine invocation and return.

Execution begins with a call to address `206`. The subroutine sets `V1` and returns to the instruction following the `CALL`.

### Expected behaviour

The call at `200` pushes the return address onto the stack.

The subroutine executes:

```text
206: LD V1, 02
208: RET
```

Execution then resumes at:

```text
202: LD V0, 01
```

Afterward the program jumps to `20A`, which is outside the supplied ROM.

### Expected state before leaving the ROM

```text
V0 = 01
V1 = 02
SP  = original stack level
```

### Instructions exercised

* `2NNN` — `CALL NNN`
* `6XNN` — `LD VX, NN`
* `00EE` — `RET`
* `1NNN` — `JP NNN`

---

## ROM 4 — Arithmetic and Carry/Borrow Flags

### Test code

```text
60 0A 61 05 80 14 62 03 80 24 63 0F 80 35 12 0E
```

### Disassembly

```text
200 600A  LD V0, 0A
202 6105  LD V1, 05
204 8014  ADD V0, V1
206 6203  LD V2, 03
208 8024  ADD V0, V2
20A 630F  LD V3, 0F
20C 8035  SUB V0, V3
20E 120E  JP 20E
```

### Purpose

Tests register arithmetic, addition with carry and subtraction with borrow/carry flag handling.

The calculation proceeds as follows:

```text
V0 = 0A
V1 = 05
V0 = V0 + V1 = 0F

V2 = 03
V0 = V0 + V2 = 12

V3 = 0F
V0 = V0 - V3 = 03
```

The subtraction also tests the expected `VF` result for a subtraction that does not borrow.

### Expected behaviour

The ROM eventually loops at `20E`.

Expected final state:

```text
V0 = 03
V1 = 05
V2 = 03
V3 = 0F
VF = 01
PC = 20E
```

### Instructions exercised

* `6XNN` — `LD VX, NN`
* `8XY4` — `ADD VX, VY`
* `8XY5` — `SUB VX, VY`
* `1NNN` — `JP NNN`

---

## ROM 5 — Timer Access

### Test code

```text
60 05 F0 15 F0 18 F0 07 70 01 12 06
```

### Disassembly

```text
200 6005  LD V0, 05
202 F015  LD DT, V0
204 F018  LD ST, V0
206 F007  LD V0, DT
208 7001  ADD V0, 01
20A 1206  JP 206
```

### Purpose

Tests the delay timer and sound timer instructions, as well as reading the delay timer back into a register.

The initial value `5` is written to both timers. The program then reads the delay timer and increments `V0` before returning to the timer read.

### Expected behaviour

The timers are initially set from `V0`:

```text
DT = 05
ST = 05
```

The emulator's hardware timer continues to decrement them independently at the configured timer frequency.

The CPU repeatedly executes the loop beginning at `206`.

Because `V0` is repeatedly loaded from `DT`, its value follows the current delay timer and is then incremented by one.

### Instructions exercised

* `6XNN` — `LD VX, NN`
* `FX15` — `LD DT, VX`
* `FX18` — `LD ST, VX`
* `FX07` — `LD VX, DT`
* `7XNN` — `ADD VX, NN`
* `1NNN` — `JP NNN`

---

## ROM 6 — Register Store to Memory

### Test code

```text
60 01 61 02 62 03 A3 00 F2 55 12 0A
```

### Disassembly

```text
200 6001  LD V0, 01
202 6102  LD V1, 02
204 6203  LD V2, 03
206 A300  LD I, 300
208 F255  LD [I], V2
20A 120A  JP 20A
```

### Purpose

Tests storing a range of registers to memory using `FX55`.

Before the store:

```text
V0 = 01
V1 = 02
V2 = 03
I  = 300
```

The `FX55` instruction stores `V0` through `V2` starting at address `300`.

### Expected memory

```text
300: 01
301: 02
302: 03
```

The program then enters an infinite loop at `20A`.

### Instructions exercised

* `6XNN` — `LD VX, NN`
* `ANNN` — `LD I, NNN`
* `FX55` — `LD [I], VX`
* `1NNN` — `JP NNN`

---

## ROM 7 — Drawing and Collision Detection

### Test code

```text
60 00 61 00 A3 00 D0 11 D0 11 12 0A
```

followed by zero-filled memory up to address `300`, with:

```text
300: FF
```

### Disassembly

```text
200 6000  LD V0, 00
202 6100  LD V1, 00
204 A300  LD I, 300
206 D011  DRW V0, V1, 1
208 D011  DRW V0, V1, 1
20A 120A  JP 20A
```

### Purpose

Tests sprite drawing and collision detection.

The sprite consists of one byte:

```text
FF
```

which represents eight set pixels.

The sprite is drawn twice at the same position.

### Expected behaviour

The first draw turns the eight pixels on.

The second draw XORs the same pixels and therefore turns them off again. The second draw must report a collision through `VF`.

After the second draw:

```text
VF = 01
```

and the affected pixels are cleared again.

The program then loops at `20A`.

### Instructions exercised

* `6XNN` — `LD VX, NN`
* `ANNN` — `LD I, NNN`
* `DXYN` — `DRW VX, VY, N`
* `1NNN` — `JP NNN`

### Additional purpose

The large zero-filled region between the executable code and address `300` deliberately separates program code from sprite data. This also provides useful material for testing code analysis and Code View classification.

---

## ROM 8 — Keyboard Input and Skip Instructions

### Test code

```text
60 00 E0 9E 61 01 61 02 E0 A1 62 01 62 02 F0 0A 12 00
```

### Disassembly

```text
200 6000  LD V0, 00
202 E09E  SKP V0
204 6101  LD V1, 01
206 6102  LD V1, 02
208 E0A1  SKNP V0
20A 6201  LD V2, 01
20C 6202  LD V2, 02
20E F00A  LD V0, K
210 1200  JP 200
```

### Purpose

Tests keyboard-dependent skip instructions and blocking keyboard input.

The program uses key `0` for the keyboard tests.

`SKP V0` conditionally skips the next instruction when key `0` is pressed. `SKNP V0` performs the inverse test when the key is not pressed. `FX0A` then waits for a key event and stores the resulting key value in `V0`.

### Expected behaviour

The exact values of `V1` and `V2` depend on the keyboard state when the corresponding skip instructions execute.

The `FX0A` instruction blocks until the emulator receives the required keyboard event.

Once the key operation completes, execution returns to `200` and repeats.

### Instructions exercised

* `6XNN` — `LD VX, NN`
* `EX9E` — `SKP VX`
* `EXA1` — `SKNP VX`
* `FX0A` — `LD VX, K`
* `1NNN` — `JP NNN`

---

## ROM 9 — BNNN Runtime Code Discovery

### Test code

```text
60 04 B2 06 00 00 61 01 62 02 63 03 12 0C
```

### Disassembly

```text
200 6004  LD V0, 04
202 B206  JP V0, 206
204 0000  DATA / unreachable
206 6101  LD V1, 01
208 6202  LD V2, 02
20A 6303  LD V3, 03
20C 120C  JP 20C
```

### Purpose

Tests the special runtime behaviour of `BNNN`.

The target is calculated from the address encoded in the instruction and the current value of `V0`:

```text
BNNN = 206 + V0
     = 206 + 4
     = 20A
```

The important purpose of this ROM is not merely testing execution. It also exercises the emulator's runtime-assisted code analysis.

### Expected behaviour

The instruction at `202` causes execution to leave the statically obvious linear path.

The code analyzer must be able to discover the runtime target and update the Code View accordingly.

The bytes at `204` are not executed.

Execution eventually reaches the loop at `20C`.

### Instructions exercised

* `6XNN` — `LD VX, NN`
* `BNNN` — `JP V0, NNN`
* `1NNN` — `JP NNN`

### Code-analysis behaviour

This ROM is specifically useful for verifying:

* runtime `BNNN` target observation
* dynamic code discovery
* Code View refresh
* correct classification of unreachable bytes
* suppression of duplicate runtime targets

---

## ROM 10 — Memory Store, Timers and Subroutine

### Test code

```text
60 01 61 02 80 14 A3 00 F1 55 62 00 F2 15 F2 18
22 20 12 0E 00 00 00 00 00 00 63 01 70 01 00 EE
```

### Intended disassembly

```text
200 6001  LD V0, 01
202 6102  LD V1, 02
204 8014  ADD V0, V1
206 A300  LD I, 300
208 F155  LD [I], V1
20A 6200  LD V2, 00
20C F215  LD DT, V2
20E F218  LD ST, V2
210 2220  CALL 220
212 120E  JP 20E
...
220 6301  LD V3, 01
222 7001  ADD V0, 01
224 00EE  RET
```

### Purpose

Combines several subsystems in one small program:

* register arithmetic
* memory addressing
* register-to-memory storage
* timer writes
* subroutine calls
* subroutine returns

This makes the ROM useful as a small integration test rather than testing one instruction in isolation.

### Instructions exercised

* `6XNN` — `LD VX, NN`
* `8XY4` — `ADD VX, VY`
* `ANNN` — `LD I, NNN`
* `FX55` — `LD [I], VX`
* `FX15` — `LD DT, VX`
* `FX18` — `LD ST, VX`
* `2NNN` — `CALL NNN`
* `00EE` — `RET`
* `1NNN` — `JP NNN`

---

# Regression Coverage

The suite deliberately combines instruction-level tests with a few integration-oriented tests.

| ROM | Primary purpose                                  |
| --- | ------------------------------------------------ |
| 1   | Basic register loading and arithmetic            |
| 2   | Conditional skips and branching                  |
| 3   | CALL/RET and stack handling                      |
| 4   | Arithmetic flags                                 |
| 5   | Delay/sound timer access                         |
| 6   | Register-to-memory transfer                      |
| 7   | Sprite drawing and collision detection           |
| 8   | Keyboard input and keyboard-dependent skips      |
| 9   | `BNNN` and runtime code discovery                |
| 10  | Combined memory, timers and subroutine behaviour |

The suite therefore provides controlled coverage of the emulator's most important execution paths without depending on the behaviour of third-party games.

## Relationship to automated tests

The regression ROMs complement the unit-test suite rather than replacing it.

Unit tests are appropriate for checking individual operations and internal components. The regression ROMs exercise those operations through the actual emulator execution path:

```text
ROM
 │
 ▼
Chip8Machine
 │
 ├── ISA decode
 ├── ISA execute
 ├── memory
 ├── registers
 ├── timers
 ├── display
 ├── keyboard
 └── stack
```

This makes the ROM suite particularly useful after changes to the instruction execution architecture, debugger, code analysis, tracing or other components that interact with the emulator core.

## Regression procedure

For each ROM:

1. Load the ROM into the emulator.
2. Reset the emulator.
3. Run the ROM.
4. Observe the expected final or steady-state behaviour described above.
5. Inspect the Code View where the ROM is intended to exercise code analysis.
6. Inspect the execution trace where instruction sequencing or state changes are relevant.
7. Confirm that no unexpected diagnostics or exceptions are produced.

The ROMs should remain intentionally small and deterministic. When a new emulator feature or refactoring changes their behaviour, the corresponding ROM documentation should be updated together with the implementation and automated tests.
