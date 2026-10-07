# Unicode identifier policy lab

See exactly how a chosen Unicode comparison policy changes synthetic strings and collision groups. The lab preserves each original plus intermediate text/code points, so a normalization decision stays explainable.

It demonstrates three policies: exact scalar equality; NFC then equality; explicitly ordered NFKC -> Python default full casefold -> NFKC then equality. The last is this lab's profile, not official toNFKC_Casefold. Equality gives no visual identity, authenticity, account authorization or spoof-resistance verdict. Use invented strings only.

## Run

No runtime packages are required. Use CPython 3.13.x with UCD 15.1.0; verified locally on Windows/3.13.7. From this directory:

```powershell
python -m unicode_lab samples/mixed.json
python -m unicode_lab samples/mixed.json --output fresh-report.json
python -m scripts.demo_reports fresh-demo.json
python -m unittest discover -s tests -v
python -O -m unittest discover -s tests -v
```

Output paths must be fresh: input aliases, hard links and existing reports are preserved. Exit 0 means complete/no induced collision; 1 means complete/induced collision; 2 means invalid/limit/I-O/delivery failure; 3 means unsupported admitted profile/runtime. An exit 1 is a completed observation. Success JSON goes to stdout or the fresh output; bounded error JSON goes to stderr. A partially delivered report after error is incomplete and must not be used. `--help` describes the CLI.

Input has exactly schema, policy, items; items have unique ASCII labels and string values:

```json
{"schema":"unicode-policy-lab/1","policy":"nfkc-casefold-nfkc-v1","items":[{"label":"item-0","value":"A"},{"label":"item-1","value":"A"},{"label":"item-2","value":"\uff21"}]}
```

The first two originals are exact duplicates. The fullwidth third original is distinct. Under the ordered compatibility/folding policy, all become `a`: the duplicate group retains indices 0,1 and the induced collision retains indices 0,1,2, member count 3 and distinct-original count 2. Under exact/NFC there is only the duplicate group. Repeated identical originals alone are not induced collisions.

## Demonstration

[Eight saved cases](samples/demo.json) and [mixed-group report](samples/mixed-report.json) preserve actual runtime metadata and reversible escaped evidence. `scripts.demo_reports.generate()` is the reusable fixed-case generator; it accepts no real data, returns eight reports, checks hand-fixed statuses and is verified by demo tests. The CLI above saves it to a new file.

| Synthetic comparison | Exact | NFC | NFKC/fold/NFKC |
|---|---|---|---|
| C-cedilla versus C + combining cedilla | Different | Collision | Collision |
| A versus fullwidth A | Different | Different | Collision |
| sharp-s versus ss | Different | Different | Collision |
| Latin a versus Cyrillic a | Different | Different | Different |

Code-point inequality in the last row is not a visual-security assessment. Another case shows U+01F0 producing U+006A U+030C at the folding step, then recomposing to U+01F0 in the final step. Empty/NUL/soft-hyphen/private-use/unassigned/supplementary controls demonstrate preservation. One supplementary scalar occupies four UTF-8 bytes; scalar counts do not measure graphemes or display width.

## Architecture and contract

`contract.py` performs strict whole-envelope admission and bounded regular-file reads. `model.py` validates before unsupported decisions, applies the named ordered policy with step bounds, then groups complete evidence. `__main__.py` delivers checked ASCII JSON and fixed diagnostics. `analyze(document)` is the reusable in-process API: returns `(report, exit_status)`, raises `LabError`/`Unsupported`, admits exact built-in objects and preserves the input. See [PLAN.md](PLAN.md) for exact schema/type/status priority and [SECURITY.md](SECURITY.md) for trust boundaries.

Bounds: 16 KiB UTF-8 JSON, container depth 4, 16 items, original 64 scalars/256 bytes per item; each intermediate 256 scalars/1024 bytes, batch stage 4096 scalars/16384 bytes; final JSON 512 KiB. Reject duplicate decoded fields, numbers/nonfinite tokens, extra fields, coercion, surrogates/noncharacters, custom types and cycles. Validate late records even when the profile/runtime is unknown. Over-expansion emits no partial groups. Evidence is ASCII escaped JSON, not redacted text.

Controls, whitespace, formatting/default-ignorable characters, private-use and unassigned scalars are intentionally admitted as teaching values and never silently removed. This is not a production identifier grammar, registry, authentication service, UTS39 implementation or locale policy. No IDNA/email/path/network transformations, remote lookups or system configuration changes. Metadata checks do not eliminate malicious filesystem races; stdout is not atomic and failed newly created output may be partial.

## Verification and learning

25 normal and 25 optimized tests pass on final Windows/CPython 3.13.7/UCD 15.1 source. Selected independent Unicode vectors cover seven normalization rows and seven folding mappings; fixtures were frozen before implementation and provenance tamper/repair is tested. Four isolated mutants are detected by assertion failures, including an independently distinguishing final-step mutation. Real child CLI/closed pipe, aliases/exclusive output and read/write/flush/close/help errors are checked. Compile and installed Bandit 1.9.4 pass with zero findings/suppressions. ECC implementer self-review fixed two bounded-delivery gaps. [VALIDATION.md](VALIDATION.md), [REVIEW.md](REVIEW.md) and [receipt](verification/receipt.json) record evidence and limits.

Other Python patches/platforms, hosted checks, full Unicode/visual conformance and account safety are unverified. Prepared SHA-pinned CI/CodeQL/Dependabot have not run on GitHub; no remote repository or protections were configured. Scanner dependencies are development-only exact pins, not a wheel hash lock or comprehensive advisory review. No new packages were installed for local tests.

[Research](RESEARCH.md) compares maintained normalization and confusable alternatives; [decisions](DECISIONS.md) explain why the original stdlib model fits this scope; [learning](LEARNING.md) provides an optional prediction exercise. Original implementation is MIT. Licensed Unicode data notices, source lines and bindings are retained in [NOTICE.md](NOTICE.md), [LICENSES/UNICODE.txt](LICENSES/UNICODE.txt) and [fixture documentation](fixtures/README.md). Codex assisted implementation/review, with one reviewed local Ollama label draft; no independent review or safety certification is implied.

## Publication status

See [publication review](PUBLICATION.md) for the October 5 source snapshot, fresh local checks, evidence boundaries and current hosted-check distinction.
