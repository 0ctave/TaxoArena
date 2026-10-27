# POSTRUN EMBED-QUANT (adversarial-reviewer, 2026-10-01; zero calls)

Reviewed: run commit eec43e8d (`experiment_results/embed_quant/{outcome.txt, nmi_q.csv, cos_q.csv, readout_run.txt, readout_dryrun2.txt}`)
against the registration (prog L22738-L22760, _as_of 28b4032b) and its brackets (L22819-L22831); READY_embed_quant.md (9ad94e12) C-EQ-5.

## Verdict

**VALID.** EQ1 **NOT-A-CONFOUND** stands, decided by the two SCOREABLE corpora: MASSIVE and Banking77 both EQUIVALENT
(2 of 2 scoreable; the 2-of-3 rule is met without CLINC). F-EQ not fired. EQ2 (descriptive) reproduced to 6 dp.
Wording conditions W-EQ-1..W-EQ-4 below bind every record, ledger chip and synthesis that quotes this result.

## Data object

- Corpora `intent_transfer_corpora_v1.db` sha256 487e0093719c184c; Q4 `intent_emb_qwen3.db` 9e100e04fc91b137; Q8 `intent_emb_qwen3_q8.db`
  771666bc8563d972. All three re-hashed before and after my readout: unchanged (opened `mode=ro&immutable=1`).
- Text set 57,350 (sha256 0ba7eb3c805127d5), both arms 57,350 of 57,350 vectors. Slice = first 1024 of 4096 (big-endian f4), L2-renormalised.
- Deciding rows: kept, in-scope (non-OOS) EVAL fine rows: MASSIVE 4,946 / CLINC 6,672 / Banking77 3,908; fits on kept in-scope TRAIN rows
  only (my own row selection, independent of `fit_rows`). No GATE row, no pool of record.
- Script pins: embed_quant.py `blob:3930cf4bc5e77bebd38309c74cf4ecf8eeba74d0` (LF, = HEAD tree = outcome line; CRLF rendering
  `8fa995b9d6729ac0`), embed_quant_writer.py `blob:1b2abdc8617f84f3cfd00c9778e3bbb94ae63d6f` (LF; CRLF `cf79cb53312cf1de`).
  Working tree clean for these paths and `experiment_results/embed_quant/` (`git status --porcelain ... | wc -l` = 0).

## Per-claim table (deciding claims; my numbers from an independent script, see Commands)

| claim | claimed | mine | status | sev |
|---|---|---|---|---|
| per-seed NMI (120 fits) | nmi_q.csv | own TRAIN fits (ITS.skmeans only) + sklearn NMI: max abs diff 4.98e-07 (csv is 6 dp) | CONFIRMED | — |
| D_q MASSIVE / CLINC / B77 | +0.00030 / +0.00090 / +0.00091 | +0.00030 / +0.00090 / +0.00091 (Q8 0.76602/0.92873/0.84643, Q4 0.76571/0.92783/0.84552) | CONFIRMED to 5 dp | — |
| delta_c (Q4 seeds 0-4 max-min) | 0.01428 / 0.00417 / 0.01043 | 0.01428 / 0.00417 / 0.01043 | CONFIRMED | — |
| seed term sqrt(var_seed/20) | 0.00205 / 0.00151 / 0.00170 | 0.00205 / 0.00151 / 0.00170 | CONFIRMED | — |
| SE_boot (registered stream, B 2000) | 0.00093 / 0.00041 / 0.00076 | 0.00093 / 0.00041 / 0.00076; own stream 0.00091 / 0.00043 / 0.00079 | CONFIRMED (stream-robust) | — |
| SE_total | 0.00226 / 0.00157 / 0.00186 | 0.00226 / 0.00157 / 0.00186 (own stream 0.00225 / 0.00157 / 0.00187) | CONFIRMED | — |
| 90% TOST intervals | [-0.00340,+0.00401] / [-0.00168,+0.00348] / [-0.00215,+0.00397] | identical | CONFIRMED | — |
| all inside +/-delta_c -> EQUIVALENT x3 | EQUIVALENT 3/3 | EQUIVALENT 3/3 | CONFIRMED | — |
| verdict NOT-A-CONFOUND | 3 of 3 | 2 of 2 SCOREABLE corpora suffice; CLINC is DESCRIPTIVE-ONLY (W-EQ-2) | CONFIRMED, wording PARTLY | MEDIUM |
| Kish DEFF / n_eff (C-EQ-5) | 1.0093 / 1.0000 / 1.0015; 4900 / 6672 / 3902 | re-measured from EVAL stem_key components: 1.0093 (4,923 comps) / 1.0000 (6,672) / 1.0015 (3,905); n_eff 4900 / 6672 / 3902 | CONFIRMED | — |
| TOST MDE80 (2.487 x SE_total) vs bar | 0.00561 / 0.00390 / 0.00463 | 0.00561 / 0.00390 / 0.00463; observed margin delta_c - |D_q| 0.01398 / 0.00327 / 0.00952 | CONFIRMED | — |
| SCOREABLE at predicted |D| 0.003 | S / DESCRIPTIVE-ONLY / S | 0.01128>=0.00561 S; 0.00117<0.00390 D-O; 0.00743>=0.00463 S (in-run SE beat the planning SE 0.00348/0.00148/0.00285) | CONFIRMED | — |
| BASIC 95% (descriptive) | [-0.00166,+0.00201] / [+0.00009,+0.00168] / [-0.00037,+0.00262] | identical; own stream [-0.00163,+0.00191] / [+0.00000,+0.00173] / [-0.00040,+0.00268] | CONFIRMED; CLINC's exclusion of 0 is stream-marginal | LOW |
| EQ2 median / min, all | 0.992032 / 0.873615 (57,350) | 0.992032 / 0.873615 | CONFIRMED | — |
| EQ2 per corpus | 0.992396/0.930274; 0.992212/0.873615; 0.991429/0.934049 (16,425 / 23,841 / 13,083) | identical | CONFIRMED | — |
| pins unchanged before/after | 3 pins | unchanged across my own read too | CONFIRMED | — |

Sensitivity (deciding path): the SE_boot that would break EQUIVALENT is 0.00824 (MASSIVE), 0.00129 (CLINC), 0.00553 (Banking77),
against measured 0.00093 / 0.00041 / 0.00076. With the registration's conservative TRANSPORTED SE_boot (0.00289 / 0.00137 / 0.00247)
MASSIVE and Banking77 stay EQUIVALENT (90% [-0.00553,+0.00614], [-0.00402,+0.00584]) but **CLINC would read NEITHER** (upper +0.00426 >
0.00417). The verdict does not depend on CLINC; CLINC's EQUIVALENT does depend on the measured (small) SE_boot.

## Defects / conditions

- **W-EQ-1 (MEDIUM, wording; scope of "discharged").** outcome.txt CONSEQUENCE says the quantisation half of W2 "is discharged for qwen3
  at d_q* 1024 only". What was shown is the Q4_K_M -> Q8_0 step. The W2 confound is "qwen3 Q4_K_M vs gemma BF16"; Q8_0 is itself
  quantised and BF16/F16 qwen3 was never measured. Fix (record/ledger/synthesis): "Q4_K_M vs Q8_0: EQUIVALENT within the seed spread at
  d 1024 on MASSIVE and Banking77 (TOST; CLINC descriptive); qwen3 precision above Q8_0 untested". The UNCONTROLLED tag on the DS1 rows
  becomes "quantisation: Q4_K_M ~ Q8_0 (EMBED-QUANT); above Q8_0 untested; prompts RAW", not deleted.
- **W-EQ-2 (MEDIUM, CLINC).** CLINC was registered DESCRIPTIVE-ONLY (Support (f)) and the run's own Support line prints DESCRIPTIVE-ONLY,
  yet the EQ1 line prints `-> EQUIVALENT` and the verdict line counts it ("EQUIVALENT on 3 of 3"). The rule (>=2 of 3) is met either way,
  so this is wording, not a change of verdict. Fix: quote as "NOT-A-CONFOUND (EQUIVALENT on MASSIVE and Banking77, the two SCOREABLE
  corpora; CLINC EQUIVALENT DESCRIPTIVE-ONLY)"; never "3 of 3" without the CLINC qualifier. The commit subject eec43e8d
  ("EQUIVALENT 3/3") is not rewritten; the registrar's outcome record carries the qualifier.
- **W-EQ-3 (LOW, CLINC bootstrap).** CLINC's BASIC 95% [+0.00009, +0.00168] excludes 0 (own stream [+0.00000, +0.00173]: marginal). It is
  the item bootstrap with the 20 partitions held fixed (no seed term); the registered interval with the seed term includes 0. Report as
  "a small Q8-higher item-level shift on CLINC (+0.0009, 0.2x delta_c), conditional on the fitted partitions; not a seed-robust difference",
  never as DIFFERENT and never as evidence of a confound.
- **W-EQ-4 (MEDIUM, wording; what it does not show).** Quantisation is **not shown to explain gemma's edge** on these corpora: the Q4->Q8
  90% upper bound (+0.00401 MASSIVE, +0.00397 Banking77) is about a tenth of gemma's DS1 edge (+0.03329, +0.04386; embed_dim_slice
  outcome.txt L22/L24). This does not make the edge a property of the models: **prompts stay uncontrolled** (RAW on both sides until
  CARD-PROTOCOL CP1) and precision above Q8_0 is untested (W-EQ-1). **The embedder of record (qwen3) is unchanged by this test alone**;
  D3 and its revisit conditions are the author's. Never write "gemma is the better embedder" from this result.
- D1 (MEDIUM, READY_embed_quant): three writer guards not selftested stays OWED; it had no effect on this run (pins unchanged, my check).

No BLOCKER. Leakage: none found (my fits use TRAIN in-scope rows only and reproduce every per-seed NMI; EVAL rows are filed, never fit).
Own mutants: none run (post-run numbers review; every deciding number recomputed independently instead; the READY's mutant suite covers
the code, which is unchanged since 31b3c69c: blobs match).

## Commands

```
# independent recompute (scratchpad eqrev/rev_eq.py; imports only ITS.skmeans for the fit and ITS.text_set for the 57,350-text list)
#   sqlite3 file:...?mode=ro&immutable=1; rows from items; slice >f4[:1024], L2 unit; TRAIN = kept & side TRAIN & !is_oos; EVAL likewise
#   20 seeds x 2 arms x 3 corpora; sklearn normalized_mutual_info_score; own weighted NMI for the component bootstrap
#   streams: registered default_rng(20260929 + 10*ci + fine_idx) and own default_rng(777+ci); B 2000; Kish = sum m^2 / sum m over EVAL stem_key
OMP_NUM_THREADS=4 python <scratchpad>/eqrev/rev_eq.py      # -> lines quoted in the table; "max |NMI - nmi_q.csv| 4.98e-07"; "sha after unchanged True"
python - <<EOF ... nmi_q.csv only: D, delta, seed term, SE_total under claimed vs transported SE_boot, SE_boot to break  # sensitivity paragraph
git rev-parse HEAD:tools/analysis/embed_quant.py; git hash-object [--no-filters] tools/analysis/embed_quant{,_writer}.py   # LF / CRLF pins
git status --porcelain tools/analysis/embed_quant*.py experiment_results/embed_quant/ | wc -l   # 0
sed -n 22,24p experiment_results/embed_dim_slice/outcome.txt   # gemma DS1 D* +0.03329 / -0.00244 / +0.04386
```
