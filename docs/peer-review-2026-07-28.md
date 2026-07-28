# Peer review — TaxoArena thesis (report/ as of 2026-07-28)

Reviewer stance: external examiner + journal referee. Everything below cites file:line.
Claims were checked against `docs/arena-math-findings.md` (later sections supersede
earlier), `docs/thesis-plan-v2.md`, `docs/reconciled-argument.md`, `docs/prereg_*.md`,
`docs/frozen-artifact.md`, `docs/measurement-discipline.md`, `docs/void-results.md`,
`docs/known-defects.md`, and — where the docs were silent — against the run artifacts
under `experiment_results/`. Numbers I recomputed myself are marked "verified against
artifact".

---

## (a) Summary verdict

The thesis establishes, with unusually careful controls, one strong result: on a
multiple-choice corpus an LLM judge's pairwise verdict tracks answer correctness rather
than reasoning quality (88.8% key agreement, tie rate tripling where the key stops
discriminating, agreement highest on reasoning-free pairs, 99.4% winner agreement with a
rubric-free judge). It also establishes a certified construction (link 1), a lexical
rubric-specificity result against a randomised null (link 2), and a pre-registered
negative about granularity (link 3's premise) — all traceable to the evidence record. The
self-auditing posture (measured/argued marking, void-result discipline, errors reported
against own published numbers) is genuinely above the standard for a Master's thesis.
What it fails to establish, as it stands: (i) the no-partition comparison (Run B) is
reported under a roster description that **contradicts the run's own manifest** — the
model table in Appendix D is not the roster that produced the numbers; (ii) the
"pre-registered null held" reading of Run B **contradicts the pre-registered decision
rule as written** — under both tie conventions the measured Δρ meets the registered
"failed null" criterion, in the direction of the *no-partition* arm; (iii) one MEASURED
claim (11-model-band granularity flatness, 0.973/0.936) is quoted although the project's
own audit says the derivation exists nowhere; and (iv) the judge model is never named and
its identity is unresolved between two contradictory sources, on which the
no-self-preference claim rests. The thesis is defensible after these four are repaired —
the first two are the kind of thing that, discovered *during* a defense, would damage
exactly the credibility the measurement-discipline chapter builds. None of them requires
new judge calls; all four are fixable from data already on disk.

---

## (b) Major issues

### 1. Appendix D's roster table is not the roster Run B used — verified against artifact

- Thesis: `report/04_Appendix/10_Appendix_ModelRoster.tex:19-43` (Table
  `tab:model-roster`, "the roster the arena configuration declares") lists
  gemini-1.5-pro-002, Meta-Llama-3_1-70B-Instruct, claude-3-5-haiku-20241022,
  Mixtral-8x7B-Instruct-v0.1, c4ai-command-r-v01, Meta-Llama-3_1-8B-Instruct among its 12.
  `report/03_Content/5_Experimental_Design.tex:209-215` says "The length-matched band
  (12 models) is the roster of Run B" with r(len,acc) = +0.286.
- Artifact: `experiment_results/arena_math_paired/seed_42/manifest.json` and
  `.../diagnostics/config.toml` (which itself carries the r = +0.286 comment) show Run B's
  actual 12: gemini-3.1-pro_5-shots, iask_pro, arx_3, claude-3.5-sonnet,
  gpt-4o-2024-08-06, deepseek-chat-v2_5, gpt-4o-mini, claude-3-5-sonnet-20241022,
  Qwen1.5-72B-Chat, Meta-Llama-3-8B-Instruct, Qwen1.5-14B-Chat, Meta-Llama-3-8B.
  Only 6 of 12 names overlap with the Appendix D table.
- Why it matters, in increasing order:
  1. The roster table an examiner reads is wrong for the run whose numbers the thesis
     quotes (94.2/94.7, Table `tab:c5-rho`).
  2. `5_Experimental_Design.tex:217-222` defines the corrected 11-model band as "the
     length-matched band less" gemini-1.5-pro-002 — but gemini-1.5-pro-002 is **not in**
     the actual Run B band. The three-roster story (`5_Exp:176-178`) collapses: there are
     at least four rosters, and the stated relationship between two of them is false.
  3. The actual Run B roster contains members the project's own evidence record says
     require disclosure or scrutiny: `gemini-3.1-pro_5-shots` is a **5-shot prompting
     condition** in a 0-shot field (`docs/arena-math-findings.md:608-611, 690-696`:
     "either label the prompting condition in the roster table or drop it" — the thesis
     does neither); `arx_3` and `iask_pro` are systems of unknown provenance
     ("must not be described as LLMs without knowing what they are",
     `arena-math-findings.md:605-607`); `Meta-Llama-3-8B` is a base (non-instruct) model;
     and the deliberate near-clone pair claude-3-5-sonnet-20241022 / claude-3.5-sonnet is
     present with a **pre-registered resolution check** (three predictions,
     `arena-math-findings.md:698-711`, restated in the run config comment) that the
     thesis never reports.
  4. It puts Run C at risk of the exact error the thesis itself elevates to a rule
     (`6_Results.tex:760-765`: "The screen must be computed at the roster the arena will
     actually run"): the domain screen, the reliability constant c = 2.52, and the law
     coverage 287 were all computed on the *reconciled* 11-band
     (`docs/reconciled-argument.md:143-186`), which is a different set from
     "Run B's band minus one".
- Fix: rebuild Appendix D from the run manifests (pilot from
  `arena_math_scoped`/`arena_math_frozen`, Run B from `arena_math_paired`, Run C from
  `arena_law_paired` when it lands); disclose the 5-shot member, the two
  unknown-provenance systems, and the base model, or re-run without them; report the
  pre-registered near-clone check (the verdicts are on disk); state which 11 models Run C
  actually uses and re-run the screen at that set if it differs.

### 2. The Run B primary outcome contradicts the pre-registered decision rule, and the abstract says "the null held"

- The rule, fixed in advance: `docs/prereg_generic_judge_baseline.md:189-195` — "A
  difference of two grid steps or more — |Δρ| ≥ 0.007 — counts as a real difference on
  math **and therefore as a FAILED null**. Anything below that is one quantisation step
  and is read as flat." The thesis reproduces the threshold at `6_Results.tex:361-364`
  and in the caption of Table `tab:c5-rho` (`6_Results.tex:381-384`).
- The measurement (`6_Results.tex:385-393`): Δρ = **+0.064** (half-weighted) and
  **+0.007** (dropped) — both ≥ 0.007, both in favour of the **no-partition** arm.
  Under the registered rule as written, the null failed under *both* tie conventions.
- The thesis records the opposite: "the pre-registered null on Math held"
  (`6_Results.tex:400-411`), "Prediction~1 … is therefore recorded as held";
  `e_Abstract.tex:47-48` "The pre-registered null held"; `8_Conclusion.tex:42-46`.
  The escape is rule D5 (both tie conventions), which the thesis itself says was adopted
  **after** these results ("This rule is newer than the other four and was forced by the
  results of Section~res-tie-policy", `4_Methodology.tex:381-383`). Overriding a
  pre-registered decisive criterion with a rule adopted after seeing the data is
  precisely the move the thesis's own Discussion condemns ("A null under a rule chosen
  afterwards is a shrug", `7_Discussion.tex:79-81`).
- Two further deviations from the same pre-registration, neither named in the thesis:
  the prereg mandates disattenuation of the primary outcome at a re-fitted constant
  ("Disattenuation is mandatory", `prereg_generic_judge_baseline.md:213-247`, including
  "If this run uses a different roster — including the 12-model set — the constant must
  be REFITTED FIRST") — no disattenuated value and no refitted c appear anywhere in
  `6_Results.tex:345-419`; and the prereg anticipated only a *per-leaf* advantage as the
  artifact case (`:186-188`) — the observed *generic* advantage is an outcome the
  registered reading table does not cover.
- The tie-artifact interpretation may well be right — the generic arm has 702 ties
  against MAIN's 582 (verified against artifact,
  `experiment_results/arena_math_paired/seed_42/judging/*_verdicts.csv`), which is
  consistent with tie scoring driving the half-weighted gap, and the thesis does not even
  report these per-arm tie counts that would support its own argument. But the honest
  record is: *the registered criterion fired, in the unanticipated direction; we argue
  post hoc that it is a tie-scoring artifact*. "The pre-registered null held" is spin
  relative to the thesis's own registered rule, and it is in the abstract.
- Fix: restate the outcome as above everywhere it appears
  (`e_Abstract.tex:47-48`, `1_Introduction.tex:357-364`, `6_Results.tex:400-411`,
  `6_Results.tex:885-890`, `8_Conclusion.tex:42-46`); report per-arm tie counts and the
  Davidson-fit or a tie-rate-matched sensitivity check as the supporting evidence;
  name the two prereg deviations explicitly.

### 3. A MEASURED claim rests on numbers the project's own audits say do not exist

- `6_Results.tex:671-675`: "Re-derived at the corrected band it holds: 0.929 and 0.922
  at 8 models, and **0.973 and 0.936 at the 11-model band**." Marked MEASURED.
- The evidence record says the opposite: `docs/reconciled-argument.md:187-204` ("The
  11-band figures are **nowhere** … Do not cite the 11-band flatness numbers until they
  are written to a doc with the script that produced them") and again at `:1173-1175`;
  `docs/thesis-plan-v2.md:1275-1277` repeats it. I searched the repository
  (`tools/`, `build/`, `experiment_results/`, all `.md`) and found no artifact carrying
  these values; the only hits are the audit documents saying they are absent.
- This matters doubly because `6_Results.tex:668-671` uses it to immunise the granularity
  null against the pilot-roster objection, and because the flatness result is the stated
  license for `minClusterSize = 55`
  (`3_System_Architecture.tex:133-138`, `7_Appendix_TuningProtocol.tex:50-54`).
- Fix: either commit the derivation (script + output, roster named) and cite it, or
  delete the sentence and scope the flatness claim to the 8-model roster — in which case
  the R2 caveat at `3_System_Architecture.tex:136-138` needs strengthening.

### 4. The judge model is never named, and its identity is unresolved

- `5_Experimental_Design.tex:52-55` describes "a single large instruction-tuned model
  accessed through an Azure OpenAI-compatible client" — no name, anywhere in the thesis.
- The thesis knows this is open: todos at `5_Experimental_Design.tex:68-73` and
  `10_Appendix_ModelRoster.tex:88-90`; the record shows the conflict
  (`docs/reconciled-argument.md:1188-1191`: `Mistral-Large-3` per
  `arena-math-findings.md:618` vs `ministral-3:14b` per `TaxonomyConfig.kt:59`).
- Load-bearing consequences: the no-self-preference claim
  (`7_Discussion.tex:222-226`, `10_Appendix_ModelRoster.tex:83-86`) is unverifiable; the
  capability premise of the whole verification story ("a judge capable of solving the
  item", `7_Discussion.tex:7-12`) is uncheckable — a 14B judge and a frontier judge make
  that sentence mean very different things; and basic reproducibility of every judge
  result fails without the model name. An examiner will ask this in the first ten
  minutes.
- Fix: read the run manifests, name the model in `5_Exp` §Environment and Appendix D,
  and re-examine the self-preference claim against the *actual* Run B roster (issue 1).

### 5. Run B's analysis numbers are not in the evidence record, and one is quoted in the wrong unit

- Verified against artifact: 94.2% (1133/1203) and 94.7% (1151/1216) key agreement
  reproduce exactly from `arena_math_paired/seed_42/judging/{MAIN,C5}_verdicts.csv`;
  250 distinct questions confirmed.
- Not traceable anywhere: the four ρ values of Table `tab:c5-rho`
  (`6_Results.tex:385-393`: 0.887/0.951/0.916/0.923), the ±0.029 tie-policy movement
  (`6_Results.tex:423-427`), and the 0.860–0.916 sampler×tie spread
  (`6_Results.tex:429-432`). No doc in `docs/` and no committed script produces them.
  The run's own exports give **different** values — MAIN ρ = 0.874, C5 ρ = 0.965
  (`arena_math_paired/seed_42/validation/{MAIN,C5}_thesis_metrics.json`) — i.e. a third
  convention exists in the exports and matches neither quoted row. After the
  correctness-blind-ρ episode (`6_Results.tex:134-150`: two computations, convention not
  written down, number withdrawn), quoting four new convention-dependent ρ values with no
  committed derivation invites the identical failure.
- Unit problem: "5{,}278 comparisons" (`6_Results.tex:44-45`). The manifest records
  2,640 **logical** comparisons per condition (5,280 API calls; two C5 verdicts were
  INVALID). `7_Discussion.tex:239-244` commits the thesis to quoting B_logical.
  5,278 is neither arm's logical count and violates the thesis's own convention.
- Fix: commit the Run B analysis script and its output (the analogue of
  `arena-math-findings.md` for Run B), state the convention that produces each ρ, explain
  the relation to the exported 0.874/0.965, and restate the count as 2,640 logical
  comparisons per arm (5,280 API calls).

### 6. The thesis's cleanest positive result is one `git clean` from unsupported, and its pre-registration currently says the opposite of what happened

- Known and flagged by the thesis itself (`6_Results.tex:615-623`,
  `5_Experimental_Design.tex:373-377`, `7_Appendix_TuningProtocol.tex:300-306`), so this
  is a severity assessment, not a discovery: the p = 1.21e-6 rubric-specificity result
  (link 2) has untracked supporting artifacts
  (`tools/analysis/rubric_specificity_null.py`,
  `src/test/kotlin/taxonomy/RandomCellRubricNullHarness.kt` — confirmed untracked in
  `docs/reconciled-argument.md:93-98, 139-141`), a pre-registration that still reads
  "Treatment arm only. No null. This is not yet evidence."
  (`docs/prereg_rubric_specificity.md:80`), and two band sets whose scope is ambiguous
  (`prereg_arena_launch.md:58-63` vs `prereg_rubric_specificity.md:111-117`).
- Why this is major rather than minor: the thesis calls this result "pre-registered" in
  the abstract's supporting chain and at `6_Results.tex:555-560`, and Appendix
  `7_App:267-306` promises the reader can check the claim. Right now a check *falsifies*
  the label: the registered document disclaims the result. The band ambiguity means the
  headline sentence "0.012 falls inside the ≤ 0.05 band" (`6_Results.tex:598-601`) and
  the within-arm "median ≥ 0.05" criterion could be conflated by a hostile reader.
- Fix: commit both artifacts; append a dated amendment to the prereg with the null-arm
  outcome; state in one sentence which band governs which statistic (they are different
  quantities: random-arm absolute specificity vs within-arm specificity).

### 7. Chapter 2's synthesis contradicts the thesis's own framing and its own results

- `2_Literature.tex:656-673`: "TaxoArena addresses it through **two integrated
  contributions**. The first is a label-bootstrapped, corpus-induced geometric taxonomy …
  it produces the coherent sub-domains **required** by both the ranking model and the
  domain judge. The second is a reference-informed, answer-key-blind arena that
  **produces the per-domain profiles required by routing**."
- This contradicts `1_Introduction.tex:226-228` ("The induced taxonomy is *not* the
  contribution of this thesis") and asserts as delivered exactly what Chapter 5 refutes:
  no per-domain profile signal exists for this roster on this corpus
  (`6_Results.tex:625-712`), and the judge bypasses the partition
  (`6_Results.tex:474-476`). The synthesis reads as a survivor of the pre-reframing
  draft. An examiner who reads Chapter 2's last paragraph and then Chapter 5 will ask
  which thesis they are examining.
- Fix: rewrite the synthesis to promise what Chapter 5 delivers — a measurement of the
  judge, an instrumented construction, and a bounded negative.

### 8. R1's evidence is half-void and the main-text bar-positioning sentence does not say so loudly enough

- `3_System_Architecture.tex:99-109` (Table row R1) positions the 0.025 bar "between two
  measured nulls", and the caveat column marks the within-node values "unresolved as to
  values"; the todo at `:84-87` is honest. But
  `11_Appendix_DAGConstructionFormalism.tex:605-615` states the same positioning
  ("the within-node null of a node's own elongation, whose median lies above it",
  "conservative by a factor of 2.7–4.5") with **no** void marker — the reader of the
  appendix never learns the within-node numbers were computed on the superseded tree
  (`docs/void-results.md:24`; `docs/frozen-artifact.md:137-138`). Half of the R1 defence
  is currently a citation to withdrawn values.
- Fix: re-derive on the frozen mcs=55 artifact (the method survives per
  `void-results.md`), or carry the void marker into `11_App:605-615` and weaken
  "positioned between two measured nulls" to "positioned above the isotropic null;
  within-node comparison pending re-derivation" everywhere it appears
  (`3_Arch:99-109`, `8_Conclusion.tex:24-25`, `1_Introduction.tex:370-372`).

---

## (c) Minor issues

1. **Davidson misattribution.** `2_Literature.tex:422-428` says ties-as-half-wins follows
   "the tie-as-half-win convention introduced for paired-comparison models by Davidson";
   `8_Appendix_JudgeGeneration.tex:44-47` repeats it. Davidson (1970) introduces a tie
   *propensity parameter* — the thing `4_Methodology.tex:119-123` correctly says is NOT
   fitted. Half-win credit is not Davidson's convention. Fix the attribution; cite
   Davidson only where the un-fitted alternative is discussed.
2. **Appendix E figure captions describe the retired acceptance rule.**
   `11_App:698-708` and `:714-727` caption the proposal-gate figures as "the
   lexicographic $(\Delta J, \Delta|V|)$ test against the neutrality band $\tau$" — the
   legacy z=0 arm, contradicting the corrected text at `11_App:643-676`. Fix captions.
3. **Iteration accounting conflict.** `11_App:205-211`: quiescence requires five
   consecutive zero-edit iterations and "canonical runs converge at approximately
   iteration 15"; but the frozen certificate reads final iteration 10 with 8/9/10
   identical (`6_Results.tex:499-503`, `frozen-artifact.md:30-39`). Three identical
   iterations ≠ five quiescent; reconcile the streak length, the stop iteration, and the
   "≈15" sentence.
4. **DAG residue in a tree.** `11_App:491-495`: "a node reached along several paths
   aggregates them by log-sum-exp, so a multi-parent destination's membership is the sum
   over its incoming paths" — there are no multi-parent destinations in a strict tree
   (`6_Results.tex:774-786`). Delete or mark historical.
5. **"refused" for "refuted".** `4_Methodology.tex:443`, `6_Results.tex:545`,
   `6_Results.tex:902`, `8_Conclusion.tex:32`. "Premise refused" will read as a typo four
   times; if it is intentional voice, it will still read as a typo.
6. **Abstract quotes a 33-comparison cell without n.** `e_Abstract.tex:42-44` gives
   "97.0% against 83.2%" — the 97.0% cell holds 33 comparisons
   (`6_Results.tex:270-272`). At n=33 the binomial SE is ~3 points; the abstract should
   carry the qualifier or drop the decimal.
7. **All figures are placeholders.** `1_Introduction.tex:92-105`,
   `6_Results.tex:194-208`, `:510-523`, `:714-727`, `7_App:182-197`, `11_App:698-728`.
   No actual figure exists in the document. Not a finding about honesty — every
   placeholder declares its data source — but the thesis cannot be submitted this way,
   and the volume of remaining figure work is understated by the todo list.
8. **Screen draw counts disagree with the prereg.** `6_Results.tex:737` (and
   `arena-math-findings.md:802`) say 1,500-draw null at the 11-band;
   `prereg_generic_judge_baseline.md:172-174` says 2,000-draw. Trivial, but the thesis
   sells pre-registration hard; say which governs.
9. **Run C's decisive threshold is not itself pre-registered.** The |Δρ| ≥ 0.009 at
   M = 11 in the todo (`6_Results.tex:53-59`) is derived by analogy from the Math rule;
   P4 registered a directional prediction for law, not a threshold. Register it (dated)
   before Run C completes, or the law reading inherits issue 2's weakness.
10. **The 0.884 re-routed figure is unsourced.** `6_Results.tex:678-685` names the
    convention (good — this is the required handling of the known irreproducible 0.922),
    but 0.884 appears in no doc or artifact I could find. Commit the recomputation.
11. **Run B parse failures and tie counts unreported.** `5_Exp:303-311` promises the
    failure *modes* differ between verdict formats; the realised counts (2 INVALID in C5,
    0 in MAIN; ties 582 vs 702 — verified against artifact) appear nowhere. Both bear
    directly on the tie-artifact interpretation of `6_Results.tex:400-411`.
12. **No multiplicity handling in the domain screen.** `6_Results.tex:729-743` reports
    law p = 0.008 among ~12 domains screened per policy with no correction; at
    Bonferroni α = 0.0036 law would not survive under policy B. The convergent evidence
    (p = 0.000 at 8 models, p = 0.000 under policy A) is the real defence — state it as
    such.
13. **Options-blind arm, as described, cannot remove the correctness channel.** The
    project's own addendum (`prereg_generic_judge_baseline.md:283-289`) records that
    94.8% of traces *state their own answer*, so withholding options is insufficient and
    a stated-answer strip (NO_KEY) is a second, independent manipulation. The thesis's
    future-work item 2 (`8_Conclusion.tex:92-104`) and prereg P5
    (`7_App:339-361`) describe options-blind only. Import the addendum's point, or the
    flagship future experiment is known-broken at proposal time.
14. **Same-model rubric induction is a disclosed choice with an unexamined consequence.**
    `8_App:18-21` says the rubric-generation model is the arena judge "to avoid
    introducing a second model's stylistic biases" and promises the limitation is
    revisited in `sec:disc-limitations` — it is not (that section,
    `7_Discussion.tex:246-332`, covers SEs, the constant, redundancy, ECE). The
    unexamined consequence: rubrics written by the judge's own model may encode the
    judge's own priors, which is an alternative mechanism for the 99.4% rubric/no-rubric
    agreement that does not involve correctness at all. Add the paragraph the appendix
    promises.
15. **Dependence of comparisons is acknowledged but the claimed defence is not shown.**
    `4_Methodology.tex:444-447` says "the query-level bootstrap intervals of
    Section~exp-metrics are the reported defence" — no such interval is reported anywhere
    in Chapter 5 (`5_Exp:422-426` gives resample counts by path only). Either produce the
    intervals or soften the sentence.
16. **Cross-reference staleness.** `11_App:135` points the single-parent invariant at
    "Section~subsec:polyhierarchy, Chapter~discussion"; the polyhierarchy section now
    lives in Results (`6_Results.tex:774`). Also `8_App:35-38` is an unfilled comment
    placeholder for the verbatim judge template ("insert … once finalized") — the
    appendix currently promises content it does not contain, and the vestigial prompt
    line "If the ground truth answer is provided…" must be excluded when it is filled
    (`docs/reconciled-argument.md:519-520`).
17. **`known-defects.md` contradicts the thesis on routing ECE.** The thesis's handling
    (0.2114 with the max-vs-sum discrepancy named, `7_Discussion.tex:315-323`,
    `9_App:144-156`) follows `reconciled-argument.md:33-83`; but `known-defects.md:63-66`
    still says "Do not report routing ECE — never measured". Amend the doc so the
    evidence record agrees with the thesis (the reconciliation already ordered this).

---

## (d) Defense questions an examiner would actually ask

1. *"Which twelve models produced Table `tab:c5-rho`? Your Appendix D lists Mixtral and
   Command-R; your run manifest lists arx_3 and a 5-shot Gemini condition."* — **Not
   answered; the thesis contradicts its own artifact** (major issue 1).
2. *"Your pre-registration says |Δρ| ≥ 0.007 counts as a failed null. You measured
   +0.064 and +0.007, both favouring the no-partition arm. Why does your abstract say the
   null held?"* — **Partially answered** (the tie-artifact argument at
   `6_Results.tex:400-411` exists) but the rule contradiction is unacknowledged and the
   supporting tie counts are unreported (major issue 2).
3. *"What is the judge model, and what is its own accuracy on these 241/250 questions?
   If the verdict is verification, agreement should track the judge's solve rate — is
   88.8% the judge's solve rate?"* — **Not answered.** Identity unresolved
   (`5_Exp:68-73`); the judge's own accuracy is never measured; the stem-only probe the
   project designed for exactly this bound is "NOT YET RUN"
   (`prereg_generic_judge_baseline.md:302-306`).
4. *"Where is the derivation of 0.973/0.936 at the corrected roster?"* — **Not
   answerable from the repository** (major issue 3).
5. *"You screened ~12 domains and selected law at p = 0.008. What survives a
   multiplicity correction?"* — **Not answered**; the convergent-evidence answer exists in
   the record but is not assembled (minor 12).
6. *"Two judges agreeing on 99.4% of winners is your evidence the rubric is decorative.
   Your rubrics were written by the same model that judges. How do you exclude that the
   agreement reflects shared model priors rather than correctness verification?"* —
   **Not answered** (minor 14); the trace-stratum and tie-stratum results partially
   defend, but the confound is never named.
7. *"Your Fisher SEs assume independent comparisons; each of 250 questions appears in up
   to 66 pairs. How large is the effective-sample-size inflation, and do the sign tests
   in `6_Results` inherit it?"* — **Acknowledged, not quantified**
   (`4_Methodology.tex:428-434`, `7_Discussion.tex:152-156`); the promised query-level
   bootstrap is not shown (minor 15).
8. *"You pre-registered three predictions for the near-clone pair and ran both models in
   Run B. What happened?"* — **Not answered anywhere in the thesis**
   (`arena-math-findings.md:698-711`; the verdicts are on disk).
9. *"The correctness-blind fidelity magnitude is unresolved between ~0.75 and ~0.92 on
   the same verdicts. Doesn't your composite claim lean on that magnitude?"* — **Answered
   well** (`6_Results.tex:134-150`): the magnitude is withdrawn, direction and tie
   behaviour carry the claim; this is the model for how issues 2–5 should be handled.
10. *"Why is the thesis being defended before Run C, given that law is the only domain
    where the partition has anything to detect?"* — **Answered honestly**
    (`6_Results.tex:49-59`, `8_Conclusion.tex:105-111`): Math is the designated null arm;
    the law test is named as outstanding. Expect pressure, but the scoping is defensible.
11. *"You claim answer-key-blindness is enforced. What does the judge see, exactly, and
    would your build fail if a reserved query leaked into rubric induction?"* —
    **Answered strongly** (`3_System_Architecture.tex... 4_Methodology.tex:63-71`,
    `5_Exp:160-172`): the build-failing assertion is the right answer, and the thesis
    correctly distinguishes answer-key-blind from answer-blind.
12. *"What, concretely, would this architecture measure on an open-ended corpus, and how
    would you validate it without a key?"* — **Partially answered**: the binding-regime
    argument is made (`7_Discussion.tex:24-39`), the NO_KEY design exists in the record
    (`prereg_generic_judge_baseline.md:277-402`) but is absent from the thesis's future
    work, and no validation strategy without ground truth is sketched (split-half judge
    self-consistency is in the addendum, not the thesis).

---

## (e) Slop audit — `report/03_Content/*.tex`

The prose is essentially free of standard LLM slop: **zero** hits for the banned-word
list in authorial use ("robust" appears only in technical senses — "sandwich robust
standard error" `2_Literature.tex:120`, "robust across all three definitions"
`6_Results.tex:567` — none flagged) and **zero** hits for the empty-phrase list ("it is
worth noting", "in order to", etc.). No weasel attribution, no rhetorical-question
setups, no summary-recap endings. The findings below are rhythm and register, not
vocabulary.

1. **Robotic rhythm: the "X, not Y" antithesis is the document's default sentence
   shape.** ~130 instances of ", not …" / "rather than" across the eight files (11 in
   `6_Results.tex` for the ", not x" form alone). Examples: "a budget choice, not a
   statistical one" (`3_System_Architecture.tex:179-180`); "rationale-conditioned, not
   rationale-driven" (`6_Results.tex:324`); "Power, not proof" (`6_Results.tex:688`);
   "Ceiling, not prediction" (`6_Results.tex:701`); "a measurement rather than a
   housekeeping decision" (`5_Experimental_Design.tex:224-225`). Each is fine alone; at
   this density the reader starts hearing the template. Fix: keep the five strongest,
   recast the rest as plain declaratives.
2. **Recycled aphorism.** "A null under a decision rule fixed before the data is a
   finding. A null under a rule chosen afterwards is a shrug."
   (`7_Discussion.tex:79-81`) reappears as "…the difference between a result and a
   shrug" (`8_Conclusion.tex:71-73`). A signature line loses force on the second use.
   Fix: use once.
3. **Em-dash density as a rhythm crutch.** 53 `---` in `6_Results.tex` (~1 per 125
   words), 32 in `5_Experimental_Design.tex`, 23 in `3_System_Architecture.tex`
   (~1 per 71 words). Fix: convert roughly half to commas, parentheses, or sentence
   breaks; the surviving dashes will regain their emphasis.
4. **Meta-discursive self-narration at chapter and section openings.** "That ordering is
   load-bearing rather than editorial." (`6_Results.tex:6`); "The sections are not sized
   by the size of their literatures." (`2_Literature.tex:15-16`); "The ordering is
   deliberate." (`3_System_Architecture.tex:19`); "This ordering is not a late
   concession." (`1_Introduction.tex:236-237`). Four chapters each pause to explain
   their own structure's virtue. Fix: keep at most one (the `6_Results` one earns its
   place); delete the rest — the structure should demonstrate, not advertise.
5. **Dramatised narration in a results chapter.** "It arrived from a direction nobody
   was looking in" (`6_Results.tex:101-102`). Fix: "It was recorded for the
   Bradley–Terry sufficient statistics, not as a test of anything" (the next clause)
   already says it; delete the theatrical lead-in.
6. **Fake-profound kicker risk.** "A result that changes sides under a scoring
   convention is not a result." (`6_Results.tex:407-408`); "a reframing announced is a
   contribution, a reframing concealed is a rationalisation"
   (`1_Introduction.tex:290-291`); "this thesis's most defensible sentence"
   (`7_Discussion.tex:34`). Each individually defensible; collectively the thesis
   editorialises its own virtue about once per page. Fix: thin by half; and delete
   "most defensible sentence" — let the examiner rank the sentences.
7. **Bold sprinkled mid-sentence.** "\textbf{Mixed pairs are $868/1736 = 50\%$ of all
   Run~A comparisons.}" (`6_Results.tex:236-238`); "\textbf{actual winner flips: …}"
   (`6_Results.tex:306-307`); bold paragraph-lead phrases throughout
   `5_Experimental_Design.tex:325-378` and `6_Results.tex:461-476`. Fix: reserve bold
   for run/condition names and paragraph leads; use italics for in-sentence emphasis per
   thesis convention.

Not flagged: the pervasive short-sentence verdicts ("It does not fall.",
`6_Results.tex:657`; "The question is replaced rather than repaired.",
`1_Introduction.tex:303`) — at their current frequency they read as voice, not slop, and
several carry real argumentative weight. The register is unusually assertive for a
Master's thesis, but that is an authorial choice, not an AI pattern.

---

## (f) What I could not verify

1. **Run B's four ρ values, the ±0.029 movement, and the 0.860–0.916 spread**
   (`6_Results.tex:385-393, 421-432`) — no committed script or doc; the run's exports
   give 0.874/0.965 under an unstated third convention. (Key agreement 94.2/94.7 and
   tie/INVALID counts I verified directly from the verdict CSVs.)
2. **The 11-model-band flatness figures 0.973/0.936** (`6_Results.tex:674`) — the audits
   say they exist nowhere (`reconciled-argument.md:187-204`), and I found nothing.
3. **The 0.884 re-routed leaf-level figure** (`6_Results.tex:682`).
4. **r(len,acc) = +0.286 / +0.597** (`5_Exp:212-213`) — asserted in the run-config
   comment and the prereg; no script or table of per-model lengths in the record.
5. **The 94.8% stated-answer rate** (`1_Introduction.tex:258-259`,
   `4_Methodology.tex:90-91`) — asserted in the prereg addendum
   (`prereg_generic_judge_baseline.md:284-289`); no artifact.
6. **The judge model identity** (major issue 4) and therefore the no-self-preference
   claim.
7. **Which roster Run C is running on** — `experiment_results/arena_law_paired/` exists
   with no manifest yet; if its roster is not the set the screen and c = 2.52 were
   computed on, `6_Results.tex:735-743` inherits issue 1.
8. **Whether any Bradley–Terry interval was recomputed post-correction** — the thesis
   quotes no CI, consistent with its own rule (`4_Methodology.tex:152-165`), and the todo
   at `7_Discussion.tex:325-332` remains open.
9. **The within-node null values on the frozen artifact** (major issue 8) — void per
   `void-results.md:24`; not re-derived.
10. **Commit dates of the pre-registration documents** — the thesis's pre-registration
    claims rest on the documents being dated *in git* before their data
    (`5_Exp:329-331`, `7_App:269-271`); I did not audit the git history, and for
    `prereg_rubric_specificity.md` the in-document status contradicts the claimed
    sequence until amended (major issue 6). An examiner may run `git log` on these files;
    the thesis should preempt with the commit hashes.
11. **The count of \todo markers**: I found nine `\todo[inline]` blocks
    (`3_Arch:84`, `5_Exp:68`, `5_Exp:373`, `6_Results:53`, `6_Results:145`,
    `6_Results:615`, `7_Disc:325`, `7_App:300`, `10_App:88`) plus the German-abstract
    TODO (`e_Abstract.tex:15-19`) and a comment-level `TODO(calibration)`
    (`7_App:262`). Load-bearing for the defense: the judge-identity pair (issue 4), the
    stale-prereg pair (issue 6), and the within-node-null todo (issue 8). The Run C todo
    (`6_Results:53`) and the correctness-blind-ρ todo (`6_Results:145`) are honestly
    scoped and survivable as stated. The German abstract is a submission requirement,
    not a research gap — but it blocks submission at TU Berlin all the same.
