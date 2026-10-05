"""Frozen semantic controls and reproducibility of the published synthetic demo."""
import json
import subprocess
import sys
import unittest

from scripts.demo_reports import generate
from tests.test_model import ROOT


class DemoTests(unittest.TestCase):
    def test_eight_cases_and_saved_reproduction(self):
        current = generate()
        saved = json.loads((ROOT / "samples/demo.json").read_text(encoding="ascii"))
        # The artifact records the actual verified runtime; semantic reproduction
        # may be compared across the admitted family without pretending to test it.
        for artifact in (saved, current):
            for case in artifact["cases"]:
                case["report"].pop("runtime")
        self.assertEqual(current, saved)
        self.assertEqual([case["exit_status"] for case in current["cases"]], [0, 1, 0, 1, 1, 0, 0, 0])
        overlap = current["cases"][3]["report"]
        self.assertEqual(overlap["exact_duplicates"][0]["member_count"], 2)
        self.assertEqual(overlap["induced_collisions"][0]["member_count"], 3)
        final = current["cases"][5]["report"]["items"][0]["stages"]
        self.assertEqual([stage["text"] for stage in final], ["\u01f0", "j\u030c", "\u01f0"])
        self.assertEqual(current["cases"][7]["report"]["induced_collisions"], [])

    def test_demo_preserves_existing_evidence(self):
        output = ROOT / "samples/demo.json"
        before = output.read_bytes()
        command = [sys.executable] + (["-O"] if not __debug__ else [])
        result = subprocess.run(command + ["-m", "scripts.demo_reports", str(output)], cwd=ROOT,
                                capture_output=True, timeout=15, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stderr)["reason"], "demo input or delivery failed")
        self.assertEqual(result.stdout, b"")
        self.assertEqual(output.read_bytes(), before)
