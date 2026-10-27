# READY review — EMBED-DIM-SLICE (tools/analysis/embed_dim_slice.py)

Reviewer: adversarial-reviewer, 2026-10-01. Zero calls; no `--run`; one `--dry-run` on the pinned S0 DBs.
Reviewed: branch `embed-dim-slice`, tip `1d27b6a3`, `tools/analysis/embed_dim_slice.py` **blob:068550b4** (LF; the worktree
copy holds 0 CR bytes, so the LF rendering is the working tree): sha256-lf16:d55f950843698a0a (sha256-crlf16:8a77f31392e104ac,
not on disk). Imported S0 machinery `intent_transfer_s0.py` blob:f662ceb1 on main and in the worktree (asserted by the script).
Against: registration `## Registered 2026-10-01 (before any code or call) — EMBED-DIM-SLICE: ...`, prog L22579-L22607 _as_of 46954215.

## Verdict

**MERGEABLE. `--run` READY after merge**, under conditions C1-C4. The branch adds one file (merge-tree clean against main
46954215); the registration heading is on main at L22579 (the worktree predates 6983d397, hence its dry-run's "ABSENT"; `--run`
refuses there, and will pass on main).

## Deciding claims

| # | Claim | Result | Mine vs claimed | Sev |
|---|---|---|---|---|
| 1 | Identity: D(gemma-qwen3, fine, 256) +0.03340 / -0.00691 / +0.05628; S seed 0 0.7598 / 0.8262 | CONFIRMED | Script's dry-run: identical digits; S0's c4() 0.759777 / 0.826195. My independent recomputation (own `mode=ro&immutable=1` read, big-endian decode, own slice + L2, own side masks, sklearn NMI; only S0's skmeans shared for seed identity): +0.03340 / -0.00691 / +0.05628; S 0.759777 / 0.826195. All five equal the record (INTENT-TRANSFER-S0.json, SLOTSWAP M3) | — |
| 2 | GATE-only selection; EVAL read only after selection.json is written and hashed | CONFIRMED | Code path: every EVAL index goes through `eval_idx` (the one `S_idx(...SS.EVAL)` call, L211; census L252-253 counts EVAL rows/components only, dry-run). Phase A = TRAIN fits (`fit_rows` TRAIN-ONLY guard), GATE filing, d2/h_boot on TRAIN. Selftest ST-E2E shows by execution SELECTION = event 0, all EVAL reads after; dry-run fit audit 43 fits, 0 with an EVAL row | — |
| 3 | EB7: the dry-run identity reads EVAL of S0's 256 arms only | CONFIRMED; ADMISSIBLE | Dry-run printed 8 EVAL reads, all @256 (6 NMI + 2 c4); `eval_idx` refuses any other d in dry mode (mutant killed). The values read are of record (S0 C1a, SLOTSWAP M3); no non-256 arm, no GATE score and no selection is computed in the dry-run, and `--run` is a fresh process that recomputes the identity after its own selection. Nothing the selection could condition on is learnt. Admissible (C3 for the record) | — |
| 4 | DS1 = S0's C1 rule; bar = max(MDE80, max(spread_q(d_q*), spread_g(d_g*))), spreads in-run on EVAL | CONFIRMED (code); test gap | `ds1` L429-439 matches the registration and S0's `c1_level` L796-802 (bar formula, BASIC CI decides, `c1_status`). At (256,256) DS1 equals S0's c1_level to 1e-12 (ST-EQUIV). My mutants RV-A (bar from the 256 arms' spreads) and RV-D (status on the percentile CI) SURVIVE: the code is right at this blob, but no selftest pins the bar or the status at d* != 256 | MEDIUM (D1) |
| 5 | Verdict REOPEN-CANDIDATE (BETTER >= 2) / KEEP-STRONG (WORSE >= 2) / KEEP; total | CONFIRMED | `verdict` L446-454; nb>=2 and nw>=2 are exclusive on 3 corpora; every branch printed and executed (ST-UNIT, ST-E2E fixtures R/K/N) | — |
| 6 | Confounds on every outcome line (EB8) | CONFIRMED | `tag_lines` over the whole outcome; ST-E2E asserts every line ends with CONFOUNDS; my RV-E (untagged at the call site) KILLED. CSVs carry no lines of verdict | — |
| 7 | Support (registration) reproduces | CONFIRMED | n_eff 4946/1.0093 = 4900, 6672, 3908/1.0015 = 3902 (dry-run Kish 1.0093 / 1.0000 / 1.0015 re-measured from the components = S0's); MDE80 2.8 x 0.00289/0.00137/0.00247 = 0.0081/0.0038/0.0069; DS3 0.0153/1.96 = 0.0078, MDE 0.022; planning bars = my in-data seed spreads at 256 (qwen3 0.02463/0.00942/0.01434, gemma 0.01757/0.00229/0.01400): exact. (f): 0.045-0.0143 = 0.0307 > 0.0069 SCOREABLE; 0.012-0.0094 = 0.0026 < 0.0038 and 0.022 < 0.0246 DESCRIPTIVE-ONLY. DEFF source named (S0 measured). Non-vacuous | — |
| 8 | Selftest 186 checks; mutants 53/53 killed | CONFIRMED (count); PARTLY (kind) | My runs: 186 passed; 53 of 53 KILLED. One, "outcome paths not checked", is KILLED(CRASH FileExistsError), not by its own check (D2) | LOW |
| 9 | No write to the inputs | CONFIRMED | sha256 of the three S0 DBs before and after my dry-run identical and equal to the registration's pins; no -wal/-journal | — |
| 10 | Price | CONFIRMED (order) | One qwen3@4096 CLINC fit 19.0 s here (builder 15.6 s); 150 fits ~280 s + bootstraps; within the registered 1-2 h | — |

## The FileExistsError mutant (brief item)

"outcome paths not checked" removes the pre-read refusal of an existing output. ST-REFUSE's "existing selection.json" case then
does not refuse: `main_run` reads the pins, fits phase A, and dies at `open(..., "xb")` in `write_selection`. `_cap` catches only
`SystemExit`, so the FileExistsError escapes the selftest and the harness counts any exception as KILLED. The check written for
it (`"exists" in err and "pin " not in o`) is never evaluated. Consequence at this blob: none for the record (mode "x" on every
output still protects; for an existing selection.json the crash precedes any EVAL read). For an existing outcome.txt without a
selection.json the mutant would read EVAL and crash at the outcome write, leaving a fresh selection.json and no record: waste,
not leakage. Non-decisive; the docstring's "every refusal mutant by its own check" is false for this one.

## EB1-EB9

| EB | Reading | Ruling |
|---|---|---|
| EB1 | d* = smallest d with GATE score >= max - 0.001 | CONFIRMED (the registered "ties within 0.001 go to the smaller d"; boundary inclusive, tested) |
| EB2 | GATE = kept in-scope rows on the TRAIN centroids that file EVAL | CONFIRMED (same denominator rule as EVAL; OOS excluded) |
| EB3 | DS1/DS2 stream = S0's C1 fine stream | CONFIRMED (makes (256,256) equal S0's interval) |
| EB4 | DS3 percentile CI, stream BOOT_SEED+4, BASIC beside | CONFIRMED (SLOTSWAP M3's convention; DS3 descriptive) |
| EB5 | DS4 TRAIN-component bootstrap, zero-weight labels dropped (counted) | PARTLY: the registration says "item-bootstrap"; components ~ items here (Kish ~1.01) and the component version is the CK-CLOSE convention. Registrar brackets the word (C4); descriptive only |
| EB6 | P6 reads gemma at d_g* | CONFIRMED as a reading (P6 is silent on gemma's slice); registrar records it |
| EB7 | dry-run identity reads S0's 256 EVAL only | ADMISSIBLE (claim 3) |
| EB8 | literally every outcome line carries the confounds | CONFIRMED |
| EB9 | coarse NMI at K_c, seeds 0-4, EVAL | CONFIRMED (printed, never deciding) |

## Defects

- **D1 (MEDIUM, test gap on a deciding path).** RV-A and RV-D survive: no assertion that DS1's bar uses the d* arms' spreads or
  that status uses the BASIC interval away from (256,256). Fix (post-merge or in the post-run review): in ST-E2E, assert for each
  corpus that the printed bar equals max(printed MDE80, printed spreads) and the printed spreads equal the oracle's EVAL seed
  spreads at (d_q*, d_g*); add a fixture corpus whose status differs between BASIC and percentile. Not blocking: the code is
  correct at blob 068550b4 and every input is printed (C2 makes the post-run check binding).
- **D2 (LOW).** `run_mutants` counts any exception as a kill; `_cap` catches only SystemExit. Fix: in `_cap` catch
  `Exception` too and return it as `err` (then the ST-REFUSE check `"pin " not in o` kills the mutant on its own), or record
  CRASH kills as SURVIVED.
- **D3 (LOW).** RV-B (the `sel_i < first_eval` refusal removed) survives: redundant with `eval_idx`, which refuses earlier, and
  with ST-E2E's order assertion. Non-decisive.
- **D4 (LOW).** RV-C (S0's c4() equality dropped from the identity) survives: the S digits are still checked. Non-decisive.
- **D5 (LOW).** `check_registered` is a presence check on a needle that occurs twice in the programme on main (the heading, and
  a quotation in INTENT-S0-CARD-PROTOCOL's provenance): it would pass with only the quotation. Fix: match `^## Registered .*`
  + needle, count == 1. Moot on main today (the heading is there, L22579).
- **D6 (LOW, operator).** The heavy-process guard sees java only; an Ollama embedding run (CARD-PROTOCOL) is not detected.

## Conditions

- **C1 (registrar / operator).** Run only on main after the merge (`--run` refuses elsewhere); the outcome of record is
  `experiment_results/embed_dim_slice/outcome.txt` from script blob 068550b4 (or a later blob only with a delta READY). No Ollama
  embedding run in the window (D6). An identity refusal is a failed precondition: it leaves selection.json; any re-run in a
  fresh `--out-dir` is recorded as such, with the reason.
- **C2 (post-run reviewer).** Recompute from `nmi_matrix.csv` the spreads at (d_q*, d_g*), the bar against the printed MDE80, and
  each status from the printed BASIC CI (closes D1 for the outcome); confirm `selection.json`'s sha equals the ORDER line's.
- **C3 (registrar).** Record EB7 as admissible: the dry-run's EVAL reads are S0's 256 arms, values of record, before any
  selection exists.
- **C4 (registrar).** Bracket EB5 ("item-bootstrap" read as the TRAIN-component bootstrap) and EB6 pre-data.

Orchestrator ruling relayed for the registrar (not this script): in INTENT-TRANSFER-S1, a LOSS that fires jointly with
EQUIVALENT blocks the parity sentence (closes the registrar's note N1).

## Commands

```
git ls-tree embed-dim-slice tools/analysis/embed_dim_slice.py      # blob 068550b4
grep -c $'\r' <worktree>/tools/analysis/embed_dim_slice.py          # 0 (LF on disk)
python tools/analysis/embed_dim_slice.py --selftest                 # 186 checks passed (4m46s)
python tools/analysis/embed_dim_slice.py --mutants                  # 53 of 53 KILLED; 1 by CRASH FileExistsError
TAXOARENA_DATA_ROOT=<main> python tools/analysis/embed_dim_slice.py --dry-run   # pins OK; identity REPRODUCED; 8 EVAL reads @256
sha256sum intent_transfer_corpora_v1.db intent_emb_qwen3.db intent_emb_gemma.db   # before = after = registration pins
python scratchpad/eds_rev/indep.py      # independent identity: D +0.03340/-0.00691/+0.05628; S 0.759777/0.826195; seed spreads
python scratchpad/eds_rev/own_mut.py    # E.MUTANTS replaced by RV-A..RV-G, builder's harness: 3 of 7 KILLED
git merge-tree --write-tree main embed-dim-slice                   # clean; 1 file changed
git show main:docs/judge_v2_program.md | grep -n '^## Registered.*EMBED-DIM-SLICE:'   # L22579
```

Own mutants (decisive = on the DS1 decision path): RV-A bar from the 256 arms' spreads — SURVIVED, decisive; RV-B order guard
removed — SURVIVED, non-decisive; RV-C c4 equality dropped — SURVIVED, non-decisive; RV-D status on the percentile CI —
SURVIVED, decisive; RV-E outcome untagged at the call site — KILLED; RV-F caveat keyed on CLINC — KILLED; RV-G spreads zeroed —
KILLED, decisive.
