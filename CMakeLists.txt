###############################################################################
#
#  CHIP-8 Emulator
#
#  CMake configuration
#
###############################################################################

cmake_minimum_required(VERSION 3.28)

project(
    CHIP8
    VERSION 0.1.0
    DESCRIPTION "CHIP-8 Emulator"
    LANGUAGES NONE
)

###############################################################################
# Options
###############################################################################
option(CHIP8_BUILD_DOCS "Build Doxygen documentation" ON)
option(CHIP8_ENABLE_MYPY "Enable mypy target" ON)
option(CHIP8_ENABLE_RUFF "Enable Ruff target" ON)

###############################################################################
# Python
###############################################################################
find_package(Python3 3.12 REQUIRED COMPONENTS Interpreter)
message(STATUS "Python executable : ${Python3_EXECUTABLE}")
message(STATUS "Python version    : ${Python3_VERSION}")

###############################################################################
# PyQt6
###############################################################################
execute_process( COMMAND "${Python3_EXECUTABLE}" -c "import PyQt6" RESULT_VARIABLE PYQT_RESULT)

if(NOT PYQT_RESULT EQUAL 0)
    message(FATAL_ERROR "PyQt6 is not installed.")
endif()

###############################################################################
# Doxygen
###############################################################################
if(CHIP8_BUILD_DOCS)
    find_package(Doxygen QUIET)
    if(DOXYGEN_FOUND)
        find_program(GRAPHVIZ_DOT dot)
        if(GRAPHVIZ_DOT AND EXISTS "${PROJECT_SOURCE_DIR}/doc/Doxyfile.in")
            configure_file( "${PROJECT_SOURCE_DIR}/doc/Doxyfile.in" "${PROJECT_BINARY_DIR}/Doxyfile" @ONLY)
            add_custom_target( docs COMMAND ${DOXYGEN_EXECUTABLE} "${PROJECT_BINARY_DIR}/Doxyfile" WORKING_DIRECTORY "${PROJECT_BINARY_DIR}" COMMENT "Generating Doxygen documentation")
        else()
            message(STATUS "Documentation disabled (missing dot or Doxyfile.in).")
        endif()
    else()
        message(STATUS "Doxygen not found.")
    endif()
endif()

###############################################################################
# Custom targets
###############################################################################
add_custom_target(
    run COMMAND "${CMAKE_COMMAND}" -E env PYTHONPATH="${PROJECT_SOURCE_DIR}/src" "${Python3_EXECUTABLE}" -m chip8 WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}" VERBATIM)

if(CHIP8_BUILD_DOCS)
    add_custom_target(
        docs COMMAND "${DOXYGEN_EXECUTABLE}" "${PROJECT_BINARY_DIR}/Doxyfile" WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}"
    )
endif()

###############################################################################
# Ruff
###############################################################################
if(CHIP8_ENABLE_RUFF)
    add_custom_target( ruff COMMAND "${Python3_EXECUTABLE}" -m ruff check src)
endif()

###############################################################################
# mypy
###############################################################################
if(CHIP8_ENABLE_MYPY)
    add_custom_target( mypy COMMAND "${Python3_EXECUTABLE}" -m mypy src)
endif()

###############################################################################
# Tests
###############################################################################
add_custom_target(
    test COMMAND "${Python3_EXECUTABLE}" -m pytest
)

###############################################################################
# Clean Python cache files
###############################################################################

add_custom_target(
    clean_python
    COMMAND ${CMAKE_COMMAND} -E echo "Removing Python cache files..."
    COMMAND find "${PROJECT_SOURCE_DIR}" -type d -name "__pycache__" -exec rm -rf {} +
    COMMAND find "${PROJECT_SOURCE_DIR}" -type f -name "*.pyc" -delete
    COMMAND find "${PROJECT_SOURCE_DIR}" -type f -name "*.pyo" -delete
    COMMAND find "${PROJECT_SOURCE_DIR}" -type d -name ".mypy_cache" -exec rm -rf {} +
    COMMAND find "${PROJECT_SOURCE_DIR}" -type d -name ".ruff_cache" -exec rm -rf {} +
    VERBATIM
)

###############################################################################
# Help
###############################################################################
add_custom_target(
    info 
    COMMAND "${CMAKE_COMMAND}" -E echo ""
    COMMAND "${CMAKE_COMMAND}" -E echo "CHIP-8 Emulator - Available targets"
    COMMAND "${CMAKE_COMMAND}" -E echo "=================================="
    COMMAND "${CMAKE_COMMAND}" -E echo ""
    COMMAND "${CMAKE_COMMAND}" -E echo "run          - Run the emulator"
    COMMAND "${CMAKE_COMMAND}" -E echo "format       - Format Python sources using Ruff"
    COMMAND "${CMAKE_COMMAND}" -E echo "lint         - Run Ruff linter"
    COMMAND "${CMAKE_COMMAND}" -E echo "typecheck    - Run mypy"
    COMMAND "${CMAKE_COMMAND}" -E echo "all_checks   - Run format, lint and mypy"
    COMMAND "${CMAKE_COMMAND}" -E echo "docs         - Generate Doxygen documentation"
    COMMAND "${CMAKE_COMMAND}" -E echo "info         - Show this help"
    COMMAND "${CMAKE_COMMAND}" -E echo "clean_python - Remove Python cache files"
    VERBATIM
)

