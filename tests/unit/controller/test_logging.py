from datetime import datetime
import tempfile
import unittest
from pathlib import Path

from chip8.isa.classicisa import ClassicInstructionSetArchitecture
from chip8.isa.instruction import Instruction
from chip8.isa.instructionid import InstructionId
from controller.diagnostic import DiagnosticSource
from controller.emulatorconfiguration import EmulatorConfiguration, TraceLevel
from controller.logging import ApplicationLogger, ExecutionTracer, LogManager, SessionHeader
from controller.sessionheader import SessionHeader
from emulator.tracerecord import TraceRecord, KeyExecutionEvent

from tests.helpers import create_registers

class ApplicationLoggerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.logger = ApplicationLogger()
        self.addCleanup(self.logger.disable)
        self.filename = str(Path(self.temp_dir.name) / "application.log")

    def test_messages_are_ignored_while_disabled(self) -> None:
        self.logger.set_filename(self.filename)
        self.logger.info(DiagnosticSource.UNIT_TEST, "not logged")

        self.assertFalse(Path(self.filename).exists())

    def test_all_severities_are_written_when_enabled(self) -> None:
        self.logger.set_filename(self.filename)
        self.logger.enable()

        self.logger.info(DiagnosticSource.CONTROLLER, "information")
        self.logger.warning(DiagnosticSource.EMULATOR, "warning")
        self.logger.error(DiagnosticSource.AUDIO, "error")
        self.logger.disable()

        contents = Path(self.filename).read_text(encoding="utf-8")
        self.assertIn("[INFO]", contents)
        self.assertIn("[WARNING]", contents)
        self.assertIn("[ERROR]", contents)
        self.assertIn("information", contents)
        self.assertIn("warning", contents)
        self.assertIn("error", contents)

    def test_enable_without_filename_does_not_open_sink(self) -> None:
        self.logger.enable()

        self.assertTrue(self.logger._enabled)
        self.assertFalse(self.logger._sink.is_open())

    def test_setting_filename_while_enabled_opens_new_file(self) -> None:
        self.logger.enable()
        self.logger.set_filename(self.filename)
        self.logger.info(DiagnosticSource.CONTROLLER, "after filename")
        self.logger.disable()

        self.assertIn(
            "after filename",
            Path(self.filename).read_text(encoding="utf-8")
        )

    def test_enable_and_disable_are_idempotent(self) -> None:
        self.logger.set_filename(self.filename)

        self.logger.enable()
        self.logger.enable()
        self.logger.info(DiagnosticSource.CONTROLLER, "once")
        self.logger.disable()
        self.logger.disable()

        contents = Path(self.filename).read_text(encoding="utf-8")
        self.assertEqual(contents.count("once"), 1)

    def test_function_trace_is_suppressed_by_default(self) -> None:
        self.logger.set_filename(self.filename)
        self.logger.enable()
        self.logger.enter(DiagnosticSource.CONTROLLER, "example")
        self.logger.leave(DiagnosticSource.CONTROLLER, "example")
        self.logger.disable()

        contents = Path(self.filename).read_text(encoding="utf-8")
        self.assertNotIn("ENTER", contents)
        self.assertNotIn("LEAVE", contents)

    def test_function_trace_records_nested_calls(self) -> None:
        self.logger.set_filename(self.filename)
        self.logger.enable_function_trace(True)
        self.logger.enable()

        self.logger.enter(DiagnosticSource.CONTROLLER, "outer")
        self.logger.enter(DiagnosticSource.EMULATOR, "inner")
        self.logger.leave(DiagnosticSource.EMULATOR, "inner")
        self.logger.leave(DiagnosticSource.CONTROLLER, "outer")
        self.logger.disable()

        contents = Path(self.filename).read_text(encoding="utf-8")
        self.assertIn("outer() ENTER", contents)
        self.assertIn("inner() ENTER", contents)
        self.assertIn("inner() LEAVE", contents)
        self.assertIn("outer() LEAVE", contents)
        self.assertIn("    ", contents)

    def test_leave_without_prior_enter_does_not_make_indent_negative(self) -> None:
        self.logger.set_filename(self.filename)
        self.logger.enable_function_trace(True)
        self.logger.enable()

        self.logger.leave(DiagnosticSource.CONTROLLER, "standalone")
        self.logger.info(DiagnosticSource.CONTROLLER, "after leave")
        self.logger.disable()

        contents = Path(self.filename).read_text(encoding="utf-8")
        self.assertIn("standalone() LEAVE", contents)
        self.assertIn("after leave", contents)

    def test_reset_clears_function_trace_indentation(self) -> None:
        self.logger.set_filename(self.filename)
        self.logger.enable_function_trace(True)
        self.logger.enable()

        self.logger.enter(DiagnosticSource.CONTROLLER, "outer")
        self.logger.reset()
        self.logger.info(DiagnosticSource.CONTROLLER, "after reset")
        self.logger.disable()

        contents = Path(self.filename).read_text(encoding="utf-8")
        self.assertIn("after reset", contents)
        self.assertNotIn("    ", contents.split("after reset")[0][-4:])

class ExecutionTracerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.filename = str(Path(self.temp_dir.name) / "trace.log")
        self.tracer = ExecutionTracer()
        self.addCleanup(self.tracer.disable)
        self.tracer.set_filename(self.filename)
        self.tracer.set_isa(ClassicInstructionSetArchitecture())

    def make_record(
        self,
        before=None,
        after=None,
        memory_range: tuple[int, int] | None = None,
        display_changed: bool = False,
        delay_before: int = 0,
        delay_after: int = 0,
        sound_before: int = 0,
        sound_after: int = 0
    ) -> TraceRecord:
        if before is None:
            before = create_registers()
        if after is None:
            after = before.copy()

        instruction = Instruction(
            address=before.pc,
            opcode=0x6001,
            id=InstructionId.LD_BYTE,
            x=0,
            y=0,
            n=1,
            nn=1,
            nnn=1
        )

        return TraceRecord(
            cycle=1,
            instruction=instruction,
            registers_before=before,
            registers_after=after,
            delay_timer_before=delay_before,
            delay_timer_after=delay_after,
            sound_timer_before=sound_before,
            sound_timer_after=sound_after,
            memory_range=memory_range,
            display_changed=display_changed
        )

    def test_trace_key_event_none_does_not_write_output(self) -> None:
        self.tracer.enable()
        self.tracer.trace_key_event(3, KeyExecutionEvent.NONE, 0xA)
        self.tracer.disable()
        contents = Path(self.filename).read_text(encoding="utf-8")
        self.assertEqual(contents, "")

    def test_trace_key_event_unknown_event_writes_empty_line(self) -> None:
        event = object.__new__(KeyExecutionEvent)
        self.tracer.enable()
        self.tracer.trace_key_event(3, event, 0xA)
        self.tracer.disable()
        contents = Path(self.filename).read_text(encoding="utf-8")
        self.assertEqual(contents, "\n")

    def test_application_header_without_logging_details(self) -> None:
        logger = ApplicationLogger()
        logger.set_filename(self.filename)
        logger.enable()
        header = SessionHeader(
            title="Test",
            application="CHIP-8",
            version="1.0",
            python_version="3.x",
            timestamp=datetime(2026, 1, 1),
            logging=None
        )

        logger.write_header(header)
        logger.disable()
        contents = Path(self.filename).read_text(encoding="utf-8")
        self.assertIn("CHIP-8 - Test", contents)
        self.assertNotIn("Logging         :", contents)

    def test_execution_trace_header_without_trace_level(self) -> None:
        self.tracer.set_filename(self.filename)
        self.tracer.enable()
        header = SessionHeader(
            title="Test",
            application="CHIP-8",
            version="1.0",
            python_version="3.x",
            timestamp=datetime(2026, 1, 1),
            trace_level=None
        )
        self.tracer.write_header(header)
        self.tracer.disable()
        contents = Path(self.filename).read_text(encoding="utf-8")
        self.assertIn("CHIP-8 - Test", contents)
        self.assertNotIn("Trace level     :", contents)

    def test_enable_without_filename_does_not_open_sink(self) -> None:
        tracer = ExecutionTracer()
        tracer.enable()
        self.assertTrue(tracer._enabled)
        self.assertEqual(tracer._filename, "")
        tracer.disable()


    def test_setting_filename_while_enabled_opens_sink(self) -> None:
        self.tracer.enable()
        self.tracer.set_filename(self.filename)
        self.tracer.trace_instruction(self.make_record())
        self.tracer.disable()
        contents = Path(self.filename).read_text(encoding="utf-8")
        self.assertIn("6001", contents)

    def test_changes_trace_without_memory_update(self) -> None:
        self.tracer.set_level(TraceLevel.CHANGES)
        self.tracer.enable()
        self.tracer.trace_instruction(self.make_record(memory_range=None))
        self.tracer.disable()
        contents = Path(self.filename).read_text(encoding="utf-8")
        self.assertIn("6001", contents)
        self.assertNotIn("MEM:", contents)

    def test_trace_key_down_event(self) -> None:
        self.tracer.enable()
        self.tracer.trace_key_event(3, KeyExecutionEvent.KEY_DOWN, 0xA)
        self.tracer.disable()
        contents = Path(self.filename).read_text(encoding="utf-8")
        self.assertIn("000003 KEY DOWN <A>", contents)

    def test_trace_is_ignored_while_disabled(self) -> None:
        self.tracer.trace_instruction(self.make_record())

        self.assertFalse(Path(self.filename).exists())

    def test_instruction_trace_requires_isa_when_enabled(self) -> None:
        self.tracer._isa = None
        self.tracer.enable()

        with self.assertRaisesRegex(
            RuntimeError,
            "Instruction set architecture has not been configured."
        ):
            self.tracer.trace_instruction(self.make_record())

    def test_basic_trace_contains_cycle_address_opcode_and_mnemonic(self) -> None:
        self.tracer.enable()
        self.tracer.trace_instruction(self.make_record())
        self.tracer.disable()

        contents = Path(self.filename).read_text(encoding="utf-8")
        self.assertIn("000001", contents)
        self.assertIn("200", contents)
        self.assertIn("6001", contents)
        self.assertIn("LD V0, 01", contents)

    def test_changes_trace_includes_changed_registers_timers_memory_and_display(self) -> None:
        before = create_registers()
        after = before.copy()
        after.pc = before.pc + 2
        after.i = 0x345
        after.sp = 1
        after.write_register(0, 0x12)

        self.tracer.set_level(TraceLevel.CHANGES)
        self.tracer.enable()
        self.tracer.trace_instruction(
            self.make_record(
                before=before,
                after=after,
                memory_range=(0x300, 0x301),
                display_changed=True,
                delay_before=1,
                delay_after=2,
                sound_before=3,
                sound_after=4
            )
        )
        self.tracer.disable()

        contents = Path(self.filename).read_text(encoding="utf-8")
        for expected in (
            "PC:",
            "I:",
            "SP:",
            "DT:",
            "ST:",
            "V0:",
            "MEM:",
            "DISPLAY UPDATED"
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, contents)

    def test_changes_trace_formats_single_address_memory_update(self) -> None:
        self.tracer.set_level(TraceLevel.CHANGES)
        self.tracer.enable()
        self.tracer.trace_instruction( self.make_record(memory_range=(0x300, 0x300)))
        self.tracer.disable()
        contents = Path(self.filename).read_text(encoding="utf-8")
        self.assertIn("MEM: 0x300 UPDATED", contents)

    def test_full_trace_includes_all_registers(self) -> None:
        registers = create_registers()
        for index in range(16):
            registers.write_register(index, index)
        self.tracer.set_level(TraceLevel.FULL)
        self.tracer.enable()
        self.tracer.trace_instruction( self.make_record(after=registers))
        self.tracer.disable()
        contents = Path(self.filename).read_text(encoding="utf-8")
        self.assertIn("V0=0x00", contents)
        self.assertIn("V7=0x07", contents)
        self.assertIn("V8=0x08", contents)
        self.assertIn("VF=0x0F", contents)


    def test_enable_is_idempotent(self) -> None:
        self.tracer.enable()
        self.tracer.enable()
        self.assertTrue(self.tracer._enabled)
        self.tracer.disable()


    def test_trace_key_event_writes_key_up_and_key_down(self) -> None:
        self.tracer.enable()
        self.tracer.trace_key_event(1, KeyExecutionEvent.KEY_DOWN, 0xA)
        self.tracer.trace_key_event(2, KeyExecutionEvent.KEY_UP, 0x3)
        self.tracer.disable()
        contents = Path(self.filename).read_text(encoding="utf-8")
        self.assertIn("000001 KEY DOWN <A>", contents)
        self.assertIn("000002 KEY UP   <3>", contents)


    def test_none_key_event_writes_nothing(self) -> None:
        self.tracer.enable()
        self.tracer.trace_key_event(1, KeyExecutionEvent.NONE, 0xA)
        self.tracer.disable()
        contents = Path(self.filename).read_text(encoding="utf-8")
        self.assertEqual(contents, "")


class LogManagerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.log_filename = str(Path(self.temp_dir.name) / "application.log")
        self.trace_filename = str(Path(self.temp_dir.name) / "execution.log")
        self.manager = LogManager()

    def test_configure_enables_logging_and_trace_and_writes_headers(self) -> None:
        configuration = EmulatorConfiguration(
            logging_enabled=True,
            logging_enabled_info=True,
            logging_enabled_warning=True,
            logging_enabled_error=True,
            function_trace_enabled=True,
            log_filename=self.log_filename,
            execution_trace_enabled=True,
            trace_filename=self.trace_filename,
            trace_level=TraceLevel.CHANGES
        )

        self.manager.configure(configuration)

        log_contents = Path(self.log_filename).read_text(encoding="utf-8")
        trace_contents = Path(self.trace_filename).read_text(encoding="utf-8")

        self.assertIn("Logging", log_contents)
        self.assertIn("Information", log_contents)
        self.assertIn("Warnings", log_contents)
        self.assertIn("Errors", log_contents)
        self.assertIn("Function trace", log_contents)
        self.assertIn("Execution Trace", trace_contents)
        self.assertIn("CHANGES", trace_contents)

    def test_configure_disables_logging_and_trace(self) -> None:
        configuration = EmulatorConfiguration(
            logging_enabled=False,
            execution_trace_enabled=False,
            log_filename=self.log_filename,
            trace_filename=self.trace_filename
        )

        self.manager.configure(configuration)

        self.assertFalse(self.manager._logger._enabled)
        self.assertFalse(self.manager._tracer._enabled)

    def test_reset_resets_application_log_indentation(self) -> None:
        self.manager._logger._indent_level = 3

        self.manager.reset()

        self.assertEqual(self.manager._logger._indent_level, 0)

    def test_reporter_accessors_return_reporters(self) -> None:
        self.assertIsNotNone(
            self.manager.application_logger(DiagnosticSource.CONTROLLER)
        )
        self.assertIsNotNone(self.manager.execution_trace_reporter())

if __name__ == "__main__":
    unittest.main()

