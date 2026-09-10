# Rubric v2 — from a process checklist to a verification kit (design, 2026-09-10)

## What the evidence says a rubric is, and is not

| finding | source | consequence for design |
|---|---|---|
| Induced cell rubrics are worth 0 to +1pp to either judge tier on keyed questions; anchor = leaf | RUBRIC-P8 (0.0), 512 (+1.8 boundary), 512-SS (+1.0 n.s.), 512-R (0.0, reasoning judge); ladder p=0.68 | the current rubric TEXT is not a lever; finer text is not better text |
| The rubrics are specific but are PROCESS checklists ("apply the governing law, check units, justify assumptions") with no cell-specific failure modes or facts | free audit 2026-09-10: 2,861 chars median, Jaccard 0.08, 7% boilerplate | they tell the judge what good reasoning looks like in general, which it already knows; they give it nothing it can CHECK |
| Rubric gain tracks judge competence (ρ=+0.52): rubrics help where the judge can already solve | S1 | a rubric guides evaluation; it does not substitute for the ability to verify |
| A reference answer is the lever (+7.6 all, +13.9 top cluster); a wrong reference hurts; two references are worse than one | J2, J2-R, J2-D | what helps is VERIFIABLE content about the answer, not advice about reasoning |
| Verify-first mechanics move the elaboration bias (truncated arm 0.350 → 0.433) and, with the reference and the anchor rubric, give the best judge measured (0.865, board key-ordered) | L1-V2, STACK-v2 | the prompt's job is to force verification before comparison; rubric content should feed that verification |
| Leaf-level structure is real in the key (model×leaf interaction p=0.005; Math leaf-over-anchor +12.7/1000) — what models get wrong IS cell-specific | LEAF-PROFILE A, F2, F5 | the cell's train-side wrong answers and solved examples are the information a leaf uniquely holds |
| Rubrics generated from the question alone score below no-rubric; response-in-view rubrics help; decomposed + filtered checks help most | Shen et al. 2602.05125 (in the proposals doc) | induce WITH wrong answers in view; decompose into checks; filter by the key |
| Markdown/format carries no weight; padding carries no weight; content of reasoning does | FORMAT, L1 pad, L1 truncate | do not spend rubric text on style; spend it on checkable content |

Conclusion: a rubric in this system should not be a description of quality. It should be a **verification kit**: the material a judge that cannot solve the question needs in order to check the two answers — assembled per cell from what only the cell has (its solved train-side questions and its observed failure modes), delivered in a form the prompt forces the judge to use.

## Root cause, found in the induction templates
`JudgePrompts.induceBatchGuidelines` instructs the inducer: "Focus on PROCEDURAL LOGIC and VALIDITY of
reasoning, not memorized facts or specific numbers … Rules must describe properties of a REASONING
PROCESS, never properties of an answer's content … Never state what a correct answer looks like." The
process-checklist character of every rubric is therefore by design — a leakage-safety choice (no rule
may help pick an option without reasoning) that also removed everything a non-solving judge could
verify. The kit keeps the safety property by a different mechanism (cell-general content only; the
H2-style n-gram audit against the correct options of every judged question; neighbours filtered for
option overlap) and drops the prohibition on content.

## The kit, in layers (each is separately testable and separately cheap)

**K0 Anchor process rubric** (keep). The 14 clean anchor rubrics from the ladder. Cost 0. Value ≈ the leaf's; it sets the evaluative register.

**K1 Cell failure catalogue** (contrastive, cell-specific). From the cell's TRAIN-side wrong answers (key-labelled, frontier contestants): the 5–8 recurrent error patterns, each with its tell-tale sign and the check that exposes it ("chose the unit-inconsistent option after dropping the 1/2 in ½mv²: check that kinetic-energy expressions carry the factor"). Induced by the reasoning model once per cell (1 call; the anchor-level version is J6's contrastive arm, running now). This is the only layer whose content differs between sibling leaves for a reason the key confirms (LEAF-PROFILE A).

**K2 Cell knowledge card** (content, response-blind). From the cell's train-side reference reasonings: the recurring facts, formulas, definitions, sign conventions and boundary conditions that answers in this cell must satisfy — a compact "what must hold" list (≤ 12 items). Induced once per cell (1 call). Gives the judge checkable statements without solving from scratch; it is what a Math/Physics leaf can offer that "apply the governing law" cannot.

**K3 Worked neighbours** (retrieval, zero calls). The 2 most similar TRAIN-side questions of the same leaf (embedding cosine on the 512-slice), with their key and reference reasoning, inserted next to the judged question as worked examples. Pool hygiene is preserved by construction: the reserved question is never in induction or retrieval material; neighbours are train-side only. This uses the leaf functionally — as a retrieval unit — which is the first design in the campaign where leaf granularity does something an anchor cannot.

**K4 Reference** (the lever, keep). One reasoning-model answer per question, marked as fallible (J2-R). Never gated, never doubled (free test, J2-D).

**K5 Structured verification mechanics** (prompt). v2's verify-first policy, extended into a decomposed output the judge must fill BEFORE the verdict: extracted final answer per response; agreement with the reference; for each K1 failure sign, present/absent per response; K2 facts violated per response; then the comparison and verdict. Turns the rubric from prose the judge may skim into checks the judge must answer (the "decomposed" rubric of 2602.05125). Confidence field kept; dual order kept.

**K6 Key-filtered checks** (adaptive, cell-specific weights; later). On train-side pairs only, have the judge fill the K1/K2 checks once; keep the checks whose presence predicts the key in that cell (logistic filter), drop the rest. Cell-adaptive without touching arena questions. This is the "filtered" step that made the biggest difference in the literature, and it is the mechanism by which the kit adapts to a leaf's actual discriminating signals.

## Restricted domains and arriving domains

- A leaf with 40 train questions still yields a K2 card and K3 neighbours (they need a handful of items) and a K1 catalogue as long as model outputs exist for its questions; the anchor rubric is absent for an unanchored domain (D4) but the kit does not need it. Graceful degradation is measured, not assumed (RK-3 below: kits from 20 / 40 / 80 train items).
- For agent traces without a key, K1 is built from verifier-labelled failures and K4 from a verifier or a stronger agent's run — the same shape; the kit is the reference-free judge's substitute for the key.

## Registered tests (all on R3's 1,980 matches, Mistral, dual order, one session per test; paired McNemar on key-decidable; arms interleaved)

| id | question | arms | cost | pass rule | prediction |
|---|---|---|---|---|---|
| J6 (running) | does authorship or contrastive content change the anchor rubric's value? | Mistral-induced / frontier / contrastive anchor rubric, no reference | ~12k | contrastive > Mistral-induced p<0.05 | null (+0–1pp) |
| RK-1 | does cell CONTENT (K2 card + K3 neighbours) beat the anchor rubric under the STACK-v2 mechanics? | STACK-v2 (anchor rubric) vs STACK-v2 + K2 + K3 | ~4k | +1pp at p<0.05 on all decidable; secondary: gain in Math/Physics/Chemistry/Engineering > discursive | +1–3pp, quantitative-led — the first rubric variant that could beat the anchor, because it supplies facts rather than process |
| RK-2 | does decomposed verification output (K5) beat prose? | STACK-v2 prose vs K5 structured output, same content | ~4k | accuracy ≥ and long-wrong preference lower, ties ≤ 8% | small accuracy gain, larger bias reduction |
| RK-3 | how does the kit degrade in restricted cells? | K2+K3 built from 20 / 40 / 80 train items per leaf | ~6k | gain monotone in items; 20-item kit ≥ anchor rubric | 20 items already ≥ anchor |
| RK-4 | does key-filtering the checks (K6) add value in the cells where the judge is weak? | K5 vs K5-filtered | ~2k train + ~4k | gain in the 6 lowest-S1 anchors > elsewhere | modest |

Honest prior: after four nulls on rubric text, the expected total gain of the kit over STACK-v2 is +1 to +3pp on keyed questions, concentrated where the judge is weak and the content is checkable; its real payoff is the reference-free setting, where K1–K3 are the only verification material available.

## Build plan
- `tools/analysis/rubric_kit.py`: `--induce` builds K1 and K2 per leaf of bareq512_s42 on the reasoning model from train-side material only (2 calls per leaf, ~175 calls); `--neighbours` precomputes K3 (zero calls); `--judge` runs RK-1 (STACK-v2 mechanics + kit) with its own cache; `--analyze`.
- Registration lines above are the commitments; outcomes append below.
