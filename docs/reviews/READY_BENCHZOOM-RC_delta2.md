# Delta-2 READY review: benchzoom 6afd89a..a3b2d4a (R-1..R-4 of READY_BENCHZOOM-RC_delta 7f797b54) + HF post revision (A-1..A-11), 2026-10-09

Reviewer: adversarial-reviewer. Zero LLM calls. benchzoom read-only (working tree 0 dirty lines, `git status --short | wc -l`;
`git diff --name-only 6afd89a..a3b2d4a | grep -c -iE "\.json|\.csv|\.db|\.npz"` = 0; 7 files, +55/-5). Runs in the scratch clone
E:/TaxoArena_tmp/bz_review/clone checked out at a3b2d4a, non-editable reinstall. Code outside the delta: as CONFIRMED in
a6bf9bb2 and 7f797b54, not re-derived. Post: docs/drafts/hf/benchmark-zoom/article.md, 412 lines, read whole (untracked draft).
Pins at a3b2d4a (LF blob `git rev-parse a3b2d4a:<path>` = `git hash-object` of the CRLF working tree, autocrlf true):
README.md 451693d7308d, NOTICE.md 4db5a6b08039, pyproject.toml e8a753f9151d, docs/defaults.md ca67731fdc09,
src/benchzoom/__init__.py de6418bc696c, examples/gate_calibration.py 3dac96b58f69, tests/test_review_fixes.py f8beb72b9326,
CITATION.cff 52a21b3a2c73 (unchanged by the delta).

## Verdict
**Library: NOT YET RELEASE-CANDIDATE: one residue of R-1 (R-1b), a one-line fix.** CITATION.cff L3 still reads
"benchzoom: nested capability maps and per-model fingerprints for any benchmark". It is present at 6afd89a too: the prior
review's grep covered only the three named files, so its R-1 fix list was incomplete (reviewer gap, not builder error).
Once CITATION.cff says "topic maps", and `git grep -n -i capabilit` over the whole tree returns only README L151, the library is
RELEASE-CANDIDATE with no further review (R-4 stays a release-note condition). R-2 and R-3 CONFIRMED, R-4 CLOSED-DISCLOSED.
130 tests pass, ruff and mypy are clean, D1-D6 all KILLED, and 26 of the 27 original mutants are KILLED (I5 equivalent).
**Post: NOT publishable.** The headline (ADAPTIVE-PROFILE) has not run. A-1..A-11 are fixed in substance (table). One new
MEDIUM overstatement (A-12) and two LOW items (A-13, A-14) remain.

## Library fix table (R-1..R-4)
| id | claim | my result | status | sev |
|---|---|---|---|---|
| R-1 | "capability" gone from README L3, pyproject description and keywords, `__init__` docstring | those 3 files: only README L151 "It is not a capability claim". Whole tree `git grep -n -i capabilit a3b2d4a -- .` = 2 lines: README L151 and **CITATION.cff L3 "nested capability maps"** | PARTLY | MEDIUM (R-1b) |
| R-2 | neutral-id GPQA fixtures; D2, D6 killed; NOTICE states the name-only limit | test parametrized on subject "GPQA Diamond" / task "Gpqa_Main"; limit test present; NOTICE L41-43 text matches; my D2 and D6 reruns KILLED (`test_to_json_gpqa_refused_by_task_or_subject_any_case[subject-GPQA Diamond]`) | CONFIRMED | - |
| R-3 | base-5 reason stated; sweep 193/200 printable | docstring and defaults.md state "next unused base"; `--delta2-bases 1-10` prints 18, 20, 19, 20, 19, 19, 20, 20, 19, 19 = 193 of 200, equal to my 7f797b54 figure to the digit | CONFIRMED | - |
| R-4 | lm-eval selection disclosed as fixture-only | README L96-97 states it; the real run was not done | CLOSED-DISCLOSED; release-note condition stands | LOW |
| T | 130 passed, 4 deselected; ruff, mypy clean | 130 passed, 4 deselected in 30.95 s; ruff "All checks passed!" (src tests examples); mypy "no issues found in 12 source files" | CONFIRMED | - |
| B | "branch main" | the benchzoom branch is `master` (`git branch --show-current`); a3b2d4a is its tip | hand-back wording wrong | LOW |

Mutants: D1-D6 (run_own2.py) all KILLED at a3b2d4a; 27 originals (run_mutants.py): 26 KILLED, I5 SURVIVED (equivalent, as in a6bf9bb2); `grep -c KILLED` = 26 of 27 lines.

## Post fix table (A-1..A-11)
| id | fix in the revision | my check | status |
|---|---|---|---|
| A-1 | opening and "category average" passage posed as questions | L41-48, L67-69: no sentence asserts within-category differences; title (a) is a question | CONFIRMED |
| A-2 | "nothing we tested beat it" removed | L59 and L234-238: wording as fixed; "library default was not an arm" added; HB1, TC, GF1-CC, NESTING sources match | CONFIRMED |
| A-3 | record-plant rows relabelled, like-for-like row | L170-171; prog L25333 "record plants, delta 6: 0 of 15 at n 486, 0 of 15 at n 441"; L25338 "Record plants: D4 4/15, D6 15/15 per size"; TL;DR 0/30 vs 30/30 sums correctly | CONFIRMED |
| A-4 | time spans dropped | L47, L192: none | CONFIRMED |
| A-5 | design choice, not tested gain; reviewer's wording rejected | prog L25138 "ARMS (all with the same b_i and theta_m)": no arm reads raw accuracy, so the writer is RIGHT and my suggested "the headline test will judge it" was wrong. L60, L241-249 correct | CONFIRMED (prior fix wording withdrawn) |
| A-6 | heading "(descriptive)" | L229 | CONFIRMED |
| A-7 | sensitivity line, inside the interval | L336-337; tau 0.8824 [0.8036, 0.9219] vs H 0.9216 | CONFIRMED |
| A-8 | every OLL repo gated; metric scoped; refusal in text and snippet; API re-pinned | README a3b2d4a L91-92 "Every ... gated with automatic approval"; `from_lm_eval(..., metric: str | Mapping)` L530; from_open_llm_leaderboard L672, from_csv L864, metric_table L134, sensitivity L140, Atlas.fit L99, profile L140, plot_sunburst L177, SentenceTransformerEmbedder L60, to_frame has `certified`: all valid at a3b2d4a (src unchanged by the delta) | CONFIRMED; snippet not executed (A-14) |
| A-9 | "agreed with" | L96 | CONFIRMED |
| A-10 | "18 models (the programme's union roster)" | prog L25137 "18 models, Meta-Llama-3-70B-Instruct excluded"; SATURATION-IRT depends_on MC-ROUTER | CONFIRMED |
| A-11 | "by design" | L46 | CONFIRMED |

## Remaining defects
- **R-1b (MEDIUM, library)** CITATION.cff L3 "nested capability maps". Fix: "nested topic maps"; then whole-tree
  `git grep -n -i capabilit` must return README L151 only.
- **A-12 (MEDIUM, post) L355** box heading "Registered before we looked; here is what died." HIER-FAIR-BACKOFF's
  pilot_disclosure says "SEEN before registration ... hier_tests/test3_fair_backoff" (HB1 re-reads the pilot's 11,841 TRAIN
  items, W-5). SATURATION-IRT records SI2 as "confirmatory of a seen pattern (GPQA-HEADROOM)", and P3 is the GPQA band. The
  post's own L154-156 discloses the pilots, but the box heading contradicts it. Fix: "Registered predictions that failed"
  plus one clause: "(the routing prediction was registered after a pilot on the same training items)".
- **A-13 (LOW, post) L292-293** "where the source names none, with the one you declare". lm-eval single-metric tasks
  are read with their only metric and nothing is declared (L331 says so correctly). Fix: "where the source names none and
  a task lists several, with the one you declare".
- **A-14 (LOW, post; carries A-8's condition)** the snippet reassigns `imp` three times, so run top to bottom the last
  source is `from_csv`. `Imported.sensitivity` then raises "this import kept no per-sample records" (sources.py L146-147),
  and the comment at L322 refers to the BBH import. Fix: make the three sources alternatives (comment two of them out), and
  attach the sensitivity call to the leaderboard import by name (`imp_oll.sensitivity("acc")`). Then run it once on a fixture.
  Also re-pin the API comment L326 from 6afd89a to a3b2d4a (line numbers are unchanged).
- Writer's own 4 unsourced items stand (title {{N}}, AP values, P-FAM size, delta unit); all AP numbers are placeholders.
  No other overstatement found against the registered record. Numbers spot-checked: prog L25137/L25138/L25333/L25338/L4691,
  plus the cited JSON fields from the 7f797b54 pass. The descriptive numbers were not re-derived.

## Commands
```
git -C E:/TaxoArena_tmp/bz_review/clone fetch -q Z:/FAC/TUBerlin/benchzoom HEAD; checkout -q a3b2d4a; venv python -m pip install --force-reinstall --no-deps .
python -m pytest -q -p no:cacheprovider        # 130 passed, 4 deselected in 30.95s; ruff check src tests examples; mypy src
python examples/gate_calibration.py --delta2-bases 1-10     # 193 of 200
python mut/run_own2.py > mut/results_own_a3b2d4a.txt        # D1-D6 KILLED
python mut/run_mutants.py > mut/results_a3b2d4a.txt         # 27 originals
git -C Z:/FAC/TUBerlin/benchzoom grep -n -i capabilit a3b2d4a -- .   # 2 lines (README L151, CITATION.cff L3)
git -C Z:/FAC/TUBerlin/benchzoom show 6afd89a:CITATION.cff | grep -n -i capabil   # present before the delta
sed -n 25137,25138p / 25333p / 25338p docs/judge_v2_program.md; JSON pilot_disclosure of HIER-FAIR-BACKOFF, SATURATION-IRT
```
