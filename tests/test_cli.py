"""Real child-process status/delivery and focused regular-file I/O controls."""

import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from unicode_lab.__main__ import main, write_checked
from unicode_lab.contract import LabError, read
from tests.test_model import ROOT, document


class CliTests(unittest.TestCase):
    def setUp(self):
        base = ROOT / ".private/verification/test-temp"
        base.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=base)
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.source = self.base / "synthetic.json"
        self.source.write_text(json.dumps(document(["A", "\uff21"])), encoding="ascii")

    def child(self, *args):
        command = [sys.executable] + (["-O"] if not __debug__ else [])
        return subprocess.run(command + ["-m", "unicode_lab", *map(str, args)],
                              cwd=ROOT, capture_output=True, timeout=15, check=False)

    def test_child_all_input_statuses_and_escaped_reports(self):
        for doc, expected in ((document(["A", "\uff21"]), 1), (document(["X", "X"]), 0),
                              ({**document([]), "policy": "unknown"}, 3), (document([False]), 2)):
            self.source.write_text(json.dumps(doc), encoding="ascii")
            result = self.child(self.source)
            self.assertEqual(result.returncode, expected, result.stderr)
            channel = result.stdout if expected < 2 else result.stderr
            self.assertTrue(channel.isascii())
            self.assertEqual(json.loads(channel)["status"], "complete" if expected < 2 else
                             "unsupported" if expected == 3 else "error")
            if expected >= 2:
                self.assertEqual(result.stdout, b"")

    def test_arguments_and_paths_do_not_leak(self):
        result = self.child("--unexpected-" + "\u202e" * 200)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)["reason"], "invalid command arguments")
        result = self.child(self.base / ("\u202e" * 50))
        self.assertEqual(result.returncode, 2)
        self.assertLess(len(result.stderr), 200)
        self.assertNotIn(b"\\u202e", result.stderr)
        # OS argv cannot carry NUL, but direct main(argv) callers can.
        with patch("sys.stderr", io.StringIO()) as errors:
            self.assertEqual(main(["inert\0path"]), 2)
            self.assertEqual(json.loads(errors.getvalue())["reason"], "I/O or output delivery failed")

    def test_help_and_help_delivery_failure(self):
        result = self.child("--help")
        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout.isascii())
        self.assertIn(b"unicode-lab", result.stdout)
        class Broken:
            def write(self, text):
                raise OSError("help pipe failed")
        with patch("sys.stdout", Broken()), patch("sys.stderr", io.StringIO()) as errors:
            self.assertEqual(main(["--help"]), 2)
            self.assertEqual(json.loads(errors.getvalue())["reason"], "I/O or output delivery failed")

    def test_exclusive_output_and_input_aliases(self):
        initial = self.source.read_bytes()
        output = self.base / "new.json"
        result = self.child(self.source, "--output", output)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b"")
        self.assertEqual(json.loads(output.read_bytes())["status"], "complete")
        stored = output.read_bytes()
        self.assertEqual(self.child(self.source, "--output", output).returncode, 2)
        self.assertEqual(output.read_bytes(), stored)
        self.assertEqual(self.child(self.source, "--output", self.source).returncode, 2)
        alias = self.base / "hardlink.json"
        os.link(self.source, alias)
        self.assertEqual(self.child(self.source, "--output", alias).returncode, 2)
        self.assertEqual(self.source.read_bytes(), initial)

    def test_actual_closed_pipe_child(self):
        self.source.write_text(json.dumps(document(["\U0001f600" * 64] * 16)), encoding="ascii")
        command = [sys.executable] + (["-O"] if not __debug__ else [])
        with subprocess.Popen(command + ["-m", "unicode_lab", str(self.source)],
                              cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as child:
            child.stdout.close()
            error = child.stderr.read()
            child.wait(timeout=15)
            self.assertEqual(child.returncode, 2, error)
            self.assertEqual(json.loads(error)["reason"], "I/O or output delivery failed")

    def test_regular_file_size_and_exact_byte_read(self):
        self.assertEqual(read(self.source), self.source.read_bytes())
        with self.assertRaises(LabError):
            read(self.base)
        self.source.write_bytes(b" " * 16385)
        with self.assertRaises(LabError):
            read(self.source)

    def test_observed_metadata_changes(self):
        import types
        info = self.source.stat()
        changed = types.SimpleNamespace(st_dev=info.st_dev, st_ino=info.st_ino,
                                        st_size=info.st_size, st_mtime_ns=info.st_mtime_ns + 1,
                                        st_mode=info.st_mode)
        with patch("unicode_lab.contract.os.fstat", side_effect=[info, changed]):
            with self.assertRaisesRegex(LabError, "metadata changed"):
                read(self.source)

    def test_short_and_flush_failure(self):
        class Writer:
            def write(self, text):
                return len(text) - 1

            def flush(self):
                raise AssertionError("not reached")
        with self.assertRaises(OSError):
            write_checked(Writer(), "abc")
        class FlushWriter:
            def write(self, text):
                return len(text)

            def flush(self):
                raise OSError("flush failure")
        with self.assertRaises(OSError):
            write_checked(FlushWriter(), "abc")
        with patch("sys.stdout", FlushWriter()), patch("sys.stderr", io.StringIO()) as errors:
            self.assertEqual(main([str(self.source)]), 2)
            self.assertEqual(json.loads(errors.getvalue())["reason"], "I/O or output delivery failed")

    def test_close_failure_and_error_channel_failure(self):
        @contextlib.contextmanager
        def close_failure(*args, **kwargs):
            yield io.StringIO()
            raise OSError("close failed")
        with patch("unicode_lab.__main__.read", return_value=self.source.read_bytes()):
            with patch.object(Path, "open", close_failure), patch("sys.stderr", io.StringIO()) as errors:
                self.assertEqual(main([str(self.source), "--output", str(self.base / "new")]), 2)
                self.assertEqual(json.loads(errors.getvalue())["reason"], "I/O or output delivery failed")
        class Broken:
            def write(self, text):
                raise OSError("stderr failed")
        with patch("sys.stderr", Broken()):
            self.assertEqual(main([str(self.base / "missing")]), 2)


if __name__ == "__main__":
    unittest.main()
