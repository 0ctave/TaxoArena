# POSTRUN HARNESS-EXTRACTOR run2 (adversarial reviewer, 2026-10-10; zero judge calls)

Reviewed: the `--run` of `tools/analysis/harness_extractor.py` blob:4107eb0b9ed20e48ab5ee9cdca818db3405de33d. That is the LF
blob of record: `git hash-object` on HEAD 64106064 gives the same value, and the identity line shows sha256-lf16 05ab8b87bbb49869.
The blob was merged in a80fa610 and declared READY in delta4 eba84716.
Outcome: `experiment_results/hf_blog/harness_extractor/harness_extractor_outcome.txt`, sha256-lf16 fd31a8e4ede9ee60 (recomputed).
It is not tracked: `git ls-files experiment_results/hf_blog/harness_extractor | wc -l` = 0.
The E: backup holds the identical outcome (`diff` gives no output). Its SHA256SUMS check is 6/6 OK.
Registration: prog L25229-L25315, with the brackets HX-R1/R2/R4 (L25363-L25372), S-1 and F-H-SUPPORT (L25412-L25418), and D-2026-10-08-5.
The previous POSTRUN (8012b48a, INVALID) crashed because it read `f.is_correct_mathfix`. This blob SELECTs `f.is_correct`
(RUN_SQL["mf"], L312). The 12 remaining occurrences of `is_correct_mathfix` are all docstrings, the
schema-drift fixture, negative tests or mutant strings (`grep -n`, every line read).

## VERDICT: VALID (outcome of record for HX1-HX5 and P1-P8, as printed). No conditions block it.

The outcome stands on the instrument as reviewed. Every deciding number reproduces to the 4th digit from my own script, which
reads the DBs read-only (immutable=1), uses scipy kendalltau(variant b) and rankdata, and shares no code with the instrument.

## Per-claim table (deciding paths)

| Claim | Instrument | Mine | Status | Sev |
|---|---|---|---|---|
| R1 twins on pool paeec37 EVAL (6,482 ids) | 471 / 427 | 471 / 427 | CONFIRMED | - |
| MATH kept after collapse / IFEval kept | 1309 of 1324 / 541 | 1309 of 1324 / 541 | CONFIRMED | - |
| Roster: 18 models, same set on MATH and IFEval; scored rows | 18; 23,562 / 9,738 | 18, True; 23,562 rows, 0 missing any of X0/MF/H | CONFIRMED | - |
| HX1 X0-MF tau-b / max shift | -0.0473 / 15.0 | -0.0473 / 15.0 | CONFIRMED | - |
| HX1 X0-H | 0.0338 / 15.0 | 0.0338 / 15.0 | CONFIRMED | - |
| HX1 MF-H | 0.9216 / 3.0 | 0.9216 / 3.0 | CONFIRMED | - |
| HX1 word: min tau-b < 0.85, so RANKS-MOVE; rule 8 not refuted; F-HX NOT FIRED | as printed | follows from the points above | CONFIRMED | - |
| HX1 min tau-b bootstrap 95% / SD | [-0.0950, 0.0068] / 0.0248 | iid, own seed 777, B 500: [-0.0879, 0.0068] / 0.0255 | CONFIRMED (spot check) | - |
| HX2 {MF,H}: 0.9216 / 3.0, so RANKS-MOVE (descriptive-only by support) | as printed | 0.9216 / 3.0 | CONFIRMED | - |
| HX3 I0-IS / I0-IL / IS-IL | 1.0000/0.0; 0.9739/2.0; 0.9739/2.0, so RANKS-HOLD (descriptive-only) | identical; rows with I0 != IS: 0 (join doc_id = upstream_id) | CONFIRMED | - |
| HX4: models whose 95% CI clears 0.02, so SHIFT-MATERIAL | 2 (R1-Llama-8B [.0802,.1146], R1-Qwen-32B [.0581,.0879]) | 2 (own iid bootstrap, seed 777: [.0817,.1131], [.0596,.0879]); the next model, Qwen2.5-32B at +0.0191, cannot clear 0.02 | CONFIRMED | - |
| HX4 max abs(MF-H); per-model accuracies X0/MF/H (18 x 3) | 0.0970; table | 0.0970; all 54 values equal to 4 dp | CONFIRMED | - |
| HX5 denominator: X0=0, MF=1 rows after R1 / questions | 5088 / 1022 | 5088 / 1022 (5181 before R1 = the pilot's count); X0=1, MF=0: 0; X0=1, H=0: 0 | CONFIRMED | - |
| HX5 format share 0.9013, so FORMAT-DOMINATED | 0.9013 | coarse superset: 0.9369 of the 5181 rows carry `\boxed` or "final answer is"; that leaves 327 unmarked rows against 502 non-format rows. Consistent; margin 0.40 against the bar. I did not re-implement the 7-rule classifier | PARTLY (spot check, non-deciding) | LOW |
| P8 max abs(IS-IL) | 0.0924 | 0.0924 | CONFIRMED | - |
| Components (CK-CLOSE stem_key), Kish MATH / IFEval | 1309 / 541, 1.0000 | 1309 / 541, 1.0000 | CONFIRMED | - |
| DB of record untouched | before = after ad66e30a... | my sha256sum before and after my own reads: ad66e30a...6770577, equal | CONFIRMED | - |
| H table pin | 6b010fa6...eb1d1 | sha256sum gives the same | CONFIRMED | - |
| Zero judge calls | 0 | the instrument has 0 network imports or URLs (`grep -cE`); run.log has rc 0, 0 Traceback, 0 REFUSE | CONFIRMED | - |

## Support (check 8), re-measured after the run
- HX1: DEFF from cluster sizes = 1.0000 (Kish; every component is a singleton), so n_eff = 1309. The bootstrap SD of record is 0.0248,
  so MDE80 = 2.8 x 0.0248 = 0.0694. The point is 0.8973 below the bar: SCOREABLE. The rank-shift clause (15 against 2) is a count
  and decides independently.
- HX4: SD 0.0085, MDE80 0.0239; margin 0.0770: SCOREABLE.
- HX5: measured DEFF 1.93 against the declared pilot assumption 3.0; MDE80 0.0163, margin 0.40: SCOREABLE.
- HX2: the realised SD is 0.0197, against the registered 0.0420. That would make it scoreable at the realised SE (MDE80 0.0553 < margin 0.0716),
  but the registered word is DESCRIPTIVE-ONLY BY SUPPORT, and the instrument keeps that qualifier, so there is no C-7 substitution. The registrar
  must not upgrade HX2 after the fact (D2).
- Check 3 (wrong(established)) does not apply: no judge verdict enters.

## Defects
- D1 (LOW, carried over from delta4): the "before" DB sha is taken after the schema check. Equal before and after, and my own
  sha256 is equal too, so it has no effect here. Fix: hash before `schema_check`.
- D2 (LOW, registrar): the realised Support shows HX2 and HX3 "SCOREABLE at the realised SE", while the registered words stay
  DESCRIPTIVE-ONLY. Record the outcome with the registered qualifier, and quote the realised SD only as a plan-vs-realised note
  (the transported SE(tau) overstated the noise about 2x).
- D3 (LOW, registrar): P5 is FAILED (0.9739 is above the band ceiling of 0.97). Record it as FAILED. It is not a defect of the instrument.

## Commands (all read-only; scratch scripts not committed)
```
git hash-object tools/analysis/harness_extractor.py            # 4107eb0b...
sha256sum multicorpus_cache_v1.db experiment_results/math_scorer_h/math_h_table.csv   # before AND after: ad66e30a.., 6b010fa6..
powershell -File E:/TaxoArena_tmp/busy.ps1 ; echo $?           # 1 (free) before my reads
python <scratch>/hx_recompute.py   # R1 (pool JSON, byte-equal text, min-id collapse) -> X0/MF/H accuracies, scipy tau-b,
                                   # rankdata midrank shifts, HX4 iid bootstrap seed 777, IFEval IS/IL from the 18 sample jsonl
python <scratch>/hx5.py            # SQL count of X0=0,MF=1 rows (5181) and \boxed / "final answer is" markers (4854)
python -c "...split_side.stem_key over kept texts..."          # components 1309 / 541, Kish 1.0000
grep -n 'is_correct_mathfix' tools/analysis/harness_extractor.py   # 12 lines, all docstrings / fixture / negative tests / mutants
sed 's/\r$//' <outcome> | sha256sum                            # fd31a8e4ede9ee60
(cd E:/TaxoArena_backup_20261009_harness_extractor_run && sha256sum -c SHA256SUMS)   # 6/6 OK
```
Selftest (10/10) and mutants (117/117) were not re-run: the run used the blob that READY delta4 (eba84716) reviewed, unchanged.
