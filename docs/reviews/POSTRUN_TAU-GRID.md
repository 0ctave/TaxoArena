# POSTRUN review: TAU-GRID (is the L2 re-read an artefact of S-TAU's factor-2 grid for tau_L2? EXPLORATORY, WORK rows only)

Authority: D-2026-10-26-1 item (3) (a8990e4b, `docs/agents/author_decisions/2026-10-26.md`, incl. the main session's
reading: "does not switch the deciding estimator"). Reviewer: adversarial reviewer, 2026-10-26. Zero LLM calls. My loads
read no vault or reserved response (`guard.reads` 0 on MATH, MMLU-Pro, MMLU). This is structural (WORK split; the guard
is never armed), not a count. Reviewed: benchzoom branch `tau-grid` (local; remote branches containing fdeee7f: 0),
8d8d824..fdeee7f. 8d8d824 is still master's tip, so the merge is a fast-forward.
- Run of record: 32c2e6e, script `blob:d89d8ea1d804f863d9bbe0a1969df47bf98b78a3` (LF, sha256-lf16:f689bf63efe3d92e). The
  working tree has 0 CR bytes, so there is no CRLF rendering. All 3 part JSONs and meta carry `dirty ""` and head 32c2e6e.
- Tip blob `601416f5` (= working tree). Its only hunk vs the run blob is `@@ -119,0 +120,16 @@`, inside the module docstring
  (which closes at L136). Plan `docs/tau-grid.md` blob `4ef4f65c`; test blob `a0e9fd42`.
- Outputs: `E:/benchzoom_demo/followups/tau-grid` (SHA256SUMS sha256 75e7bb179f050030, summary.txt 36ea3e91669bc6a1).
  `sha256sum -c`: 10/10 and 15/15; backup 15/15 and 10/10; `cmp` of the two SHA256SUMS files: identical.

## Verdict

**OUTCOME CONFIRMED (exploratory). The rule word GRID MECHANISM SUPPORTED stands (MATH, MAP, cont vs g2). Branch
MERGEABLE. No BLOCKER. Two record conditions (R1, R2) and four LOW items.**
- Every deciding number reproduces from my own wiring (independent script, see Commands):
  - own criterion: own sums, shrinkage and clipped log-loss;
  - own continuous optimiser: an 802-point dense log grid, then bounded Brent with xatol 1e-10. This is not the
    builder's golden section in the g4 bracket;
  - own L2 offsets in every context;
  - library `meter.step` / `gw.reader` for RR, L3a and the C1 chain, and the reviewed REREAD-STEPS `held_chain` for the MAP.
- Per-item agreement with the builder's npz:
  - g2: 0 to 1.6e-16;
  - cont: ≤ 1.8e-10 (MATH), 3.5e-10 (MMLU-Pro), 1.4e-9 (MMLU). The source is |tau_cont mine − builder| ≤ 5.3e-8.
  - tau_RR and tau_L3a equal the builder's in 75/75 tasks under both g2 and cont.
- The plan preceded every statistic. The word follows the pre-specified rule. There is no src change, and the branch
  touches only its own 3 new files.
- **In substance:** with tau_L2 picked continuously by the same S-TAU inner criterion (same folds, seeds and inner
  contexts), S-TAU sets tau_RR = 0 in 25/25 tasks on every dataset, so the re-read is exactly 0. The criterion has ONE
  local minimum in every one of the 75 tasks (dense grid), so the "local search" caveat does not bite.

## Per-claim table (deciding claims; x 1e-3 nats per cell; WORK rows only)

| # | Claim (builder) | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | Plan 2b1bb0e before any statistic; [P1] insertion only | D-2026-10-26-1 16:38:26; plan 16:47:21; runner 32c2e6e 17:18:24; MATH part 17:18:42-17:24:22; MMLU-Pro end 17:26:26, MMLU 17:48:33; analyze 17:49:07; [P1] fdeee7f 18:04:09. Plan lines deleted after 2b1bb0e: 0 (numstat 39/0). Files in `E:/TaxoArena_tmp/tau-grid` before 16:47:21: 0 (`find -newermt`); scratch = fixture selftests and mutants only. NOT APPLICABLE branch present in 2b1bb0e itself | CONFIRMED | - |
| 2 | RA: g2 = REREAD-STEPS per item (0.0), per-task tau² equal, digits | Comparator npz sha256 = its SHA256SUMS; clusters equal. Builder g2 vs REREAD-STEPS max\|diff\| 0.0 on all 6 arrays × 3 datasets; mine vs builder 0 (MAP) / ≤ 8.8e-17 (n = 1). MATH R_inf +0.0114032 (0.0036381), R_1 +0.0116412; MMLU +0.0135539 (0.0101741); MMLU-Pro +0.0250075 (0.0154508): equal to POSTRUN_REREAD-STEPS claims 3-5 to 7 digits | CONFIRMED | - |
| 3 | RB: C1(V0) = FLAT-COMPARE per item; MATH +0.1093 SE 0.0316 | max\|diff\| 0.0 (3 datasets); MATH +0.1093248 (0.0315934) | CONFIRMED | - |
| 4 | Same inner criterion, folds, seeds for every grid and cont | Own criterion's argmin on TAU_GRID = library tau_L2 = builder g2 in 25/25 × 3; own g2 L2 vs library ≤ 2.7e-15; builder's criterion at its cont minus mine: −7e-12 .. +1.2e-10 nats (same minimum); variants are computed inside the same fold task from the same contexts | CONFIRMED | - |
| 5 | MATH R g2 → cont +0.0114 → 0.0000; D +0.0114 (0.0036; 3.13) | R_cont ≡ 0 per item (max\|.\| 0, both n). D +0.0114032, paired SE 0.0036381, z 3.1344 | CONFIRMED | - |
| 6 | Composite SE z 3.03; DEFF 1.005; n_eff; MDE80 0.0103 | Per-seed drops 0.01475/0.01217/0.00982/0.01006/0.01022 → composite SE 0.003757, z 3.0354. Re-measured from this cache's clusters (2,949 items / 2,946 clusters): iid SE 0.003629, DEFF 1.0051, n_eff 2,934, MDE80 0.010338 (91% of D). Plan Support (DEFF 1.005, source POSTRUN_REREAD-STEPS table S; SE 0.003638 = 0.003629 × √1.005) reproduces | CONFIRMED | - |
| 7 | Word SUPPORTED by the pre-specified rule | R_c/R_g2 = 0 ≤ 0.5; D ≥ 2 SE_D (3.13); evaluation order WITHHELD, NA, SUPPORTED, KILLED, UNCLEAR as planned; RA REPRODUCED on all three | CONFIRMED (qualifier C1) | - |
| 8 | tau_RR = 0 in 25/25 under cont; cont tau_L2 MATH 0.048-0.073, MMLU 0.094-0.107, MMLU-Pro 0.049-0.066 | Mine 25/25 × 3; 0.04811-0.07290, 0.09363-0.10661, 0.04912-0.06586; none at the bound; golden point taken 25/25 × 3; MAP safeguard 0, 5 iterations; fallbacks 0 | CONFIRMED | - |
| 9 | PR1-PR3 HELD; PR4 FAILED (MMLU H −0.0204 (0.0055)) | PR2 8/8 in (0.04, 0.08); PR3 25/25 > 0.08. H cont − g2: MATH −0.000387 (0.000333), MMLU −0.020362 (0.005491; 3.71 SE), MMLU-Pro +0.005838 (0.005221) | CONFIRMED | - |
| 10 | MMLU C1 −0.0104 (0.0045) | −0.010398 (0.004464), 2.33 SE | CONFIRMED (descriptive) | - |
| 11 | "Record's net of re-read ≠ cont" (MATH +0.1117 vs +0.1228, MMLU +0.0463 vs +0.0395, MMLU-Pro −0.0355 vs −0.0046) | Levels confirmed. Paired H_cont − net_g2: MATH +0.0110 (0.0036, 3.0 SE), MMLU-Pro +0.0308 (0.0149, 2.1 SE), MMLU **−0.0068 (0.0093, 0.7 SE)**. So "net" UNDER-states the cont headline on MATH and MMLU-Pro, and on MMLU it is within noise of it | PARTLY (R2) | MEDIUM |
| 12 | No src change; selftest 66 PASS; mutants 69/70; suite exit 0 (898); ruff clean | `--name-only \| grep -c ^src/` 0 of 3 files; execution_graph.md unchanged (no algorithm change, not required). Selftest rc 0, 66 PASS / 0 FAIL; `tests/test_tau_grid.py` 2 passed; collect-only 898/904 (6 deselected), no errors; ruff clean. Full suite NOT re-run by me (the delta adds files only) | CONFIRMED (suite: collection only) | LOW |
| 13 | No write to inputs | Files newer than my start marker under `E:/benchzoom_cache`, `E:/benchzoom_demo` and the worktree: 0; worktree `git status --porcelain` 0 lines | CONFIRMED | - |

## Defects, conditions, fixes

- **R1 (record condition): quote the word with its qualifier.** Suggested wording: "SUPPORTED (exploratory, MATH WORK,
  MAP); structural: tau_RR(cont) = 0 in 25/25; z 3.13 is the g2 re-read's own z".
  - Because R_cont ≡ 0, D ≡ R_g2 per item, so the test adds no strength beyond REREAD-STEPS claim 3. The new evidence is
    the count tau_RR(cont) = 0 (75/75) plus unimodality.
  - The result was close to foregone. At an optimum of the shared inner criterion, a small RR read is approximately a
    small step in tau_L2, which cannot help to first order.
- **R2 (record condition; MEDIUM): what moves in the record.**
  - The mechanism is asymmetric. RR can only add dispersion, so the re-read appears only where g2 undershoots
    (MATH 8/25 at 0.04; MMLU 25/25 at 0.08 below cont ≈ 0.1).
  - Where g2 overshoots (MATH 17/25 at 0.08 above cont), nothing compensates, so the grid bias on the leaf readouts is
    two-sided and not removed by "net of re-read".
  - On WORK MMLU the leaf headline itself falls by 0.0204 (3.7 SE), more than the re-read (0.0136). The g2 net is within
    0.7 SE of the cont headline.
  - Consequence for the vault figure of record C-M1 +0.1171 (BZ-AXIS-CONFIRM-MMLU), not re-read here: the raw figure is
    the one exposed. Keep quoting it only beside its net +0.0864 (already POSTRUN_BZ-AXIS-CONFIRM-MMLU D1). Bracket it:
    "WORK analogue: the coarse tau_L2 grid inflated G(L3a|L2) by 0.0204; whether the vault moves is open".
  - Do not call "net of re-read" a conservative bound: it is conservative on MATH and MMLU-Pro WORK and undetermined on
    MMLU.
- **C2 (LOW): selftest gap.** My mutant V5 (the half leg reads R_g2 at one step instead of the MAP) SURVIVES. The fixtures
  have R_g2(1) = R_g2(inf). It is not decisive on the run of record: R_cont ≡ 0 makes the half leg hold for either.
  Fix: add one fixture where R_g2(1) and R_g2(inf) straddle 2 R_v.
- **C3 (LOW): "strictly between g2 points in every task" carries no information** for a continuous optimiser (any
  non-grid float qualifies). The informative facts are PR2 (8/8 in (0.04, 0.08)), PR3 (25/25 > 0.08) and the ranges.
  Fix: drop the phrase in the record.
- **C4 (LOW): the hand-back table omits D for MMLU and MMLU-Pro:** +0.0136 (0.0102; 1.33) and +0.0250 (0.0155; 1.62).
- **C5 (LOW): full suite not re-run by the reviewer** (collection and the new test only). Run the full suite at merge
  if master moves.

**What it licenses (exploratory, WORK rows only):**
- On MATH WORK rows the L2 re-read of record (+0.0114 at the MAP, 3.13 SE) is a product of S-TAU's factor-2 grid for
  tau_L2. With tau_L2 chosen continuously by the same criterion, S-TAU sets tau_RR = 0 in every task.
- The same structure holds on MMLU and MMLU-Pro descriptively (z 1.33 / 1.62 for the g2 re-read).
- g4 (factor 2^(1/4)) already removes it (MATH −0.000008, SE 0.000219); gs2 overshoots (negative re-reads).
- Under cont, G(L2|L1) rises: MATH +0.0199 (4.5 SE), MMLU-Pro +0.0461 (3.7 SE), MMLU +0.0158 (1.5 SE).

**What it does not license:**
- Any switch of S-TAU's grid (`meter.TAU_GRID`) or of any deciding estimator (the author's; no default changed).
- Any vault, reserved or registered number. C-M1 +0.1171 and net +0.0864 were not re-read.
- That the re-read is zero under a continuous tau_RR. RR, L3a and the C1 readers stayed on TAU_GRID, whose smallest
  positive point is 0.0025.
- That leaf gains are grid-invariant. PR4 FAILED: MMLU H −0.0204, C1 −0.0104.
- That "net of re-read" is a lower bound (R2).
- Any statement at n_eff below the WORK sizes. The MATH MDE80 is 0.0103 against D 0.0114, so only a near-complete
  mechanism was detectable.

## Own mutants (sandbox copies `E:/TaxoArena_tmp/tau-grid-review/mut/r1/<id>`; TMP/TEMP/TMPDIR/BZ_SANDBOX redirected; deciding paths)

| id | change | result | decisive |
|---|---|---|---|
| V0 | control | passes (66/0) | - |
| V1 | rule reads D / SE from the one-step drop | killed (S5 word SUPPORTED; 11 FAIL) | yes |
| V2 | variant tau_L2 in the main context only; inner contexts keep g2's L2 (RR selected on g2) | killed (S4 one task cont MAP RR / L3a) | yes |
| V3 | RR selected on g2's L2 for every variant | killed (AssertionError held n = 1 differs) | yes |
| V4 | criterion drops the last inner context | killed (AssertionError g2 tau_L2 guard) | yes |
| V5 | half leg reads R_g2 at n = 1 | **SURVIVED** (C2) | no (R_cont ≡ 0) |
| V6 | cont = g4 choice (golden point never taken) | killed (S3 interior minimum) | yes |
| V7 | drop = g2 MAP − cont one-step | killed (S4 drop recomputed) | yes |

## Commands (reviewer; read-only on every input; scratch `E:/TaxoArena_tmp/tau-grid-review`)
```
git diff --name-only 8d8d824..fdeee7f | wc -l -> 3; ... | grep -c '^src/' -> 0; git branch -r --contains fdeee7f | wc -l -> 0
git rev-parse 32c2e6e:examples/tau-grid.py -> d89d8ea1; git hash-object examples/tau-grid.py -> 601416f5; grep -c $'\r' -> 0
git diff -U0 32c2e6e fdeee7f -- examples/tau-grid.py | grep '^@@' -> @@ -119,0 +120,16 @@ ; git diff --numstat 2b1bb0e..fdeee7f -> 39 0 docs/tau-grid.md
git diff --name-only {983c34f,8177915} 8d8d824 -- src <harness examples> | wc -l -> 0, 0
sha256sum -c SHA256SUMS (10/10), SHA256SUMS_all (15/15); backup 15/15, 10/10
python pooled.py        # pooled values, D, SEs, DEFF, n_eff, MDE80, composite SE, RA/RB vs comparator npz (sha-checked)
python indep.py <ds> 5  # independent fold tasks (own criterion + dense grid + Brent; library S-TAU; held_chain MAP)
python compare.py <ds>  # mine vs builder per item / pooled / per task (MATH 399 s, MMLU-Pro 119 s, MMLU 1,422 s)
python examples/tau-grid.py --selftest (sandboxed) -> rc 0, 66 PASS, 0 FAIL; pytest tests/test_tau_grid.py -> 2 passed
pytest --collect-only tests -> 898/904 (6 deselected); ruff check -> clean; NPAR=3 python mutants_rev.py r1 -> 6/7 killed
find E:/benchzoom_cache E:/benchzoom_demo <worktree> -newer marker_start -type f | wc -l -> 0
```
