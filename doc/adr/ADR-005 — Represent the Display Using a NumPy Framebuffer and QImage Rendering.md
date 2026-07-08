# ADR-005 — Represent the Display Using a NumPy Framebuffer and QImage Rendering

**Author:** Michael Dlubatz

**Date:** 2026-07-01

**Status:** Accepted

---

## Title

Represent the display as a NumPy-backed framebuffer and render it using
Qt's `QImage`.

---

## Context

The CHIP-8 display consists of a fixed monochrome framebuffer with a
resolution of 64 × 32 pixels.

The graphical user interface must display this framebuffer efficiently
while keeping the emulator independent of the GUI.

Several rendering techniques were considered.

The chosen solution should

- remain simple,
- perform well,
- minimize unnecessary copying,
- integrate naturally with Qt,
- allow future display customization.

---

## Alternatives Considered

### Option 1 — QGraphicsScene / QGraphicsView

Represent each CHIP-8 pixel as an individual graphics item.

Advantages

- Simple conceptual model.
- Good integration with Qt graphics framework.

Disadvantages

- One graphics item per pixel.
- Significant object management overhead.
- Poor scalability.
- Unnecessary complexity for a fixed-size display.

---

### Option 2 — Paint Individual Rectangles

Draw every pixel manually during each paint event.

Advantages

- Straightforward implementation.
- No intermediate image buffer.

Disadvantages

- Thousands of drawing operations per frame.
- Rendering performance depends on painter operations.
- Difficult to optimize.

---

### Option 3 — NumPy Framebuffer + QImage

Maintain the framebuffer as a NumPy array.

Convert the framebuffer into a `QImage` during rendering and display it
using `QPainter`.

Advantages

- Compact framebuffer representation.
- Efficient memory layout.
- Excellent Qt integration.
- Low rendering overhead.
- Supports future color palettes.
- Easy implementation.

Disadvantages

- Requires NumPy.
- Requires conversion to a `QImage` before rendering.

---

## Decision

The logical framebuffer shall be represented as a two-dimensional NumPy
array.

The display widget shall convert the framebuffer into a `QImage` during
painting.

The emulator shall never depend upon Qt classes.

The display widget shall remain responsible for

- pixel scaling,
- rendering,
- color selection,
- repaint scheduling.

The framebuffer shall remain the sole representation of the display
state.

---

## Rationale

The selected approach cleanly separates the logical display from its
graphical representation.

NumPy provides an efficient and compact representation of the
framebuffer while remaining independent of the graphical user
interface.

`QImage` integrates naturally with Qt's painting system and allows the
display to be rendered efficiently without introducing unnecessary
complexity.

This approach also provides a clear path for future enhancements such as

- configurable color palettes,
- display filters,
- screenshots,
- display scaling.

These enhancements can be implemented entirely within the display widget
without modifying the emulator core.

---

## Consequences

### Positive

- GUI-independent framebuffer.
- Efficient memory representation.
- Clean separation of concerns.
- Good rendering performance.
- Easy future enhancements.
- Simple implementation.

### Negative

- Introduces a dependency on NumPy.
- Requires framebuffer-to-image conversion during rendering.

---

## References

- SRDS Chapter 4 — Emulator Core
- SRDS Chapter 5 — Graphical User Interface
- REQ-EMU-312
- REQ-EMU-313
- REQ-GUI-505
- REQ-GUI-506
- REQ-GUI-507
