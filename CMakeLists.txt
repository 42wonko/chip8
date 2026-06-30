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
option(CHIP8_RUN_MYPY "Enable mypy target" ON)
option(CHIP8_RUN_RUFF "Enable Ruff target" ON)

###############################################################################
# Python
###############################################################################
find_package(Python3 3.12 REQUIRED COMPONENTS Interpreter)
message(STATUS "Python executable : ${Python3_EXECUTABLE}")
message(STATUS "Python version    : ${Python3_VERSION}")

###############################################################################
# PyQt6
###############################################################################
execute_process(
    COMMAND ${Python3_EXECUTABLE} -c "import PyQt6"
    RESULT_VARIABLE PYQT_RESULT
)

if(NOT PYQT_RESULT EQUAL 0)
    message(FATAL_ERROR "PyQt6 is not installed.")
endif()

###############################################################################
# Doxygen
###############################################################################
if(CHIP8_BUILD_DOCS)
    find_package(Doxygen REQUIRED)
    find_program(GRAPHVIZ_DOT dot)

    if(NOT GRAPHVIZ_DOT)
        message(FATAL_ERROR "Graphviz 'dot' executable not found.")
    endif()
endif()

###############################################################################
# Configure Doxygen
###############################################################################
if(CHIP8_BUILD_DOCS)
    configure_file( ${PROJECT_SOURCE_DIR}/doc/Doxyfile.in ${PROJECT_BINARY_DIR}/Doxyfile @ONLY)
endif()

###############################################################################
# Custom targets
###############################################################################
add_custom_target(
    run COMMAND ${Python3_EXECUTABLE} ${PROJECT_SOURCE_DIR}/src/main.py WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
)

if(CHIP8_BUILD_DOCS)
    add_custom_target(
        docs COMMAND ${DOXYGEN_EXECUTABLE} ${PROJECT_BINARY_DIR}/Doxyfile WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
    )
endif()

###############################################################################
# Ruff
###############################################################################
if(CHIP8_RUN_RUFF)
    add_custom_target( ruff COMMAND ${Python3_EXECUTABLE} -m ruff check src)
endif()

###############################################################################
# mypy
###############################################################################
if(CHIP8_RUN_MYPY)
    add_custom_target( mypy COMMAND ${Python3_EXECUTABLE} -m mypy src)
endif()

###############################################################################
# Tests
###############################################################################
add_custom_target(
    test COMMAND ${Python3_EXECUTABLE} -m pytest
)

