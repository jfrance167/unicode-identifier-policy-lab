# Local verification

Executed Windows, CPython 3.13.7 (64-bit), UCD 15.1.0, 2026-10-05. Report records actual Python/UCD metadata; no separate casefold-version field is invented. Other admitted 3.13 patches/implementations/platforms were not run.

| Check | Command/evidence | Outcome |
|---|---|---|
| Normal tests | python -m unittest discover -s tests -v | PASS, 25, exit 0 |
| Optimized tests | python -O -m unittest discover -s tests -v | PASS, 25, exit 0; CLI/demo child commands use -O |
| Compile | python -m compileall -q unicode_lab scripts tests | PASS, exit 0 |
| SAST | python -m bandit -r unicode_lab scripts -f json -o .private/verification/bandit.json | PASS, Bandit 1.9.4, 309 lines, zero findings/nosec/skips, exit 0 |
| Independent data | Seven normalization-column and seven C/F-folding mappings; frozen mixed-group/controls | PASS; hashes checked before fixture use |
| Source capture | Three official data/license artifacts, original Git blob/length/SHA256 | PASS; RESEARCH.md bindings |
| Provenance tamper/repair | Modified excerpt in own temporary copy | PASS: mismatch rejected, restored bytes accepted |
| CLI/delivery | Child statuses 0/1/2/3, real closed stdout pipe, checked help, fixed diagnostics, hard-link/input alias, exclusive output, short/flush/close failures | PASS, no test skips |
| Demo | Eight fixed cases, sample reproduction and existing-output protection | PASS; semantic reproduction excludes runtime metadata from cross-patch comparison, actual artifact retains 3.13.7 metadata |
| Mutations | .private/verification/run_mutations.py; four separate copies | PASS: each exit 1 / FAILED(failures=...), no crash/error count; source unchanged |
| ECC self-review | REVIEW.md, actual code/callers/tests/CI | PASS after two concrete fixes; not independent |
| CI/targeted secret signatures | Reused trusted repository_checks.py, exact result in receipt | PASS local preparation only; not a complete secret scanner |
| Hosted CodeQL/CI, GitHub protections/security eligibility | No remote repository | NOT RUN / unavailable |
| Third-party type/lint tool | No configured installed project checker | NOT APPLICABLE; no checker downloaded |

Private full logs preserve normal/optimized tests, prior failing help/path regressions, Bandit JSON, compile, per-mutant outputs, pin identities and local repository checks. verification/receipt.json binds current source/tests/fixtures/samples/CI/licensing manifests by bytes/SHA256. It is integrity evidence, not an origin signature or full security proof.

The four mutants are full-fold replaced by lower; NFKC replaced by NFC; raw duplicate member count substituted for distinct-original induced collision; last normalization omitted. The last one is meaningful because the independent U+01F0 -> U+006A U+030C -> U+01F0 fixture distinguishes it. Tests fail assertions, not syntax errors or dependency crashes. Source model SHA256 remains 4aa05370426c21f90cb290228d7b21d609cd7f2456537df89901897c3e880620.

## Bounds and honest guard reachability

Input scalar/item limits and surrogate rejection already imply original UTF-8/aggregate ceilings (64*4=256 bytes; 16*64=1024 scalars; 16*256=4096 bytes). Each stage <=256 scalars implies <=1024 UTF-8 bytes and, for <=16 items, <=4096 scalars/16384 bytes. Those redundant guards do not have independent over-limit admitted examples. A reduced stage-byte guard tests its seam; aggregate guards are supported by the finite bound, not claimed overflow tests. Reachable expansion overflow uses 15 U+FDFA scalars whose independently listed NFKC mapping has 18 scalars (270 >256); fourteen produce 252 and pass. Grouping is mocked to fail if called on the rejected batch, proving no partial grouping.

Single-report conservative scalar-evidence count: item originals/stages/keys <=16*(64+3*256+256)=17408 scalars; at most eight induced group keys add 2048; at most eight exact-duplicate keys add 512. Total <=19968. Worst escaped scalar text plus quoted code-point entry/comma costs <=23 ASCII bytes per scalar, giving 459264; generously bounded fixed framing/labels/counts/operations/members/assumptions under 40960 yields <=500224, below 524288. Thus final output cap is tested at a reduced serializer seam, not by a fictitious oversized admitted document. Demo is eight fixed small cases, not an unbounded aggregate input service. Limits constrain evidence/workload, not exact temporary allocation, RSS or time.

Initial sandbox attempts failed on temporary-tree and hard-link access, not application assertions. Temporary trees are now generated inside the owned lab; authorized unsandboxed filesystem suite runs verified real hard links. No test was skipped or weakened. New review regressions separately exposed help-write suppression and direct-call NUL-path handling, repaired and followed by final normal/optimized suites, compile and Bandit. No redundant application reruns for later documentation-only changes.
