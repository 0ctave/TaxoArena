# DRAFT registration (not registered; zero calls; nothing run) — BZ-MMLUPRO-MOREMODELS: does the MMLU-Pro `L3a | L2` NOT SUPPORTED of BZ-METER-AXIS hold on a roster of about 310 further Open LLM Leaderboard v2 models? (a RE-TEST, NOT fresh)

Status: DRAFT by the registrar, 2026-10-21, `_as_of 37a83396`. It becomes a registration only when the reviewer's
pre-data READY and the author's answer to Q1 (end of file) are in, and it is appended to `docs/judge_v2_program.md`
as `## Registered <date> (before any code or call) — BZ-MMLUPRO-MOREMODELS: ...`. No code before then. Edits before
that commit are insertion-only brackets `[D<n>]`.

Authority: the author, `docs/agents/author_decisions/2026-10-21.md` (37a83396), D-2026-10-21-2, verbatim: "I don't
have enough storage for now for 110GB but i'd like to do both" (read by the main session as: go for both; MMLU-Pro
raw files streamed one at a time and deleted after their compact part is written, about 1 GB working space; only the
compact parts kept and backed up; zero LLM calls).

Sources (copied, not re-derived): benchzoom `docs/meter_axis_registration.md` (blob 5de17ff1, LF) and
`docs/meter_registration.md` (blob 5c457088, LF); `docs/reviews/POSTRUN_BZ-METER-AXIS.md` (1260cf3a); programme
section "## BZ-METER-AXIS (2026-10-20, 0 calls) — VALID (POSTRUN 1260cf3a): ..." (L25482-L25492 `_as_of 37a83396`);
the Open LLM Leaderboard `contents` dataset, revision 9c09a7cae43334062a82cb164f2ef255013dafa2 (cached under
`E:/benchzoom_cache/hf/oll_contents`).

## Question

On the same 11,994 MMLU-Pro items, the same axis_v1 tree and the same meter as BZ-METER-AXIS, with a roster of new
models disjoint from the 24 already cached, is `G(L3a | L2)` still NOT SUPPORTED?

## Hygiene

- NOT FRESH, stated in every quotation: the items are those whose text built the axis_v1 tree (all 11,994, vault
  included) and on which BZ-METER v2 and BZ-METER-AXIS read responses; L2 (`category x src`) is the declared label of
  record. New is only the RESPONSES of models never read by the meter.
- Roster disjoint from the 24 models whose MMLU-Pro responses are cached (`E:/benchzoom_cache/hf/mmlu_pro_models.csv`,
  23 + QwQ-32B): no response the meter has read is read again.
- Split: the BZ-METER split of record (parent Section 7.1 id lists, sha256 5c05640d... for the MMLU-Pro vault id
  list; Section 7.2 near-duplicate drop, dropped-list sha256 4cd9a0a8...): fits on the 7,197 WORK items, scored once
  on the 4,654 kept vault items. This reads NEW responses on the BZ-METER vault ITEMS: under D-2026-10-20-4 ("Go
  with your recommendation, wait for fresh data": no further opening) it is disclosed as the FOURTH read of the vault
  items and the first with new responses only; whether D-2026-10-21-2 covers it is the author's (Q1).
- Before READY: the selection may read only the `contents` aggregates (the `MMLU-PRO Raw` column, for the floor);
  no per-item details file is opened. The frozen roster (fullname, precision, details revision) is committed in the
  census before any download.
- Stream-and-delete (D-2026-10-21-2): one raw details file at a time; its compact part (item id, model, correct;
  parquet) is written and sha-pinned, then the raw file is deleted; compact parts backed up to
  `E:/TaxoArena_backup_<date>_mmlupro_moremodels` with SHA256SUMS; never committed.
- Gates: READY-1 (pre-data: registration, code, synthetic gate, census) authorises the download and the WORK dry
  run; `[A1]` Support re-cut at the WORK-selected tau^2 of the full WORK fitting set (POSTRUN_BZ-METER-AXIS D2); READY-2
  authorises the one vault-item read into a new directory.

## Instrument

- Calls: 0 LLM calls; no judge (not a judged test).
- Data: Open LLM Leaderboard v2 MMLU-Pro details (5-shot, log-likelihood over the 10 options; the harness of the 23
  cached models). Outcome = per-item `acc`.
- SELECTION RULE (fixed now, applied to `contents` revision 9c09a7ca... in this order): (1) `Official Providers` ==
  true; (2) `Merged` == false and `Type` not "base merges and moerges" and not "other"; (3) `Flagged` == false; (4)
  one precision per `fullname`: bfloat16, else float16, else the rest; (5) `MMLU-PRO Raw` >= 0.12 (chance 0.10); (6)
  **cap 3 per `Base Model`**, the kept 3 = the lowest sha256(fullname) (outcome-blind); (7) drop the 24 cached models;
  (8) drop a model whose details dataset is missing or covers fewer than 99% of the 11,994 items (census, before any
  details file is parsed for values: coverage from the row count only).
  Registrar's count at that revision (metadata only): 452 rows after (1)-(3), 356 after (4)-(5) (281 Base Model
  values), 335 after the cap 3, 312 after (7). For comparison: cap 1 -> 262, cap 2 -> 295, cap 5 -> 322, no cap -> 333
  (after (7)). Why 3: it removes the fine-tune clusters (Mistral-7B-v0.1: 16 -> 3) while keeping a family's base,
  instruct and one variant; note `Base Model` equals the model itself in 228 of the 356, so the cap is a light
  cluster trim, not a family dedup.
- Tree and meter: the axis_v1 MMLU-Pro pickle (sha256 e1d0b00a..., tree.csv 57050563...), L3a = `category | leaf`,
  L2 = `category x src` (91 cells), the parent's backbone, chain, S-TAU, [R15], statistic, [R18] harness; null = leaf
  permuted within category, R = 200, seed stream `[20261021, 18, r]`; the BZ-METER-AXIS runner path
  (`examples/meter_axis.py`) with the roster as the only new input; synthetic gate = Section 9 `AXIS_FIXTURES`
  unchanged. Guards as BZ-METER-AXIS Section 10 (blob pins, clean code, write-once outputs to a new directory,
  refusal of `meter_v1`, `meter_v2`, `meter_axis_v1` paths).
- Control of record: L2 (deciding parent).

## Readouts and criteria (x 1e-3 nats per model x item cell; scored on 4,654 kept vault items, 4,625 clusters)

1. **C-P1 (DECIDING; family of 1):** `G(L3a | L2)`, new roster (about 312). Word by the parent's [R2] precedence,
   applied ONCE to the point with its SE (the POINT against 3 SE, q95 and delta_min = 0.10 decides; no interval
   clause, rule 7). FAILS as "the NOT SUPPORTED holds" if SUPPORTED, BELOW INTEREST or INCONCLUSIVE is printed.
2. **C-P2 (secondary):** `G(L3a | L1)` (L1 = 14 categories), new roster.
3. **C-P3 (secondary):** C-P1 on the weak half (models with WORK accuracy below the roster median, frozen from WORK
   rows before the vault read; the analogue of the MATH 22-model set).
4. **C-P4 (sensitivity, no word):** C-P1 without reasoning-tuned models: fullname matching
   `(?i)(r1|qwq|reason|think)` (list printed in the census).
5. Descriptive: C-P1 side by side with the 23-model value (-0.0059, SE 0.0183); the [R18] harness.

## Support

(a) DECIDING denominator: C-P1, 4,654 kept vault items, 4,625 twin-component clusters (Kish mean cluster size
4,654 / 4,625 = 1.006), roster about 312 models.
(b) DEFF 1.13, MEASURED on this corpus's own cache: the MMLU-Pro `L3a | L2` vault readout of BZ-METER-AXIS (n_eff
4,134; POSTRUN_BZ-METER-AXIS claim 5); same items, clusters and reader.
(c) n_eff = 4,134 (copied).
(d) SE reported: the measured 0.0183, carried with NO credit for the larger roster (conservative). Arithmetic of the
credit not taken: 0.0183 x sqrt(23 / 312) = 0.0183 x 0.2715 = 0.0050 (an optimistic bound, not of record; model
offsets are not independent and the S-TAU tau^2 is re-selected).
(e) MDE80 = 3.84 x 0.0183 = 0.0703, against delta_min 0.10.
(f) VERDICT: **SCOREABLE**: the prediction (point 0.00) is 0.10 from the bar, above MDE80 0.0703. If the [A1] re-cut
gives a vault MDE80 >= 0.10, C-P1 is recorded DESCRIPTIVE-ONLY by insertion before the vault-item read.
(g) STRUCTURAL leg: at infinite budget SUPPORTED is reachable iff the true gain over `category x src` is >= 0.10 on
this roster (no construction caps it: the leaves cross `src` cells inside a category); NOT SUPPORTED is reachable for
any true g < 0.10. PASSES.

## Predictions

Honest prior: the 23-model read was powered (MDE80 0.0703) and found -0.0059; WORK A6 found -0.010 (SE 0.021); more
models add weak and near-chance models whose item structure is thin.

| id | line | interval | point | word set |
|---|---|---|---|---|
| PP1 | C-P1 (deciding) | [-0.020, 0.050] | 0.00 | NOT SUPPORTED, DEGENERATE |
| PP2 | C-P2 `L3a\|L1` | [0.100, 0.500] | 0.20 | SUPPORTED (secondary), INCONCLUSIVE (secondary) |
| PP3 | C-P3 weak half | [-0.030, 0.080] | 0.01 | NOT SUPPORTED (secondary), DEGENERATE (secondary), INCONCLUSIVE (secondary) |
| PP4 | C-P4 minus C-P1 | [-0.020, 0.020] | 0.00 | range only |

## Falsifier

C-P1 SUPPORTED fires it: it overturns BZ-METER-AXIS MMLU-Pro NOT SUPPORTED as a statement about MMLU-Pro (it would
then hold for the 23-model roster only, i.e. a roster-size or roster-composition effect).

## What it can and cannot conclude

CAN: whether the powered MMLU-Pro null survives a roster about 13 times larger on the same items (a roster-power
re-test). CANNOT: be a fresh confirmation (items, tree text and the declared label are those of the original read;
the vault items are read a fourth time); speak for generative or chain-of-thought evaluation. REASONING-MODEL
HANDICAP: 5-shot log-likelihood scores the option letter without letting a model reason, so reasoning-tuned models
are scored off their trained mode, most where the item needs computation; their per-item pattern then mixes ability
with a format penalty that may itself cluster by text leaf (computation-heavy vs recall leaves). A gain driven by
those models is a harness interaction, not a capability structure: C-P4 shows its size, it decides nothing.

## Cost and consequence

0 LLM calls; about 312 x 0.36 GB streamed (about 1 GB working space), about 312 x 5 MB compact kept on E:; CPU meter
fits about 13 times the 23-model cell count. Consequence: NOT SUPPORTED again strengthens the MMLU-Pro null as
roster-general on this harness; SUPPORTED restricts it to the 23-model roster.

## Open questions

- Q1 (author): reading new models' responses on the BZ-METER vault ITEMS: is it covered by D-2026-10-21-2 or barred
  by D-2026-10-20-4? (Alternative that avoids the vault items: fit and score by a 5-fold cross-fit on WORK only,
  7,197 items, a different statistic from the registered one.)
- Q2 (reviewer): cap 3 per `Base Model` given the self-referencing column; the reasoning-model regex.

[D1 2026-10-21 by the registrar: SUPERSEDED as text by the registration of record, docs/judge_v2_program.md section "## Registered 2026-10-21 (before any code or call) — BZ-MMLUPRO-MOREMODELS: ..." (L25562-L25614 _as_of the commit that writes it, parent 8948b9ed), with M1-M7 of docs/reviews/READY_BZ-MMLUPRO-MOREMODELS.md (5109ef9c) applied; roster = the downloaded cap-8 set (D-2026-10-21-4, 8948b9ed); Q1 answered by D-2026-10-21-3. This draft is not the registration.]
