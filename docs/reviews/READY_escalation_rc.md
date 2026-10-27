# READY — ESCALATION-RC: tools/analysis/escalation_rc.py (zero calls)

Reviewer: adversarial-reviewer, 2026-10-03. Object: branch `escalation-rc`, tip 11d66b50, worktree
`.claude/worktrees/escalation-rc`; script `blob:a17f6821fbad64a734a9ecc365c8996d66af0fba` / `sha256-lf16:acb1f27cf2af8159` /
`sha256-crlf16:33287ff98f1706e5` (the working tree holds the LF rendering, 0 CRLF; `git rev-parse HEAD:<path>` = the blob).
Registration: prog L23960-L23973 (964511fd), record L23939-L23942 with its L23941 bracket (OT1 EQUIVALENT: OOS legs read as
written; 1aa083b3). Both are ancestors of the tip (`merge-base --is-ancestor`). Branch delta: 1 file (`git diff --name-only
main...HEAD | wc -l` = 1). Zero calls, no JVM, no build.

## Verdict: READY, with conditions C-1..C-3 (registrar brackets pre-data; nothing in the code blocks the run)

Run command (plain form, from the MAIN checkout, after the merge; rule 7 applies, so the operator runs it only when no
construction or site null is running, NOT beside the CERT-PC-K2 site null, PID 66072 at review time):
```
python tools/analysis/escalation_rc.py --dry-run
python tools/analysis/escalation_rc.py --run
```
Without a merge (from the worktree): append `--data-root Z:/FAC/TUBerlin/THESIS/TaxoArena` to both (the outputs then land
under main's `experiment_results/archv2/escalation_rc/`).

## Per-claim table (deciding paths)

| # | claim | builder / registration | mine | verdict | sev |
|---|---|---|---|---|---|
| 1 | Rule = margin < tau_m OR OOS < tau_oos, strict; fragility descriptive only | R5, R6; `escalate()` L336 | code reads `(m < tm) \| (o < to)`; fragility enters only `orders()` / rates; X04, X05 killed; my Y1 (rule inverted) killed | CONFIRMED | — |
| 2 | Thresholds from GATE only | R5: GATE side items with a routing row | dry-run: GATE side 2,033, used 2,033, not used 0; my plain-sort percentile over the same GATE scores: AF-U tau_m 0.016134, tau_oos 0.540800; K_0 0.024357 / 0.538278: EQUAL to the code's to the printed digit (6 dp). No EVAL item in the GATE list (filter `== "GATE"`); X06 and my Y4 (GATE+EVAL) killed | CONFIRMED | — |
| 3 | Identity precondition | R12: 0.6049 / 0.6201 / 0.6271, G_AF +1.52pp [+0.14, +2.91], 5,907 / 5,404 | UNION-AF-ROUTE outcome sha256 e50a8e0f… (= the pin): L154 best single 0.6049, L159 AF-U leaf cell 0.6201, L160 K_s K0 0.6271, L170 G_AF +1.52pp two-stage [+0.14pp, +2.91pp]. Refusal fires before any new number (X18, X19 and my Y2, point-only, killed). The hook draws no RNG (`run_boot` L714: `hook(D, wt, v)` after the draws), so the replicates are UNION-AF-ROUTE's | CONFIRMED (targets); the real reproduction is only checkable at `--run` (one EVAL read) | — |
| 4 | K_0 comparator like with like | registration's LIKE WITH LIKE: "labels: same" | K_0 candidates = the centroids of the item's DECLARED source(s) (`k_cands`, `np.isin(g.k_src, srcs)`, srcs from `true_key`), for GATE and EVAL; AF searches all 122 graft leaves. The K_0 re-filing equals k_cells_s0 on 6,153 / 6,153 (0 differ), so it is the K_0 of record, but it reads the source label at filing: D-4 of POSTRUN_union_af_route mirrored onto margins and OOS scores | PARTLY: right cells, label asymmetry not stated in the registration | MEDIUM (C-2) |
| 5 | IFEVAL one cell never margin-escalated (R3) | margin +inf with one candidate | GATE: IFEVAL margin-escalated 0 / 54; but its OOS score is cos to its own TRAIN unit mean (R2), median 0.530 < the pooled tau_oos 0.5408: **29 of 54 IFEVAL GATE items (53.7%) are OOS-escalated, about 29 of the ~102 OOS-escalated GATE items (28%) while IFEVAL is 2.7% of GATE**. MUSR escalates 0 / 73. The OOS leg on IFEVAL measures within-member spread around a one-cell mean, not out-of-scope | PARTLY: the reading is as stated; its consequence is not disclosed | MEDIUM (C-1) |
| 6 | RC1 "wholly above / below 0" strict | R7 | `rc1_verdict`: HELD iff lo > 0, FAILED iff hi < 0, an end at exactly 0 -> UNDETERMINED; X01, X02 killed | CONFIRMED | — |
| 7 | D_E against the analytic random-escalation expectation at the same weights | R7 | `esc_stats` L421-427: D_E = acc(rule) - [(1-e) acc(cells) + e acc(best)], all weighted by v, best single re-fitted in each replicate (X12, X13, X17 killed) | CONFIRMED | — |
| 8 | C0 gate replaced by the identity check | R11 | arms + G_AF + denominators through the same views, fit and replicates are a stronger check than a count gate; accepted | CONFIRMED (bracket the reading) | LOW (C-3) |
| 9 | Support re-derived | SE 0.00367, MDE80 0.0103, DEFF 1.595 (source: UNION-AF-ROUTE U1 two-stage/iid), n_eff 3,704 | sqrt(0.05 x 1.595 / 5,907) = 0.003674; 2.80 x = 0.01029; n_eff 5,907 / 1.595 = 3,703.4 (3,704 is from the unrounded DEFF). Planning discordance 0.05 = e(1-e) P(models' correctness differ) at e 0.25, P 0.27: plausible. DESCRIPTIVE-ONLY at the prediction (+0.003 < 0.0103) holds; the run prints SE_2stage, i.i.d. SE, DEFF, n_eff, MDE80 beside RC1 | CONFIRMED | — |
| 10 | Registered (g): "bounded by e x the accuracy gap (about 0.2 x 0.03)" and the STRUCTURAL line | `rc_lines` L515: "\|D_E\| <= e x \|acc gap on the escalated items\|" | the identity is D_E = e (gap_esc - gap_all), gap = acc(best) - acc(cells); gap_all = -0.0152 on this roster, so with gap_esc = 0 D_E = +0.0038 while the printed bound gives 0: the printed inequality is false, and the registered "bound" is not a bound (gap_esc is not limited by the overall gap). RC1 is reachable at infinite budget (not impossible); the verdict line rests on the prediction, not on (g) | REFUTED (wording; descriptive line) | MEDIUM (C-1) |
| 11 | Write-once | R13, mode "x" | `run()` refuses before any read if outcome or marker exists (X39 killed); marker via `G.read_marker` -> `write_once` mode "x" before the EVAL unseal (X22 killed); outcome via `G.write_once` mode "x"; a changed view sha writes `_VOID.txt` | CONFIRMED (the VOID branch is untested: Y3 survived) | LOW |
| 12 | Read-only real dry-run | — | rc 0, 52 lines, POOL first; pool check rc 0 (child `--dry-run`, nothing written; the tracked engine pool file unmodified, `git status --short` empty); gen_view sha256 BEFORE = AFTER c2930c60…; eval_view NOT opened; R4 AF agreement 5,991 / 5,991 (1.00000), vectors equal to the bundle on 6,139; mtimes of embeddings_cache.db, multicorpus_cache_v1.db, the frozen policy unchanged; `experiment_results/archv2/escalation_rc` absent after | CONFIRMED | — |
| 13 | Selftest / builder mutants | 6 / 6; 40 / 40 killed | re-run: `[ERC] selftest: 6 / 6 passed`; `40 of 40 KILLED; control SURVIVED; survivors none; not applied none` | CONFIRMED | — |

## Own mutants (deciding paths; driver replaces `MUTANTS` and calls the builder's `run_mutants`)

- Y1 escalated items keep the cell model (rule inverted): KILLED (decisive).
- Y2 identity compares the G_AF point only: KILLED (decisive).
- Y4 thresholds on GATE + EVAL: KILLED (decisive).
- Y3 `if not ok_sha:` -> `if False:` (a changed view sha writes the file of record): SURVIVED, not decisive (views opened
  immutable, sha printed before/after in the outcome anyway). D-5.
- Y5 denominator check on items only (components dropped): SURVIVED, not decisive (the identity also refuses). D-5.
- Y6 empty-cell fallback -> model 0, not the best single: SURVIVED in the fixture (no empty cell), fail-closed on real data:
  `[ERC-HOOK]` compares the hook's cell accuracy with run_boot's own arm in every replicate. Not decisive.
- Y7 STRUCTURAL gap over all items: SURVIVED; the line is untested and wrong (row 10). D-3.

## Defects

- **D-1 (MEDIUM; C-1)** IFEVAL's OOS leg (row 5). Fix: registrar bracket on R2/R3 pre-data: "IFEVAL (one cell) is never
  margin-escalated; its OOS score is cos to its own TRAIN mean, so about half its items are OOS-escalated (GATE 29 / 54)". The
  POSTRUN review must print e and D_E excluding IFEVAL (descriptive), and a HELD's words name the share carried by IFEVAL.
- **D-2 (MEDIUM; C-2)** K_0 reads the declared source at filing (row 4). Fix: registrar bracket on the LIKE WITH LIKE table
  and P2: K_0 is source-conditioned k-means (D-4 of UNION-AF-ROUTE, mirrored); D_E(AF-U) - D_E(K_0) is descriptive and never
  "the tree escalates better / worse than unsupervised k-means" (memory anchored-tree-comparisons).
- **D-3 (MEDIUM; C-1)** the STRUCTURAL line and registered (g) (row 10). Fix (either): a one-line edit printing
  "D_E = e x (gap_esc - gap_all)" with both gaps (delta review, <= 3 mutants), or a registrar bracket pre-data that (g) is read
  as that identity and the printed inequality is not a bound.
- **D-4 (LOW)** n_eff 3,703.4 vs 3,704 registered (unrounded DEFF). No action.
- **D-5 (LOW)** untested guards (Y3 VOID, Y5 components). Fix: one selftest case each in a later delta; not blocking.
- **D-6 (LOW)** the escalation set is fixed (GATE not resampled), so threshold variability is outside the interval (R7 says so);
  the words carry "thresholds fixed from GATE".
- **D-7 (LOW)** tau_m is p20 over GATE margins including 54 +inf (one-cell) values, i.e. about p19.4 of the finite margins;
  the same set feeds EVAL, so consistent; disclose.

## Readings: which need registrar brackets (pre-data)

- **Bracket:** R2 + R3 (one-cell centroid and candidate set; D-1), R3 for K_0 (declared-source candidates; D-2), R6
  (fragility descriptive although the title names "decision-fragile"; the registered rule governs), R7 (escalation set fixed;
  strict ends, an end at 0 UNDETERMINED), R11 (C0 gate replaced by the R12 identity; C-3), and (g) (D-3).
- **Confirmed, no bracket needed:** R1, R4, R5, R8, R9, R10, R12, R13.

## Commands

```
python tools/analysis/escalation_rc.py --selftest                       # worktree; 6 / 6 passed (11 s)
python tools/analysis/escalation_rc.py --mutants                        # 40 of 40 KILLED; control SURVIVED
python tools/analysis/escalation_rc.py --dry-run --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena   # rc 0, 52 lines (scratchpad erc/dryrun.log)
python scratchpad/erc/gate_by_src.py      # prepare() + score_items on GATE only: plain-sort thresholds = code's; per-source e, OOS share
python scratchpad/erc/my_mutants.py       # Y1-Y7 through run_mutants: 3 / 7 killed (all decisive ones), survivors above
grep -nE "^    (best single|AF-U leaf cell|K_s K0) |U1: G_AF" experiment_results/archv2/union_af_route/outcome.txt ; sha256sum <same>
stat -c '%Y %s' embeddings_cache.db multicorpus_cache_v1.db .../scratch/union_af_route_train_policy.json   # before = after
git rev-parse HEAD:tools/analysis/escalation_rc.py ; git diff --name-only main...HEAD | wc -l ; git merge-base --is-ancestor 964511fd HEAD
python -c "import math; print(math.sqrt(0.05*1.595/5907), 5907/1.595)"   # 0.003674, 3703.4
```
