# READY review: ARCH-V2-E-A (the G22 simulator and the G23 replay) at ca84e44

Adversarial reviewer, 2026-09-24. Zero judge calls. Read-only, single process. Selftests, dry-runs and my own mutants only. No R = 1,000 leg was run and no -wal file was created.

## DELTA READY 2026-09-24, the RB1-RB3 fixes at **74fc4f7** (on 6d35537): instrument_lf16 **876d01413318bd7b**; archv2_g22_sim.py unchanged, sha256-lf16:fee6e27a207fbbea

### Verdict

**READY FOR THE REPLAY**, which still needs the USER'S permission (ruling 1 (v); no agent message authorises it; I did not run it). Conditions:
- RP1: the run-operator launches the replay from the 74fc4f7 blobs. The replay's printed instrument_lf16 must read 876d01413318bd7b. On PASS, the chain file names exactly that successor.
- RP2: the registrar writes `experiment_configs/g22_rebind_chain.json` ONLY after a replay PASS and commits it. It is not one of the 11 hashed files, so writing it does not move the lf16. Its replay_output_sha must be the sha of the replay OUTPUT file, which the code checks for format only (the registrar checks the value).
- RP3: RB4 stays procedural. D0 / D2 run only on the author's recorded request.
- RP4 (LOW): the board-line comparison is vacuous when neither text has a board line. This shows on the fixture: "recorded None | replay None: EQUAL". It does not bite on the real record, which has exactly 1 board line (L26), so the replay must print an equal one. Better: require the recorded line to exist.

Pins: `git rev-parse 74fc4f7:<p>`, `git show 74fc4f7:<p> | sha256sum`. `git diff --stat 6d35537 74fc4f7` lists 2 files: g22.py blob:c21e0a33867aca0e15fe1c135089a931f0c8e580 / sha256-lf16:3d178b1bc6d7207d, and selftest_g22_rebind.py blob:69d1e569867691d1787b3cbdcd89ebede19817cc / sha256-lf16:a87ea1646bbf4dee. instrument_lf16 876d01413318bd7b recomputed independently from the 11 blobs: MATCH.

| # | check | result | evidence |
|---|---|---|---|
| 1 | Diff confined as claimed; replay computation untouched | CONFIRMED | The g22.py diff touches only: the MUTANT comment; the new REBIND constants and `rebind_accepts`; the instrument check in `load_token`, which now calls `rebind_accepts` only when the lf16 differs (the seal check before it and the record checks after it are unchanged); the MEETS suffix in designs_leg; and replay_v2's board-line comparison and print. Nothing in validity_leg, validity_v2_leg, the stores, the streams or the fits |
| 2 | The old → new fixture proof carries over | CONFIRMED BY RE-RUN | The OLD record from 17a93c7 (lf16 f37145df9516b7ec, `g22.__file__` in at17a), replayed in a separate process on the 74fc4f7 extraction (`g22.__file__` in at74f, lf16 876d01413318bd7b): block 9,852 bytes, lf16 107ab5bc277e9ee4 on both sides, BYTE-IDENTICAL; streams 111 / b19fc344… EQUAL; vm digest 3c8de66f… EQUAL; witness +24 records, 15 lines, 0 missing; PASS; no ONE_SHOT, no token. v1 fixture text f9ff45c7… |
| 3 | No instrument path writes CHAIN_PATH | CONFIRMED | `git grep -n "g22_rebind_chain\|CHAIN_PATH" 74fc4f7 -- tools`: the only non-selftest uses are the definition (g22.py L672) and a READ, `json.load(open(chain_path))` (L689). The selftest writes its chains under its tmp dir and restores CHAIN_PATH. The real `experiment_configs/` holds no rebind file (count 0) |
| 4 | The chain file sits outside the hashed files | CONFIRMED | CHAIN_PATH = `<data root>/experiment_configs/g22_rebind_chain.json`; no INSTRUMENT_FILES entry contains "rebind" |
| 5 | Fail-closed on the REAL token | CONFIRMED | Read-only `load_token` of G22_validity_v2.txt.validity_v2.json on the 74fc4f7 build: REFUSED ("… the rebind chain does not admit it (no chain file …)"). The ADMIT path is executed by the selftest with a temporary chain naming 876d01413318bd7b |
| 6 | `rebind_accepts` logic | CONFIRMED | The token digest must equal the pinned 3069666d…cdfc0; the token's lf16 must equal f37145df9516b7ec; the chain must exist and parse; all 5 fields present; the chain's old_lf16 and token_digest must equal the pinned values; its new_lf16 must equal the LIVE lf16; replay_output_sha must be 16 or 64 hex; registrar_commit must be 7-40 hex. Otherwise it refuses. The four builder mutants (missing chain, unchecked digest, unchecked old lf16, unchecked successor) are KILLED |
| 7 | RB2, RB3 | CONFIRMED (RP4) | MEETS gets " (optimistic by construction, ruling 2 (ii))"; the replay compares the `  board ` lines, and a changed line FAILS (selftest) |
| 8 | Selftests: G22 217, G23 44, python and -O | CONFIRMED | at74f: 217/0 and 44/0 under both interpreters. The real ONE_SHOT.json keeps its mtime of 11:31:42 |

## DELTA READY 2026-09-24, G22-REBIND-1 (registration 56751fa, programme L15667-L15686) at **6d35537**: archv2_g22_sim.py **sha256-lf16:fee6e27a207fbbea** (blob:72b0197805dbd77816db23453a0a92cab38ac86f), instrument_lf16 **d70f3608177046d0** (old f37145df9516b7ec)

### Verdict

**NOT READY FOR THE REPLAY, on one HIGH defect (RB1). The additivity itself is CONFIRMED.**

At 6d35537 the designs gate REFUSES the token of record. Ruling 1 (iii) requires the gate to accept "the pinned token_digest together with the new lf16 named in that chain", but `load_token` is unchanged in this diff. My execution on the new build, reading the recorded token read-only: "the token was produced by another instrument (lf16 f37145df9516b7ec, this one d70f3608177046d0); refused".

Any code added AFTER the replay to fix this changes g22.py (or archv2_g22_sim.py), so it changes instrument_lf16 again. The replay would then prove a build that designs and stop never run on, and the chain of ruling 1 (iii) would break. The acceptance must therefore land in the SAME build the replay proves, before the replay. Fix (RB1):
- `load_token` accepts a v2 token iff its token_digest equals the registrar-pinned 3069666d0f5e553ad61bd9cb8f178e2771d6fd683f63f01b8b35435cf56cdfc0, its instrument_lf16 is f37145df9516b7ec, AND the live instrument_lf16 is named as the successor in a chain file the registrar writes AFTER the replay PASS;
- that chain file lives OUTSIDE the 11 hashed files, e.g. `experiment_configs/g22_rebind_chain.json`, because a file cannot name its own hash;
- until the chain file exists, the old-token path refuses (fail-closed);
- plus a selftest with mutants for a missing chain, a wrong digest and a wrong old lf16.

The replay (ruling 1 (ii)) then proves exactly that build.

Everything else is READY: the storage, the replay mode, the ruling-2 lines and D15. Once RB1 lands, a short delta review of `load_token` and the chain file is enough, and the replay can be put to the USER (ruling 1 (v); no agent message authorises it; I did NOT run it).

Pins at 6d35537: `git rev-parse 6d35537:<p>` and `git show 6d35537:<p> | sha256sum`; the worktree is LF and clean. `git diff --stat 17a93c7 6d35537` lists exactly 4 files.

| file | blob | sha256-lf16 |
|---|---|---|
| archv2_g22_sim.py | 72b0197805dbd77816db23453a0a92cab38ac86f | fee6e27a207fbbea |
| archv2_arena/g22.py | 56d80aba4318218fa37a73b53139217ffb4e5fc3 | 13e630c18c5d1f77 |
| archv2_arena/selftest_g22.py | 608dc869a455bf0c9d811fa39e263b994ef5c513 | 513713722fa3eeba |
| archv2_arena/selftest_g22_rebind.py (new) | 4e169b09423fc1a77dacc1c79308eac1994fd87e | 9f45a679bef48717 |

instrument_lf16 **d70f3608177046d0**: I recomputed it independently over the 11 INSTRUMENT_FILES from the 6d35537 blobs (CRLF normalised to LF), and it matches the code's value.

### Claims (G22-REBIND-1)

| # | claim | result | evidence | mine vs claimed |
|---|---|---|---|---|
| 1 | The diff is ADDITIVE: no computed value, draw, stream name or draw order changes | CONFIRMED | I read all 461 diff lines of g22.py and archv2_g22_sim.py (17 removed). Every removed line is a signature gaining `store=None`, a call passing `store=`, the D15 print (token_digest in full, on the `token sealed:` line, which lies OUTSIDE the replayed block), the MODULES list, the designs names line (routed through `declared_deviation`), or designs / stop print text. `store_put` is called AFTER `run_reps` returns: it json-dumps the finished records (sort_keys; no mutation), writes once, prints with `print()` (not `say`, so the output text is unchanged), and consumes no RNG (mutant store_draws_random killed; the selftest compares the numpy and random states). Named streams are seeded by sha256(master\|name), so dropping D0 / D2 moves no other stream | no line alters a validity-v2 value. v1's golden f9ff45c7… holds (selftest; my proof below) |
| 2 | Old build → new replay, byte-identical on the fixture; the two processes really load different builds | CONFIRMED BY MY OWN RUN | My copy of the builder's script (scratchpad rev_ea/myproof.py) with ONE tree on sys.path per process: the `git archive` of 17a93c7 (old) and of 6d35537 (new) | old: `g22.__file__` = …/at17a/…, instrument_lf16 f37145df9516b7ec. new: …/at6d3/…, d70f3608177046d0. v1 fixture text f9ff45c7… in BOTH. Replay: (a) block 9,852 bytes, lf16 107ab5bc277e9ee4 = 107ab5bc277e9ee4, BYTE-IDENTICAL; (b) 111 streams, sha b19fc344… EQUAL; (c) vm digest 3c8de66f… EQUAL; witness +24 records, 15 quantile lines recomputed, 0 missing; PASS; ONE_SHOT created False; token minted False |
| 3 | The block extraction covers every verdict and table line of the REAL record | CONFIRMED | `extract_replay_block` (new code) applied read-only to experiment_results/archv2/g22_g23/G22_validity_v2.txt (blob 79e9348d, LF) | block = file lines 28-134 (107 lines), ending on the line before `  token sealed:` (L135). Table rows ending yes/NO: 48 in the block of 48 in the file. Both verdict lines (v2 PART A L99; VALIDITY v2 L126) and the D5 lines are inside. No stop-prefix line lies inside the block. Recorded block sha256-lf16 06039d95eff7b781. Outside the block, only the [POOL] line matches a verdict marker ("PASSED"). The streams line (58,039 streams, 0791961e…) is compared separately by (b). Not compared: the header's `board grok: 9131 valid verdicts …` line (L26), a data-object line (RB3) |
| 4 | Replay mode can never claim ONE_SHOT or mint a token | CONFIRMED (code and execution) | `record = not (dev or dry_run or replay)` → no claim. `--dry-run` with `--replay-record` takes the dry-run branch first (timings only, return 0). `--dev` with the replay → no claim, no token. A non-record master → `need(streams.master == expect_master)` refuses. `--replay-record` with another leg is ignored. The replay branch has no token write (only under MUTANT replay_mints_token, killed). My proof: ONE_SHOT created False, token minted False. The real ONE_SHOT.json keeps its mtime 11:31:42 (the record launch) after my selftests | - |
| 5 | Ruling-2 lines verbatim | CONFIRMED with one gap (RB2) | Programmatic comparison against the registered text: BIAS_LINE ends with the registered bias text verbatim (the prefix "  BIAS (ruling 2 (iii), 56751fa): " is added); ADMISSIBLE_AS contains ruling 2 (i) verbatim; DEFF_LOWER_BOUND verbatim; PASS_CHIP verbatim; token_digest printed in full; both counts; the deflated sensitivity ×1.06 / ×1.18 with Wilson, from the STORED records, "NOT a correction"; D0 / D2 NOT RUN with `--author-d0d2` | RB2: the registration says "a MEETS read on it is LABELLED 'optimistic by construction'". The code states it once in the ADMISSIBLE header, not on the MEETS line itself |
| 6 | Selftests: G22 203, G23 44, under python and -O | CONFIRMED | at6d3, both interpreters | 203/0 and 44/0; mutants store_draws_random, replay_touches_one_shot, replay_mints_token and bias_line_missing KILLED |

### Defects (G22-REBIND-1)

- **RB1 (HIGH, blocks the replay):** described in the verdict above. The rebind acceptance must be in the replayed build.
- **RB2 (LOW):** append "optimistic by construction" to every MEETS word on P(nominal >= 9), as registered in ruling 2 (ii).
- **RB3 (LOW):** the replay does not compare the header's board line (L26: 9,131 valid verdicts, 14 anchors, 12 models, snapshot 20260909_212117). It is not a deciding line, but it names the data object. The post-replay reviewer checks it by eye; better, add it to (a).
- **RB4 (LOW, procedural):** `--author-d0d2` can be passed by anyone. D0 / D2 are run only on the author's recorded request (ruling 2 (iv)).
- **Note:** the replay's record files are written beside `--out`, whose path must differ from the recorded output. write_once refuses a clash, but only after the records have been written. The run-operator uses a fresh `--out`. The replay may use any `--workers`: the stream log is merged in task order (w1 = w2 shown at ca84e44).

## DELTA READY 2026-09-24 at **17a93c7** (inserted above the ca84e44 review, which stands as written): archv2_g22_sim.py **sha256-lf16:719723d3163e7f4f** (blob:1019d61d42970dbce7a529a4b0ec5d67abc9943c)

### Verdict per leg at 17a93c7

| leg | verdict |
|---|---|
| G22 (a) v1 validity | **READY**, unchanged. The record run from main at ca84e44 stands, because 17a93c7 is byte-identical on v1 output (claim 7 below) |
| G22 (a') v2 fresh-judge (POST-HOC-SPECIFIED, one shot) | **READY-WITH-CONDITIONS** C1-C6 |
| G22 (c) designs, (d), (g), (e) stop | **READY-WITH-CONDITIONS** C3, C4 and C7. They run ONLY on a record v2 PASS token (run order (3)) |
| G22 (b) nu, (h) coverage | READY (unchanged) |
| G22 (f) with P7; G23 residue on merged | **READY**. D6 is fixed (exit 2 and a `.FAILED-PRECONDITION.txt` name), so condition F1 is now enforced by the code as well as by procedure |
| G23 identity, certab, conjuncts, holm, mcstreams | READY (unchanged) |

Pins at 17a93c7: blob / sha256-lf16 / sha256-crlf16, each verified with `git rev-parse` and `git show | sha256sum`. The worktree is LF and its lf16 equals these.

| file | blob | sha256-lf16 | sha256-crlf16 |
|---|---|---|---|
| archv2_g22_sim.py | 1019d61d42970dbce7a529a4b0ec5d67abc9943c | 719723d3163e7f4f | bc009ddbec1ca702 |
| archv2_g23_replay.py | f1763bf892578d291e41bb0061ead67e7a1b53cb | 8595768e18e63921 | 078ec55ed9a40d9c |
| archv2_arena/g22.py | 1d1ff47b04a94a00d34634482e25a7525f43cfa1 | b7f31cd4c97db231 | 1c2cd231bf6edd23 |
| archv2_arena/verdict_model.py | 418d979e3ca632340f739a9449180e653932bddf | c87ef3a34e7b3a7f | 969bb9949e54a638 |
| archv2_arena/selftest_g22_v2.py | bb1143cae99cfdc09d42d26b5f62ebbdef5c0ec3 | 9c8d993ddc3bc09f | 5b8d345f2d21a9c9 |

All other files are as pinned at ca84e44 (`git diff --stat ca84e44 17a93c7`: these 5 files only). The token binding is instrument_lf16 **f37145df9516b7ec**. I recomputed it independently from the 11 git blobs at 17a93c7, in the code's order with CRLF normalised to LF, and it matches.

### Conditions (delta)

- **C1. The one-shot claim, and recovery from a crash between claim and outcome (RULED here).** The claim is created (mode x) in main() before load_board, so before any real-data computation or figure. Only the header lines precede it. Two properties of the code matter for recovery:
  - A crash between claim and outcome strands the claim, and every later record launch is refused.
  - The output file is written only in finish(), but the console echoes the figures as they are computed (part A's tables print before part B runs).

  My ruling on recovery, for the registrar to record:
  - (i) The run-operator captures the whole console of the record launch to a file (tee).
  - (ii) If the process died BEFORE the first figure line (no "VERDICT MODEL" line and no "mode random" table in the captured console), the one shot is NOT consumed. The registrar records a dated bracket citing the console file; the claim file is renamed `*.VOID-<date>.json` (never deleted); ONE relaunch is allowed from the same pins.
  - (iii) If ANY v2 figure was printed, the one shot IS consumed. v2 is recorded UNDETERMINED (crash). It is neither PASS nor FAIL, and no relaunch is allowed without a new author decision (ruling 1 (v): no v3).
  - (iv) After a successful launch, the claim file and its sha are recorded in the programme with the outcome.
- **C2. No v2 figures on real data before the record run.** `--dev --leg validity-v2` on the record DBs still runs the whole leg, prints every figure and makes no claim (`record = not (dev or dry_run)`). That is a peek that defeats the one shot. Until the CLI refuses `--dev` for validity-v2 on the DBs of record (recommended fix, MEDIUM), the rule is procedural: none may be run. Already seen, and disclosed: the R = 1 figures of the pre-17a93c7 dry-runs (the specialist's DEV R = 1 / 3 / 30 diagnostics, and my a944d22 and ca84e44 dry-runs, which predate the suppression). v2 is declared POST-HOC-SPECIFIED on exactly that basis.
- **C3. Instrument freeze.** A record v2 token is bound to instrument_lf16 f37145df9516b7ec over 11 files, g23.py and data.py included. ANY later byte change to those files makes the one-shot token unloadable by designs and stop, and v2 cannot be re-run. So:
  - no edit to the 11 files between the v2 record run and the last designs or stop run;
  - the merge to main must be byte-identical, and instrument_lf16 is re-derived on main before launch;
  - if a designs or stop fix becomes necessary after v2, a registered re-binding rule is needed first: the gate accepts the registrar-pinned token_digest instead of the live lf16.
- **C4. The seal is integrity, not authentication (RULED).** `seal_token` is a public function of the instrument. My probe: a hand-built, record-shaped token (master REC-1, R 1,000, record True, parts PASS, T 14 / T2 12), sealed with g22.seal_token, is ADMITTED by the record gate. Anyone holding the code can re-seal. This does NOT block, because the gate's purpose is to stop ACCIDENTAL misuse (a DEV token, an edited status, another instrument's token), and those are refused: selftest checks D2 and mutant gate_presence_only killed. Deliberate forgery is excluded by the record, not by the code:
  - the registrar pins the record token's `token_digest` and file sha in the programme at the v2 outcome;
  - every designs or stop outcome must show that same digest. Today designs_leg prints only `vm_digest[:16]`. LOW fix: print `token_digest` in full.
- **C5.** Before the record launch, run `--leg validity-v2 --dry-run` from the launch checkout once, outside any other pool reader. Its console must hold no figure line (it must match what I observed, claim 3 below) and print the pool id and the timing line.
- **C6.** v1's conditions V2-V4 apply to v2: record master, R 1,000, single process or `--workers`; the `.streams.tsv` exists and its sha matches (my mutant R7 still survives); D9 is disclosed in the outcome.
- **C7.** Designs and stop admit only a sealed record v2 PASS token at instrument f37145df9516b7ec. `--dev` admits a sealed DEV token for non-record readings only.

### Claims (delta)

| # | claim | result | evidence | mine vs claimed |
|---|---|---|---|---|
| 1 | Selftests: G22 176 and G23 44 under python and -O | CONFIRMED | `git archive 17a93c7`, then `--selftest` with python and -O | 176/0 and 44/0 under both. python vs -O differ only in 1 timing line (2.16 / 0.340 s vs 2.14 / 0.343 s) |
| 2 | R3-R6, R8, R9 killed; gate_presence_only and one_shot_off killed | CONFIRMED | Builder's switches: selftest lines "D1 (R3)" to "D1 (R9)", D2, D3 all PASS. MY independent replacements (scratchpad rev_ea/mutants17.py): half seed ignored KILLED (split golden sha 0b031066…); dropped question KILLED (completeness check); T2 + 1 KILLED; LOMO leak KILLED (0-leak count); my fast-builder and u = 0 replacements crash on the new interface (TypeError, KeyError u_sd), while the builder's h2_fast and u_zero are killed by the exact-builder witness and the u-SD check | R7 (the `.streams.tsv` not written) still SURVIVES → C6 |
| 3 | The v2 dry-run prints no validity figure | CONFIRMED BY READING, THEN BY EXECUTION | Code: the dry-run passes `say = lambda *lines: None` into validity_v2_leg. No `print(` exists in g22, g23, data, cert, verdict_model, bt, streams, ro or design; report.py's only print is Out's echo. systematic_budget fit / established / nll / mcnemar_edge, jf.board_from and rj.mm_fit contain 0 prints. Then run on real data (109 s, single process): I counted figure markers by grep before viewing | 30 lines. The only lines matching the marker regex were the [POOL] line ("PASSED") and the timing line ("H2 builder"). No quantile row, verdict-model line, share or PASS/FAIL was printed. No claim file was created (`experiment_results/archv2/` holds only g22_g23/, before and after) |
| 4 | The timing on the real board is plausible | CONFIRMED (order of magnitude) | The same dry-run: "fixed stage 103.7 s \| per replicate 3.24 s (3 part-A modes + 1 part-B draw) \| about 0.93 h" | Builder: 129 s + 2.70 s → 0.79 h. Mine was measured while the run-operator's record legs were running (CPU contention). Per unit about 0.81 s, consistent with the v1 dry-run's 4.0 s total for load, fit and 3 replicates. The per-replicate figure is one draw per mode (noisy); read it as 0.8-1.0 h single-process |
| 5 | D2: sealed whole-token digest bound to the instrument; forged DEV tokens refused | CONFIRMED, with the caveat of C4 | Selftest: a DEV token, an altered field and another instrument's token are all refused. My 5dfc825 probe token (master DEV-ANY, R 3) would now fail on record, master, R, label, parts and T. My re-seal probe is ADMITTED (C4) | instrument_lf16 f37145df9516b7ec, recomputed |
| 6 | D3: claim with mode x before any computation | CONFIRMED | Code order in main(): header, then one_shot_claim, then load_board. `report.write_once` refuses an existing path. A second launch is refused while the file exists, whatever --out says. The selftest writes its marker under a tmp dir, never ONE_SHOT_PATH (verified: the real directory is unchanged) | Crash stranding is real → C1. `--dev` bypass → C2 |
| 7 | v1 still byte-identical | CONFIRMED | Fixture golden f9ff45c78a4f0249…, `cmp`-identical to 4c2d2b5's text. Real-data `--leg validity --dry-run` at 17a93c7 vs 4c2d2b5 differs ONLY in the header (now "DRY-RUN …", D10; the record-run header is unchanged for v1 in code), the witness line and the timing line | the verdict model, every table row and the stream-log sha are identical |
| 8 | D5 replacement as ruled (ccc1c50, L15422-L15448) | CONFIRMED | d5_lines: in-sample share var(β̂ k) / var(T), T = β̂ k + mean_g û; fresh share β̂² var(k) / (β̂² var(k) + σ²_LOMO), var with ddof 0; the v1 DEV R² 0.933 printed beside; Pearson of the LOMO errors on k_m with the two lowest and two highest models; β̂ on H1 vs the full board labelled "not independent"; corr(û, keyacc) kept as an OPTIMISER CHECK (\|·\| < 1e-3). Hand-checked in the selftest (0.72727) | ddof is not stated in the ruling (it changes var(k) by 12/11). Descriptive; LOW |
| 9 | D6-D8, D10-D12 fixed | CONFIRMED by reading and selftest | D6: exit 2 plus the file-name suffix, in both CLIs. D7: isinstance(list). D8: "N/A". D10: headings cite 83f431b / 4b25059 / 97f3a1f and the inner line says "PART A". D11: g23.py added to MODULES. D12: key-set identities compared | - |

### New defects (delta)

- **D13 (MEDIUM → C2):** `--dev --leg validity-v2` on the DBs of record runs the whole leg without a claim. Fix: refuse it in the CLI; the selftest does not use the CLI path.
- **D14 (MEDIUM → C3):** the token is bound to the live code of 11 files, so any later fix to designs or stop orphans the one-shot token. Fix: a registered re-binding rule, or freeze the files.
- **D15 (LOW → C4):** designs and stop print `vm_digest[:16]`, not `token_digest`. Print the full token digest.
- **D16 (LOW):** part B's "fresh judge" check is SD(u) > 0, a presence check. The fitted H1 u (SD > 0) would pass it. Fix: require that u differs across replicates.
- **D17 (LOW):** no recovery path from a stranded claim exists in code. The procedure is ruled in C1.

## VERDICT (per leg), at branch worktree-agent-a43fa24264b556ea7 HEAD **ca84e44**, archv2_g22_sim.py **sha256-lf16:eff3435a973c1cfd** (blob:522cefe751fcbf53d8e898f043218b697c254db2)

| leg | verdict |
|---|---|
| G22 (a) validity v1, AS REGISTERED (d6129cf; ruling 1 (i) of 83f431b) | **READY**, conditions V1-V4 below |
| G22 (a') validity FRESH-JUDGE v2 (POST-HOC-SPECIFIED, one shot) | **NOT READY**. D1 (HIGH), D2 (HIGH), D3, D4 and D5 (MEDIUM) must be fixed, then a delta READY |
| G22 (c) designs, (d) identification, (g) DEFF, (e) stop | **NOT READY** (D2 HIGH, the token gate). They are also gated on a v2 PASS under run order (3) |
| G22 (b) nu, (h) coverage | **READY** (descriptive; unchanged in substance since the provisional run) |
| G22 (f) overdispersion + residue (ruling B) + P7 scoring (ca84e44) | **READY-WITH-CONDITIONS** F1-F2 (D6 and D7 LOW). The precondition recomputes MET |
| G23 (a) identity | **READY**. Re-run it at ca84e44 as the record run; the identity code is unchanged since the provisional PASS |
| G23 (b) certab, (c) conjuncts, (e) holm, (f) mcstreams | **READY** (the code is unchanged since 4c2d2b5 except the residue leg) |
| G23 (d) residue (ruling B, merged precondition) | **READY-WITH-CONDITIONS** F1 |

Pins at ca84e44. Each file carries three identities: the git blob, sha256-lf16 (the LF rendering of record) and sha256-crlf16. The working tree is LF: wt-lf16 equals lf16 on all 17 files (command: `git rev-parse ca84e44:<p>`; `git show ca84e44:<p> | sha256sum`; `sha256sum <p>` in the worktree).

| file | blob | sha256-lf16 | sha256-crlf16 |
|---|---|---|---|
| archv2_g22_sim.py | 522cefe751fcbf53d8e898f043218b697c254db2 | eff3435a973c1cfd | 9023845e49799760 |
| archv2_g23_replay.py | c0dc861339032041f3d871456ff5216b412ddf77 | 0d07c4f20415778b | e22c358859d6ca82 |
| archv2_arena/g22.py | 257d14ca64328f1d48d52fc57b0386dc71690b3b | a8e7026c0d7e8c7a | 407a72846563346f |
| archv2_arena/g23.py | ff6a1201db9321c4379e933f1b4c9d34e4047410 | 882540d6ff955471 | 86d19c819e1019cc |
| archv2_arena/design.py | 4959cb525c8d07a26d19358c3f98342d5b28b3d2 | becd63768eedb8fc | c0e5c5ffd6dcd994 |
| archv2_arena/verdict_model.py | 2d6d0e2c9f494f33bfc40fab18a30d31b2d433ad | 10b9a030c3f09e47 | 5ba1fa98b405f8a1 |
| archv2_arena/selftest_g22_v2.py | bd1e73f96db66ae31cb360a28be466c925e6c86c | b3f4d8bffa636c41 | d478cfe70a36b9d1 |
| archv2_arena/selftest_g22.py | 88adb8247e51f9231282fc421fe9b6d82ac18aff | e12bf469e0071db9 | 50145f9087cd36d5 |
| archv2_arena/selftest_g23.py | 836679b59d9d1a3e5e83afd22c97bf1c4b215951 | 9f4933e7273dc383 | 7c941cd258be34e3 |
| archv2_arena/data.py | 7de0b135028ba96eab24b2ba998a62dd74e03247 | 78d3947f51dc8596 | 769163d4f95b4437 |
| archv2_arena/cert.py | d150ec9c3084352354bd83c4b106f7936f11d036 | 11e2ec7e76e0b495 | 1a5f2a861058b6d1 |
| archv2_arena/synth.py | 02db84ba5d3ee2c819bddc1be4455ec0e186b5ca | b64657775ffa4422 | 3633804b08d6b3f1 |
| archv2_arena/report.py | 51639563bdd47d48e0ec8b1673eee0e7b865653a | da954a3c4d1b833f | 50e5e1884a1eb849 |
| archv2_arena/ro.py | 98cfb84a58e7844e24b73ba301c2792cddc61b7c | 23d4f38710e3007f | 297117b2176e7cd7 |
| archv2_arena/streams.py | 30c23f9700a1309cda059c76bfe6fcbc6c41d64b | 315a30993d340650 | bd52a16174d485b7 |
| archv2_arena/bt.py | 8ee2e28b4fe9097f68b462562adaedea92f54813 | 138bd034706eb2e1 | b9c25ce1f79d1875 |
| archv2_arena/__init__.py | 210bd76eaff44916ea9d85b0d6dcccd711d85154 | ae6a0736954a8674 | 2f57cabe6c394809 |

History reviewed: f1192e6 → 4c2d2b5 → a944d22 → 805d830 → ca84e44. Every commit touches only `tools/analysis/` (count: 9 / 1 / 10 / 7 / 3 files, 0 outside; `git show <c> --name-only --format= | grep -vc '^tools/analysis/'`). Each ruling precedes the code that implements it: 83f431b 09:48 → a944d22 10:04; 4b25059 10:11 → 805d830 10:22; 97f3a1f 10:24 → ca84e44 10:27.

## Conditions of record

- **V1.** Run v1 validity from the pinned ca84e44 blobs (merge by path, byte-identical, or run from the branch at ca84e44) as `--leg validity --out <dir>/G22_validity.txt` with the default master ARCHV2-G22-REC-1, R 1,000, B 300 and floor 200, and the three modes random (primary), fixed and retest. Its outcome is recorded whatever it is (ruling 1 (i)). The R = 1 dry-run already prints random-mode f_raw_wrong 181 against 7, so a FAIL is expected. It then STOPS legs (c)-(e) only through the v1 token, which the designs gate refuses in any case (need_v2).
- **V2.** Under rule 7, single process or `--workers N`. `--workers 2 --dry-run` gives byte-identical output to `--workers 1` at ca84e44, including the stream-log sha 8cbd361f… and the witness. The extrapolation is about 1.2 h single-process.
- **V3.** After the run, the run-operator checks that `<out>.streams.tsv` exists and that its sha256 equals the "log sha256" line printed in the output. No selftest checks the stream log (mutant R7 survives).
- **V4.** The output's first line is `[POOL] p2dca21ab5f4ef3ae`. Its DB OPENS lists exactly 3 files (snapshots, grok_calib, eval), all immutable.
- **F1.** For G22 (f) and G23 residue on merged, use the exact builder only. A precondition line other than "REPRODUCED KTD-CHECK: called 1714 / 4(4) -> MET" is a FAILED PRECONDITION: record no residue reading and no P7 identity. The instrument prints this but still exits 0 (D6).
- **F2.** The reviewer has seen the (f) readout and the P7 reading on real data in a dry-run, because the overdispersion "dry-run" computes the whole deterministic leg. That readout is DEV and not of record. The P7 ruling (97f3a1f) was already declared post-data.

## Per-claim table

| # | claim | result | command / evidence | mine vs claimed |
|---|---|---|---|---|
| 1 | Selftests pass under python and -O (G22 121 at a944d22; 137 at 805d830; 148 at ca84e44; G23 44) | CONFIRMED | `python [-O] tools/analysis/archv2_g22_sim.py --selftest` and `archv2_g23_replay.py --selftest`, run on `git archive` extractions of each commit | a944d22: 121/0 and 44/0. 805d830: 137/0 and 44/0. ca84e44: 148/0 and 44/0, under both python and -O. The python vs -O outputs differ only in tmp-dir names (diff after masking: 0 lines) |
| 2 | v1 golden f9ff45c7… / vm digest f0dc0350… computed from the PRE-change code (4c2d2b5) | CONFIRMED | My own script (scratchpad rev_ea/golden_any.py, the builder's fixture call) run on the `git archive 4c2d2b5` tree, then on a944d22, 805d830 and ca84e44 | 4c2d2b5: TEXT_SHA256 f9ff45c78a4f0249a501b4e0daa5b82870d051fd0081e9f5525d2416fc16e0c3, vm f0dc035085378c4d…; the 30-line texts are byte-identical (`cmp`) at all four commits |
| 3 | The v1 execution witness is genuine | CONFIRMED | The witness counter `validity.v1_path` is absent at 4c2d2b5 and equals 1 at a944d22, 805d830 and ca84e44, on the fixture AND on real data | The discriminator exists only in the changed code, so the changed code ran |
| 4 | v1 byte-identity on REAL data (beyond the fixture) | CONFIRMED | `--leg validity --dry-run` on the 4c2d2b5 extraction vs a944d22, 805d830 and ca84e44 (same DBs, TAXOARENA_DATA_ROOT = main) | `diff` differs ONLY in the identity/blob lines, the start time, the DRY-RUN wall line and the witness line. The verdict model (digest ea25e7fd…), every quantile row, the stream-log sha 8cbd361f… and the verdict line are identical |
| 5 | Dry-runs print the pool id first and an extrapolated wall time | CONFIRMED (the v2 extrapolation is wrong: D4) | dry_v1_ca8.txt, dry_v2_ca8.txt | First line `[POOL] p2dca21ab5f4ef3ae: pool_guard.assert_pool_of_record PASSED`. v1: 4.4 s at R = 1 → "about 1.2 h". v2: 104.1 s at R = 1 → "about 28.9 h" (D4) |
| 6 | Read-only: immutable opens, no -wal created, no DB changed | CONFIRMED | `ls -l --time-style=full-iso` on 13 DB and sidecar paths before and after, diffed (13 lines, unchanged); sha256 of grok_calib, x12all and x20 before and after, unchanged (0b53f834…, eb0bec27…, 0826577f…); DB OPENS lines | v1 3 opens; v2 3; overdispersion 11; all `mode=ro&immutable=1`. The pre-existing -wal files are 0 B and unchanged |
| 7 | G23 identity (provisional PASS; tables sha 04754dbc…) | CONFIRMED (recomputed from the artefacts; not re-run: see D-note) | `cmp edges_v1_recorded_build.tsv edges_v2_new_builder.tsv` (identical, 921 lines = 920 edges plus a header); `sha256sum` = 04754dbc5d942dbf… | The provisional run was at 4c2d2b5 (its identity lines show g22_sim blob 09188836). The code the identity leg executes is unchanged since then: `git diff 4c2d2b5 ca84e44` touches only g23.residue_leg, data.KeyTable (missing_sources, default no-op) and the replay's residue branch |
| 8 | H2 targets use only H2 questions | CONFIRMED | Code: `board_by_questions(board, H2)` keeps rows whose question is in H2. edges_exact takes qs, la, gap and anchor_qs from those rows only (data.py L281-L330). Dry-run: H1 1,402 + H2 1,409 = 2,811 (the judged denominator), disjoint YES | H2 edges f 704 / u 722 / est 582 against the full board's 891 / 920 / 809 |
| 9 | keyacc on judged questions only; model-level (ruling A) | CONFIRMED | keyacc_matrix counts over `board.by[anc]` (judged rows) and pools correct / n over the anchors (design.model_level_keyacc). In the design legs the pool is the replicate's whole EVAL supply over all strata. The selftest compares against an independent formula (ka_expected), and mutant keyacc_cell is killed | as ruled (4b25059 (ii)) |
| 10 | The oracle-projection selftest is a genuine oracle, not β̂'s own fit | CONFIRMED | selftest_g22_v2.board_world: oracle = Σ(uc·KA)/Σ(KA²) from the GENERATOR's u_true, centred per anchor, on the centred model-level KA; β̂ comes from a separate fit | (β̂, oracle) = (4.884, 4.916), (4.158, 4.132), (4.673, 4.849), at 12 models × 10 anchors, 3 seeds, all within 0.5 |
| 11 | SHIPPED_PAIRS = FRAMEWORK L95 and GROK-CALIB L3928 | CONFIRMED | `sed -n 95p docs/design/FRAMEWORK.md`: b0 -3.2326, b1 +3.3133 (the 920 pair -3.0438 / +3.1980 is not yet adopted, per the UNFILTERED-ADOPT bracket). Programme L3928: "Fit b0 -3.5451, b1 +3.3854" | x12 = merged = (-3.2326, 3.3133); grok = (-3.5451, 3.3854) |
| 12 | Precondition on merged reproduces KTD-CHECK 1,714 / 4(4); x12 651 / 1(1); grok 649 / 1(1) | CONFIRMED (recomputed) | `--leg overdispersion --boards merged,x12,grok --dry-run` at ca84e44 (130 s) | merged 2,538 gap-filtered → widener 1,783 → after the decline 1,714 called, wrong 4(4), MET. The 4 edges are Law Llama-3.1-70B vs Qwen1.5-72B / deepseek-v2.5 / gpt-4o-mini and Philosophy Llama-3.1-70B vs gpt-4o-mini. x12 891 → 665 → 651, 1(1). grok 891 → 669 → 649, 1(1). The in-sample widener printed beside is -2.4305 / +2.4507 on merged; on x12 and grok it equals the stored pair (sanity) |
| 13 | Precondition fail-closed | PARTLY | Code and probe: on a mismatch or a fast builder, residue = "STOPPED", "NOT READ" is printed, and the G23 residue word is FAILED PRECONDITION; P7 identity → UNDETERMINED (selftest). BUT the leg exits 0 and writes its output (D6), and the "RESOLVED FROM THE DATA" line prints `{S, T, O, P, P, E, D}` (D7, probe) | the readout is withheld; the process does not fail |
| 14 | P7 scoring as ruled (97f3a1f) | CONFIRMED | Code reading of p7_score; builder's mutants p7_tie_held, p7_x12_scored and p7_roster_merged_only killed (148/0); dry-run readout | merged {Meta-Llama-3_1-70B-Instruct} unique at 4 → HELD (DEV). x12 and grok {Llama-3.1-70B, Qwen1.5-72B-Chat} → UNRESOLVED (one-edge tie). Roster OK on all 3 boards |
| 15 | v1 token accepted by the designs gate | REFUTED (the gate holds) | reviewer mutant R1 (need_v2 dropped) KILLED by 2 checks | - |
| 16 | POST-HOC label present on every v2 line | CONFIRMED | reviewer mutant R2 (g22.POST_HOC altered) KILLED by 2 checks | - |
| 17 | Registration Support of G22 is non-vacuous | CONFIRMED (arithmetic) | sqrt(p(1-p)/1000): 0.8 → 0.01265; 0.75 → 0.01369; 0.85 → 0.01129; 0.03 → 0.00539. MDE 2.8×: 0.0354, 0.0383, 0.0316, 0.0151 | all match the registration to the printed digits. DEFF 1.0 by design (independent re-draws); the source is stated |

### Reviewer mutants at ca84e44 (scratchpad rev_ea/mutants.py; each one patched in-process, then the full G22 selftest run)

| id | mutant | result |
|---|---|---|
| R0 | none (baseline) | 148 / 0 |
| R1 | the designs gate accepts a v1 token | KILLED (2) |
| R2 | the POST-HOC label is altered | KILLED (2) |
| R3 | the half split ignores the registered seed ARCHV2-G22-V2-HALF-1 | **SURVIVED** |
| R4 | halves disjoint but one question per anchor dropped (H1 ∪ H2 ≠ judged) | **SURVIVED in substance**: the check that failed was the builder's half_same switch, which my replacement function dropped |
| R5 | H2 targets from the FAST builder, not the builder of record | **SURVIVED** (only the printed words "builder of record" are checked) |
| R6 | part-B Bonferroni at T2 + 1 | **SURVIVED** (the real dry-run prints the correct 0.99583 = 1 - 0.05/12; the code is right, the test is absent) |
| R7 | `.streams.tsv` not written | **SURVIVED** (all legs, v1 included → condition V3) |
| R8 | LOMO refit keeps model m's observations (leak) | **SURVIVED** (the code excludes them correctly, `keep = (O.f != m) & (O.s != m)`; the test is absent). At a944d22 it was "killed" only because my replacement dropped the lomo_zero switch; re-run correctly at ca84e44 |
| R9 | part B simulates with u = 0 instead of a fresh judge | **SURVIVED** |
| R10 | overall v2 status = part A only | KILLED (1) |

## Defects

- **D1 (HIGH, v2): the one-shot v2 leg's deciding mechanics are untested.** Mutants R3, R4, R5, R6, R8 and R9 survive. The code is correct as written on each point (by reading, and on the real dry-run: seed, disjoint halves summing to 2,811, H2 from edges_exact, level 0.99583, LOMO exclusion, fresh u drawn by draw_u). But a ONE-SHOT, FINAL leg needs every deciding branch killed before its single irreversible run. Fix:
  - pin a golden of the split (sha of the sorted H1 ids on the fixture under ARCHV2-G22-V2-HALF-1);
  - assert H1 ∪ H2 = the judged set;
  - require a positive edges_exact witness delta inside part B;
  - write T2 and level2 into the token and check them;
  - add a mutant for the LOMO leak and one for the fresh u in part B.
- **D2 (HIGH, designs / stop): the token gate is a presence check.** `load_token(need_v2=True)` checks only `mode` and `status`, and the digest covers `verdict_model` alone. Probe: a hand-made token with master 'DEV-ANY', R 3, label 'anything' and status 'PASS' loads as VerdictModelV2. The selftest itself admits an R = 8, master 'SELFTEST-V2-A' token. Fix: require master == ARCHV2-G22-REC-1, R == 1,000 (or a registered R), label == POST_HOC, partA == partB == 'PASS', T == 14 and T2 == 12, and a digest over the whole token (status included).
- **D3 (MEDIUM, v2): ONE SHOT is printed, not enforced.** The leg can be re-run to any new `--out` under the record master. Fix: refuse when a `*.validity_v2.json` with the record master exists under the registered output directory, or require a one-time `--one-shot-ack <programme ref>` and log the launch append-only.
- **D4 (MEDIUM, v2): the dry-run extrapolation multiplies one-time costs by 1,000.** The formula is el × 1,000. The v2 wall of 104 s is dominated by 2 × 13 LOMO fits and the record builder on H2 (3,300 exact boards), which run once. "28.9 h" is therefore not a planning figure for the rule-7 window. For scale, the v1 dry-run (3 modes, the same fast builder) is 4.4 s in total. My timing run (`--dev --R 5`) was refused by the permission system, so the true per-replicate cost is UNDETERMINED. Fix: time the fixed stage and the per-replicate stage separately and extrapolate only the latter.
- **D5 (MEDIUM, v2; ruling A (v)): corr(û, keyacc) is IDENTICALLY ZERO by construction.** β is unpenalised, so at the MAP ∂/∂β = Σ KA_c · ∂ℓ/∂u = Σ KA_c · u / σ0² = 0. With both centred per anchor, the Pearson correlation is 0. Observed values: +0.0000 on real data (full board and H1) and -0.0000 on the fixture. The diagnostic the ruling asked for carries no information. Fix: the arena-specialist should name a non-degenerate diagnostic, for example corr(û_(-m), keyacc_m) from the LOMO fits, or the share of the total model effect's variance explained by β·keyacc. Until then, print the identity beside it.
- **D6 (MEDIUM, (f) / G23 residue): a failed precondition does not fail the process.** The leg prints "NOT READ" but exits 0 and writes its outcome file. Fix: a non-zero exit, or a FAILED-PRECONDITION suffix on the output name. Condition F1 covers it until then.
- **D7 (LOW, (f)): the residue string is rendered as characters.** With residue == "STOPPED", g22.py L1051-L1052 prints `{S, T, O, P, P, E, D}` (probe). Fix: test isinstance(list).
- **D8 (LOW): the precondition line reads "no precondition registered for board x12 -> MET".** This is a MET that certifies an exclusion. Print "N/A".
- **D9 (MEDIUM, disclosure, v1 and v2): the validity gate's interval ends rest on the ~2nd order statistic.** The central 0.99643 interval at R = 1,000 puts each end at q = 0.00179, which numpy interpolates between the 2nd and 3rd order statistics. H2's 0.99583 puts it at q = 0.00208. So a target near a tail flips with the Monte-Carlo draw. The registration calls the gate "deterministic given R" (true given the master) but states no Monte-Carlo error for it. Registered as is; disclose it in the outcome. It is not a blocker for v1, whose R = 1 read is 181 against 7.
- **D10 (LOW):** the dry-run header reads "RUN UNDER THE REGISTRATION ... R 1", and the v2 header names only d6129cf; inside v2, part A's inner verdict line says "REGISTERED ... legs (c), (d), (e) REFUSE". Say DRY-RUN and name 83f431b / 4b25059 for v2.
- **D11 (LOW):** G22's instrument-identity list (MODULES) omits archv2_arena/g23.py, which the v2 leg executes (record_count_targets → g23.v1_readout). Add it.
- **D12 (LOW):** part B's edge-set check (`edges_ok`) compares counts (f, u, est), not edge identities.

D-note on G23 identity: I did not re-run the G23 identity leg. It has no `--dry-run`, and a record-master run writes an output; a comparable run (`--dev`) was refused by the permission system in this session. I confirmed the identity claim from the committed-to-scratch artefacts (the two tables are byte-identical, sha 04754dbc…) and from the diff showing that its code path is unchanged. The record run at ca84e44 is the run-operator's.

## What this review does not show

- The per-replicate wall time of v2 (D4).
- Any rate-leg reading: (c), (d) and (e) were never run.
- That the P7 reading will hold in the record run. It is deterministic and should reproduce, but it is DEV here.
- The 46-model roster's membership beyond the models in the residue sets.
- Anything about a content-closed split (bareq512_s42 is id-disjoint only).
