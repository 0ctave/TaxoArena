# READY review: FITSET-FAITHFUL stage 0 (adversarial-reviewer, 2026-10-03; zero calls)

Reviewed: branch `fitset-faithful`, tip d4baa036 (parent = main 111c2dc2; `merge-base --is-ancestor 111c2dc2 d4baa036` true);
`tools/analysis/fitset_faithful.py` blob:ed34306596ef63ba2d4b59bc24d54fad0eb8149a (LF, `git hash-object` = `git rev-parse
HEAD:<path>`), sha256-lf16 3cabb5e382a78237. The worktree file holds 0 CR bytes (`grep -c $'\r'`), so no CRLF rendering exists
there; on a CRLF checkout the LF blob stays the pin (the script's own `blob_lf` normalises). Diff 111c2dc2..d4baa036 = 1 file,
1,301 insertions (`git diff --stat`, whole output). Registration: prog L23580-L23614, gates bracket at L23582 (111c2dc2).

## Verdict: READY, with two pre-data registrar brackets (C-1, C-2) and two record lines (C-3, C-4)

None needs a code change; no criterion, bar, prediction or reading moves. `--run` may launch after the registrar's bracket
commit, from main after the merge (command at the end), never beside a construction or site null (rule 7; it is a pool reader).

## Per-claim table (deciding claims only)

| # | claim | result | mine vs claimed | sev |
|---|---|---|---|---|
| 1 | Refit is TRAIN-only | CONFIRMED | `A["gt"][a] = flatnonzero(yt == a_cls[a])` indexes `o["Xt"]` (bundle train_X, side-checked by g13 I0/check_sides); my assert: every gt index < 12,334 and every label = the anchor's class; naming reads `Xt` only; EVAL read once for filing; M01 killed | - |
| 2 | Class-pure fit sets, out-of-anchor guard | CONFIRMED | union of gt = 12,334 = TRAIN (each item in exactly one declared class); assignment searches only the anchor's own leaves (`ks = by_anchor[a]`) and refuses on a foreign leaf; count guard refuses if an anchor's leaves receive != class TRAIN count; M03, M39 killed | - |
| 3 | 512-d slice | CONFIRMED | Xt (12334, 512), Xe (6139, 512), leaf mu (133, 512) | - |
| 4 | FF1 = A-refit vs A at matched cells | PARTLY (C-1) | cells matched (same 133 leaves, topology, anchors). PIPELINE NOT MATCHED: A's OWN vmfMu cells through DSC.name_and_file (the rule A-refit is filed by) give 0.812347 against the bundle's eval_fl P_A 0.811859: 23 items discordant, net +3 / 6,139 = +0.000489 (1 leaf named differently from the leaves CSV). D carries this offset in the refit's favour | HIGH |
| 5 | Identity vs DSC (refuses) | CONFIRMED | my dry-run: P_A 0.8119, P(B_0) 0.7985, P(D_0) 0.8334, B-gt_0 - D_0 +0.0028, spread_B 0.0125; I1 (d13 -0.0215 [-0.0301, -0.0125], ncc 0.8065, p_kc, ukm), depth 2 (p_tree2 0.8042), I2/I3/I4/R3 PASSED; purity 10,021 / 12,334 | - |
| 6 | Label table and three confounds printed verbatim | CONFIRMED | AST-extracted LABEL_INFO rows and CONFOUNDS (1)-(3): each a substring of the registration span; WILL_NOT_SHOW identical modulo the opening ". That" -> ": that" | - |
| 7 | Write-once outcome | CONFIRMED | exists-refusal + `open(outp, "x")`; outcome path absent now (`ls` error); M18, M19 killed | - |
| 8 | Decision (i) exact bar 0.012543 + KNIFE-EDGE | CONFIRMED (C-2) | 77/6,139 = 0.0125428; D lies on the 1/6,139 lattice, so the exact and rounded bars disagree at ONE point, D = 77/6,139 (HELD vs UNDETERMINED); KNIFE-EDGE prints there; M32, my R3 killed | MEDIUM |
| 9 | Decision (ii) impurity = 1 - declared-class share of F-tree(a), pooled 10,021 | CONFIRMED, moot | majority-class share = declared-class share on all 52 anchors (0 differ); pooled declared = majority = 10,021 = W2 | - |
| 10 | Decision (iii) --root | CONFIRMED | operational: `guard_paths` refuses lane != r2 and runs LN.guard on bundle / both validation dirs / --out under root; I0 pointer sha + printed shas pin the objects | - |
| 11 | FF2 m = 32 vs planned 30 | CONFIRMED (C-3) | 32 split anchors, 20 unsplit; min EVAL of a split anchor 64, so the >= 30 threshold excludes none; m = 32 is the registered rule's own count | LOW |
| 12 | Support arithmetic | CONFIRMED | sqrt(0.10 x 1.223 / 6,139) = 0.0044634; MDE80 0.012497; n_eff 5,019.6; DEFF 1.223 source = DSC outcome L33 (C-DB, measured); SE_z(30) 0.1961, rho-MDE 0.4999; at m = 32: SE_z 0.1890, rho-MDE 0.4847 (FF2 still DESCRIPTIVE-ONLY at P2 0.30); FF1 DESCRIPTIVE-ONLY at P1 +0.015 stands | - |
| 13 | Verdict logic | CONFIRMED | FF1 = DSC.v_spread (lo > 0 and D > bar; hi < 0 and D < -bar); FF2 lo > 0 / hi <= 0; F-FF hi <= 0; SE_z 1/sqrt(m-4); partial Spearman = partial Pearson on average ranks (log size is rank-irrelevant) | - |
| 14 | Selftest / mutants | CONFIRMED | `--selftest` 7 / 7; `--mutants` 39 / 39 KILLED, control survived | - |
| 15 | Real --dry-run, no writes | CONFIRMED | rc 0, 24 s; POOL rc 0 (pin 79d48f4b; DRY RUN nothing written); "NO new statistic"; mtimes/sizes of mmlu_pro_dataset_cache_v2.db, multicorpus_cache_v1.db and every root -wal (0 B) identical before/after; rule 7: only the Gradle and Kotlin daemons (idle) and Ollama | - |

## Conditions / defects

- **C-1 (HIGH; pre-data registrar bracket; no code change).** Pipeline offset of FF1. The registered D compares A-refit filed
  by DSC's common rule with A filed by the engine's flatLeaf CSV (eval_fl). The common rule on A's UNCHANGED leaves files
  3 more items net (23 discordant), so +0.000489 of any D is pipeline, not refit. D stays the deciding contrast (changing the
  comparator would be C-7). Bracket text to fix now: "the refit-attributable point is D - 3/6,139; if FF1 reads HELD with
  D in {78, 79, 80}/6,139 (0.012706-0.013031), it is written 'HELD (PIPELINE KNIFE-EDGE: not held against A filed by the
  common rule)'; if F-FF does not fire with the upper end in (0, +0.000489], it is written 'DOES NOT FIRE (PIPELINE
  KNIFE-EDGE)'". REVERSED is not affected (the offset moves D down). The post-run reviewer recomputes A0 (A's vmfMu through
  name_and_file) and the item-paired D' with its interval beside D. Record note for DSC W1: the same offset favours A in
  C-AB (D_AB against common-rule A would be 85/6,139, margin 8 items, not 5): W1 is not weakened.
- **C-2 (MEDIUM; pre-data registrar bracket).** Decision (i): the registration says "D > spread_B (0.0125, the measured DSC
  comparator spread)"; the exact measured value 77/6,139 = 0.012543 is the faithful reading and is endorsed, but it decides
  the lattice point D = 77/6,139, so it is bracketed before data, with the KNIFE-EDGE line.
- **C-3 (LOW; record line).** FF2 m = 32 (all split anchors; min 64 EVAL items), SE_z 0.189, rho-MDE 0.485: a Support
  fact seen pre-data, not a criterion change; FF2 stays DESCRIPTIVE-ONLY at its prediction.
- **C-4 (LOW; record line, no bracket needed).** Decision (ii) is moot (declared = majority on every anchor);
  decision (iii) is operational.
- **D-1 (LOW, non-decisive).** My R8 (B-gt identity arm at seed 1) survives the selftest (fixture k-means seed-invariant);
  the real-data identity +0.0028 is the seed-0 value, so a seed slip would most likely refuse there. Fix (optional): a fixture
  where B-gt seed 0 and seed 1 differ.
- **D-2 (LOW, descriptive).** D includes the 20 unsplit anchors' re-estimated cells (registered); the per-anchor table lets
  the post-run reviewer split D into split / unsplit true-class items. No change.

## Rulings on what needs a pre-data registrar bracket

C-1 (pipeline offset wording) and C-2 (exact bar) YES, before --run. m = 32 (C-3) and decisions (ii)/(iii) (C-4): a record
line in the same bracket suffices; no re-registration.

## Own mutants (deciding paths; full selftest each)

R1 nearest leaf by argmin: KILLED (decisive). R2 refit mean not normalised: KILLED (decisive). R3 FF1 bar = constant 0.0125:
KILLED (decisive). R4 spread_B over seeds 0-3: KILLED. R5 per-anchor mask rolled by 1: SURVIVED (equivalent on the fixture's
block boundaries; non-decisive); R5b mask reversed: KILLED (decisive). R6 FF1 comparator B_0 instead of A: KILLED (decisive).
R7 impurity -> purity: KILLED (decisive). R8 B-gt identity at seed 1: SURVIVED (non-decisive, D-1).

## Commands

```
cd .claude/worktrees/fitset-faithful
git diff --stat 111c2dc2..HEAD; git hash-object tools/analysis/fitset_faithful.py; git rev-parse HEAD:tools/analysis/fitset_faithful.py
grep -c $'\r' tools/analysis/fitset_faithful.py                      # 0
PYTHONIOENCODING=utf-8 python tools/analysis/fitset_faithful.py --selftest     # 7 / 7
PYTHONIOENCODING=utf-8 python tools/analysis/fitset_faithful.py --mutants      # 39 / 39 KILLED, control survived
TAXOARENA_DATA_ROOT=<main> python tools/analysis/fitset_faithful.py --dry-run --lane r2 --root <main>   # rc 0
ls -la --time-style=full-iso <main>/*.db-wal <main>/mmlu_pro_dataset_cache_v2.db <main>/multicorpus_cache_v1.db  # before = after
scratchpad/ffrev/rev_ff.py   # loads o, A via FF._hooks + GB.load_objects + DSC.load_anchors (read-only): dims; purity declared vs
                             # majority; split/unsplit, min EVAL, m; gt TRAIN/label asserts; zero-refit A0 = DSC.name_and_file(A vmfMu)
                             # vs eval_fl (0.812347 vs 0.811859, 23 discordant); naming diffs (1); Support arithmetic
scratchpad/ffrev/rev_mut.py, rev_mut2.py   # R1-R8 via FF._exec_selftest on all 7 cases
grep -n "1.223" <main>/experiment_results/archv2/rp12_r2/deep_split_compare_outcome.txt   # L33 C-DB DEFF 1.223
```

## --run (after the merge into main and the C-1/C-2 bracket commit; PowerShell, from the main checkout)

`$env:PYTHONIOENCODING='utf-8'; python tools/analysis/fitset_faithful.py --run --lane r2`
(defaults: --root = the script's checkout = main; outcome experiment_results/archv2/rp12_r2/fitset_faithful_s0_outcome.txt,
write-once; precede it by the rule-7 check: no java construction / site null, no other pool reader.)
