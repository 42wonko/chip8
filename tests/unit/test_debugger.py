
"""
@file test_debugger.py
@brief Unit tests for the CHIP-8 debugger.
"""

import unittest
from unittest.mock import Mock

from chip8.debugger import Debugger


class TestDebugger(unittest.TestCase):

    def setUp(self) -> None:
        self.debugger = Debugger()


    def test_set_breakpoint(self) -> None:
        self.debugger.set_breakpoint(0x200)
        self.assertTrue(self.debugger.has_breakpoint(0x200))
        self.assertTrue(self.debugger.is_breakpoint_enabled(0x200))
        self.assertFalse(self.debugger.is_breakpoint_disabled(0x200))
        self.assertTrue(self.debugger.has_breakpoints())


    def test_set_breakpoint_reactivates_disabled_breakpoint(self) -> None:
        self.debugger.disable_breakpoint(0x200)
        self.debugger.set_breakpoint(0x200)
        self.assertTrue(self.debugger.is_breakpoint_enabled(0x200))
        self.assertFalse(self.debugger.is_breakpoint_disabled(0x200))


    def test_toggle_breakpoint_creates_new_breakpoint(self) -> None:
        self.debugger.toggle_breakpoint(0x200)
        self.assertTrue(self.debugger.is_breakpoint_enabled(0x200))


    def test_toggle_breakpoint_disables_active_breakpoint(self) -> None:
        self.debugger.set_breakpoint(0x200)
        self.debugger.toggle_breakpoint(0x200)
        self.assertFalse(self.debugger.is_breakpoint_enabled(0x200))
        self.assertTrue(self.debugger.is_breakpoint_disabled(0x200))


    def test_toggle_breakpoint_enables_disabled_breakpoint(self) -> None:
        self.debugger.disable_breakpoint(0x200)
        self.debugger.toggle_breakpoint(0x200)
        self.assertTrue(self.debugger.is_breakpoint_enabled(0x200))
        self.assertFalse(self.debugger.is_breakpoint_disabled(0x200))


    def test_enable_breakpoint_ignores_unknown_address(self) -> None:
        self.debugger.enable_breakpoint(0x200)
        self.assertFalse(self.debugger.has_breakpoints())


    def test_disable_breakpoint_ignores_unknown_address(self) -> None:
        self.debugger.disable_breakpoint(0x200)
        self.assertFalse(self.debugger.has_breakpoints())


    def test_clear_breakpoint_removes_active_and_disabled_breakpoints(self) -> None:
        self.debugger.set_breakpoint(0x200)
        self.debugger.disable_breakpoint(0x200)
        self.debugger.set_breakpoint(0x202)
        self.debugger.clear_breakpoint(0x200)
        self.assertFalse(self.debugger.is_breakpoint_enabled(0x200))
        self.assertFalse(self.debugger.is_breakpoint_disabled(0x200))
        self.assertTrue(self.debugger.is_breakpoint_enabled(0x202))


    def test_clear_unknown_breakpoint_is_safe(self) -> None:
        self.debugger.clear_breakpoint(0x200)
        self.assertFalse(self.debugger.has_breakpoints())


    def test_clear_all_breakpoints_clears_temporary_breakpoint(self) -> None:
        self.debugger.set_breakpoint(0x200)
        self.debugger.disable_breakpoint(0x202)
        self.debugger.set_temporary_breakpoint(0x204)
        self.debugger.clear_all_breakpoints()
        self.assertFalse(self.debugger.has_breakpoints())
        self.assertIsNone(self.debugger.temporary_breakpoint)


    def test_has_any_breakpoint_matches_active_breakpoint(self) -> None:
        self.debugger.set_breakpoint(0x200)
        self.assertTrue(self.debugger.has_any_breakpoint(0x200))
        self.assertFalse(self.debugger.has_any_breakpoint(0x202))


    def test_disabled_breakpoint_does_not_match(self) -> None:
        self.debugger.disable_breakpoint(0x200)
        self.assertFalse(self.debugger.has_any_breakpoint(0x200))


    def test_temporary_breakpoint_matches_once_then_clears(self) -> None:
        self.debugger.set_temporary_breakpoint(0x204)
        self.assertEqual(self.debugger.temporary_breakpoint, 0x204)
        self.assertTrue(self.debugger.has_any_breakpoint(0x204))
        self.assertIsNone(self.debugger.temporary_breakpoint)
        self.assertFalse(self.debugger.has_any_breakpoint(0x204))


    def test_temporary_breakpoint_does_not_match_other_address(self) -> None:
        self.debugger.set_temporary_breakpoint(0x204)
        self.assertFalse(self.debugger.has_any_breakpoint(0x202))
        self.assertEqual(self.debugger.temporary_breakpoint, 0x204)


    def test_disabled_debugger_does_not_consume_temporary_breakpoint(self) -> None:
        self.debugger.set_temporary_breakpoint(0x204)
        self.debugger.enable(False)
        self.assertFalse(self.debugger.has_any_breakpoint(0x204))
        self.assertEqual(self.debugger.temporary_breakpoint, 0x204)
        self.debugger.enable(True)
        self.assertTrue(self.debugger.has_any_breakpoint(0x204))
        self.assertIsNone(self.debugger.temporary_breakpoint)


    def test_active_and_inactive_breakpoints_return_copies(self) -> None:
        self.debugger.set_breakpoint(0x200)
        self.debugger.set_breakpoint(0x202)
        self.debugger.disable_breakpoint(0x202)
        active = self.debugger.active_breakpoints()
        inactive = self.debugger.inactive_breakpoints()
        active.add(0x204)
        inactive.add(0x206)
        self.assertEqual(self.debugger.active_breakpoints(), {0x200})
        self.assertEqual(self.debugger.inactive_breakpoints(), {0x202})


    def test_read_settings_restores_breakpoints_and_enabled_state(self) -> None:
        settings = Mock()
        settings.value.side_effect = lambda key, default=None, type=None: {
            "debugger/enabled": False,
            "debugger/active_breakpoints": ["512", "516"],
            "debugger/inactive_breakpoints": ["514"]
        }.get(key, default)

        self.debugger.set_breakpoint(0x300)
        self.debugger.set_temporary_breakpoint(0x302)
        self.debugger.read_settings(settings)
        self.assertEqual(self.debugger.active_breakpoints(), {0x200, 0x204})
        self.assertEqual(self.debugger.inactive_breakpoints(), {0x202})
        self.assertIsNone(self.debugger.temporary_breakpoint)
        self.assertFalse(self.debugger.has_any_breakpoint(0x200))


    def test_read_settings_with_none_breakpoint_lists(self) -> None:
        settings = Mock()
        settings.value.side_effect = lambda key, default=None, type=None: {
            "debugger/enabled": True,
            "debugger/active_breakpoints": None,
            "debugger/inactive_breakpoints": None
        }.get(key, default)
        self.debugger.set_breakpoint(0x200)
        self.debugger.disable_breakpoint(0x202)
        self.debugger.read_settings(settings)
        self.assertEqual(self.debugger.active_breakpoints(), set())
        self.assertEqual(self.debugger.inactive_breakpoints(), set())


    def test_write_settings_sorts_breakpoint_addresses(self) -> None:
        settings = Mock()
        self.debugger.set_breakpoint(0x204)
        self.debugger.set_breakpoint(0x200)
        self.debugger.set_breakpoint(0x206)
        self.debugger.set_breakpoint(0x202)
        self.debugger.disable_breakpoint(0x206)
        self.debugger.disable_breakpoint(0x202)
        self.debugger.enable(False)
        self.debugger.write_settings(settings)
        settings.setValue.assert_any_call("debugger/enabled", False)
        settings.setValue.assert_any_call( "debugger/active_breakpoints", [0x200, 0x204])
        settings.setValue.assert_any_call( "debugger/inactive_breakpoints", [0x202, 0x206])


if __name__ == "__main__":
    unittest.main(verbosity=2)

