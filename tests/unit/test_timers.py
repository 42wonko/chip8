"""
@file test_timers.py
@brief Test for the CHIP-8 delay and sound timers.
"""
import unittest

from emulator.chip8timers import Chip8Timers


class TestChip8Timers(unittest.TestCase):

    def test_timer_init(self) -> None:
        timers = Chip8Timers()
        timers.delay_timer = 2
        timers.sound_timer = 2
        self.assertEqual(timers.delay_timer, 2)
        self.assertEqual(timers.sound_timer, 2)

    def test_timer_tick(self) -> None:
        timers = Chip8Timers()
        timers.delay_timer = 2
        timers.sound_timer = 2
        timers.tick()
        self.assertEqual(timers.delay_timer, 1)
        self.assertEqual(timers.sound_timer, 1)

    def test_timer_stop(self) -> None:
        timers = Chip8Timers()
        timers.delay_timer = 2
        timers.sound_timer = 2
        timers.tick()
        timers.tick()
        timers.tick()
        self.assertEqual(timers.delay_timer, 0)
        self.assertEqual(timers.sound_timer, 0)

    def test_timer_reset(self) -> None:
        timers = Chip8Timers()
        timers.delay_timer = 2
        timers.sound_timer = 2
        self.assertEqual(timers.delay_timer, 2)
        self.assertEqual(timers.sound_timer, 2)
        timers.reset()
        self.assertEqual(timers.delay_timer, 0)
        self.assertEqual(timers.sound_timer, 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)

