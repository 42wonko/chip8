from emulator.chip8memory import Chip8Memory


def test_read_write_byte() -> None:
    memory = Chip8Memory()
    memory.write_byte( 0x234, 0xAB)
    assert memory.read_byte( 0x234) == 0xAB

def test_read_write_word() -> None:
    memory = Chip8Memory()
    memory.write_byte( 0x300, 0x12)
    memory.write_byte( 0x301, 0x34)
    assert (memory.read_byte( 0x300) << 8) | memory.read_byte(0x301) == 0x1234


def test_load_rom() -> None:
    memory = Chip8Memory()
    rom = bytes([ 0x60, 0x01, 0x61, 0x02 ])
    memory.load_rom(rom)
    assert (memory.read_byte( 0x200) << 8) | memory.read_byte(0x201) == 0x6001
    assert (memory.read_byte( 0x202) << 8) | memory.read_byte(0x203) == 0x6102

