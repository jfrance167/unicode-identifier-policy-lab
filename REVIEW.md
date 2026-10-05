# ECC actual-change self-review

Implementer reviewed new runtime modules, demo, tests, frozen oracle/provenance artifacts, prepared CI and surrounding callers against the pinned ECC code-reviewer checklist. Baseline is research/oracle commit f7c607a, not merely the last commit. No independent agent or native ECC plugin review is claimed; the native plugin remains unavailable under the machine's recorded approval restriction. Used installed ecc-code-review and ecc-verification-loop entry points only.

## Concrete fixes

1. **Medium: help could conceal delivery failure.** At Parser in unicode_lab/__main__.py:12, delegating help to argparse's default _print_message suppressed OSError. A broken writer followed by --help reached SystemExit(0), confirmed by the regression failure saved privately. Override at line 16 routes the static help through write_checked, propagates short/flush errors and lets main return 2 while replacing the failed stdout buffer. Successful help and failed help regression now pass in both modes.
2. **Low: direct main(argv) path exception escaped the bounded diagnostic.** The file read at unicode_lab/__main__.py:42 could raise ValueError when an in-process caller supplied a NUL path. OS argv itself cannot contain NUL; this is a direct-call robustness gap, not an exposed account vulnerability. Reproduced embedded-null stat ValueError in the saved regression log. I/O handler at line 57 now covers ValueError after the specific LabError/Unsupported handlers, using the fixed diagnostic rather than exception text. Direct-call regression and affected/full suites pass.

Final inspection found no additional actionable defects. Reviewed whole-record validation before unsupported decisions, exact built-in schema/cycle rejection, numerical/duplicate JSON hooks, scalar/noncharacter/expansion bounds, shared-version guard, original preservation, overlapping memberships, first-occurrence determinism, ASCII serialization/fixed diagnostics, exclusive output/alias handling, read metadata and write/flush/close failures. Algorithms are linear over bounded input/stage evidence; no network, dynamic code, package/table execution or real identifiers. Original/source-vector provenance remains independent of runtime transformations.

25 normal and 25 optimized tests pass on the final source, including optimized child CLI. Four isolated model mutants fail assertions rather than crash, with original source hash unchanged. Compile, installed Bandit (309 lines, zero findings/suppressions) and local diff/CI-policy checks pass. Targeted secret-signature scan is recorded separately with its limits. No broad suppression, arbitrary coverage target or paid/missing checker introduced.

| Severity | Fixed | Unresolved |
|---|---:|---:|
| Critical | 0 | 0 |
| High | 0 | 0 |
| Medium | 1 | 0 |
| Low | 1 | 0 |

Verdict: ready for local review within the declared teaching scope. No merge/deployment/publication authorization follows. Other-runtime/Linux/hosted, full Unicode/UTS39 conformance, visual identity, account safety and hostile-filesystem-race guarantees remain unverified or excluded; see SECURITY.md and VALIDATION.md.
