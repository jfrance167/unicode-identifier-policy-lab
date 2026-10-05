# Unicode identifier policy lab: research

Research date: 2026-10-05. This records the pre-implementation research; coordinator subsequently approved stages 1–5 at 02:49 and local implementation is complete. Owner: chat 01a10a39-9594-7f23-b92e-4e72adde2261. See PLAN.md for the contract and STATE.md/VALIDATION.md for current authorization and verification.

## Question and recommendation

What happens when an application deliberately compares synthetic Unicode strings using exact equality, canonical normalization, or an ordered compatibility/case-folding policy? Recommend building a small original standard-library teaching model. Preserve each supplied string and show intermediate code points, final keys, exact duplicates and transformation-induced collision groups. This complements JSON canonicalization, which preserves string distinctions. No production account policy or visual-security verdict follows from this experiment.

## Reuse and local context

Read relevant vault notes: Unicode Decoding and Evidence Preservation; Python Regex Validation Semantics; prior JSON Canonicalization Lab research/completion. Originals, decoded text and display views carry different evidence. Regex character classes and match extent require explicit contracts.

Bounded workspace filename searches did not establish an existing dedicated identifier-comparison model. Inspected llm-prompt-injection-firewall/firewall/screening.py: its screening views include NFKC and removal of category Cf, with casefold used for canary comparisons. That heuristic is not an identity policy; preserve it unchanged. The JSON lab's strict-decoding and bounded-I/O patterns are useful references, but its numeric subset and canonical-JSON verdict cannot supply this lab's equality contract. Review exact reused portions after code approval; no importing other labs as runtime dependencies or changing shared helpers.

Read tooling STARTUP.md. Remote readiness checks are unnecessary for this local-only research. One installed qwen3.5:2b extraction took 4,533 ms; raw response and reviewed corrections remain in .private/research/. No remote inference, paid calls, installation or third-party execution. Laya's classification/triage schema is unsuitable here. Codex performed source assessment, security judgments and plan drafting because these require review beyond the bounded worker.

## Primary sources and version evidence

- [Python 3.13 unicodedata](https://docs.python.org/3.13/library/unicodedata.html): normalization forms and database version interface.
- [Python str.casefold](https://docs.python.org/3.13/library/stdtypes.html#str.casefold): full caseless matching differs from lowercasing, including sharp-s expansion. Documentation currently identifies a later 3.13 patch; it is API guidance, not evidence that our installed patch was tested.
- Local read-only metadata: Python 3.13.7, unicodedata.unidata_version 15.1.0.
- [CPython v3.13.7 table generator](https://github.com/python/cpython/blob/v3.13.7/Tools/unicode/makeunicodedata.py), blob c4ba674ecb134a5eb595bc73aa653afba413a4e3: UNIDATA_VERSION 15.1.0, CaseFolding input, generation of Modules/unicodedata_db.h and Objects/unicodetype_db.h. This supports keeping normalization and built-in folding on the same CPython release. No generator executed or copied into runtime.
- [UAX 15](https://www.unicode.org/reports/tr15/): current page identifies Unicode 18.0.0. Canonical and compatibility normalization are different choices; use version-matched 15.1 data for lab expectations. An attempted historical page fetch failed; do not claim that page was inspected.
- [UTS 39 revision 28](https://www.unicode.org/reports/tr39/tr39-28.html), section 4: skeleton-based confusable comparison is distinct from normalization/case equality. Its intermediate skeleton is not a display identifier or account authorization. This lab does not implement UTS 39 conformance, script restrictions or visual matching.
- [UAX 44](https://www.unicode.org/reports/tr44/): NFKC_Casefold can map soft hyphen U+00AD to the empty string. Consequently our explicitly ordered NFKC/casefold/NFKC profile must not be named official toNFKC_Casefold. The historical tr44-31 page inspected was a draft, not adopted as normative final data.

## Open-source alternatives inspected

Connected GitHub repository searches initially failed with transport errors; public primary-source browsing found candidates. Subsequent connected metadata, directory/tree and pinned-file reads succeeded where listed below. Failed responses are not search evidence. Firecrawl was not called because current free-account readiness was not established.

### unicodedata2: useful maintained normalization alternative

[Repository](https://github.com/fonttools/unicodedata2), pinned tree revision a8ee359dc5ee99ceaf63598ef101113865093ed4; nonarchived metadata reported push 2026-09-18. Actually inspected README, Apache-2.0 LICENSE, pyproject.toml, unicodedata2/unicodedata.c, tests/test_unicodedata2.py and .github/workflows/ci.yml, saved under .private/research/candidates/unicodedata2/.

README/manifest identify version 18.0.0 and Python >=3.9. Build requires setuptools >=77.0.1; distribution is a compiled extension using unicodedata.c and unicodectype.c. Optional testing uses pytest/pytest-randomly; dev uses tox. Actual normalization code dispatches NFC/NFKC/NFD/NFKD and performs decomposition/composition. Tests use version-matched Unicode normalization data and assert official c1..c5 relationships; they explicitly omit is_normalized. CI describes wheel builds and tests across Windows/macOS/Linux, with normalization data downloaded before testing. We did not run upstream CI or assess every code path. Workflow uses mutable action tags and unpinned build tooling; do not copy that pipeline into an owned repository.

Read current open-issue titles: #72 additional UCD properties, #28 old tables, #25 is_normalize. These show API requests, not a vulnerability audit. No Scorecard or comprehensive advisory assessment performed. Adopting a newer normalization database does not replace Python str.casefold tables, so version mixing would need another explicit design. Avoid this dependency for the pinned stdlib lab; revisit only if a future approved scope needs newer Unicode data. No code borrowed, fork, package install or safety certification.

### confusable_homoglyphs: alternate learning question

[GitHub snapshot](https://github.com/vhf/confusable_homoglyphs/tree/c18e47db2188eafe5856d30c5c7d69ecd5395eda). Metadata marks that repository archived, last push 2024-01-02, MIT license metadata. Read README.rst, setup.py and confusable_homoglyphs/confusables.py. Actual code loads confusables data and checks unique characters against optional preferred script aliases; is_dangerous combines mixed-script and confusable checks. This is a heuristic question different from equality after our ordered transformation.

README redirects maintenance since January 2024 to [SourceHut](https://sr.ht/~valhalla/confusable_homoglyphs/); its current page was blocked by robots policy. Do not infer that the successor is inactive. Snapshot license bytes and tests could not be retrieved successfully; MIT metadata alone is insufficient for copying code. No runtime download behavior verified because the loader was not inspected. Current successor maintenance/CI/data pinning remain unassessed. Avoid adoption for this scope, rather than claim an exhaustive comparison or confirmed insecurity.

## Independent data provenance

[Official Unicode tools tree](https://github.com/unicode-org/unicodetools/tree/6661370193d31b1cfb28a5b854ee8a894a95edbf), complete tree response (not truncated). Raw data blobs recovered through connected GitHub after public-directory fetch failures and empty ranged responses; these failures were not treated as content. Saved UTF-8 files match upstream Git blob IDs and metadata lengths, checked by standard-library hashing. No table/package generator executed.

| Artifact in .private/research/upstream/ | Bytes | Git blob | SHA-256 |
|---|---:|---|---|
| CaseFolding-15.1.0.txt | 84870 | 69c5c64b4c6a124f4608722db723a9e32667f190 | 4e55acfdc32825a22e87670e9056a3bf94ad7c5400065778e9e10f8314372bcf |
| NormalizationTest-15.1.0.txt | 2625136 | 2e88574243dbb5dd4109f54bd25d43588e78226f | 871238e37e3be0696ec2bd0891119a041b052da1a84485eda05a5438724b223e |
| UNICODE-LICENSE.txt | 2033 | d7e7973c2fd6f2586a8999a69dc21e39af26be0f | fe5c62b543e287981db198f2acfa0ca732d12591a1024536dc8fd85dacd77104 |

Files originate at unicodetools/data/ucd/15.1.0/{CaseFolding,NormalizationTest}.txt and root LICENSE at the revision above. The repository license is Unicode License V3 / Unicode-3.0, copyright 2001-2024; individual data headers retain 2023 Unicode copyright. License allows reuse with its notice retained with copies or documentation, includes warranty disclaimer and name-use restriction. Preserve exact notices plus source/revision attribution in any adopted fixture excerpts; original project code may use MIT separately. No upstream implementation copied.

Read independent vector rows: casefold C/F mappings 0041->0061, 00DF->0073 0073, 0130->0069 0307, 03A3/03C2->03C3, FB00->0066 0066; T mappings are excluded from default full folding. Header warns folding does not preserve normalization. Normalization c1/c2/c3/c4/c5 cases include combining D dot-above/dot-below reordering, C-cedilla, Angstrom, fullwidth A and ff ligature. Expected NFC/NFKC comes from data columns, never from the lab under test. Capture selected source lines and expected sequences with provenance before adaptation. Full conformance, every assigned code point and font-independent visual behavior are outside this bounded lab.

## Decision and unresolved gates

Decision adopted: build the original stdlib model, rather than fork either candidate. Exact transformation/equality contract in PLAN.md; expansion limits, original evidence, duplicate-versus-induced collision distinction and runtime guard are mandatory. Source capture/provenance succeeded before implementation. Subsequent approval and completed code/tests/mutations/SAST are recorded in STATE.md and VALIDATION.md; those later results are separate from this research evidence. A successful artifact hash check is not a security audit or an authenticated trust guarantee.
