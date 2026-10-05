"""Reproduce fixed synthetic policy cases without collecting real identifiers."""

import io
from pathlib import Path
import sys

from unicode_lab.__main__ import Parser, write_checked
from unicode_lab.contract import LabError
from unicode_lab.model import analyze, render

CASES = [
    ("exact-canonical-distinct", "exact-v1", ["\u00c7", "C\u0327"], 0),
    ("nfc-canonical-collision", "nfc-v1", ["\u00c7", "C\u0327"], 1),
    ("nfc-width-distinct", "nfc-v1", ["A", "\uff21"], 0),
    ("overlapping-groups", "nfkc-casefold-nfkc-v1", ["A", "A", "\uff21"], 1),
    ("full-fold-expansion", "nfkc-casefold-nfkc-v1", ["\u00df", "ss"], 1),
    ("last-stage-recomposition", "nfkc-casefold-nfkc-v1", ["\u01f0"], 0),
    ("formats-preserved", "nfkc-casefold-nfkc-v1", ["", "\0", "\u00ad", "\ue000", "\u0378", "\U0001f600"], 0),
    ("scalar-unequal", "nfkc-casefold-nfkc-v1", ["a", "\u0430"], 0),
]


def generate():
    """Return eight reproducible reports; expected statuses are hand-fixed controls."""
    reports = []
    for name, policy, values, expected in CASES:
        document = {"schema": "unicode-policy-lab/1", "policy": policy,
                    "items": [{"label": f"item-{i}", "value": value} for i, value in enumerate(values)]}
        report, code = analyze(document)
        if code != expected:
            raise ValueError("demo status differs from frozen expectation")
        reports.append({"case": name, "exit_status": code, "report": report})
    return {"cases": reports}


def main():
    parser = Parser(prog="unicode-demo", description="Write fresh synthetic demo evidence only")
    parser.add_argument("output", type=Path)
    try:
        args = parser.parse_args()
        content = render(generate())
        with args.output.open("x", encoding="ascii", newline="\n") as handle:
            write_checked(handle, content)
        return 0
    except (OSError, ValueError, UnicodeError):
        sys.stdout = io.StringIO()
        try:
            write_checked(sys.stderr, render({"status": "error", "reason": "demo input or delivery failed"}))
        except (OSError, UnicodeError, LabError):
            sys.stderr = io.StringIO()
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
