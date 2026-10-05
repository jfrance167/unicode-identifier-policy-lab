"""Independent data-column/mapping checks plus bounded semantic controls."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from unicode_lab.contract import LabError, Unsupported, parse, validate
from unicode_lab.model import analyze, render

ROOT = Path(__file__).resolve().parents[1]


def document(values, policy="nfkc-casefold-nfkc-v1"):
    return {"schema": "unicode-policy-lab/1", "policy": policy,
            "items": [{"label": f"item-{i}", "value": text} for i, text in enumerate(values)]}


def from_hex(points):
    return "".join(chr(int(cp, 16)) for cp in points)


def verify_provenance(base: Path):
    bindings = json.loads((base / "fixtures/provenance.json").read_text(encoding="ascii"))
    for relative, binding in bindings.items():
        content = (base / relative).read_bytes()
        if len(content) != binding["bytes"] or hashlib.sha256(content).hexdigest() != binding["sha256"]:
            raise ValueError("fixture provenance mismatch")


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        verify_provenance(ROOT)
        cls.oracle = json.loads((ROOT / "fixtures/oracles.json").read_text(encoding="utf-8"))

    def test_independent_normalization_columns(self):
        for vector in self.oracle["normalization"]:
            columns = [from_hex(col) for col in vector["columns"]]
            for policy, column in (("nfc-v1", 1), ("nfkc-casefold-nfkc-v1", 3)):
                # First intermediate isolates normalization from later folding.
                result, _ = analyze(document([columns[0]], policy))
                self.assertEqual(result["items"][0]["stages"][0]["text"], columns[column])

    def test_independent_full_casefold_mappings(self):
        for vector in self.oracle["folding"]:
            source, expected = from_hex([vector["input"]]), from_hex(vector["expected"])
            # FB00 has already decomposed on the first NFKC, producing the same ff.
            report, _ = analyze(document([source]))
            self.assertEqual(report["items"][0]["stages"][1]["text"], expected)

    def test_final_normalization_recomposes_casefold(self):
        report, _ = analyze(document(["\u01f0"]))
        self.assertEqual([stage["text"] for stage in report["items"][0]["stages"]],
                         ["\u01f0", "j\u030c", "\u01f0"])

    def test_overlapping_duplicate_and_induced_group(self):
        expected = self.oracle["mixed_group"]
        doc = document([from_hex([p]) for p in expected["values"]])
        before = deepcopy(doc)
        report, code = analyze(doc)
        self.assertEqual(doc, before)
        self.assertEqual(code, 1)
        duplicate, collision = report["exact_duplicates"][0], report["induced_collisions"][0]
        self.assertEqual(duplicate["members"], [{"index": i, "label": f"item-{i}"} for i in [0, 1]])
        self.assertEqual(collision["members"], [{"index": i, "label": f"item-{i}"} for i in [0, 1, 2]])
        self.assertEqual((collision["member_count"], collision["distinct_original_count"]), (3, 2))
        for row, stages in zip(report["items"], expected["nfkc_stages"]):
            self.assertEqual([x["text"] for x in row["stages"]], [from_hex([p]) for p in stages])
        for policy in ("exact-v1", "nfc-v1"):
            report, code = analyze({**doc, "policy": policy})
            self.assertEqual((code, len(report["exact_duplicates"]), report["induced_collisions"]), (0, 1, []))

    def test_duplicates_alone_are_not_induced_collisions(self):
        report, code = analyze(document(["X", "X"]))
        self.assertEqual(code, 0)
        self.assertEqual(report["induced_collisions"], [])
        self.assertEqual(report["exact_duplicates"][0]["member_count"], 2)

    def test_canonical_policy_difference(self):
        for policy, expected in (("exact-v1", 0), ("nfc-v1", 1), ("nfkc-casefold-nfkc-v1", 1)):
            report, code = analyze(document(["\u00c7", "C\u0327"], policy))
            self.assertEqual(code, expected)
            self.assertEqual(report["items"][1]["original"]["text"], "C\u0327")

    def test_preserved_scalar_controls_and_nonvisual_comparison(self):
        controls = ["", "\0", "\u00ad", "\ue000", "\u0378", "\U0001f600", " a "]
        for policy in ("exact-v1", "nfc-v1", "nfkc-casefold-nfkc-v1"):
            report, _ = analyze(document(controls, policy))
            self.assertEqual([x["key"]["text"] for x in report["items"]], controls)
            scalar = report["items"][5]["original"]
            self.assertEqual((scalar["scalars"], scalar["utf8_bytes"], scalar["codepoints"]), (1, 4, ["U+1F600"]))
            self.assertEqual(analyze(document(["a", "\u0430"], policy))[1], 0)
        escaped = render(report)
        self.assertTrue(escaped.isascii())
        self.assertNotIn("\0", escaped)
        self.assertIn("\\u0000", escaped)

    def test_empty_and_deterministic_group_order(self):
        report, code = analyze(document([]))
        self.assertEqual((code, report["items"], report["exact_duplicates"], report["induced_collisions"]), (0, [], [], []))
        doc = document(["B", "b", "A", "a"])
        report, _ = analyze(doc)
        self.assertEqual([g["key"]["text"] for g in report["induced_collisions"]], ["b", "a"])
        self.assertEqual(render(report), render(analyze(doc)[0]))

    def test_full_validation_precedes_unsupported(self):
        for mode in ("schema", "policy", "runtime"):
            doc = document(["good", "\ud800"])
            if mode != "runtime":
                doc[mode] = "unknown"
            with patch("unicode_lab.model._guard_runtime", side_effect=Unsupported("test runtime")):
                with self.assertRaises(LabError) as caught:
                    analyze(doc)
                self.assertNotIsInstance(caught.exception, Unsupported)
        for field in ("schema", "policy"):
            doc = document(["good"])
            doc[field] = "unknown"
            with self.assertRaises(Unsupported):
                analyze(doc)
        with patch("unicode_lab.model.unicodedata.unidata_version", "18.0.0"):
            with self.assertRaises(Unsupported):
                analyze(document([], "exact-v1"))

    def test_shape_types_labels_and_cycles(self):
        class CustomDict(dict):
            pass
        bad = [None, [], CustomDict(document([])), {**document([]), "extra": "x"}]
        doc = document(["a"])
        doc["items"].append(doc)
        bad.append(doc)
        doc = document(["a", "b"])
        doc["items"][1]["label"] = "item-0"
        bad.append(doc)
        for value in (None, False, 2, [], {}, "\ud800", "\ufdd0", "\U0010ffff"):
            bad.append(document([value]))
        for label in ("", "x" * 33, "\u0430", "x\n"):
            doc = document(["a"])
            doc["items"][0]["label"] = label
            bad.append(doc)
        for doc in bad:
            with self.assertRaises(LabError):
                validate(doc)

    def test_input_and_expansion_boundaries(self):
        analyze(document(["\U0001f600" * 64]))  # 64 scalars, 256 bytes exactly.
        for doc in (document(["x" * 65]), document(["x"] * 17)):
            with self.assertRaises(LabError):
                analyze(doc)
        report, _ = analyze(document(["\ufdfa" * 14]))  # 252-scalar first intermediate.
        self.assertEqual(report["items"][0]["stages"][0]["scalars"], 252)
        with patch("unicode_lab.model._groups", side_effect=AssertionError("grouping must not occur")):
            with self.assertRaises(LabError):
                analyze(document(["a", "\ufdfa" * 15]))
        # UTF-8 step and aggregate limits are redundant under scalar/item caps;
        # reduced guards test seams without inventing an admitted overflow.
        with patch("unicode_lab.model.MAX_STAGE_BYTES", 1):
            with self.assertRaises(LabError):
                analyze(document(["\u00e9"]))

    def test_json_ambiguity_utf8_depth_and_tokens(self):
        raw = json.dumps(document(["x"], "exact-v1")).encode()
        self.assertEqual(parse(raw), document(["x"], "exact-v1"))
        bad = [b"\xff", b"\xef\xbb\xbf{}", b" " * 16385, b"[[[[[0]]]]]",
               b'{"schema":"x","sch\\u0065ma":"y","policy":"x","items":[]}',
               b'{"schema":"x","policy":"x","items":[],"n":1}', b"{} trailing"]
        bad += [b'{"schema":"x","policy":"x","items":[' + token + b"]}" for token in
                (b"0", b"-0", b"1.2", b"1e300", b"NaN", b"Infinity", b"true", b"null")]
        for value in bad:
            with self.assertRaises(LabError):
                parse(value)
        doc = document(['braces {[]}, quote " and slash \\'])
        self.assertEqual(parse(json.dumps(doc).encode()), doc)

    def test_output_limit_seam(self):
        with patch("unicode_lab.model.MAX_OUTPUT", 10):
            with self.assertRaises(LabError):
                render(analyze(document([]))[0])

    def test_provenance_tamper_and_repair(self):
        import tempfile
        import shutil
        temp_root = ROOT / ".private/verification/test-temp"
        temp_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temp_root) as directory:
            base = Path(directory)
            shutil.copytree(ROOT / "fixtures", base / "fixtures")
            shutil.copytree(ROOT / "LICENSES", base / "LICENSES")
            target = base / "fixtures/unicode-excerpts.txt"
            original = target.read_bytes()
            target.write_bytes(original + b"tamper")
            with self.assertRaises(ValueError):
                verify_provenance(base)
            target.write_bytes(original)
            verify_provenance(base)


if __name__ == "__main__":
    unittest.main()
