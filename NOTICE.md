# Attribution and assistance

Original teaching implementation and project documentation: MIT, Jake Franciosa. Reviewed admission/file-delivery patterns from Jake's earlier JSON canonicalization lab informed this implementation; that separate project is not a runtime dependency and remains unchanged.

Selected Unicode 15.1 normalization/folding rows in fixtures/oracles.json and fixtures/unicode-excerpts.txt originate from Unicode, Inc. (2023 data headers), official unicode-org/unicodetools revision 6661370193d31b1cfb28a5b854ee8a894a95edbf, paths unicodetools/data/ucd/15.1.0/NormalizationTest.txt and CaseFolding.txt. Original line numbers/comments, Git blob/byte bindings and SHA-256 are in RESEARCH.md. Retained Unicode License V3 notice is LICENSES/UNICODE.txt, copied from that revision's root LICENSE; it covers adopted data separately from original MIT code. Excerpt selection/JSON representation and manual group controls are lab adaptations. No third-party library implementation was copied or installed.

Python/Unicode documentation, unicodedata2 and archived confusable_homoglyphs were research references, not adopted runtime libraries. Candidate source snapshots are ignored private research evidence and not distributed. CI references immutable official action commits, not vendored code.

AI assistance: Codex drafted and reviewed code, tests and documentation under Jake's approved workflow. Installed loopback-only qwen3.5:2b produced one bounded learning-label extraction; raw imperfect draft and reviewed corrections were preserved privately. Codex retained source verification and security judgments. Implementer's ECC review is a self-review. Neither AI drafting nor a clean scanner result certifies production safety.
