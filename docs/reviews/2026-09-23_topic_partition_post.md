# Post-run review — TOPIC-PARTITION-20NG (adversarial reviewer, 2026-09-23)

Object. Registration `docs/judge_v2_program.md` L10039-L10399 at 6aa2a0d (range corrected by pre-run bracket (g);
the outcome header still carries the superseded "L10030-L10390"). Pre-run brackets 76e5582 (a)-(d) and 8949550
(e)-(h). READY `docs/reviews/READY_topic_partition_20ng.md` at 2708795. Chain `tools/chains/topic_partition.sh`,
HEAD 8949550; run 2026-09-22 19:29 -> stopped 20:12 by the author, resumed 2026-09-23 03:36, CHAIN DONE 04:43:04,
ACCEPTANCE OK. Zero LLM calls.

Method. Every headline figure below was recomputed by the reviewer with his own scripts from the corpus DB, the
sklearn cache, the snapshot vectors and the site-null CSV — never from the outcome file. DBs opened
`mode=ro` (`immutable=1` for `snapshots.db`, whose WAL is 0 bytes; NOT immutable for
`embeddings_cache.db` / `twenty_newsgroups_cache_v1.db`, which carry a WAL tail). Nothing was written under
`experiment_results/`; no JVM, no build, no site null was started. Scratch only.

Data object, named. Corpus = the ingest DB `twenty_newsgroups_cache_v1.db` (16,921 rows, sha
`fc27ef38…6fa46e75`), NOT an arena pool: p2dca21ab5f4ef3ae and paeec37aa28063c75 are neither read nor written;
`mmlu_pro_dataset_cache_v2.db.twenty_newsgroups` stays at n=0. Split = the corpus's own, seed 42, ratio 0.30,
per label, pool `pf844849e133cda4e`: TRAIN 11,845 / held-out 5,076. Arm of record T1 = `ng_af_s42`
(snapshot `20260922_195728_Headless_Run_Auto_ge`, slice 256, bar 0.025, L = 110 leaves, 101 sites). T1b =
`ng_af_bareq512_s42` (slice 512, bar 0.0145, 100 leaves, 97 sites), site null ABSENT.

---

## 1. Per-claim table

| # | claim (as the outcome states it) | my command / script | my number | verdict |
|---|---|---|---|---|
| 1 | raw 18,846; short 1,808; dup 117 (57 groups, 9 cross-label); kept 16,921; leak 380; NUL 0; >8,000 chars 306; max 158,787 | own reimplementation of norm-v1 over `fetch_20newsgroups(subset='all', remove=('headers','footers','quotes'), shuffle=False, download_if_missing=False)` | 18,846 / 1,808 (9.59%) / 117 in 57 groups, 9 cross-label (0.62%) / 16,921 / 380 ci (371 cs) / 0 / 306 / 158,787 | **CONFIRMED** to the digit |
| 2 | manifest sha `fc27ef38a1b5daedf7d3b07dc48cd53f14d86a4bbd7aa42236a03f756fa46e75` | sha256 over `repr(row)+LF` of `SELECT id,question,category ORDER BY id`, computed **twice**: from the DB and independently from the sklearn kept list | identical both ways; every DB row byte-identical to the sklearn kept row | **CONFIRMED** |
| 3 | held-out 5,076 / TRAIN 11,845 (outcome) vs 11,846 / 5,075 (pre-run bracket (a)) | `sum(min(max(floor(n*0.30+0.5),0),n-1))` per label (the engine's `Math.round`, MMLUDatasetFetcher.splitTrainTest L740) + the snapshot's `reserved_queries` | 5,076 / 11,845; snapshot reserved ids = 5,076 distinct; 0 held-out texts inside any leaf | **5,076 IS RIGHT.** The bracket's 5,075 is a banker's-rounding artefact: `comp.graphics` n=875, 875×0.30 = 262.5; Java `Math.round` = 263, Python `round` = 262. Exactly one document. Bracket (a) already made the build's own number of record, so no criterion moves |
| 4 | C1 rows: tree NMI20 0.5422 / purity 0.6673 (3387/5076) / ARI20 0.1855 / NMI7 0.4009; k-means k=L seeds 0-4; k=20; k=7; Ward 0.5497; HDBSCAN k=3 noise 0.927; permuted null ×5; full-4096 0.5585 | own load of `dag_snapshots.jsonl` + `snapshots.db` graph + `embeddings_cache.db` big-endian f32, own KMeans/Ward/HDBSCAN | **every one of the 21 rows reproduces to 4 decimals** (tree 0.6673/0.5422/0.1855/0.4009; kmeans0 0.6789/0.5442/0.1835; Ward 0.6844/0.5497; HDBSCAN k=3, noise 0.927, NMI20 0.2407; full-4096 0.6913/0.5585) | **CONFIRMED** |
| 5 | headline diff NMI(20) tree − kmeans0 = −0.0020; seed spread 0.0074; bootstrap CI [−0.0081, +0.0036] | own 1,000-resample fixed-partition bootstrap, registered seed 20260922 **and** my own seed 777 | −0.0020 / 0.0074 / [−0.0081, 0.0036] at the registered seed; [−0.0084, +0.0039] at my seed | **CONFIRMED**, seed-robust |
| 6 | C1 FAILED, F1 fires; F1' does not fire | rule read off the registration | diff (−0.0020) < spread (0.0074) **and** CI covers 0 → HELD clause fails on both conjuncts; F1' needs diff < −0.05 with CI excluding 0 → far from firing | **CONFIRMED.** C1 correctly FAILED, F1 fires as registered |
| 7 | the k-means-on-FULL-4096-d row 0.5585 | registration I6 Q1: "one sensitivity row k-means at k = L on the FULL 4096-d vectors" | permitted **as a REPORTED sensitivity row, not as a C1 comparator** — C1's comparator is pinned to `kmeans0` at the arm's slice | **CONFIRMED as registered.** Caveat: the tree is 0.0163 NMI below that row, i.e. more than the seed spread; that contrast is *beside*, must never be promoted to a C1 reading (criterion substitution, C-7) |
| 8 | C2: 16 certified / 85 uncertified of 101 sites; raw gap +0.1215 (20) / +0.1206 (7) | own read of `site_null_ng_af_s42.csv` + own per-site child-partition NMI | 16/101 = 0.1584 [0.0999, 0.2419]; raw 0.1215 / 0.1206; `cert_site_p95 == (observed >= p95)` for all 101 rows; 101 null rows ↔ 101 sites, no orphan either way; reps 300 on every row; one snapshot id | **CONFIRMED** |
| 9 | depth-stratified gap +0.0740 (20) / +0.0888 (7); strata c2/u1, c4/u0, c2/u8, c6/u12, c2/u64 | own weighted min(n_c,n_u) stratified gap | 0.0740 / 0.0888; strata identical; **total weight = 11** (0-1: w1 gap −0.0114; 2: w0, EMPTY; 3: w2 gap −0.1064; 4: w6 gap +0.1510; ≥5: w2 gap +0.0663) | **CONFIRMED** — see defect D2 |
| 10 | OLS HC1: cert 0.0865 (SE 0.0395) at 20 labels; 0.0796 (SE 0.0368) at 7 | own HC1 sandwich with the same design matrix | 0.0865 (0.0395), log n 0.0041 (0.0225), depth −0.0146 (0.0154), int 0.1827; and 0.0796 (0.0368), 0.0127 (0.0243), −0.0117 (0.0134), 0.0613 | **CONFIRMED.** The OLS is a **registered** side condition of C2's HELD clause (instrument (iii)), **not** a substitution |
| 11 | within-depth permutation p = 0.0480 (20 labels), 0.0030 (7 groups) | own permutation, registered seed **and my own seeds 1/2/3**, and 200,000 permutations | 20 labels: 0.0480 (reg. seed), 0.0390 / 0.0420 / 0.0390 (mine), **0.0365 at 200k**. 7 groups: 0.0030 (reg.), 0.0070 / 0.0020 / 0.0050, **0.0036 at 200k** | **CONFIRMED and robust.** 0.0480 is the *most conservative* of the six draws; the Monte-Carlo SE at P=1,000 is ±0.0068, so the reported p sat one SE from the bar, but the 200k reference settles it below 0.05 |
| 12 | C2 HELD | rule + bracket (e) | gap > 0 ✓, p < 0.05 ✓, OLS cert > 0 ✓; bracket (e)'s UNDETERMINED conditions (i) ≥2 certified (16), (ii) ≥2 uncertified (85), (iii) weight sum 11 > 0, (iv) non-degenerate permutation — all false, so the HELD/FAILED path is the right one | **CONFIRMED** at the registered bar, with defects D2/D3 attached |
| 13 | depth curve d=1 (2 cells) NMI7 0.2962 / NMI20 0.2472 … d=3 (10) NMI7 0.4812 … d=4 (21) NMI20 0.5514 … d=8 (110) NMI20 0.5161 | own max-cosine-path descent on TRAIN | **all 16 numbers reproduce to 4 decimals**; argmax NMI7 at d=3, argmax NMI20 at d=4 | **CONFIRMED** — see §3 on its status |
| 14 | leaf-to-label Jaccard: 1 of 110 at ≥0.5, median 0.1023; per-label/per-group best nodes; median best depth 4.0 / J 0.4058 (20), 3.0 / 0.4957 (7) | own Jaccard over all 211 member sets | identical, every row, including all 20 label rows and 7 group rows | **CONFIRMED** |
| 15 | depth-1 purity 7-group 0.4277 (2171/5076), 20-label 0.1084 (550/5076), k=2; migration matrices | own train-majority scoring on the held-out side | 0.427699 (2171) / 0.108353 (550); both migration matrices identical row by row | **CONFIRMED** |
| 16 | Q3: built, leaves 110, sites 101, depth 8, depth-blocked 4, iterations 15; root 0.061713/0.050961/1.211 cert; n00000004 0.042300/0.033308/1.270 cert; n00000005 0.038280/0.045768/0.836 not cert | own snapshot + CSV | identical; depth-blocked (depth ≥8 and n ≥110) = 4; jsonl iteration 15; build log "leaves=110" (ng_af_s42.build.out:3045) = snapshot L 110 | **CONFIRMED** |
| 17 | certified share 16/101 = 0.158 [0.100, 0.242]; bands n<200 1/27, 200-400 2/34, 400-800 3/21, ≥800 10/19 | own banding + own Wilson | 0.1584 [0.0999, 0.2419]; 1/27, 2/34, 3/21, 10/19; below n 400 = 3/61 = 0.0492 | **CONFIRMED** |
| 18 | C3 HELD (leaves 110 > 20; root certified; depth-1 certified 1 of 2) | rule | "at least one depth-1 site" satisfied by 1 of 2 | **CONFIRMED** (and correctly separated from P2, which requires *both* and FAILS) |
| 19 | T1b: 100 leaves, 97 sites, tree NMI20 0.5526, ARI20 0.2038, diff +0.0032 | own load + own KMeans at k=100 | 100 / 97 / 0.5526 / 0.2038 / +0.0032 | **CONFIRMED** (REPORTED only, never scored) |
| 20 | P10 pre-scored FAILED by bracket (a) on the measured drop rates | arithmetic | short 1,808/18,846 = 9.59% (band 2-5%: FAILED); dup 117/18,846 = 0.62% (band 1-4%: FAILED); leak held-out 112/5,076 = 0.0221 (band 1-4%: HELD); purity delta +0.0148 pp < 0.5 pp (HELD) | **CONFIRMED.** P10 FAILED was fixed before the run and is a prediction failure, not an instrument defect |
| 21 | ACCEPTANCE OK: 12 mmlu_pro tables unchanged in n and sha in both views; embeddings 20,710 → 39,631 (+18,921); queries 18,741 → 31,986 (+13,245); gmm_vectors 0 | own diff of `pin_before.txt`/`pin_after.txt`; own `sqlite_master` table listing on both DBs | only the two embeddings rows differ between the pins; **both views agree on both pins**; +18,921 = 16,921 (20NG) + 2,000 (ag_news smoke); +13,245 = 11,845 (20NG train, shared by both arms) + 1,400 (ag_news smoke train) — exact. `mmlu_pro_dataset_cache_v2.db` has exactly the 12 pinned tables, **no table created**; `embeddings_cache.db` has 6, the 3 unpinned (`agent_ratings`, `match_history`, `sqlite_sequence`) all at 0 rows | **CONFIRMED.** READY condition 10's manual `sqlite_master` comparison is hereby performed and passes |
| 22 | `snapshots_frozen.db` untouched (3f7f5e9a470baba3) | own sha256 of the whole file | `3f7f5e9a470baba3a66d0dbc870bf772739ae60cc415615b0c4f54e0f4793e4e`, mtime 2026-08-02 04:49, no `-wal`/`-shm` | **CONFIRMED** |
| 23 | the 20NG corpus never touched p2dca or any MMLU-Pro row (collision check 0) | `collision_check.out` re-read; `mmlu_pro_dataset_cache_v2.db.twenty_newsgroups` count | 0 exact / 0 norm-v1 against `embeddings.query`, `queries.raw_text`, `mmlu_pro.question`, `multicorpus corpus_questions.text` (total 0); the MMLU-Pro `twenty_newsgroups` table still n=0 sha e3b0c442 (empty) before and after; `reserved_pool`/`reserved_pool_meta` byte-identical | **CONFIRMED** |
| 24 | the two backups | `experiment_results/_backup/` + chain.log L33/34, L81/82 | `snapshots_2026-09-22.db` (sha 4b3846f836a7503f = live at the time) and `reserved_test_queries_2026-09-22.json` (795d1c2d7c688bf9); a second pair on the resume (`…_2026-09-23`, 5433dd419fc6e7cf / 22e737acd0e38733). `pin_before.txt` was **not** recomputed on the resume, so the before-state is the genuine pre-run state; `pin_after.txt` did not exist before 04:43, so bracket (h)(2)'s staleness hazard did not materialise | **CONFIRMED** |
| 25 | P12 timings | chain.log arithmetic | T1 build 19:32:32→20:08:30 = 36.0 min; T1 null (restart) 03:36:38→04:29:56 = 53.3 min; smoke 19:30:13→19:32:20 = 2.1 min; readout 4.7 min; T1b "null" 04:35:07→04:37:59 = 2.9 min but **the null failed** | **PARTLY** — see defect D4 |

---

## 2. Defects

**D1 — HIGH — the C2 HELD sentence of record was silently dropped from the write-once outcome file (a numpy-bool
identity bug).** `tools/analysis/topic_partition.py` L1061 reads `if c2 is True:`. `c2` is built at L1085 as
`c2 = c["strat"] is not None and c["strat"] > 0 and c["p"] is not None and c["p"] < 0.05 and c["beta"][1] > 0`;
the last operand is `numpy.bool_`, so the whole `and`-chain evaluates to `numpy.bool_(True)`, and
`numpy.True_ is True` is **False**. Verified:

```
>>> c2 = 0.0740 > 0 and 0.0480 < 0.05 and np.array([...])[1] > 0
>>> repr(c2), c2 is True, bool(c2)
('True', False, True)
```

Consequence: the criterion line correctly prints `C2 … HELD` (that branch uses truthiness), but the registered
VERDICT-RULE sentence *"The certificate is topic-informative on a corpus with discrete topics (stratified gap
0.0740, p 0.0480)."* was never written. The bug is **fail-silent in both directions**: `if c2 is False:` at L1063
would likewise never fire, so on a measured-null path the outcome would carry **no** C2 sentence at all. The
outcome file is write-once and cannot be repaired. Fix: (a) the registrar writes the sentence into the outcome
*section* of `docs/judge_v2_program.md` with a bracket naming this defect and this review as the recomputation;
(b) engine-coder replaces `is True` / `is False` with `bool(...)` at L1061/L1063 (and audits `c1 is True` /
`c1 is False` at L1056/L1054, which survive today only because `float()` happens to be applied to the CI bound),
and, per pre-run bracket (c)(12), adds the missing selftest assertions for the seven untested paths and raises
the pinned selftest count in the same commit.

**D2 — HIGH — C2's effective support is 11, one stratum carries 6 of it, and two of the four contributing strata
have negative gaps.** The registered weight is `min(n_cert, n_uncert)` per depth stratum. Recomputed:
0-1 → w1 (gap −0.0114); 2 → **w0, an empty cell** (c4/u0: four certified sites at depth 2 contribute nothing);
3 → w2 (gap −0.1064); 4 → **w6 (gap +0.1510)**; ≥5 → w2 (gap +0.0663). Total 11. So +0.0740 =
(1·−0.0114 + 2·−0.1064 + 6·+0.1510 + 2·+0.0663)/11, i.e. 55% of the weight and effectively the whole sign come
from one stratum of 6 certified vs 12 uncertified sites at depth 4. This is the ~26-events class: a single
stratum identifying a parameter. C2 is HELD **as registered**, and I do not move it; but no sentence of record
may read "certification selects topic-aligned nodes" without the effective weight printed beside it. Fix:
mandatory bracket on the sentence (see §5).

**D3 — MEDIUM — the registered null preserves depth but not size, and the finding does not survive an added
size control.** Certified sites are 4.6× larger overall (median n 1301 vs 284). *Within* depth strata the size
gap is modest (depth 4: 737 vs 683; ≥5: 287 vs 221), and the registered OLS does carry `log n` (coefficient
0.0041, SE 0.0225 — no size effect detected), so the confound is partly addressed. But as an **unregistered
reviewer sensitivity**, stratifying the same permutation by depth × size-tercile gives gap +0.0477 with
p = 0.133 (20,000 permutations, weight 10). This is **not** a substituted criterion and must not be promoted
(C-7); it is the reason F2's converse — "the certificate is topic-informative" — must be printed with the
qualifier that it rests on a depth-only null at 11 effective site-pairs and does not reproduce under an
additional size control.

**D4 — MEDIUM — P12 scores a clause that reads a run that never happened, contradicting the outcome's own rule.**
The arm header (outcome L120) states "every criterion and prediction that reads the null is UNDETERMINED" for
T1b, and then P12's clause "T1b null 40-90 min" is scored **FAILED** at 2.9 min — which is the wall time of a
`:siteNull` task that exited 1 and wrote no CSV, not the duration of a completed null. The correct score is
UNDETERMINED. P12's overall verdict does not move (it is FAILED on the T1 clauses alone: 36.0 vs 45-80; 53.3 vs
55-90; 4.7 vs 6-15). Fix: bracket the P12 line in the outcome section — "the T1b-null clause reads UNDETERMINED,
not FAILED; P12 stays FAILED on the three T1 clauses".

**D5 — MEDIUM — pre-run bracket (f) clause (i) is not satisfied by the outcome.** Bracket (f) requires the
outcome to print, side by side with L, "(i) the chain's leaf count parsed from the build log" and "(ii) the
effective number of tree cells that receive at least one held-out arrival". (ii) is printed (`cells 110 (ho 110;
…; empty: 0)`). (i) is **not** printed anywhere in the outcome: `build_state` parses `leaves=` but the readout
uses it only on a not-built arm. I verified the agreement myself — `experiment_results/topic_partition/
ng_af_s42.build.out:3045` reads `Held-out leaf support (MAIN): leaves=110`, equal to the snapshot's L = 110, so
no DISAGREEMENT line was due and no number moves. Fix: the registrar states the two counts in the outcome
section ("build-log leaf count 110 = snapshot L 110, reviewer-verified"); engine-coder prints (i) next time.

**D6 — LOW — the outcome's header carries the superseded registration range.** Line 1 reads
"L10030-L10390"; bracket (g) fixed the range of record to **L10039-L10399** (registrar's check L10319-L10399).
Write-once file; fix by the registrar's outcome section carrying the corrected range.

**D7 — LOW — no explicit falsifier lines.** The outcome states C1 FAILED and prints "F1' … does not fire", but
never prints "F1 FIRED", "F2 NOT FIRED", "F3 NOT FIRED". The registration makes each falsifier a scored object.
Fix: the registrar records F1 FIRED, F2 NOT FIRED (C2 HELD), F3 NOT FIRED (C3 HELD) in the outcome section.

**D8 — LOW — C0's wording is ambiguous across arms.** `C0 gate: HELD` is scored on T1 only (the registered
clause is "T1's null complete at 300 reps"), while the T1b arm block says "C0's null clause FAILED". Both are
true of their arm; the outcome should have said so in one place. No number moves.

**D9 — INFORMATIONAL — permutation loop recomputes the gap five times per draw.** In `cert_vs_alignment`, the
`g, _ = stratified_gap(...)` assignment sits **inside** the `for idx in groups_idx.values():` loop, so the gap is
recomputed after each stratum is shuffled and only the last (all strata shuffled) value is used. The result is
correct; it is 5× slower than needed. Not a defect in any number.

**D10 — INFORMATIONAL, not a defect — P7's qualitative clause is weak by construction.** The registrar reduced
"technical vs discursive, rec.* the swing group" to "comp.* majority cell ≠ talk.* majority cell" **before the
run** (registrar's check (e), bracket (b)(4)), which almost any non-degenerate 2-way split satisfies. It was
registered pre-run, so it stands; but the record should not quote P7 HELD as evidence for the substantive
technical/discursive reading. The underlying matrix does support it descriptively (comp 0.978 → n00000004, talk
0.987 → n00000005, sci 0.561/0.439 nearly split, rec 0.324/0.676).

**No defect found** in: the split's identity, the pool, the collision check, the pins, the backups, the
frozen DB, the T1b UNDETERMINED chain (except D4), the C1 arithmetic, the C1 rule application, the bootstrap,
the depth curve, the Jaccards, or the 20 other prediction clauses (§4).

---

## 3. Registered or exploratory? (the orchestrator's question about the depth curve)

**The depth curve, the leaf-to-label Jaccards and the depth-1 purities are all REGISTERED readouts**, verbatim in
instrument I6 Q2: "depth-d cuts d = 1..8 (partition into the deepest nodes at depth <= d) -> NMI_7, NMI_20 per
depth and the argmax depth for the 7 groups; per label the node of any depth with max Jaccard … ; per leaf max
Jaccard to a label and the share of leaves at J >= 0.5"; and depth-1 alignment is named in C2's
"Depth-1 alignment, best-match depths, Jaccards: **REPORTED**". So: **not exploratory** — no "exploratory of
record" label is required. But three qualifiers are mandatory whenever the depth curve is described as a finding:

1. **REPORTED, not scored.** No criterion reads the curve. Only two prediction clauses touch it: P7's
   "best 7-group depth 3-4" (argmax NMI_7 = 3, HELD) and P8's Jaccard clauses. The NMI_20 argmax at d=4 (0.5514)
   is printed and **no criterion or prediction reads it**; it may not be quoted as a scored result.
2. **TRAIN-side and in-sample.** The depth cuts (n = 11,845), the per-label/per-group best-Jaccard nodes and the
   per-leaf Jaccards are all computed on the construction's **own training members**. They describe the object
   the algorithm fitted; they are not held-out generalisation. Only Q1's purity/NMI/ARI rows and the depth-1
   purities (0.4277 / 0.1084) are held-out (n = 5,076).
3. **One draw.** One corpus, one embedding model, one slice, one seed, one split. REDRAW showed leaf counts and
   the certified fringe are per-draw objects; the depth at which NMI_20 peaks is of the same kind.

The substantive shape is real and reproduces exactly: **NMI_20 peaks at d=4 (21 cells, 0.5514) and falls to
0.5161 at the 110 leaves; NMI_7 peaks at d=3 (10 cells, 0.4812) and falls to 0.3837**. That is, the tree's
best agreement with the label hierarchy is at an intermediate depth, and going to the leaves costs alignment.
It may be reported with the three qualifiers above.

---

## 4. P1-P12 as scored

Recomputed clause by clause against my own numbers; **every P-line's verdict is correct as printed except the
one clause in D4**.

- **P1 HELD** — leaves 110 ∈ [95,175]; sites 101 ∈ [80,150]; depth 8; blocked 4 ∈ [2,15]; iterations 15 ∈ [12,20]. ✓
- **P2 FAILED** — root k=2 ✓, obs 0.061713 ∈ [0.045,0.10] ✓, p95 0.050961 ∈ [0.040,0.075] ✓, margin 1.211 ∈ [1.1,1.8] ✓, root certified ✓; **both depth-1 certified: 1 of 2 → FAILED**; depth-1 observed: 0.042300 ✓ but 0.038280 ✗ → FAILED; depth-1 p95 0.033308 / 0.045768 both ∈ [0.030,0.060] ✓. Bracket (b)(3)'s two-highest-mass reading coincides with the all-sites reading (exactly two depth-1 sites exist). ✓
- **P3 FAILED** — 16/101 = 0.158 vs 22-38% FAILED; n≥800 10/19 = 0.526 ∈ [0.50,0.75] HELD; below n 400 **3/61 = 0.0492** vs the bracketed 5-15% FAILED. *Knife-edge*: 0.0492 misses 0.050 by one site in 61; correctly scored, worth the note.
- **P4 FAILED** — 13 of 14 clauses HELD; the failing one is ARI20 k-means 0.1835 vs [0.20,0.38]. ✓
- **P5 FAILED** — tree purity 0.6673 (<0.68) FAILED; k-means 0.6789 (<0.70) FAILED; random purity ~0.050 vs [0.10,0.17] FAILED; Ward, tree-7group, random NMI20, random ARI HELD. ✓
- **P6 FAILED** — all three clauses fail (noise 0.927, k=3, NMI20 0.2407). The HDBSCAN comparator is effectively degenerate at mcs=55 on these vectors: 92.7% noise, 3 clusters. ✓
- **P7 HELD** — 0.4277 ∈ [0.35,0.60]; 0.1084 ∈ [0.10,0.25] (*knife-edge*, 0.1084 vs the 0.10 floor); qualitative clause HELD under the pre-run rule (see D10); argmax NMI_7 depth 3 ∈ [3,4]. ✓
- **P8 FAILED** — median best depth 4.0 ∈ [3,5] HELD; median best J **0.4058** ∈ [0.40,0.60] HELD (*knife-edge*, 0.0058 above the floor); religion triad 2 of 3 below 0.40 (alt.atheism 0.3109, talk.religion.misc 0.1875; soc.religion.christian 0.4957) HELD; both comp clauses HELD; "≥6 of the ten at J ≥ 0.5": I count **4** (hockey 0.8272, baseball 0.8268, med 0.5370, mideast 0.7115; space 0.3860, crypt 0.4224, autos 0.4366, motorcycles 0.2260, guns 0.4078, forsale 0.4037 all below) FAILED; leaves at J ≥ 0.5 = 1/110 = 0.009 vs 15-35% FAILED. ✓
- **P9 FAILED** — raw 0.1215 ∈ [0.10,0.30] HELD; stratified 0.0740 ∈ [0.00,0.10] HELD; p 0.0480 ∈ [0.02,0.6] HELD; the clause "⇒ C2 FAILED" FAILED because C2 is HELD. ✓ **P9 is the interesting one**: the specialist predicted the gap and the p almost exactly and predicted the wrong conclusion from them, because P9's point was "not significant" at p 0.048.
- **P10 FAILED** — pre-scored by bracket (a) on the corpus, confirmed (table row 20). ✓
- **P11 UNDETERMINED** — builds HELD; more leaves than T1: 100 vs 110 FAILED; certified-share comparison UNDETERMINED (no T1b null; and bracket (b)(5) makes it descriptive-only in any case); NMI20 |0.5526 − 0.5422| = 0.0104 < 0.03 HELD. ✓
- **P12 FAILED** — correct overall, one clause mis-scored (D4).

**T1b's UNDETERMINED wording: complete except D4.** I checked every place T1b's null could be read. Correctly
marked UNDETERMINED: the arm header (with the rule stated), Q3's three site rows ("no site-null row"), Q3's
certified-share line, Q2's "certification vs alignment: no site null (UNDETERMINED)", C3-beside, P11's
certified-share clause and P11's overall verdict. **Nothing is silently scored on T1 alone**: T1b is never given
a C1 or C2 score (registration SCORING RULE: REPORTED only), and the "T1b comparability" line against
ANCHOR-FREE-CERT arm 4 is correctly suppressed because `T1b.q3.cert is None`. The one exception is P12's
T1b-null clause (D4).

---

## 5. What the registrar may write

**Sentences of record** (the registered VERDICT RULE's, and only those):

> On a corpus with known topics the anchor-free recipe of record builds and certifies, and partitions the
> embedding space no better than k-means at the same number of parts; its value on this corpus is the split
> discipline, the support per cell and the certificate, not the partition.

(printed verbatim by the readout; C3 HELD and C1 FAILED; the k = 20 reference row is beside in Q1 as the
registration requires: k-means k=20 seed 0 NMI20 0.6160, ARI20 0.4638, purity 0.6340.)

> The certificate is topic-informative on a corpus with discrete topics (stratified gap 0.0740, p 0.0480).

— **this sentence is of record and is MISSING from the outcome file** (defect D1). The registrar must insert it
in the outcome section, and it carries a **MANDATORY BRACKET**:

> [Depth-stratified over 101 sites with **effective weight 11** = Σ min(n_cert, n_uncert) over the registered
> depth strata; the depth-2 stratum is empty (4 certified, 0 uncertified) and contributes nothing; 6 of the 11
> come from the depth-4 stratum, and the depth-0-1 and depth-3 strata read negative gaps (−0.0114, −0.1064).
> p = 0.0480 at the registered seed; the adversarial reviewer reproduced 0.0390 / 0.0420 / 0.0390 at three other
> seeds and 0.0365 over 200,000 permutations, so the sign and the bar hold, but the permutation preserves depth
> only, and an unregistered depth × size-tercile null reads gap +0.0477 at p = 0.133. One corpus, one embedding
> model, one seed.]

> The per-corpus pair (512 / 0.0145) builds on this corpus.

— **MANDATORY BRACKET**, because this sentence sits directly under one that says "builds **and certifies**":

> [Builds only: 100 leaves, 97 sites. T1b's site null exited 1 and wrote no CSV, so T1b's certification, its C3
> and every prediction clause that reads its null are UNDETERMINED; no certified count exists for this arm and
> none may be compared to T1's or to ANCHOR-FREE-CERT arm 4's.]

Plus the corrections the registrar owes by insertion: the registration range is **L10039-L10399** (bracket (g),
not the outcome header's L10030-L10390); **F1 FIRED, F2 NOT FIRED, F3 NOT FIRED**; the build-log leaf count
**110 = snapshot L 110** (bracket (f) clause (i), reviewer-verified); P12's T1b-null clause reads
**UNDETERMINED, not FAILED** (P12 stays FAILED); and the split is **11,845 / 5,076**, the pre-run bracket (a)'s
11,846 / 5,075 being a banker's-rounding artefact on `comp.graphics` (875 × 0.30 = 262.5; the engine's
`Math.round` takes 263).

**Chips** (proposed):

`BUILD` · `0 CALLS` · `C3 HELD` · `C1 FAILED, F1 FIRED (−0.0020 vs spread 0.0074, CI [−0.0081, +0.0036])` ·
`C2 HELD BUT THIN (gap 0.0740, p 0.048; effective weight 11, one stratum carries 6)` · `T1b UNDETERMINED (null
crashed)` · `P9 PREDICTED THE NUMBERS AND THE WRONG CONCLUSION` · `ONE CORPUS / ONE MODEL / ONE SEED` ·
`DEPTH CURVE PEAKS AT d=4 (TRAIN, REPORTED)` · `ACCEPTANCE OK, FROZEN DB UNTOUCHED`

---

## 6. What this study does NOT show

The lead's registered list (ceilings (1)-(6)) stands and I re-affirm it: nothing about capability (no models,
keys, eval rows, arena, board or judge on 20NG); one embedding model (qwen3-embedding, 4096-d sliced); the bar's
size dependence is uncontrolled (p95 falls with n, so 11.8k train certifies more easily than MMLU-Pro's 8.1k and
the 16/101 vs 14/69 comparison is descriptive, not like-for-like); the 20-topic ceiling (the religion triad, the
comp.* quintet, the politics triad overlap in any embedding, so absolute levels are corpus-bound and only same-k
contrasts are the test); header stripping and Ollama's silent truncation of long inputs (306 kept docs > 8,000
chars) move absolute levels for every method; one seed, one split, no re-draw.

I add:

7. **"Certification selects topic-aligned nodes" does not survive a size control.** C2 is HELD at its registered
   bar, but the estimate rests on 11 effective site-pairs, one stratum supplies 6 of them, two strata read
   negative, and an added size stratification takes p to 0.13. The record may say the certificate *is*
   topic-informative on this corpus at the registered instrument; it may **not** say the effect is established,
   robust, or independent of site size.
8. **Nothing about the certificate on the 512/0.0145 recipe.** T1b built but never certified; the whole Q2
   question is unanswered for the per-corpus pair.
9. **The depth curve, the Jaccards and the per-site NMIs are TRAIN-side.** Only Q1's purity/NMI/ARI and the
   depth-1 purities are held-out. No statement about generalisation of the depth structure is supported.
10. **Nothing about routing, support or the split discipline as *values*.** The verdict sentence asserts the
    tree's value "is the split discipline, the support per cell and the certificate"; this study measured
    neither routing quality nor question support against any alternative. That clause is the registered
    *contrast to* the partition claim, not a measured finding of this run. The only support figure here is
    descriptive (median held-out support 40 per leaf; 23 of 110 leaves below 30).
11. **HDBSCAN is not a fair third baseline on this corpus.** At mcs = 55 it labels 92.7% of TRAIN as noise and
    returns k = 3; its NMI20 0.2407 says almost nothing about density clustering's ceiling here and must not be
    read as "the taxonomy beats HDBSCAN".
12. **Nothing about a second draw.** Leaf count, certified fringe and the depth of the NMI peak are per-draw
    objects (REDRAW); this run has no re-draw arm.

---

## Verdict

**The numbers are sound.** Every headline figure of TOPIC-PARTITION-20NG — the corpus and its manifest sha, the
split, all 21 Q1 rows, the C1 diff / spread / CI, the certified counts and bands, the raw and stratified C2 gaps,
both OLS fits, both permutation p's, the whole depth curve, every Jaccard, the depth-1 purities, T1b's Q1
headline, the pins, the collision check and the acceptance — reproduces from my own scripts against the caches,
to four decimals, with no exception. C1 is correctly FAILED and F1 fires as registered; C2 is correctly HELD at
its registered bar and the permutation p is robust to the seed (0.0365 at 200k draws); C3 is correctly HELD;
T1b is correctly UNDETERMINED throughout save one prediction clause. Zero LLM calls, zero writes to any DB of
record's pinned tables, `snapshots_frozen.db` untouched, no arena pool read or written.

**Verdict: READY for the registrar's outcome — CONDITIONAL on the four insertions.** The outcome file of record
is incomplete, not wrong: (1) the C2 sentence of record must be written by the registrar because a numpy-bool
identity bug dropped it (D1, HIGH); (2) that sentence and the T1b clause carry the mandatory brackets in §5;
(3) the registration range, the falsifier lines, the build-log leaf count and P12's T1b clause are corrected by
insertion; (4) `tools/analysis/topic_partition.py` is **NOT READY for another run** until D1's `is True` /
`is False` are fixed and pre-run bracket (c)(12)'s seven missing selftest assertions are added with the pinned
count raised in the same commit.

**Do not let the headline drift.** The study's one positive result (C2) is a thin-strata result and must never
be quoted without its effective weight; the study's negative result (C1) is clean, well powered at n = 5,076 and
is the finding that should carry the chapter.

---

*Commands and scripts: the reviewer's recomputations ran from*
`C:\Users\octav\AppData\Local\Temp\claude\Z--FAC-TUBerlin-THESIS-TaxoArena\7c10e5cb-d16b-4a0e-864a-f3a6151d835b\scratchpad\`
*(corpus.py, rev.py, q1.py, q2.py, q2b.py, q2c.py; scratch, not of record). Files of record read:*
`Z:\FAC\TUBerlin\THESIS\TaxoArena\experiment_results\topic_partition\topic_partition_outcome.txt`,
`…\site_null_ng_af_s42.csv`, `…\chain.log`, `…\acceptance.txt`, `…\collision_check.out`,
`…\pin_before.txt`, `…\pin_after.txt`, `…\ng_af_s42.build.out`, `…\ng_af_s42\seed_42\dag_snapshots.jsonl`,
`Z:\FAC\TUBerlin\THESIS\TaxoArena\twenty_newsgroups_cache_v1.db.manifest.json`,
`Z:\FAC\TUBerlin\THESIS\TaxoArena\twenty_newsgroups_cache_v1.db`,
`Z:\FAC\TUBerlin\THESIS\TaxoArena\snapshots.db`, `Z:\FAC\TUBerlin\THESIS\TaxoArena\embeddings_cache.db`,
`Z:\FAC\TUBerlin\THESIS\TaxoArena\tools\analysis\topic_partition.py`.
