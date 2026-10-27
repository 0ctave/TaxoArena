# VOTE-FRAME-CERT: post-run numbers review (adversarial reviewer, zero calls, read-only)

Object: the outcome of record at c731836, `experiment_results/vote_frame_cert.txt` (blob:8db4403fbfa1c53f28a1f4672b781c119420c00b / sha256-lf16:5e3af71cfd97e759, working tree CRLF sha256-crlf16:06876dacff71dd85) and `experiment_results/vote_frame_cert.json` (blob:5ec19826a1b2bb33eccbe2810b389051906dd8c0 / sha256-lf16:48e5f5a3d4dd02d0; working tree CRLF). Instrument `tools/analysis/vote_frame_cert.py` blob:8e1fbf6a7d557c2a82f5769ecea89c1d03f10705 / sha256-lf16:72ceddfe919a982e / sha256-crlf16:9d86e3fba063ef5d. Those pins match the outcome header and position_index_all.py's `VFC_PIN_LF`. Registration L13032-L13109 (8adae39). Rulings L13691-L13746, L13967-L14002, L14201-L14246, L14529-L14549 and L14572-L14589. READY: docs/reviews/READY_vote_frame_family_rr3.md (ae88d3a). Operator log `vfc_run/run.log` equals the outcome .txt line for line, apart from its final two lines ([WRITTEN], exit 0).

Scratch (outside the repo): `C:/Users/octav/AppData/Local/Temp/claude/Z--FAC-TUBerlin-THESIS-TaxoArena/7c10e5cb-d16b-4a0e-864a-f3a6151d835b/scratchpad/vfc_post/`. It holds `census.py` / `census.out` (sha, size, mtime and -wal/-journal for all 62 caches), `frames.py` / `frames.out` / `frames.json` (the independent frame recompute), `ndo.out`, `overlap.py` / `overlap.out`, and `vfc.py` (the instrument at c731836, read only as source and never imported). My scripts import neither vote_frame_cert, rejudge_grok nor any writer. The parser is my own re-implementation, and name maps are taken from the writers' source. Every DB was opened `mode=ro&immutable=1` after checking for a -wal and a -journal. None of the 62 has either file (census.out: 62 of 62 `wal=None journal=None`). The six non-empty -wal files are embeddings / topic caches and are not among the 62 (`find ... -name "*-wal" -size +0c`). None of them was opened.

Rule 7: no construction and no site null was running. Only two JVMs were up: the Gradle daemon (PID 49416, idle since 11:35) and the Kotlin compile daemon (PID 5940). There was no test-executor JVM. The only python process tree was a peer reviewer's scratch `recompute_seed.py` (cert_post), which had exited by the time I checked. None of my scripts writes to the repo.

## 1. The anomaly: `_backup/newcomer_placement_steps_2026-09-19_complete.db`

**(a) Why it happened: the name profile is looked up by BASENAME.** Confirmed from source (vfc.py at c731836):
- L187-L192 `NAME_PROFILES` has four entries, keyed by basename: `arena13.db`, `placebo.db`, `newcomer_placement.db`, `newcomer_placement_steps.db`.
- L690 `prof = NAME_PROFILES.get(os.path.basename(path))`. The copy's basename is `newcomer_placement_steps_2026-09-19_complete.db`, so the lookup returns `(None, None)` and there is no resolver.
- L941 `to_order1_frame(label, None)` returns None for every stored name, so `t.unresolvable += 1` and the row is skipped. My count is 767 names, and the other 33 labels are TIE. That leaves n1_inf = n2_inf = 0.
- `classify()` L651-L664 returns **AMBIGUOUS** when n2_inf == 0. L947-L949 then overrides this to `UNCERTIFIABLE` with `uncert_reason = "RX"`.
- The unit's `label_space` stays `'positions'` (JSON), which is false: the labels are names.

The copy is byte-identical to the original. census.py computed the full sha256 of each file: 56 distinct contents among the 62 files, falling into 6 byte-identical groups, one of which is this pair (sha256_16 292fdf095f527ce1). My recompute on the COPY gives exactly the original's frame: fwd 387/387 and rev 380/380, with the stored name equal to the contestant shown at the parsed position; `o1frame==T(parse)` 380/380 and `o1frame==parse` 0/380 (frames.out, "BACKUP newcomer_placement_steps"). The class is a PATH artefact, not a property of the content.

**(b) Could any other class depend on the path in a way that matters? No, not in this run.**
- Every path-keyed table in the instrument was checked:
  - `NAME_PROFILES` (decides the class; applies only to name-labelled LONG tables).
  - `COMB_WRITER` (decides the H3 check; applies only to E-COMB-only caches, and none of those has a _backup copy).
  - `WRITER_OF` (printed only: used at L1029 and L1174, decides nothing).
  - `P5_NAMED` (the prediction's named files).
- The other 5 pairs were compared unit by unit in the JSON. All classes are equal and 0 unit fields differ, including every count. Only the printed `writer` string differs (UNMAPPED vs the mapped name).

| pair (copy under _backup/ -> original) | copy class | original class | unit-field diffs |
|---|---|---|---|
| bfcl_final_state_swap | POSITIONAL | POSITIONAL | 0 |
| bfcl_judged_pilot_COMPLETE_1316rows -> agent/bfcl_judged_pilot | POSITIONAL | POSITIONAL | 0 |
| canary_baseline_pass2_2026-09-22_complete | POSITIONAL | POSITIONAL | 0 |
| ifeval_response_oracle_2026-09-23 | POSITIONAL | POSITIONAL | 0 |
| **newcomer_placement_steps_2026-09-19_complete** | **UNCERTIFIABLE (RX)** | **CONTESTANT** | **7** (klass, counts, label_space, names_desc, notes, uncert_reason, contestant_cols) |
| sb_realdiff/stack_v2_promptv2_x12all | POSITIONAL | POSITIONAL | 0 |

The other five are path-independent because their stored labels are positions (bfcl LONG) or their names resolve from the row's own `model_a` / `model_b` columns (WIDE).

**(c) It contradicts ruling (1)'s stated premise, and RX is an unregistered, unruled reason.**
- **Ruling (1) (L14578)** says: "a byte-identical copy gets the same class as its original, which is correct". That sentence was false for 1 of the 6 byte-identical pairs. The ruling's OPERATIVE parts still stand:
  - the universe stays as registered;
  - the pooled index excludes `_backup/` by prefix (position_index_all.py L154, blob:31299cf31e134e05657798f528954f578975d286);
  - the review runs the distinctness belt.
- **RX is outside the registered definition.** The registration (L13064-L13067) defines UNCERTIFIABLE as "(neither raw text nor a combined column)". This table HAS raw text on all 800 rows, so it is not UNCERTIFIABLE under the definition. The D7 ruling (L14201-L14246) names five reasons, R1-R5, and no sixth. A grep for "stored labels unresolvable", "labels are neither", "name profile", "NAME_PROF" and "basename" over docs/judge_v2_program.md and every READY_vote_frame_family*.md gives 0 lines. RX exists only in the instrument's docstring (L123) and code (L224, L949). It was never ruled by the registrar and never examined by a READY.
- **What the registration's own words give.** For a cache "whose informative rows are all degenerate", L13086 says AMBIGUOUS AT ANY BUDGET, and the instrument's own `classify()` returned AMBIGUOUS before the override.
- **What the content gives:** CERTIFIED-CONTESTANT.
- **Consequence.** AMBIGUOUS and UNCERTIFIABLE are both exclusion classes, so no index consequence follows. But RX should have been a registrar question BEFORE the run, not a class assigned by the code.

**(d) P4 does not depend on it. CONFIRMED.**
- P4 is "≥ 1 UNCERTIFIABLE among the dual-order caches". Without the copy, the count is 1 (rubric_contrast.db, R2, pin timing) ≥ 1, so P4 is HELD. P1, P2 and P3 are unchanged.
- Recount with the copy reclassed to its content's class: P2 = 54/60 still (the copy was never POSITIONAL), P3 = 0, P4 = 1.
- **But P4 is carried by a procedural exclusion.** The registered-definition reason R1 = 0 (outcome L402 of the LF rendering: "(1) the registered definition ... 0"). P4 is HELD only through R2 (pin timing), which the D7 ruling admitted into P4's count. That is "a MET that certifies an exclusion rather than a cell". The chip must say so.

**(e) E2 is met in its wording, but its content is off-definition for this one cache (PARTLY).**
- E2 is "EXACTLY ONE class with its evidence counts (rows checked, informative rows, agreements under each hypothesis)". The copy has one class and counts (rows 800, informative 0, positional 0, contestant 0, unresolvable 767), so E2 is HELD as registered.
- E2 is a presence check: it does not verify that the class is the one the registered definition assigns, and here it is not.
- E3 did not cover the gap either. The selftest (240 checks) reaches the name-profile path only through a synthetic `x12/arena13.db`, so its basename is mapped. No fixture exercises a name-labelled LONG table under an unmapped basename. The RX classification branch ran for the first time on real data.

**Recommendation (record by insertion; the outcome is write-once, no re-run):** the registrar records
1. the copy's printed class, UNCERTIFIABLE (RX), as an INSTRUMENT ARTEFACT, not a frame finding;
2. by content, the copy is byte-identical to a CERTIFIED-CONTESTANT cache and reproduces its frame to the digit (fwd 387/387, rev 380/380 contestant, 0 positional);
3. a [CORRECTED] bracket on ruling (1)'s premise sentence;
4. P4 as HELD on R2 (pin timing) alone, R1 = 0;
5. RX as a sixth reason that was never registered, with the rule for any reuse that it must be ruled before a run (keying NAME_PROFILES by content sha, or by the certificate path's original, is a code change to a READY blob and needs a delta READY).

## 2. Per-claim table

| # | claim (as printed) | my number | verdict | command / script |
|---|---|---|---|---|
| 1 | 62 enumerated; E1 matches steward file for file | steward 62 (non-comment lines), JSON 62, set-equal True | CONFIRMED | census.py (`set(st) == set(jc)`); `grep -vc '^#'` on the listing = 62; listing sha256 e332d739...eba reproduces |
| 2 | Class counts 54 / 4 / 0 / 0 / 2 / 2 | Counter over JSON: POS 54, CON 4, UNC 2, NDO 2 | CONFIRMED | python Counter on vote_frame_cert.json |
| 3 | arena13 CONTESTANT (order-1 1771/1771, contestant 1776/1776, 0 positional) | ensemble 1771/1771 name-at-parsed-position, o1frame==parse 1771; reversed 1776/1776 name-at-parsed-position, o1frame==T(parse) 1776, ==parse 0; 1800 dual mids | CONFIRMED to the digit | frames.py `long_names(arena13, NEW='grok-4-1-fast-reasoning', pair=(ensemble, reversed))` |
| 4 | placebo CONTESTANT (587/587; 585 contestant) | fwd 587/587; rev 585/585 T(parse), 0 parse | CONFIRMED | frames.py |
| 5 | newcomer_placement CONTESTANT (752/752; 746) | fwd 752/752 (1 invalid excluded); rev 746/746 T(parse), 0 parse | CONFIRMED | frames.py |
| 6 | newcomer_placement_steps CONTESTANT (387/387; 380) | fwd 387/387; rev 380/380 T(parse), 0 parse | CONFIRMED | frames.py |
| 7 | the 4 store NAMES in both arms (writer source) | labels: arena13 3547 names + 53 TIE; placebo 1172 + 26; newcomer 1498 + 101 TIE + 1 INVALID; steps 767 + 33; writer maps {"Model A": new, "Model B": opp} fwd / {"Model A": opp, "Model B": new} rev (placement_steps.py L459-L460, newcomer_placement.py L487, arena13.py ensemble / position_decomp.py L64-L67 reversed) | CONFIRMED | frames.py + grep of writers |
| 8 | rubric_ladder E-COMB POSITIONAL 3812/3812 | 3812 informative, positional 3812, contestant 0 | CONFIRMED | frames.py `wide(..., r1=none)`, winner names mapped by row model_a/model_b |
| 9 | rubric_swap E-COMB POSITIONAL 4006/4006 | 4006 / 4006 / 0 | CONFIRMED | frames.py |
| 10 | rubric_contrast UNCERTIFIABLE by pin timing (would be POSITIONAL 10478/10478) | 10478 / 10478 / 0; first write 2026-09-06 13:06:29 UTC (1788699989), earliest commit 7037035 15:07:16 +0200 = 47 s after | CONFIRMED | frames.py; `git log -- tools/analysis/rubric_value_contrast.py` |
| 11 | H3 pins: ladder f03cb302, swap 3ebf4f4a; L307 / L187 direct `rj.combine_orders(v1, v2)` with v1 / v2 from parse_judge | both are commits; source at pin shows `v1, _ = rj.parse_judge(raw1)`, `v2, _ = rj.parse_judge(raw2)`, `gw, flip, invalid = rj.combine_orders(v1, v2)` at L305-L307 (ladder) and L185-L187 (swap) | CONFIRMED (spot check, not the full AST check) | `git show <pin>:tools/analysis/rubric_ladder.py \| sed -n 303,308p` |
| 12 | V-C2'' counts 3 / 2 / 1 / 0 / 0 / 0 + pin-timing line | 3 / 2 / 1 / 0 / 0 / 0; "PIN TIMING" 1; P4 reason line 1 | CONFIRMED | `grep -c` on the LF outcome |
| 13 | Kotlin board kotlin_c0d3f708 POSITIONAL (verdicts 8008/8008, 8193; judge_calls same) | verdicts o1 8008/8008, o2 8193 pos / 0 con, E-COMB 7640/7640/0; judge_calls order1 8008/8008, order2 8193 pos / 0 con, duplicate keys 0 of 18246 rows | CONFIRMED | frames.py `wide`, `kotlin_calls` |
| 14 | grok_calib POSITIONAL (8049/8049; 8189) | 8049/8049; 8189 / 0; E-COMB 7692/7692/0 | CONFIRMED | frames.py |
| 15 | random 6 of the POSITIONAL caches (seed 20260923 over the 54 minus named ones): arxiask, bareq512_s42, grok_reasoning_generic, escalate_llama_law, stack_v2_promptv2_x12all, ref_checklist | arxiask 284/284, 289/0; bareq512 1890/1890, 1890/0; grok_reasoning_generic 1881/1881, 1878/0; escalate 323/323, 324/0 (E-COMB r1_winner 322/322/0); x12all 8132/8132, 8186/0 (E-COMB 7789/7789/0); ref_checklist 2394/2394, 2406/0 (2353/2353/0). Each equals the printed count | CONFIRMED (8 of 8 with 13-14) | frames.py |
| 16 | P5: bfcl_judged_pilot LONG, POSITIONAL on rev; canaries POSITIONAL | bfcl verdicts fwd 570 / 570 pos, rev 584 / 584 pos, 0 contestant; probe 49/49, 48/48; canary pass1 259/259, 266/0 (E-COMB 245/245/0); pass2 264/264, 259/0 (244/244/0) | CONFIRMED. The registered "on both arm values" also holds, trivially, on fwd | frames.py `long_pos`, `wide` |
| 17 | leaf_powered NOT-DUAL-ORDER | 2156 rows, raw1 non-empty 2156, raw2 non-empty 0, flip = 0 on 2156; arms leaf / anchor 1078 each | CONFIRMED | ndo.out |
| 18 | refgated NOT-DUAL-ORDER (card / base are conditions) | 3600 rows, base 1800 / card 1800, 1800 mids carry both, max 1 row per (mid, arm); writer ref_gated_rubric.py L102 judges one order (`build_user_prompt(q, ta, tb)` only) | CONFIRMED | ndo.out + grep |
| 19 | P1 60 in 25-60 | 60 = band's UPPER EDGE; 6 of the 60 are byte-identical _backup copies; distinct-content dual-order caches = 54 | CONFIRMED (qualifier: at the edge, includes copies) | census.py groups |
| 20 | P2 54/60 = 0.900 ≥ 0.80 | 54/60 = 0.900; on distinct content 49/54 = 0.907 (the copy counted as its original's class) | CONFIRMED | arithmetic |
| 21 | P3 0 MIXED | 0 | CONFIRMED | JSON Counter |
| 22 | P4 2 UNCERTIFIABLE ≥ 1 | 2 printed; 1 after removing the RX artefact; R1 (registered definition) = 0 | PARTLY: HELD under D7, carried by a pin-timing exclusion; R1 = 0 | outcome L402-L404 (LF) |
| 23 | E2 exactly one of six classes with counts | formally true for 62 of 62; one class (RX copy) is outside the registered definition and contradicts content | PARTLY | section 1 |
| 24 | E3 selftest PASS | 240 checks, 0 failed (python and -O logs); no fixture covers an unmapped-basename name-labelled LONG table | CONFIRMED as registered; coverage gap | vfc_run/selftest.log, selftest_O.log |
| 25 | E4 no write (size and mtime) | as REGISTERED, E4 is size + mtime only (L13075), so it checks no content. EXTENDED: full-file sha256_16 of all 62 now = the run-time JSON value 62/62, size 62/62, mtime_ns 62/62; no -wal / -journal beside any; operator's 10-DB sha before/after `dbid_before.txt` == `dbid_after.txt` | CONFIRMED (extended to sha on 62 of 62) | census.py (`MISMATCH/NONEMPTY: 0 []`) |
| 26 | "a byte-identical copy gets the same class as its original" (ruling (1), L14578) | 5 of 6 pairs yes; 1 of 6 no | REFUTED (premise only) | section 1(b) |

## 3. Checks that pass without checking (hunted)

- **E4 is size and mtime.** That is how it is registered, so it is not a defect of the run. Extended here to sha on 62 of 62: no change.
- **E2 is a presence check** (it checks for one class and some counts). It passed a class the registration does not define.
- **P4 is HELD on an exclusion.** Section 1(d).
- **Silent drop in LONG certification.** L947-L949 make a table UNCERTIFIABLE (RX) only when n2_inf == 0. A name-labelled LONG table with SOME unresolvable labels is certified on the resolved subset alone, with the dropped rows noted but not refused. The 100%-of-informative-rows threshold is then read over a denominator that silently shrank. It was not exercised in this run: the JSON scan shows 0 primary-unit unresolvable counts outside the RX copy. It is latent for reuse.
- **Silent drop in the index's reader.** `unit_votes()` in the LONG reader skips a match with `if None in xs: continue`, with no counter or note. For the four originals the unresolvable count is 0, so nothing drops. Under any other basename, every row would drop silently.
- **Weak secondary E-COMB.** For causal_length ×4, arxiask and oracle the secondary is "CERTIFIED-POSITIONAL" on 111/1024, 187/1068, 182/1001, 140/991, 29/279 and 36/288 rows. The rest are unresolvable, because the combined winner is a name and the table has no model columns. It is secondary and decides nothing; its "CERTIFIED" is a weak check.
- **`source_constant` reads the writer's CURRENT source, not a pinned blob** (arena13.NEW, placebo_entry.GEM). The data validates it: 0 unresolvable and 1771/1771 and 587/587 order-1 agreement. A later edit of the constant would silently turn these caches RX.
- **E1's shared blind spot.** The steward skipped the 6 non-empty -wal files. The instrument read their main file only (immutable=1 ignores the WAL). A dual-order table living only in a WAL tail would be missed by both lists. All six are embeddings / topic caches, so this is a stated limit, not a finding.

## 4. Defects

| id | severity | defect | fix |
|---|---|---|---|
| D1 | MEDIUM | Path-keyed NAME_PROFILES produced a content-contradicting class (the RX copy); ruling (1)'s premise "a byte-identical copy gets the same class" is false for 1 of 6 pairs | Record by insertion (section 1). Reuse: key the profile on content (sha256 of the file, matched against the certificate's originals) or refuse on RX; delta READY |
| D2 | MEDIUM | RX ("OTHER (stored labels unresolvable)") is a sixth UNCERTIFIABLE reason, never registered or ruled, reached by an override of AMBIGUOUS; the registered definition (no raw text, no combined column) does not describe the case | Registrar records RX as unruled; for any reuse it rules RX before the run (AMBIGUOUS per L13086, or refuse) |
| D3 | MEDIUM (chip) | P4 HELD is carried by R2 (pin timing), with R1 = 0; the registered UNCERTIFIABLE mechanism never fired | Chip: "P4 HELD (under D7) on one pin-timing exclusion; 0 under the registered definition" |
| D4 | LOW | Partial-unresolvable LONG / WIDE tables certify on the resolved subset (L947-L949; comb_tally L790); `unit_votes` drops unresolved matches without a count | Before reuse: refuse (or class RX) when unresolvable > 0 on the deciding table; count drops in unit_votes |
| D5 | LOW | JSON `label_space` = "positions" on the RX copy (the labels are names) | Note by insertion; descriptor only |
| D6 | LOW | No selftest fixture for an unmapped-basename name-labelled LONG table; E3 did not reach the RX branch | Add a fixture on any reuse |
| D8 | MEDIUM (POSITION-INDEX-ALL, not this test) | The two Kotlin caches enter the index with both certified tables; the verdicts unit is dropped only because it lacks judge_model, silently (item 5.6) | Restrict to judge_calls, or print per-unit record counts at run time |
| D7 | LOW | P1 = 60 sits at the band's upper edge and includes 6 byte-identical copies (distinct content 54) | Print the distinct-content count beside P1 in the record |

No BLOCKER for VOTE-FRAME-CERT. No certified class is wrong. Every deciding count I recomputed reproduces to the digit.

## 5. What POSITION-INDEX-ALL must know before it runs

1. **The four CERTIFIED-CONTESTANT caches store MODEL NAMES in BOTH arms, not positions.** The reader maps a name to its order-1 position and transposes the order-2 arm. Verified independently: in every informative row of both arms, the stored name equals the contestant shown at the parsed position (fwd / ensemble: 1771, 587, 752, 387; rev / reversed: 1776, 585, 746, 380). The order-1-frame reading equals parse on fwd and T(parse) on rev in 100% of rows, 0 the other way. After the reader's transposition, p2 is the order-2 POSITION.
2. **arena13.db:** only the (ensemble, reversed) pair enters (1800 dual mids). The unpaired arms selfref 598, t0a 299 and t0b 299 must never be read as orders. `ensemble` (order 1, grok-4-1-fast-reasoning shown first) was written by arena13.py. `reversed` (opponent first) was written LATER by a different script, position_decomp.py, with the same ensemble reference.
3. **Name resolution is keyed by basename, and the NEW / GEM constants are read from the CURRENT source.** Enter the four caches only at their certified paths. The index's sha256_16 refusal (position_index_all.py L263-L265) protects the content, not the constants. Re-check `NEW` and `GEM` against the stored labels (0 unresolvable) at run time.
4. **_backup/ is excluded by prefix** (L154). Expected sha collisions among ENTERED caches: 0. All 6 byte-identical pairs have their copy under _backup/. As a belt beyond the sha check: 0 raw-response texts are shared between any two of the 53 certified non-_backup units with raw text (142,533 distinct raw keys; overlap.out). Row-level duplication across entered caches is therefore 0 on the raw evidence. The 2 E-COMB-only caches (ladder, swap) have no raw text and are not covered by this check.
5. **Excluded by class:** rubric_contrast.db (UNCERTIFIABLE, pin timing; the frame is positional 10478/10478, but it may not enter), the RX copy, leaf_powered.db and refgated.db (NOT-DUAL-ORDER).
6. **The Kotlin board has two certified tables** (judge_calls LONG by presentation_order, and verdicts WIDE) holding the same 9,123 matches (8008 / 8193 informative in both). kotlin_ae92da306544f453.db has the same shape (513 / 518). position_index_all.py (blob:31299cf3) gives these two caches NO `tables=` restriction (FAMILY_MAP L150-L151; bfcl_judged_pilot has `tables=("verdicts",)`), so BOTH units enter `plan()`. The Kotlin `verdicts` table has no `judge_model` column, while the map sets `judge_col="judge_model"`. Every verdicts row therefore reaches `if not corpus or not judge: continue` (extract(), L290) and is dropped SILENTLY, so the board is not double-counted, but only by accident. Before the run, either restrict the two caches to `tables=("judge_calls",)` (a change to a READY blob: delta check) or require the readout to print per-unit record counts showing judge_calls 9,123 / 600 entered and verdicts 0. MEDIUM for POSITION-INDEX-ALL.
7. **bfcl_judged_pilot.db has two certified tables** (verdicts 1216 rows, probe 100 rows). The same one-table rule applies unless the registration says otherwise.

## 6. Proposed sentence of record

"VOTE-FRAME-CERT post-run review (2026-09-23, zero calls): every deciding count re-computed independently reproduces to the digit. That covers the 4 CERTIFIED-CONTESTANT caches (names in both arms; rev arm 1776 / 585 / 746 / 380 transposed, 0 positional), the 3 E-COMB caches (3812 / 4006 / 10478 positional, 0 contestant), 8 sampled POSITIONAL caches including the Kotlin board and grok_calib, P5 (bfcl fwd 570/570 and rev 584/584 positional; both canaries positional), and the 2 NOT-DUAL-ORDER caches. The sha256_16 of all 62 caches equals the certificate's. The certificate is HELD. One class is an instrument artefact: _backup/newcomer_placement_steps_2026-09-19_complete.db is byte-identical to the CERTIFIED-CONTESTANT original and was printed UNCERTIFIABLE under an unregistered reason (RX), because the instrument's name profile is keyed by file basename. Its content reproduces the original's frame exactly. Ruling (1)'s premise that a byte-identical copy gets its original's class is corrected for this pair. P4 stays HELD on rubric_contrast's pin-timing exclusion alone (0 under the registered definition). No index consequence follows, because _backup/ is excluded by rule."

## 7. What this review does not show

- It does not re-run the H3 AST checks. They were spot-checked only: the call lines at the pinned commits and the pin timing of rubric_contrast.
- It does not check the 46 unsampled CERTIFIED-POSITIONAL caches beyond their sha, size and mtime identity to the certificate.
- It does not show that my parser equals `rejudge_grok.parse_judge` on every string. It was written independently to the same rules and agreed with every stored vote in the recomputed tables. It does not show that it would agree on inputs not present here.
- It does not open the six WAL-carrying caches, snapshots_frozen.db, or any WAL tail. E1's shared blind spot is stated in section 3.
- It does not check a NOT-DUAL-ORDER cache's order beyond the writer's source line and the stored columns (for refgated, the prompts are not stored).
- It does not check the pools each cache belongs to. The registration prints pools and does not assert them.
- It does not re-score any consumer readout (AGREE-ORDER, POSITION-DECOMP, POSITION-FULL, ORDER-1). No sign-inversion defect was found that would require it: every cache a readout treated as name-labelled is CONTESTANT by content.
- It does not show that row-level duplication is absent for the two E-COMB-only caches (no raw text to compare).

Verdict: CERTIFICATE HELD, CONFIRMED. P1, P2, P3 and P5 CONFIRMED; P4 PARTLY (HELD under D7 on an exclusion). The anomaly is RESOLVED as an instrument artefact (path-keyed name profile), with no effect on any criterion, prediction or index input. Record by insertion, no re-run. POSITION-INDEX-ALL may proceed on this certificate with items 5.1-5.7 carried into its run.
