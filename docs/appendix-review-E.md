# Appendix E review — E_Construction_Formalism.tex

Date: 2026-08-01. Scope: `report/04_Appendix/E_Construction_Formalism.tex` only. No builds run.

## Goal 1 — measured/argued tags

None existed. A case-insensitive grep for `\textsc{measured}` / `\textsc{argued}` in the
file returned nothing before editing; there was nothing to remove. (Occurrences of
"measured" in plain prose — "measured proposal", "measured nulls", "the threshold that
governed every decision was measured rather than set" — are part of the canonical
telling and were left intact.)

## Goal 2 — inbound-ref check

Grep for `app:dag-formalism`, `sec:meth-split`, `sec:meth-routing`, `sec:meth-vmf`,
`sec:meth-mrl`, `app:cross-link-operator` across `report/03_Content` and the other
appendices:

- **`app:dag-formalism`** (chapter label): Introduction 143, Background 712, Method
  200/217/307, Results 739/791/1537, Appendix A:56, Appendix C:22/73, Appendix
  F:5/37/47/84. Chapter label untouched.
- **`sec:meth-split`**: Appendix C:22 and C:34 (chance-corrected score vs. Dasgupta
  distinction). The score definition, its exact expectation, and the not-a-Dasgupta-delta
  paragraph are kept in full so both refs land on what they cite.
- **`sec:meth-routing`**: Appendix C:73. Gate/beam/floor mechanics kept in full.
- **`app:cross-link-operator`**: Results 1536 (evaluation-time single-leaf propagation
  vs. construction-time weighted multi-membership). The invariant section, the retired
  polyhierarchy operator note, and the evaluation-time multi-leaf paragraph all kept.
- **`sec:meth-vmf`, `sec:meth-mrl`** and all subsection labels (`tab:pipeline`,
  `subsec:migration`, `sec:meth-migration`, `subsec:quiescence`, `subsec:dim-schedule`,
  `sec:app-dag-pipeline`, `sec:meth-construction-summary`): referenced only from within
  E itself. Labels kept anyway (hard rule: no label deleted or renamed).
- Appendix A:56 quotes "largest gap ever seen (Appendix \ref{app:dag-formalism})" —
  the descent-margin over-provisioning numbers (worst gap 0.0486 over 67 internal nodes,
  0.0647 over twenty-one runs, margin 1.85x) are therefore kept verbatim.

All 14 labels verified present after editing (grep of `\label{...}`); none renamed,
none deleted. `tab:pipeline` now anchors the compressed six-phase subsection heading
(the table it named was cut; no `\ref{tab:pipeline}` exists anywhere in the report).

## Goal 3 — what was cut or compressed

- **Six-phase walkthrough table (`tab:pipeline`) + per-phase paragraphs** (~100 lines):
  duplicated Method 3.2 at lower altitude by its own admission. Replaced by a
  ~19-line pointer paragraph that keeps the three downstream-relevant facts: the loop
  is global, routing is skipped in iteration 1, and Phase 5's operation order is
  outcome-relevant with every operator preserving the single-parent invariant.
- **NiW regulariser section** (~46 lines): diagnostic-only by its own text. Compressed
  to one ~18-line paragraph: not the vMF conjugate (gopal2014mises kept), Student-t
  predictive, hyperparameters/updates deferred to Appendix F, diagonal storage,
  centroid no-update band. The diffuse-node-exclusion arithmetic (unreachable at
  d=256, "retired by arithmetic") was cut as a dead-code note.
- **MRL slice section** (~62 lines): duplicated Method plus the never-run-ablation
  essay. Compressed to ~16 lines: fixed d=256, the two-pressure rationale as pointers,
  mandatory re-normalisation formula, and one sentence recording that the width is an
  unablated compile-time constant whose ablation would confound estimator regime and
  PCA geometry.
- **Dead-code notes**: log-sum-exp multi-path aggregation ("retained dead code" in a
  tree), the 1e-4→1e-30 guard history compressed to a parenthetical, the
  implementing-class roster, the GtWarmStart history compressed to a parenthetical.
- **Migration subsection**: Δτ/RQ2 history compressed to a two-line pointer to
  `sec:res-granularity`; three-effects list folded into two sentences.
- **vMF MLE**: Newton iteration-count re-derivation compressed to one sentence
  (numbers 0.377–0.827 band dropped, "two or three steps, cap of five not reached"
  kept); the "conclusion does not survive its own corrected input" essay compressed to
  the budget-not-estimator statement with both refs.
- Peripheral prose tightening throughout (gate periphery, routing tail, quiescence
  criteria statements) — compressions only, no facts or numbers removed from the
  kept-intact set.

## What was kept in full, and why

- Chance-corrected separation score: W(S), the exact expectation under random
  partition, the score s, and its properties — Appendix C points into
  `sec:meth-split` for exactly this.
- Four-stage acceptance path (proposal / routed sustainability / min-pairwise /
  global gate) including the 129/373, 5682, 0 rejection counts and the
  epsilon_sep = 0.025 positioning between the two measured nulls.
- The proposal gate: full acceptance rule display, paired bootstrap, second-branch
  semantics, tau termination bound, the SE-span argument (13.4x, eight declined
  sites, z = 0.089 worst case), tau-never-bound (88tau / 65tau), both refuted
  corroborations, k-fallback, and the coarsening-asymmetry paragraph (70/68/2,
  z between -7.2 and -14.6).
- Trickle routing gate/beam/floor: all three equations and all numbers
  (delta = 0.12, 0/8299, 0.00%, 0.0486, 0.0647, 1.85x, boundary between 0.05
  and 0.06).
- Stopping-criteria detail: both criteria, the which-arm-fired paragraph, the full
  certificate values paragraph (Section 5.3.1 points here), and the twenty-seed
  period-2 sweep (4 failures, bimodal 3–7e-13 vs 1.3–6.0e-3, Fisher p = 0.0035).
- Single-parent invariant section, including the 154-node / crossDomainNodes = 0
  check and the pointer to `sec:poly-negative`.
- The framing sentence that the pipeline is the instrument, not the contribution.

## Invariants checked

- All 14 labels preserved: `app:dag-formalism`, `sec:meth-construction-summary`,
  `sec:app-dag-pipeline`, `tab:pipeline`, `subsec:migration`, `sec:meth-migration`,
  `subsec:quiescence`, `sec:meth-vmf`, `sec:meth-mrl`, `subsec:dim-schedule`,
  `sec:meth-routing`, `sec:meth-split`, `sec:meth-proposal-gate`,
  `app:cross-link-operator`.
- No numbers changed anywhere; cuts were whole statements only (the dropped
  0.377–0.827 Newton band and the p10/p90 4.0x clause were removed entire, not
  altered).
- All five citations retained: banerjee2005vmf, hornik2014vmf, gopal2014mises,
  kusupati2022mrl, dasgupta2016cost.
- Environments balanced (3 begin/end pairs; 9/9 display-math delimiters — the tenth
  `\[` grep hit is the `\\[4pt]` row separator inside the cases environment).
- No other file modified; no build run (author builds with `arara main.tex`).
- File shrank from 905 to 534 lines. The remainder above the ~500 target is the
  kept-intact set itself (equations plus the mandated empirical paragraphs come to
  roughly 350–380 lines) plus the minimum surrounding context for the 14 ref anchors;
  further shrinkage would cut into content the review marked load-bearing.
