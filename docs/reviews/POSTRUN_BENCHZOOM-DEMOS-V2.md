# POSTRUN review: benchzoom "v2 demos" (hand-back of de36610) — 2026-10-10

Reviewed: benchzoom `master` de36610 (parent cd911f2), the hand-back "DEMOS: blocked on purpose", the demo outputs under
`E:/benchzoom_demo/{math,mmlu_pro}`, the scratch pilot `E:/TaxoArena_tmp/bz_c2_pilot/`. Authority: D-2026-10-10-1
(`docs/agents/author_decisions/2026-10-09.md`). Prior reviews cited, not re-derived: POSTRUN_BENCHZOOM-ZOOM-DEMOS.md
(64106064; v1 numbers recomputed from atlas + raw parquet there, F1-F11) and POSTRUN_BENCHZOOM-CROSSFIT-DEPTH.md
(edf839a0; C1-C3). Zero LLM calls, no Ollama, nothing written in benchzoom or E:/benchzoom_*.

## Verdict

- **DEMOS: NOT BLOG-READY. No v2 demo exists.** No file under `E:/benchzoom_demo/{math,mmlu_pro}` is newer than
  `mmlu_run.log` (05:23), and both predate the v1 review commit 64106064 (05:35). So the object on disk is the v1 demo
  set, unchanged. F1-F11 of 64106064 are all still open. That includes **F5: QwQ-32B is still in the MMLU-Pro demo, not
  excluded and not disclosed** (`sunburst_Qwen_QwQ-32B.png` exists; 25 QwQ mentions in summary.json, 47 in profiles.csv).
  There is nothing v2 to recompute. The v1 summary numbers were recomputed to the digit in 64106064 and their files have
  not changed since.
- **"blocked on purpose": CORRECT under D-2026-10-10-1.** No cross-fit rule has a RELIABLE verdict without HIGH
  conditions, so the crossfit-vs-strict labelling question does not yet arise. The v1 demos carry the strict read only:
  0 "crossfit" mentions in mmlu_pro/summary.json, and LABEL.txt says "illustrative demo, not a registered result".
- **de36610 (C2 fix, opt-in): MERGEABLE as a library change, NOT CALIBRATED.** Default path inert: confirmed
  bit-identical on my own fixtures. Tests, lint and the decisive mutants: confirmed. The pilot numbers reproduce to the
  digit from the run files. Two prose sentences overstate (D2, D3).

## Per-claim table (deciding claims)

| claim | mine | status | sev |
|---|---|---|---|
| v2 demos produced / QwQ excluded + disclosed | no v2 outputs; QwQ present in v1 MMLU-Pro (F5 open) | REFUTED (as a deliverable; the builder says so itself) | BLOCKER for blog |
| default path unchanged (golden c8a9e551.., 124e4439..) | own fixtures (planted depth 3, 200/leaf, 10 models, seeds 0 and 7; crossfit fold seed 2), UNROUNDED sha of d,dc,se,raw,h,D,tau,eta,tau,theta: cd911f2 `git archive` = de36610: cf43383992aa2f38, 7845864c478a381f | CONFIRMED | - |
| centred scores sum to 0 per node (new code executed) | g' = g - h·Σg/Σh has Σ=0 by construction; test_sums_zero passes; mutant M1 kills it | CONFIRMED | - |
| pytest 214 passed / 4 deselected; ruff, mypy clean | 214 passed, 4 deselected (84.0 s); ruff "All checks passed"; mypy 13 files OK (.venv) | CONFIRMED | - |
| 8/8 mutants killed | re-ran decisive M1 (no-op centring) 3 failed, M2 (noise 1/h) 2 failed; own R1 (noise 1/h-2/H) 1 failed, R2 (g[u] left uncentred: d/dc use raw g) 1 failed | CONFIRMED (sampled) | - |
| pilot hardnull 39→0/1104, ceilnull 14→0/1104 | an.py on runs/: cf2 39/1104, cc2 0/1104; cf2 14/1104, cc2 0/1104; depth-2 gate open, uncentred 4/8 and 2/8, centred 0/8 | CONFIRMED | - |
| no-subject null 32→21/1104; gate open 7/8; 21/184 models | 32/1104 → 21/1104; gate unc 8/8, cen 7/8; anym 21/184 | CONFIRMED | - |
| detection dense E0.5 mmlu 115→113/288, math 200→192/432; registered 42, 29 | same to the digit | CONFIRMED | - |
| ability-slope centring "changed nothing" | an_slope.py: nosubj 22/1104 (vs 21), math det 194/432, mmlu det 115/288 | CONFIRMED (approx.) | - |
| LF blobs profile 7ea41a03, crossfit b66e551d, atlas b230b17a, test 1bc582ea | `git hash-object` on the working tree = `git rev-parse de36610:<path>`; status empty, so no CRLF rendering differs | CONFIRMED | - |
| no data / GPQA text committed | `git ls-files` with parquet/db/npz/jsonl/gpqa in the name: 0; d872d24..de36610 diff lines containing "gpqa": 0 | CONFIRMED | - |

## Defects (ranked)

- **D1 BLOCKER (blog).** No v2 demo exists and the v1 demos still carry F1-F11, including F5 (QwQ in). Fix: once the
  depth rule is decided (author option a/b/c), rerun both demos. Then fix F1-F11: exclude QwQ-32B from the MMLU-Pro fit,
  or at least from the sunburst picks and the panel, and print the reason in LABEL.txt and the README. Label every figure
  "strict registered read" or "cross-fitted depth (k SE, calibration ref)".
- **D2 MEDIUM (unsupported).** defaults.md and the hand-back state the cause of the residual C2 leak as fact: the MoM
  floor 1/h "ignores that the parent offset was fitted on the same items ... and the extra noise of the LOMO
  difficulties". No run isolates either mechanism. The only experiment shown (slope centring) changes nothing, which
  rules out a third cause, not these two. Fix: write "hypothesised" and name the test, e.g. a pilot with an oracle
  difficulty b, or with offsets fitted on disjoint item halves.
- **D3 LOW (overstated).** "at no visible cost in detection": centred detection falls 200→192/432 (math) and
  115→113/288 (mmlu), and centred false zoom in the dense cells RISES 7→9/1224 and 9→12/816. defaults.md's table shows
  this; the hand-back table omits the dense false-zoom row. With 8 seeds none of it is resolved. Fix: "no cost
  resolvable at 8 seeds; dense-cell false zoom 7→9, 9→12".
- **D4 LOW.** `fit_offsets(centre_models=True)` centres over ALL models, but tau's moment estimate uses only the models
  with h ≥ h_min (`use`), with 1/H_u taken over all models. This is consistent only when every model passes h_min (true
  at the demo sizes). Fix: one sentence in the docstring, or centre over `use` models.
- **D5 LOW.** "about an hour of compute" for option (a) is an estimate with no basis shown. "--analyze now refuses" was
  not re-run here: depth_calibration.py L67-68 documents the sha-pin refusal, but the refusal itself was not exercised.

## Author decision (unchanged from the hand-back)

Choose (a) a registered recalibration of centred 2 SE, with V1 counted over open-gate fits plus a per-model any-zoom
rate, fixed before any run; (b) strict only, rerunning the demos with F1-F11 fixed; or (c) uncentred 2 SE with C1-C3
disclosed. Nothing in this review is a reason to prefer (c): the residual 1.90% false zoom in the no-subject null comes
from 8 seeds and is not a calibration.

## Commands

```
find E:/benchzoom_demo/{math,mmlu_pro} -type f -newer E:/benchzoom_demo/mmlu_run.log | wc -l     # 0
git -C TaxoArena log -1 --format=%ci 64106064                                                  # 05:35:12, after the demo mtimes
grep -c QwQ E:/benchzoom_demo/mmlu_pro/summary.json profiles.csv                                 # 25, 47
.venv/Scripts/python -m pytest -q ; ruff check . ; mypy src                                      # 214 passed/4 desel; clean; clean
git archive cd911f2 src | tar -x -C scratch/old ; python scratch/inert.py <old|new src>          # cf43383992aa2f38 / 7845864c478a381f both
scratch mutants on a git-archive copy, PYTHONPATH=copy/src pytest tests/test_centre_models.py    # M1 3F, M2 2F, R1 1F, R2 1F
cd E:/TaxoArena_tmp/bz_c2_pilot && python an.py ; python an_slope.py                            # pilot table above
git ls-files | grep -ciE '\.(parquet|db|npz|jsonl)$|gpqa' ; git diff d872d24 de36610 | grep -ci gpqa   # 0 ; 0
```
