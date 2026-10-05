"""Explicit ordered keys and complete grouping over bounded synthetic strings."""

import json
import platform
import sys
import unicodedata

from .contract import (LabError, Unsupported, MAX_OUTPUT, MAX_STAGE, MAX_STAGE_BYTES,
                       SCHEMA, POLICIES, check_text, validate)

ASSUMPTIONS = [
    "Synthetic strings only; admitted text is not a valid-account recommendation.",
    "Equality is exact scalar equality after the named ordered policy.",
    "No visual identity, authenticity, authorization or spoof-resistance verdict.",
    "Original and intermediate text are reversible evidence, not redaction.",
    "No whitespace, default-ignorable or format-control deletion.",
    "NFKC/casefold/NFKC is this lab profile, not official toNFKC_Casefold.",
    "Scalar length is not grapheme count, display width or UTF-16 length.",
]


def runtime() -> dict:
    return {"implementation": platform.python_implementation(),
            "python": platform.python_version(), "ucd": unicodedata.unidata_version}


def _guard_runtime() -> None:
    if sys.implementation.name != "cpython" or sys.version_info[:2] != (3, 13) or unicodedata.unidata_version != "15.1.0":
        raise Unsupported("runtime outside CPython 3.13 and UCD 15.1.0 contract")


def _evidence(text: str) -> dict:
    return {"text": text, "codepoints": [f"U+{ord(char):04X}" for char in text],
            "scalars": len(text), "utf8_bytes": len(text.encode("utf-8"))}


def _stages(original: str, policy: str) -> list[tuple[str, str]]:
    if policy == "exact-v1":
        return [("exact", original)]
    if policy == "nfc-v1":
        return [("NFC", unicodedata.normalize("NFC", original))]
    compatible = unicodedata.normalize("NFKC", original)
    # Reject oversized intermediates before the next transformation as well as grouping.
    check_text(compatible, MAX_STAGE, MAX_STAGE_BYTES)
    folded = compatible.casefold()
    check_text(folded, MAX_STAGE, MAX_STAGE_BYTES)
    final = unicodedata.normalize("NFKC", folded)
    return [("NFKC", compatible), ("default-full-casefold", folded), ("NFKC", final)]


def _groups(items: list[dict], field: str, induced: bool) -> list[dict]:
    grouped = {}
    for item in items:
        grouped.setdefault(item[field]["text"], []).append(item)
    output = []
    for key, members in grouped.items():
        distinct = len({item["original"]["text"] for item in members})
        if (induced and distinct >= 2) or (not induced and len(members) >= 2):
            output.append({"key": _evidence(key), "distinct_original_count": distinct,
                           "member_count": len(members),
                           "members": [{"index": item["index"], "label": item["label"]} for item in members]})
    return output


def analyze(document: dict) -> tuple[dict, int]:
    """Return complete evidence and exit status; raise bounded admission errors.

    Uses exact builtin objects and does not mutate its input. Unsupported policy
    or runtime is considered only after the entire common envelope is validated.
    """
    validate(document)
    if document["schema"] != SCHEMA or document["policy"] not in POLICIES:
        raise Unsupported("unknown schema or policy")
    _guard_runtime()
    items = []
    totals = [[0, 0] for _ in range(3)]
    for index, item in enumerate(document["items"]):
        stages = _stages(item["value"], document["policy"])
        evidence = []
        for position, (operation, text) in enumerate(stages):
            check_text(text, MAX_STAGE, MAX_STAGE_BYTES)
            totals[position][0] += len(text)
            totals[position][1] += len(text.encode("utf-8"))
            if totals[position][0] > 4096 or totals[position][1] > 16384:
                raise LabError("stage aggregate limit")
            evidence.append({"operation": operation, **_evidence(text)})
        items.append({"index": index, "label": item["label"], "original": _evidence(item["value"]),
                      "stages": evidence, "key": _evidence(stages[-1][1])})
    # No group is formed until every stage of every item has passed its bounds.
    duplicates = _groups(items, "original", False)
    collisions = _groups(items, "key", True)
    return ({"schema": SCHEMA, "policy": document["policy"], "status": "complete",
             "runtime": runtime(), "items": items, "exact_duplicates": duplicates,
             "induced_collisions": collisions, "assumptions": list(ASSUMPTIONS),
             "limits": {"input_bytes": 16384, "items": 16, "original_scalars": 64,
                        "original_utf8_bytes": 256, "stage_scalars": 256,
                        "stage_utf8_bytes": 1024, "stage_total_scalars": 4096,
                        "stage_total_utf8_bytes": 16384, "output_bytes": MAX_OUTPUT}},
            1 if collisions else 0)


def render(report: dict) -> str:
    """Serialize ASCII evidence and enforce the final delivery byte ceiling."""
    result = json.dumps(report, ensure_ascii=True, allow_nan=False, separators=(",", ":")) + "\n"
    if len(result) > MAX_OUTPUT:
        raise LabError("report byte limit")
    return result
