# POST-DRAW review L2 (R4): LCB-STAGE0-INTERACTION record split, draw commit 3c70660

Reviewer: adversarial-reviewer, 2026-09-25. Zero LLM calls. No LCB outcome value read: no graded_list, no pass@1, no outcome DB. The only data file opened was the texts DB, table `problem` (plus `sqlite_master` for the schema), with `mode=ro&immutable=1`. Governing text: docs/judge_v2_program.md L17702-L17982 (registration: H1 closure, H2 draw, strata, fractions), L18102-L18373 (pre-data amendment; it changes nothing in the split), L18459-L18543 (READY record; L2 requires this re-derivation before any "content-closed" wording).

## VERDICT

**R-L2 MET. 0 of 1,055 problems differ** in side, and 0 differ in any other field of split_side.tsv (item_id, component_id, stratum, rank_hex, platform, question_id). closure_edges.tsv matches edge for edge: 91 of 91 P edges, 0 only in the committed file, 0 only in mine; edge-set sha16 c3498356c2cc5e11 in both. Content disjointness re-checked independently on all three side pairs: 0 stem-key twins, 0 token-sequence twins, 0 families on two sides, 0 closure edges across sides. The texts DB sha256 is unchanged after my reads.

Words (CONTEXT rule 12; H2 at L17730): from this review on, the record split may be called **"content-closed under CK-CLOSE-v2"**. The qualifier is the stated R = 6 policy (A7): see F1.

## Pins (hash kind named; LF rendering of record; no CRLF rendering exists for the four outputs, 0 CR bytes each)

| object | pin |
|---|---|
| draw commit | 3c70660e8a6edeaabafaf4239bf91d7fe69a9180 (parent 449737330bc4880566719f05377eec09beaef937), branch worktree-agent-adb18465164aaf122, NOT MERGED |
| split_side.tsv | blob:0a5da5ab2211907b50f1b7db0c22aa7adb58c8a2 / sha256 f0a694b268eb8ed7cebf671c9779de1ea65851d008abfe7e819ec77b90e64317 (commit bytes = worktree bytes) |
| closure_edges.tsv | blob:fdffafed79ac632168036fe61e509735e8d60eae / sha256 a94bb29ad15c20566ba5988df89bbbe876436130c233a620645095f8e9230cf4 |
| split_manifest.json | blob:4348585084c82d43b3df9ef504219d7f2071137c / sha256 8a655d5896e630ab3486d33b7959215fbc904bded028ef92912d5b14c619e7e5 |
| split_runlog.txt | blob:15ee194aa7ba48cf851a93842c682b51197110ec / sha256 eacea12d2fd2d7112a7635b490708c5549ee0a65a86c5c4b3a72ddf66a25f542 |
| draw.py | blob:ed5801a8e37132cdc4fa4e742d5ed1854d708a16 / sha256-lf16:23618585ef34e575, identical at ed948d6, 4497373, 3c70660 |
| common.py | blob:022f11bfcca6666aa96ec0c9fe46e4568209e757 / sha256-lf16:a890323a74b2bd9b, identical at the same three commits |
| __init__.py | blob:a861097a56475bfcadfb884dd5536fe7e6466877 / sha256-lf16:758ab9c9ca3225fb, identical at the same three commits |
| closure modules at 4497373 | split_side.py blob:05224b5a..., passage_closure.py blob:003d5d4e..., content_closure.py blob:1533cb5a... (the registered blobs) |
| texts DB | Z:\FAC\TUBerlin\THESIS\TaxoArena_data\lcb\lcb_v6_texts_7d2f4cad635b254d.db, file sha256 5f8ae5d8acbfa4dcf97cf6fb329cc51af4cb7c108be4299b52fc01838cf689be, 2,400,256 bytes, mtime 2026-09-25 06:38:02.036; the same before and after my reads, and no -wal / -shm created (the directory still holds 3 entries) |
| reviewer scripts (scratchpad, not of record) | rv_lcb/postdraw/rederive.py sha256-16 a8a4a44fcefd57d0; rsens.py bec1390a2d925284; output rederive.out e9de277ab8c9ee05 |

## Independence of the re-derivation

- rederive.py does not import draw.py, common.py, ingest.py or indep_draw.py.
- It reads only the raw columns platform, question_id, question_content and difficulty. It re-derives the stored columns (surrogate_id, format, stratum, stem_key, item_id) and compares them.
- stem_key is RE-IMPLEMENTED from its norm-v1 definition: NFKC, ASCII fold, the explicit whitespace class collapsed to one space, strip; then sha256(norm(stem) US "" US ""). It is cross-checked against the pinned split_side blob 05224b5a, which was loaded from `git cat-file` after the blob sha1 was verified.
- P edges use a per-pair diagonal DP over unmasked 8-shingles (2 <= df <= 6, run >= 20 tokens). This is a different algorithm from the postings/diagonal method that passage_closure and indep_draw share.
- Components are found by BFS. Strata are the modal vote, with ties to the lexicographically smallest.
- Quotas use exact integer arithmetic, (3n+5)//10 and (n+5)//10 capped at n - n_eval, asserted equal to the float form in every stratum.
- The rank is the sha256 hex of "taxoarena-split-v2" US seed US component_id, with the RECORD seed "LCB-STAGE0-SPLIT:cc7a6d7f31345d571253c67ca9799d2e8a3d95c4".
- The committed files were compared from `git show 3c70660:<path>`, not from the working tree (the two are byte-equal).

## Per-claim table

| # | claim | result | command / script | mine vs claimed | sev |
|---|---|---|---|---|---|
| 1 | Stored problem columns are the registered derivations | CONFIRMED | rederive.py | surrogate / stem_key (own impl vs stored, own vs pinned) / item_id / format / stratum mismatches 0/0/0/0/0/0 of 1,055 | - |
| 2 | 1,055 problems; atcoder 602 / leetcode 444 / codeforces 9; easy 322 / medium 383 / hard 350 (D3) | CONFIRMED | rederive.py | equal | - |
| 3 | Exact stem_key groups 0; P 91; O 0; D 0; band 15-19 134; edge-set sha16 c3498356c2cc5e11 | CONFIRMED | rederive.py | P 91, D 0, band 134, exact groups 0, sha16 c3498356c2cc5e11. O: the registered key has no options channel; my starter_code channel (a sensitivity) gives 0 edges / 0 band | - |
| 4 | closure_edges.tsv edge by edge | CONFIRMED | rederive.py vs `git show 3c70660:.../closure_edges.tsv` | 91 rows, all kind P; sets equal; 0 only-theirs / 0 only-mine; problems_a/b labels 0 mismatches | - |
| 5 | 986 components; 49 multi; largest 8; histogram {1:937, 2:40, 3:5, 5:3, 8:1}; Kish 1.214218; 33 multi-stratum | CONFIRMED | rederive.py | equal to the digit | - |
| 6 | Per-stratum plan (components -> EVAL/GATE/TRAIN) | CONFIRMED | rederive.py | f-easy 135->41/14/80; f-hard 94->28/9/57; f-medium 197->59/20/118; s-easy 184->55/18/111; s-hard 225->68/23/134; s-medium 151->45/15/91; integer and float quotas agree in all 6 | - |
| 7 | EVAL 296/314, GATE 99/111, TRAIN 591/630 (components/problems) | CONFIRMED | rederive.py | equal | - |
| 8 | split_side.tsv problem by problem | CONFIRMED | rederive.py | 1,055/1,055 rows compared; **side differences 0**; all 7 other fields 0 differences | - |
| 9 | R3 realised shares 0.2976 / 0.1052 / 0.5972 and per-stratum problem counts (own stratum) | CONFIRMED | rederive.py; 314/1055, 111/1055, 630/1055 | f-easy 41/14/80, f-hard 32/11/59, f-medium 62/20/125, s-easy 55/20/112, s-hard 74/25/149, s-medium 50/21/105: equal | - |
| 10 | CK-CLOSE PASS x3: 0 twins, 0 shared families | CONFIRMED (independent) | rederive.py | stem_key shared across sides 0; token-sequence key (\w+ casefold, joined) shared across sides 0; components on >1 side 0; P/D edges across sides 0/0; cross-side pairs with an unmasked run >= 20 tokens 0 (76 cross-side pairs in the 15-19 band, 3,042 below 15) | - |
| 11 | EVAL Kish 1.165605 (manifest checks.eval_kish_combined) | CONFIRMED | python over the committed TSV | EVAL 1.165605 (GATE 1.360360, TRAIN 1.212698: not claimed, printed for the record) | - |
| 12 | Runlog matches the outputs | CONFIRMED | cat split_runlog.txt vs rederive.out and sha256sum | every [H1]/[H2]/[R3]/[CK-CLOSE] number above equal; [R2] shas f0a694b2 / a94bb29a / 8a655d58 equal to the committed bytes; [R1] "dirty paths: none; HEAD 4497373" (not re-verifiable after the fact, see F3) | - |
| 13 | split_manifest.json names seed, registration, code blob, texts DB sha | CONFIRMED | cat split_manifest.json | seed "LCB-STAGE0-SPLIT:cc7a6d7f31345d571253c67ca9799d2e8a3d95c4"; registration LCB-STAGE0-INTERACTION; script_pins draw.py blob ed5801a8 / lf16 23618585, common.py blob 022f11bf / lf16 a890323a (both re-derived); closure pins 05224b5a / 003d5d4e / 1533cb5a; texts_db_sha256 5f8ae5d8...; side_tsv_sha256 and closure_edges_sha256 equal the files; dev false, label OF RECORD, draw_tag taxoarena-split-v2, ratios 0.3 / 0.1 | - |
| 14 | Draw code unchanged from the READY build (identity line of READY, section 3) | CONFIRMED | git rev-parse {ed948d6,4497373,3c70660}:tools/analysis/lcb_stage0/{draw,common,__init__}.py | all three blob-identical across the three commits | - |
| 15 | Drawn once | CONFIRMED as far as git can show | `git log --all --oneline -- .../split_side.tsv .../split_manifest.json \| wc -l` | 1 commit (3c70660) on any ref | - |
| 16 | Texts DB unchanged | CONFIRMED | sha256sum and ls --full-iso before and after | 5f8ae5d8... both times; mtime 06:38:02.036 both times; no sidecar created | - |
| 17 | No outcome ingested before the side manifest (R2 / H3) | CONFIRMED (state) | `ls` of TAXOARENA_LCB_ROOT | 3 entries: the texts DB, the superseded texts DB, submissions_6ca212e9/; no lcb_v6_train_gate_* or lcb_v6_eval_sealed_* DB exists yet | - |

## Findings

- **F1 (LOW, disclosure; not a defect of the draw).** "Content-closed" is relative to A7's R = 6 policy.
  - 366 cross-side pairs share a RAW common run of >= 20 tokens once masked shingles (df > 6) are counted.
  - I read the longest eight. All are boilerplate:
    - a sample output of 50 zeros (abc306_b EVAL / abc331_c TRAIN);
    - the AtCoder "input is given from standard input in the following format ..." block;
    - the multi-test-case header;
    - the grid preamble;
    - the N x N matrix input layout;
    - an XOR definition.
  - Sensitivity (rsens.py): cross-side pairs with an unmasked run >= 20 at R = 6 / 8 / 10 / 15 / 20 / 30 number 0 / 14 / 15 / 27 / 47 / 72.
  - The top examples at R = 8-10 are the same templates.
  - The registration's disclosed containment pair abc339_a (GATE) / abc344_a (EVAL) sits on two sides. Its shared run is the input-format block (37 tokens raw, 28 unmasked at R = 20), and the two tasks differ.
  - Fix: the outcome writes "content-closed under CK-CLOSE-v2 (R = 6 policy)". It quotes the 134-pair band, of which 76 pairs cross sides, as disclosed.
- **F2 (LOW).** The `stratum` column of split_side.tsv holds the COMPONENT's modal stratum (the draw stratum), not the problem's own.
  - The two differ for 40 problems in the 33 multi-stratum components.
  - The runlog's [R3] table uses own strata, and it says so.
  - Nothing is wrong with the draw. A downstream reader who takes the TSV column as the problem's own stratum would misclassify 40 problems.
  - Fix: name it in the outcome, or in the analysis that reads the TSV. analysis.py's permutation strata are format x dhat quintile, not this column, so the primary test is unaffected.
- **F3 (LOW, carried from READY D8).** "Run exactly once" and "dirty paths: none" are the tool's own statements.
  - The git history shows a single commit of the outputs on any ref.
  - The draw is byte-deterministic given texts DB 5f8ae5d8 and the seed, as reproduced here. A hidden re-draw with the same seed would therefore yield identical bytes. A re-draw under another seed is not excluded by anything but the record.
  - Nothing to fix beyond D8's disclosure.
- **F4 (LOW).** split_manifest.json's script_pins name draw.py and common.py but not __init__.py, which the READY identity line includes. __init__.py is blob-identical at ed948d6 / 4497373 / 3c70660 (blob:a861097a), so the gap has no consequence here. Fix: pin it in any future draw manifest.

No BLOCKER, HIGH or MEDIUM finding.

## What this review does NOT show

- Anything about outcomes: none was read, and none exists yet in TAXOARENA_LCB_ROOT.
- The raw download or the ingest's derivation of the texts DB from the submissions: the texts DB is taken at its pinned sha.
- The tree, the build, the analysis or D1-D9 of the READY.
- That R = 6 is the right policy: it is a stated policy, A7.
- That the working tree was clean at the moment of the draw: that is the runlog's statement.
