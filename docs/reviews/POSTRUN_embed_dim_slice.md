# POSTRUN review — EMBED-DIM-SLICE (run 54ea7329, script blob 068550b4)

Reviewer: adversarial-reviewer, 2026-10-01. Zero calls. Read-only on every input and output.
Object: `experiment_results/embed_dim_slice/` as committed in 54ea7329 (outcome.txt, run_log.txt, nmi_matrix.csv 240 data
rows, s_table.csv, h_table.csv, selection.json) against the registration (prog L22579-L22607) and the registrar's brackets
(L22719-L22723; READY C1-C4, `docs/reviews/READY_embed_dim_slice.md` d26afd88).

## Verdict

**VALID.** DS1 = **REOPEN-CANDIDATE** (gemma BETTER on MASSIVE and Banking77; CLINC NEITHER); **F-DS FIRED**. Every
deciding number reproduces to the printed digit from `nmi_matrix.csv` plus the printed BASIC CIs (C2 discharged). Wording
conditions W1-W5 below bind every downstream sentence (results JSON, INDEX, thesis, plan).

## Deciding claims

| # | Claim (outcome.txt) | Mine (own script, nmi_matrix.csv) | Status | Sev |
|---|---|---|---|---|
| 1 | GATE score qwen3 {256 .85697, 512 .85700, 1024 .86340, 4096 .86247} -> d_q* 1024 | .85698 / .85700 / .86340 / .86247 -> 1024 (rule: smallest d with score >= max-0.001; 4096 sits 0.00093 below max, 1024 is the max) | CONFIRMED (last-digit rounding on 256) | - |
| 2 | GATE score gemma {256 .88529, 768 .88752} -> d_g* 768 | .88529 / .88752 -> 768 | CONFIRMED | - |
| 3 | ORDER: selection.json sha f1b508cf... at event 0, before 20 EVAL reads | sha256(selection.json) = f1b508cfa889021e6a4d8dac5e82a2188399373996818db0d622aad076bf400d = ORDER line; run_log L14 (SELECTION written) precedes L15 (IDENTITY, first EVAL use); `eval_idx` refuses any EVAL index before `selection_sha` is set (L205-L211); the order refusal at L668-L670 is the READY-reviewed guard | CONFIRMED | - |
| 4 | IDENTITY: D256 +0.03340 / -0.00691 / +0.05628; S seed 0 0.7598 / 0.8262 | D256 from the CSV: +0.03340 / -0.00691 / +0.05628; s_table S_seed0 qwen3@256 0.759777, gemma@256 0.826195 | CONFIRMED | - |
| 5 | MASSIVE D* +0.03329; spreads q@1024 0.01428, g@768 0.01277; bar 0.01428; BASIC [+0.02961, +0.03998] -> BETTER | +0.03329; 0.01428 / 0.01277; bar max(0.00759, .01428, .01277) = 0.01428; D*>bar and lo>0 -> BETTER | CONFIRMED | - |
| 6 | CLINC D* -0.00244; spreads 0.00417 / 0.00968; bar 0.00968; BASIC [-0.00560, -0.00048] -> NEITHER | -0.00244; 0.00417 / 0.00968; bar 0.00968; |D*| < bar -> NEITHER (not WORSE: point clause fails) | CONFIRMED | - |
| 7 | Banking77 D* +0.04386; spreads 0.01043 / 0.01216; bar 0.01216; BASIC [+0.04108, +0.04990] -> BETTER | +0.04386; 0.01043 / 0.01216; bar 0.01216 -> BETTER | CONFIRMED | - |
| 8 | VERDICT REOPEN-CANDIDATE (2 of 3); F-DS FIRED | 2 BETTER -> REOPEN-CANDIDATE; F-DS fires iff REOPEN-CANDIDATE | CONFIRMED | - |
| 9 | Support: n_eff 4900 / 6672 / 3902; MDE80 = 2.8 x SE 0.00759 / 0.00362 / 0.00637 | 4946/1.0093 = 4900.4; 6672; 3908/1.0015 = 3902.1; 2.8 x printed SE = 0.00759 / 0.00361 / 0.00636 (gap <= 0.00001, SE printed rounded); MDE never binds the bar (spreads 1.9-2.7x MDE80) | CONFIRMED | - |
| 10 | Input pins unchanged before/after | sha256 now: ingest 487e0093..., qwen3 9e100e04..., gemma b187b82f... = registration pins; mtimes 2026-09-30 00:59 / 10-01 05:55 / 10-01 06:39, all before the run (18:50); 0 -wal/-journal files beside them (`ls -a | grep -c`) | CONFIRMED | - |
| 11 | Script of record | `git hash-object tools/analysis/embed_dim_slice.py` = 068550b4f7a5a918b9bd1f3e9c2ae4e4a86a9b44 (LF) = `git rev-parse 54ea7329:tools/analysis/embed_dim_slice.py`; last commit touching it 91e738d7 (the merge) -> C1 met; S0 machinery f662ceb1 | CONFIRMED | - |
| 12 | TRAIN-ONLY: 186 fits on TRAIN, 0 with an EVAL row | taken from the READY-reviewed audit (`ITS.fit_audit`), not re-derived | CONFIRMED by citation | - |

Descriptive (spot-checked, never deciding): DS2 points recomputed from the CSV match all 12 printed values (e.g. Banking77
qwen3 1024-256 +0.00909; CLINC gemma 768-256 +0.00459). DS3 +0.03650 and DS4 H not recomputed (no per-variant / per-draw
data in the outputs); h_table.csv equals the outcome's DS4 lines.

## Robustness (descriptive; my script, point-only, own in-run bar per arm)

D*(gemma@768 - qwen3@d) by qwen3 slice: MASSIVE +0.03459 / +0.04231 / +0.03329 / +0.03298 (d 256/512/1024/4096), each
above its own bar (0.02463 / 0.01703 / 0.01428 / 0.02702); Banking77 +0.05295 / +0.04618 / +0.04386 / +0.04695, each above
its bar; CLINC inside its bar at every slice. The qwen3 selection was a near-tie (1024 vs 4096 by 0.00093), but the 2-of-3
classification does not depend on which qwen3 slice was picked, including the tree slice of record 512 (point clause only;
the CI clause was not computed for the non-selected arms).

## Defects / notes

- **N1 (MEDIUM, wording).** CLINC's BASIC CI lies wholly below 0 ([-0.00560, -0.00048]) while the percentile CI straddles 0
  and the point sits inside the seed-spread bar. NEITHER is the registered status. Fix: never write "gemma worse on CLINC" or
  "parity on CLINC"; write "CLINC NEITHER (inside its seed-spread bar 0.00968)".
- **N2 (MEDIUM, wording).** The slice explains part of the Banking77 edge: D falls from +0.05628 (256/256) to +0.04386
  (1024/768), and DS3 S falls from +0.0664 (SLOTSWAP M3, seed 0) to +0.03650 (seed mean). Fix: "survives", never "unchanged" or
  "the slice plays no role".
- **N3 (LOW).** s_table seed_spread for qwen3@1024 and gemma@768 are both 0.029795. Not a bug: S is a mean over 3,222
  variants and 0.029795 x 3222 = 96.0, the same lattice step; `ds3()` computes the spread per arm (L469).
- **N4 (LOW, descriptive).** DS4 H is flat across qwen3 slices 512-4096 (0.440163 MASSIVE, 0.174655 CLINC), so P6b
  "non-decreasing" OCCURRED partly through ties; gemma@MASSIVE's interval has its lower bound at the point (0.876308). The
  "dropped labels 280" unit (labels x draws?) is not stated. Fix: the registrar records P6b with "(ties)" and does not quote DS4
  beyond DESCRIPTIVE-ONLY.
- **N5 (LOW).** Support (f) planned MASSIVE as DESCRIPTIVE-ONLY at P3's point (planning bar 0.0246); the in-run bar of record
  (0.01428) made it SCOREABLE. This is the registered rule (bar of record = in-run spread), not a criterion change; no
  substitution (C-7 clean).

## Wording conditions (bind every downstream text)

- **W1.** Reading of record, verbatim: "gemma's fine edge survives the slice confound on >= 2 of 3 corpora" with the scope
  "at each embedder's GATE-selected slice (qwen3 1024, gemma 768), MASSIVE and Banking77 BETTER, CLINC NEITHER".
- **W2.** Every sentence carries both confounds: quantisation (qwen3 Q4_K_M vs gemma BF16) and prompt protocol (RAW on both
  sides) UNCONTROLLED. The result does not separate the embedders from their quantisation.
- **W3.** "This test alone never changes the embedder of record." D3 (keep qwen3, gemma secondary) stands; its revisit is the
  author's, under checkpoint B (CARD-PROTOCOL CP1 HELD AND F-E1 not fired). REOPEN-CANDIDATE is a candidate, not a reopening.
- **W4.** DS2-DS4 DESCRIPTIVE-ONLY. d_q* = 1024 != 512 is RELAYED to the tree specialist and changes nothing of record (NMI vs
  gold, not certification). Intent corpora only: nothing about MMLU-Pro.
- **W5.** F-DS FIRED overturns only the working hypothesis "S0's gemma edge is a slice artefact"; no recorded number is
  revised. Per the registered Out of scope, EMBED-QUANT's recommendation trigger ("only if EMBED-DIM-SLICE or CP1 reads
  REOPEN-CANDIDATE") is now MET; the download and the go remain the author's.

## Commands

```
# deciding recomputation (scratchpad/pr.py; read-only on the CSV/outcome):
#   per-arm seed means/spreads from nmi_matrix.csv (240 rows; 90 fine GATE, 90 fine EVAL, 60 coarse; all 5 seeds per key asserted)
#   GATE score = mean over 3 corpora of seed-mean GATE fine NMI; d* = min d with score >= max-0.001
#   D* = mean(gemma@768 EVAL) - mean(qwen3@1024 EVAL); bar = max(MDE80 printed, spread_q, spread_g)
#   status: BETTER iff D*>bar and BASIC lo>0 (BASIC parsed from outcome.txt); WORSE symmetric; else NEITHER
python scratchpad/pr.py   -> qwen3 d* 1024, gemma d* 768; massive +0.03329 bar 0.01428 BETTER; clinc -0.00244 bar 0.00968
                             NEITHER; banking77 +0.04386 bar 0.01216 BETTER; REOPEN-CANDIDATE 2; sel sha f1b508cf...; D256 identity
sha256sum intent_transfer_corpora_v1.db intent_emb_qwen3.db intent_emb_gemma.db   (repo root = TAXOARENA_DATA_ROOT default)
ls -a | grep -E '^intent_.*-(wal|journal)$' | wc -l            -> 0
git hash-object tools/analysis/embed_dim_slice.py; git rev-parse 54ea7329:tools/analysis/embed_dim_slice.py   -> 068550b4 both
git log --oneline -3 -- tools/analysis/embed_dim_slice.py      -> 91e738d7 only
sed -n 200,215p / 660,680p / 457,471p tools/analysis/embed_dim_slice.py   (EVAL gate, ORDER refusal, ds3 spread)
python (inline) D* at every qwen3 slice vs gemma@768 with own bars   -> robustness table above
python -c "print(4946/1.0093, 3908/1.0015, 0.029795*3222)"     -> 4900.4, 3902.1, 96.0
```
