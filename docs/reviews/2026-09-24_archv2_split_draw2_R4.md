# R4 post-draw review: ARCH-V2-SPLIT-DRAW-2 (draw 5a3e756, seed "ARCHV2-SPLIT-2:2929bd46aa271d883050bfe735f96e621ed55fd2")

Reviewer: adversarial-reviewer, 2026-09-24. Zero judge calls. Single process, read-only: every DB opened `mode=ro&immutable=1`, and every REG DB re-hashed unchanged afterwards (hashes and mtimes below).

## VERDICT: R4 MET. The split of record stands as drawn.

I re-derived the whole split with the reviewer's own third implementation, pointed at the REG corpora and the registered seed. The deliberate difference from the builder's code is shingle identity: exact token tuples, not packed ids or sha256. It agrees with the sealed split and with the committed side TSV on every one of the checks below:
- U;
- the P, O and D edges;
- the components and their ids;
- the strata;
- the side of every one of the 20,544 items;
- the pool ids.

The committed TSV re-hashes row by row to its table_sha, and it equals the sealed `side` table in every row.

The purpose of the redraw holds, checked two ways:
- no EVAL item shares a rare (unmasked) run of 20 or more tokens with any TRAIN or GATE item: 0 pairs;
- the same result holds on the texts that generation-side code can actually read, the variant stems and source_row texts of the views: 0 pairs.

No defect affects the split. Two LOW notes on the record: N1 (rendering of two committed files) and N2 (pre-launch evidence that is only the operator's word).

## Data objects

Hashes, taken at the start of the review and re-taken at the end, all unchanged:

| file | sha256 |
|---|---|
| corpus_v2_mmlu_pro_v2.db | c8afeaa615bd962d... |
| corpus_v2_union_mc6.db | 21d79e8cd53cd7ac... |
| split_v2_REG_ARCHV2-SPLIT-2_2929bd46....db | a4e8a1362818c424... |
| gen_view_REG.db | c2930c609c67d6c7... |
| eval_view_REG.db | e35b751887820583... |

- **Corpora.** The two corpora are byte-identical to the DEV builds ED5 and ED6, which the READY verified.
- **Committed files at 5a3e756** (blob / sha256-lf16):

  | file | blob | sha256-lf16 |
  |---|---|---|
  | manifest | 715e117b | 912eaa5fed6910b8 |
  | side TSV | 716b3b84 | 47e9048bb09a6910 |
  | transcript | c555e900 | 75c9c800f78d659e |
  | gates | 44125328 | 19fc6c02a502031d |
  | runlog | ec277554 | 0753367a774c4a38 |

  The manifest's full sha256 is 912eaa5f..., as the coordinator reported.

## Per-check table

Scripts are in the session scratchpad `...\scratchpad\ckv2\`:
- `load_reg.py`, `third_reg.py`: the READY's `third.py`, pointed at the REG corpora;
- `r4.py`, output in `r4_out.txt`;
- `g2_r4.py`, output in `g2_r4_out.txt`;
- `relax.py`.

| # | check | result | mine | draw / claim |
|---|---|---|---|---|
| 1a | U | CONFIRMED | 840 excluded, digest e3d291d0042cf044..., universe 20,544. Equal to the `excluded_u` table as a set. | 840 / e3d291d0... |
| 1b | P, O and D edges | CONFIRMED | P 2,710, O 62, D 1 group; band 2,773 / 59. Equal to `closure_edge` as sets. Edge-set sha16 a4c613ed2d4957ad. | same; meta edge_set_sha16 a4c613ed2d4957ad |
| 1c | Components | CONFIRMED | 18,800. The component_id differs for 0 of 20,544 items. | 18,800 |
| 1d | Strata | CONFIRMED | The (stratum_source, stratum_domain) pair differs for 0 of 20,544 items. There are 52 strata. | 52 |
| 1e | The side of every item under the registered seed | CONFIRMED | 0 of 20,544 differ. EVAL 6,153 / GATE 2,033 / TRAIN 12,358 items; 5,642 / 1,883 / 11,275 components; EVAL share 0.2995. | the same |
| 1f | Pool ids | CONFIRMED | Recomputed as "pv2_" + sha256(sorted EVAL component ids joined by LF)[:16]: all corpora pv2_1575de61bb20e977 (5,642). mc6 gives the same id, with 6,153 EVAL items. mmlu-pro-v2 pv2_41dbd3dbcd399df0 (3,400 components / 3,492 items). | the same |
| 2 | The committed TSV, row by row | CONFIRMED | 20,544 body rows. The header row equals the `side` columns. 0 rows differ from `SELECT * FROM side ORDER BY item_id`. 0 CR bytes. The sha256 over repr(row) per line, computed from the text, is 75b4662eacf9adeb..., which equals the TSV's header and the transcript. | 75b4662eacf9adeb... |
| 3a | C3 lines in the transcript | CONFIRMED | "BUILD EXIT 0". 14 of 14 [R1] samples read "0 FOREIGN" (counted: 14 sample lines, 14 of them 0). All 4 inputs are UNCHANGED, with values equal to the C2 pins. "[R1] verdict: CLEAN". Manifest: r1_void false, 0 reasons, 0 foreign pids across the samples. Gates: ALL PASS (G1 G2 G4 G5). G2: independent edges equal, 0 side differences, K2 a4c613ed×3, D7 {EVAL 228, GATE 89, TRAIN 523} with 0 absent. | as reported |
| 3b | C1 | CONFIRMED | At HEAD 4cbb743, the parent of 5a3e756, every pinned blob equals 0414fb8's: passage_closure 003d5d4e, build 519c69d9, gates 28876ea9, split a0ed6e06, independent ba7fedf1, common 462ffef3, views 7a0f0ab3, content_closure 1533cb5a, split_side 05224b5a. `git diff --stat 0414fb8 4cbb743` over those paths is empty (0 lines). The manifest's code pins list the same blobs. The transcript shows "dirty paths: none". The seed and registration are the registered pair. | |
| 3c | C2 / C2' | CONFIRMED (C2) / PARTLY (C2') | C2: the runlog's pre-launch shas equal the pins, and the transcript's own [R1] BEFORE lines carry the full shas. C2': the tasklist output, the live probe of `process_snapshot` and 36 GB of free RAM rest on the operator's runlog alone (N2). | |
| 3d | C4 before the draw | CONFIRMED | The first-order commit chain runs d6cdb45 (C4, rulings recorded) -> 093ab1e (merge) -> 4cbb743 (delta recorded) -> 5a3e756 (draw). | |
| 3e | C6 | CONFIRMED | `git log -S "ARCHV2-SPLIT-2:2929bd46" 7cf6284^..5a3e756` lists only record commits and the draw: 7cf6284, d3ab777, fc94b40, d6cdb45, 093ab1e, 4cbb743 and 5a3e756. The only REG_ARCHV2-SPLIT-2 directory is the draw's; its files were created at 20:21-20:23 local, i.e. at launch (18:20:48Z). | |
| 4 | Ratios | CONFIRMED | meta eval_ratio "0.3" and gate_ratio "0.1". All 52 strata follow n_eval = floor(0.30 n + 0.5) and n_gate = min(floor(0.10 n + 0.5), n - n_eval) on component counts: 0 strata off the rule. | 0.30 / 0.10 |
| 5a | Independent G2 | CONFIRMED | Item ids: gen_view 14,391 / eval_view 6,153, 0 in both. Stem keys: 0 in both. The eval_view items equal my EVAL set exactly, and the gen_view items equal my TRAIN+GATE set exactly. Side values: gen {GATE, TRAIN}, eval {EVAL}. The 6,153 rows of gen `eval_key_hash` equal the EVAL item count. I re-keyed every variant stem and source_row text in both views with my own norm-v1 stem_key: 0 keys are shared, and 0 gen texts key to an EVAL item. | |
| 5b | The passage check, the purpose of the redraw | CONFIRMED: **0** | Corpus level (my closure over the universe): EVAL x TRAIN/GATE pairs with an unmasked run of 20 or more tokens: P 0, O 0. View level (the texts in gen_view and eval_view, the registered masks, and a dictionary-based diagonal run, a different method from `third.py`'s numpy scan): 24,161 candidate pairs, **0 with a run of 20 or more tokens, maximum run 19**. | |
| 5c | Residual, disclosed and not joined by design | DESCRIPTIVE | 15-19-token band across the boundary: P 1,142 pairs involving 422 EVAL items (1,096 BBH, 28 MMLU-Pro, 12 MATH, 4 GPQA, 2 IFEval); O 20 pairs, 19 MMLU-Pro EVAL items. With the non-BBH rarity cap relaxed (the BBH rule unchanged), runs of 20 or more tokens across the boundary number: at df > 12, 2 pairs / 2 EVAL items (IFEval 1, MMLU-Pro computer science 1); at df > 40, 72 pairs / 18 EVAL items (philosophy 42 pairs, IFEval 20, chemistry 9, computer science 1). These are shared frames above the registered R 6 and outside the rule. A downstream per-use guard (the INDUCE D1 8-token audit) still applies. | |

## Notes (LOW, record only; neither affects the split)

- **N1.** In the main working tree, `_gates.txt` and `_runlog.txt` are CRLF: 130 and 129 CR bytes, sha256-crlf16 69f58e4aaa741abb and 0965827ce54fafe9. The committed LF renderings, 19fc6c02a502031d and 0753367a774c4a38, are the renderings of record. Stripping the CRs reproduces them. The manifest, TSV and transcript are LF in the working tree. Any pin of these two files must name its kind.
- **N2.** Part of the C2' evidence exists only as the operator's runlog lines: the tasklist output, the `process_snapshot` probe and the free RAM figure. It is corroborated by the build's own launch sample ("0 FOREIGN" at 18:20:48Z) and by R1 CLEAN over all 14 samples.
- **Not committed.** `_build.log` and `_gates_run.log` sit beside the committed files; `git status` does not list them, which is consistent with an ignore rule. Their content is duplicated by the transcript and the gates file.

## What this licenses

The split of record for forward use is ARCH-V2-SPLIT-DRAW-2:
- pools pv2_1575de61bb20e977 (all corpora + mc6) and pv2_41dbd3dbcd399df0 (mmlu-pro-v2);
- views gen_view_REG c2930c60... and eval_view_REG e35b7518....

Under CONTEXT rule 12 it may be called content-closed under CK-CLOSE-v2, with the 15-19-token band and the frames above R 6 (row 5c) disclosed. The downstream re-pins (the stage-1 anchor re-draw under a new registered seed, PILOT-K46, the G22 re-run, INDUCE-SELECT-1 / INDUCE-RUBRIC-1) may proceed by insertion.
