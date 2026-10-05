"""CLI that emits bounded ASCII JSON diagnostics and preserves evidence files."""

import argparse
import io
from pathlib import Path
import sys

from .contract import LabError, Unsupported, parse, read
from .model import analyze, render


class Parser(argparse.ArgumentParser):
    def error(self, _message):
        raise LabError("invalid command arguments")

    def _print_message(self, message, file=None):
        # argparse's default suppresses OSError; propagate checked help delivery.
        if message:
            write_checked(file if file is not None else sys.stderr, message)


def write_checked(handle, content: str) -> None:
    if handle.write(content) != len(content):
        raise OSError("short output write")
    handle.flush()


def _diagnostic(code: int, message: str) -> None:
    # All callers select fixed strings. Filenames, labels and OS errors never leak.
    text = render({"status": "unsupported" if code == 3 else "error", "reason": message})
    write_checked(sys.stderr, text)


def main(argv: list[str] | None = None) -> int:
    parser = Parser(prog="unicode-lab", description="Bounded synthetic Unicode keys; no account or visual-security verdict.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, help="exclusive new ASCII JSON report")
    stdout_delivery = True  # --help can write before argument parsing returns.
    try:
        args = parser.parse_args(argv)
        stdout_delivery = False
        report, code = analyze(parse(read(args.input)))
        content = render(report)
        if args.output is not None:
            if args.output.exists() and args.output.samefile(args.input):
                raise LabError("output aliases input")
            with args.output.open("x", encoding="ascii", newline="\n") as handle:
                write_checked(handle, content)
        else:
            stdout_delivery = True
            write_checked(sys.stdout, content)
        return code
    except Unsupported as error:
        code, message = 3, str(error)
    except LabError as error:
        code, message = 2, str(error)
    except (OSError, UnicodeError, ValueError):
        code, message = 2, "I/O or output delivery failed"
        if stdout_delivery:
            # A real closed pipe must not become exit 120 at interpreter shutdown.
            sys.stdout = io.StringIO()
    try:
        _diagnostic(code, message)
    except (OSError, UnicodeError, LabError):
        # Prevent a second buffered stderr failure at interpreter shutdown.
        sys.stderr = io.StringIO()
        return 2
    return code


if __name__ == "__main__":
    raise SystemExit(main())
