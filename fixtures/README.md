# Frozen independent expectations

Frozen before model implementation under October 5 02:49 approval. Seven normalization rows and seven default C/F folding rows were selected from verified Unicode 15.1 data without invoking Python normalization/casefold or the implementation. oracles.json retains original source-line numbers, unmodified source rows and columns/mappings. unicode-excerpts.txt preserves their comments; LICENSES/UNICODE.txt retains the notice. Full source/revision/byte/hash bindings are in RESEARCH.md; full private research captures are ignored, not CI dependencies.

Normalization columns are source/NFC/NFD/NFKC/NFKD. Default folding excludes T and S overrides and uses C/F. The 01F0 vector distinguishes folding alone (006A 030C) from the last NFKC recomposition (01F0). FDFA independently expands to 18 scalars on NFKC, providing a reachable 256-scalar overflow from a 15-scalar repeated source.

Manual mixed-group oracle: labels item-0,item-1,item-2 contain U+0041,U+0041,U+FF21. Exact/NFC have one duplicate group [0,1] and no induced collision. NFKC/casefold/NFKC stages are U+0041 then U+0061 then U+0061 for every item. Duplicate group remains [0,1]; induced collision contains [0,1,2] with two distinct originals. All labels and indices must survive; repeated originals do not themselves create a transformed collision.

Other manual controls: empty, NUL, soft hyphen, private-use U+E000, unassigned U+0378 and supplementary U+1F600 stay unchanged under each policy; Latin U+0061 versus Cyrillic U+0430 remain unequal under all three policies. These are code-point policy expectations, not visual or valid-account claims. A single supplementary scalar is one scalar, four UTF-8 bytes and one code-point entry.

provenance.json fixes the adapted artifact lengths/SHA256. Tests must check it before consuming expected results, reject a tampered excerpt and pass again after repair. It is local integrity evidence, not authenticated provenance. Only selected vectors are tested; no full conformance claim.
