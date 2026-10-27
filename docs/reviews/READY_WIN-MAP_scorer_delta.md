# READY review WIN-MAP, D-5 scorer delta (2026-10-08): NOT READY (BLOCKED, no delta exists)

Reviewed: WIN-MAP branch tip 7e2673d4 (= 43ff4f09 + the delta READY file only; `git diff --stat 43ff4f09 7e2673d4`:
1 file, docs/reviews/READY_WIN-MAP_delta.md), win_map.py blob 74f2e234 (LF) unchanged. The builder made no change and
reported BLOCKED (B1). Authority: docs/agents/author_decisions/2026-10-08.md D-2026-10-08-5 (5211616a); registrar's
record prog L25317-L25327 (bb5eb124). Zero calls; no pool read (busy.ps1 not needed: nothing was run on data).

## Verdict
NOT READY / BLOCKED. There is no scorer delta to review. The builder's B1 is CONFIRMED: an official-scorer
WIN-MAP cannot pass its own registered identity refusals, and the record does not say which of them change.
This is a registration question for the registrar, and it may need the author. It is not a builder defect.

## Per-claim table
| claim (builder) | my check | result | sev |
|---|---|---|---|
| B1 identity checks are MATH-FIX-bound | win_map.py@7e2673d4 L832 `V.read_key(tw,"response_lite",...,train_meta, True, ...)` (TRAIN refit key); v2_declared_cells.read_key L451: `overlay` = is_correct_mathfix where non-null; identities L40-41 + L205 `r_af=0.6201, b=0.6049, tol=1e-4, gaf=(+1.52pp,+0.14pp,+2.91pp)`; refusal L973 "W-ID: the point policy refitted on TRAIN differs from the frozen file" | CONFIRMED | BLOCKER |
| MATH is in the scored set | union_cells_io.py L9/L158 (one key read with MATH-FIX overlay); win_map fixtures FX_SRC carry MATH (L1139) and an overlay branch for MATH (L1188) | CONFIRMED | - |
| the switch changes the fitted object | D-5 disclosure (prog L25317ff): official scorer credits 2,335 of 23,832 MATH rows vs MATH-FIX 7,516 (5,181 disagreements); MATH ranks differ (Qwen2.5-32B 16th vs 1st). With about 3.2x fewer MATH credits, a TRAIN refit that reproduces the frozen picks of policy 8d68018c, plus R_AF and B to within 1e-4, is not credible. I did not compute it (that needs a pool read, which is unwarranted while the design is undecided) | CONFIRMED in direction; size UNDETERMINED | BLOCKER |
| deviation (3) does not rule on it | L25321 (3) "Criteria, Support, denominators and predictions stand as registered, because the official scorer scores the same rows". It names neither the W-ID identities nor the frozen-policy "never refit" clause. Support (b) borrows UNION-AF-ROUTE's G_AF interval, which was computed under MATH-FIX | CONFIRMED (gap in the record) | BLOCKER |
| C1 H table pin owed | `grep -c 6b010fa6 docs/judge_v2_program.md` = 0 (whole-file count at HEAD 62d269af); 62d269af says "Pin of record owed by the registrar" | CONFIRMED | HIGH (blocks any --run printing H) |

## Defects / required actions
- D1 (BLOCKER, registrar; author if (a)). Bracket WIN-MAP and choose one option:
  - (a) Official scorer throughout. The frozen UNION-AF-ROUTE policy was fitted under MATH-FIX, so W-ID must either
    re-pin under the official scorer or be dropped. Then choose between the frozen policy without the identity check
    and a declared official-scorer refit; the second is a design change against "never refit".
  - (b) Policy and W-ID stay under MATH-FIX from the one key read; only the oracle and waterfall terms use the official
    scorer. rho then mixes two scorers, and every such line must say so.
  - (c) Another reading.
  The author's principle in D-5 ("use the way the benchmark work for each benchmarks") favours (a) for every
  number that WIN-MAP reports. The frozen policy is an input object recorded under MATH-FIX, and D-5 makes that
  record non-retroactive. Whether that input may stay MATH-FIX-fitted is the registrar's call.
  Support must be re-derived for whichever option is chosen. Under (a), G_AF's interval and the MDE come from an
  official-scorer bootstrap, not from UNION-AF-ROUTE.
- D2 (HIGH, registrar). Record the H table pin (sha256-lf 6b010fa60dde7278..., 62d269af) in a registrar's record
  before any consumer --run (deviation (2)).
- D3 (LOW, orchestration). The brief spliced another agent's report into the WIN-MAP instruction. The builder
  correctly worked from the record.
- Check the same pattern elsewhere. ADAPTIVE-PROFILE (37b9b293) reads the union through union_cells_io L187 with
  overlay=True. If its registration also carries MATH-FIX-computed identities or frozen-policy checks, it has the
  same gap. Its delta review must grep for them before it is passed as READY.

## After the registrar's ruling (builder delta, then delta READY)
Checks owed:
- overlay=False at every key read: win_map L832 and union_cells_io L187. Kill test: flipping either back to True
  must make a selftest fail.
- The scorer header line from deviation (1).
- The H line read from the pinned table, refusing on a sha mismatch.
- W-ID per the ruling.
- Selftest and mutant suite re-run, plus prior decisive mutants R1-R8 and N1/N3.
- The real --dry-run, once busy.ps1 exits 1.

## Commands
```
git diff --stat 43ff4f09 7e2673d4                       # 1 file, review only
git show 7e2673d4:tools/analysis/win_map.py | grep -n "read_key\|0\.6201\|0\.6049\|W-ID"   # L832, L205, L973
sed -n 451,453p tools/analysis/v2_declared_cells.py      # overlay = is_correct_mathfix
grep -n -i math tools/analysis/union_cells_io.py         # L9, L158 overlay
sed -n 25317,25327p docs/judge_v2_program.md             # D-5 record, deviation (3), condition
grep -c 6b010fa6 docs/judge_v2_program.md                # 0
```
Own mutants: none. No code delta exists.
