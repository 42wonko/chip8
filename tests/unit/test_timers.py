from emulator.chip8timers import Chip8Timers


def test_timer_tick() -> None:
    timers = Chip8Timers()
    timers.delay_timer = 2
    timers.sound_timer = 2
    timers.tick()
    assert timers.delay_timer == 1
    assert timers.sound_timer == 1
    timers.tick()
    assert timers.delay_timer == 0
    assert timers.sound_timer == 0
    timers.tick()
    assert timers.delay_timer == 0
    assert timers.sound_timer == 0

