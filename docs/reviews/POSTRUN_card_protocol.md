# POSTRUN review: INTENT-S0-CARD-PROTOCOL (run 3898a2ec)

Reviewer: adversarial-reviewer, 2026-10-02. Zero calls, zero embeddings. All DBs opened `mode=ro&immutable=1`.
Reviewed: `experiment_results/card_protocol/outcome.txt` + `readout_run.txt`, `nmi_card.csv`, `s_card.csv` (commit 3898a2ec),
against the registration ("## Registered 2026-10-01 (before any code or call) — INTENT-S0-CARD-PROTOCOL: ...", prog L22655-L22680
_as_of 3898a2ec) with its brackets (4ef4faad: C-CP-1 shifted point, CB1/CB2/CW1-CW3, D3, D4; c72925d3: C-CP-3 pins).
Blobs (LF, `git hash-object`): card_protocol.py cdcc1dbb4ece15b1, card_protocol_writer.py 2788d7214df86dd8, intent_transfer_s0.py
f662ceb19738f515: equal to the READY pins. DB sha256-bytes before AND after this review: qwen3_card e8dd85afc2afc075, gemma_card
9396cb1bbb2352cb, qwen3 9e100e04fc91b137, gemma b187b82f90ce9837, ingest 487e0093719c184c (equal to the pins; no -wal/-journal).

## Verdict: VALID, with wording conditions W1-W6

CP1 KEEP-STRONG and CP2 NOT SHOWN (F-CP2 FIRED) reproduce to the digit from the caches. The data are valid: same text keys in
all four DBs, the right prompt on the right file (meta + writer T4 execution), the CARD vectors are aligned to their texts in every
corpus (Banking77 included), and the Banking77 swings survive a k-means-free check. The printed "CB9 ... no shifted-points bracket" line
is stale; scoring against the 4ef4faad bracket changes no prediction's status.

## Per-claim table (deciding claims)

| # | Claim (outcome) | Reviewer | Status | Sev |
|---|---|---|---|---|
| 1 | 60 EVAL fine NMIs (4 arms x 3 corpora x 5 seeds) | my own re-implementation of the fits (TRAIN-only, slice + renormalise, k-means++ D^2=1-cos, seeds 0-4) + sklearn arithmetic NMI: max abs diff 4.9e-07 over 60 fits | CONFIRMED | - |
| 2 | CP1 MASSIVE D_card -0.03238, bar 0.01120 (qC spread), WORSE | -0.03238; spreads qC 0.01120 gC 0.00755; my CI [-0.03819, -0.02636] (claimed [-0.03801, -0.02619]); SE 0.00307 (0.00300) | CONFIRMED | - |
| 3 | CP1 CLINC -0.03388, bar 0.01262, WORSE | -0.03388; qC 0.01262 gC 0.01239; CI [-0.03851, -0.03205] ([-0.03861, -0.03196]); SE 0.00167 (0.00169) | CONFIRMED | - |
| 4 | CP1 Banking77 +0.11826, bar 0.01991, BETTER | +0.11826; qC 0.01991 gC 0.01165; CI [+0.11728, +0.12975] ([+0.11690, +0.12971]); SE 0.00324 (0.00329) | CONFIRMED | - |
| 5 | CP1 VERDICT KEEP-STRONG (BETTER 1 of 3, WORSE 2 of 3) | same; KEEP holds even with MASSIVE removed (BETTER <= 1); KEEP-STRONG needs MASSIVE (see W2) | CONFIRMED | - |
| 6 | CP2 per corpus +0.04875 / -0.00308 / -0.09064; D-bar -0.01499 | identical | CONFIRMED | - |
| 7 | CP2 bar_pool 0.01560, CI [-0.01885, -0.01319], NOT SHOWN | spread term (0.01428+0.01262+0.01991)/3 = 0.01560 > MDE80 0.00401; my CI [-0.01900, -0.01321], SE 0.00145; D-bar > -bar_pool by 0.00061, so NOT HURTS; upper < 0, so not HELD -> NOT SHOWN | CONFIRMED (thin, W4) | - |
| 8 | F-CP2 FIRED; F-CP1 NOT FIRED | follows from 5 and 7 under the registered FALSIFIERS line | CONFIRMED | - |
| 9 | Support: Kish 1.0093 / 1.0000 / 1.0015, n_eff 4900 / 6672 / 3902; MDE80 = 2.8 SE | re-measured from the ingest's stem_key components: identical; 2.8 x 0.00300 = 0.00840, x 0.00169 = 0.00473, x 0.00329 = 0.00921, x 0.00143 = 0.00400 | CONFIRMED | - |
| 10 | IDENTITY: RAW arms reproduce EMBED-DIM-SLICE | my RAW seed NMIs equal the csv; seed means 0.76554 / 0.92810 / 0.84900 and 0.79883 / 0.92566 / 0.89286 | CONFIRMED | - |
| 11 | "CB9: scored as registered, no shifted-points bracket" | FALSE as a statement of record: 4ef4faad bracketed MASSIVE +0.021 [+0.001, +0.041]; the READY (D1) ordered the post-run record to score against it. -0.03238 is outside both intervals: FAILED either way; no status changes (D-1) | PARTLY | LOW |
| 12 | Brier lines | KEEP 0.0625, KEEP-STRONG 0.8100, REOPEN 0.0625, CP2 HELD 0.2025, HURTS 0.0025: recomputed | CONFIRMED | - |
| 13 | CP3 / CP4 (descriptive) | spot check: CP4 -0.01692 / -0.03452 / -0.01623 exact; CP3 S(gemma CARD) - S(qwen3 CARD) = 0.79410 - 0.85990 = -0.06580, R(qwen3 CARD) 0.7199 from s_card.csv | CONFIRMED (spot) | - |

## Data-validity checks (Banking77 swings)

| Check | Result |
|---|---|
| Text identity | the four DBs hold the SAME 57,350 keys (set equality); the 7 ingest texts absent are all `drop_reason = cross_label` (never read). Banking77 texts are read by identical keys from RAW and CARD; 12 Banking77 texts carry lead/trail whitespace, identical in both. |
| Right prompt, right file | meta: qwen3_card prompt_sha256 e92a9484..., model qwen3-embedding:latest digest 64b93349 (= S0 RAW); gemma_card 11ab9b67..., embeddinggemma digest 85462619 (= S0 RAW); writer prefix = `card_arm(e).prefix = PROMPTS[e]`. Execution evidence: qwen3 T4 re-embedded 20 stored rows WITH the qwen3 prefix at cos min 0.999147 (bar 0.9980); T2b cos(CARD,RAW) < 1 (0.78 median) shows a prefix was applied. |
| Alignment (resume at 51,008) | pairwise-similarity correlation CARD vs RAW on 20k random EVAL pairs, aligned / shuffled: qwen3 0.610 / 0.596 / **0.702** (Banking77) vs shuffled <= 0.015; gemma 0.726 / 0.719 / 0.733. Centred self-retrieval qwen3 0.336 / 0.312 / 0.602, gemma 0.928 / 0.924 / 0.960. Rows written after rowid 51,008 (6,342: 1,430 Banking77) have the same self-retrieval as the earlier rows (0.386 vs 0.377 Banking77). Banking77 is the BEST-aligned corpus for qwen3: no misalignment. |
| k-means-free check | TRAIN fine-label centroids -> EVAL nearest-centroid accuracy, Banking77: qwen3 RAW 0.8866 -> CARD **0.8055** (-8.1 pp), 1-NN 0.9304 -> 0.8928; gemma RAW 0.9335 -> CARD 0.9168. MASSIVE: qwen3 0.8607 -> 0.8908 (+3.0 pp), gemma 0.8908 -> 0.8668. The swings are properties of the embeddings, not of the k-means seeds. |

The Banking77 qwen3 CARD drop is a real effect of this prompt on this corpus. Why it happens (a generic "virtual assistant" task line
against 77 fine banking intents) is a conjecture; nothing here tests it.

## Defects

- **D-1 LOW (stale printed reading, CB9).** The write-once outcome prints "CB9: scored as registered, no shifted-points bracket", and
  the builder's readings print "CB9 no shifted-CP1-points bracket at build". The READY had ruled CB9 NOT ADMISSIBLE as a reading (D1), and
  4ef4faad bracketed MASSIVE +0.021 [+0.001, +0.041]. Fix (registrar, by insertion in the outcome record): "CP1-P MASSIVE scored against the
  4ef4faad bracket +0.021 [+0.001, +0.041]: -0.03238, FAILED (same status as against the registered point)". No code change is needed.
  Side note: at the bracketed point the IN-RUN Support line would read SCOREABLE (|0.021| - 0.01120 = 0.0098 > MDE80 0.0084), but the
  bracket fixed the (f) word to DESCRIPTIVE-ONLY. That word decides no verdict, because CP1 is a total classification over 3 corpora.
- **D-2 LOW (wording risk, not a code defect).** The outcome's CP2 block prints only the pooled verdict. The per-corpus effects go in
  opposite directions, each far outside its own seed-spread bar: MASSIVE +0.04875 vs bar 0.01428; Banking77 -0.09064 vs bar 0.01991. Fix: W3.

## Wording conditions (bind the registrar's record and any synthesis)

- **W1 (mixed embedder result).** The embedder evidence is MIXED: "EMBED-DIM-SLICE REOPEN-CANDIDATE (RAW protocol) vs CP1 KEEP-STRONG (card
  protocol); relayed as mixed; no wording chosen". Each corpus moves differently. MASSIVE flips because qwen3 gains from its prompt
  (D +0.033 -> -0.032). CLINC turns WORSE because gemma loses from its prompt (gemma CARD - RAW -0.035; qwen3 -0.003). The Banking77 edge
  grows because qwen3 collapses (+0.044 -> +0.118). Never write "qwen3 is the better embedder" or "protocol explains S0's gemma edge"
  (registered: KEEP reads "not shown"). D3's revisit condition (CP1 in the gemma direction) is NOT met; D3 stays the author's.
- **W2 (KEEP-STRONG rests on MASSIVE).** KEEP is robust, but KEEP-STRONG needs MASSIVE's WORSE, and MASSIVE was registered DESCRIPTIVE-ONLY at
  its prediction. Its reading is still clear (-0.03238, 2.9x its bar, CI excludes 0). Write "KEEP-STRONG (MASSIVE and CLINC WORSE; MASSIVE
  DESCRIPTIVE-ONLY at its prediction)".
- **W3 (the prompt effect depends on the corpus).** CP2's NOT SHOWN is a POOLED reading over effects of opposite sign. State it as "card
  prompts did not raise qwen3's fine NMI pooled over the three corpora (D-bar -0.01499); the per-corpus effect is corpus-dependent: +0.049
  MASSIVE, -0.003 CLINC, -0.091 Banking77 (per-corpus values descriptive, no per-corpus criterion registered)". Never write "card prompts
  do not matter for qwen3".
- **W4 (NOT SHOWN, not HURTS, by 0.0006).** D-bar -0.01499 against -bar_pool -0.01560, with the CI wholly below 0. Do not write "hurts";
  write "NOT SHOWN (pooled point inside the seed-spread bar by 0.0006; interval below 0)".
- **W5 (F-CP2 scope).** F-CP2 withdraws "qwen3 is instruction-aware and was run RAW" as a candidate MECHANISM for S0's qwen3 rows, POOLED.
  It stays a disclosure, and the record must add that on MASSIVE the card prompt reverses the sign of the gemma-qwen3 contrast.
- **W6 (scope of every line).** Fine-level k-means NMI on the three intent corpora; qwen3 at d 1024 Q4_K_M ("quantisation: Q4_K_M ~ Q8_0
  (EMBED-QUANT); above Q8_0 untested"); one task line for qwen3, not tuned per corpus; gemma's card clustering prompt; nomic NOT READ (D4).

## Own checks (mutant-equivalent, on deciding paths)

- RM1: the classification computed with MASSIVE excluded gives KEEP (BETTER 1, WORSE 1), not KEEP-STRONG. KEEP is robust; KEEP-STRONG depends on MASSIVE (W2). Decisive for the wording only.
- RM2: CP2 with the bar taken as MDE80 alone (0.00401) would read HURTS. The spread term (registered) decides, so NOT SHOWN is a consequence of the registered bar (W4).
- RM3: a stream-independent bootstrap (seed 20261002) leaves every CP1/CP2 status unchanged; interval ends move by at most 0.0004.

## Commands (scripts in the session scratchpad `rvcp/`; all read-only)

```
sha256sum intent_emb_{qwen3,gemma}{,_card}.db intent_transfer_corpora_v1.db   # before and after: equal to pins
git hash-object tools/analysis/card_protocol.py tools/analysis/card_protocol_writer.py tools/analysis/intent_transfer_s0.py
python rv_cp.py     # key-set equality; 60 fits re-run (own skmeans + sklearn NMI) vs nmi_card.csv: max diff 4.89e-07; D_card, spreads, CP2, CP4
python rv_boot.py   # own component bootstrap B 2000 seed 20261002; Kish DEFF / n_eff from stem_key components; CP1 CIs, CP2 joint CI
python rv_valid.py  # cos(CARD,RAW), self-retrieval, rows after rowid 51008, nearest-centroid and 1-NN accuracy (k-means-free)
python rv_align.py  # centred self-retrieval; pair-similarity correlation aligned vs shuffled
grep -h 'T2b\|T3\|T4\|wrote' experiment_results/card_protocol/writer_*go*.log   # prompt sha, T4 resume parity 0.999147
sed -n '54,66p' docs/reviews/READY_card_proto.md; grep -n 'TRIGGERED on MASSIVE' docs/judge_v2_program.md   # CB9 / C-CP-1 bracket
```
