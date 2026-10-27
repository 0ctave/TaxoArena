# DRAFT registration (not registered; zero calls; nothing run) — BZ-AXIS-CONFIRM-MMLU: do the leaves of the full axis_v1-recipe tree, built on original-MMLU text, add a gain of interest over the declared subject label under the BZ-METER meter, on items and responses that no tree, demo or meter has read?

Status: DRAFT by the registrar, 2026-10-21, `_as_of 37a83396`. It becomes a registration only when the reviewer's
pre-data READY and the author's answers to the open questions (end of file) are in, and it is appended to
`docs/judge_v2_program.md` as `## Registered <date> (before any code or call) — BZ-AXIS-CONFIRM-MMLU: ...`; the
commit that appends it is the registration commit. No code may be written for it before then. Edits before that
commit are insertion-only brackets `[D<n>]`.

Authority: the author, `docs/agents/author_decisions/2026-10-21.md` (37a83396). D-2026-10-21-1 (read by the main
session as: the fresh confirmation uses the full axis_v1-recipe tree as primary, the zoom curve as a reported
secondary, V1b not registered). D-2026-10-21-2, verbatim: "I don't have enough storage for now for 110GB but i'd like
to do both" (read as: register the original-MMLU test before any of its data is opened; no MMLU results opened
before the registration is committed and READY; zero LLM calls). Relation to the queue item BZ-AXIS-CONFIRM-FRESH
(drafted 2026-10-20, MATH): this draft INSTANTIATES the fresh confirmation on a different benchmark; it does not
retire the MATH draft (open question Q1).

Sources (copied, not re-derived): benchzoom `docs/meter_axis_registration.md` (blob 5de17ff1, LF) and its parent
`docs/meter_registration.md` (blob 5c457088, LF); `docs/reviews/POSTRUN_BZ-METER-AXIS.md` (1260cf3a);
`docs/reviews/POSTRUN_BZ-TREE-VARIANTS-WORK.md` (6e39fc98); programme section "## BZ-METER-AXIS (2026-10-20, 0 calls)
— VALID (POSTRUN 1260cf3a): MATH L3a|L2 SUPPORTED ..." (L25482-L25492 `_as_of 37a83396`); the axis_v1 MMLU-Pro
manifest `E:/benchzoom_demo/axis_v1/mmlu_pro/manifest.json` (config block, build-script LF blob cef9440a).

## Question

On original MMLU (Hendrycks et al., `cais/mmlu` test split, 14,042 items, 57 subjects), is the meter's deciding
statistic `G(L3a | L2)` (leaves of the full axis_v1-recipe tree over the declared subject label) SUPPORTED under the
parent's [R2] words (g >= 3 SE AND g > q95 AND g >= delta_min = 0.10 x 1e-3 nats per cell), on the HELM roster?

## Hygiene

- RESULTS = any per-instance model output, correctness, log-probability or score, and any per-model aggregate
  computed from them, from HELM, tinyBenchmarks or elsewhere. No result is opened (downloaded files may exist; they
  are not parsed) before READY-1 is committed. The public HELM MMLU leaderboard aggregates (per-model, per-subject
  means) are known in general to the author and the main session: disclosed, not used.
- MAY be read before READY-1: the item text and answer key (`cais/mmlu`); HELM `run_spec.json` and `instances.json`
  (inputs, references, instance ids; no predictions); the HELM model list per release; the MMLU-Redux annotations
  (item-error flags, no model result); the MMLU-Pro item text (for the overlap key); the tinyBenchmarks pickle's KEYS
  and array LENGTHS only (no values).
- NEVER read by the tree: any response (`model_responses_read: false` in the manifest, asserted).
- Split (item level, fixed now): items are ids `mmlu/<subject>/<index in cais/mmlu test order>`. Per subject k (57
  subjects in sorted order, k = 0..56), vault = `round(0.4 n_k)` items drawn by `numpy.random.default_rng([20261021,
  k])`; WORK = the rest (about 8,425 / 5,617 items). Near-duplicates: the parent's Section 7.2 rule on the new
  embeddings (a vault item with max cosine >= 0.98 to any WORK item is DROPPED before scoring; vault-vault twins share
  one SE cluster). The id lists and the dropped list are sha-pinned (sha256 of sorted ids, `\n`, utf-8) in READY-1.
- Gates: READY-1 (pre-data: registration, code, synthetic gate, census, tree pins) authorises the WORK read only;
  the WORK dry run then writes an insertion `[A1]` (Support re-cut at the WORK-selected tau^2 of the FULL WORK fitting
  set, POSTRUN_BZ-METER-AXIS D2, with the spread over 5 pseudo-vault draws, D3), criteria-neutral; READY-2 (delta)
  authorises ONE vault read into a new directory. Every mode but the vault read counts 0 vault-response reads.
- Wording (Q2 of POSTRUN_BZ-METER-AXIS carried): the tree is built on ALL 14,042 items' text, vault included (a
  transductive leaf assignment, not a response leak). The read is "fresh items and responses, held out from the meter;
  leaves built on all items' text". Never "clean", "content-closed" or "held-out tree". The MMLU-Pro overlap (S2
  below) is disclosed: about half of MMLU-Pro's items descend from original MMLU questions, and the axis_v1 recipe was
  designed and tuned while reading MMLU-Pro (text and responses).

## Instrument

- Calls: 0 LLM calls. One local embedding run (qwen3-embedding-8b-q8_0 via Ollama, 14,042 texts, 4096-d, then the
  512-d MRL prefix renormalised): one heavy process, under the machine rules (KNOWLEDGE §2). No judge, cap,
  temperature or reference: not a judged test.
- Tree (the object): the axis_v1 RECIPE, run once, seed 0: `examples/identifiable_map.py` at LF blob cef9440a (the
  blob the axis_v1 manifests record; present at benchzoom da3bf22, replaced at d92e406) with `src/` of that commit,
  OR a later commit only if it reproduces the MMLU-Pro axis_v1 pickle sha256 e1d0b00a... bit-identically from the
  cached MMLU-Pro inputs (an execution discriminator, KNOWLEDGE §2 guards). Config = the `config` block of the
  axis_v1 MMLU-Pro manifest verbatim (kappa 3.0, split_rule axis, min_child 80, min_cell 55, use_subjects and
  enter_subjects true, sep_alpha 0.05, null_reps 300, km_restarts 10, seed 0, ...), input columns id, text,
  options, subject, where `subject` := the 17-subcategory label (L1 below). The FULL tree as built is the object: no
  depth cut, prune or leaf merge is chosen on any response. Pinned by tree.csv and pickle sha256 in READY-1, before
  any result is read.
- Levels (the parent's Section 2 readers, unchanged): L0 backbone; **L1 = the 17 Hendrycks subcategories**
  (`categories.py`: subject -> one subcategory); **L2 = the 57 subjects**; L3a = `L1 | axis leaf` (the tree enters
  at L1, so L3a = the leaf). The runner refuses unless every subject maps to exactly one subcategory and every leaf
  lies in one subcategory. The 4 Hendrycks groups (STEM, humanities, social sciences, other) are a DESCRIPTIVE line
  only (`G(L1 | groups)` printed, no word).
  WHY L1 = 17 and L2 = 57 (proposal; open question Q2): (i) L2 must be the FINEST declared label, so that a gain is
  information beyond the benchmark's own annotation (the anchored-tree rule); MMLU has nothing below subject; (ii)
  the recipe enters at L1 (`enter_subjects`), as it entered MATH `subject` (7) and MMLU-Pro `category` (14); 17
  subcategories sit at that granularity, 4 groups would let the recipe spend its first splits re-finding
  subcategories; (iii) entering at the 57 subjects would nest the leaves inside L2, so `L3a | L2` would become a
  nested within-subject test carrying the L2 re-read artefact (POSTRUN_BZ-TREE-VARIANTS-WORK D4) and the floor
  artefact (subjects under 160 items cannot split at min_child 80; MATH V2 analogue), a different statistic from the
  one BZ-METER-AXIS read; (iv) it mirrors MMLU-Pro, whose L2 (`category x src`) carried the MMLU subject as `src`.
- Rosters. PRIMARY: Stanford HELM MMLU per-instance outputs, 81 models after dedup by model across HELM MMLU releases
  v1.0-v1.13 (rule: the NEWEST release that carries the model's MMLU run; the model list and release of each frozen
  in the census commit before READY-1). Outcome = HELM `exact_match` per instance (5-shot, generated letter). Join to
  item ids by (subject, normalised question + choices) from `instances.json`; the census refuses if more than 1% of a
  model's instances are unmatched and drops (before READY-1, listed) any model covering fewer than 99% of the 14,042
  items. COMPANION (secondary): tinyBenchmarks `lb.pickle` (395 Open LLM Leaderboard v1 models, 5-shot
  log-likelihood, no text), joined by subject block and within-subject `cais/mmlu` order; its alignment check after
  READY-1 reads WORK only: Spearman of per-item WORK mean correctness HELM vs tinyBenchmarks >= 0.50, else the
  companion is reported "NOT ALIGNED" and scores nothing.
- Meter: the parent's backbone, reader chain, S-TAU rule with the [R15] inner refits, statistic and item-clustered SE
  (Section 3), [R18] harness (must PASS before the null), null = leaf permuted within L1, R = 200, seed stream
  `[20261021, 8, r]`; all fits on WORK rows, scored once on kept vault rows. Synthetic gate = the `AXIS_FIXTURES` of
  benchzoom `docs/meter_axis_registration.md` Section 9 unchanged (planted SUPPORTED, null not SUPPORTED), with 81
  models in place of 16 printed as a second, non-gating fixture.
- Control of record: L2 (deciding parent). Guard: the runner refuses the vault read unless this registration's
  programme span and blob, the code (clean), the tree pins, the split shas, READY-2 and an absent outcome file all
  match; outputs write-once (mode `x`), SHA256SUMS, backup to `E:/TaxoArena_backup_<date>_axis_confirm_mmlu`.

## Readouts and criteria (x 1e-3 nats per model x item cell; denominators = kept vault items, HELM roster)

1. **C-M1 (DECIDING; family of 1):** `G(L3a | L2)`, HELM roster, scored on the kept vault items (about 5,617 less
   near-duplicate drops; clusters = twin components). Word by the parent's [R2] precedence, applied ONCE to the
   point with its SE: DEGENERATE (tau^2 = 0 selected on WORK) / NOT SUPPORTED (g <= q95, or g + 2 SE < 0.10) /
   SUPPORTED (g >= 3 SE AND g > q95 AND g >= 0.10) / BELOW INTEREST / INCONCLUSIVE. The POINT against 3 SE, q95 and
   delta_min decides, in this one place; no separate interval clause exists (rule 7). One-sided 3 SE, p .00135.
   FAILS (as "the axis leaves add a gain of interest on MMLU") at the planned n if any word other than SUPPORTED is
   printed. Under the transported SE 0.0167, a true g = 0 prints NOT SUPPORTED with probability above 0.99 (the
   interest branch fires for g < 0.10 - 2 SE = 0.067, 4 SE above 0) and a true g = 0.12 prints SUPPORTED with
   probability about 0.88 (g >= 0.10 is 1.2 SE below it; 3 SE = 0.050 binds less), so both outcomes are reachable.
2. **C-M2 (secondary, word carries "(secondary)"):** `G(L3a | L1)`, HELM.
3. **C-M3 (secondary):** `G(L3a | L2 + diff + len)`, the per-model difficulty + length control form of
   BZ-GRANULARITY-WORK / BZ-TREE-VARIANTS-WORK (their C1), HELM; asks whether a gain survives difficulty and length.
4. **C-M4 (secondary):** C-M1 on the tinyBenchmarks roster (only if ALIGNED).
5. **Z (DESCRIPTIVE, no word; the zoom curve of D-2026-10-21-1):** for every depth d of the full tree, the cut at d
   (leaf count printed), `G(cut_d | L2)` and `G(cut_d | L1)` with item-clustered SEs, each also printed net of its own
   cut-at-cells re-read (D4); a max-T over depths (Gaussian multiplier bootstrap, 20,000 draws, seed
   `[20261021, 9]`) printed with its adjusted p. No depth is selected, promoted or decided by Z.
6. **S1 (sensitivity, no word):** C-M1 recomputed with the MMLU-Redux error-flagged items removed from the scored
   set (flag = any annotation other than "ok"; Redux annotates a subset per subject, so unannotated items stay;
   count printed). **S2 (sensitivity, no word):** C-M1 with every vault item whose `split_side.stem_key` matches an
   MMLU-Pro item removed (text only; the overlap count is computed and pinned before READY-1).
7. Identity checks (not criteria): the [R18] harness PASS; the census counts; Section 1-style tree checks (node set,
   partition, every used row mapped).

## Support

(a) DECIDING denominator: C-M1, kept vault items, HELM 81 models. Planned n = 0.4 x 14,042 = 5,617 items before the
near-duplicate drop (MMLU-Pro dropped 143 of 4,797 = 3.0% at 0.98; the census prints MMLU's). Clusters = twin
components among kept vault items; Kish mean cluster size about 1.01 (MMLU-Pro: 4,654 items / 4,625 clusters).
(b) DEFF and its source: 1.13, TRANSPORTED from the MMLU-Pro `L3a | L2` vault readout of BZ-METER-AXIS (measured on
that corpus's own cache: n 4,654, n_eff 4,134; POSTRUN_BZ-METER-AXIS claim 5). Transport named: same reader type and
SE, multiple-choice items, the same 56 MMLU subjects as MMLU-Pro's `src`. Re-measured on WORK in [A1].
(c) n_eff = 5,617 / 1.13 = 4,971.
(d) SE reported: transported from the MMLU-Pro SE 0.0183 at n 4,654 by item count only, no credit for 81 vs 23
models: SE = 0.0183 x sqrt(4,654 / 5,617) = 0.0183 x sqrt(0.8286) = 0.0183 x 0.9102 = 0.0167. Stress transport
(MATH, whose WORK selected tau^2 0.04 and inflated the SE, POSTRUN D2): 0.0628 x sqrt(1,960 / 5,617) = 0.0628 x
0.5907 = 0.0371.
(e) MDE80 at the registered rule (one-sided 3 SE, 80% power): 3.84 x SE = 3.84 x 0.0167 = 0.064 (stress: 3.84 x
0.0371 = 0.142), against the bar delta_min 0.10.
(f) VERDICT: **SCOREABLE** under the primary transport: the registered prediction (point 0.00) is 0.10 from the bar,
above MDE80 0.064. Under the stress transport it would be DESCRIPTIVE-ONLY (0.10 < 0.142). Condition, written now:
if the [A1] WORK re-cut gives a vault MDE80 >= 0.10, C-M1 is recorded DESCRIPTIVE-ONLY by insertion BEFORE the vault
opens, and the word is printed but decides nothing.
(g) STRUCTURAL leg (infinite budget): SUPPORTED is reachable iff the true leaf-over-subject gain is >= 0.10; nothing
caps it by construction (the leaves cross subjects inside a subcategory; a subcategory under 2 x min_child = 160
items cannot split and contributes zero, its share printed by the census; expected: the one-subject subcategory
"engineering"). NOT SUPPORTED is reachable whenever the true g < 0.10 (SE -> 0). DEGENERATE is reachable at any n
and confirms nothing. PASSES (under L1 = 17 subcategories; under entry at the 57 subjects the floor share would have
to be re-derived).

## Predictions (numbers; scored by the runner)

Honest prior: on MMLU-Pro, whose L2 carried the MMLU subject, the axis leaves added nothing over L2 (vault -0.0059,
SE 0.0183, powered; WORK A6 -0.010, SE 0.021); MMLU's L2 is that subject label; the MATH gain arose where the leaves
crossed the declared `level`, a dimension MMLU does not have.

| id | line | interval | point | word set |
|---|---|---|---|---|
| PM1 | C-M1 `L3a\|L2`, HELM (deciding) | [-0.020, 0.060] | 0.00 | NOT SUPPORTED, DEGENERATE |
| PM2 | C-M2 `L3a\|L1`, HELM | [0.050, 0.500] | 0.20 | SUPPORTED (secondary), INCONCLUSIVE (secondary) |
| PM3 | C-M3 controlled, HELM | [-0.030, 0.050] | 0.00 | NOT SUPPORTED (secondary), DEGENERATE (secondary) |
| PM4 | C-M4 `L3a\|L2`, tinyBenchmarks | [-0.020, 0.060] | 0.00 | NOT SUPPORTED (secondary), DEGENERATE (secondary) |
| PM5 | Z: max over d of `G(cut_d\|L2)`, HELM | [-0.020, 0.060] | - | range only |
| PM6 | S1 minus C-M1 | [-0.020, 0.020] | 0.00 | range only |

A prediction HOLDS iff g is in its interval AND the word is in its set; a DEGENERATE where not listed, or a
not-ALIGNED companion for PM4, is scored FAILED / NOT SCORED respectively, printed as such.

## Falsifier

C-M1 SUPPORTED fires it: it overturns the reading of BZ-METER-AXIS MMLU-Pro NOT SUPPORTED (and BZ-GRANULARITY-WORK
A6) that on subject-labelled MMLU-derived items the axis leaves add nothing of interest over the subject label, and
it would show the MATH gain is not MATH-specific. A NOT SUPPORTED does NOT overturn BZ-METER-AXIS MATH SUPPORTED
(different benchmark and label structure); it bounds the claim to benchmarks with a declared level-like dimension.

## What this cannot show (carried into the outcome)

Contamination: MMLU's test set has been public since 2020 and is widely present in pretraining corpora; per-item
outcomes partly reflect exposure, which may cluster by source text and so by text leaves; the meter cannot separate
exposure structure from ability structure. HELM scores a generated letter, tinyBenchmarks log-likelihood: harness
differences are not modelled. Not a test of MATH (BZ-AXIS-CONFIRM-FRESH), of V1b (dropped, D-2026-10-21-1), of other
seeds of the recipe, or of "skills".

## Cost and consequence

0 LLM calls; one local embedding run; HELM per-instance files (size printed by the census) and the 90 MB pickle on
E: (bulky outputs never committed; sha-pinned and backed up). Consequence: SUPPORTED extends the axis claim beyond
MATH; NOT SUPPORTED (powered) records that the full-tree gain did not transfer to MMLU's subject structure.

## Open questions (for the reviewer / the author)

- Q1 (author): does BZ-AXIS-CONFIRM-MMLU retire BZ-AXIS-CONFIRM-FRESH (MATH), or does the MATH confirmation stay
  drafted pending fresh MATH items? The honest prior predicts NOT SUPPORTED on MMLU, so this does not confirm the MATH
  result itself.
- Q2 (author / reviewer): L1 = 17 subcategories and L2 = 57 subjects, with the build entering at L1 (proposal above);
  the alternatives are entry at the 4 groups or at the 57 subjects.
- Q3 (reviewer): C-M1 is the uncontrolled `L3a | L2` (the statistic BZ-METER-AXIS SUPPORTED); the 2026-10-20 draft
  made the difficulty + length controlled form deciding. Confirm which decides.
- Q4 (reviewer): the 99% coverage and 1% unmatched census thresholds, and the newest-release dedup rule.

[D1 2026-10-21 by the registrar: SUPERSEDED as text by the registration of record, docs/judge_v2_program.md section "## Registered 2026-10-21 (before any code or call) — BZ-AXIS-CONFIRM-MMLU: ..." (L25503-L25560 _as_of the commit that writes it, parent 8948b9ed), with E1-E8 of docs/reviews/READY_BZ-AXIS-CONFIRM-MMLU.md (5109ef9c) applied; Q1/Q2 answered by D-2026-10-21-3, Q3/Q4 settled by that review. This draft is not the registration.]
