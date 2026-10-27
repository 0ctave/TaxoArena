"""adaptive_profile.py: ADAPTIVE-PROFILE -- on the content-closed v2 union split, do key-based, LOMO-difficulty-adjusted capability
profiles read at an ADAPTIVE (certified, shrunk) granularity of AF-U predict each model's held-out correctness better than
benchmark-level ability, than the best fixed depth, and than k-means cells or a bisecting k-means hierarchy under the same rule?
ZERO calls: no judge, no LLM, no embedding call, no construction, no Gradle. A CPU reader of keyed correctness.

REGISTRATION OF RECORD (resolve by heading; the last bracket wins):
  docs/judge_v2_program.md "## Registered 2026-10-08 (before any code or call) — ADAPTIVE-PROFILE: on the content-closed v2 union
  split, do key-based, LOMO-difficulty-adjusted capability profiles read at an ADAPTIVE (certified, shrunk) granularity of AF-U
  predict ..." L25133-L25145 (_as_of d999e689, parent 375cbcc9): AP1 (the one DECIDING criterion), AP2-AP4 (secondary), Support
  (a)-(g), P1-P9, F-AP, WILL NOT SHOW; the registrar's record L25127-L25131. Shared rules R1 / R2 of the 2026-10-08 HF record
  (L25046). RULINGS applied (registrar 2026-10-08, "## Registrar's record 2026-10-08 ... rulings GAP-FIX-CC P-1 ..., the R1 twin
  rule ..., and ADAPTIVE-PROFILE D-3" L25212-L25219, _as_of 6098f22f): R1 (L25217) and D-3 (L25218); L-1 fixed here (left to the
  delta review by the ruling). Pinned constants: s_max 0.20 logit, BH q 0.05, delta_min 0.0005 Brier, prior N(0, 2^2), clip +-5, B 2,000 on
  default_rng(20261008), the grid s_max {0.15, 0.20, 0.30, inf} x q {0.10, 0.05, 0.01, none} (descriptive).
  MATH SCORER (delta 2026-10-09; authority docs/agents/author_decisions/2026-10-08.md D-2026-10-08-5 (5211616a), recorded in
  "## Author's decision 2026-10-08 (recorded by the registrar; zero calls; insertion only) — D-2026-10-08-1..6 ..." L25317-L25327,
  _as_of bb5eb124, paragraphs D-5, H, DECLARED PRE-RUN DEVIATIONS and CONDITION): the scored MATH flag is the official is_correct,
  read WITHOUT the MATH-FIX overlay (AP-R17); the H sensitivity line is computed from the pinned H table and decides nothing
  (AP-R18); the outcome carries the registrar's header line "MATH scorer: official (eval_results.is_correct, no overlay);
  sensitivity: H (table sha256-lf <hex>); MATH-FIX beside: no". Criteria, Support, denominators and predictions unchanged
  (deviation (3)): under UNUSABLE_CELL the scored sets do not depend on the flag.

LAUNCH SEQUENCE (the run-operator; from the MAIN checkout, plain form; rule 7: --dry-run and --run are POOL READERS: run
`powershell -NoProfile -File E:/TaxoArena_tmp/busy.ps1` first; exit 1 = free, 0 = busy, wait while busy; never beside a
construction or a site null):
  0. python tools/analysis/scratch_dir.py --run -- python tools/analysis/adaptive_profile.py --selftest   # fixtures only; no DB of record
     python tools/analysis/scratch_dir.py --run -- python tools/analysis/adaptive_profile.py --mutants    # the table below (sandbox)
  1. python tools/analysis/adaptive_profile.py --dry-run   # POOL line first; pins; denominators; cost; the B0-2 pool check; the
                                                           #   UNION-AF-ROUTE inputs re-hashed; frozen policy sha; AF-U, F_flat, F_bis
                                                           #   built (TRAIN vectors only); R1 recomputed (471 / 427) and the twin items
                                                           #   by split side; NO key (TRAIN, GATE or EVAL); NO statistic; writes nothing
                                                           #   [ADDED 2026-10-09b, POSTRUN_ADAPTIVE-PROFILE R-3: the structural, pre-key
                                                           #   TRAIN DENOMINATOR line, items / components counted from the gen view;
                                                           #   [AP-DENOM] refuses the dry-run on a mismatch (of record 11,841 / 10,781)]
  2. python tools/analysis/adaptive_profile.py --run       # TRAIN key, the EVAL-twin pre-check, the GATE key (d* only), ONE EVAL key
       read (marker first); outcome WRITE-ONCE: experiment_results/archv2/adaptive_profile/outcome.txt (+ adaptive_profile.READ_STARTED);
       the fingerprint export WRITE-ONCE: E:/TaxoArena_tmp/blog/profiles/adaptive_profile_fingerprints.csv (+ _README.txt). Never
       committed: pin by sha256 and back up to E:/TaxoArena_backup_<date>_adaptive_profile with SHA256SUMS.txt.
  --data-root <dir> (every mode): the checkout whose experiment_results/, data_v2/ and cache DBs are read; from a worktree:
  --data-root Z:/FAC/TUBerlin/THESIS/TaxoArena. CPU: about 2-3 min for the 18 LOMO Rasch fits (measured on a synthetic union of
  the real size: 18 models x 19.7k items, 230 sweeps each), about 2 min for the rest (B 2,000); the view reads and sha256 checks
  as TREE-BACKOFF's: about 10 min in all, one thread; the H line runs core() a second time (about +4 min). Then the
  adversarial-reviewer (numbers), the registrar.
  H TABLE (both modes read it, before any pool read; not a pool file): <data-root>/experiment_results/math_scorer_h/math_h_table.csv
  (math_scorer_h.py --run, 62d269af; backup E:/TaxoArena_backup_20261009_math_scorer_h_table), refused unless its bytes' sha256 is
  6b010fa60dde727816b91196d2cb3045094082c3800fe738adebe21d19eeb1d1 (sha256-lf; the file is LF) and it carries 23,832 rows.
  PRECONDITION OF --run (registrar, deviation (2)): that sha pinned in a registrar's record before the --run.

WHAT --run DOES, IN THIS ORDER (each refusal is a failed precondition: SystemExit, no outcome):
  (1) POOL line; outcome, marker and export absent (write-once); the H table (AP-R18: sha / rows / header refused otherwise) and the
  MATH scorer line; denominators and the DATA ALREADY LOOKED AT line; (2) union_route_
  common.prepare (the B0-2 pool check, AF-U state, the inputs manifest sha256-lf 53021e26... with every file re-hashed, AF and K0..K4
  cells, the frozen TRAIN policy sha256 8d68018c...); the AF-U hierarchy (tree_backoff.af_hier); vectors equal to the bundle's;
  F_flat (K_s cells) and F_bis (bisecting fits) per seed; (3) R1: 471 ids / 427 texts recomputed (refused otherwise); (4) the gen
  view (TRAIN key); BETWEEN the TRAIN key and the eval view: the EVAL-side twin COUNT (printed, never refused on) and the GATE key
  (escalation_curve.gate_key); the eval view, the marker mode "x", THE EVAL KEY READ (union_route_common.read_views); the three
  key reads go through the AP-R17 seam (official, no overlay; the H key beside; [AP-H-JOIN] / [AP-SCORER]); [AP-DENOM]
  EVAL 5,907 / 5,404 and TRAIN 11,841 / 10,781; [AP-GATE-DENOM] 1,944; [AP-GATE-SIDE]; R1 counts on the scored sets and [R1-EVAL]
  (REFUSED iff a twin is among the SCORED EVAL items; before any fit); (5) core():
  [CORRECTED 2026-10-09b by POSTRUN_ADAPTIVE-PROFILE R-1 / R-4 (docs/reviews/POSTRUN_ADAPTIVE-PROFILE.md): [AP-DENOM] TRAIN 11,841
  items / 10,781 components and [AP-GATE-DENOM] 1,944 now run inside `between`, i.e. after the TRAIN and GATE keys and BEFORE the
  eval view opens and the marker is written; the TRAIN components are counted from the data (train_denoms: the key-complete TRAIN
  items' components, = len(set(D.comp[k] for k in D.T))), never from train_units (PRECONDITIONS train_unit stays "item", ruling 3).
  Only [AP-DENOM] EVAL (needs the EVAL key), [AP-GATE-SIDE] and [R1-EVAL] stay after the read.]
  LOMO b, theta, the node fits, the rule, every arm, the bootstrap; (6) AP1, rule 8, F-AP, AP2-AP4, P1-P9, Support (planned and
  measured), the descriptive lines, the fingerprints; (7) the H sensitivity lines (core() on the H key; numbers only); the outcome
  written mode "x" (a view whose sha changed writes *_VOID.txt instead), then the export (official key only).

READINGS (stated, for the READY to confirm or refuse; none is chosen silently):
  AP-R0  R1 (WIN-MAP's W-R1 rule, re-implemented here: win_map.py is not on main): RES = every question_id of
         experiment_configs/reserved_pool_frozen_paeec.json; a RES id is a twin iff another question_id of corpus_questions
         (multicorpus_cache_v1.db, mode=ro) carries the IDENTICAL text (Python ==; blank texts skipped); refused unless 471 ids / 427
         texts; twin v2 item = "i:" + data_v2.common.KeyCache.stem(text) (rp12_pairing P4's item key). Twin items are dropped from
         every fit (LOMO, theta, nodes) and from GATE, counted per side. [RULED 2026-10-08, R1 ruling L25217: the deciding EVAL
         set is the SCORED set of record, 5,907 / 5,404, which carries 0 twins (a twin v2 item joins >= 2 question_ids and is never
         scored); an EVAL-side twin that is not scored is dropped and COUNTED, never refused on; [R1-EVAL] refuses iff a twin is
         among the SCORED EVAL items, after the read and before any fit (the pre-read refusal of blob:7e2949bb is gone).]
         L-2 (READY f4dd6292, disclosed in every outcome's header): the TRAIN-side twins' VECTORS stay among the TRAIN bundle rows
         F_bis is fitted on (AF-U and the K_s cells are used as built); no twin ANSWER enters any fit.
  AP-R1  LOMO difficulty: for each target model m, a joint MAP Rasch fit P = expit(theta_j - b_i) on the OTHER 17 models' answers to
         every kept item (TRAIN, GATE, EVAL; the declared "new model on calibrated items" setting), prior b_i ~ N(0, 4), theta_j
         flat; alternating one Newton step on every b_i and one on every theta_j (steps clipped at +-2; the fixed point is
         unchanged) until the largest step < 1e-10 (20,000 sweeps cap; refused otherwise). m's own answers never enter its b.
  AP-R2  theta_m = the MLE of m's TRAIN answers with b fixed at m's LOMO values (no prior; Newton to 1e-12).
  AP-R3  P(m correct on i) = expit(theta_m + Delta_m,v - b_i(m)); Delta_m,v = the sum of the node offsets d_m,u on the path from the
         depth-1 node to v (Delta = 0 at the union root).
  AP-R4  AF-U = TREE-BACKOFF R1 (every member's LAST dag snapshot; a one-cell member's cell and the pseudo-leaves <no-routing-row>,
         <unrouted> under the union root). The item's BENCHMARK NODE = the depth-1 ancestor of its AF flatLeaf filing leaf (the
         registration's "d = 1 is C" and Support (g)'s "A coincides with C"): for the cross-source EVAL items (UNION-AF-ROUTE D-4)
         it is the FILING member's root; the OWN-SOURCE subset (filing member = stratum source) is printed beside every contrast.
         GATE items: their modal AF leaf (ESCALATION-RC R5).
  AP-R5  Node fits, top-down by depth l = 1..max: for every (model, node u at depth l), over u's kept TRAIN items, the score U and
         the information I at the parent's linear predictor theta_m + Delta_m,parent(u) - b_i(m); tau_l^2 = max(0, UNWEIGHTED mean
         over the models x non-pseudo nodes of depth l with I > 0 of (U / I)^2 - 1 / I) (method of moments; pseudo-leaves excluded);
         posterior (the registered Laplace, one Newton step from the parent's value) d = U / (I + 1 / tau_l^2), SE = (I + 1 /
         tau_l^2)^-1/2. The SE is DEFINED iff the node is not a pseudo-leaf, I > 0 and tau_l^2 > 0; otherwise d = 0 and the node
         is never certified, never descended into.
  AP-R6  Certification: z = d / SE, p = erfc(|z| / sqrt 2) (two-sided); Benjamini-Hochberg (cell_flips.bh: step-up, p_(r) <= r q /
         n) within the family = the children of the same parent with a defined SE for that model; a one-member family certifies
         iff p <= 0.05, i.e. |z| >= 1.95996 (the registered "|z| > 1.96" to five digits). [FIXED 2026-10-08 (L-1 of READY
         f4dd6292): a one-member family at the registered q 0.05 certifies iff |z| > 1.96, STRICT, as registered; at the grid's other
         q (descriptive) a one-member family is BH at n = 1 (p <= q).]
  AP-R7  The rule: start at the benchmark node; descend into the child on the filing path iff SE < s_max (strict) AND certified;
         at the first failure stop (no deeper node is considered); predict at the stop node.
  AP-R8  Arms: B = Delta 0; C = D_1; D_d = the deepest node at depth <= d on the filing path (the leaf when shallower), path-shrunk,
         no certification, d = 1 .. max depth of AF-U; d* = argmin over d of the GATE Brier (first minimum = ties to the
         shallower); E = per (model, filing leaf) the unshrunk MLE offset relative to theta_m (bisection on [-5, +5]; an MLE beyond
         the clip is clipped; a leaf without TRAIN items has 0).
  AP-R9  F_flat = the K_s cells of record (k_cells_s0..s4.tsv, manifest-pinned: UNION-AF-ROUTE's per-source spherical k-means at
         AF-U's per-source leaf counts, seeds 0-4, items filed to the nearest centre of their declared source(s)); hierarchy union ->
         "KF<s>:<SOURCE>" -> cell; prediction at the cell (depth 2), path-shrunk with F_flat's own tau_1, tau_2 (moments over its
         nodes), no certification ("one shrunk offset per (model, cell) toward the benchmark level").
  AP-R10 F_bis: per seed s and source, stability_vs_kmeans.fit_bisecting (largest live cluster split by spherical 2-means; seed s)
         on the source's TRAIN bundle rows (the 256-d unit rows K_s is fitted on) down to AF-U's per-source leaf count; the binary
         tree from the laminar family of leaf sets (source root under the union root); leaf centroid = the renormalised mean of its
         rows; every item filed to the nearest leaf centroid among its declared source(s) (as K_s are filed); rule A at s_max 0.20,
         BH q 0.05, with F_bis's own tau_l. A source whose fit stops short of its leaf count is printed.
  AP-R11 Bootstrap (registered "two-stage", B 2,000, default_rng(20261008)): per replicate the EVAL CK-CLOSE components resampled
         with replacement (UNSTRATIFIED: the registration names no strata), then 5 k-means seeds drawn with replacement (in this
         order, one stream); an F arm's replicate = the mean over the drawn seeds; D replicate = weighted mean difference; 95% =
         numpy percentile (linear) 2.5 / 97.5, 90% = 5 / 95; the bootstrap SD is the SE of record. Support beside: DEFF =
         Var(component bootstrap, seeds at their mean) / Var(item i.i.d. bootstrap on default_rng(20261009)), n_eff = n / DEFF,
         MDE80 = 2.8 SE; Kish = sum n^2 / sum n over the EVAL components. A replicate in which a descriptive subset gets no weight
         is dropped for that subset.
  AP-R12 Rule 8 for AP2-AP4: the predicted modal word (P2 PARITY, P3 NEITHER, P4 KMEANS-BETTER) fails by the sign word opposite to
         the predicted point's sign, or (a PARITY prediction) by the 90% interval leaving [-0.0005, +0.0005].
  AP-R13 Predictions: "X [lo, hi]" HELD iff the point lies in the closed band; the word probabilities by the multi-outcome Brier
         sum; binary events by (p - [event])^2; P7: sign 0 = sign 0 (A identical to C gives D_C = 0 under both scores).
  AP-R14 NOT BUILT (a deviation, reported to the registrar): the af_clean_s42 SECONDARY DESCRIPTIVE leg (A vs B, A vs D_d* on
         MMLU-Pro; P9). Its run directory carries no per-question routing (validation/ holds aggregates; the snapshot nodes carry
         counts), so the leg needs a per-question re-filing of af_clean_s42's TRAIN and held-out questions (site_support's member
         sets and a re-route) and the OPTIONS-key join to the union items: a separate instrument. P9 prints NOT SCORED.
         [ACCEPTED 2026-10-08, ruling D-3 L25218: P9 prints "NOT SCORED (leg not built; declared deviation)", neither HELD nor
         FAILED; the WILL NOT SHOW line carries "anything on af_clean_s42".]
  AP-R15 Fingerprints (descriptive): per (model, AF-U node other than the root and the pseudo-leaves): d, Delta, SE, p, certified
         (BH q 0.05), sign, TRAIN / EVAL item counts, the EVAL observed accuracy and the mean predicted P AT THE NODE (Delta of the
         node); names: the snapshot label and the TRAIN-majority declared stratum (no LLM). The export carries no item id or text.
  AP-R16 Brier and log-loss per (model, item), log-loss with P clipped to [1e-15, 1 - 1e-15]; scores averaged over 18 x EVAL.
  AP-R17 (D-2026-10-08-5) The official scorer of record. The pinned readers call v2_declared_cells.read_key(..., overlay True, ...)
         at three sites (union_route_common.read_views L197 TRAIN and L227 EVAL; escalation_curve.gate_key L528 GATE; NOT
         union_cells_io L187, which this script does not reach: the registrar's CONDITION names that line, reported). The pinned
         modules are NOT edited (MY_PINS unchanged): inside run() the name V.read_key is bound to Scorer.read_key, which calls the
         pinned read_key with overlay False (the official is_correct = eval_results.is_correct, data_v2 ingest) and restores the
         name on exit. Refused [AP-SCORER]: a caller passing overlay != True (a pinned reader changed), reads other than TRAIN /
         GATE / EVAL in that order (the GATE read identified by identity with gate_key's return), any overlay row read.
  AP-R18 (D-2026-10-08-5) The H sensitivity line. In the same unsealed window and scope as each official read, one more SELECT
         (model, item_id, legacy_qid, source, is_correct; no sealed column beyond the key): a row with source 'MATH' takes
         H(question_id = legacy_qid, model) from the pinned table, every other row its official value; the variant rule as
         read_key applies it; refused [AP-SCORER] if H's usable cells differ from the official's. Refused [AP-H-JOIN]: a model
         without H rows, a MATH row without an H row, an id-space mismatch (route 'imported' iff official 1). The line = core() on
         the same positions with H on the MATH cells of TRAIN, GATE and EVAL: Brier of every arm, D_C, D_d*, D_F_bis, D_F_flat
         with their intervals, the MATH rows read and the cells changed per side. NO word, falsifier, rule-8 or prediction line is
         printed for H; the fingerprint export is the official key's.
  Not applicable (stated): no judge verdict (keyed correctness): no wrong(established) count, no tie convention A / B; no call
  cache, --pilot or truncation guard (zero calls).

SELFTEST (--selftest; temp on E: via scratch_dir; opens NO DB of record; about 6 min since the H delta):
  irt           rasch_map against a scipy L-BFGS + dense joint Newton MAP; LOMO column m = the fit on the other models, unmoved by
                m's own answers, moved by another's; theta_fit and the leaf MLE (clipped +-5, empty leaf 0) against brentq; the
                non-convergence refusal
  nodes         node_fit (tau_l^2, d, SE, Delta), certify (q 0.05, 0.10, none), the rule (s_max 0.10, 0.20, inf) and fixed depth
                against a plain-loop oracle on a 3-level tree; hand cases: a one-member family at |z| 1.97 / 1.95 / -1.97, no skipping
                past an uncertified child, SE exactly s_max does not descend
  planted       core() on a synthetic union (12 models, 6 leaves): every planted (model, node) certified with its sign and REACHED by
                the rule; A = the rule at the REGISTERED s_max 0.20 / q 0.05, which differ from q 0.10 / 0.01 / none here (non-
                vacuous); GRANULARITY-PAYS; NULL data: every tau^2 = 0, no descent, D_C = 0 exactly, TOO-SMALL, F-AP not fired, d* =
                1 on the tied GATE curve, the empty OWN-SOURCE subset line; flipping EVAL answers / moving EVAL difficulties leaves
                theta and every node fit unchanged (TRAIN-only); an EVAL item without a cell refused
  branches      AP1 (both clauses at their edges, the order), F-AP (UB95 exactly 0), rule 8, AP2-AP4 four words at the edges, every
                prediction line by value (bands inclusive, each Brier)
  bis_gate      (D-2) F_bis's SE gate on a planted synthetic union: a certified F_bis child with SE >= 0.20 is NOT descended
                into (>= 3 planted models, every seed), a certified child with SE < 0.20 is; core's F_bis Brier equals the rule's at
                s_max 0.20 and differs from the ungated rule's (non-vacuous)
  bis           bis_fit's tree reconstruction and centroids (injected fitter), filing by declared source, the real fit_bisecting
                seam (binary, k leaves), the k > rows refusal, kflat_hier, the non-leaf AF cell refusal
  twins         R1's exact-text rule on a hand table (no normalisation, blanks skipped)
  scorer        (AP-R17 / AP-R18, hand tables in an in-memory view) official K = is_correct although is_correct_mathfix differs;
                H on MATH rows only (a BBH row whose key IS in the table keeps its official value); the AGREE_OR_UNUSABLE rule
                on a two-row cell; V.read_key restored after success and after every refusal; refusals by text: no H row, id space
                (both directions), model without H rows, H usable cells != official, overlay False passed, read order / GATE
                identity / an overlay row (scorer_keys); scorer_line == the registrar's text
  run_e2e     --run end to end on union_af_route's fixture with TREE-BACKOFF's deepened MMLU_PRO tree and responses re-drawn from a
                planted 1PL: every printed Brier (A, C, B, E, D_d*, F_flat, F_bis), the GATE depth curve, d*, tau^2, D_C point /
                95% / SD, D_F_flat point / 95% (seeds resampled), the support SE / DEFF / n_eff / MDE80, Kish, the histogram and the
                share below, the export's certified set and offsets against an INDEPENDENT oracle (scipy Rasch, loop fits, loop BH,
                loop rule, k_cells files, bootstrap replay); AP1 / F-AP by the hand rule; outcome = printed lines; a second --run
                refused, the outcome unchanged. D-2026-10-08-5 (fixture: MATH-FIX overlay values differing from the official on
                about a third of the MATH cells, scored on TRAIN, GATE and EVAL (asserted > 0 per side); a fixture H table keyed by a
                stable legacy_qid (the fixture views are re-stamped before their seal); H moves Brier(A) by > 1e-4 (asserted)):
                the scorer line verbatim (a literal, not scorer_line) before DENOMINATORS; both overlay counts printed 0; every
                official number above against the oracle on the OFFICIAL key (c, never mf); the H line (Brier of 7 arms, d*, D_C
                point / 95%, D_F_flat point / 95%, the changed-cell counts per side) against the same INDEPENDENT oracle on an H key
                built from the fixture's H dict
  null_e2e      --run on the fixture re-drawn without plants: no descent, D_C +0.000000 [+0.000000, +0.000000], TOO-SMALL; the
                scorer line and the H line present
  refusals      pool rc 1 (POOL line first), TRAIN items / components, GATE count, the R1 count, policy sha, a SCORED EVAL twin
                (refused after the read, before any fit, no statistic), marker or export present (refused before any read); no
                outcome written by any. run_e2e carries an UNSCORED EVAL-side twin: counted (1), never refused on. H: wrong sha,
                absent table, wrong row count (refused before DENOMINATORS and any read; nothing under res/ap); a MATH row
                missing from the table, a flipped 'imported' route, a model missing (refused at the read, no statistic, no outcome)
  dry_run       POOL first, structure lines, no key, no statistic, nothing written; the REAL registered constants (and the H
                pin 6b010fa6..., 23,832 rows, the table path, the scorer line with the real sha); the dry-run prints the H TABLE and
                scorer lines
  branch_cover  every print / refusal branch executed
MUTANTS (--mutants; the exact edits are the MUTANTS table at the end of this file; each edits the code ABOVE the SELFTEST marker in
memory and runs the whole selftest on sandbox fixtures): 2026-10-08, 70 of 70 KILLED, control X00 SURVIVED
(run on blob:b31657e8 = this file with this MUTANTS paragraph read @@MUTANT_SUMMARY@@; shards X0-X1 / X2-X3 / X4-X5 / X6-X7).
First pass 69 / 70: X33 (pseudo-leaves in the moments) survived because no fixture placed a TRAIN item on a pseudo-leaf; the
nodes case now puts 15 TRAIN items there (the loop oracle excludes them from the moments) and kills it. Classes: the AP1 / F-AP /
rule-8 clauses at their edges and their order (X01-X09), AP2-AP4 words and rule 8 (X10-X13), the contrast, the interval and the
bootstrap (wrong arm, log-loss, sign, i.i.d. interval, items for components, seeds not resampled / drawn first, 90% as 95%, DEFF,
Kish: X14-X23), LOMO / prior / wrong split side for theta and the node fits / theta's difficulties / R1 keep (X24-X30), the
moments, shrinkage, path and first-level-only (X31-X37), BH, the family, z, one-sided p, the SE gate, SE <= s_max, skipping, the
root start, the registered constants, the rule ignored (X38-X48), fixed depth, d* min<->max / ties / EVAL side, E's clip, F_flat
depth, F_bis rule / tree / filing (X49-X57), R1's rule and refusal, the EVAL-twin pre-check, the denominators, write-once (X58-X63),
OWN-SOURCE, the share below, the fingerprints' certification, P6 / P7 / P1 on the wrong value, Brier summed (X64-X70).
DELTA 2026-10-08 (B1 / D-2 / L-1 / L-2 / D-3): X60 re-targeted (an UNSCORED EVAL-side twin refused), X71-X82 added (the scored-EVAL
twin check; F_bis's SE gate, constant and certification; the one-member threshold; the review's Y1 = X75, Y2 = X73, Y3 = X79,
Y4 = X81, Y5 = X82, Y6 = X80; Y7 / Y8 not re-added); 2026-10-08: 82 of 82 KILLED, control X00 SURVIVED (shards X0-X1 / X2-X3 / X4-X5 / X6-X7 / X8;
X71 first written as a syntax error, rewritten and re-run alone with X00: KILLED by AssertionError); selftest 12 / 12.
DELTA 2026-10-09 (D-2026-10-08-5; AP-R17 / AP-R18): X83-X99 added (overlay kept; H pin, row count, model, MATH-only, missing row,
id-space, AGREE clause, usable-cell, read-order / GATE identity, overlay-row checks; the H line on the official matrices / GATE /
TRAIN; the changed-cell count side; the scorer header word; the dry-run's H read). 2026-10-09, the WHOLE table re-run on the delta
code (the fixture changed: overlay values and the H table): 99 of 99 KILLED, control X00 SURVIVED, none not applied (12 shards X0 /
X1 / ... / X7 / X80-X84 / X85-X89 / X90-X94 / X95-X99, each under scratch_dir.py --run, rc 0); selftest 13 / 13.
DELTA 2026-10-09b (POSTRUN_ADAPTIVE-PROFILE R-1 / R-2 / R-4 and R-3's dry-run line; author D-2026-10-09-1): train_denoms,
structural_train, check_train added; run()'s TRAIN and GATE denominator checks moved before the marker; the scored-line print from
D.comp. SELFTEST: every fixture run now carries the REAL train_unit (_unit: PRECONDITIONS "item"; the pinned fixture cfg says
"component"); run_e2e asserts the run's train_units counted ITEMS (n_units = n_train) and n_train != comp_train (non-vacuous), the
TRAIN DENOMINATOR line and the scored line by value, and the order TRAIN line < GATE key < eval view; refusals asserts the full
[AP-DENOM] / [AP-GATE-DENOM] messages by value (n_train + 1, comp_train - 1, comp_train + 1, n_gate_key + 1), no marker and no eval
view on each, and the same [AP-DENOM] numbers under the "component" unit; dry_run asserts the structural line by value and a dry-run
[AP-DENOM] refusal (comp_train + 1); a key-complete GATE item stripped of its AF cell refuses [AP-GATE-DENOM] at ng - 1 before the
marker. X61 / X62 re-targeted; X100-X107 added (the item-count form = the review's M1, the whole-side
population, the check not called in either mode, the dry-run's forms, the print, the GATE cell filter). 2026-10-09b, the WHOLE
table on blob:2f3c46b9 (this file before the stripped-cell case, its paragraph read @@MUTANT_SUMMARY_B@@): 106 of 107 KILLED,
control X00 SURVIVED, X107 SURVIVED (no fixture GATE item was key-complete without a cell); the refusals case then gained the
stripped-cell case, and on blob:638dea0c (= this file with this paragraph read @@MUTANT_SUMMARY_B@@) X00 SURVIVED (selftest
13 / 13) and X61 / X62 / X100 / X102 / X107 KILLED: 107 of 107 KILLED, none not applied (12 processes, shards X00-X08 / X09-X17 /
... / X99-X107, each under scratch_dir.py --run). MANUAL (two-site edits, on sandbox copies of the tracked tree on E:, cases
run_e2e / refusals / dry_run): MA the TRAIN check moved after the marker (right count, wrong place) KILLED (marker written; TRAIN
line after the eval view); MB the GATE check moved after the marker KILLED; MC the reviewed blob aff80c1d's code under this
selftest KILLED (run_e2e "[AP-DENOM] TRAIN 1101 items / 1101 components, not the registered 1101 / 934": the incident, the
review's M1, now reproduced on the fixture).
DELTA 2026-10-09c (READY_ADAPTIVE-PROFILE_delta3 B-1, L-1): run() prints the registrar's line of D-2026-10-09-1 (prog L25397,
edb060b9) verbatim as a header line right after U.header, "DECLARED DEVIATION D-2026-10-09-1: second EVAL read after the refused
attempt of 2026-10-09 (aff80c1d)", then its authority line; it enters `lines`, so the write-once outcome FILE carries it; the
dry-run prints it prefixed "DEVIATION HEADER (printed by --run into the outcome file, verbatim): ". L-1: the fixture's mc6
registry gains a non-ACTIVE model (V.EXCLUDED, status EXCLUDED, no responses). SELFTEST: run_e2e asserts, from a LITERAL (never
the code's constant), the line as exactly one whole line of the outcome file's BYTES, preceded by U.header's threads line, before
the scorer line and DENOMINATORS, followed by the authority line by value; dry_run asserts the prefixed line after the threads
line and the bare line absent. Mutants X108-X114 added (dropped, wrong attempt sha, stdout only, authority dropped, order swapped,
dry-run line dropped, the review's R03 = the structural roster from the whole registry); X99 re-targeted (a line now sits between
the header and load_h). 2026-10-09c, the WHOLE table on blob:8ce1b1cb (this file before this paragraph and the X99 re-target):
113 of 114 KILLED, control X00 SURVIVED, X99 NOT APPLIED (0 matches: its old text was mistyped); re-targeted, X99 alone KILLED;
114 of 114 KILLED, no survivor (12 + 6 processes under scratch_dir.py --run; selftest 13 / 13 on blob:8ce1b1cb). MANUAL (two-site,
sandbox E:/TaxoArena_tmp/ap_md_20261009 = git archive + this file): MD the deviation lines moved from the header to just before
the result lines (still in the file, not a header) KILLED (run_e2e). Real --dry-run (busy.ps1 rc 1; blob:3fac8429 = this file
before this paragraph): rc 0, 67 lines, POOL pv2_1575de61bb20e977 first, the DEVIATION HEADER line 14, TRAIN DENOMINATOR 11841 /
10781 (registered 11841 / 10781), eval view NOT opened; gen / eval view sha256 equal before and after; the marker untouched.
NOT DONE HERE: the real --dry-run / --run (the operator's, after the delta READY and the registrar's pin of the H table, in a pool
slot); the af_clean_s42 leg (AP-R14; ruled D-3).
"""
import os
import sys


def _pre_root(argv):
    for i, a in enumerate(argv):
        if a == "--data-root" and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith("--data-root="):
            return a.split("=", 1)[1]
    return None


_DR = _pre_root(sys.argv[1:]) if __name__ == "__main__" else None
if _DR:
    os.environ["TAXOARENA_DATA_ROOT"] = os.path.abspath(_DR)
    os.environ["TAXOARENA_RESULTS_ROOT"] = os.path.abspath(_DR)

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")
for _v in THREAD_VARS:
    os.environ[_v] = "1"

import io            # noqa: E402
import csv           # noqa: E402
import copy          # noqa: E402
import json          # noqa: E402
import math          # noqa: E402
import types         # noqa: E402
import hashlib       # noqa: E402
import argparse      # noqa: E402
from collections import Counter, defaultdict   # noqa: E402

import numpy as np   # noqa: E402
from scipy.special import expit, erfc   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import union_route_common as U   # noqa: E402  (pins escalation_rc 8f99db7d, union_cells_io 92a04543, union_af_route bf3f17db)

MY_PINS = (("union_route_common.py", "d54739769d38a3a402e2deaab9e45109cd86de4e"),
           ("tree_backoff.py", "da80c57e927c6ebf8a1db9e2f0420c96c1514519"),
           ("stability_vs_kmeans.py", "a67bbf0a673cffabd7dccdced95b23b11a4ac01b"),
           ("intent_transfer_s0.py", "f662ceb19738f515972871f5963f5dcfc764a271"),
           ("cell_flips.py", "998d39a7b718faa6647c4d5795dcf03044544955"),
           ("escalation_curve.py", "0acfb0cce8d1c91e3365c3f6099172c6d4ccc929"),
           ("union_cells_io.py", "92a04543b9c75eae5f37a76ae86eb189a190a9bd"),
           ("union_af_route.py", "bf3f17dbdc42dbfc6803687d8739d459fc1ed75d"),
           ("v2_declared_cells.py", "f0f568057995b5d0231da6e3d0d48755a7cf8386"))
for _name, _pin in MY_PINS:
    if U.blob_lf(os.path.join(HERE, _name)) != _pin:
        raise SystemExit("[AP] REFUSED: %s is blob:%s, not the pinned blob:%s" % (_name, U.blob_lf(os.path.join(HERE, _name)), _pin))
import tree_backoff as TB          # noqa: E402  (Hier, af_hier: the AF-U hierarchy reader of record (TREE-BACKOFF R1); EC.gate_key)
import stability_vs_kmeans as SVK  # noqa: E402  (fit_bisecting: the BKM seam, split = spherical 2-means)
import cell_flips as CF            # noqa: E402  (bh: Benjamini-Hochberg step-up)

ERC, UAR, V, GB, GC = U.ERC, U.UAR, U.V, U.GB, U.GC
RP = UAR.RP
UCI = U.UCI
FM = GC.FM
EC = TB.EC

TAG = "[AP]"
TEST_ID = "ADAPTIVE-PROFILE"
REG_TEXT = ('docs/judge_v2_program.md "## Registered 2026-10-08 (before any code or call) — ADAPTIVE-PROFILE: on the content-closed'
            ' v2 union split, do key-based, LOMO-difficulty-adjusted capability profiles read at an ADAPTIVE (certified, shrunk)'
            ' granularity of AF-U predict ..." L25133-L25145 (_as_of d999e689, parent 375cbcc9); registrar\'s record L25127-L25131')
OUT = "experiment_results/archv2/adaptive_profile"
# B-1 (READY_ADAPTIVE-PROFILE_delta3): the registrar's record of the author's D-2026-10-09-1 (prog L25394-L25401, edb060b9) requires
# the re-run's outcome FILE to carry this line, verbatim; run() prints it as a header line, right after U.header
DEVIATION_LINE = "DECLARED DEVIATION D-2026-10-09-1: second EVAL read after the refused attempt of 2026-10-09 (aff80c1d)"
DEVIATION_AUTH = ("  deviation authority: the author's D-2026-10-09-1 (docs/agents/author_decisions/2026-10-09.md, defab40c), recorded by the"
                  " registrar at prog L25394-L25401 (edb060b9); it covers the one refused attempt (blob aff80c1d, main 980c3982) only;"
                  " registration, criteria, Support and predictions unchanged")
INF = float("inf")
Z_SINGLE, Q_SINGLE = 1.96, 0.05          # AP-R6 / L-1: the registered single-sibling threshold |z| > 1.96 at q 0.05
REG = dict(U.COMMON, out=OUT + "/outcome.txt", marker=OUT + "/adaptive_profile.READ_STARTED", n_train=11841, comp_train=10781,
           n_gate_key=1944, twins=(471, 427), paeec_rel="experiment_configs/reserved_pool_frozen_paeec.json",
           texts_db="multicorpus_cache_v1.db", s_max=0.20, q=0.05, dmin=0.0005, prior_var=4.0, clip=5.0, B_ap=2000,
           boot_seed=20261008, iid_seed=20261009, grid_s=(0.15, 0.20, 0.30, INF), grid_q=(0.10, 0.05, 0.01, None),
           export_dir="E:/TaxoArena_tmp/blog/profiles", export_file="adaptive_profile_fingerprints.csv",
           export_readme="adaptive_profile_fingerprints_README.txt",
           # D-2026-10-08-5 (AP-R17 / AP-R18): the pinned H table (math_scorer_h.py --run, 62d269af; sha256-lf of the LF bytes)
           h_table="experiment_results/math_scorer_h/math_h_table.csv",
           h_sha="6b010fa60dde727816b91196d2cb3045094082c3800fe738adebe21d19eeb1d1", h_rows=23832)
FIXTURE_REG = dict(out="res/ap/outcome.txt", marker="res/ap/READ_STARTED")
MATH_SRC = "MATH"                        # response.source of a MATH row (= corpus_questions.source; data_v2 ingest)
H_HEAD = ["question_id", "model", "H", "route"]
_REG = [REG]


def reg():
    return _REG[0]


SEEDS = U.SEEDS
UNION = TB.UNION
PSEUDO = TB.PSEUDO
SUPPORT = dict(n_eval=5907, comp=5404, models=18, preds=106326, deff=2.118, n_eff=2789,
               se=dict(AP1=0.00022, AP2=0.000147, AP3=0.000207, AP4=0.000207),
               mde=dict(AP1=0.00062, AP2=0.00041, AP3=0.00058, AP4=0.00058))
VERDICT_LINE = ("Support (f): AP1 SCOREABLE (predicted D_C +0.0012 lies 0.0012 from 0 and 0.0007 from delta_min, both above the MDE80"
                " 0.00062, narrowly); AP2 sign words DESCRIPTIVE-ONLY (predicted +0.0001 < MDE80 0.00041), PARITY SCOREABLE (0.0004 >="
                " 0.000366); AP3 DESCRIPTIVE-ONLY (predicted -0.0002; PARITY needs 0.0003 >= 0.000515: not met); AP4 SCOREABLE narrowly"
                " for KMEANS-BETTER (predicted -0.0006, |pred| > 0.00058)")
PRED = dict(P1=(("GRANULARITY-PAYS", 0.55), ("UNDETERMINED", 0.20), ("TOO-SMALL", 0.25)), P1_band=(0.0005, 0.0020),
            P2=(("PARITY", 0.55), ("NEITHER", 0.25), ("ADAPTIVE-BETTER", 0.10), ("FIXED-BETTER", 0.10)), P2_band=(-0.0003, 0.0005),
            P3=(("NEITHER", 0.55), ("KMEANS-BETTER", 0.25), ("PARITY", 0.15), ("TREE-BETTER", 0.05)), P3_band=(-0.0008, 0.0004),
            P4=(("KMEANS-BETTER", 0.50), ("NEITHER", 0.40), ("PARITY", 0.05), ("TREE-BETTER", 0.05)), P4_band=(-0.0013, 0.0001),
            P5=0.80, P6_band=(0.35, 0.85), P7=0.90, P8=0.70, P8_set=(2, 3, 4), P9_band=(0.0005, 0.0030),
            pt=dict(AP2=0.0001, AP3=-0.0002, AP4=-0.0006))
HIT = Counter()


def hit(name):
    HIT[name] += 1


def refuse(msg):
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def f6(x):
    return "%+.6f" % x


def g6(x):
    return "%.6f" % x


# ── the IRT pieces (AP-R1 .. AP-R3) ────────────────────────────────────────────────────────────────────────────────────────

def rasch_map(Y, prior_var, tol=1e-10, maxit=20000):
    """AP-R1: joint MAP Rasch fit, P(y_ij = 1) = expit(theta_j - b_i), prior b_i ~ N(0, prior_var), theta flat; alternating one
    Newton step on every b_i and one on every theta_j (each step clipped to +-2 logits; the fixed point is unchanged) until the
    largest step is below tol. -> (theta, b, sweeps). Refuses when not converged."""
    y = np.asarray(Y, dtype=np.float64)
    pm = np.clip(y.mean(axis=0), 0.02, 0.98)
    theta = np.log(pm / (1 - pm))
    theta -= theta.mean()
    pi = np.clip(y.mean(axis=1), 0.02, 0.98)
    b = -np.log(pi / (1 - pi))
    for it in range(1, maxit + 1):
        p = expit(theta[None, :] - b[:, None])
        g = -(y - p).sum(axis=1) - b / prior_var
        h = -(p * (1 - p)).sum(axis=1) - 1.0 / prior_var
        db = np.clip(-g / h, -2.0, 2.0)
        b = b + db
        p = expit(theta[None, :] - b[:, None])
        dt = np.clip((y - p).sum(axis=0) / (p * (1 - p)).sum(axis=0), -2.0, 2.0)
        theta = theta + dt
        if max(float(np.abs(db).max()), float(np.abs(dt).max())) < tol:
            return theta, b, it
    hit("REFUSE.CONVERGE")
    refuse("[AP-R1] the LOMO Rasch fit did not converge in %d sweeps" % maxit)


def lomo_b(Y, keep, prior_var):
    """AP-R1: per target model m, b_i from a Rasch fit on the OTHER models' answers to every kept item (TRAIN, GATE, EVAL); never
    fitted on m's answers. -> (n x M array, rows not kept = nan; sweeps per model)."""
    n, M = Y.shape
    out = np.full((n, M), np.nan)
    rows = np.flatnonzero(keep)
    sweeps = []
    for m in range(M):
        others = [j for j in range(M) if j != m]
        _t, b, it = rasch_map(Y[np.ix_(rows, others)], prior_var)
        out[rows, m] = b
        sweeps.append(it)
    return out, sweeps


def theta_fit(Y, Bm, rows, tol=1e-12, maxit=200):
    """AP-R2: each model's global ability theta_m: the MLE of m's answers on `rows` (TRAIN) with b fixed at m's LOMO values."""
    y = np.asarray(Y[rows], dtype=np.float64)
    bb = Bm[rows]
    pm = np.clip(y.mean(axis=0), 0.02, 0.98)
    th = np.log(pm / (1 - pm)) + bb.mean(axis=0)
    for _it in range(maxit):
        p = expit(th[None, :] - bb)
        st = np.clip((y - p).sum(axis=0) / (p * (1 - p)).sum(axis=0), -2.0, 2.0)
        th = th + st
        if float(np.abs(st).max()) < tol:
            return th
    hit("REFUSE.CONVERGE")
    refuse("[AP-R2] the theta fit did not converge")


# ── hierarchies and node fits (AP-R4 .. AP-R7) ────────────────────────────────────────────────────────────────────────────

def anc_table(h):
    """A[l][v] = the ancestor of node v at depth l (v itself at its own depth), -1 when depth(v) < l; l = 0..max depth."""
    D = int(h.depth.max())
    A = np.full((D + 1, h.N), -1, dtype=np.int64)
    for v in range(h.N):
        a = v
        while a >= 0:
            A[int(h.depth[a]), v] = a
            a = int(h.parent[a])
    return A


def children_of(h):
    ch = defaultdict(list)
    for v in range(h.N):
        if h.parent[v] >= 0:
            ch[int(h.parent[v])].append(v)
    return ch


def node_fit(h, node, train, Y, Bm, theta):
    """AP-R4 / AP-R5: top-down per depth l = 1..max: for every (model m, node u at depth l) over the TRAIN items below u, with the
    parent's linear predictor theta_m + Delta_m,parent(u) - b_i(m) as an offset: score U and information I at that offset; tau_l^2 =
    max(0, mean over models x non-pseudo nodes of depth l with I > 0 of (U/I)^2 - 1/I) (method of moments); posterior (one Newton
    step from the parent's value, Laplace) d = U / (I + 1/tau_l^2), SE = (I + 1/tau_l^2)^-1/2, defined iff the node is not a
    pseudo-leaf, I > 0 and tau_l^2 > 0 (else d = 0, SE nan); Delta_m,u = Delta_m,parent(u) + d. `node` = the item's filing leaf
    (-1 = none); `train` = the TRAIN rows of the fit (bool over items)."""
    A = anc_table(h)
    N, M = h.N, Y.shape[1]
    Delta = np.zeros((N, M))
    d = np.zeros((N, M))
    se = np.full((N, M), np.nan)
    Uu = np.zeros((N, M))
    Ii = np.zeros((N, M))
    tau2 = {}
    sel = np.flatnonzero(train & (node >= 0))
    if not len(sel):
        hit("REFUSE.NOTRAIN")
        refuse("[AP-R4] %s: no TRAIN item to fit" % h.label)
    leaf = node[sel]
    for l in range(1, A.shape[0]):
        a = A[l][leaf]
        ok = a >= 0
        rows, av = sel[ok], a[ok]
        par = h.parent[av]
        p = expit(theta[None, :] + Delta[par] - Bm[rows])
        r = Y[rows] - p
        w = p * (1 - p)
        for m in range(M):
            Uu[:, m] += np.bincount(av, weights=r[:, m], minlength=N)
            Ii[:, m] += np.bincount(av, weights=w[:, m], minlength=N)
        lev = np.flatnonzero(h.depth == l)
        real = lev[~h.pseudo[lev]]
        Ul, Il = Uu[real], Ii[real]
        has = Il > 0
        vals = (Ul[has] / Il[has]) ** 2 - 1.0 / Il[has]
        t2 = max(0.0, float(vals.mean())) if vals.size else 0.0
        tau2[l] = t2
        if t2 > 0:
            prec = Ii[lev] + 1.0 / t2
            d[lev] = Uu[lev] / prec
            s = 1.0 / np.sqrt(prec)
            defined = (Ii[lev] > 0) & ~h.pseudo[lev][:, None]
            se[lev] = np.where(defined, s, np.nan)
            d[lev] = np.where(defined, d[lev], 0.0)
        Delta[lev] = Delta[h.parent[lev]] + d[lev]
    return dict(h=h, A=A, Delta=Delta, d=d, se=se, U=Uu, I=Ii, tau2=tau2, ch=children_of(h))


def certify(fit, q):
    """AP-R6: certified[u, m] iff SE defined and (q None: always; else) BH at q rejects u's two-sided p = erfc(|z| / sqrt 2), z = d / SE,
    within the family of u's siblings (the children of u's parent) with a defined SE for model m. A ONE-MEMBER family at the
    registered q 0.05 certifies iff |z| > 1.96 (strict; the registration's "single-sibling threshold |z| > 1.96"; L-1 of READY
    f4dd6292); at the descriptive grid's other q a one-member family is BH at n = 1 (p <= q)."""
    d, se = fit["d"], fit["se"]
    N, M = d.shape
    defined = np.isfinite(se)
    if q is None:
        return defined.copy(), np.full((N, M), np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        z = np.where(defined, d / np.where(defined, se, 1.0), np.nan)
    pv = np.where(defined, erfc(np.abs(np.where(defined, z, 0.0)) / math.sqrt(2.0)), np.nan)
    cert = np.zeros((N, M), dtype=bool)
    for par, kids in fit["ch"].items():
        kids = np.asarray(kids, dtype=np.int64)
        for m in range(M):
            fam = kids[defined[kids, m]]
            if not len(fam):
                continue
            if len(fam) == 1 and q == Q_SINGLE:           # L-1: the registered single-sibling threshold, strict
                cert[fam, m] = bool(abs(float(z[fam[0], m])) > Z_SINGLE)
                continue
            rej = CF.bh([float(pv[u, m]) for u in fam], q)
            cert[fam, m] = np.asarray(rej, dtype=bool)
    return cert, pv


def stops_rule(fit, node, s_max, cert):
    """AP-R7 (the registered rule): start at the item's depth-1 node on its filing path; descend into the child c on the path ONLY
    IF SE(d_m,c) < s_max AND c is certified for m; otherwise stop. -> stop node per (item, model)."""
    A, se = fit["A"], fit["se"]
    M = se.shape[1]
    st = np.repeat(A[1][node][:, None], M, axis=1)
    active = np.ones(st.shape, dtype=bool)
    for l in range(2, A.shape[0]):
        c = A[l][node]
        has = c >= 0
        cc = np.where(has, c, 0)
        ok = active & has[:, None] & (se[cc] < s_max) & cert[cc]
        st = np.where(ok, cc[:, None], st)
        active = ok
    return st


def stops_depth(fit, node, depth, M):
    """D_d: the deepest node on the filing path at depth <= d (the leaf when it is shallower)."""
    A = fit["A"]
    st = A[1][node].copy()
    for l in range(2, min(depth, A.shape[0] - 1) + 1):
        c = A[l][node]
        st = np.where(c >= 0, c, st)
    return np.repeat(st[:, None], M, axis=1)


def predict(fit, stop, rows, theta, Bm):
    M = stop.shape[1]
    return expit(theta[None, :] + fit["Delta"][stop, np.arange(M)[None, :]] - Bm[rows])


def leaf_mle(node, train, Y, Bm, theta, N, clip):
    """Arm E (AP-R8): per (model, filing leaf) the unshrunk MLE offset e relative to theta_m over the leaf's TRAIN items, the root of
    the monotone score sum (y - expit(theta + e - b)) by bisection on [-clip, +clip] (an MLE beyond the clip is clipped); a leaf
    without TRAIN items has e = 0."""
    M = Y.shape[1]
    sel = np.flatnonzero(train & (node >= 0))
    lv = node[sel]
    lo = np.full((N, M), -clip)
    hi = np.full((N, M), clip)
    has = np.bincount(lv, minlength=N) > 0

    def score(e):
        p = expit(theta[None, :] + e[lv] - Bm[sel])
        r = Y[sel] - p
        return np.stack([np.bincount(lv, weights=r[:, m], minlength=N) for m in range(M)], axis=1)
    s_hi, s_lo = score(hi), score(lo)
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        s = score(mid)
        up = s > 0
        lo = np.where(up, mid, lo)
        hi = np.where(up, hi, mid)
    e = 0.5 * (lo + hi)
    e = np.where(s_hi > 0, clip, e)
    e = np.where(s_lo < 0, -clip, e)
    e[~has] = 0.0
    return e


def brier_ll(Y, P):
    """Per item: the mean over models of the Brier score and of the log-loss (P clipped to [1e-15, 1 - 1e-15])."""
    Pc = np.clip(P, 1e-15, 1 - 1e-15)
    br = ((Y - P) ** 2).mean(axis=1)
    ll = -(Y * np.log(Pc) + (1 - Y) * np.log(1 - Pc)).mean(axis=1)
    return br, ll


# ── the F hierarchies (AP-R9, AP-R10) ──────────────────────────────────────────────────────────────────────────────────────

def kflat_hier(seed, cells):
    """F_flat (AP-R9): the K_s cells of record (k_cells_s<seed>.tsv) under one source node each ("KF<s>:<SOURCE>"), the source nodes
    under the union root; pseudo cells under the union root."""
    names, parents, leaves = [UNION], [None], set()
    srcs = sorted(set(c.split(":")[1] for c in cells if c not in PSEUDO))
    for so in srcs:
        names.append("KF%d:%s" % (seed, so))
        parents.append(UNION)
    for c in sorted(set(cells) - set(PSEUDO)):
        names.append(c)
        parents.append("KF%d:%s" % (seed, c.split(":")[1]))
        leaves.add(c)
    for p in PSEUDO:
        names.append(p)
        parents.append(UNION)
        leaves.add(p)
    return TB.Hier("F_flat K%d" % seed, names, parents, leaves)


def bis_fit(seed, Xt, tsrc, ksrc, sources, fitter=None):
    """F_bis (AP-R10): per source (registered order) stability_vs_kmeans.fit_bisecting (largest live cluster split by spherical
    2-means, seed s) on the source's TRAIN bundle rows down to AF-U's leaf count ksrc[source]; leaf centroids = the renormalised
    mean of the leaf's rows. -> (names, parents, leaves, centroids (L, d), centroid source, centroid name, realised leaf counts)."""
    fitter = fitter or SVK.fit_bisecting
    names, parents, leaves = [UNION], [None], set()
    C, csrc, cname, real = [], [], [], {}
    for so in sources:
        rows = np.flatnonzero(tsrc == so)
        k = int(ksrc.get(so, 0))
        if k < 1 or k > len(rows):
            hit("REFUSE.BIS")
            refuse("[AP-R10] source %s: k %d for %d TRAIN rows" % (so, k, len(rows)))
        X = Xt[rows]
        if k == 1:
            lab, L, internal = np.zeros(len(rows), dtype=np.int64), 1, []
        else:
            fz = fitter(X, k, seed)
            lab, L, internal = np.asarray(fz["lab"], dtype=np.int64), int(fz["L"]), list(fz["internal"])
        real[so] = L
        lname = ["B%d:%s:%03d" % (seed, so, j) for j in range(L)]
        if L == 1:
            names.append(lname[0])
            parents.append(UNION)
        else:
            sets = [frozenset(range(L))] + [frozenset(s) for s, _key in internal]
            inner = ["B%d:%s:r" % (seed, so)] + ["B%d:%s:n%03d" % (seed, so, j) for j in range(len(internal))]

            def parent_of(members, self_idx):
                cand = [j for j, s in enumerate(sets) if j != self_idx and members < s]
                if not cand:
                    return None
                return min(cand, key=lambda j: (len(sets[j]), j))
            for j, s in enumerate(sets):
                names.append(inner[j])
                pj = parent_of(s, j)
                parents.append(UNION if pj is None else inner[pj])
            for j in range(L):
                names.append(lname[j])
                parents.append(inner[parent_of(frozenset([j]), -1)])
        for j in range(L):
            v = X[lab == j].sum(axis=0)
            C.append(v / np.linalg.norm(v))
            csrc.append(so)
            cname.append(lname[j])
            leaves.add(lname[j])
    for p in PSEUDO:
        names.append(p)
        parents.append(UNION)
        leaves.add(p)
    return names, parents, leaves, np.vstack(C), np.array(csrc), cname, real


def file_cells(af, vec, srcs, C, csrc, cname):
    """AP-R10 filing (as UNION-AF-ROUTE R3 files K_s): every item of the AF cells to the nearest leaf centroid among its declared
    source(s); an item without a routing row keeps <no-routing-row>."""
    out = {}
    for it, afc in af.items():
        if afc == V.NO_ROUTING_ROW:
            out[it] = V.NO_ROUTING_ROW
            continue
        if it not in vec or it not in srcs:
            hit("REFUSE.NOVEC")
            refuse("[AP-R10] item %s has no vector / declared source" % it)
        out[it] = cname[UAR.file_by_source(vec[it], srcs[it], C, csrc)]
    return out


# ── R1 (the 471 content twins) ─────────────────────────────────────────────────────────────────────────────────────────────

def twins_exact(qtext, res_ids, blank):
    """AP-R0 (the shared rule R1, as WIN-MAP's W-R1): RES = the paeec pool ids; a RES id is a twin iff another (GEN) id carries the
    IDENTICAL text (Python ==, no normalisation; blank texts skipped). -> (sorted twin ids, number of distinct twin texts)."""
    res = set(res_ids)
    gen_texts = set(t for q, t in qtext.items() if q not in res and not blank(t))
    ids = sorted(q for q in res if q in qtext and not blank(qtext[q]) and qtext[q] in gen_texts)
    return ids, len(set(qtext[q] for q in ids))


def twin_items_real():
    """corpus_questions (mode=ro through data_v2.ro.open_ro) and the paeec pool file -> (ids, n texts, twin v2 items "i:" + stem)."""
    conn = RP.ro.open_ro(os.path.join(RP.C.DATA_ROOT, reg()["texts_db"]))
    try:
        qtext = {q: t for q, t in conn.execute("SELECT question_id, text FROM corpus_questions")}
    finally:
        conn.close()
    d = json.load(open(U.P(reg()["paeec_rel"]), encoding="utf-8"))
    res = sorted(set(int(q) for v in d.values() for q in v))
    ids, ntx = twins_exact(qtext, res, RP.EP._kotlin_blank)
    keys = RP.C.KeyCache()
    return ids, ntx, sorted(set("i:" + keys.stem(qtext[q]) for q in ids))


_IO = dict(twins=twin_items_real)


def r1_block(say):
    ids, ntx, items = _IO["twins"]()
    want = tuple(reg()["twins"])
    say("R1 (shared rule; AP-R0): exact-text twins of the paeec pool %d ids / %d distinct texts (registered %d / %d) -> %d v2 items" % (
        len(ids), ntx, want[0], want[1], len(items)))
    if (len(ids), ntx) != want:
        hit("REFUSE.TWINS")
        refuse("[R1] the exact-text rule gives %d ids / %d texts, not the registered %d / %d" % (len(ids), ntx, want[0], want[1]))
    return set(items)


# ── the deciding path (core: no printing; run() and the planted selftests call it) ─────────────────────────────────────────

class Data:
    """items (ids), side ('T' / 'G' / 'E'), Y (n x M 0/1), comp, src (stratum source), keep (R1), models, H (name -> Hier), node
    (name -> filing leaf per item, -1 = none), member (AF filing leaf's member per item)."""


def iid_and_two(Xc, comp, B, seed, iid_seed, masks):
    """AP-R11: two-stage replicates: per replicate b, CK-CLOSE components of EVAL resampled with replacement (unstratified), then the
    5 k-means seeds resampled with replacement (default_rng(seed); in this order). -> (R two-stage column means per mask (S x B x K),
    seed draws (B x 5), R_iid (S x B x K): EVAL items resampled i.i.d. on default_rng(iid_seed))."""
    NE, K = Xc.shape
    cu, cidx = np.unique(np.asarray(comp), return_inverse=True)
    nC = len(cu)
    rng = np.random.default_rng(seed)
    rng2 = np.random.default_rng(iid_seed)
    S = len(masks)
    R = np.empty((S, B, K))
    Ri = np.empty((S, B, K))
    sd = np.empty((B, 5), dtype=np.int64)
    Mk = np.stack([mk.astype(np.float64) for _n, mk in masks])
    for b in range(B):
        w = np.bincount(rng.integers(0, nC, nC), minlength=nC)[cidx].astype(np.float64)
        sd[b] = rng.integers(0, 5, 5)
        W = Mk * w[None, :]
        wi = np.bincount(rng2.integers(0, NE, NE), minlength=NE).astype(np.float64)
        Wi = Mk * wi[None, :]
        with np.errstate(invalid="ignore", divide="ignore"):
            R[:, b, :] = (W @ Xc) / W.sum(axis=1)[:, None]          # a subset without weight in a replicate -> nan (dropped)
            Ri[:, b, :] = (Wi @ Xc) / Wi.sum(axis=1)[:, None]
    return R, sd, Ri


def core(Dt, c):
    """Everything the outcome prints, from the assembled Data -> st."""
    M = len(Dt.models)
    side, keep, Y = Dt.side, Dt.keep, Dt.Y.astype(np.float64)
    tr = (side == "T") & keep
    ga = (side == "G") & keep
    ev = (side == "E") & keep
    if not ev.any() or not tr.any():
        refuse("no EVAL or TRAIN item")
    Bm, sweeps = lomo_b(Dt.Y, keep, c["prior_var"])
    theta = theta_fit(Y, Bm, np.flatnonzero(tr))
    E = np.flatnonzero(ev)
    G = np.flatnonzero(ga)
    for nm, nd_ in Dt.node.items():
        if (nd_[E] < 0).any() or (nm == "AF" and (nd_[G] < 0).any()):
            hit("REFUSE.NOCELL")
            refuse("[AP-R4] %s: an EVAL / GATE item without a cell" % nm)
    YE, YG = Y[E], Y[G]
    st = dict(models=list(Dt.models), n_eval=len(E), n_gate=len(G), n_train=int(tr.sum()), sweeps=sweeps, theta=theta)
    # AF-U
    h = Dt.H["AF"]
    nd = Dt.node["AF"]
    fit = node_fit(h, nd, tr, Y, Bm, theta)
    st["tau2"] = fit["tau2"]
    maxd = int(h.depth.max())
    cert, pv = certify(fit, c["q"])
    stopA = stops_rule(fit, nd[E], c["s_max"], cert)
    cols, names = [], []

    def add(nm, P):
        names.append(nm)
        cols.append(P)
    add("B", expit(theta[None, :] - Bm[E]))
    for dd in range(1, maxd + 1):
        add("D%d" % dd, predict(fit, stops_depth(fit, nd[E], dd, M), E, theta, Bm))
    add("A", predict(fit, stopA, E, theta, Bm))
    e_off = leaf_mle(nd, tr, Y, Bm, theta, h.N, c["clip"])
    add("E", expit(theta[None, :] + e_off[nd[E][:, None], np.arange(M)[None, :]] - Bm[E]))
    # GATE: the depth curve (d* by GATE Brier, ties to the shallower)
    gate_br = []
    for dd in range(1, maxd + 1):
        Pg = predict(fit, stops_depth(fit, nd[G], dd, M), G, theta, Bm)
        gate_br.append(float(brier_ll(YG, Pg)[0].mean()))
    dstar = 1 + int(np.argmin(gate_br))
    st.update(maxd=maxd, gate_br=gate_br, dstar=dstar)
    # F arms
    fstat = {}
    for s in SEEDS:
        hf, nf = Dt.H["KF%d" % s], Dt.node["KF%d" % s]
        ff = node_fit(hf, nf, tr, Y, Bm, theta)
        add("FF%d" % s, predict(ff, stops_depth(ff, nf[E], 2, M), E, theta, Bm))
        hb, nb = Dt.H["BIS%d" % s], Dt.node["BIS%d" % s]
        fb = node_fit(hb, nb, tr, Y, Bm, theta)
        cb, _pb = certify(fb, c["q"])
        sb = stops_rule(fb, nb[E], c["s_max"], cb)
        add("FB%d" % s, predict(fb, sb, E, theta, Bm))
        fstat[s] = dict(tau2_ff=ff["tau2"], tau2_fb=fb["tau2"], below_fb=float((fb["h"].depth[sb] > 1).mean()), stop_fb=sb, fit_fb=fb,
                        cert_fb=cb)
    st["fstat"] = fstat
    # the sensitivity grid (descriptive)
    grid = []
    for s_ in c["grid_s"]:
        for q_ in c["grid_q"]:
            cq, _p = certify(fit, q_)
            sg = stops_rule(fit, nd[E], s_, cq)
            add("G:%s:%s" % (s_, q_), predict(fit, sg, E, theta, Bm))
            grid.append((s_, q_, float((h.depth[sg] > 1).mean())))
    st["grid"] = grid
    # per-item matrices
    BR = np.stack([brier_ll(YE, P)[0] for P in cols], axis=1)
    LL = np.stack([brier_ll(YE, P)[1] for P in cols], axis=1)
    idx = {n: j for j, n in enumerate(names)}
    BR = np.column_stack([BR, BR[:, [idx["FF%d" % s] for s in SEEDS]].mean(axis=1), BR[:, [idx["FB%d" % s] for s in SEEDS]].mean(axis=1)])
    LL = np.column_stack([LL, LL[:, [idx["FF%d" % s] for s in SEEDS]].mean(axis=1), LL[:, [idx["FB%d" % s] for s in SEEDS]].mean(axis=1)])
    names += ["FFmean", "FBmean"]
    idx = {n: j for j, n in enumerate(names)}
    st["names"], st["idx"] = names, idx
    st["point_br"] = {n: float(BR[:, j].mean()) for n, j in idx.items()}
    st["point_ll"] = {n: float(LL[:, j].mean()) for n, j in idx.items()}
    # adaptive-depth histogram
    dA = h.depth[stopA]
    st["hist"] = Counter(int(x) for x in dA.ravel())
    st["below"] = float((dA > 1).mean())
    # subsets: ALL, per stratum source, own-source filing (AF leaf member == stratum source)
    srcE = np.array([Dt.src[k] for k in E])
    own = np.array([Dt.member[k] == Dt.src[k] for k in E], dtype=bool)
    masks = [("ALL", np.ones(len(E), dtype=bool)), ("OWN-SOURCE", own)] + [("SRC:" + s, srcE == s) for s in sorted(set(srcE.tolist()))]
    st["n_xsrc"] = int((~own).sum())
    X = np.column_stack([BR, LL])
    K = BR.shape[1]
    R, sd, Ri = iid_and_two(X, [Dt.comp[k] for k in E], c["B_ap"], c["boot_seed"], c["iid_seed"], masks)
    st["masks"] = [(n, int(mk.sum())) for n, mk in masks]
    st["kish"] = float(sum(v * v for v in Counter(Dt.comp[k] for k in E).values()) / len(E))
    st["n_comp"] = len(set(Dt.comp[k] for k in E))

    def contrast(xname, sub="ALL", metric="br"):
        j = [n for n, _m in masks].index(sub)
        off = 0 if metric == "br" else K
        mk = masks[j][1]
        base = X[mk][:, off + idx["A"]].mean()
        if xname in ("FF", "FB"):
            seeds_cols = [off + idx["%s%d" % (xname, s)] for s in SEEDS]
            pt = float(X[mk][:, off + idx[xname + "mean"]].mean() - base)
            reps = R[j][np.arange(c["B_ap"])[:, None], np.array(seeds_cols)[sd]].mean(axis=1) - R[j][:, off + idx["A"]]
            comp_only = R[j][:, off + idx[xname + "mean"]] - R[j][:, off + idx["A"]]
            iid = Ri[j][:, off + idx[xname + "mean"]] - Ri[j][:, off + idx["A"]]
        else:
            pt = float(X[mk][:, off + idx[xname]].mean() - base)
            reps = R[j][:, off + idx[xname]] - R[j][:, off + idx["A"]]
            comp_only = reps
            iid = Ri[j][:, off + idx[xname]] - Ri[j][:, off + idx["A"]]
        reps = reps[np.isfinite(reps)]
        lo95, hi95 = (float(x) for x in np.percentile(reps, [2.5, 97.5]))
        lo90, hi90 = (float(x) for x in np.percentile(reps, [5.0, 95.0]))
        sdv = float(np.std(reps, ddof=1))
        vi = float(np.nanvar(iid, ddof=1))
        vc = float(np.nanvar(comp_only, ddof=1))
        deff = vc / vi if vi > 0 else float("nan")
        n = int(mk.sum())
        return dict(pt=pt, lo=lo95, hi=hi95, lo90=lo90, hi90=hi90, se=sdv, deff=deff,
                    n_eff=(n / deff) if deff == deff and deff > 0 else float("nan"), mde=2.8 * sdv, n=n, sub=sub)
    st["contrast"] = contrast
    st["D_C"] = contrast("D1")
    st["D_C_ll"] = contrast("D1", metric="ll")
    st["D_dstar"] = contrast("D%d" % dstar)
    st["D_Fbis"] = contrast("FB")
    st["D_Fflat"] = contrast("FF")
    st["D_B"] = contrast("B")
    st["D_E"] = contrast("E")
    # fingerprints (q = 0.05 BH certification, TRAIN fit; EVAL calibration at the node)
    fp = []
    cert05, pv05 = certify(fit, c["q"])
    A = fit["A"]
    for v in range(h.N):
        if v == h.root or h.pseudo[v]:
            continue
        below = A[int(h.depth[v])][nd] == v
        ntr = int((below & tr).sum())
        evm = below[E]
        for m in range(M):
            if evm.any():
                pn = expit(theta[m] + fit["Delta"][v, m] - Bm[E[evm], m])
                cal = (int(evm.sum()), float(YE[evm, m].mean()), float(pn.mean()))
            else:
                cal = (0, float("nan"), float("nan"))
            fp.append(dict(model=Dt.models[m], node=h.names[v], depth=int(h.depth[v]), d=float(fit["d"][v, m]),
                           delta=float(fit["Delta"][v, m]), se=float(fit["se"][v, m]), p=float(pv05[v, m]),
                           certified=bool(cert05[v, m]), n_train=ntr, n_eval=cal[0], eval_acc=cal[1], eval_pred=cal[2],
                           label=Dt.labels.get(h.names[v], ""), majority=Dt.majority.get(h.names[v], ("", 0.0))))
    st["fp"] = fp
    st["fit"], st["cert"], st["stopA"] = fit, cert, stopA
    st["Bm"], st["E"], st["G"] = Bm, E, G
    return st


# ── words (AP1 .. AP4, F-AP, rule 8, predictions) ──────────────────────────────────────────────────────────────────────────

def ap1_word(c_, dmin):
    """AP1 (DECIDING), the clauses in the order written; the first that holds is the word."""
    if c_["lo"] > 0 and c_["pt"] >= dmin:
        hit("AP1.PAYS")
        return "GRANULARITY-PAYS"
    if c_["hi"] < dmin:
        hit("AP1.TOO_SMALL")
        return "TOO-SMALL"
    hit("AP1.UNDETERMINED")
    return "UNDETERMINED"


def sign_word(c_, dmin, better, worse, tag):
    if c_["lo"] > 0:
        hit(tag + ".BETTER")
        return better
    if c_["hi"] < 0:
        hit(tag + ".WORSE")
        return worse
    if c_["lo90"] >= -dmin and c_["hi90"] <= dmin:
        hit(tag + ".PARITY")
        return "PARITY"
    hit(tag + ".NEITHER")
    return "NEITHER"


def fap_fires(word, c_):
    fires = bool(word == "TOO-SMALL" and c_["hi"] < 0)
    hit("FAP.FIRED" if fires else "FAP.NOT")
    return fires


def rule8_ap1(c_, dmin):
    ref = bool(c_["lo"] <= 0 or c_["pt"] < dmin)
    hit("R8.AP1.REFUTED" if ref else "R8.AP1.NOT")
    return ref


def rule8_sign(word, c_, pred_pt, pred_word, better, worse, dmin):
    """AP-R12: the predicted word fails by the sign word opposite to the predicted point's sign, or (a PARITY prediction) by the 90%
    interval leaving [-dmin, +dmin]."""
    opp = worse if pred_pt > 0 else better
    fails = bool(word == opp)
    if pred_word == "PARITY":
        fails = fails or not (c_["lo90"] >= -dmin and c_["hi90"] <= dmin)
    hit("R8.SIGN.FAILS" if fails else "R8.SIGN.NOT")
    return fails, opp


def brier_multi(probs, observed):
    return float(sum((p - (1.0 if o == observed else 0.0)) ** 2 for o, p in probs))


def brier_bin(p, event):
    return float((p - (1.0 if event else 0.0)) ** 2)


def band_word(x, band):
    held = bool(band[0] <= x <= band[1])
    hit("PRED.HELD" if held else "PRED.FAILED")
    return "HELD" if held else "FAILED"


def ci(c_):
    return "%s [%s, %s] (90%% [%s, %s]; bootstrap SD %s)" % (f6(c_["pt"]), f6(c_["lo"]), f6(c_["hi"]), f6(c_["lo90"]), f6(c_["hi90"]),
                                                            g6(c_["se"]))


def ap_lines(st, c):
    """Every registered criterion, falsifier, rule-8 and prediction line, by value -> (lines, words)."""
    dmin = c["dmin"]
    L, w = [], {}
    pb = st["point_br"]
    dc, dd, fb, ff = st["D_C"], st["D_dstar"], st["D_Fbis"], st["D_Fflat"]
    L.append("BRIER (EVAL, mean over %d models x %d items = %d predictions; lower is better): A %s | C (= D_1) %s | B %s | E %s |"
             " D_d* (d* = %d) %s | F_flat (mean of K0..K4) %s | F_bis (mean of 5 seeds) %s" % (
                 len(st["models"]), st["n_eval"], len(st["models"]) * st["n_eval"], g6(pb["A"]), g6(pb["D1"]), g6(pb["B"]), g6(pb["E"]),
                 st["dstar"], g6(pb["D%d" % st["dstar"]]), g6(pb["FFmean"]), g6(pb["FBmean"])))
    w["AP1"] = ap1_word(dc, dmin)
    L.append("AP1 (DECIDING) D_C = Brier(C) - Brier(A) = %s on the %d EVAL items (%d components) -> %s" % (
        ci(dc), dc["n"], st["n_comp"], w["AP1"]))
    L.append("  AP1 clauses (in order): GRANULARITY-PAYS iff LB95 > 0 AND point >= %.4f: LB95 %s, point %s; TOO-SMALL iff UB95 < %.4f:"
             " UB95 %s" % (dmin, f6(dc["lo"]), f6(dc["pt"]), dmin, f6(dc["hi"])))
    r8 = rule8_ap1(dc, dmin)
    L.append("  AP1 rule 8: GRANULARITY-PAYS refuted iff LB95 <= 0 or point < %.4f -> %s" % (dmin, "REFUTED" if r8 else "NOT REFUTED"))
    w["FAP"] = fap_fires(w["AP1"], dc)
    L.append("FALSIFIER F-AP (AP1 TOO-SMALL with UB95(D_C) < 0: the adaptive profile predicts held-out correctness WORSE than"
             " benchmark-level ability): %s" % ("FIRES" if w["FAP"] else "NOT FIRED"))
    if w["FAP"]:
        L.append("  F-AP FIRED: the RESP-PROFILE-INFO RP1 reading does not convert into per-model prediction; the fingerprints are"
                 " withdrawn as anything beyond description")
    w["AP2"] = sign_word(dd, dmin, "ADAPTIVE-BETTER", "FIXED-BETTER", "AP2")
    L.append("AP2 (SECONDARY) D_d* = Brier(D_%d) - Brier(A) = %s -> %s (sign words DESCRIPTIVE-ONLY at the registered support;"
             " PARITY scoreable)" % (st["dstar"], ci(dd), w["AP2"]))
    w["AP3"] = sign_word(fb, dmin, "TREE-BETTER", "KMEANS-BETTER", "AP3")
    L.append("AP3 (SECONDARY; DESCRIPTIVE-ONLY at the registered support; confirmatory of a seen pattern) D_F_bis = Brier(F_bis) -"
             " Brier(A) = %s -> %s" % (ci(fb), w["AP3"]))
    w["AP4"] = sign_word(ff, dmin, "TREE-BETTER", "KMEANS-BETTER", "AP4")
    L.append("AP4 (SECONDARY; scoreable narrowly for KMEANS-BETTER; confirmatory of a seen pattern) D_F_flat = Brier(F_flat) -"
             " Brier(A) = %s -> %s" % (ci(ff), w["AP4"]))
    for nm, c_, pw, better, worse in (("AP2", dd, "PARITY", "ADAPTIVE-BETTER", "FIXED-BETTER"),
                                      ("AP3", fb, "NEITHER", "TREE-BETTER", "KMEANS-BETTER"),
                                      ("AP4", ff, "KMEANS-BETTER", "TREE-BETTER", "KMEANS-BETTER")):
        fails, opp = rule8_sign(w[nm], c_, PRED["pt"][nm], pw, better, worse, dmin)
        L.append("  %s rule 8 (predicted %s, point %+.4f): fails by %s%s -> %s" % (
            nm, pw, PRED["pt"][nm], opp, " or the 90%% interval leaving [-%.4f, +%.4f]" % (dmin, dmin) if pw == "PARITY" else "",
            "FAILS" if fails else "DOES NOT FAIL"))
    return L, w


def pred_lines(st, w, c):
    L = []
    dc = st["D_C"]
    for key, word_key, val in (("P1", "AP1", dc["pt"]), ("P2", "AP2", st["D_dstar"]["pt"]), ("P3", "AP3", st["D_Fbis"]["pt"]),
                               ("P4", "AP4", st["D_Fflat"]["pt"])):
        L.append("PREDICTION %s: word %s (Brier over the outcomes %.4f); point %s in [%+.4f, %+.4f] -> %s" % (
            key, w[word_key], brier_multi(PRED[key], w[word_key]), f6(val), PRED[key + "_band"][0], PRED[key + "_band"][1],
            band_word(val, PRED[key + "_band"])))
    pb = st["point_br"]
    e5 = bool(pb["E"] > pb["D1"])
    hit("P5.TRUE" if e5 else "P5.FALSE")
    L.append("PREDICTION P5: Brier(E) %s > Brier(C) %s: %s (p 0.80, Brier %.4f)" % (g6(pb["E"]), g6(pb["D1"]), e5, brier_bin(PRED["P5"], e5)))
    L.append("PREDICTION P6: share of EVAL (model, item) predictions served below the benchmark level %.4f in [%.2f, %.2f] -> %s" % (
        st["below"], PRED["P6_band"][0], PRED["P6_band"][1], band_word(st["below"], PRED["P6_band"])))
    agree = bool(np.sign(st["D_C_ll"]["pt"]) == np.sign(dc["pt"]))
    hit("P7.TRUE" if agree else "P7.FALSE")
    L.append("PREDICTION P7: log-loss agrees with Brier on the sign of D_C (log-loss D_C %s, Brier D_C %s; sign 0 = 0): %s (p 0.90,"
             " Brier %.4f)" % (f6(st["D_C_ll"]["pt"]), f6(dc["pt"]), agree, brier_bin(PRED["P7"], agree)))
    p8 = bool(st["dstar"] in PRED["P8_set"])
    hit("P8.TRUE" if p8 else "P8.FALSE")
    L.append("PREDICTION P8: d* = %d in {2, 3, 4}: %s (p 0.70, Brier %.4f)" % (st["dstar"], p8, brier_bin(PRED["P8"], p8)))
    hit("P9.UNSCORED")
    L.append("PREDICTION P9 (af_clean_s42 leg, Brier(B) - Brier(A) in [+0.0005, +0.0030]): NOT SCORED (leg not built; declared"
             " deviation) -- neither HELD nor FAILED (registrar's ruling D-3, prog L25218; AP-R14)")
    return L


def support_lines(st, c):
    L = ["SUPPORT (registered, planned): EVAL %d items in %d CK-CLOSE components x %d models = %d (model, item) predictions; DEFF %.3f"
         " (TRANSPORTED from RESP-PROFILE-INFO); n_eff %d; SE AP1 %.5f, AP2 %.6f, AP3 / AP4 %.6f; MDE80 AP1 %.5f, AP2 %.5f, AP3 / AP4"
         " %.5f" % (SUPPORT["n_eval"], SUPPORT["comp"], SUPPORT["models"], SUPPORT["preds"], SUPPORT["deff"], SUPPORT["n_eff"],
                    SUPPORT["se"]["AP1"], SUPPORT["se"]["AP2"], SUPPORT["se"]["AP3"], SUPPORT["mde"]["AP1"], SUPPORT["mde"]["AP2"],
                    SUPPORT["mde"]["AP3"]), "  " + VERDICT_LINE]
    L.append("SUPPORT (measured, beside the deciding statistic; the bootstrap SD is the SE of record): EVAL %d items, %d components,"
             " Kish mean component size %.4f (sum n^2 / sum n over the EVAL components)" % (st["n_eval"], st["n_comp"], st["kish"]))
    for nm, key in (("AP1 D_C", "D_C"), ("AP2 D_d*", "D_dstar"), ("AP3 D_F_bis", "D_Fbis"), ("AP4 D_F_flat", "D_Fflat")):
        c_ = st[key]
        L.append("  %-12s SE %s; DEFF %.3f (Var component bootstrap / Var item i.i.d. bootstrap; seeds at their mean); n_eff %.0f;"
                 " MDE80 %s" % (nm, g6(c_["se"]), c_["deff"], c_["n_eff"], g6(c_["mde"])))
    L.append("  NOT APPLICABLE (stated): no judge verdict enters (keyed correctness): no wrong(established) count, no tie convention"
             " A / B; no call cache, --pilot or truncation guard (zero calls)")
    return L


def desc_lines(st, c):
    pb, pl = st["point_br"], st["point_ll"]
    L = ["DESCRIPTIVE: LOMO Rasch sweeps per model %s; theta (global, TRAIN) %s" % (
        "/".join(str(x) for x in st["sweeps"]), ", ".join("%s %+.3f" % (m, t) for m, t in zip(st["models"], st["theta"])))]
    L.append("DESCRIPTIVE: tau_l^2 by depth (AF-U, method of moments on TRAIN) %s" % (
        ", ".join("d%d %.5f" % (l, t) for l, t in sorted(st["tau2"].items()))))
    L.append("DESCRIPTIVE: depth curve (path-shrunk, no certification): GATE Brier %s; EVAL Brier %s; d* = %d (argmin GATE, ties"
             " to the shallower)" % (" ".join("d%d %s" % (j + 1, g6(x)) for j, x in enumerate(st["gate_br"])),
                                      " ".join("d%d %s" % (j, g6(pb["D%d" % j])) for j in range(1, st["maxd"] + 1)), st["dstar"]))
    tot = sum(st["hist"].values())
    L.append("DESCRIPTIVE: adaptive-depth histogram (EVAL (model, item) predictions by the depth A stops at) %s; served below the"
             " benchmark level %.4f" % (" ".join("d%d %d" % (k, v) for k, v in sorted(st["hist"].items())), st["below"]))
    if tot != len(st["models"]) * st["n_eval"]:
        refuse("the adaptive-depth histogram counts %d predictions, not %d" % (tot, len(st["models"]) * st["n_eval"]))
    for nm, key in (("B (global only)", "D_B"), ("E (leaves, unshrunk)", "D_E")):
        L.append("DESCRIPTIVE: Brier(%s) - Brier(A) = %s" % (nm, ci(st[key])))
    L.append("DESCRIPTIVE: log-loss A %s | C %s | B %s | E %s | D_d* %s | F_flat %s | F_bis %s" % (
        g6(pl["A"]), g6(pl["D1"]), g6(pl["B"]), g6(pl["E"]), g6(pl["D%d" % st["dstar"]]), g6(pl["FFmean"]), g6(pl["FBmean"])))
    for nm, x in (("D_C", "D1"), ("D_d*", "D%d" % st["dstar"]), ("D_F_bis", "FB"), ("D_F_flat", "FF")):
        L.append("DESCRIPTIVE: log-loss %s = %s" % (nm, ci(st["contrast"](x, metric="ll"))))
    for sub, n in st["masks"][1:]:
        if n == 0:
            hit("SUB.EMPTY")
            L.append("DESCRIPTIVE subset %s: no EVAL item" % sub)
            continue
        hit("SUB.SCORED")
        parts = []
        for nm, x in (("D_C", "D1"), ("D_d*", "D%d" % st["dstar"]), ("D_F_bis", "FB"), ("D_F_flat", "FF")):
            c_ = st["contrast"](x, sub=sub)
            parts.append("%s %s [%s, %s]" % (nm, f6(c_["pt"]), f6(c_["lo"]), f6(c_["hi"])))
        L.append("DESCRIPTIVE subset %s (n %d): %s" % (sub, n, "; ".join(parts)))
    L.append("DESCRIPTIVE: cross-source filed EVAL items (AF leaf of another member) %d; the OWN-SOURCE subset excludes them" % st["n_xsrc"])
    for s_, q_, below in st["grid"]:
        c_ = st["contrast"]("G:%s:%s" % (s_, q_))
        # D vs A of a grid arm X is Brier(X) - Brier(A); the grid prints Brier(C) - Brier(X) = D_C - (Brier(X) - Brier(A))
        dcx = st["D_C"]["pt"] - c_["pt"]
        L.append("SENSITIVITY (descriptive) s_max %s q %s: Brier %s; Brier(C) - Brier(arm) %s; below the benchmark level %.4f" % (
            "inf" if s_ == INF else "%.2f" % s_, "none" if q_ is None else "%.2f" % q_, g6(st["point_br"]["G:%s:%s" % (s_, q_)]),
            f6(dcx), below))
    for s in SEEDS:
        fs = st["fstat"][s]
        L.append("DESCRIPTIVE F seed %d: F_flat Brier %s (tau^2 %s); F_bis Brier %s (tau^2 %s; below the benchmark level %.4f)" % (
            s, g6(pb["FF%d" % s]), " ".join("d%d %.5f" % kv for kv in sorted(fs["tau2_ff"].items())), g6(pb["FB%d" % s]),
            " ".join("d%d %.5f" % kv for kv in sorted(fs["tau2_fb"].items())), fs["below_fb"]))
    ncert = sum(1 for r in st["fp"] if r["certified"])
    L.append("FINGERPRINTS (descriptive; BH q %.2f within sibling families, TRAIN fit; not a capability claim): %d certified (model, node)"
             " pairs of %d; strong %d, weak %d" % (c["q"], ncert, len(st["fp"]), sum(1 for r in st["fp"] if r["certified"] and r["d"] > 0),
                                                   sum(1 for r in st["fp"] if r["certified"] and r["d"] < 0)))
    for m in st["models"]:
        rows = [r for r in st["fp"] if r["model"] == m and r["certified"]]
        L.append("  %s: %s" % (m, "; ".join("%s(d%d) %+.3f SE %.3f n %d EVAL %d obs %.3f pred %.3f" % (
            r["node"], r["depth"], r["d"], r["se"], r["n_train"], r["n_eval"], r["eval_acc"], r["eval_pred"]) for r in rows) or "none"))
    return L


def all_lines(st, c):
    L, w = ap_lines(st, c)
    L += pred_lines(st, w, c)
    L += support_lines(st, c)
    L += desc_lines(st, c)
    L.append("WHAT THIS RESULT WILL NOT SHOW (registered): that a fingerprint is a capability claim or tree-robust (no cross-tree leg);"
             " anything beyond these 18 models, this split, draw and embedder; that the tree's CONTENT beats k-means; a label-free result"
             " on the deciding leg (AF-U is [SC]); any judged quantity; an independent replication of RESP-PROFILE-INFO (same EVAL"
             " items); anything on af_clean_s42 (the leg is not built: ruling D-3, prog L25218)")
    return L, w


FP_HEAD = ("model", "node", "depth", "offset_vs_parent", "path_offset", "se", "p_two_sided", "certified", "sign", "n_train_items",
           "n_eval_items", "eval_observed_acc", "eval_predicted_at_node", "snapshot_label", "train_majority_stratum", "majority_share")


def fingerprint_csv(fp):
    import io
    buf = io.StringIO()
    wr = csv.writer(buf, lineterminator="\n")
    wr.writerow(FP_HEAD)
    for r in fp:
        wr.writerow([r["model"], r["node"], r["depth"], "%.6f" % r["d"], "%.6f" % r["delta"], "%.6f" % r["se"] if r["se"] == r["se"] else "",
                     "%.6g" % r["p"] if r["p"] == r["p"] else "", int(r["certified"]),
                     ("strong" if r["d"] > 0 else "weak") if r["certified"] else "", r["n_train"], r["n_eval"],
                     "%.6f" % r["eval_acc"] if r["eval_acc"] == r["eval_acc"] else "",
                     "%.6f" % r["eval_pred"] if r["eval_pred"] == r["eval_pred"] else "", r["label"], r["majority"][0],
                     "%.4f" % r["majority"][1]])
    return buf.getvalue()


# ── the MATH scorer (D-2026-10-08-5; AP-R17 official of record, AP-R18 the H sensitivity line) ─────────────────────────────

def scorer_line(c):
    """The registrar's declared pre-run deviation (1), verbatim form (prog L25317-L25327)."""
    return ("MATH scorer: official (eval_results.is_correct, no overlay); sensitivity: H (table sha256-lf %s); MATH-FIX beside: no"
            % c["h_sha"])


def load_h(c, say):
    """AP-R18: the per-row H table of record, refused unless its bytes' sha256 equals the pin (the file is LF, so this is the
    sha256-lf) and it carries the pinned row count, the header question_id,model,H,route, H in {0, 1}, no duplicate key.
    -> {(question_id, model): (H, route)}. Read before any pool read; refused = nothing read, nothing written."""
    p = U.P(c["h_table"])
    if not os.path.isfile(p):
        hit("REFUSE.H_PIN")
        refuse("[AP-H-PIN] the H table %s is absent: no H line without the pinned table (D-2026-10-08-5, deviation (2))" % p)
    raw = open(p, "rb").read()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != c["h_sha"]:
        hit("REFUSE.H_PIN")
        refuse("[AP-H-PIN] the H table %s is sha256 %s, not the pinned %s" % (p, sha, c["h_sha"]))
    rows = list(csv.reader(io.StringIO(raw.decode("utf-8"))))
    if not rows or rows[0] != H_HEAD:
        hit("REFUSE.H_PIN")
        refuse("[AP-H-PIN] the H table's header is %r, not %r" % (rows[0] if rows else None, H_HEAD))
    tab = {}
    for r in rows[1:]:
        if len(r) != 4 or r[2] not in ("0", "1") or (int(r[0]), r[1]) in tab:
            hit("REFUSE.H_PIN")
            refuse("[AP-H-PIN] the H table row %r is malformed or repeated" % (r,))
        tab[(int(r[0]), r[1])] = (int(r[2]), r[3])
    if len(tab) != int(c["h_rows"]):
        hit("REFUSE.H_PIN")
        refuse("[AP-H-PIN] the H table carries %d rows, not the pinned %d" % (len(tab), c["h_rows"]))
    say("H TABLE (AP-R18; the sensitivity line's input, decides nothing): %s sha256-lf %s (= the pin); %d rows, %d models; H credits"
        " %d, route 'imported' %d" % (c["h_table"], sha, len(tab), len(set(m for _q, m in tab)), sum(h for h, _r in tab.values()),
                                      sum(1 for _h, r in tab.values() if r == "imported")))
    say(scorer_line(c))
    return tab


def h_key(tw, table, cv, models, items, rule, htab):
    """AP-R18: the H key over the SAME scope and the same unsealed window as the official read: a MATH row's value is H(question_id
    = legacy_qid, model), every other row's the official is_correct; the variant rule as v2_declared_cells.read_key applies it.
    Refused: a model outside the H table; a MATH row without an H row; an id-space mismatch (H route 'imported' iff official 1)."""
    ms = set(models)
    hm = set(m for _q, m in htab)
    if ms - hm:
        hit("REFUSE.H_JOIN")
        refuse("[AP-H-JOIN] model(s) %s have no row in the H table" % sorted(ms - hm))
    mlist, ilist = sorted(ms), sorted(items)
    vals = defaultdict(list)
    n_math = n_diff = 0
    for s0 in range(0, len(ilist), 500):
        ch = ilist[s0:s0 + 500]
        for m, iid, q, src, ok in tw.execute("SELECT model, item_id, legacy_qid, source, is_correct FROM %s WHERE corpus_version=? AND"
                                             " model IN (%s) AND item_id IN (%s)" % (table, ",".join("?" * len(mlist)),
                                                                                    ",".join("?" * len(ch))), [cv] + mlist + ch):
            if m not in ms or iid not in items:
                continue
            v = int(ok)
            if src == MATH_SRC:
                hv = htab.get((int(q), m))
                if hv is None:
                    hit("REFUSE.H_JOIN")
                    refuse("[AP-H-JOIN] MATH row (question_id %s, model %s) has no H row" % (q, m))
                if (hv[1] == "imported") != (v == 1):
                    hit("REFUSE.H_JOIN")
                    refuse("[AP-H-JOIN] id space: (question_id %s, model %s) official %d but H route %r" % (q, m, v, hv[1]))
                n_math += 1
                n_diff += int(hv[0] != v)
                v = hv[0]
            vals[(iid, m)].append(v)
    K = defaultdict(dict)
    for (iid, m), vs in vals.items():
        if len(vs) == 1 or (rule == "AGREE_OR_UNUSABLE" and len(set(vs)) == 1):
            K[iid][m] = vs[0]
    return K, dict(math_rows=n_math, h_changed=n_diff)


class Scorer:
    """AP-R17: the pinned readers (union_route_common.read_views: TRAIN and EVAL; escalation_curve.gate_key: GATE) call
    v2_declared_cells.read_key(..., overlay True, ...). Inside run() that name is bound to Scorer.read_key, which calls the pinned
    read_key with overlay FALSE (the official is_correct, of record) and, in the same window and scope, builds the H key (AP-R18).
    The pinned modules are not edited (their blobs stay as MY_PINS). Restored on exit."""

    def __init__(self, htab):
        self.htab, self.calls, self.orig = htab, [], None

    def __enter__(self):
        self.orig = V.read_key
        V.read_key = self.read_key
        return self

    def __exit__(self, *exc):
        V.read_key = self.orig
        return False

    def read_key(self, tw, table, cv, models, items, overlay, rule):
        if overlay is not True:
            hit("REFUSE.SCORER")
            refuse("[AP-SCORER] a key read with overlay %r: the pinned callers pass True (a pinned reader changed)" % (overlay,))
        K, st = self.orig(tw, table, cv, models, items, False, rule)
        KH, hs = h_key(tw, table, cv, models, items, rule, self.htab)
        if set((i, m) for i, d in K.items() for m in d) != set((i, m) for i, d in KH.items() for m in d):
            hit("REFUSE.SCORER")
            refuse("[AP-SCORER] the H key's usable cells differ from the official key's (%s)" % table)
        self.calls.append(dict(table=table, K=K, KH=KH, hs=hs, overlay_rows=st["overlay_rows"]))
        return K, st


def scorer_keys(calls, gate_K):
    """The three reads in their order (TRAIN response_lite, GATE response_lite, EVAL response) -> (KH_tr, KH_gate, KH_ev); refused
    otherwise. The GATE read is identified by identity with the key escalation_curve.gate_key returned."""
    tabs = [x["table"] for x in calls]
    if tabs != ["response_lite", "response_lite", "response"] or calls[1]["K"] is not gate_K:
        hit("REFUSE.SCORER")
        refuse("[AP-SCORER] key reads %s, not TRAIN / GATE / EVAL (response_lite, response_lite, response)" % tabs)
    if any(x["overlay_rows"] for x in calls):
        hit("REFUSE.SCORER")
        refuse("[AP-SCORER] an overlay row was read (official scorer: no overlay)")
    return calls[0]["KH"], calls[1]["KH"], calls[2]["KH"]


def h_lines(sH, D, A_H, Kg, Kg_H, c, calls):
    """AP-R18: the H sensitivity lines (DESCRIPTIVE; no word, falsifier or prediction is read off them)."""
    hit("H.LINE")
    pb = sH["point_br"]
    dT = int((D.A[D.T] != A_H[D.T]).sum())
    dE = int((D.A[D.E] != A_H[D.E]).sum())
    dG = int((Kg != Kg_H).sum())
    L = ["SENSITIVITY H (AP-R18, D-2026-10-08-5; DESCRIPTIVE, decides nothing: no criterion word, falsifier or prediction is read off"
         " these lines): the MATH cells re-scored by H (table sha256-lf %s), every other cell official; MATH rows read TRAIN %d /"
         " GATE %d / EVAL %d, H differs on %d / %d / %d; scored (model, item) cells changed TRAIN %d, GATE %d, EVAL %d" % (
             c["h_sha"], calls[0]["hs"]["math_rows"], calls[1]["hs"]["math_rows"], calls[2]["hs"]["math_rows"],
             calls[0]["hs"]["h_changed"], calls[1]["hs"]["h_changed"], calls[2]["hs"]["h_changed"], dT, dG, dE)]
    L.append("  H BRIER (EVAL, %d predictions): A %s | C (= D_1) %s | B %s | E %s | D_d* (d* = %d) %s | F_flat (mean of K0..K4) %s |"
             " F_bis (mean of 5 seeds) %s" % (len(sH["models"]) * sH["n_eval"], g6(pb["A"]), g6(pb["D1"]), g6(pb["B"]), g6(pb["E"]),
                                               sH["dstar"], g6(pb["D%d" % sH["dstar"]]), g6(pb["FFmean"]), g6(pb["FBmean"])))
    L.append("  H D_C = Brier(C) - Brier(A) = %s" % ci(sH["D_C"]))
    L.append("  H D_d* = %s; H D_F_bis = %s; H D_F_flat = %s" % (ci(sH["D_dstar"]), ci(sH["D_Fbis"]), ci(sH["D_Fflat"])))
    return L


# ── modes ───────────────────────────────────────────────────────────────────────────────────────────────────────────────

def files():
    return [os.path.abspath(__file__), U.__file__, TB.__file__, SVK.__file__, CF.__file__, EC.__file__] + \
        [os.path.join(HERE, n) for n, _ in U.PINS]


def denominators(say):
    c = reg()
    say("DENOMINATORS (registered): TRAIN %d scored items / %d CK-CLOSE components (fits); GATE %d key-complete items (d* only);"
        " EVAL %d items / %d components (scored ONCE) x 18 models" % (c["n_train"], c["comp_train"], c["n_gate_key"], c["n_route"],
                                                                     c["comp_route"]))
    say("PLANNED: LOMO Rasch b (prior N(0, %.0f)), theta TRAIN MLE, EB path shrinkage (tau_l^2 by moments); rule s_max %.2f, BH q %.2f;"
        " delta_min %.4f; bootstrap B %d default_rng(%d) (EVAL components, then k-means seeds); i.i.d. beside on default_rng(%d);"
        " grid s_max %s x q %s" % (c["prior_var"], c["s_max"], c["q"], c["dmin"], c["B_ap"], c["boot_seed"], c["iid_seed"],
                                   "/".join("inf" if s == INF else "%.2f" % s for s in c["grid_s"]),
                                   "/".join("none" if q is None else "%.2f" % q for q in c["grid_q"])))
    say("DATA ALREADY LOOKED AT (disclosed; the predictions are informed, NOT blind): PROFILE-RELIABILITY anchor R 0.6728 (judge"
        " reliability 0.70 at about 210 q per cell, the key at 50); PROFILE-RELIABILITY-INTERACTION 0.8665 vs null 0.3142 (the brief's"
        " '0.88 vs 0.51' is in no committed record); RESP-PROFILE-INFO RP1 R2_int AF-U +0.052744 vs RWS p97.5 +0.037950, SRC +0.045400,"
        " RP2 K0-BETTER D -0.004423 [-0.006118, -0.002728], DEFF 2.118; PROFILE-DEVIATION-CERT 127 / 280 key-certified [P-FAM];"
        " CELL-DIFFICULTY composition share 0.6985, eta2_b 0.2299; SCPB iteration 3 (exploratory, TRAIN only, not of record): about"
        " 210 items per reliable profile. Every claim is relative to these 18 models")
    say("DISCLOSED (L-2, READY f4dd6292): R1's TRAIN-side twin items keep their VECTORS among the TRAIN bundle rows that F_bis's"
        " bisecting fits are fitted on (as AF-U and the K_s cells of record, used as built; no answer of a twin enters any fit: LOMO b, theta, the node fits"
        " and GATE drop them); P9 NOT SCORED, the af_clean_s42 leg not built (declared deviation, ruling D-3, prog L25218)")
    say("COST: 0 calls, 0 CCE; CPU: 18 LOMO Rasch fits, 11 hierarchy fits (AF-U, 5 F_flat, 5 F_bis), 5 x 6 bisecting fits, B %d"
        " replicates of weighted means; minutes on one thread" % c["B_ap"])


def prepare(say):
    """Everything before any key: union_route_common.prepare, the AF-U hierarchy, the vectors, F_flat and F_bis, the GATE cells."""
    c = reg()
    S = U.prepare(say, c, refuse, hit)
    u = UAR.reg()
    ip = UAR.input_paths()
    b, _meta = GC.load_bundle(U.P(ip["bundle"]), expect=(u["pool"], u["n_eval_before"], u["comp_before"]), sides=None)
    Xt = FM.unit_rows(np.asarray(b["train_X"], dtype=np.float64))
    classes = [str(x) for x in b["classes"]]
    tsrc = np.array([UAR.src_of(classes[i]) for i in np.asarray(b["train_y"], dtype=int)])
    side, _smeta = UAR._SIDES[0]()
    val = UAR.afu_paths(S["single"])[1]
    rows_h, rows_t = ERC.item_rows(ip["merged"] if S["single"] else val)
    srcs = UAR.item_sources(rows_h + rows_t)
    gits, gcell, _gs = ERC.gate_items(rows_h, side)
    if not gits:
        hit("REFUSE.GATE_EMPTY")
        refuse("no GATE item has a routing row: d* is undefined")
    H_af = TB.af_hier(u["members"], u["afu"], S["single"])
    say("  AF-U HIERARCHY (TREE-BACKOFF R1): %s" % H_af.summary())
    ids = sorted(set(i for i, cl in S["af"].items() if cl != V.NO_ROUTING_ROW) | set(gits))
    vec = ERC.get_vectors(ids)
    nov = [i for i in ids if i not in vec]
    if nov:
        hit("REFUSE.NOVEC")
        refuse("%d item(s) have no vector (first %s)" % (len(nov), nov[:3]))
    nb = ERC.check_vectors_vs_bundle(vec, b)
    H_kf, H_bis, bis_cells = {}, {}, {}
    for s in SEEDS:
        H_kf[s] = kflat_hier(s, list(S["kx"]["K%d" % s].values()))
        names, parents, leaves, C, csrc, cname, real = bis_fit(s, Xt, tsrc, S["man"]["ksrc"], u["sources"])
        H_bis[s] = TB.Hier("F_bis s%d" % s, names, parents, leaves)
        bis_cells[s] = file_cells(S["af"], vec, srcs, C, csrc, cname)
        short = {so: (S["man"]["ksrc"][so], real[so]) for so in u["sources"] if real[so] != S["man"]["ksrc"][so]}
        say("  F_flat K%d: %s | F_bis s%d: %s; leaf counts below the target %s" % (s, H_kf[s].summary(), s, H_bis[s].summary(),
                                                                                  short or "none"))
    say("  vectors equal to the bundle's on %d items; GATE items with a routing row %d (modal AF leaf)" % (nb, len(gits)))
    labels = {}
    for m, so in u["members"]:
        if so in S["single"]:
            continue
        snap = GB.last_snapshot(U.P("%s/%s/seed_42/dag_snapshots.jsonl" % (u["afu"], m)))
        for n in snap["nodes"]:
            labels["%s:%s" % (so, n["id"])] = str(n.get("label") or "")
    return dict(S, H_af=H_af, H_kf=H_kf, H_bis=H_bis, bis_cells=bis_cells, gits=gits, gcell=gcell, labels=labels, side=side)


def assemble(D, P_, gitems, Kg, gmeta, twins):
    """Data over the scored positions (TRAIN, EVAL) plus the key-complete GATE items; R1's twin items not kept."""
    Dt = Data()
    Dt.models = list(D.models)
    n0 = D.n
    Dt.items = list(D.items) + list(gitems)
    Dt.side = np.array(["E" if D.is_eval[k] else "T" for k in range(n0)] + ["G"] * len(gitems))
    Dt.Y = np.vstack([D.A, Kg]).astype(np.int64) if len(gitems) else D.A.astype(np.int64)
    Dt.comp = list(D.comp) + [gmeta[i][0] for i in gitems]
    Dt.src = list(D.src) + [gmeta[i][1] for i in gitems]
    Dt.keep = np.array([i not in twins for i in Dt.items], dtype=bool)
    Dt.H = {"AF": P_["H_af"]}
    afn = [D.tree_keys[g] for g in D.g_tree] + [P_["gcell"][i] for i in gitems]
    h = P_["H_af"]
    bad = sorted(set(n for n in afn if n not in h.idx or not h.leaf[h.idx[n]]))
    if bad:
        hit("REFUSE.HIER")
        refuse("[AP-R4] %d AF cell(s) are not filing leaves of the AF-U hierarchy (first %s)" % (len(bad), bad[:3]))
    Dt.node = {"AF": np.array([h.idx[n] for n in afn], dtype=np.int64)}
    Dt.member = [UCI.cell_member(n) for n in afn]
    for s in SEEDS:
        hk = P_["H_kf"][s]
        kn = [D.xkeys["K%d" % s][g] for g in D.groupings["x:K%d" % s][0]]
        Dt.H["KF%d" % s] = hk
        Dt.node["KF%d" % s] = np.array([hk.idx[n] for n in kn] + [-1] * len(gitems), dtype=np.int64)
        hb = P_["H_bis"][s]
        bn = [P_["bis_cells"][s][i] for i in D.items]
        Dt.H["BIS%d" % s] = hb
        Dt.node["BIS%d" % s] = np.array([hb.idx[n] for n in bn] + [-1] * len(gitems), dtype=np.int64)
    Dt.labels = dict(P_.get("labels", {}))
    Dt.majority = majority(h, [Dt.node["AF"][k] for k in range(n0) if not D.is_eval[k]],
                           ["%s/%s" % D.dom[k] for k in range(n0) if not D.is_eval[k]])
    return Dt


def majority(h, leaves, labels):
    """Fingerprint names: per node, the TRAIN-majority declared stratum (source/domain) of the TRAIN items below it (ties -> the
    smallest name) and its share."""
    A = anc_table(h)
    cnt = defaultdict(Counter)
    for lf, lab in zip(leaves, labels):
        for l in range(1, A.shape[0]):
            a = A[l][lf]
            if a >= 0:
                cnt[int(a)][lab] += 1
    out = {}
    for v, cn in cnt.items():
        top = min(k for k, x in cn.items() if x == max(cn.values()))
        out[h.names[v]] = (top, cn[top] / float(sum(cn.values())))
    return out


def write_export(c, fp, say):
    d = c["export_dir"]
    p = os.path.join(d, c["export_file"])
    txt = fingerprint_csv(fp)
    G = V.G
    G.write_once(p, txt)
    G.write_once(os.path.join(d, c["export_readme"]), (
        "ADAPTIVE-PROFILE fingerprints (DESCRIPTIVE, for the HF blog visual; not a capability claim, not tree-robust).\n"
        "One row per (model, AF-U node): offset vs parent and path offset (logits, TRAIN fit, empirical-Bayes shrunk), SE, two-sided p,\n"
        "certified (BH q 0.05 within the sibling family), sign, TRAIN / EVAL item counts, EVAL observed accuracy and the mean predicted\n"
        "probability at the node. Node names: the AF-U snapshot node id; snapshot_label and the TRAIN-majority declared stratum beside.\n"
        "No item text; relative to these 18 models (Meta-Llama-3-70B-Instruct excluded). Never committed; sha256 %s.\n"
        % hashlib.sha256(txt.encode("utf-8")).hexdigest()))
    say("EXPORT written write-once: %s (sha256 %s; %d rows)" % (p, hashlib.sha256(txt.encode("utf-8")).hexdigest(), len(fp)))
    hit("EXPORT.WRITTEN")


def train_denoms(K_tr, train_meta, models):
    """R-1 (POSTRUN_ADAPTIVE-PROFILE): the scored TRAIN items (key-complete: build_ud's own rule, V.complete_items) and their CK-CLOSE
    components COUNTED FROM THE DATA (= len(set(D.comp[k] for k in D.T)) of the D build_ud would return: D.comp is train_meta's
    component over the same items), independent of PRECONDITIONS train_unit (ruling 3, "item", left as of record: AP never resamples
    TRAIN). Runs on the TRAIN key alone, i.e. BEFORE the eval view opens and before the write-once marker (R-4)."""
    tr = V.complete_items(K_tr, models)
    return len(tr), len(set(train_meta[i][0] for i in tr))


def structural_train(cfg, say):
    """R-3 / R-4: the dry-run's TRAIN denominator, structural and pre-key (no key column is selected): TRAIN items of the gen view
    whose every ACTIVE cell is usable under the variant rule BEFORE the key is read (V.structurally_complete; under UNUSABLE_CELL:
    one response per cell), and their components, from the data."""
    rule = cfg.pre.get("variant_rule")
    tw, gsha = V.open_tw("gen", "policy_fit", cfg.gen_path, cfg.gen_sha, "gen_view(TRAIN structure)", say)
    try:
        models = sorted(m for m, s_ in V.registry(tw, cfg.cv_u).items() if s_ == "ACTIVE")
        meta = V.side_items(tw, cfg.cv_u, "TRAIN")
        ok = V.structurally_complete(V.cell_counts(tw, "response_lite", cfg.cv_u, models, meta), models, rule)
    finally:
        tw.close()
    if not V.after_sha(cfg.gen_path, gsha, "gen_view(TRAIN structure)", say):
        refuse("[PIN] the gen view's sha moved during the structural TRAIN count")
    return len(ok), len(set(meta[i][0] for i in ok))


def check_train(n_items, n_comp, c, say, how):
    """[AP-DENOM] TRAIN, the one form both modes use (R-1 / R-4): items and components counted from the data, never train_units."""
    say("TRAIN DENOMINATOR (%s; counted from the data; before the marker and any EVAL read): %d items / %d components (registered"
        " %d / %d)" % (how, n_items, n_comp, c["n_train"], c["comp_train"]))
    if (n_items, n_comp) != (c["n_train"], c["comp_train"]):
        hit("REFUSE.DENOM")
        refuse("[AP-DENOM] TRAIN %d items / %d components, not the registered %d / %d" % (n_items, n_comp, c["n_train"],
                                                                                           c["comp_train"]))


def dry_run(out=print):
    say = out
    U.header(say, TEST_ID, "--dry-run", REG_TEXT, files())
    say("DEVIATION HEADER (printed by --run into the outcome file, verbatim): " + DEVIATION_LINE)
    load_h(reg(), say)
    denominators(say)
    P_ = prepare(say)
    tw = r1_block(say)
    by = Counter(P_["side"][i][1] for i in tw if i in P_["side"])
    say("  R1 twin items by split side (all items of the split): %s (--run REFUSES if any is a scored EVAL item)" % dict(sorted(by.items())))
    cfg = UAR._VDC_CFG[0]()
    cfg.policy_path = U.P(UAR.reg()["policy"])
    U.read_views(cfg, say, True, P_["af"], P_["kx"], reg()["marker"], None, refuse, hit, tag=TEST_ID)
    check_train(*structural_train(cfg, say), reg(), say, "structural, pre-key")
    say("OUTPUTS (write-once, never committed): %s, %s; export %s/%s" % (reg()["out"], reg()["marker"], reg()["export_dir"],
                                                                          reg()["export_file"]))
    say("DRY-RUN: nothing written; no key read (TRAIN, GATE or EVAL); no statistic printed.")
    hit("DRY.DONE")
    return 0


def run(out=print):
    c = reg()
    lines = []

    def say(s_):
        lines.append(s_)
        out(s_)
    U.header(say, TEST_ID, "--run", REG_TEXT, files())
    say(DEVIATION_LINE)
    say(DEVIATION_AUTH)
    exp = [os.path.join(c["export_dir"], c["export_file"]), os.path.join(c["export_dir"], c["export_readme"])]
    for p in [U.P(c["out"]), U.P(c["marker"])] + exp:
        if os.path.exists(p):
            hit("REFUSE.WRITE_ONCE")
            refuse("%s exists (write-once); refused before any read" % p)
    htab = load_h(c, say)
    denominators(say)
    P_ = prepare(say)
    twins = r1_block(say)
    cfg = UAR._VDC_CFG[0]()
    cfg.policy_path = U.P(UAR.reg()["policy"])
    gk = {}

    tw_side = sorted(i for i in twins if P_["side"].get(i, (None, None))[1] == "EVAL" and
                     P_["af"].get(i, V.NO_ROUTING_ROW) != V.NO_ROUTING_ROW)

    def between(K_tr, train_meta, models):
        # R1 ruling (registrar 2026-10-08, prog L25217): an EVAL-side twin item is dropped and counted, never refused on; the
        # refusal is iff a twin is among the SCORED EVAL items, decided after the read and before any fit (below).
        if tw_side:
            hit("R1.EVAL_SIDE")
        say("R1 EVAL-side twin items with an AF cell (pre-read count): %d; dropped and counted, not refused on (R1 ruling: refused"
            " iff a twin is among the SCORED EVAL items, checked after the read, before any fit)" % len(tw_side))
        # R-4: every denominator check that needs no EVAL data runs HERE, after the TRAIN / GATE keys and before the eval view
        # opens and the write-once marker is written (the TRAIN one counted from the data, R-1)
        check_train(*train_denoms(K_tr, train_meta, models), c, say, "key-complete")
        gk["K"], gk["comp"], gk["meta"] = EC.gate_key(cfg, say, models, P_["gits"])
        gk["items"] = sorted(i for i in gk["comp"] if i in P_["gcell"])
        if len(gk["items"]) != int(c["n_gate_key"]):
            hit("REFUSE.GATE_DENOM")
            refuse("[AP-GATE-DENOM] %d key-complete GATE items with a cell, not the registered %d" % (len(gk["items"]), c["n_gate_key"]))
    with Scorer(htab) as sc:
        D, ok_sha = U.read_views(cfg, say, False, P_["af"], P_["kx"], c["marker"],
                                 "ADAPTIVE-PROFILE: the EVAL key read started (one read).", refuse, hit, between=between, tag=TEST_ID)
    KH_tr, KH_g, KH_ev = scorer_keys(sc.calls, gk["K"])
    say("MATH SCORER (AP-R17, D-2026-10-08-5): the key reads TRAIN / GATE / EVAL through the pinned read_key with overlay OFF"
        " (official is_correct, of record); overlay rows read 0 / 0 / 0")
    U.check_denominators(D, c, refuse, hit, "AP")       # EVAL: needs the EVAL key (TRAIN and GATE were checked before the marker)
    gitems = gk["items"]
    if set(gitems) & set(D.items):
        hit("REFUSE.GATE_SIDE")
        refuse("[AP-GATE-SIDE] %d GATE item(s) are among the scored TRAIN / EVAL items" % len(set(gitems) & set(D.items)))
    tw_e = sorted(set(D.items[k] for k in D.E) & twins)
    tw_t = sorted(set(D.items[k] for k in D.T) & twins)
    tw_g = sorted(set(gitems) & twins)
    say("R1 on the scored sets: twin items dropped TRAIN %d, GATE %d; among the %d scored EVAL items %d" % (len(tw_t), len(tw_g), D.n_eval, len(tw_e)))
    say("R1 EVAL-side twin items NOT scored (outside the %d; dropped and counted): %d" % (D.n_eval, len(set(tw_side) - set(tw_e))))
    if tw_e:                                       # the R1 ruling's refusal: a twin among the SCORED EVAL items; before any fit
        hit("REFUSE.TWIN_EVAL")
        refuse("[R1-EVAL] %d scored EVAL item(s) are R1 twins (first %s): the R1 ruling (prog L25217) refuses iff a twin is among the"
               " scored EVAL items; a failed precondition, refused before any fit" % (len(tw_e), tw_e[:3]))
    Kg = np.array([[gk["K"][i][m] for m in D.models] for i in gitems], dtype=np.int64)
    say("  scored: TRAIN %d (%d components), GATE %d, EVAL %d (%d components); TRAIN kept after R1 %d" % (
        D.n_train, len(set(D.comp[k] for k in D.T)), len(gitems), D.n_eval, D.eval_units["n_units"], D.n_train - len(tw_t)))
    Dt = assemble(D, P_, gitems, Kg, gk["meta"], twins)
    st = core(Dt, c)
    L, words = all_lines(st, c)
    # AP-R18: the H sensitivity line (descriptive); the same positions, H on the MATH cells of TRAIN, GATE and EVAL
    A_H = np.array([[(KH_ev if D.is_eval[k] else KH_tr)[i][m] for m in D.models] for k, i in enumerate(D.items)],
                   dtype=np.int64).reshape(D.n, len(D.models))
    Kg_H = np.array([[KH_g[i][m] for m in D.models] for i in gitems], dtype=np.int64).reshape(len(gitems), len(D.models))
    D_H = copy.copy(D)
    D_H.A = A_H
    st_H = core(assemble(D_H, P_, gitems, Kg_H, gk["meta"], twins), c)
    L += h_lines(st_H, D, A_H, Kg.reshape(len(gitems), len(D.models)), Kg_H, c, sc.calls)
    for ln in L:
        say(ln)
    U.write_outcome(c["out"], "\n".join(lines) + "\n", ok_sha, refuse, out)
    write_export(c, st["fp"], out)
    hit("RUN.DONE")
    return dict(st=st, words=words, D=D, Dt=Dt, st_H=st_H)


def main(argv=None, out=print):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    gr = ap.add_mutually_exclusive_group(required=True)
    gr.add_argument("--selftest", action="store_true")
    gr.add_argument("--mutants", action="store_true")
    gr.add_argument("--dry-run", action="store_true")
    gr.add_argument("--run", action="store_true")
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--data-root", default=None, help="the checkout whose results / views / caches are read (set before any import)")
    a = ap.parse_args(argv)
    if a.selftest:
        selftest(only=a.only)
        return 0
    if a.mutants:
        return run_mutants(only=a.only)
    if any(os.environ.get(v) != "1" for v in THREAD_VARS):
        refuse("OMP / OPENBLAS / MKL must be 1")
    if a.dry_run:
        return dry_run(out=out)
    run(out=out)
    return 0


# ══ SELFTEST ══════════════════════════════════════════════════════════════════════════════════════════════════════════

import re            # noqa: E402
import contextlib    # noqa: E402

BRANCHES = ("AP1.PAYS", "AP1.TOO_SMALL", "AP1.UNDETERMINED", "AP2.BETTER", "AP2.WORSE", "AP2.PARITY", "AP2.NEITHER", "AP3.BETTER",
            "AP3.WORSE", "AP3.PARITY", "AP3.NEITHER", "AP4.BETTER", "AP4.WORSE", "AP4.PARITY", "AP4.NEITHER", "FAP.FIRED", "FAP.NOT",
            "R8.AP1.REFUTED", "R8.AP1.NOT", "R8.SIGN.FAILS", "R8.SIGN.NOT", "PRED.HELD", "PRED.FAILED", "P5.TRUE", "P5.FALSE",
            "P7.TRUE", "P7.FALSE", "P8.TRUE", "P8.FALSE", "P9.UNSCORED", "SUB.SCORED", "SUB.EMPTY", "RUN.DONE", "DRY.DONE",
            "EXPORT.WRITTEN", "MARKER.WRITTEN", "REFUSE.WRITE_ONCE", "REFUSE.POOL", "REFUSE.POLICY_SHA", "REFUSE.DENOM",
            "REFUSE.GATE_DENOM", "REFUSE.TWINS", "REFUSE.TWIN_EVAL", "R1.EVAL_SIDE", "REFUSE.HIER", "REFUSE.CONVERGE", "REFUSE.BIS", "REFUSE.NOCELL",
            "REFUSE.H_PIN", "REFUSE.H_JOIN", "REFUSE.SCORER", "H.LINE")
need = U.need


def _me():
    return types.SimpleNamespace(_REG=_REG, REG=REG, FIXTURE_REG=FIXTURE_REG)


# ── a synthetic union (core-level planted / null cases) ─────────────────────────────────────────────────────────────────────

def _syn_hier():
    """AF: union -> S1 root -> (a -> a1, a2), (b -> b1, b2); union -> S2 root -> c1, c2; pseudo leaves."""
    names = [UNION, "S1:r", "S1:a", "S1:b", "S1:a1", "S1:a2", "S1:b1", "S1:b2", "S2:r", "S2:c1", "S2:c2"]
    parents = [None, UNION, "S1:r", "S1:r", "S1:a", "S1:a", "S1:b", "S1:b", UNION, "S2:r", "S2:r"]
    leaves = {"S1:a1", "S1:a2", "S1:b1", "S1:b2", "S2:c1", "S2:c2"}
    names += list(PSEUDO)
    parents += [UNION, UNION]
    leaves |= set(PSEUDO)
    return TB.Hier("AF syn", names, parents, leaves)


SYN_LEAVES = ("S1:a1", "S1:a2", "S1:b1", "S1:b2", "S2:c1", "S2:c2")
SYN_PLANT = {(3, "S1:a1"): 1.2, (3, "S1:a2"): 1.2, (5, "S1:b2"): -1.4, (7, "S2:c1"): 1.0, (1, "S1:a1"): 1.2, (1, "S1:a2"): 1.2}


def _syn_data(planted=True, seed=17, M=12, n_tr=700, n_ga=60, n_ev=260):
    """n_tr / n_ga / n_ev items per leaf; components: pairs of consecutive EVAL items share a component 1 time in 4."""
    rs = np.random.RandomState(seed)
    h = _syn_hier()
    th = np.linspace(-1.2, 1.2, M)
    items, side, leaf, comp, src = [], [], [], [], []
    for lf in SYN_LEAVES:
        for sd, n in (("T", n_tr), ("G", n_ga), ("E", n_ev)):
            for j in range(n):
                items.append("%s/%s/%d" % (lf, sd, j))
                side.append(sd)
                leaf.append(lf)
                comp.append("c:%s/%s/%d" % (lf, sd, j - 1 if (sd == "E" and j % 4 == 1) else j))
                src.append(lf.split(":")[0])
    n = len(items)
    b = rs.normal(0, 1.0, n)
    off = np.zeros((n, M))
    if planted:
        for (m, lf), x in SYN_PLANT.items():
            if m < M:
                off[[k for k in range(n) if leaf[k] == lf], m] += x
    Y = (rs.rand(n, M) < expit(th[None, :] + off - b[:, None])).astype(np.int64)
    Dt = Data()
    Dt.models = ["m%02d" % m for m in range(M)]
    Dt.items, Dt.side, Dt.Y, Dt.comp, Dt.src = items, np.array(side), Y, comp, src
    Dt.keep = np.ones(n, dtype=bool)
    Dt.keep[[1, 2]] = False                                     # two R1 twin TRAIN items
    Dt.H = {"AF": h}
    Dt.node = {"AF": np.array([h.idx[x] for x in leaf], dtype=np.int64)}
    Dt.member = [x.split(":")[0] for x in leaf]
    for s in SEEDS:
        # F_flat: per source two random cells; F_bis: per source a binary tree over 3 leaves, items filed at random
        cells = ["K%d:%s:%03d" % (s, src[k], int(rs.randint(2))) for k in range(n)]
        hk = kflat_hier(s, cells)
        Dt.H["KF%d" % s] = hk
        Dt.node["KF%d" % s] = np.array([hk.idx[x] if side[k] != "G" else -1 for k, x in enumerate(cells)], dtype=np.int64)
        nm, pa, lv = [UNION], [None], set()
        for so in ("S1", "S2"):
            nm += ["B%d:%s:r" % (s, so), "B%d:%s:n000" % (s, so), "B%d:%s:000" % (s, so), "B%d:%s:001" % (s, so), "B%d:%s:002" % (s, so)]
            pa += [UNION, "B%d:%s:r" % (s, so), "B%d:%s:n000" % (s, so), "B%d:%s:n000" % (s, so), "B%d:%s:r" % (s, so)]
            lv |= {"B%d:%s:00%d" % (s, so, j) for j in range(3)}
        nm += list(PSEUDO)
        pa += [UNION, UNION]
        lv |= set(PSEUDO)
        hb = TB.Hier("F_bis syn", nm, pa, lv)
        Dt.H["BIS%d" % s] = hb
        Dt.node["BIS%d" % s] = np.array([hb.idx["B%d:%s:%03d" % (s, src[k], int(rs.randint(3)))] if side[k] != "G" else -1
                                         for k in range(n)], dtype=np.int64)
    Dt.labels = {}
    Dt.majority = majority(h, [Dt.node["AF"][k] for k in range(n) if side[k] == "T"], [leaf[k] for k in range(n) if side[k] == "T"])
    Dt.leaf = leaf
    return Dt


def _syn_c(**over):
    return dict(REG, **dict(dict(B_ap=300), **over))


# ── the fixture (union_af_route's, deepened MMLU_PRO tree as TREE-BACKOFF's; responses re-drawn from a planted 1PL) ────────

FX_PLANT = {("u01", "MMLU_PRO:mA"): 1.6, ("u04", "MMLU_PRO:mB"): -1.6, ("u06", "MMLU_PRO:L0"): 1.6, ("u07", "MMLU_PRO:L1"): -1.6,
            ("u02", "MATH:root"): 1.0, ("u03", "@BBH"): -1.0}


def _fx_cells(lay):
    man = json.load(open(os.path.join(lay.tmp, "res", "inputs", "inputs_manifest.json"), encoding="utf-8"))
    af, _ = V.load_tree_cells(os.path.join(lay.tmp, "res", "inputs", "af_cells.tsv"), man["inputs"]["res/inputs/af_cells.tsv"])
    with UAR._patched(lay.fx):
        gc = TB._o_gate_cells(lay.tmp)
    return af, gc


def _fx_redraw(lay, plant, seed=29):
    """Every mc6 response of the fixture re-drawn from P = expit(theta_m + sum of the planted offsets on the item's AF path - b_i);
    duplicate rows of a cell carry the same value (the cell stays unusable as before); no MATH-FIX overlay."""
    af, gc = _fx_cells(lay)
    _mu, _K, _man, _af, par, _tr = TB._o_af(lay)
    bbh = sorted(set(c for c in af.values() if c.startswith("BBH")))[0]
    rs = np.random.RandomState(seed)
    mu = sorted(lay.fx.spec["models_u"])
    th = dict(zip(mu, np.linspace(-1.0, 1.0, len(mu))))
    items = sorted(set(r["item"] for r in lay.fx.spec["responses"] if r["cv"] == "mc6"))
    b = dict(zip(items, rs.normal(0, 0.7, len(items))))
    pl = {(m, bbh if n == "@BBH" else n): x for (m, n), x in plant.items()}

    def path(cell):
        out, a = [], cell
        while a is not None:
            out.append(a)
            a = par.get(a)
        return out
    val = {}
    for i in items:
        cell = af.get(i) or gc.get(i)
        nodes = path(cell) if cell else []
        for m in mu:
            off = sum(pl.get((m, n), 0.0) for n in nodes)
            val[(i, m)] = int(rs.rand() < expit(th[m] + off - b[i]))
    spec = copy.deepcopy(lay.fx.spec)
    for r in spec["responses"]:
        if r["cv"] == "mc6":
            r["c"], r["mf"] = val[(r["item"], r["model"])], None
    lay.fx.spec = spec
    return af, gc, par


def _qid_map(spec):
    """A stable legacy_qid per mc6 (item, model): the real views carry eval_results.question_id in both views; the fixture's _mk_view
    numbers the rows per view, so the selftest re-stamps them (below) before the seal."""
    keys = sorted(set((r["item"], r["model"]) for r in spec["responses"] if r["cv"] == "mc6"))
    return {k: 10000000 + j for j, k in enumerate(keys)}


@contextlib.contextmanager
def _stable_qids():
    """The fixture views with _qid_map's legacy_qid on the mc6 rows (an UPDATE before v2_declared_cells._mk_view's seal)."""
    orig_mk, orig_seal = V._mk_view, V.dv2ro.seal

    def mk(path, kind, sides, sp):
        rt = "response_lite" if kind == "gen" else "response"
        q = _qid_map(sp)

        def seal(conn, p, label):
            conn.executemany("UPDATE %s SET legacy_qid=? WHERE corpus_version='mc6' AND item_id=? AND model=?" % rt,
                             [(v, i, m) for (i, m), v in q.items()])
            return orig_seal(conn, p, label)
        V.dv2ro.seal = seal
        try:
            return orig_mk(path, kind, sides, sp)
        finally:
            V.dv2ro.seal = orig_seal
    V._mk_view = mk
    try:
        yield
    finally:
        V._mk_view = orig_mk


def _h_csv(hfx):
    return "question_id,model,H,route\n" + "".join("%d,%s,%d,%s\n" % (q, m, h, r) for (q, m), (h, r) in sorted(hfx.items()))


def _put_h(tmp, rel, hfx):
    """Writes a fixture H table (LF bytes) under tmp -> its sha256."""
    txt = _h_csv(hfx)
    p = os.path.join(tmp, *rel.split("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(txt)
    return hashlib.sha256(txt.encode("utf-8")).hexdigest()


def _fx_math(lay, seed=31):
    """MATH-FIX overlay values that DIFFER from the official on about a third of the mc6 MATH cells (an overlay leak moves the
    official numbers), and the fixture's H table: H = 1 'imported' where the official is 1; else H = 1 'boxed:str' on about half
    the cells, H = 0 'none' on the rest. lay.common carries the table's path, sha and row count."""
    rs = np.random.RandomState(seed)
    q = _qid_map(lay.fx.spec)
    hfx, mfd = {}, {}
    for r in lay.fx.spec["responses"]:
        if r["cv"] != "mc6" or r["src"] != MATH_SRC:
            continue
        key = (q[(r["item"], r["model"])], r["model"])
        if key not in hfx:
            hfx[key] = (1, "imported") if r["c"] == 1 else ((1, "boxed:str") if rs.rand() < 0.5 else (0, "none"))
            mfd[key] = (1 - r["c"]) if rs.rand() < 0.35 else None
        r["mf"] = mfd[key]
    lay.hfx = hfx
    rel = "res/h/math_h_table.csv"
    lay.common = dict(lay.common, h_table=rel, h_sha=_put_h(lay.tmp, rel, hfx), h_rows=len(hfx))


def build_base(tmp, plant=None):
    """union_route_common.build_layout with TREE-BACKOFF's deepened MMLU_PRO tree; responses re-drawn (planted unless plant == {});
    the registered constants this script checks, read off the fixture; R1 twins: two scored TRAIN items, one GATE item and one
    UNSCORED EVAL-side item with an AF cell (key-incomplete; the R1 ruling: dropped and counted, never refused on)."""
    real = UAR._fixture
    UAR._fixture = TB._deep_fixture(real)
    try:
        lay = U.build_layout(tmp)
    finally:
        UAR._fixture = real
    af, gc, par = _fx_redraw(lay, FX_PLANT if plant is None else plant)
    mu, K, _man, _af, _par, tr = TB._o_af(lay)
    gk = TB._o_gate_key(lay.fx.spec, sorted(gc))
    tr = [i for i in tr if i in K]
    mu_, val_ = U.o_key(lay.fx.spec)
    Kf = TB.val_k(val_, mu_)
    uns = sorted(i for i, (_c, s) in lay.fx.side.items() if s == "EVAL" and i in af and i not in Kf)
    assert uns, "the fixture has no unscored EVAL-side item with an AF cell"
    lay.twin_items = [tr[5], tr[40], sorted(gk)[3], uns[0]]   # + an UNSCORED EVAL-side twin: dropped and counted, never refused
    lay.common = dict(lay.common, n_gate_key=len(gk), n_train=len(tr), comp_train=len(set(lay.fx.side[i][0] for i in tr)),
                      twins=(4, 3), B_ap=200, export_dir=os.path.join(lay.tmp, "export"))
    lay.af, lay.gc, lay.par = af, gc, par
    # L-1 (READY_ADAPTIVE-PROFILE_delta3, R03): the real registry carries non-ACTIVE models; the fixture's mc6 registry gets one
    # (no responses), so a roster taken from the whole registry instead of the ACTIVE rows changes the structural TRAIN count
    assert all(s_ == "ACTIVE" for cv, _m, s_ in lay.fx.spec["registry"] if cv == "mc6") and V.EXCLUDED not in lay.fx.spec["models_u"]
    lay.fx.spec["registry"].append(("mc6", V.EXCLUDED, "EXCLUDED"))
    _fx_math(lay)
    return lay


def clone(lay, dest):
    new = U.clone(lay, dest)
    new.fx.spec = lay.fx.spec
    new.common = dict(lay.common, export_dir=os.path.join(dest, "export"))
    new.af, new.gc, new.par, new.twin_items, new.hfx = lay.af, lay.gc, lay.par, lay.twin_items, lay.hfx
    return new


@contextlib.contextmanager
def _twins(lay, ids=(101, 102, 103, 104), ntx=3, items=None):
    saved = _IO["twins"]
    _IO["twins"] = lambda: (list(ids), ntx, list(lay.twin_items if items is None else items))
    try:
        yield
    finally:
        _IO["twins"] = saved


@contextlib.contextmanager
def _unit(lay, unit=None):
    """R-2 (POSTRUN_ADAPTIVE-PROFILE claim 3): the fixture cfg (v2_declared_cells._fixture_cfg, pinned) carries train_unit
    "component" while the run of record carries PRECONDITIONS' "item" (ruling 3); every fixture run here gets the REAL unit unless
    `unit` names another (read lazily by union_af_route._patched through fx.cfg_factory)."""
    unit = V.PRECONDITIONS["train_unit"] if unit is None else unit
    f0 = lay.fx.cfg_factory

    def f():
        cfg = f0()
        cfg.pre = dict(cfg.pre, train_unit=unit)
        return cfg
    lay.fx.cfg_factory = f
    try:
        yield
    finally:
        lay.fx.cfg_factory = f0


def cap(fn, lay, items=None, unit=None, **over):
    with _twins(lay, items=items), _stable_qids(), _unit(lay, unit):
        return U.cap(_me(), fn, lay, **over)


# ── the INDEPENDENT oracle (plain loops, scipy optimisers; nothing above the SELFTEST marker is called) ──────────────────────

def _o_sig(x):
    return 1.0 / (1.0 + math.exp(-x))


def _o_rasch(Y, prior_var):
    """Joint MAP Rasch by scipy L-BFGS-B on the penalised negative log-likelihood (analytic gradient)."""
    from scipy.optimize import minimize
    n, k = Y.shape

    def f(x):
        th, b = x[:k], x[k:]
        eta = th[None, :] - b[:, None]
        nll = float(np.sum(np.logaddexp(0.0, eta) - Y * eta)) + float(np.sum(b * b)) / (2 * prior_var)
        r = 1.0 / (1.0 + np.exp(-eta)) - Y
        return nll, np.concatenate([r.sum(axis=0), -r.sum(axis=1) + b / prior_var])
    x0 = np.zeros(n + k)
    o = minimize(f, x0, jac=True, method="L-BFGS-B", options=dict(maxiter=100000, maxfun=200000, gtol=1e-9, ftol=1e-16, maxcor=50))
    x = o.x
    for _it in range(50):                                   # polish: joint (dense) Newton steps on the full Hessian
        g = f(x)[1]
        if float(np.abs(g).max()) < 1e-10:
            break
        th, b = x[:k], x[k:]
        p = 1.0 / (1.0 + np.exp(-(th[None, :] - b[:, None])))
        w = p * (1 - p)
        H = np.zeros((n + k, n + k))
        H[np.arange(k), np.arange(k)] = w.sum(axis=0)
        H[k + np.arange(n), k + np.arange(n)] = w.sum(axis=1) + 1.0 / prior_var
        H[:k, k:] = -w.T
        H[k:, :k] = -w
        x = x - np.linalg.solve(H, g)
    g = f(x)[1]
    assert float(np.abs(g).max()) < 1e-9, ("oracle Rasch not converged", float(np.abs(g).max()))
    return x[:k], x[k:]


def _o_root(fn, lo=-30.0, hi=30.0):
    from scipy.optimize import brentq
    return brentq(fn, lo, hi, xtol=1e-14, rtol=1e-15, maxiter=500)


def _o_bh(ps, q):
    order = sorted(range(len(ps)), key=lambda j: ps[j])
    kmax = 0
    for r, j in enumerate(order, start=1):
        if ps[j] <= r * q / len(ps):
            kmax = r
    return set(order[:kmax])


class _OTree:
    """Parent map by names; depth by walking; children; path from depth 1."""

    def __init__(self, par, pseudo=()):
        self.par = dict(par)
        self.pseudo = set(pseudo)
        self.kids = defaultdict(list)
        for v, p in self.par.items():
            if p is not None:
                self.kids[p].append(v)

    def depth(self, v):
        d = 0
        while self.par[v] is not None:
            v = self.par[v]
            d += 1
        return d

    def path(self, leaf):
        memo = self.__dict__.setdefault("_memo", {})
        if leaf not in memo:
            out = []
            v = leaf
            while self.par[v] is not None:
                out.append(v)
                v = self.par[v]
            memo[leaf] = out[::-1]
        return memo[leaf]


def _o_fit(T, cell, items_tr, y, bm, th, mu):
    """Loop node fits: top-down by depth; tau^2 by moments (non-pseudo nodes, I > 0); posterior one step from the parent."""
    nodes = sorted(v for v in T.par if T.par[v] is not None)
    maxd = max(T.depth(v) for v in nodes)
    Dl = {(T.root, m): 0.0 for m in mu}
    out = {}
    tau = {}
    for l in range(1, maxd + 1):
        lev = [v for v in nodes if T.depth(v) == l]
        stat = {}
        for v in lev:
            for m in mu:
                U_ = I_ = 0.0
                for i in items_tr:
                    pth = T.path(cell[i])
                    if len(pth) >= l and pth[l - 1] == v:
                        p = _o_sig(th[m] + Dl[(T.par[v], m)] - bm[(i, m)])
                        U_ += y[(i, m)] - p
                        I_ += p * (1 - p)
                stat[(v, m)] = (U_, I_)
        vals = [(U_ / I_) ** 2 - 1.0 / I_ for (v, m), (U_, I_) in stat.items() if v not in T.pseudo and I_ > 0]
        t2 = max(0.0, sum(vals) / len(vals)) if vals else 0.0
        tau[l] = t2
        for (v, m), (U_, I_) in stat.items():
            if t2 > 0 and I_ > 0 and v not in T.pseudo:
                d_, se_ = U_ / (I_ + 1.0 / t2), (I_ + 1.0 / t2) ** -0.5
            else:
                d_, se_ = 0.0, float("nan")
            out[(v, m)] = (d_, se_)
            Dl[(v, m)] = Dl[(T.par[v], m)] + d_
    return out, Dl, tau


def _o_cert(T, fit, mu, q):
    cert = set()
    for par, kids in T.kids.items():
        for m in mu:
            fam = [v for v in kids if fit[(v, m)][1] == fit[(v, m)][1]]
            if not fam:
                continue
            if q is None:
                cert |= {(v, m) for v in fam}
                continue
            if len(fam) == 1 and q == 0.05:            # the registration's single-sibling threshold |z| > 1.96
                if abs(fit[(fam[0], m)][0] / fit[(fam[0], m)][1]) > 1.96:
                    cert.add((fam[0], m))
                continue
            ps = [math.erfc(abs(fit[(v, m)][0] / fit[(v, m)][1]) / math.sqrt(2)) for v in fam]
            cert |= {(fam[j], m) for j in _o_bh(ps, q)}
    return cert


def _o_stop(T, leaf, m, fit, cert, s_max):
    pth = T.path(leaf)
    v = pth[0]
    for c in pth[1:]:
        se_ = fit[(c, m)][1]
        if se_ == se_ and se_ < s_max and (c, m) in cert:
            v = c
        else:
            break
    return v


def _o_brier(items, mu, y, pfun):
    return sum(sum((y[(i, m)] - pfun(i, m)) ** 2 for m in mu) / len(mu) for i in items) / len(items)


def _o_keys(lay, use_h):
    """The fixture's key from its raw rows: the OFFICIAL c (never mf: D-2026-10-08-5), or (use_h) H on the MATH rows by the fixture's
    own H dict (not the CSV, not the script's join) -> (models, TRAIN/EVAL key-complete K, GATE key-complete gk)."""
    spec = lay.fx.spec
    q = _qid_map(spec)
    mu = sorted(spec["models_u"])
    vals, gv = defaultdict(list), defaultdict(list)
    for r in spec["responses"]:
        if r["cv"] != "mc6":
            continue
        v = lay.hfx[(q[(r["item"], r["model"])], r["model"])][0] if (use_h and r["src"] == MATH_SRC) else r["c"]
        (gv if r["side"] == "GATE" else vals)[(r["item"], r["model"])].append(v)
    K = TB.val_k({k: x[0] for k, x in vals.items() if len(x) == 1}, mu)
    gk = {i: {m: gv[(i, m)][0] for m in mu} for i in sorted(lay.gc) if all(len(gv.get((i, m), [])) == 1 for m in mu)}
    return mu, K, gk


def _oracle(lay, res, c, use_h=False):
    """Recomputes the deciding numbers from the fixture's raw rows, cells and snapshots with loops and scipy (official key, or H)."""
    fx, D, Dt = lay.fx, res["D"], res["Dt"]
    mu, K, gk = _o_keys(lay, use_h)
    af = lay.af
    tw = set(lay.twin_items)
    tr = sorted(i for i in K if fx.side[i][1] == "TRAIN" and i in af and i not in tw)
    ev = sorted(i for i in K if fx.side[i][1] == "EVAL" and i in af)
    assert ev == [D.items[k] for k in D.E], "the scored EVAL set differs from the loop reader's"
    ga = sorted(i for i in gk if i not in tw)
    y = {}
    for i in tr + ev:
        for m in mu:
            y[(i, m)] = K[i][m]
    for i in ga:
        for m in mu:
            y[(i, m)] = gk[i][m]
    allit = tr + ga + ev
    bm = {}
    for jm, m in enumerate(mu):
        others = [x for x in mu if x != m]
        Ym = np.array([[y[(i, x)] for x in others] for i in allit], dtype=np.float64)
        _t, b = _o_rasch(Ym, c["prior_var"])
        for j, i in enumerate(allit):
            bm[(i, m)] = float(b[j])
    th = {}
    for m in mu:
        th[m] = _o_root(lambda t: sum(y[(i, m)] - _o_sig(t - bm[(i, m)]) for i in tr))
    par = dict(lay.par)
    T = _OTree(par, PSEUDO)
    T.root = UNION
    cell = {i: af[i] for i in tr + ev}
    cell.update({i: lay.gc[i] for i in ga})
    fit, Dl, tau = _o_fit(T, cell, tr, y, bm, th, mu)
    cert = _o_cert(T, fit, mu, c["q"])
    stop = {(i, m): _o_stop(T, cell[i], m, fit, cert, c["s_max"]) for i in ev for m in mu}

    def at_depth(i, m, d):
        pth = T.path(cell[i])
        return pth[min(d, len(pth)) - 1]
    maxd = max(T.depth(v) for v in T.par if T.par[v] is not None)
    pr = lambda i, m, v: _o_sig(th[m] + Dl[(v, m)] - bm[(i, m)])     # noqa: E731
    br = dict(A=_o_brier(ev, mu, y, lambda i, m: pr(i, m, stop[(i, m)])), B=_o_brier(ev, mu, y, lambda i, m: _o_sig(th[m] - bm[(i, m)])))
    for d in range(1, maxd + 1):
        br["D%d" % d] = _o_brier(ev, mu, y, lambda i, m: pr(i, m, at_depth(i, m, d)))
    gate = [_o_brier(ga, mu, y, lambda i, m: pr(i, m, at_depth(i, m, d))) for d in range(1, maxd + 1)]
    dstar = 1 + min(range(maxd), key=lambda j: (gate[j], j))
    # E: unshrunk leaf MLE by brentq (clipped at +-5; the bracket [-5, 5])
    eo = {}
    for lf in set(cell[i] for i in ev):
        mem = [i for i in tr if cell[i] == lf]
        for m in mu:
            if not mem:
                eo[(lf, m)] = 0.0
                continue
            fn = lambda e: sum(y[(i, m)] - _o_sig(th[m] + e - bm[(i, m)]) for i in mem)    # noqa: E731
            eo[(lf, m)] = c["clip"] if fn(c["clip"]) > 0 else (-c["clip"] if fn(-c["clip"]) < 0 else _o_root(fn, -c["clip"], c["clip"]))
    br["E"] = _o_brier(ev, mu, y, lambda i, m: _o_sig(th[m] + eo[(cell[i], m)] - bm[(i, m)]))
    # F_flat from the k_cells files (2 levels: source node, cell); F_bis on the run's bisecting trees with loop fits and the rule
    man = json.load(open(os.path.join(lay.tmp, "res", "inputs", "inputs_manifest.json"), encoding="utf-8"))
    ff, fb, perF = [], [], {}
    for s in SEEDS:
        kc, _x = V.load_tree_cells(os.path.join(lay.tmp, "res", "inputs", "k_cells_s%d.tsv" % s), man["inputs"]["res/inputs/k_cells_s%d.tsv" % s])
        kp = {UNION: None}
        for x in PSEUDO:
            kp[x] = UNION
        for i in tr + ev:
            if kc[i] not in PSEUDO:
                kp["SRC%d:%s" % (s, kc[i].split(":")[1])] = UNION
                kp[kc[i]] = "SRC%d:%s" % (s, kc[i].split(":")[1])
        TK = _OTree(kp, PSEUDO)
        TK.root = UNION
        kcell = {i: kc[i] for i in tr + ev}
        fk, Dk, _tk = _o_fit(TK, kcell, tr, y, bm, th, mu)
        perF[("FF", s)] = {i: sum((y[(i, m)] - _o_sig(th[m] + Dk[(TK.path(kcell[i])[min(2, len(TK.path(kcell[i]))) - 1], m)] - bm[(i, m)])) ** 2
                                  for m in mu) / len(mu) for i in ev}
        hb = Dt.H["BIS%d" % s]
        bp = {hb.names[v]: (hb.names[int(hb.parent[v])] if hb.parent[v] >= 0 else None) for v in range(hb.N)}
        TBs = _OTree(bp, PSEUDO)
        TBs.root = UNION
        pos = {it: k for k, it in enumerate(Dt.items)}
        bcell = {i: hb.names[Dt.node["BIS%d" % s][pos[i]]] for i in tr + ev}
        fbf, Db, _tb = _o_fit(TBs, bcell, tr, y, bm, th, mu)
        cb = _o_cert(TBs, fbf, mu, c["q"])
        perF[("FB", s)] = {i: sum((y[(i, m)] - _o_sig(th[m] + Db[(_o_stop(TBs, bcell[i], m, fbf, cb, c["s_max"]), m)] - bm[(i, m)])) ** 2
                                  for m in mu) / len(mu) for i in ev}
        ff.append(sum(perF[("FF", s)].values()) / len(ev))
        fb.append(sum(perF[("FB", s)].values()) / len(ev))
    br["FF"], br["FB"] = sum(ff) / 5, sum(fb) / 5
    # the two-stage bootstrap replayed (components, then seeds; default_rng(boot_seed))
    perA = {i: sum((y[(i, m)] - pr(i, m, stop[(i, m)])) ** 2 for m in mu) / len(mu) for i in ev}
    perC = {i: sum((y[(i, m)] - pr(i, m, at_depth(i, m, 1))) ** 2 for m in mu) / len(mu) for i in ev}
    comps = sorted(set(fx.side[i][0] for i in ev))
    cix = {cc: j for j, cc in enumerate(comps)}
    rng = np.random.default_rng(c["boot_seed"])
    rc, rf = [], []
    for _b in range(c["B_ap"]):
        cnt = Counter(int(x) for x in rng.integers(0, len(comps), len(comps)))
        sd = [int(x) for x in rng.integers(0, 5, 5)]
        w = {i: cnt.get(cix[fx.side[i][0]], 0) for i in ev}
        tot = float(sum(w.values()))
        a_ = sum(w[i] * perA[i] for i in ev) / tot
        rc.append(sum(w[i] * perC[i] for i in ev) / tot - a_)
        rf.append(sum(sum(w[i] * perF[("FF", s)][i] for i in ev) / tot for s in sd) / 5.0 - a_)
    stops_depth = Counter(T.depth(stop[(i, m)]) for i in ev for m in mu)
    rng2 = np.random.default_rng(c["iid_seed"])
    ri = []
    for _b in range(c["B_ap"]):
        cnt = Counter(int(x) for x in rng2.integers(0, len(ev), len(ev)))
        tot = float(sum(cnt.values()))
        ri.append(sum(cnt.get(j, 0) * (perC[i] - perA[i]) for j, i in enumerate(ev)) / tot)
    sizes = Counter(fx.side[i][0] for i in ev)
    return dict(br=br, gate=gate, dstar=dstar, tau=tau, cert=cert, th=th, n_ev=len(ev), n_tr=len(tr), n_ga=len(ga),
                dc=br["D1"] - br["A"], dc_ci=tuple(float(x) for x in np.percentile(rc, [2.5, 97.5])), dc_sd=float(np.std(rc, ddof=1)),
                dff=br["FF"] - br["A"], dff_ci=tuple(float(x) for x in np.percentile(rf, [2.5, 97.5])), hist=stops_depth,
                below=sum(v for d, v in stops_depth.items() if d > 1) / float(len(ev) * len(mu)), fit=fit, Dl=Dl, maxd=maxd,
                deff=float(np.var(rc, ddof=1) / np.var(ri, ddof=1)), kish=sum(v * v for v in sizes.values()) / float(len(ev)))


# ── cases ───────────────────────────────────────────────────────────────────────────────────────────────────────────────

def _close(a, b, tol, what):
    if not abs(a - b) <= tol:
        raise AssertionError("%s: %r vs %r (tol %g)" % (what, a, b, tol))


def st_irt():
    rs = np.random.RandomState(3)
    Y = (rs.rand(150, 6) < expit(np.linspace(-1, 1, 6)[None, :] - rs.normal(0, 1, 150)[:, None])).astype(np.float64)
    Y[0] = 1.0
    Y[1] = 0.0                                                 # an all-correct and an all-wrong item: the prior keeps b finite
    th, b, _it = rasch_map(Y, 4.0)
    oth, ob = _o_rasch(Y, 4.0)
    assert float(np.abs(th - oth).max()) < 1e-6 and float(np.abs(b - ob).max()) < 1e-6, "rasch_map differs from the scipy MAP"
    Yi = Y.astype(np.int64)
    keep = np.ones(150, dtype=bool)
    keep[7] = False
    B1, _s = lomo_b(Yi, keep, 4.0)
    assert np.isnan(B1[7]).all() and not np.isnan(B1[keep]).any()
    _t, b0 = _o_rasch(Y[keep][:, 1:], 4.0)
    assert float(np.abs(B1[keep, 0] - b0).max()) < 1e-6, "LOMO column 0 is not the fit on models 1..5"
    Y2 = Yi.copy()
    Y2[:, 2] = 1 - Y2[:, 2]
    B2, _s = lomo_b(Y2, keep, 4.0)
    assert float(np.abs(B2[keep, 2] - B1[keep, 2]).max()) < 1e-9, "the target model's own answers moved its LOMO difficulties"
    assert float(np.abs(B2[keep, 0] - B1[keep, 0]).max()) > 1e-3, "another model's answers did not move the difficulties"
    rows = np.flatnonzero(keep)
    t = theta_fit(Y, B1, rows)
    for m in range(6):
        o = _o_root(lambda x: sum(Y[i, m] - _o_sig(x - B1[i, m]) for i in rows))
        _close(float(t[m]), o, 1e-8, "theta_fit model %d" % m)
    # leaf MLE: three leaves, one all-correct for model 0 (-> +clip), one all-wrong for model 1 (-> -clip), one empty (0)
    node = np.array([0] * 40 + [1] * 40 + [2] * 70, dtype=np.int64)
    Yl = Yi.copy()
    Yl[:40, 0] = 1
    Yl[40:80, 1] = 0
    tr = np.ones(150, dtype=bool)
    tr[80:] = False
    e = leaf_mle(node, tr, Yl.astype(np.float64), np.nan_to_num(B1), t, 4, 5.0)
    assert e[0, 0] == 5.0 and e[1, 1] == -5.0 and (e[2] == 0).all() and (e[3] == 0).all(), e[:, :2]
    for lf, m in ((0, 2), (1, 3), (0, 5)):
        mem = [i for i in range(80) if node[i] == lf]
        o = _o_root(lambda x: sum(Yl[i, m] - _o_sig(t[m] + x - np.nan_to_num(B1)[i, m]) for i in mem), -5, 5)
        _close(float(e[lf, m]), o, 1e-9, "leaf MLE (%d, %d)" % (lf, m))
    try:
        rasch_map(Y, 4.0, maxit=1)
        raise AssertionError("a non-converged Rasch fit was not refused")
    except SystemExit as ex:
        assert "did not converge" in str(ex)


def _small_fit_case(seed=5):
    Dt = _syn_data(planted=True, seed=seed, M=6, n_tr=120, n_ga=10, n_ev=30)
    Dt.node["AF"] = Dt.node["AF"].copy()
    Dt.node["AF"][np.flatnonzero(Dt.side == "T")[:15]] = Dt.H["AF"].idx[PSEUDO[0]]     # TRAIN items on a pseudo-leaf (no moments)
    Y = Dt.Y.astype(np.float64)
    tr = (Dt.side == "T") & Dt.keep
    Bm, _s = lomo_b(Dt.Y, Dt.keep, 4.0)
    th = theta_fit(Y, Bm, np.flatnonzero(tr))
    return Dt, Y, tr, Bm, th


def st_nodes():
    Dt, Y, tr, Bm, th = _small_fit_case()
    h = Dt.H["AF"]
    nd = Dt.node["AF"]
    fit = node_fit(h, nd, tr, Y, Bm, th)
    mu = list(range(len(Dt.models)))
    par = {h.names[v]: (h.names[int(h.parent[v])] if h.parent[v] >= 0 else None) for v in range(h.N)}
    T = _OTree(par, PSEUDO)
    T.root = UNION
    cell = {k: h.names[nd[k]] for k in range(len(Dt.items))}
    trk = [k for k in range(len(Dt.items)) if tr[k]]
    y = {(k, m): Y[k, m] for k in range(len(Dt.items)) for m in mu}
    bm = {(k, m): Bm[k, m] for k in range(len(Dt.items)) for m in mu if Dt.keep[k]}
    o, oD, otau = _o_fit(T, cell, trk, y, bm, dict(enumerate(th)), mu)
    for l, t2 in otau.items():
        _close(fit["tau2"][l], t2, 1e-10, "tau^2 depth %d" % l)
    assert any(t2 > 0 for t2 in otau.values()) and len(otau) == 3
    for (v, m), (d_, se_) in o.items():
        j = h.idx[v]
        _close(float(fit["d"][j, m]), d_, 1e-10, "d %s %d" % (v, m))
        assert (np.isnan(fit["se"][j, m]) and se_ != se_) or abs(fit["se"][j, m] - se_) < 1e-10, (v, m)
        _close(float(fit["Delta"][j, m]), oD[(v, m)], 1e-10, "Delta %s %d" % (v, m))
    for q in (0.05, 0.10, None):
        cert, _p = certify(fit, q)
        oc = _o_cert(T, o, mu, q)
        got = set((h.names[v], m) for v in range(h.N) for m in mu if cert[v, m])
        assert got == oc, ("certify differs from the loop BH", q, sorted(got ^ oc))
        for s_max in (0.10, 0.20, INF):
            E = np.flatnonzero(Dt.side == "E")
            stp = stops_rule(fit, nd[E], s_max, cert)
            for jj, k in enumerate(E):
                for m in mu:
                    assert h.names[stp[jj, m]] == _o_stop(T, cell[k], m, o, oc, s_max), (k, m, q, s_max)
    E = np.flatnonzero(Dt.side == "E")
    for dd in (1, 2, 3, 4):
        sd_ = stops_depth(fit, nd[E], dd, len(mu))
        for jj, k in enumerate(E):
            pth = T.path(cell[k])
            assert h.names[sd_[jj, 0]] == pth[min(dd, len(pth)) - 1]
    # hand cases: a single-sibling family (|z| 1.97 certified, 1.95 not); no skipping past an uncertified child; SE at s_max
    hh = TB.Hier("hand", [UNION, "r", "a", "a1", "b"], [None, UNION, "r", "a", "r"], {"a1", "b"})
    for z, want in ((1.97, True), (1.95, False), (-1.97, True)):
        f = dict(h=hh, d=np.array([[0.0], [0.5], [z * 0.1], [0.0], [0.0]]), se=np.array([[np.nan], [0.1], [0.1], [np.nan], [np.nan]]),
                 ch=children_of(hh), A=anc_table(hh))
        cc, _p = certify(f, 0.05)
        assert bool(cc[2, 0]) is want, ("single-sibling BH at |z| %.2f" % z, cc[:, 0])
    # L-1: the registered single-sibling threshold is STRICT |z| > 1.96 (not p <= 0.05, i.e. not |z| >= 1.959964); SE 0.5 keeps z exact
    for dv, q_, want in ((0.97999, 0.05, False), (0.98, 0.05, False), (0.98005, 0.05, True), (-0.98005, 0.05, True),
                         (0.85, 0.10, True), (0.80, 0.10, False)):
        f = dict(h=hh, d=np.array([[0.0], [0.5], [dv], [0.0], [0.0]]), se=np.array([[np.nan], [0.5], [0.5], [np.nan], [np.nan]]),
                 ch=children_of(hh), A=anc_table(hh))
        cc, _p = certify(f, q_)
        assert bool(cc[2, 0]) is want, ("single-sibling threshold at z %.5f, q %.2f" % (dv / 0.5, q_), cc[:, 0])
    f = dict(h=hh, d=np.array([[0.0], [0.0], [0.01], [3.0], [0.0]]), se=np.array([[np.nan], [0.1], [0.1], [0.1], [0.1]]),
             ch=children_of(hh), A=anc_table(hh))
    cc, _p = certify(f, 0.05)
    assert not cc[2, 0] and cc[3, 0]
    assert hh.names[stops_rule(f, np.array([hh.idx["a1"]]), 0.20, cc)[0, 0]] == "r", "the descent skipped an uncertified child"
    cc2 = cc.copy()
    cc2[2, 0] = True
    assert hh.names[stops_rule(f, np.array([hh.idx["a1"]]), 0.20, cc2)[0, 0]] == "a1"
    f["se"][3, 0] = 0.20
    assert hh.names[stops_rule(f, np.array([hh.idx["a1"]]), 0.20, cc2)[0, 0]] == "a", "SE = s_max must not descend (strict <)"


def st_planted():
    c = _syn_c()
    Dt = _syn_data(planted=True)
    st = core(Dt, c)
    L, w = all_lines(st, c)
    t = "\n".join(L)
    assert w["AP1"] == "GRANULARITY-PAYS" and not w["FAP"], w
    assert st["D_C"]["pt"] > 0.001 and st["D_C"]["lo"] > 0
    cert = {(r["model"], r["node"]): r["d"] for r in st["fp"] if r["certified"]}
    for (m, nd_), sign in ((("m03", "S1:a"), 1), (("m01", "S1:a"), 1), (("m05", "S1:b2"), -1), (("m07", "S2:c1"), 1)):
        assert (m, nd_) in cert and np.sign(cert[(m, nd_)]) == sign, ("planted deviation not certified", m, nd_, sorted(cert))
    # the descent reaches the planted nodes for the planted models on their EVAL items
    h = Dt.H["AF"]
    E = st["E"]
    for m, lf, dmin_ in ((3, "S1:a1", 2), (5, "S1:b2", 3), (7, "S2:c1", 2)):
        rows = [j for j, k in enumerate(E) if Dt.leaf[k] == lf]
        dep = h.depth[st["stopA"][rows, m]]
        assert (dep >= dmin_).all(), ("the rule did not descend to the planted node", m, lf, Counter(dep.tolist()))
    need(t, "AP1 (DECIDING) D_C = Brier(C) - Brier(A) = %s [%s, %s]" % (f6(st["D_C"]["pt"]), f6(st["D_C"]["lo"]), f6(st["D_C"]["hi"])))
    # A is the rule at the REGISTERED constants (s_max 0.20, BH q 0.05), and those constants matter on this data (non-vacuous)
    ndE = Dt.node["AF"][E]
    assert np.array_equal(st["stopA"], stops_rule(st["fit"], ndE, 0.20, certify(st["fit"], 0.05)[0])), "A is not the registered rule"
    for q_ in (0.10, 0.01, None):
        assert not np.array_equal(st["stopA"], stops_rule(st["fit"], ndE, 0.20, certify(st["fit"], q_)[0])), "q does not discriminate"
    # NULL: no planted deviation -> the rule never descends; A coincides with C; AP1 TOO-SMALL; F-AP not fired
    Dn = _syn_data(planted=False)
    Dn.member = ["elsewhere"] * len(Dn.items)                      # every EVAL item filed cross-source: OWN-SOURCE is empty
    sn = core(Dn, c)
    Ln, wn = all_lines(sn, c)
    tn = "\n".join(Ln)
    assert sn["below"] == 0.0 and sn["D_C"]["pt"] == 0.0 and sn["D_C"]["hi"] == 0.0, (sn["below"], sn["D_C"])
    assert all(v == 0.0 for v in sn["tau2"].values()) and sn["dstar"] == 1, (sn["tau2"], sn["dstar"])   # tied GATE curve -> shallower
    assert not any(r["certified"] for r in sn["fp"]), "a null fingerprint was certified"
    assert wn["AP1"] == "TOO-SMALL" and not wn["FAP"], wn
    need(tn, "served below the benchmark level 0.0000", "-> TOO-SMALL", "FALSIFIER F-AP", "NOT FIRED",
         "DESCRIPTIVE subset OWN-SOURCE: no EVAL item", "cross-source filed EVAL items (AF leaf of another member) %d" % sn["n_eval"])
    Dx = _syn_data(planted=False)
    Dx.node["KF0"] = Dx.node["KF0"].copy()
    Dx.node["KF0"][np.flatnonzero(Dx.side == "E")[0]] = -1
    try:
        core(Dx, c)
        raise AssertionError("an EVAL item without a cell was not refused")
    except SystemExit as e:
        assert "KF0: an EVAL / GATE item without a cell" in str(e)
    # the split side: theta and every node fit read TRAIN only (EVAL answers flipped: theta and the fits unchanged)
    Df = _syn_data(planted=True)
    Ef = Df.side == "E"
    Df.Y = Df.Y.copy()
    Df.Y[Ef] = 1 - Df.Y[Ef]
    Bm0, _s = lomo_b(Df.Y, Df.keep, 4.0)
    th0 = theta_fit(Df.Y.astype(np.float64), Bm0, np.flatnonzero((Df.side == "T") & Df.keep))
    fa = node_fit(Df.H["AF"], Df.node["AF"], (Df.side == "T") & Df.keep, Df.Y.astype(np.float64), Bm0, th0)
    Bm1 = Bm0.copy()
    Bm1[Ef] += 7.0                                               # EVAL difficulties moved: no TRAIN fit may notice
    th1 = theta_fit(Df.Y.astype(np.float64), Bm1, np.flatnonzero((Df.side == "T") & Df.keep))
    fb = node_fit(Df.H["AF"], Df.node["AF"], (Df.side == "T") & Df.keep, Df.Y.astype(np.float64), Bm1, th1)
    assert np.allclose(th0, th1, atol=0, rtol=0) and np.array_equal(fa["d"], fb["d"]), "a TRAIN fit read EVAL rows"


BIS_SMALL_MODELS = (0, 2, 4, 6, 8, 10)        # +2.5 logits on the SMALL F_bis leaf S1:001 (60 TRAIN items): certified, SE >= 0.20
BIS_BIG_MODEL = 5                              # +0.8 logits on the LARGE F_bis leaf S1:000 (1,400 TRAIN items): certified, SE < 0.20


def _syn_bis_gate(seed=23):
    """D-2 (READY f4dd6292): a synthetic union whose F_bis trees (the same for the 5 seeds) are, per source, r -> 000 / 001 / 002;
    S1:000 = AF leaves a1, a2; S1:001 = the first 60 TRAIN and 40 EVAL items of b2; S1:002 = the rest of S1; S2:000 = c1, S2:002 = c2.
    Responses drawn from expit(theta + planted F_bis offset - b): BIS_SMALL_MODELS +2.5 on S1:001, BIS_BIG_MODEL +0.8 on S1:000."""
    Dt = _syn_data(planted=False, seed=seed)
    rs = np.random.RandomState(seed + 1)
    n, M = len(Dt.items), len(Dt.models)
    cnt = Counter()
    bl = []
    for k in range(n):
        lf, sd = Dt.leaf[k], Dt.side[k]
        if lf in ("S1:a1", "S1:a2", "S2:c1"):
            bl.append("000")
            continue
        if lf == "S1:b2" and sd in ("T", "E"):
            cnt[sd] += 1
            if cnt[sd] <= (60 if sd == "T" else 40):
                bl.append("001")
                continue
        bl.append("002")
    th = np.linspace(-1.2, 1.2, M)
    b = rs.normal(0, 1.0, n)
    off = np.zeros((n, M))
    for k in range(n):
        if Dt.src[k] == "S1" and bl[k] == "001":
            off[k, list(BIS_SMALL_MODELS)] += 2.5
        if Dt.src[k] == "S1" and bl[k] == "000":
            off[k, BIS_BIG_MODEL] += 0.8
    Dt.Y = (rs.rand(n, M) < expit(th[None, :] + off - b[:, None])).astype(np.int64)
    for s in SEEDS:
        nm, pa, lv = [UNION], [None], set()
        for so in ("S1", "S2"):
            nm += ["B%d:%s:r" % (s, so)] + ["B%d:%s:00%d" % (s, so, j) for j in range(3)]
            pa += [UNION] + ["B%d:%s:r" % (s, so)] * 3
            lv |= {"B%d:%s:00%d" % (s, so, j) for j in range(3)}
        nm += list(PSEUDO)
        pa += [UNION, UNION]
        lv |= set(PSEUDO)
        hb = TB.Hier("F_bis gate syn", nm, pa, lv)
        Dt.H["BIS%d" % s] = hb
        Dt.node["BIS%d" % s] = np.array([hb.idx["B%d:%s:%s" % (s, Dt.src[k], bl[k])] if Dt.side[k] != "G" else -1 for k in range(n)],
                                        dtype=np.int64)
    Dt.bis_leaf = bl
    return Dt


def st_bis_gate():
    """D-2: F_bis runs the REGISTERED rule with its SE gate: a certified F_bis child with SE >= 0.20 is NOT descended into, a
    certified one with SE < 0.20 is; core's F_bis Brier is the rule's at s_max 0.20 and differs from the rule without the gate."""
    c = _syn_c()
    Dt = _syn_bis_gate()
    st = core(Dt, c)
    E = st["E"]
    for s in SEEDS:
        fs = st["fstat"][s]
        fb, cb, sb = fs["fit_fb"], fs["cert_fb"], fs["stop_fb"]
        hb = Dt.H["BIS%d" % s]
        small, big, root = hb.idx["B%d:S1:001" % s], hb.idx["B%d:S1:000" % s], hb.idx["B%d:S1:r" % s]
        rs_ = [j for j, k in enumerate(E) if Dt.src[k] == "S1" and Dt.bis_leaf[k] == "001"]
        rb_ = [j for j, k in enumerate(E) if Dt.src[k] == "S1" and Dt.bis_leaf[k] == "000"]
        assert len(rs_) == 40 and len(rb_) == 520, (len(rs_), len(rb_))
        gated = [m for m in BIS_SMALL_MODELS if cb[small, m] and fb["se"][small, m] >= 0.20]
        assert len(gated) >= 3, ("the planted small leaf is not certified with SE >= 0.20", [(m, bool(cb[small, m]),
                                 float(fb["se"][small, m])) for m in BIS_SMALL_MODELS])
        for m in gated:
            assert (sb[rs_, m] == root).all(), ("F_bis descended into a certified child with SE >= 0.20", s, m)
        assert cb[big, BIS_BIG_MODEL] and fb["se"][big, BIS_BIG_MODEL] < 0.20, (bool(cb[big, BIS_BIG_MODEL]), fb["se"][big, BIS_BIG_MODEL])
        assert (sb[rb_, BIS_BIG_MODEL] == big).all(), ("F_bis did not descend into a certified child with SE < 0.20", s)
        P20 = predict(fb, stops_rule(fb, Dt.node["BIS%d" % s][E], 0.20, cb), E, st["theta"], st["Bm"])
        Pin = predict(fb, stops_rule(fb, Dt.node["BIS%d" % s][E], INF, cb), E, st["theta"], st["Bm"])
        YE = Dt.Y[E].astype(np.float64)
        b20, bin_ = float(brier_ll(YE, P20)[0].mean()), float(brier_ll(YE, Pin)[0].mean())
        _close(st["point_br"]["FB%d" % s], b20, 1e-12, "F_bis Brier at the registered s_max 0.20")
        assert abs(b20 - bin_) > 1e-6, ("the SE gate does not change F_bis's Brier here (vacuous)", b20, bin_)


def _fake_st(dc, dd, fb, ff, below=0.6, dstar=3, dcll=None, br=None):
    def ctr(pt, lo, hi, lo90=None, hi90=None):
        return dict(pt=pt, lo=lo, hi=hi, lo90=lo if lo90 is None else lo90, hi90=hi if hi90 is None else hi90, se=0.0001, deff=2.0,
                    n_eff=100.0, mde=0.0003, n=10, sub="ALL")
    pb = dict(A=0.2, B=0.21, E=0.2015, FFmean=0.2, FBmean=0.2)
    pb["D%d" % dstar] = 0.2
    pb["D1"] = 0.2012
    if br:
        pb.update(br)
    return dict(models=["m"] * 18, n_eval=5907, point_br=pb, D_C=ctr(*dc), D_dstar=ctr(*dd), D_Fbis=ctr(*fb), D_Fflat=ctr(*ff),
                dstar=dstar, below=below, D_C_ll=ctr(*(dcll or dc)), n_comp=5404)


def st_branches():
    c = dict(REG)
    dm = c["dmin"]
    cases = [((0.0006, 0.0001, 0.001), "GRANULARITY-PAYS"), ((0.0005, 0.0001, 0.001), "GRANULARITY-PAYS"),
             ((0.00049, 0.0001, 0.0009), "UNDETERMINED"), ((0.001, 0.0, 0.002), "UNDETERMINED"),
             ((0.0002, -0.0001, 0.0005), "UNDETERMINED"), ((0.0002, -0.0001, 0.00049), "TOO-SMALL"),
             ((-0.0003, -0.0006, -0.0001), "TOO-SMALL"), ((0.0007, 0.0006, 0.0004), "GRANULARITY-PAYS")]
    for (pt, lo, hi), want in cases:
        got = ap1_word(dict(pt=pt, lo=lo, hi=hi), dm)
        assert got == want, ((pt, lo, hi), got, want)
    assert fap_fires("TOO-SMALL", dict(hi=-0.0001)) and not fap_fires("TOO-SMALL", dict(hi=0.0)) and not fap_fires("UNDETERMINED", dict(hi=-1))
    assert rule8_ap1(dict(lo=0.0, pt=0.001), dm) and rule8_ap1(dict(lo=0.0001, pt=0.00049), dm) and not rule8_ap1(dict(lo=0.0001, pt=0.0005), dm)
    sw = [((0.0001, 0.0002, -0.0004, 0.0004), "B"), ((-0.0002, -0.0001, -0.0004, 0.0004), "W"), ((0.0, 0.0003, -0.0005, 0.0005), "PARITY"),
          ((-0.0003, 0.0, -0.0005, 0.0005), "PARITY"), ((-0.0003, 0.0004, -0.0005, 0.00051), "NEITHER"),
          ((-0.0006, 0.0003, -0.00051, 0.0002), "NEITHER")]
    for tg in ("AP2", "AP3", "AP4"):
        for (lo, hi, lo90, hi90), want in sw:
            got = sign_word(dict(lo=lo, hi=hi, lo90=lo90, hi90=hi90), dm, "B", "W", tg)
            assert got == want, (tg, lo, hi, lo90, hi90, got, want)
    assert rule8_sign("FIXED-BETTER", dict(lo90=0, hi90=0), 0.0001, "PARITY", "ADAPTIVE-BETTER", "FIXED-BETTER", dm)[0]
    assert rule8_sign("PARITY", dict(lo90=-0.0006, hi90=0), 0.0001, "PARITY", "ADAPTIVE-BETTER", "FIXED-BETTER", dm)[0]
    assert not rule8_sign("NEITHER", dict(lo90=-0.0005, hi90=0.0005), 0.0001, "PARITY", "ADAPTIVE-BETTER", "FIXED-BETTER", dm)[0]
    assert rule8_sign("TREE-BETTER", dict(lo90=0, hi90=0), -0.0006, "KMEANS-BETTER", "TREE-BETTER", "KMEANS-BETTER", dm)[0]
    assert not rule8_sign("KMEANS-BETTER", dict(lo90=-1, hi90=-0.9), -0.0006, "KMEANS-BETTER", "TREE-BETTER", "KMEANS-BETTER", dm)[0]
    # the printed lines by value: AP1 PAYS at the inclusive edge, F-AP fired, rule 8, each prediction's Brier and band word
    st = _fake_st((0.0005, 0.0001, 0.0009), (0.0001, -0.0001, 0.0003, -0.0002, 0.0002), (-0.0002, -0.0007, 0.0001),
                  (-0.0006, -0.0009, -0.0001), below=0.35, dstar=2, br=dict(E=0.2013, D1=0.2012))
    L, w = ap_lines(st, c)
    t = "\n".join(L)
    assert w == dict(AP1="GRANULARITY-PAYS", FAP=False, AP2="PARITY", AP3="NEITHER", AP4="KMEANS-BETTER"), w
    need(t, "-> GRANULARITY-PAYS", "AP1 rule 8: GRANULARITY-PAYS refuted iff LB95 <= 0 or point < 0.0005 -> NOT REFUTED",
         "F-AP (AP1 TOO-SMALL with UB95(D_C) < 0", "NOT FIRED", "AP2 rule 8 (predicted PARITY, point +0.0001): fails by FIXED-BETTER or the 90% interval"
         " leaving [-0.0005, +0.0005] -> DOES NOT FAIL", "AP3 rule 8 (predicted NEITHER, point -0.0002): fails by TREE-BETTER -> DOES NOT FAIL",
         "AP4 rule 8 (predicted KMEANS-BETTER, point -0.0006): fails by TREE-BETTER -> DOES NOT FAIL")
    P = "\n".join(pred_lines(st, w, c))
    need(P, "PREDICTION P1: word GRANULARITY-PAYS (Brier over the outcomes 0.3050); point +0.000500 in [+0.0005, +0.0020] -> HELD",
         "PREDICTION P2: word PARITY (Brier over the outcomes 0.2850); point +0.000100 in [-0.0003, +0.0005] -> HELD",
         "PREDICTION P3: word NEITHER (Brier over the outcomes 0.2900); point -0.000200 in [-0.0008, +0.0004] -> HELD",
         "PREDICTION P4: word KMEANS-BETTER (Brier over the outcomes 0.4150); point -0.000600 in [-0.0013, +0.0001] -> HELD",
         "PREDICTION P5: Brier(E) 0.201300 > Brier(C) 0.201200: True (p 0.80, Brier 0.0400)",
         "PREDICTION P6: share of EVAL (model, item) predictions served below the benchmark level 0.3500 in [0.35, 0.85] -> HELD",
         "sign 0 = 0): True (p 0.90, Brier 0.0100)", "PREDICTION P8: d* = 2 in {2, 3, 4}: True (p 0.70, Brier 0.0900)", "P9", "NOT SCORED")
    st = _fake_st((-0.0003, -0.0006, -0.0001), (0.0003, 0.0001, 0.0006), (0.0003, 0.0001, 0.0006), (0.0003, 0.0001, 0.0006),
                  below=0.8501, dstar=1, dcll=(0.0001, 0, 1), br=dict(E=0.2011, D1=0.2012))
    L, w = ap_lines(st, c)
    t = "\n".join(L) + "\n" + "\n".join(pred_lines(st, w, c))
    assert w["AP1"] == "TOO-SMALL" and w["FAP"] and w["AP2"] == "ADAPTIVE-BETTER" and w["AP4"] == "TREE-BETTER", w
    need(t, "FALSIFIER F-AP", ": FIRES", "F-AP FIRED: the RESP-PROFILE-INFO RP1 reading does not convert", "-> REFUTED",
         "AP4 rule 8 (predicted KMEANS-BETTER, point -0.0006): fails by TREE-BETTER -> FAILS",
         "PREDICTION P1: word TOO-SMALL (Brier over the outcomes 0.9050); point -0.000300 in [+0.0005, +0.0020] -> FAILED",
         "PREDICTION P5: Brier(E) 0.201100 > Brier(C) 0.201200: False (p 0.80, Brier 0.6400)", "0.8501 in [0.35, 0.85] -> FAILED",
         "(log-loss D_C +0.000100, Brier D_C -0.000300; sign 0 = 0): False (p 0.90, Brier 0.8100)",
         "PREDICTION P8: d* = 1 in {2, 3, 4}: False (p 0.70, Brier 0.4900)")
    assert abs(brier_multi(PRED["P4"], "TREE-BETTER") - (0.25 + 0.16 + 0.0025 + 0.9025)) < 1e-12


def st_bis():
    rs = np.random.RandomState(11)
    Xa = rs.normal(0, 1, (12, 4))
    Xa /= np.linalg.norm(Xa, axis=1, keepdims=True)
    tsrc = np.array(["S1"] * 9 + ["S2"] * 3)

    def fitter(X, k, seed):
        assert k == 3 and len(X) == 9 and seed == 4
        return dict(lab=np.array([0, 0, 1, 1, 2, 2, 2, 0, 1]), L=3, internal=[(frozenset([0, 1]), (-1,))])
    names, parents, leaves, C, csrc, cname, real = bis_fit(4, Xa, tsrc, {"S1": 3, "S2": 1}, ("S1", "S2"), fitter=fitter)
    par = dict(zip(names, parents))
    assert par["B4:S1:r"] == UNION and par["B4:S1:n000"] == "B4:S1:r" and par["B4:S1:000"] == "B4:S1:n000"
    assert par["B4:S1:001"] == "B4:S1:n000" and par["B4:S1:002"] == "B4:S1:r" and par["B4:S2:000"] == UNION, par
    assert real == {"S1": 3, "S2": 1} and leaves >= {"B4:S1:000", "B4:S1:001", "B4:S1:002", "B4:S2:000"}
    v = Xa[[0, 1, 7]].sum(axis=0)
    assert np.allclose(C[0], v / np.linalg.norm(v)) and list(csrc) == ["S1", "S1", "S1", "S2"]
    h = TB.Hier("b", names, parents, leaves)
    assert h.depth[h.idx["B4:S1:000"]] == 3 and h.depth[h.idx["B4:S2:000"]] == 1
    # filing: nearest centroid among the declared source(s); no-row items keep the pseudo cell
    vec = {"x": C[2] * 0.9 + C[3] * 0.1, "y": C[3], "z": C[1]}
    vec = {k: v_ / np.linalg.norm(v_) for k, v_ in vec.items()}
    out = file_cells({"x": "a", "y": "b", "z": "c", "w": V.NO_ROUTING_ROW}, vec, {"x": ["S1"], "y": ["S1"], "z": ["S1", "S2"]}, C, csrc, cname)
    assert out == {"x": "B4:S1:002", "y": max(("B4:S1:000", "B4:S1:001", "B4:S1:002"), key=lambda n: float(C[cname.index(n)] @ vec["y"])),
                   "z": "B4:S1:001", "w": V.NO_ROUTING_ROW}, out
    # the real seam: fit_bisecting on random unit rows -> a binary tree with k leaves, every internal node with two children
    Xr = rs.normal(0, 1, (80, 5))
    Xr /= np.linalg.norm(Xr, axis=1, keepdims=True)
    names, parents, leaves, C, csrc, cname, real = bis_fit(0, Xr, np.array(["S"] * 80), {"S": 5}, ("S",))
    h = TB.Hier("b", names, parents, leaves)
    ch = children_of(h)
    assert real == {"S": 5} and sum(1 for n in leaves if n.startswith("B0:S:")) == 5
    assert all(len(ch[h.idx[n]]) == 2 for n in names if n.startswith("B0:S:") and n not in leaves), "not a binary tree"
    try:
        bis_fit(0, Xr[:3], np.array(["S"] * 3), {"S": 5}, ("S",))
        raise AssertionError("k > rows not refused")
    except SystemExit as e:
        assert "[AP-R10]" in str(e)
    hk = kflat_hier(2, ["K2:A:000", "K2:A:001", "K2:B:000", V.NO_ROUTING_ROW])
    assert hk.names[int(hk.parent[hk.idx["K2:A:001"]])] == "KF2:A" and hk.depth[hk.idx["K2:B:000"]] == 2
    assert hk.depth[hk.idx[V.NO_ROUTING_ROW]] == 1 and hk.pseudo[hk.idx[V.NO_ROUTING_ROW]]
    fD = types.SimpleNamespace(models=["m"], n=2, items=["i1", "i2"], is_eval=np.array([False, True]), A=np.zeros((2, 1), dtype=np.int64),
                               comp=["c1", "c2"], src=["A", "A"], tree_keys=["K2:A:000", "KF2:A"], g_tree=np.array([0, 1]))
    try:
        assemble(fD, dict(H_af=hk), [], np.zeros((0, 1), dtype=np.int64), {}, set())
        raise AssertionError("an AF cell that is not a filing leaf was not refused")
    except SystemExit as e:
        assert "are not filing leaves of the AF-U hierarchy (first ['KF2:A'])" in str(e), str(e)


def st_twins():
    qt = {1: "a", 4: "a", 2: "b", 5: "b", 6: "b", 3: "c", 7: " ", 8: " ", 9: "A", 10: "a", 11: "d"}
    ids, ntx = twins_exact(qt, [1, 2, 3, 7, 9, 10, 12], lambda t: t.strip() == "")
    assert ids == [1, 2, 10] and ntx == 2, (ids, ntx)   # 3 'c' has no GEN copy, 7 blank, 9 'A' is not 'a' (no normalisation), 12 absent
    ids2, _n = twins_exact({1: "a", 4: "a", 10: "a"}, [1, 10], lambda t: False)
    assert ids2 == [1, 10]


def st_run_e2e(base, mk):
    lay = clone(base, mk())
    text, err, res = cap(run, lay)
    assert err is None, err
    outp = os.path.join(lay.tmp, "res", "ap", "outcome.txt")
    out = open(outp, encoding="utf-8").read()
    assert out.splitlines()[0].startswith("POOL %s (ADAPTIVE-PROFILE; --run" % U.POOL), out.splitlines()[0]
    # B-1 (READY_ADAPTIVE-PROFILE_delta3): the registrar's deviation line, verbatim, as ONE whole line of the outcome FILE's bytes,
    # a header line (right after U.header's threads line, before the scorer line and any read), followed by its authority line
    raw = open(outp, "rb").read()
    assert raw.splitlines().count(DEV_TEXT.encode("utf-8")) == 1, "the deviation line is not one whole line of the outcome bytes"
    ls = out.splitlines()
    k_dev = ls.index(DEV_TEXT)
    assert ls[k_dev - 1].startswith("  threads: ") and k_dev < ls.index(SCORER_TEXT % lay.common["h_sha"]), k_dev
    assert k_dev < min(k for k, x in enumerate(ls) if x.startswith("DENOMINATORS")), "the deviation line is not a header line"
    assert ls[k_dev + 1] == ("  deviation authority: the author's D-2026-10-09-1 (docs/agents/author_decisions/2026-10-09.md, defab40c),"
                             " recorded by the registrar at prog L25394-L25401 (edb060b9); it covers the one refused attempt (blob"
                             " aff80c1d, main 980c3982) only; registration, criteria, Support and predictions unchanged"), ls[k_dev + 1]
    assert os.path.isfile(os.path.join(lay.tmp, "res", "ap", "READ_STARTED"))
    c = dict(REG, **dict(lay.common, **FIXTURE_REG))
    # R-1 / R-2: the run used the REAL train_unit ("item"), under which train_units counts ITEMS, and the fixture's item and
    # component counts differ, so the item-count form of [AP-DENOM] would refuse here (non-vacuous)
    assert V.PRECONDITIONS["train_unit"] == "item" and res["D"].train_units["n_units"] == lay.common["n_train"], res["D"].train_units["n_units"]
    assert lay.common["n_train"] != lay.common["comp_train"], "the fixture cannot tell items from components"
    assert len(set(res["D"].comp[k] for k in res["D"].T)) == lay.common["comp_train"]
    tline = ("TRAIN DENOMINATOR (key-complete; counted from the data; before the marker and any EVAL read): %d items / %d components"
             " (registered %d / %d)" % (lay.common["n_train"], lay.common["comp_train"], lay.common["n_train"], lay.common["comp_train"]))
    need(out, tline, "  scored: TRAIN %d (%d components), GATE %d, EVAL" % (lay.common["n_train"], lay.common["comp_train"],
                                                                         lay.common["n_gate_key"]))
    assert out.index(tline) < out.index("GATE key (EC-R7)") < out.index("--- EVAL (eval_view"), "a non-EVAL denominator after the EVAL view"
    o = _oracle(lay, res, c)
    st = res["st"]
    assert o["below"] > 0 and o["dc"] > 0.0005, "the planted fixture does not exercise the descent"
    assert len(st["tau2"]) == o["maxd"] and all(abs(st["tau2"][l] - o["tau"][l]) < 1e-8 for l in o["tau"]), (st["tau2"], o["tau"])
    a, cc, bb, ee, dsv, ffv, fbv = U.num(out, r"BRIER \(EVAL, mean over \d+ models x \d+ items = \d+ predictions; lower is better\): A ([0-9.]+) \|"
                                         r" C \(= D_1\) ([0-9.]+) \| B ([0-9.]+) \| E ([0-9.]+) \| D_d\* \(d\* = \d+\) ([0-9.]+) \| F_flat \(mean of"
                                         r" K0..K4\) ([0-9.]+) \| F_bis \(mean of 5 seeds\) ([0-9.]+)")
    for got, want, nm in ((a, o["br"]["A"], "A"), (cc, o["br"]["D1"], "C"), (bb, o["br"]["B"], "B"), (ee, o["br"]["E"], "E"),
                          (dsv, o["br"]["D%d" % o["dstar"]], "D_d*"), (ffv, o["br"]["FF"], "F_flat"), (fbv, o["br"]["FB"], "F_bis")):
        _close(got, want, 1.5e-6, "printed Brier %s" % nm)
    need(out, "d* = %d (argmin GATE, ties to the shallower)" % o["dstar"], "BRIER (EVAL, mean over 9 models x %d items" % o["n_ev"])
    gl = U.num(out, r"GATE Brier d1 ([0-9.]+) d2 ([0-9.]+) d3 ([0-9.]+);")
    for x, y_ in zip(gl, o["gate"]):
        _close(x, y_, 1.5e-6, "GATE depth curve")
    pt, lo, hi = U.num(out, r"AP1 \(DECIDING\) D_C = Brier\(C\) - Brier\(A\) = ([+-][0-9.]+) \[([+-][0-9.]+), ([+-][0-9.]+)\]")
    _close(pt, o["dc"], 1.5e-6, "D_C point")
    _close(lo, o["dc_ci"][0], 1.5e-6, "D_C LB95 (two-stage replay)")
    _close(hi, o["dc_ci"][1], 1.5e-6, "D_C UB95 (two-stage replay)")
    sd_, = U.num(out, r"AP1 \(DECIDING\) D_C = .*bootstrap SD ([0-9.]+)\)")
    _close(sd_, o["dc_sd"], 1.5e-6, "D_C bootstrap SD")
    se_, deff_, neff_, mde_ = U.num(out, r"AP1 D_C      SE ([0-9.]+); DEFF ([0-9.]+) \(Var component bootstrap / Var item i.i.d. bootstrap;"
                                         r" seeds at their mean\); n_eff ([0-9]+); MDE80 ([0-9.]+)")
    _close(se_, o["dc_sd"], 1.5e-6, "support SE")
    _close(deff_, o["deff"], 1.5e-3, "support DEFF (two-stage / i.i.d. replay)")
    _close(neff_, o["n_ev"] / o["deff"], 1.0, "support n_eff")
    _close(mde_, 2.8 * o["dc_sd"], 2e-6, "support MDE80")
    kish_, = U.num(out, r"Kish mean component size ([0-9.]+) ")
    _close(kish_, o["kish"], 1e-4, "Kish")
    fpt, flo, fhi = U.num(out, r"D_F_flat = Brier\(F_flat\) - Brier\(A\) = ([+-][0-9.]+) \[([+-][0-9.]+), ([+-][0-9.]+)\]")
    _close(fpt, o["dff"], 1.5e-6, "D_F_flat point")
    _close(flo, o["dff_ci"][0], 1.5e-6, "D_F_flat LB95 (seeds resampled)")
    _close(fhi, o["dff_ci"][1], 1.5e-6, "D_F_flat UB95 (seeds resampled)")
    want = "GRANULARITY-PAYS" if (lo > 0 and pt >= 0.0005) else ("TOO-SMALL" if hi < 0.0005 else "UNDETERMINED")
    need(out, "on the %d EVAL items" % o["n_ev"], "-> %s" % want, "FALSIFIER F-AP", "NOT FIRED")
    assert res["words"]["AP1"] == want
    hist = " ".join("d%d %d" % (k, v) for k, v in sorted(o["hist"].items()))
    need(out, "adaptive-depth histogram (EVAL (model, item) predictions by the depth A stops at) %s; served below the benchmark level %.4f"
         % (hist, o["below"]))
    need(out, "R1 on the scored sets: twin items dropped TRAIN 2, GATE 1; among the %d scored EVAL items 0" % o["n_ev"],
         "R1 (shared rule; AP-R0): exact-text twins of the paeec pool 4 ids / 3 distinct texts (registered 4 / 3) -> 4 v2 items",
         "R1 EVAL-side twin items with an AF cell (pre-read count): 1; dropped and counted, not refused on",
         "R1 EVAL-side twin items NOT scored (outside the %d; dropped and counted): 1" % o["n_ev"],
         "NOT SCORED (leg not built; declared deviation) -- neither HELD nor FAILED", "anything on af_clean_s42 (the leg is not built",
         "DISCLOSED (L-2, READY f4dd6292)",
         "GATE key (EC-R7)", "SUPPORT (measured", "PREDICTION P9", "SENSITIVITY (descriptive) s_max inf q none")
    # the fingerprint export: the certified set equals the loop BH's; rows for every (model, non-root, non-pseudo node)
    ep = os.path.join(lay.common["export_dir"], REG["export_file"])
    rows = list(csv.DictReader(open(ep, encoding="utf-8")))
    got = set((r["node"], r["model"]) for r in rows if r["certified"] == "1")
    assert got == set((v, m) for v, m in o["cert"]), sorted(got ^ set(o["cert"]))
    for r in rows:
        d_, se_ = o["fit"][(r["node"], r["model"])]
        _close(float(r["offset_vs_parent"]), d_, 2e-6, "export offset %s" % r["node"])
        _close(float(r["path_offset"]), o["Dl"][(r["node"], r["model"])], 2e-6, "export path offset")
    assert os.path.isfile(os.path.join(lay.common["export_dir"], REG["export_readme"]))
    assert out == "\n".join(ln for ln in text.splitlines() if not ln.startswith(("OUTCOME written", "EXPORT written"))) + "\n"
    st_h_e2e(lay, out, res, c, o)
    t2, err2, _r = cap(run, lay)
    assert err2 and "write-once" in err2, err2
    assert open(outp, encoding="utf-8").read() == out


DEV_TEXT = "DECLARED DEVIATION D-2026-10-09-1: second EVAL read after the refused attempt of 2026-10-09 (aff80c1d)"  # prog L25397
SCORER_TEXT = ("MATH scorer: official (eval_results.is_correct, no overlay); sensitivity: H (table sha256-lf %s); MATH-FIX beside:"
               " no")      # the registrar's deviation (1) text, prog L25317-L25327 (literal here: never scorer_line itself)


def st_h_e2e(lay, out, res, c, o):
    """D-2026-10-08-5 on the --run outcome: the scorer header (literal), no overlay row read although the fixture's overlay differs
    from the official on scored MATH cells of every side, and the H line against the INDEPENDENT oracle on H keys."""
    need(out, SCORER_TEXT % lay.common["h_sha"], "H TABLE (AP-R18; the sensitivity line's input, decides nothing): res/h/math_h_table.csv"
         " sha256-lf %s (= the pin); %d rows, 9 models" % (lay.common["h_sha"], len(lay.hfx)),
         "MATH SCORER (AP-R17, D-2026-10-08-5): the key reads TRAIN / GATE / EVAL through the pinned read_key with overlay OFF")
    ls = out.splitlines()
    assert ls.index(SCORER_TEXT % lay.common["h_sha"]) < min(k for k, x in enumerate(ls) if x.startswith("DENOMINATORS")), "scorer line late"
    ov = re.findall(r"MATH-FIX overlay rows (\d+), value changed (\d+)", out)
    assert len(ov) == 2 and all(a == "0" and b == "0" for a, b in ov), ov
    D, Dt = res["D"], res["Dt"]
    side_of = dict(zip(Dt.items, Dt.side))
    leak = Counter(side_of[r["item"]] for r in lay.fx.spec["responses"] if r["cv"] == "mc6" and r["src"] == MATH_SRC and
                   r["mf"] is not None and r["mf"] != r["c"] and r["item"] in side_of)
    assert leak["T"] > 0 and leak["G"] > 0 and leak["E"] > 0, ("the overlay is not exercised on every side", leak)
    mu, Ko, gko = _o_keys(lay, False)
    _mu, Kh, gkh = _o_keys(lay, True)
    chT = sum(int(Ko[D.items[k]][m] != Kh[D.items[k]][m]) for k in D.T for m in mu)
    chE = sum(int(Ko[D.items[k]][m] != Kh[D.items[k]][m]) for k in D.E for m in mu)
    chG = sum(int(gko[i][m] != gkh[i][m]) for i, sd in zip(Dt.items, Dt.side) if sd == "G" for m in mu)
    assert chT > 0 and chG > 0 and chE > 0, (chT, chG, chE)
    need(out, "scored (model, item) cells changed TRAIN %d, GATE %d, EVAL %d" % (chT, chG, chE))
    oH = _oracle(lay, res, c, use_h=True)
    assert abs(oH["br"]["A"] - o["br"]["A"]) > 1e-4, "H does not move the fixture's Brier (vacuous)"
    g = U.num(out, r"  H BRIER \(EVAL, \d+ predictions\): A ([0-9.]+) \| C \(= D_1\) ([0-9.]+) \| B ([0-9.]+) \| E ([0-9.]+) \| D_d\* \(d\* ="
                   r" (\d+)\) ([0-9.]+) \| F_flat \(mean of K0..K4\) ([0-9.]+) \| F_bis \(mean of 5 seeds\) ([0-9.]+)")
    assert int(g[4]) == oH["dstar"], (g[4], oH["dstar"])
    for got, want, nm in ((g[0], oH["br"]["A"], "A"), (g[1], oH["br"]["D1"], "C"), (g[2], oH["br"]["B"], "B"), (g[3], oH["br"]["E"], "E"),
                          (g[5], oH["br"]["D%d" % oH["dstar"]], "D_d*"), (g[6], oH["br"]["FF"], "F_flat"), (g[7], oH["br"]["FB"], "F_bis")):
        _close(got, want, 1.5e-6, "H Brier %s" % nm)
    pt, lo, hi = U.num(out, r"  H D_C = Brier\(C\) - Brier\(A\) = ([+-][0-9.]+) \[([+-][0-9.]+), ([+-][0-9.]+)\]")
    _close(pt, oH["dc"], 1.5e-6, "H D_C point")
    _close(lo, oH["dc_ci"][0], 1.5e-6, "H D_C LB95")
    _close(hi, oH["dc_ci"][1], 1.5e-6, "H D_C UB95")
    fpt, flo, fhi = U.num(out, r"H D_F_flat = ([+-][0-9.]+) \[([+-][0-9.]+), ([+-][0-9.]+)\]")
    _close(fpt, oH["dff"], 1.5e-6, "H D_F_flat point")
    _close(flo, oH["dff_ci"][0], 1.5e-6, "H D_F_flat LB95")
    _close(fhi, oH["dff_ci"][1], 1.5e-6, "H D_F_flat UB95")
    assert res["words"]["AP1"] == ("GRANULARITY-PAYS" if (o["dc_ci"][0] > 0 and o["dc"] >= 0.0005) else
                                   ("TOO-SMALL" if o["dc_ci"][1] < 0.0005 else "UNDETERMINED")), "the word is not the official key's"


def _mem_view(rows):
    """An in-memory response table (the view's column names) for the scorer unit case."""
    import sqlite3
    cn = sqlite3.connect(":memory:")
    cn.execute("CREATE TABLE response (corpus_version TEXT, model TEXT, item_id TEXT, legacy_qid INTEGER, source TEXT, is_correct INTEGER,"
               " is_correct_mathfix INTEGER)")
    cn.executemany("INSERT INTO response VALUES ('cv',?,?,?,?,?,?)", rows)
    return cn


def _sx(fn):
    try:
        fn()
        return None
    except SystemExit as ex:
        return str(ex)


def st_scorer():
    """Scorer / h_key / scorer_keys by value on hand tables: official is_correct (never the overlay), H only on MATH rows, the
    AGREE_OR_UNUSABLE rule, the seam restored, and every AP-SCORER / AP-H-JOIN refusal."""
    htab = {(1, "m1"): (1, "boxed:str"), (2, "m1"): (1, "imported"), (3, "m1"): (0, "none"), (4, "m1"): (1, "boxed:str"),
            (5, "m1"): (1, "boxed:str")}
    rows = [("m1", "i1", 1, "MATH", 0, 1), ("m1", "i2", 2, "MATH", 1, 0), ("m1", "i3", 3, "MATH", 0, 1),
            ("m1", "i4", 4, "BBH", 0, 1),                                 # a non-MATH row whose key IS in the table: never H
            ("m1", "i5", 5, "MATH", 0, None), ("m1", "i5", 5, "MATH", 0, None)]     # a two-row cell; official and H agree
    items = {"i1": 0, "i2": 0, "i3": 0, "i4": 0, "i5": 0}
    orig = V.read_key
    with Scorer(htab) as sc:
        assert V.read_key == sc.read_key
        K, st_ = V.read_key(_mem_view(rows), "response", "cv", ["m1"], items, True, "AGREE_OR_UNUSABLE")
    assert V.read_key is orig, "the seam was not restored"
    assert dict(K) == {"i1": {"m1": 0}, "i2": {"m1": 1}, "i3": {"m1": 0}, "i4": {"m1": 0}, "i5": {"m1": 0}}, dict(K)
    assert st_["overlay_rows"] == 0
    assert dict(sc.calls[0]["KH"]) == {"i1": {"m1": 1}, "i2": {"m1": 1}, "i3": {"m1": 0}, "i4": {"m1": 0}, "i5": {"m1": 1}}, dict(sc.calls[0]["KH"])
    assert sc.calls[0]["hs"] == dict(math_rows=5, h_changed=3), sc.calls[0]["hs"]

    def one(rr, tab, rule, ov=True):
        def f():
            with Scorer(tab):
                V.read_key(_mem_view(rr), "response", "cv", ["m1"], {"i1": 0, "i5": 0}, ov, rule)
        return f
    for rr, tab, rule, needle in (
            (rows[:1], htab, "UNUSABLE_CELL", None),
            (rows[:1], {k: v for k, v in htab.items() if k != (1, "m1")}, "UNUSABLE_CELL",
             "[AP-H-JOIN] MATH row (question_id 1, model m1) has no H row"),
            ([("m1", "i1", 1, "MATH", 0, 1)], {(1, "m1"): (1, "imported")}, "UNUSABLE_CELL", "[AP-H-JOIN] id space"),
            ([("m1", "i1", 1, "MATH", 1, 1)], {(1, "m1"): (1, "boxed:str")}, "UNUSABLE_CELL", "[AP-H-JOIN] id space"),
            ([("m1", "i1", 1, "MATH", 0, 1)], {(1, "m2"): (0, "none")}, "UNUSABLE_CELL", "[AP-H-JOIN] model(s) ['m1'] have no row"),
            ([("m1", "i5", 5, "MATH", 0, 0), ("m1", "i5", 6, "MATH", 0, 0)], {(5, "m1"): (1, "boxed:str"), (6, "m1"): (0, "none")},
             "AGREE_OR_UNUSABLE", "[AP-SCORER] the H key's usable cells differ")):
        e = _sx(one(rr, tab, rule))
        assert (e is None) if needle is None else (e is not None and needle in e), (needle, e)
        assert V.read_key is orig, "the seam leaked"
    e = _sx(one(rows[:1], htab, "UNUSABLE_CELL", ov=False))
    assert e and "[AP-SCORER] a key read with overlay False" in e, e
    assert V.read_key is orig, "the seam leaked after a refusal"
    k1, k2, k3 = {}, {}, {}
    ok = [dict(table="response_lite", K=k1, KH="a", overlay_rows=0), dict(table="response_lite", K=k2, KH="b", overlay_rows=0),
          dict(table="response", K=k3, KH="c", overlay_rows=0)]
    assert scorer_keys(ok, k2) == ("a", "b", "c")
    for calls, gk_, needle in ((ok[::-1], k2, "not TRAIN / GATE / EVAL"), (ok[:2], k2, "not TRAIN / GATE / EVAL"),
                               (ok, k1, "not TRAIN / GATE / EVAL"),
                               ([ok[0], ok[1], dict(ok[2], overlay_rows=1)], k2, "an overlay row was read")):
        e = _sx(lambda: scorer_keys(calls, gk_))
        assert e and needle in e, (needle, e)
    assert scorer_line(dict(h_sha="ab" * 32)) == SCORER_TEXT % ("ab" * 32)


def st_null_e2e(nbase, mk):
    lay = clone(nbase, mk())
    text, err, res = cap(run, lay)
    assert err is None, err
    st = res["st"]
    assert st["below"] == 0.0 and st["D_C"]["pt"] == 0.0, ("the rule descended on null data", st["below"], st["hist"])
    need(text, "served below the benchmark level 0.0000", "AP1 (DECIDING) D_C = Brier(C) - Brier(A) = +0.000000 [+0.000000, +0.000000]",
         "-> TOO-SMALL", "): NOT FIRED")
    assert res["words"]["AP1"] == "TOO-SMALL" and not res["words"]["FAP"]
    need(text, SCORER_TEXT % lay.common["h_sha"], "SENSITIVITY H (AP-R18, D-2026-10-08-5; DESCRIPTIVE, decides nothing")


def _no_outcome(lay):
    assert not os.path.exists(os.path.join(lay.tmp, "res", "ap", "outcome.txt")), "an outcome was written by a refusal"
    assert not os.path.exists(os.path.join(lay.common["export_dir"], REG["export_file"])), "an export was written by a refusal"


def st_refusals(base, mk):
    lay = clone(base, mk())
    saved = UAR._POOL[0]
    buf = io.StringIO()
    with _twins(lay), _unit(lay):
        with U.mine(_me(), lay):
            UAR._POOL[0] = lambda pool: (1, "stub failure")
            try:
                with contextlib.redirect_stdout(buf):
                    try:
                        run(out=lambda s: print(s))
                        err = None
                    except SystemExit as e:
                        err = str(e)
            finally:
                UAR._POOL[0] = saved
    assert err and "B0-2 pool check failed" in err and buf.getvalue().splitlines()[0].startswith("POOL "), err
    hit("REFUSE.POOL")
    _no_outcome(lay)
    nt, ct, ng = lay.common["n_train"], lay.common["comp_train"], lay.common["n_gate_key"]
    dn = "[AP-DENOM] TRAIN %d items / %d components, not the registered %d / %d"
    for over, items, needle, branch in (
            (dict(n_train=nt + 1), None, dn % (nt, ct, nt + 1, ct), "REFUSE.DENOM"),
            (dict(comp_train=ct - 1), None, dn % (nt, ct, nt, ct - 1), "REFUSE.DENOM"),
            (dict(comp_train=ct + 1), None, dn % (nt, ct, nt, ct + 1), "REFUSE.DENOM"),
            (dict(n_gate_key=ng + 1), None, "[AP-GATE-DENOM] %d key-complete GATE items with a cell, not the registered %d" % (ng, ng + 1),
             "REFUSE.GATE_DENOM"),
            (dict(twins=(5, 3)), None, "[R1] the exact-text rule gives 4 ids / 3 texts", "REFUSE.TWINS"),
            (dict(uar_policy_sha="0" * 64), None, "frozen TRAIN policy", "REFUSE.POLICY_SHA")):
        L2 = clone(base, mk())
        t, e, _r = cap(run, L2, items=items, **over)
        assert e and needle in e, (needle, e)
        _no_outcome(L2)
        if branch in ("REFUSE.DENOM", "REFUSE.GATE_DENOM"):     # R-4: refused BEFORE the eval view opens and the marker is written
            assert not os.path.exists(os.path.join(L2.tmp, "res", "ap", "READ_STARTED")), (needle, "the marker was written")
            assert "--- EVAL (eval_view" not in t and "EVAL key:" not in t, (needle, "the EVAL view was opened before the refusal")
    # [AP-GATE-DENOM] counts only key-complete GATE items WITH an AF cell (X107): one key-complete GATE item loses its cell -> ng - 1,
    # refused at the registered ng, before the marker
    L2 = clone(base, mk())
    g0 = sorted(TB._o_gate_key(L2.fx.spec, sorted(L2.gc)))[0]
    real_prep = globals()["prepare"]

    def prep_drop(say):
        P0 = real_prep(say)
        assert g0 in P0["gcell"] and g0 in P0["gits"], g0
        return dict(P0, gcell={k: v for k, v in P0["gcell"].items() if k != g0})
    globals()["prepare"] = prep_drop
    try:
        t, e, _r = cap(run, L2)
    finally:
        globals()["prepare"] = real_prep
    assert e and "[AP-GATE-DENOM] %d key-complete GATE items with a cell, not the registered %d" % (ng - 1, ng) in e, e
    assert not os.path.exists(os.path.join(L2.tmp, "res", "ap", "READ_STARTED")) and "--- EVAL (eval_view" not in t
    _no_outcome(L2)
    # R-2 "or both units": the count does not depend on train_unit; under the fixture's own "component", the same refusal and numbers
    L2 = clone(base, mk())
    t, e, _r = cap(run, L2, unit="component", comp_train=ct - 1)
    assert e and dn % (nt, ct, nt, ct - 1) in e, e
    assert not os.path.exists(os.path.join(L2.tmp, "res", "ap", "READ_STARTED")) and "--- EVAL (eval_view" not in t
    L2 = clone(base, mk())
    mu_, val_ = U.o_key(L2.fx.spec)
    Kf = TB.val_k(val_, mu_)
    ev_item = sorted(i for i, (_c, s) in L2.fx.side.items() if s == "EVAL" and i in L2.af and i in Kf)[4]    # a SCORED EVAL item
    t, e, _r = cap(run, L2, items=list(L2.twin_items) + [ev_item])
    assert e and "[R1-EVAL] 1 scored EVAL item(s) are R1 twins (first ['%s'])" % ev_item in e and "before any fit" in e, e
    need(t, "R1 EVAL-side twin items with an AF cell (pre-read count): 2;", "among the %d scored EVAL items 1" % len(
        [i for i, (_c, s) in L2.fx.side.items() if s == "EVAL" and i in L2.af and i in Kf]),
         "R1 EVAL-side twin items NOT scored (outside the", "): 1")
    assert "AP1 (DECIDING" not in t and "BRIER (EVAL" not in t, "a statistic was printed before the scored-EVAL twin refusal"
    _no_outcome(L2)
    # D-2026-10-08-5: the H table pin (refused before any read) and the join (refused at the read, before any statistic)
    for over, needle in ((dict(h_sha="0" * 64), "[AP-H-PIN] the H table "),
                         (dict(h_table="res/h/absent.csv"), "is absent: no H line without the pinned table"),
                         (dict(h_rows=lay.common["h_rows"] + 1), "carries %d rows, not the pinned %d" % (lay.common["h_rows"],
                                                                                                         lay.common["h_rows"] + 1))):
        L2 = clone(base, mk())
        t, e, _r = cap(run, L2, **over)
        assert e and needle in e, (needle, e)
        assert "DENOMINATORS" not in t and "TRAIN key" not in t and not os.path.exists(os.path.join(L2.tmp, "res", "ap")), t[-300:]
    q = _qid_map(base.fx.spec)
    trm = [r for r in base.fx.spec["responses"] if r["cv"] == "mc6" and r["src"] == MATH_SRC and r["side"] == "TRAIN"]
    k_one = (q[(trm[0]["item"], trm[0]["model"])], trm[0]["model"])
    k_zero = [(q[(r["item"], r["model"])], r["model"]) for r in trm if r["c"] == 0][0]
    for tab, needle in (({k: v for k, v in base.hfx.items() if k != k_one}, "[AP-H-JOIN] MATH row (question_id %d, model %s) has no H row" % k_one),
                        ({k: ((1, "imported") if k == k_zero else v) for k, v in base.hfx.items()},
                         "[AP-H-JOIN] id space: (question_id %d, model %s) official 0" % k_zero),
                        ({k: v for k, v in base.hfx.items() if k[1] != "u05"}, "[AP-H-JOIN] model(s) ['u05'] have no row")):
        L2 = clone(base, mk())
        sha = _put_h(L2.tmp, "res/h/alt.csv", tab)
        t, e, _r = cap(run, L2, h_table="res/h/alt.csv", h_sha=sha, h_rows=len(tab))
        assert e and needle in e, (needle, e)
        assert "AP1 (DECIDING" not in t and "BRIER (EVAL" not in t and "SENSITIVITY H" not in t, "a statistic before the H join refusal"
        _no_outcome(L2)
    for pre in ("marker", "export"):
        L3 = clone(base, mk())
        p = os.path.join(L3.tmp, "res", "ap", "READ_STARTED") if pre == "marker" else os.path.join(L3.common["export_dir"], REG["export_file"])
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write("x")
        t, e, _r = cap(run, L3)
        assert e and "write-once" in e and "GATE key" not in t and "TRAIN key" not in t, (pre, e)
        assert not os.path.exists(os.path.join(L3.tmp, "res", "ap", "outcome.txt"))


def st_dry_run(base, mk):
    lay = clone(base, mk())
    text, err, _r = cap(dry_run, lay)
    assert err is None, err
    ls = text.splitlines()
    assert ls[0].startswith("POOL %s (ADAPTIVE-PROFILE; --dry-run" % U.POOL), ls[0]
    need(text, SCORER_TEXT % lay.common["h_sha"], "H TABLE (AP-R18;")
    assert ls[ls.index("DEVIATION HEADER (printed by --run into the outcome file, verbatim): " + DEV_TEXT) - 1].startswith("  threads: ")
    assert DEV_TEXT not in ls, "the dry-run printed the deviation line as a header of its own"
    need(text, "NOT opened by --dry-run", "DRY-RUN: nothing written; no key read", "POOL CHECK (B0-2): rc 0", "AF-U HIERARCHY (TREE-BACKOFF R1):",
         "F_bis s4:", "R1 twin items by split side", "COST: 0 calls")
    nt, ct = lay.common["n_train"], lay.common["comp_train"]
    need(text, "TRAIN DENOMINATOR (structural, pre-key; counted from the data; before the marker and any EVAL read): %d items / %d"
         " components (registered %d / %d)" % (nt, ct, nt, ct))      # R-3: printed by the dry-run, from the data path
    L4 = clone(base, mk())
    t4, e4, _r = cap(dry_run, L4, comp_train=ct + 1)
    assert e4 and "[AP-DENOM] TRAIN %d items / %d components, not the registered %d / %d" % (nt, ct, nt, ct + 1) in e4, e4
    assert "DRY-RUN: nothing written" not in t4 and not os.path.exists(os.path.join(L4.tmp, "res", "ap")), "the dry-run did not refuse"
    for bad in ("AP1 (DECIDING", "BRIER (EVAL", "PREDICTION", "GATE key (EC-R7)", "TRAIN key:"):
        assert bad not in text, bad
    assert not os.path.exists(os.path.join(lay.tmp, "res", "ap")), "the dry-run wrote under res/ap"
    assert not os.path.exists(lay.common["export_dir"]), "the dry-run wrote the export"
    L = []
    saved = _REG[0]
    _REG[0] = REG
    try:
        U.header(L.append, TEST_ID, "--dry-run", REG_TEXT, [os.path.abspath(__file__)])
        denominators(L.append)
    finally:
        _REG[0] = saved
    t = "\n".join(L)
    assert L[0].startswith("POOL pv2_1575de61bb20e977 (ADAPTIVE-PROFILE; --dry-run"), L[0]
    need(t, "TRAIN 11841 scored items / 10781 CK-CLOSE components", "GATE 1944 key-complete items", "EVAL 5907 items / 5404 components",
         "rule s_max 0.20, BH q 0.05", "delta_min 0.0005", "bootstrap B 2000 default_rng(20261008)", "default_rng(20261009)",
         "prior N(0, 4)", "grid s_max 0.15/0.20/0.30/inf x q 0.10/0.05/0.01/none", "L25133-L25145", "calls 0",
         "DATA ALREADY LOOKED AT (disclosed", "0.8665 vs null 0.3142", "127 / 280 key-certified [P-FAM]", "relative to these 18 models")
    assert REG["twins"] == (471, 427) and REG["out"] == "experiment_results/archv2/adaptive_profile/outcome.txt"
    assert REG["export_dir"] == "E:/TaxoArena_tmp/blog/profiles" and REG["clip"] == 5.0 and REG["paeec_rel"].endswith("paeec.json")
    assert REG["n_route"] == 5907 and REG["comp_route"] == 5404 and REG["pool"] == "pv2_1575de61bb20e977"
    assert REG["h_sha"] == "6b010fa60dde727816b91196d2cb3045094082c3800fe738adebe21d19eeb1d1" and REG["h_rows"] == 23832
    assert REG["h_table"] == "experiment_results/math_scorer_h/math_h_table.csv" and MATH_SRC == "MATH"
    assert scorer_line(REG) == ("MATH scorer: official (eval_results.is_correct, no overlay); sensitivity: H (table sha256-lf"
                                " 6b010fa60dde727816b91196d2cb3045094082c3800fe738adebe21d19eeb1d1); MATH-FIX beside: no")


def st_branch_cover():
    miss = [b for b in BRANCHES if HIT[b] == 0]
    assert not miss, "print / refusal branches never executed: %s" % miss


CASES = (("irt", "rasch_map / LOMO / theta / leaf MLE vs scipy; the target's answers never move its difficulties", "plain"),
         ("nodes", "node_fit, certify, the rule and fixed depth vs loops; single-sibling |z| 1.96; no skipping; SE = s_max", "plain"),
         ("planted", "core(): planted deviations certified and reached; null data never descends (D_C = 0); TRAIN-only fits", "plain"),
         ("branches", "AP1-AP4, F-AP, rule 8, P1-P9 by value at every edge", "plain"),
         ("bis", "bis_fit tree reconstruction, centroids, filing by declared source, the real seam, kflat_hier", "plain"),
         ("bis_gate", "F_bis's SE gate: certified child at SE >= 0.20 not descended, at SE < 0.20 descended; Brier at s_max 0.20", "plain"),
         ("twins", "R1's exact-text rule on a hand table", "plain"),
         ("scorer", "D-2026-10-08-5 seam: official is_correct, H on MATH rows only, AGREE rule, every AP-SCORER / AP-H refusal", "plain"),
         ("run_e2e", "--run on the planted deepened fixture: every deciding number vs the independent oracle; export; write-once", "base"),
         ("null_e2e", "--run on the null fixture: no descent, D_C = 0, TOO-SMALL", "null"),
         ("refusals", "pool, DENOM, GATE-DENOM, twins count, EVAL twin, policy sha, write-once marker / export; nothing written", "base"),
         ("dry_run", "--dry-run: POOL first, structure, no key, nothing written; the REAL constants", "base"),
         ("branch_cover", "every print / refusal branch executed", "plain"))
_FN = {"irt": st_irt, "nodes": st_nodes, "planted": st_planted, "branches": st_branches, "bis": st_bis, "bis_gate": st_bis_gate, "twins": st_twins, "scorer": st_scorer,
       "run_e2e": st_run_e2e, "null_e2e": st_null_e2e, "refusals": st_refusals, "dry_run": st_dry_run, "branch_cover": st_branch_cover}


def selftest(only=None, quiet=False, base=None, nbase=None):
    import tempfile
    import scratch_dir   # noqa: F401  TEMP-SPRAWL: temp on E:, removed at exit
    import shutil
    made, fails, ran = [], [], 0

    def mk():
        d = tempfile.mkdtemp(prefix="ap_")
        made.append(d)
        return os.path.join(d, "lay")
    HIT.clear()
    try:
        for name, desc, kind in CASES:
            if only is not None and name not in only:
                continue
            ran += 1
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    if kind == "base" and base is None:
                        base = build_base(mk())
                    if kind == "null" and nbase is None:
                        nbase = build_base(mk(), plant={})
                    fn = _FN[name]
                    fn() if kind == "plain" else fn(base if kind == "base" else nbase, mk)
                if not quiet:
                    print("  ok   %-13s %s" % (name, desc), flush=True)
            except BaseException as e:            # noqa: B902
                fails.append(name)
                if not quiet:
                    import traceback
                    print("  FAIL %-13s %s: %s: %s" % (name, desc, type(e).__name__, str(e)[:600]), flush=True)
                    traceback.print_exc()
    finally:
        for d in made:
            shutil.rmtree(d, ignore_errors=True)
    if not quiet:
        print("%s selftest: %d / %d passed" % (TAG, ran - len(fails), ran))
    if fails:
        raise AssertionError("selftest failed: %s" % fails)
    return ran


def run_mutants(only=None):
    """tree_backoff.run_mutants' procedure with this script's planted and null bases: each mutant edits the code ABOVE the SELFTEST
    marker in memory, executes the edited module and runs its selftest; KILLED iff the selftest fails. X00 must survive. Sandbox:
    every fixture and output lives in scratch_dir's per-process directory on E: (run under scratch_dir.py --run)."""
    import tempfile
    import scratch_dir   # noqa: F401
    import shutil
    mark = NL + "# " + chr(0x2550) * 2 + " SELFTEST"
    path = os.path.abspath(__file__)
    src = open(path, encoding="utf-8").read()
    cut = src.index(mark)
    d = tempfile.mkdtemp(prefix="ap_mut_")
    rows, bad = [], []
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            base = build_base(os.path.join(d, "lay"))
            nbase = build_base(os.path.join(d, "nlay"), plant={})
        for name, old, new in MUTANTS:
            if only and not any(name.startswith(o) for o in only):
                continue
            head = src[:cut]
            if old and head.count(old) != 1:
                bad.append(name)
                rows.append((name, "NOT APPLIED (%d matches)" % head.count(old)))
                print("  %-74s NOT APPLIED (%d matches)" % (name, head.count(old)), flush=True)
                continue
            try:
                mod = types.ModuleType("adaptive_profile_mutant")
                mod.__file__ = path
                exec(compile((head.replace(old, new) if old else head) + src[cut:], path, "exec"), mod.__dict__)
                with contextlib.redirect_stdout(io.StringIO()):
                    mod.selftest(quiet=True, base=base, nbase=nbase)
                res = "SURVIVED"
            except BaseException as e:   # noqa: B902
                res = "KILLED (%s)" % type(e).__name__
            rows.append((name, res))
            print("  %-74s %s" % (name, res), flush=True)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    ctrl = [r for n, r in rows if n.startswith("X00")]
    surv = [n for n, r in rows if r == "SURVIVED" and not n.startswith("X00")]
    killed = sum(1 for n, r in rows if r.startswith("KILLED") and not n.startswith("X00"))
    total = sum(1 for n, _r in rows if not n.startswith("X00"))
    print("%s mutants: %d of %d KILLED; control %s; survivors %s; not applied %s" % (
        TAG, killed, total, ctrl[0] if ctrl else "not run", surv or "none", bad or "none"))
    return 1 if (surv or bad or (ctrl and ctrl[0] != "SURVIVED")) else 0


NL = chr(10)
MUTANTS = (
    ("X00 control (no edit)", "", ""),
    # AP1 / F-AP / rule 8 (the deciding words)
    ("X01 AP1 PAYS at LB95 >= 0 (boundary)", '    if c_["lo"] > 0 and c_["pt"] >= dmin:', '    if c_["lo"] >= 0 and c_["pt"] >= dmin:'),
    ("X02 AP1 PAYS at point > delta_min (strict)", '    if c_["lo"] > 0 and c_["pt"] >= dmin:', '    if c_["lo"] > 0 and c_["pt"] > dmin:'),
    ("X03 AP1 PAYS without the point clause", '    if c_["lo"] > 0 and c_["pt"] >= dmin:', '    if c_["lo"] > 0:'),
    ("X04 AP1 TOO-SMALL at UB95 <= delta_min", '    if c_["hi"] < dmin:' + NL + '        hit("AP1.TOO_SMALL")', '    if c_["hi"] <= dmin:' + NL + '        hit("AP1.TOO_SMALL")'),
    ("X05 AP1 TOO-SMALL against 0, not delta_min", '    if c_["hi"] < dmin:' + NL + '        hit("AP1.TOO_SMALL")', '    if c_["hi"] < 0:' + NL + '        hit("AP1.TOO_SMALL")'),
    ("X06 AP1 clause order (TOO-SMALL first)", '    if c_["lo"] > 0 and c_["pt"] >= dmin:' + NL + '        hit("AP1.PAYS")' + NL + '        return "GRANULARITY-PAYS"' + NL + '    if c_["hi"] < dmin:',
     '    if c_["hi"] < dmin:' + NL + '        hit("AP1.TOO_SMALL")' + NL + '        return "TOO-SMALL"' + NL + '    if c_["lo"] > 0 and c_["pt"] >= dmin:' + NL + '        hit("AP1.PAYS")' + NL + '        return "GRANULARITY-PAYS"' + NL + '    if c_["hi"] < dmin:'),
    ("X07 F-AP fires on any TOO-SMALL", 'fires = bool(word == "TOO-SMALL" and c_["hi"] < 0)', 'fires = bool(word == "TOO-SMALL")'),
    ("X08 F-AP fires at UB95 <= 0", 'fires = bool(word == "TOO-SMALL" and c_["hi"] < 0)', 'fires = bool(word == "TOO-SMALL" and c_["hi"] <= 0)'),
    ("X09 rule 8 AP1: LB95 < 0 instead of <= 0", 'ref = bool(c_["lo"] <= 0 or c_["pt"] < dmin)', 'ref = bool(c_["lo"] < 0 or c_["pt"] < dmin)'),
    # AP2-AP4 words and rule 8
    ("X10 sign word BETTER at LB95 >= 0", '    if c_["lo"] > 0:' + NL + '        hit(tag + ".BETTER")', '    if c_["lo"] >= 0:' + NL + '        hit(tag + ".BETTER")'),
    ("X11 PARITY on the 95% interval (not the 90%)", '    if c_["lo90"] >= -dmin and c_["hi90"] <= dmin:' + NL + '        hit(tag + ".PARITY")', '    if c_["lo"] >= -dmin and c_["hi"] <= dmin:' + NL + '        hit(tag + ".PARITY")'),
    ("X12 PARITY band strict", '    if c_["lo90"] >= -dmin and c_["hi90"] <= dmin:' + NL + '        hit(tag + ".PARITY")', '    if c_["lo90"] > -dmin and c_["hi90"] < dmin:' + NL + '        hit(tag + ".PARITY")'),
    ("X13 rule 8: the opposite word chosen by the wrong sign", '    opp = worse if pred_pt > 0 else better', '    opp = better if pred_pt > 0 else worse'),
    # the contrasts and the bootstrap
    ("X14 D_C against D_2, not D_1 (C)", '    st["D_C"] = contrast("D1")', '    st["D_C"] = contrast("D2")'),
    ("X15 D_C decided on log-loss", '    st["D_C"] = contrast("D1")', '    st["D_C"] = contrast("D1", metric="ll")'),
    ("X16 point sign reversed", '            pt = float(X[mk][:, off + idx[xname]].mean() - base)', '            pt = float(base - X[mk][:, off + idx[xname]].mean())'),
    ("X17 deciding interval from the i.i.d. bootstrap (naive)", '            reps = R[j][:, off + idx[xname]] - R[j][:, off + idx["A"]]', '            reps = Ri[j][:, off + idx[xname]] - Ri[j][:, off + idx["A"]]'),
    ("X18 items resampled, not components", '        w = np.bincount(rng.integers(0, nC, nC), minlength=nC)[cidx].astype(np.float64)', '        w = np.bincount(rng.integers(0, NE, NE), minlength=NE).astype(np.float64)'),
    ("X19 k-means seeds not resampled", '            reps = R[j][np.arange(c["B_ap"])[:, None], np.array(seeds_cols)[sd]].mean(axis=1) - R[j][:, off + idx["A"]]', '            reps = R[j][:, off + idx[xname + "mean"]] - R[j][:, off + idx["A"]]'),
    ("X20 seeds drawn before the components", '        w = np.bincount(rng.integers(0, nC, nC), minlength=nC)[cidx].astype(np.float64)' + NL + '        sd[b] = rng.integers(0, 5, 5)', '        sd[b] = rng.integers(0, 5, 5)' + NL + '        w = np.bincount(rng.integers(0, nC, nC), minlength=nC)[cidx].astype(np.float64)'),
    ("X21 the 90% interval as the deciding 95%", '        lo95, hi95 = (float(x) for x in np.percentile(reps, [2.5, 97.5]))', '        lo95, hi95 = (float(x) for x in np.percentile(reps, [5.0, 95.0]))'),
    ("X22 DEFF inverted (i.i.d. / two-stage)", '        deff = vc / vi if vi > 0 else float("nan")', '        deff = vi / vc if vc > 0 else float("nan")'),
    ("X23 Kish = plain mean component size", '    st["kish"] = float(sum(v * v for v in Counter(Dt.comp[k] for k in E).values()) / len(E))', '    st["kish"] = float(len(E) / len(set(Dt.comp[k] for k in E)))'),
    # IRT: LOMO, theta, split side
    ("X24 LOMO keeps the target model (not leave-one-out)", '        others = [j for j in range(M) if j != m]', '        others = list(range(M))'),
    ("X25 prior variance ignored in the b gradient", '        g = -(y - p).sum(axis=1) - b / prior_var', '        g = -(y - p).sum(axis=1) - b / 1.0'),
    ("X26 theta fitted on TRAIN + EVAL (wrong side)", '    theta = theta_fit(Y, Bm, np.flatnonzero(tr))', '    theta = theta_fit(Y, Bm, np.flatnonzero(tr | ev))'),
    ("X27 AF-U node fits on TRAIN + EVAL (wrong side)", '    fit = node_fit(h, nd, tr, Y, Bm, theta)', '    fit = node_fit(h, nd, tr | ev, Y, Bm, theta)'),
    ("X28 theta with model 0's difficulties for every model", '    bb = Bm[rows]' + NL, '    bb = Bm[rows][:, [0] * Bm.shape[1]]' + NL),
    ("X29 R1 twins kept (keep mask ignored)", '    Dt.keep = np.array([i not in twins for i in Dt.items], dtype=bool)', '    Dt.keep = np.array([True for i in Dt.items], dtype=bool)'),
    ("X30 GATE twin kept", '    ga = (side == "G") & keep', '    ga = (side == "G")'),
    # node fits
    ("X31 tau^2 without the sampling-variance correction", '        vals = (Ul[has] / Il[has]) ** 2 - 1.0 / Il[has]', '        vals = (Ul[has] / Il[has]) ** 2'),
    ("X32 tau^2 not floored at 0", '        t2 = max(0.0, float(vals.mean())) if vals.size else 0.0', '        t2 = float(vals.mean()) if vals.size else 0.0'),
    ("X33 pseudo-leaves in the moments", '        real = lev[~h.pseudo[lev]]', '        real = lev'),
    ("X34 no shrinkage (prior precision dropped)", '            prec = Ii[lev] + 1.0 / t2' + NL, '            prec = Ii[lev] + 1e-12 / t2' + NL),
    ("X35 path offset from the root, not the parent", '        Delta[lev] = Delta[h.parent[lev]] + d[lev]', '        Delta[lev] = d[lev]'),
    ("X36 parent's offset not in the node score", '        p = expit(theta[None, :] + Delta[par] - Bm[rows])', '        p = expit(theta[None, :] - Bm[rows])'),
    ("X37 only depth 1 fitted (first level only)", '    for l in range(1, A.shape[0]):' + NL + '        a = A[l][leaf]', '    for l in range(1, 2):' + NL + '        a = A[l][leaf]'),
    # certification and the rule
    ("X38 BH replaced by p <= q (no multiplicity)", '            rej = CF.bh([float(pv[u, m]) for u in fam], q)', '            rej = [float(pv[u, m]) <= q for u in fam]'),
    ("X39 family includes siblings without a defined SE", '            fam = kids[defined[kids, m]]', '            fam = kids'),
    ("X40 z from the path offset, not the node offset", '        z = np.where(defined, d / np.where(defined, se, 1.0), np.nan)', '        z = np.where(defined, fit["Delta"] / np.where(defined, se, 1.0), np.nan)'),
    ("X41 one-sided p (registered: two-sided)", '    pv = np.where(defined, erfc(np.abs(np.where(defined, z, 0.0)) / math.sqrt(2.0)), np.nan)', '    pv = np.where(defined, 0.5 * erfc(np.abs(np.where(defined, z, 0.0)) / math.sqrt(2.0)), np.nan)'),
    ("X42 rule without the SE gate", '        ok = active & has[:, None] & (se[cc] < s_max) & cert[cc]', '        ok = active & has[:, None] & cert[cc]'),
    ("X43 rule SE <= s_max", '        ok = active & has[:, None] & (se[cc] < s_max) & cert[cc]', '        ok = active & has[:, None] & (se[cc] <= s_max) & cert[cc]'),
    ("X44 rule skips an uncertified child (no stop)", '        ok = active & has[:, None] & (se[cc] < s_max) & cert[cc]', '        ok = has[:, None] & (se[cc] < s_max) & cert[cc]'),
    ("X45 rule starts at the union root (depth 0)", '    st = np.repeat(A[1][node][:, None], M, axis=1)', '    st = np.repeat(A[0][node][:, None], M, axis=1)'),
    ("X46 A certified at q 0.10 (wrong constant)", '    cert, pv = certify(fit, c["q"])', '    cert, pv = certify(fit, 0.10)'),
    ("X47 A at s_max 0.15 (wrong constant)", '    stopA = stops_rule(fit, nd[E], c["s_max"], cert)', '    stopA = stops_rule(fit, nd[E], 0.15, cert)'),
    ("X48 A served at the leaf (rule ignored)", '    add("A", predict(fit, stopA, E, theta, Bm))', '    add("A", predict(fit, stops_depth(fit, nd[E], 99, M), E, theta, Bm))'),
    # fixed depth, d*, E, F
    ("X49 fixed depth one level short", '    for l in range(2, min(depth, A.shape[0] - 1) + 1):', '    for l in range(2, min(depth - 1, A.shape[0] - 1) + 1):'),
    ("X50 d* = GATE argmax (min<->max)", '    dstar = 1 + int(np.argmin(gate_br))', '    dstar = 1 + int(np.argmax(gate_br))'),
    ("X51 d* ties to the deeper", '    dstar = 1 + int(np.argmin(gate_br))', '    dstar = len(gate_br) - int(np.argmin(gate_br[::-1]))'),
    ("X52 d* chosen on EVAL (wrong side)", '        gate_br.append(float(brier_ll(YG, Pg)[0].mean()))', '        gate_br.append(float(brier_ll(YE, predict(fit, stops_depth(fit, nd[E], dd, M), E, theta, Bm))[0].mean()))'),
    ("X53 E unclipped (+-50)", '    lo = np.full((N, M), -clip)' + NL + '    hi = np.full((N, M), clip)', '    lo = np.full((N, M), -50.0)' + NL + '    hi = np.full((N, M), 50.0)'),
    ("X54 F_flat at depth 1 (the source), not the cell", '        add("FF%d" % s, predict(ff, stops_depth(ff, nf[E], 2, M), E, theta, Bm))', '        add("FF%d" % s, predict(ff, stops_depth(ff, nf[E], 1, M), E, theta, Bm))'),
    ("X55 F_bis without the rule (its leaves)", '        sb = stops_rule(fb, nb[E], c["s_max"], cb)', '        sb = stops_depth(fb, nb[E], 99, M)'),
    ("X56 F_bis leaves hung under the source root", '                parents.append(inner[parent_of(frozenset([j]), -1)])', '                parents.append(inner[0])'),
    ("X57 F_bis filing among all sources", '        out[it] = cname[UAR.file_by_source(vec[it], srcs[it], C, csrc)]', '        out[it] = cname[int(np.argmax(C @ vec[it]))]'),
    # R1, refusals, write-once
    ("X58 R1 exact-text rule case-folded", '    ids = sorted(q for q in res if q in qtext and not blank(qtext[q]) and qtext[q] in gen_texts)', '    ids = sorted(q for q in res if q in qtext and not blank(qtext[q]) and qtext[q].lower() in set(x.lower() for x in gen_texts))'),
    ("X59 R1 count refusal removed", '    if (len(ids), ntx) != want:', '    if False:'),
    ("X60 an UNSCORED EVAL-side twin refused (the pre-read refusal restored; R1 ruling)", '            hit("R1.EVAL_SIDE")', '            refuse("[R1-EVAL] an EVAL-side twin item")'),
    ("X61 TRAIN denominator check removed (both modes)", '    if (n_items, n_comp) != (c["n_train"], c["comp_train"]):', '    if False:'),
    ("X62 GATE denominator check removed", '        if len(gk["items"]) != int(c["n_gate_key"]):', '        if False:'),
    ("X63 export not in the write-once pre-check", '    for p in [U.P(c["out"]), U.P(c["marker"])] + exp:', '    for p in [U.P(c["out"]), U.P(c["marker"])]:'),
    # descriptive / predictions
    ("X64 OWN-SOURCE mask inverted", '    own = np.array([Dt.member[k] == Dt.src[k] for k in E], dtype=bool)', '    own = np.array([Dt.member[k] != Dt.src[k] for k in E], dtype=bool)'),
    ("X65 share below the benchmark counts depth 1", '    st["below"] = float((dA > 1).mean())', '    st["below"] = float((dA >= 1).mean())'),
    ("X66 fingerprints without certification (q none)", '    cert05, pv05 = certify(fit, c["q"])', '    cert05, pv05 = certify(fit, None)'),
    ("X67 P6 scored on D_C", '        st["below"], PRED["P6_band"][0], PRED["P6_band"][1], band_word(st["below"], PRED["P6_band"])))', '        st["below"], PRED["P6_band"][0], PRED["P6_band"][1], band_word(st["D_C"]["pt"], PRED["P6_band"])))'),
    ("X68 P7 compares with D_d*", '    agree = bool(np.sign(st["D_C_ll"]["pt"]) == np.sign(dc["pt"]))', '    agree = bool(np.sign(st["D_C_ll"]["pt"]) == np.sign(st["D_dstar"]["pt"]))'),
    ("X69 P1 band on D_d*", '    for key, word_key, val in (("P1", "AP1", dc["pt"]),', '    for key, word_key, val in (("P1", "AP1", st["D_dstar"]["pt"]),'),
    ("X70 Brier summed over models (not the mean)", '    br = ((Y - P) ** 2).mean(axis=1)', '    br = ((Y - P) ** 2).sum(axis=1)'),
    # delta 2026-10-08 (READY f4dd6292 B1 / D-2 / L-1; the R1 ruling prog L25217); X73 = the review's Y2, X75 Y1, X79 Y3, X80 Y6,
    # X81 Y4, X82 Y5
    ("X71 scored-EVAL twin refusal removed", "    if tw_e:                                       # the R1 ruling's refusal", "    if False:  # the R1 ruling's refusal"),
    ("X72 twin refusal on the EVAL-SIDE set, not the scored set", '    tw_e = sorted(set(D.items[k] for k in D.E) & twins)', '    tw_e = sorted(set(tw_side))'),
    ("X73 F_bis rule without the SE gate (s_max inf)", '        sb = stops_rule(fb, nb[E], c["s_max"], cb)', '        sb = stops_rule(fb, nb[E], INF, cb)'),
    ("X74 F_bis at s_max 0.30 (wrong constant)", '        sb = stops_rule(fb, nb[E], c["s_max"], cb)', '        sb = stops_rule(fb, nb[E], 0.30, cb)'),
    ("X75 F_bis without certification (q none)", '        cb, _pb = certify(fb, c["q"])', '        cb, _pb = certify(fb, None)'),
    ("X76 one-member family by BH p <= 0.05 (|z| >= 1.95996; L-1 reverted)", '            if len(fam) == 1 and q == Q_SINGLE:', '            if False:'),
    ("X77 one-member threshold |z| >= 1.96 (not strict)", '                cert[fam, m] = bool(abs(float(z[fam[0], m])) > Z_SINGLE)', '                cert[fam, m] = bool(abs(float(z[fam[0], m])) >= Z_SINGLE)'),
    ("X78 the 1.96 threshold at every q (the grid's q 0.10 too)", '            if len(fam) == 1 and q == Q_SINGLE:', '            if len(fam) == 1:'),
    ("X79 R1 twins in LOMO b (keep ignored)", '    Bm, sweeps = lomo_b(Dt.Y, keep, c["prior_var"])', '    Bm, sweeps = lomo_b(Dt.Y, np.ones_like(keep), c["prior_var"])'),
    ("X80 GATE rows in the TRAIN fits", '    tr = (side == "T") & keep', '    tr = (side != "E") & keep'),
    ("X81 bootstrap stream seed + 1", '    rng = np.random.default_rng(seed)', '    rng = np.random.default_rng(seed + 1)'),
    ("X82 sampling SE 1/sqrt(I) for the posterior SE", '            s = 1.0 / np.sqrt(prec)', '            s = 1.0 / np.sqrt(np.maximum(Ii[lev], 1e-300))'),
    # delta 2026-10-09 (D-2026-10-08-5: the official scorer of record, AP-R17; the H sensitivity line, AP-R18)
    ("X83 the MATH-FIX overlay kept (the pinned callers' True passed through)", '        K, st = self.orig(tw, table, cv, models, items, False, rule)', '        K, st = self.orig(tw, table, cv, models, items, overlay, rule)'),
    ("X84 H table sha pin not checked", '    if sha != c["h_sha"]:', '    if False:'),
    ("X85 H table row count not checked", '    if len(tab) != int(c["h_rows"]):', '    if False:'),
    ("X86 H applied to any row whose key is in the table (not MATH only)", '            if src == MATH_SRC:', '            if src == MATH_SRC or (int(q), m) in htab:'),
    ("X87 a MATH row without an H row read as official", '                hv = htab.get((int(q), m))', '                hv = htab.get((int(q), m), (v, "imported" if v == 1 else "none"))'),
    ("X88 id-space check removed", '                if (hv[1] == "imported") != (v == 1):', '                if False:'),
    ("X89 H key: the AGREE_OR_UNUSABLE clause dropped", '        if len(vs) == 1 or (rule == "AGREE_OR_UNUSABLE" and len(set(vs)) == 1):', '        if len(vs) == 1:'),
    ("X90 H model check removed", '    if ms - hm:', '    if False:'),
    ("X91 H vs official usable-cell check removed", '        if set((i, m) for i, d in K.items() for m in d) != set((i, m) for i, d in KH.items() for m in d):', '        if False:'),
    ("X92 read-order / GATE-identity check removed", '    if tabs != ["response_lite", "response_lite", "response"] or calls[1]["K"] is not gate_K:', '    if False:'),
    ("X93 overlay-rows check removed", '    if any(x["overlay_rows"] for x in calls):', '    if False:'),
    ("X94 H line on the official matrices", '    D_H.A = A_H', '    D_H.A = D.A'),
    ("X95 H line with the official GATE key", '    st_H = core(assemble(D_H, P_, gitems, Kg_H, gk["meta"], twins), c)', '    st_H = core(assemble(D_H, P_, gitems, Kg, gk["meta"], twins), c)'),
    ("X96 H line with the official TRAIN key (H on EVAL only)", '    A_H = np.array([[(KH_ev if D.is_eval[k] else KH_tr)[i][m]', '    A_H = np.array([[(KH_ev if D.is_eval[k] else sc.calls[0]["K"])[i][m]'),
    ("X97 changed-cell count TRAIN read on the EVAL rows", '    dT = int((D.A[D.T] != A_H[D.T]).sum())', '    dT = int((D.A[D.E] != A_H[D.E]).sum())'),
    ("X98 scorer header says MATH-FIX beside: yes", 'sensitivity: H (table sha256-lf %s); MATH-FIX beside: no"', 'sensitivity: H (table sha256-lf %s); MATH-FIX beside: yes"'),
    # delta 2026-10-09b (POSTRUN_ADAPTIVE-PROFILE R-1..R-4): the TRAIN denominator from the data, before the marker; the dry-run's structural count; the GATE count moved
    ("X100 [AP-DENOM] TRAIN in the item-count form (train_units under the real unit; R-2)", '    return len(tr), len(set(train_meta[i][0] for i in tr))', '    return len(tr), len(tr)'),
    ("X101 TRAIN components over the whole TRAIN side (not the scored items)", '    return len(tr), len(set(train_meta[i][0] for i in tr))', '    return len(tr), len(set(v[0] for v in train_meta.values()))'),
    ("X102 the --run TRAIN check not called before the marker (R-4)", '        check_train(*train_denoms(K_tr, train_meta, models), c, say, "key-complete")', '        pass'),
    ("X103 the dry-run TRAIN check not called (R-3)", '    check_train(*structural_train(cfg, say), reg(), say, "structural, pre-key")', '    pass'),
    ("X104 dry-run components counted as items", '    return len(ok), len(set(meta[i][0] for i in ok))', '    return len(ok), len(ok)'),
    ("X105 dry-run over the whole TRAIN side (structure ignored)", '    return len(ok), len(set(meta[i][0] for i in ok))', '    return len(meta), len(set(v[0] for v in meta.values()))'),
    ("X106 the scored-line print in the item-count form", '        D.n_train, len(set(D.comp[k] for k in D.T)), len(gitems), D.n_eval', '        D.n_train, D.train_units["n_units"], len(gitems), D.n_eval'),
    ("X107 GATE denominator on all key-complete GATE items (cell filter dropped)", '        gk["items"] = sorted(i for i in gk["comp"] if i in P_["gcell"])', '        gk["items"] = sorted(gk["comp"])'),
    # B-1 / L-1 (READY_ADAPTIVE-PROFILE_delta3): the deviation header of D-2026-10-09-1 and the structural roster
    ("X108 deviation line dropped from --run", '    say(DEVIATION_LINE)' + NL + '    say(DEVIATION_AUTH)', '    say(DEVIATION_AUTH)'),
    ("X109 deviation line names the wrong attempt", 'of 2026-10-09 (aff80c1d)"', 'of 2026-10-09 (7279bf43)"'),
    ("X110 deviation line to stdout only (not in the outcome file)", '    say(DEVIATION_LINE)' + NL, '    out(DEVIATION_LINE)' + NL),
    ("X111 deviation authority line dropped", '    say(DEVIATION_LINE)' + NL + '    say(DEVIATION_AUTH)', '    say(DEVIATION_LINE)'),
    ("X112 deviation line after its authority line (not the header line)", '    say(DEVIATION_LINE)' + NL + '    say(DEVIATION_AUTH)', '    say(DEVIATION_AUTH)' + NL + '    say(DEVIATION_LINE)'),
    ("X113 deviation line absent from --dry-run", '    say("DEVIATION HEADER (printed by --run into the outcome file, verbatim): " + DEVIATION_LINE)' + NL, ''),
    ("X114 structural roster = the whole registry (review R03)", 'models = sorted(m for m, s_ in V.registry(tw, cfg.cv_u).items() if s_ == "ACTIVE")', 'models = sorted(V.registry(tw, cfg.cv_u))'),
    ("X99 the H pin not read by --dry-run", '" + DEVIATION_LINE)' + NL + '    load_h(reg(), say)', '" + DEVIATION_LINE)'),
)


if __name__ == "__main__":
    sys.exit(main())
