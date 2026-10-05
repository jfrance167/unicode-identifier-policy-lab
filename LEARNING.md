# Learning

Preserve originals alongside keys. Normalization deliberately changes comparison evidence; canonical JSON preserving text cannot choose an application's identity policy. NFC can merge composed/decomposed sequences, while NFKC additionally removes compatibility distinctions such as fullwidth letters. Full folding can expand sharp-s to ss and differs from lowercasing.

Order is observable. Unicode's folding data warns that folding can disrupt normalization. U+01F0 folds to U+006A U+030C, then the last NFKC recomposes it. That independent vector detects omission of the final step; a mutation that merely changes code but preserves all tested results would not establish test sensitivity.

Groups answer precise questions. Two identical originals are duplicates; adding a distinct fullwidth original can place all three in an induced collision as well. Neither group identifies a real entity or grants an account permission. Latin/Cyrillic scalar inequality is compatible with possible visual confusion; visual policy needs a different model.

A supplementary code point counts as one scalar and four UTF-8 bytes. It can occupy multiple UTF-16 units and does not establish a grapheme/display-width count. Escaped text/code points make controls visible without deletion, but provide no privacy protection.

Verification lessons: fixture hashes gate adaptations; tamper fails and repair passes. Windows sandbox initially blocked temporary-tree access and hard links; owned test directories plus authorized filesystem checks resolved the platform restriction without dropping tests. Help/delivery paths also need bounded errors and closed-pipe handling. Source data hashes and selected tests are evidence with limits, not a security certification.

Optional exercise: predict duplicate/collision memberships for A,A,fullwidth A under all three policies, then explain why an unequal Latin/Cyrillic pair can still need a separate visual-confusable assessment.
