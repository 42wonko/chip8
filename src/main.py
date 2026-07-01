"""
@file main.py

@brief Compatibility wrapper for starting the application.

@details
The real application entry point is implemented in
chip8.__main__. This wrapper allows developers to start
the application directly from the source tree using

    python src/main.py

without requiring installation.

@author
Michael Dlubatz

@copyright
MIT License
"""

from chip8.__main__ import main

if __name__ == "__main__":
    raise SystemExit(main())
