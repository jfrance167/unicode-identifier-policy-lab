"""Whole-envelope admission with exact types and finite structural bounds."""

import json
import os
from pathlib import Path
import re
import stat

MAX_INPUT = 16 * 1024
MAX_ITEMS = 16
MAX_VALUE = 64
MAX_VALUE_BYTES = 256
MAX_STAGE = 256
MAX_STAGE_BYTES = 1024
MAX_OUTPUT = 512 * 1024
SCHEMA = "unicode-policy-lab/1"
POLICIES = ("exact-v1", "nfc-v1", "nfkc-casefold-nfkc-v1")


class LabError(ValueError):
    """A bounded fixed diagnostic; never include input or OS exception text."""


class Unsupported(LabError):
    """Admitted input outside the declared profile/runtime (exit 3)."""


def _keys(value: object, expected: set[str]) -> None:
    if type(value) is not dict or len(value) != len(expected):
        raise LabError("invalid object shape")
    if any(type(key) is not str for key in value) or set(value) != expected:
        raise LabError("invalid object fields")


def _ascii(value: object, pattern: str) -> None:
    if type(value) is not str or re.fullmatch(pattern, value, flags=re.ASCII) is None:
        raise LabError("invalid ASCII label")


def check_text(value: object, scalars: int, byte_limit: int) -> None:
    """Limit scalar strings without deleting controls, formats or whitespace."""
    if type(value) is not str or len(value) > scalars:
        raise LabError("scalar length or type limit")
    for char in value:
        cp = ord(char)
        if 0xD800 <= cp <= 0xDFFF or 0xFDD0 <= cp <= 0xFDEF or cp & 0xFFFF in (0xFFFE, 0xFFFF):
            raise LabError("surrogate or noncharacter")
    if len(value.encode("utf-8")) > byte_limit:
        raise LabError("UTF-8 byte limit")


def validate(document: object) -> None:
    """Validate every record before policy/runtime decisions; shape excludes cycles."""
    _keys(document, {"schema", "policy", "items"})
    _ascii(document["schema"], r"[A-Za-z0-9/_-]{1,64}")
    _ascii(document["policy"], r"[A-Za-z0-9_-]{1,64}")
    items = document["items"]
    if type(items) is not list or len(items) > MAX_ITEMS:
        raise LabError("item list limit or type")
    labels = set()
    total_scalars = total_bytes = 0
    for item in items:
        _keys(item, {"label", "value"})
        _ascii(item["label"], r"[A-Za-z0-9_-]{1,32}")
        if item["label"] in labels:
            raise LabError("duplicate item label")
        labels.add(item["label"])
        check_text(item["value"], MAX_VALUE, MAX_VALUE_BYTES)
        total_scalars += len(item["value"])
        total_bytes += len(item["value"].encode("utf-8"))
    if total_scalars > 1024 or total_bytes > 4096:
        raise LabError("original aggregate limit")


def _reject_number(_token: str):
    raise LabError("numeric tokens forbidden")


def _pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise LabError("duplicate decoded JSON field")
        result[key] = value
    return result


def _preflight(text: str) -> None:
    # This bounds parser recursion; json.loads remains the grammar authority.
    depth, quoted, escaped = 0, False, False
    for char in text:
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in "[{":
            depth += 1
            if depth > 4:
                raise LabError("JSON depth limit")
        elif char in "}]":
            depth -= 1


def parse(raw: bytes) -> dict:
    """Strict exact-bytes UTF-8 JSON admission; no coercion or partial verdict."""
    if type(raw) is not bytes or len(raw) > MAX_INPUT:
        raise LabError("input byte limit or type")
    try:
        text = raw.decode("utf-8", errors="strict")
        if text.startswith("\ufeff"):
            raise LabError("UTF-8 BOM forbidden")
        _preflight(text)
        document = json.loads(text, object_pairs_hook=_pairs, parse_int=_reject_number,
                              parse_float=_reject_number, parse_constant=_reject_number)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise LabError("invalid UTF-8 JSON") from error
    validate(document)
    return document


def _identity(info):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)


def read(path: Path) -> bytes:
    """Bound regular-file reads and detect observed metadata changes, not races."""
    before = path.stat()
    if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_INPUT:
        raise LabError("input must be a bounded regular file")
    flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0)
    with os.fdopen(os.open(path, flags), "rb") as handle:
        opened = os.fstat(handle.fileno())
        if not stat.S_ISREG(opened.st_mode) or _identity(before) != _identity(opened):
            raise LabError("input metadata changed")
        raw = handle.read(MAX_INPUT + 1)
        if len(raw) > MAX_INPUT or len(raw) != opened.st_size:
            raise LabError("input read length changed")
        if _identity(opened) != _identity(os.fstat(handle.fileno())):
            raise LabError("input metadata changed")
        return raw
