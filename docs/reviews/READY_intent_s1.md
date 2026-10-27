# READY review: INTENT-TRANSFER-S1 (branch intent-s1, tip f3e46394). Zero calls.

Reviewer: adversarial-reviewer, 2026-10-02. Registration: prog L22682-L22710 plus the brackets at L22688 / L22695 / L22696
(e45474b8; record L23752-L23758); definitions docs/agents/plans/2026-10-03_intent_s1_definitions.md (868c1bb3).
Reviewed blobs (LF, of record; the worktree renderings are byte-identical, so CRLF = LF here):
- tools/analysis/intent_transfer_s1.py `blob:a54bbec044cd4897768b0df290b38691177d2bce`, `sha256-lf16:163782538512fd6e`
- tools/analysis/intent_s1_export.py `blob:75310a98afe87788ca01f45c56a19b9ceb045698`, `sha256-lf16:65a5e4ae53d728b3`
- experiment_configs/intent_s1/ at f3e46394; Kotlin DatasetType.INTENT and working-copy route from 43bf914e (unchanged since)

## Verdict

- **BUILD HALF (exporter, nine configs, Kotlin INTENT): READY** for `intent_s1_export.py --export` and the eight qwen3
  builds, under the registration's own preconditions (rule 7 W1-W5, backup before each build, one construction at a time,
  embeddings_cache.db per-table hashes before/after each build as the HYGIENE acceptance check, M-AF-g only per N3).
- **READOUT `--dry-run`: READY** (no EVAL statistic; it runs census, P0, the GATE constants and the descent acceptance).
- **READOUT `--run`: NOT READY.** Two blockers: B-1 (code, T-C4 fails open) and B-2 (registrar bracket, T-C7's delta).
  After the B-1 fix, a delta review (the diff plus the selftest and mutants) and the B-2 bracket make it READY. If the
  bracket changes code, that change goes into the same delta review.

## Per-claim table (deciding claims)

| # | Claim | My number / finding | Status | Sev |
|---|---|---|---|---|
| 1 | B1: salt 2 keeps the salt-1 EVAL; moves TRAIN->GATE 1,413 / GATE->TRAIN 1,435 / TRAIN->TRAIN 8,457 / EVAL->EVAL 4,946 | own hashlib script on the ingest DB (ro, immutable): 1,413 / 1,435 / 8,457 / 4,946 (+ GATE->GATE 256); build rows 9,844 TRAIN + 1,658 GATE | CONFIRMED to the digit | - |
| 2 | Hard refusal: no salt-1 EVAL text or stem in any build row | 0 text and 0 stem-key hits for massive s1, massive s2 and clinc s1, against ALL salt-1 EVAL rows (massive 4,954 / clinc 8,024, OOS and dropped rows included). assert_no_eval runs in derive() and again on the written DB | CONFIRMED | - |
| 3 | Committed GATE exports and pools = the derivation | my GATE id sets equal the committed JSONs (1,676 / 1,658 / 2,332); my pool ids p9d1bbcd0ee6b8988 / pc02b3fcbb3641056 / pf5c3cefdb02b7769 = the TOMLs; Kotlin computePoolId agrees (IntentS1ConfigTest PASS) | CONFIRMED | - |
| 4 | Descent port = TaxonomyTrickler.trickle + routeQueryToLeaves + profiles filter | line by line: topological push, meanKappa x dot, gate `best < max(r-margin,0) x parentDot` with r recomputed as updateChildCentroidShrinkage (orderedSum mass shares, uniform fallback), beam on dots, LSE over the beam with max over all scores, ln(1e-30) prune on the accumulated mass, residual candidates, floor, cap, leaf filter: equal. Two differences: D-6 (profiles) and D-7 (residual flag) | CONFIRMED, two LOW deviations | LOW |
| 5 | The port agrees with the engine on a real build | ng_af_s42 (snapshot 20260922_195728, 110 leaves, slice 256): with a block parser, **4,873 of 4,873** agree, unrouted 0/0. The script's own `--port-parity` prints "7 of 7 ... ACCEPTED" with 4,801 queries missing (D-4) | CONFIRMED (own harness); the tool's check is vacuous | MED |
| 6 | Modal leaf = TRAIN flatLeaf plurality per item, ties to the smallest id; LCA in edges; r = Pearson(count, -dist), one-sided p | as bracketed (modal_leaves, lca_dist, mantel). The Mantel p fails open when r is NaN (B-1) | PARTLY | HIGH |
| 7 | P0 = snapshots.graph, row by the single Snapshot ID, -wal refuses, node-id and queryIds sets decide | as bracketed (snapshot_id_of, snapshot_row via S0.RO.open_ro, p0). Test gap MY-5 (D-5) | CONFIRMED | - |
| 8 | Criteria and falsifiers as registered | T-C1 TOST (strict) / LOSS / GAIN with joined labels; T-C1b g13_verdict on KC_0; T-C2 (HELD: D2 > spread_o and lo > 0; FAILED: hi < 0); T-C7; T-C9 / T-C8 (FAILED iff upper <= 0); T-C8 needs both to be HELD, FAILED on either; T-C8b; T-C4; F-S1a..e; positive branch with the N1 block: all match the registered text. T-C7's delta: B-2 | PARTLY | HIGH |
| 9 | Outcome write-once | `run()` refuses an existing s1_outcome.txt or s1_items.csv before any read; writes with mode `x` | CONFIRMED | - |
| 10 | sqlite guard switched off after importing g13_comparator | after the import, `sqlite3.connect is FM._RAW_CONNECT` is True. Every read goes through S0.RO.open_ro / II.open_db_ro (`mode=ro&immutable=1`); a write on an open handle raises OperationalError; snapshots.db and embeddings_cache.db have the same size, mtime and sha before and after my reads | CONFIRMED | - |
| 11 | Support (a)-(f) | census 4,946 / 4,923; 6,672 / 6,672; 3,222 / 3,207. Kish re-measured from the components: 1.0093 / 1.0000 / 1.0093; n_eff 4,900.4 / 6,672 / 3,192. SE_total T-C1 0.00373 / 0.00164; T-C7 0.00854; T-C9 0.0210; T-C8 0.00490 / 0.00420; T-C1b 0.00403 / 0.00299; MDE80 values reproduce | CONFIRMED to the stated digits | - |
| 12 | Selftests and mutants | s1 `--selftest` 137 OK; exporter `--selftest` 317 OK; s1 `--mutants` 61 of 61 KILLED; my 8 mutants: 3 killed, 5 survived (below) | CONFIRMED / gaps | MED |
| 13 | Gradle | IntentS1ConfigTest 1/1, IntentDatasetTypeTest 7/7, IntentConfigCrossCheckTest 3/3: 0 failures (fresh XML 19:01:5x UTC); `gradlew --stop` run afterwards | CONFIRMED | - |

## Blockers and defects (each with a fix)

- **B-1 (HIGH, code, deciding T-C4).** In `mantel()`, when r is NaN (std(x) or std(-dist) is 0), `ge` never increments and p
  becomes 1/(n_perm+1). That reads as HELD. Probe: constant distance, K 10, gives r nan, p 0.000999, and
  `t_c4_verdict(p, p)` returns HELD. Unlikely on these corpora, since 60 / 150 intents on 25-110 leaves force shared
  leaves, but it fails open. FIX: return p = nan when r is not finite; `t_c4_verdict` reads a non-finite p as
  UNDETERMINED (or refuses); add a selftest with constant distance.
- **B-2 (HIGH, registrar bracket before `--run`; reading R5).** T-C7's delta = 0.25 x (ceiling - floor) is computed in-run
  (i) on EVAL (ceiling = centroid co-filing of EVAL origin/variant pairs; floor = random same-intent EVAL pairs), while
  HYGIENE reads "thresholds and the TOST delta fixed on GATE before EVAL opens". C4 variants exist only for EVAL items
  (S0.c4_variants), so no GATE recomputation is possible. (ii) The floor uses k-means at k = L (S0's 0.692 used K = 60 =
  the gold fine K, seed 0). Both choices move a deciding constant: a floor at k ≈ 25-50 is higher, so delta is smaller and
  EQUIVALENT is harder. The registered text ("0.0355, both ends recomputed in-run per arm") does not decide between them.
  The registrar rules pre-data among: (a) R5 as built (EVAL, k = L), disclosed as an exception to HYGIENE's GATE rule;
  (b) the registered constant 0.0355 fixed; (c) EVAL at K = 60.
- **C-3 (MEDIUM, registrar brackets; readings that set a deciding computation).** R3: one TRAIN-flatLeaf label map serves
  both flatLeaf and descent in T-C8, and a leaf with no flatLeaf TRAIN item counts as wrong. R4: the supervised partition
  in delta_c = nearest TRAIN gold-fine centroid at the arm's slice. R7: T-C2's DP over EVAL items filed by flatLeaf, gold
  coarse, the tree = treeParents. R12: the acceptance refusal binds only M-AF / C-AF; bracket (a) says "else it refuses"
  with no arm restriction, and the descriptive arms print NOT ACCEPTED. Need no bracket (mechanical or verbatim S0/G13,
  or descriptive only): R1 (consistent with the registered SE_total and TOST), R2, R6, R8 (asserted against S0.d3's
  top-20), R9, R10, R11 (the registrar's scoring convention; it may adopt it).
- **D-4 (MEDIUM, tooling).** `--port-parity` prints ACCEPTED on 7 of 4,808 texts (0.15% coverage). parse_diagnostics is
  line-based, so multi-line texts lose everything after their first line. FIX: parse by block (`Query: "(.*)"\nTrue Domain:`, DOTALL), and refuse unless
  every parsed query has a vector and the count equals the file's `Query:` count. Not on S1's deciding path:
  descent_acceptance refuses any GATE text the diagnostics do not cover, and MASSIVE / CLINC hold 0 texts with a newline
  (counted; banking77 has 13 and is not built).
- **D-5 (MEDIUM, test gaps on deciding paths).** These mutants SURVIVE the full selftest: MY-3 (T-C8 counts a descent leaf
  with no TRAIN label as right), MY-4 (T-C7 floor from k-means seed 1), MY-5 (P0 compares leaves only; internal nodes hold
  residual queryIds under DAG_MAX), MY-8 (T-C1b counts a no-TRAIN leaf as right). The production code is right in all four.
  FIX: a fixture leaf with snapshot members but no flatLeaf TRAIN item, reached by descent and by flatLeaf; assert the
  floor's seed; plant a queryIds difference at an internal node.
- **D-6 (LOW).** "Has TRAIN members" in the port = non-empty queryIds. The engine's filter = leaf has a PARTITION profile
  (BatchTrickleEvaluator.buildLeafProfiles: at least one member, with a known domain, whose best-similarity leaf is this
  one). These can differ. The >= 99.9% acceptance covers it (fail-closed). ng_af_s42 had 0 leaves without queryIds, so
  this path was not exercised. FIX: state it in the docstring; print the count of leaves the engine never names top-1.
- **D-7 (LOW).** The port reads residual routing from dagMode. enableResidualRouting can be overridden in the TOML but is
  not serialised into the snapshot settings (checked on ng_af_s42). load_tree_checked refuses a config.toml that sets it,
  and no S1 TOML does. MY-1 (residual always on) survives: TREE_BASELINE does not discriminate. Not decisive.
- **D-8 (LOW, cosmetic).** The m_af_s2.toml header says "builder's reading B1" (now ruled). In `export()`, the post-write
  assert_no_eval refuses only after the file is written; derive() makes that case unreachable.

## Own mutants (deciding paths; in-process, full selftest each)

MY-1 residual always on: SURVIVED (not decisive, S1 is DAG_MAX) · MY-2 delta_c from k-means seed 0: KILLED · MY-3 T-C8
no-label descent leaf counted right: SURVIVED (decisive gap) · MY-4 T-C7 floor seed 1: SURVIVED (decisive gap) · MY-5
P0 leaves only: SURVIVED (decisive gap) · MY-6 census tolerance 0.5: KILLED · MY-7 T-C4 FAILED on either: KILLED · MY-8
T-C1b no-TRAIN leaf counted right: SURVIVED (decisive gap).

## Commands (scratch scripts under the session scratchpad `is1/`; all reads `mode=ro&immutable=1`)

```
git ls-tree f3e46394 tools/analysis/intent_{s1_export,transfer_s1}.py ; git hash-object --no-filters <same>   # pins, LF = worktree
python is1/b1.py            # own salt-1/salt-2 hashing on intent_transfer_corpora_v1.db: moves, leaks, GATE ids vs JSON
python -c "...pool ids from gate_ids_*.json..."                       # p9d1bb / pc02b3 / pf5c3c
python -c "...S0.load_corpora; census; S0.kish; c4_variants..."      # 4,946/4,923, 6,672, 3,222/3,207; Kish 1.0093/1.0/1.0093
python tools/analysis/intent_transfer_s1.py --selftest | --mutants ; python tools/analysis/intent_s1_export.py --selftest
python tools/analysis/intent_transfer_s1.py --port-parity <ng_af_s42/seed_42> --emb-db embeddings_cache.db --snapshot-db snapshots.db  # 7 of 7 (D-4)
python is1/parity.py <ng_af_s42/seed_42> embeddings_cache.db snapshots.db    # block parser: 4,873 / 4,873; settings have no enableResidualRouting
python is1/mymut.py         # MY-1..MY-8 + Mantel constant-distance probe (r nan, p 0.000999, HELD)
stat/sha256sum snapshots.db embeddings_cache.db (before = after: 9b8b816e1b82b1e2 / 52229e1ebfdda76e, mtimes unchanged)
gradlew.bat test --offline --tests IntentS1ConfigTest --tests IntentDatasetTypeTest --tests IntentConfigCrossCheckTest ; gradlew.bat --stop
```
Machine: no java ran at the start (tasklist count 0; the CERT-PC-SIZE arm had ended). The only python running was this
review's own mutant run.
