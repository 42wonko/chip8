from emulator.chip8machine import Chip8Machine


def test_fetch_instruction() -> None:
    machine = Chip8Machine()
    machine.memory.write_byte( 0x200, 0x6A)
    machine.memory.write_byte( 0x201, 0x05)
    instruction = machine.fetch_instruction()
    assert instruction.address == 0x200
    assert instruction.opcode == 0x6A05
    assert machine.registers.pc == 0x202
