#Chip-8 documentation

An emulator for the CHIP-8 virtual machine written in Python using PYQT.

## Table of Contents

- [Design Rationale](#rationale)
- [Chip-8 Introduction](#introduction)
- [Supported Features](#features)
- [Dependencies](#dependencies)
- [Op-code Description](#op-codes)
- [GUI Description](#gui-description)
- [External Links](#links)

<a name="rationale"></a>
## Design Rationale

-   **QT-GUI** for simple use. Provides direct visual feedback during program 
    execution (graphics and disassembler), allows single step and adjusting the
    clock frequency.
-   **Separation of GUI and emulation engine**. Perephrial devices like display
    or keyboard are abstracted to enhance reusability.
-   **Emulator engine unit tested**

<a name="introduction"></a>
## Chip-8 Introduction

From Wikipedia, the free encyclopedia
CHIP-8 is an interpreted programming language, developed by Joseph Weisbecker
on his 1802 microprocessor. It was initially used on the COSMAC VIP and Telmac
1800, which were 8-bit microcomputers made in the mid-1970s.

CHIP-8 was designed to use less memory than other programming languages like 
BASIC, while still being easier to program than machine code.[1] The language 
looks like machine code as it uses hexadecimal codes for instructions, but as 
an interpreter, like BASIC, it does not need to be assembled or linked before 
running.

CHIP-8 interpreters have since been made for many devices, such as home 
computers, microcomputers, graphing calculators, mobile phones, and video game 
consoles

<a name="features"></a>
## Supported Features

<a name="dependencies"></a>
## Dependencies
For the initial skeleton, I'll keep the dependencies to the bare minimum:
- PyQt6>=6.7

For the testing phase, add separate dependencies containing:
- pytest>=8.0
- pytest-qt
- ruff
- black
- mypy


<a name="op-codes"></a>
## Op-code Description

<a name="gui-description"></a>
## GUI Description

<a name="links"></a>
## External Links
1) [Wikipedia](https://en.wikipedia.org/wiki/CHIP-8)
