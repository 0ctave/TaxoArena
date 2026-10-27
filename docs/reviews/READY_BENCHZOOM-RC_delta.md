# Delta READY review: benchzoom bd09816..6afd89a (fixes to READY_BENCHZOOM-RC a6bf9bb2) + HF post draft, 2026-10-09

Reviewer: adversarial-reviewer. Zero LLM calls. benchzoom read-only (working tree 0 dirty lines before and after,
`git status --short | wc -l`; no remote, `git remote -v | wc -l` = 0; no data files: `git diff --name-only bd09816..HEAD
| grep -c -iE "data|\.json|\.csv|\.db|\.npz"` = 0). Runs in the scratch clone E:/TaxoArena_tmp/bz_review/clone checked
out at 6afd89a, non-editable reinstall. Scope: the delta (044f246 peer commit spot-checked through its tests and the
lm-eval metric path; 6afd89a in full) and the post draft docs/drafts/hf/benchmark-zoom/article.md (384 lines, read whole).
Code the delta does not touch: as CONFIRMED in READY_BENCHZOOM-RC (a6bf9bb2), not re-derived.
Pins at 6afd89a (LF blob = `git rev-parse 6afd89a:<path>` = `git hash-object` of the CRLF working tree, autocrlf true):
NOTICE.md 9dea40437ca7, README.md ce480ef0f536, docs/defaults.md d4b7f1adb9ea, pyproject.toml 98034f379bb2, irt.py 0964c8c4cd9e,
profile.py 147bf8d2846a, gates.py 69eec78561be, atlas.py 46c138bf4104, export.py 5cc59ff73e03, sources.py a0109e2ca2da,
examples/gate_calibration.py a8aa49a9b818, tests/test_review_fixes.py 1468b43f5f15.

## Verdict
**Library: RELEASE-CANDIDATE once R-1 has been applied.** R-1 is a wording change in 3 places; a grep re-check is enough.
Every original finding (H-1, H-2, M-1 to M-5, L-1 to L-6) is CLOSED or CLOSED-DISCLOSED. 127 tests pass, ruff and mypy
are clean, and 26 of the 27 original mutants are now killed (I5 is equivalent).
**Post draft: NOT publishable.** The headline (ADAPTIVE-PROFILE) has not run. Independently of that, 3 HIGH
overstatements (A-1 to A-3) and 5 MEDIUM ones (A-4 to A-8) must be rewritten before the text goes to the author.

## Per-claim table (original findings, deciding claims of the fix)
| # | claim (fix hand-back) | my result | status | sev |
|---|---|---|---|---|
| H-1 | NOTICE states the registered default | NOTICE "none for the certification statistic: the default is ... z = d / SE(d) (`certify="registered"`)"; `AtlasConfig().certify` unchanged | CONFIRMED | - |
| H-2 | split-dip VALID with the S-1 qualifier; gate off for the right reason | README/defaults.md/atlas/gates: wording equals prog L25333 "SD1 WORD OF RECORD"; 0/300, 0/70, D2 0/30, D4 3/30 per size, DEFF 6.0 match prog L25334-L25338; "not a certificate of tree sites" = L25339 | CONFIRMED | - |
| M-1 | I3 killed | my I3 rerun: KILLED (`test_lomo_theta_uses_its_own_leave_one_out_column`) | CONFIRMED | - |
| M-2 | no "primary metric"; multi-metric task refused until `metric=` | `grep -n primary` gives only "defines no primary metric" (sources L10/L385/L415/L539, README L67); `_official_lm` refuses len(ml) > 1 with no declaration, refuses a declaration outside ml and one on `leaderboard_*` | CONFIRMED on fixtures; real lm-eval logs not executed (lm_eval not installed) | LOW (R-4) |
| M-3 | third-party notice; GPQA refused by default | NOTICE §"Third-party benchmark data" present; `atlas_dict(include_text=None)` raises on id/task/subject containing "gpqa" (case-insensitive); False blanks text and drops options; my D3 and D4 mutants KILLED; D2 (case-sensitive) and D6 (id column only) SURVIVED | CONFIRMED (behaviour); test gap | LOW (R-2) |
| M-4 | predict_proba documented in-sample | docstring and README step 6 say "IN-SAMPLE ... not the registered held-out Brier"; `fit_rows=` not built (declared) | CONFIRMED | - |
| M-5 | calibration reproducible from seeds | `python examples/gate_calibration.py`: sep 0/30, 0/30, 1/20, 20/20, 20/20; dip 0/30, 0/30, 0/20, **19/20**, 20/20, which agrees with README and defaults.md to the digit | CONFIRMED; delta-2 seed base disclosed below | LOW (R-3) |
| L-1 | one-member family is strict at \|z\| > 1.96 | `single_member_z(0.05)` = 1.96; branch taken when exactly one child has a non-NaN p; D1 (z_{0.975} at every q) and D5 (len(pc)==1) KILLED | CONFIRMED | - |
| L-4 | non-convergence warns | RuntimeWarning that names the all-model fit and leave-out j (builder's mutants killed; test present) | CONFIRMED | - |
| L-5 | T1 and T2 killed | my T1 and T2 reruns: KILLED (`tests/test_review_fixes.py`) | CONFIRMED | - |
| L-6 | dip_version recorded; diptest pinned | stats carry `dip_version`; pyproject `diptest>=0.11,<0.12`; installed 0.11.0 | CONFIRMED | - |
| T | 127 passed, 4 deselected; ruff and mypy clean | 127 passed, 4 deselected in 43.2 s; ruff "All checks passed!" (src tests examples); mypy "no issues found in 12 source files" | CONFIRMED | - |
| R | README claims vs code/record | the tagline (README L3, pyproject `description`, `__init__` docstring) says "a nested capability map". This contradicts README L149 ("It is not a capability claim") and L174 ("not by the skill they need") | REFUTED (overclaim) | MEDIUM (R-1) |

## Own mutants on the delta (6; same runner as a6bf9bb2, full suite -x, PYTHONPATH shadow proved by `benchzoom.__file__`)
D1 single_member_z -> norm.isf(q/2) always: KILLED, decisive (L-1) · D2 gpqa match case=True: SURVIVED, not decisive ·
D3 include_text=False keeps options: KILLED · D4 items_text always True: KILLED · D5 one-member test `len(pc)==1`: KILLED,
decisive (L-1) · D6 GPQA scan on id only: SURVIVED, not decisive. Rerun of the 27 original mutants: 26 KILLED, I5 SURVIVED (equivalent).

## Defects, library (fix each)
- **R-1 (MEDIUM)** "a nested capability map" appears in README L3, pyproject `description` and the `__init__` docstring.
  Fix: replace it with "a nested topic map" or "a nested map of question topics" in all three places, then grep
  `-i capabilit` to confirm that only README L149 remains.
- **R-2 (LOW)** GPQA refusal: there is no test for an upper-case name or for a name present only in `task`/`subject`
  (D2 and D6 survive). Fix: add one fixture with `subject="GPQA Diamond"` and a neutral id. NOTICE should also say that
  detection is by id/task/subject name only: a `from_csv` table with neutral ids and no GPQA label is not caught.
- **R-3 (LOW)** delta 2 uses seed base 5, which the suite has no class for. It gives 19/20, the figure the old
  unreproducible text quoted. Over bases 1-10 the dip gate certifies 18, 20, 19, 20, 19, 19, 20, 20, 19, 19 (193/200).
  Fix: state in the script docstring why base 5 was chosen, or quote 193/200 over bases 1-10.
- **R-4 (LOW, carried from #14)** the lm-eval metric selection is verified on synthetic fixtures only. Fix: run it
  once on a real `--log_samples` output (arc_easy, hellaswag) before the release notes claim lm-eval support.

## Post draft: sentences that overstate or have no registered source
- **A-1 (HIGH) L37-38** "Inside 'Law' or 'Engineering' there are many kinds of question, and two models with the same
  category score can be strong in different places." **L60** "A category average can hide a strong sub-topic and a weak
  one that cancel." No registered source exists. The sub-anchor profile line is CLOSED (PROFILE-TREE-ROBUST,
  KEY-SUBANCHOR-SCALE; KNOWLEDGE §3). Fix: pose it as the question the post asks, not as a fact.
- **A-2 (HIGH) L224-225** "nothing we tested beat it by a margin we could detect". The post's own L191-193 refutes this:
  flat k-means beat the tree cut, CUT-WORSE 3/3, beyond the bar and MDE80. L204-206 refutes it too: a flat mixture beat
  the refined tree on all 3, with every upper bound < 0. Bisecting k-means was compared with the tree descriptively
  only. No registered test had "declared subjects, then BKM" (the library default) as an arm: HB used a k-means
  hierarchy of the tree's shape, and AP3 is DESCRIPTIVE-ONLY and has not run. Fix: "no test showed the engine's tree
  beating it; flat clusterings partition better but do not nest."
- **A-3 (HIGH) L161** table row "Same plants, old site test | 0 of 15 at n 486; 0 of 15 at n 441". The comparator is
  the RECORD plants (CERT-PLANTED, cpl_sites.csv; prog L25334), not the 60 fresh plants. Fix: label the row "record
  plants (CERT-PLANTED)" and add the descriptive split-dip count on those same record plants, 15/15 per size (prog L25338).
- **A-4 (MEDIUM) L41** "We built it over a year of pre-registered tests" and **L182** "spent most of a year on a taxonomy
  engine". No registered source exists for either duration. Fix: cite one or drop the time span.
- **A-5 (MEDIUM) L53** "Item difficulty has to come out first." and **L231-232** "The Rasch step separates the two".
  SATURATION-IRT shows that saturation differs between benchmarks. It does not show that difficulty adjustment improves
  a reading; that is what the unrun ADAPTIVE-PROFILE would test. Fix: present it as a design choice that the headline
  test will judge.
- **A-6 (MEDIUM) L219** heading "Declared labels carry information." U3b is descriptive (U3 NOT EQUIVALENT). Fix:
  "Declared labels were not beaten (descriptive)".
- **A-7 (MEDIUM) L313-314** "Which scorer counts as official matters ... moved ... from 0.88 to 0.92". The H line decides
  nothing, and 0.92 lies inside the official interval [0.80, 0.92]. Fix: drop "matters" and add "a sensitivity line
  that decides nothing; inside the interval".
- **A-8 (MEDIUM) L311** "Some leaderboard detail repositories are gated". At 6afd89a the README says every one is gated.
  **L308** "Each adapter uses the metric the benchmark reports". **L284** `from_lm_eval("lm_eval_out/")` raises on
  multi-metric tasks until `metric=` is given. The API comment at L306 pins bd09816, and its line numbers have moved.
  Fix all four, and run the snippet once on a fixture (the writer's condition stands).
- **A-9 (LOW) L87** "reproduced the full ranking ... tau 0.88". The registered word is LOSES-RANKING. Fix: "agreed with".
- **A-10 (LOW) L65** "18 open models": SATURATION-IRT.json names no roster. Cite the roster source.
- **A-11 (LOW) L40** "It goes only as deep as the data can support". This is a property of the rule as designed and
  has not been validated. Fix: add "by design".
- Confirmed against the record: the remaining numbers are present in the results JSONs (each searched by count; 114 is
  at prog L25140 (g)). The writer's own 4 unsourced items (title {{N}}, AP values, P-FAM size, delta unit) stand.

## Commands
```
git -C E:/TaxoArena_tmp/bz_review/clone checkout -q 6afd89a; venv/Scripts/python -m pip install --force-reinstall --no-deps .
python -m pytest -q -p no:cacheprovider   # 127 passed, 4 deselected in 43.20s; ruff check src tests examples; mypy
python examples/gate_calibration.py > chk_calib.txt; python chk_d2.py > chk_d2.txt   # R-3 seed sweep
python mut/run_mutants.py > mut/results_6afd89a.txt   # 27 lines: 26 KILLED, I5 SURVIVED
python mut/run_own2.py > mut/results_own_6afd89a.txt  # D1-D6
sed -n 25328,25340p docs/judge_v2_program.md          # CERT-SPLIT-DIP outcome vs README/defaults/article
python (dump docs/agents/results/{SATURATION-IRT,CERT-SPLIT-DIP,NESTING,TREE-CUT-GRANULARITY,GAP-FIX-CC,HIER-FAIR-BACKOFF,UNION-AF-ROUTE,ADAPTIVE-PROFILE}.json) > article_src.txt; grep -c per number
grep -n -i "capabilit\|skill" README.md src/benchzoom/__init__.py pyproject.toml   # R-1
```
Scratch: E:/TaxoArena_tmp/bz_review (chk_calib.txt, chk_d2.txt, mut/results_6afd89a.txt, mut/results_own_6afd89a.txt, article_src.txt).
