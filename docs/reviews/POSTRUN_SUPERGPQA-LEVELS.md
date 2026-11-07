# POSTRUN review: SUPERGPQA-LEVELS (lead #3; declared finer levels on SuperGPQA's content-closed EVAL; exploratory, key only)

Authority: D-2026-11-06-3 (`docs/agents/author_decisions/2026-11-06.md`), leads file `docs/agents/plans/2026-11-06_leads.md`
"### 3. SUPERGPQA-LEVELS" (b42d58ef). Reviewer: adversarial reviewer, 2026-11-06. Zero LLM calls by me. Read by me: the
STAGE0b key DB (`mode=ro&immutable=1`; sha256 9898d91a... and mtime equal before and after my reads), the question file
(uuid / discipline / field / subfield), the split, the exclusion list, the STAGE0b outcome file, the run's saved outputs.
Sealed / RESERVED / vault rows read by me: 0 (the key DB holds sides EVAL 371,959 rows / 7,591 uuids and TRAIN 866,663 /
17,687, nothing else: `select side, count(*) ... group by side`). At most 3 processes, BLAS 1. Scripts: scratchpad
`.../7c10e5cb-.../scratchpad/sg/` (`rv_sgl.py`, `rv_rp.py`, `rv_mut.py`, `rv_mut2.py`); mutant sandboxes
`E:/TaxoArena_tmp/rv_sgl_154736`, `E:/TaxoArena_tmp/rv_sgl_154822`; nothing deleted.

Reviewed: benchzoom branch `supergpqa-levels` (worktree `Z:/FAC/TUBerlin/benchzoom_wt_supergpqa-levels`), 4d08a3d..db52ea6:
4 new files (`git diff --name-only master..db52ea6 | wc -l` = 4; none under `src/`, so `docs/execution_graph.md` owes
nothing); master = 4d08a3d = the branch base (fast-forward). The pending review-fixes tip 06456b2 touches 10 other paths,
0 of them `supergpqa*` (`git diff --name-only 4d08a3d 06456b2 | grep -c supergpqa` = 0): the two merge in either order.
- Pins at tip (LF of record; `git hash-object` = `git rev-parse db52ea6:<path>`; 0 CR bytes in each working file, so no
  separate CRLF rendering): plan `blob:12767b05` (sha256-lf16:1207845f9f104244), runner `blob:c4138aa6`
  (sha256-lf16:34e6a2b96c86ec9c), mutant spec `blob:61d16b20` (sha256-lf16:af351c2bd85371a8), tests `blob:4663d95d`
  (sha256-lf16:ac6592732ce7c09e). Run of record: runner `blob:95eede91` at HEAD 9be5093, `dirty ''`, plan `blob:817c99f6`
  (= af4bccc's), meter `blob:f31973af` (= master's). Tip runner AST-identical to 95eede91 outside the module docstring
  (`ast.dump` equal; `git diff 9be5093 db52ea6 --stat`: runner +9, plan +55, insertions only).

## Verdict

- **SUPERGPQA-LEVELS: OUTCOME CONFIRMED (exploratory; key only; a second statistic on the STAGE0b EVAL; population
  SuperGPQA minus its 1,251 MMLU-Pro collisions), with qualifiers Q1-Q2 (MEDIUM) and Q3-Q6 (LOW).** Every deciding number
  reproduces to the printed digit from my own loaders; an own driver of the meter functions reproduces all four per-item
  arrays BIT-EQUAL and all 600 null gains to 1.4e-17; an own routing implementation (tuple-max policies) reproduces the
  G_route point, and an own two-stage bootstrap (other seed, other code) gives SE 0.474pp against 0.475pp.
- **The sub|field SUPPORTED word is CONFIRMED as computed but must not be quoted without Q1**: the plan's own Support rule
  (section 11 (b)) makes it DESCRIPTIVE-ONLY, and the word holds only under the planned subfield clustering (z 4.22); by
  field it is z 2.98, by discipline z 2.90, both INCONCLUSIVE. The [P1] "Licensed" line and the hand-back omit both.
- **MERGEABLE: YES**, fast-forward, 4 new files, 0 `src/`. Q1 goes into an insertion-only plan bracket [P2] (or the
  registrar's record verbatim); no rerun is needed. No BLOCKER. AUTHOR DECISIONS NEEDED: none.

## Per-claim table (deciding claims; 7,591 EVAL items x 49 models; x 1e-3 nats per (model, EVAL item) cell)

| # | Claim (builder) | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | Plan af4bccc before every statistic on responses | reflog: branch born 14:16:24 at 4d08a3d; af4bccc 14:57:25 (plan only, 1 file); 9be5093 15:09:06; db52ea6 15:36:05. Run outputs written 15:21:49 (12 min 31 s, so started about 15:09:18, after 9be5093) and 15:34:23. Pre-plan artefacts: `support.json` 14:55 (sha256 d35b6243 = the plan's pin; `support.log` opens qfile / split / excl only, no `[OPEN] key_db`), `mutants.py` 14:44 (runs selftests on fixtures). `find E:/TaxoArena_tmp -maxdepth 3` in 14:00-15:09:10: 405 entries, 32 supergpqa-related, all mutant / selftest / message / spec files; `make_spec.py` and `mutants.py` hold 0 sqlite / key references (`grep -c`); 0 of the other `.py` files there mention supergpqa or the key; 0 files in the claude temp in that window. Limit: the builder's key-free precondition reads left no artefact, so "the `correct` column was never selected" is unverifiable either way | CONFIRMED (artefact evidence) | - |
| 2 | Data object: key only, nothing sealed / RESERVED / vault | the runner opens exactly 5 files (grep of `open(`/`connect(`/`read_text`: qfile, split, excl, key DB ro+immutable, STAGE0b outcome); key DB sides EVAL / TRAIN only; split = TRAIN / EVAL (no reserved key); key DB sha256 + mtime unchanged by my reads (2026-09-29 mtime) | CONFIRMED | - |
| 3 | Preconditions: subfield nested; 2 twin families inside one subfield and one side | own loader: 0 fields in > 1 discipline, 0 subfield names in > 1 field; twins: one EVAL pair (Literature and Arts / Language and Literature / Classical Chinese Literature), one TRAIN pair (Science / Chemistry / Inorganic Chemistry), neither excluded; 25,278 = 17,687 + 7,591; 13 / 72 / 285; EVAL per subfield min 8, median 19; 7,590 EVAL components; 0 side mismatches; 0 empty cells | CONFIRMED | - |
| 4 | STAGE0b RP1-RP4 REPRODUCED | own code: RP1 49 / 49 pooled EVAL accuracies equal (4 d.p.); RP2 10 scored disciplines, n 7,396 in 7,395 components, DeepSeek-R1, 0.6195 / 0.6130, +0.65pp; RP3 dominance column equal on all 10; RP4 18 fields, n 4,927, +0.91pp / +0.71pp | CONFIRMED | - |
| 5 | Rerun bit-equal on all 10 files; backup 35 files verified | own `sha256sum` of every file: run = rerun (10 / 10); backup `run/` = output dir; `sha256sum -c` 35 / 35 OK (36 files incl. SHA256SUMS) | CONFIRMED | - |
| 6 | field\|disc (DECIDING) +1.5955, SE_word 0.6681 (72 fields), z 2.39, INCONCLUSIVE; meter SE beside SUPPORTED | g +1.5955; CR SE by field 0.6681 (72), by comp 0.1452; cell-iid 0.0920 -> DEFF 52.76, n_eff 144; MDE80 2.5667; q95 0.0000; word INCONCLUSIVE, meter-SE word SUPPORTED | CONFIRMED; quote as "not detected at 3 SE_word (MDE80 2.57 > g)", Q2 | - |
| 7 | sub\|field (DECIDING) +0.2799, SE_word 0.0664 (285 subfields), z 4.22, SUPPORTED | g +0.2799; SE by sub 0.0664 (285), field 0.0938 (z 2.98), disc 0.0964 (z 2.90), comp 0.0454; cell-iid 0.0354 -> DEFF 3.52, n_eff 2,157; MDE80 0.2549; q95 0.0015 (16 of 200 null gains > 0, max 0.0100); word SUPPORTED | number CONFIRMED; wording PARTLY (Q1) | MEDIUM |
| 8 | disc\|L0 (secondary) +2.6844, SE 0.8986 (13), z 2.99, INCONCLUSIVE | g +2.6844; SE by disc 0.8986; DEFF 56.10, n_eff 135; MDE80 3.4519; q95 0; INCONCLUSIVE (meter SE beside SUPPORTED) | CONFIRMED (13 clusters) | - |
| 9 | Routing +0.11pp, SE_2stage 0.48pp, MDE80 1.83pp, NEITHER | own policies: G_route +0.1054pp; 32 / 72 fields and 153 / 285 subfields differ; SE_iid 0.2916pp; saved replicates SD 0.4752pp, DEFF 2.656, n_eff 2,859, MDE80 1.83pp, z 0.22 -> NEITHER; own bootstrap (seed 777) SD 0.4740pp; descriptive sub-field -1.2383pp, disc-best +0.5928pp | CONFIRMED (DESCRIPTIVE-ONLY), Q6 | - |
| 10 | P2, P4-P7 HELD; P1, P3, P8 FAILED; F1 NOT FIRED; depth "backbone" | re-scored from my numbers against plan section 8: identical; tau^2 0.08 / 0.04 / 0.02 (own refit) so P5 0.02 <= 0.04 HELD; F1 needs NOT SUPPORTED / DEGENERATE, field\|disc is INCONCLUSIVE | CONFIRMED | - |
| 11 | Selftest passes; mutants 79 / 79 non-equivalent killed (X39a equivalent); 2 crash-kills | control passes in my sandbox (7 s); results_r4 / r5: 81 rows, 79 killed, survivors X0 (control), X39a. Killed by a crash, not an assertion: **4** (X70, X71, X77 KeyError, X79 IndexError), not 2; killed by a designed refusal: X13, X22, X29, X35, X78 (legitimate). Own mutants: 9 of 10 killed, OM8b survives (Q4) | PARTLY (count) | LOW |
| 12 | Full suite 1039 passed, 1 skipped, 0 failed | own run at db52ea6 (BLAS 1, TMP in E:/TaxoArena_tmp/rv_sgl_suite): 1039 passed, 1 skipped, 15 deselected, 0 failed (17 min 22 s) | CONFIRMED | - |
| 13 | Support projection wrong (builder's MEDIUM) | planning MDE80 about 0.3 at g 0.6 vs realised 2.5667; SE_word / SE_meter 4.60 vs 1.5-2.6 planned; disc\|L0 SE 0.8986 vs 0.53-0.71 | CONFIRMED | MEDIUM (Q2) |

## Qualifiers and defects (each with its fix)

- **Q1 (MEDIUM) sub|field wording.** Plan section 11 (b), fixed before the data: sub|field is "DESCRIPTIVE-ONLY for a
  SUPPORTED word", and the rule reads "the word is printed and read descriptively only". [P1]'s "Licensed" sentence
  states it as a finding with only "exploratory". The word is also convention-bound: SUPPORTED under subfield (planned)
  and component clustering, INCONCLUSIVE under field (z 2.98) and discipline (z 2.90). Under the item-level SE every level
  reads SUPPORTED, under the parent-cell SE none does: which levels read SUPPORTED is a property of the SE convention
  (the builder's own [P1] caveat). Fix: insertion-only [P2] (or the registrar's record) quoting it as "the declared subfield
  adds held-out per-model predictive information beyond the declared field on the content-closed EVAL (g +0.28 x 1e-3
  nats per cell, SE 0.066 clustered by subfield as planned, z 4.2; exploratory; second statistic on the STAGE0b EVAL;
  DESCRIPTIVE-ONLY at the planned Support (section 11 b); size unpredicted (P3 FAILED); INCONCLUSIVE when clustered by
  field, z 2.98)". The hand-back's "SUPPORTED (z 4.22)" is never quoted alone.
- **Q2 (MEDIUM) the Support projection was REFUTED** (builder's own finding, confirmed): field|disc was declared SCOREABLE
  on one homogeneous-offset draw per scenario; the realised DEFF is 52.8 (n_eff 144), so INCONCLUSIVE is an underpowered
  non-detection (MDE80 2.57 > g 1.60), never "no structure below the discipline". Fix: the record quotes the MDE80 beside
  the word; a later declared-cell plan on this corpus cites DEFF 52.8 / n_eff 144 (field) and 3.5 / 2,157 (subfield) from
  this run as its DEFF source, or plants between-cell heterogeneity in its simulation.
- **Q3 (LOW) the null is non-binding.** disc|L0 and field|disc: 0 of 200 null gains > 0 (tau^2 = 0 in 198 / 192), q95 0, so
  the clause g > q95 cannot decide; sub|field q95 0.0015 against g 0.28. The words rest on the SE clause alone. Fix: print
  "null non-binding (q95 0)" beside those words in the record. No word changes.
- **Q4 (LOW) selftest gap.** OM8b (depth readout reading `word_meter_se` with a fallback) survives: no fixture has SE_word
  and SE_meter words disagreeing at the depth readout. The real depth line is right ("backbone"; own words). Fix: one S5
  case with disagreeing words and an asserted depth.
- **Q5 (LOW) crash-kill count.** 4 mutants die by crash (X70, X71, X77, X79), not 2. X70 / X71 crash because the sandbox
  copy has no git repository (the guarded call proceeds to `git`), so the run-of-record refusals are not proven by
  assertion. Fix: correct the count in the docstring / registrar's record; re-run X70 / X71 in a sandbox with a git repo.
- **Q6 (LOW) routing bootstrap centre.** The replicates centre at -0.665pp (own bootstrap -0.672pp) against the point
  +0.105pp (argmax refits on resampled TRAIN): the normal interval [-0.83, +1.04] is centred on the point, the percentile
  [-1.62, +0.22] is not. Descriptive only; quote both, as printed.

## Own mutants (sandbox copies; `rv_mut.py` / `rv_mut2.py`; control OM0 passes)

OM1 word q95 -> -1e9 in word_block: killed (S3 q95 linear) · OM1b null ignored only inside the word: killed (S5 q95
decides), decisive · OM2 tau^2 -> 1.0 (never DEGENERATE): killed (S5 tau 0 DEGENERATE) · OM3 delta_min 0.3 in the word
(on the real data sub|field would read BELOW INTEREST): killed (S5 below interest), decisive · OM4 G_route against the
best single: killed (S6 G_route by hand), decisive · OM5 P2 upper bound 1.50 (flips P2 on the real data): killed (S7 upper
boundaries), decisive · OM6 nulls permute EVAL rows only: killed (S3 null replicate 0 = reference) · OM7 twins not merged
into components: killed (S1 components) · OM8 depth from `word_meter_se`: killed by KeyError (crash) · OM8b same with a
fallback (on the real data depth would read "subfield"): SURVIVED, decisive for the descriptive depth line only (Q4).

## Commands

```
# pins / ancestry / tip delta
git -C <wt> rev-parse 9be5093:examples/supergpqa-levels.py   # 95eede91; tip c4138aa6 = hash-object
git -C <wt> diff 9be5093 db52ea6 --stat; python ast.dump compare (docstring blanked) -> True
git -C <wt> diff --name-only master..db52ea6 | wc -l   # 4 ; grep -c '^src/' -> 0
git -C <wt> reflog --date=iso supergpqa-levels          # 14:16 / 14:57:25 / 15:09:06 / 15:36:05
find E:/benchzoom_demo/followups/supergpqa-levels* -type f -printf '%T+ %p'   # outputs 15:21:49, 15:34:23; support 14:55
# numbers (read-only; own code)
python -I rv_sgl.py fast    # loaders, CR SEs x4 clusterings, words, DEFF, routing policies, own bootstrap, RP1, key DB unchanged
python -I rv_sgl.py refit   # own meter driver: 4 per-item arrays bit-equal; 600 null gains maxabs <= 1.4e-17; tau0 198/192/147
python -I rv_rp.py          # RP2-RP4
sha256sum (run vs rerun vs backup/run); cd backup && sha256sum -c SHA256SUMS   # 35/35 OK
# vacuity
python -I rv_mut.py ; python -I rv_mut2.py   # OM0-OM8, OM1b, OM8b
python results_r4/r5 tally   # 79 killed; crash-kills X70 X71 X77 X79
PYTHONPATH=src .venv/Scripts/python.exe -m pytest -q -p no:cacheprovider   # at db52ea6
```
