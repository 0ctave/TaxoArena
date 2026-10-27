# READY review: paid prerequisites for RP21 (G17-CANARY) and RP20 (V2-NONE-TEMPLATE + ONE leg)

Reviewer: adversarial-reviewer, 2026-10-01. Base main 96d6ca1e; registrations L22762-L22784 (RP21) and L22786-L22810 (RP20)
(registrar 767ebb79); go: plan Amendment 34 ("Yes, include it"; "Keep ±4pp"). Zero calls, no draw, nothing posted.
This file is NOT a launch-gate file: the scripts' `--go` gates parse `READY_canary_epoch3.md` (G17-CANARY-V1E3) and
`READY_k46_repost.md` (K46-REPOST); those are written on the final blobs under the conditions below.

## Verdict

| branch @ tip | MERGE | dry-run (0 calls) | --go |
|---|---|---|---|
| rp32a-transport-check 5d179199 | **MERGEABLE** (1 added file) | n/a (tool) | n/a |
| canary-pass5 e1a307f2 | **MERGEABLE** (2 files; D1 of c6ee6155 CLOSED) | **READY** from main after the merge, under C-E3-1 | **READY** under C-E3-1..4 (date-gated 2026-10-08 by code) |
| k46-repost fb1430d8 | **MERGEABLE** (2 added files; nothing can post without the gate file; ONE leg hard-refuses) | **READY** (`--leg rp20/one/canary --dry-run`, `--freeze-canary --dry-run`) | **NOT READY** at fb1430d8: one delta (C-K1..C-K3) + the set file (C-K4) + a delta review, then the gate file |

No difference of substance between the 41cd5cbd drafts and the registered text that the code reads: every number in the
criteria, Support, ceilings and dates is the same (token diff of the draft §1 / §2+2b against the spans: the only
draft-only numbers are the unregistered 1,258-only alternative 2,516 / 5,032 / 5,290 and the count-drift brackets). The
code's own headers still say "NOT REGISTERED at build time" (LOW, D9).

## Pins (LF of record; `git hash-object` / `git cat-file blob | sha256sum`)

| file | blob (LF) | sha256-lf16 | worktree rendering |
|---|---|---|---|
| tools/analysis/transport_check.py | b9cb63ebc403524f2a945b6fdc71feaded69b755 | 15751997072a4969 | LF (same) |
| tools/analysis/canary_baseline.py | fbceff8dae5215659afd04aef8f7f717d43fb1bc | 5db7b3f4df19389a | sha256-crlf16 fc5f649bff90b1cc |
| tools/analysis/canary_baseline_selftest.py | 0026537fd752788681d515da1eead2aa520bb0de | 0093a5840c9e2bff | sha256-crlf16 94848ea07f6e8cf7 |
| tools/analysis/k46_repost.py | e7eb8e952cea985441b758da832ca9ba41078bc0 | 66df284f606838bd | LF (same) |
| tools/analysis/k46_repost_selftest.py | 11304607816cc35c3b4ee22f417d3d256a6b0970 | 00ba64b47195a05e | LF (same) |

Each branch: `git diff --name-only 96d6ca1e <tip> | wc -l` = 1 / 2 / 2; main moved since 96d6ca1e only in embed_quant*.py
(no overlap). pair_noref.py blob 2696e234 = fb1430d8 = main.

## Per-claim table (deciding claims only)

| # | claim | result | mine vs claimed | sev |
|---|---|---|---|---|
| 1 | RP32a acceptance: REFUSES 64ff708, PASSES 5e9de0f | CONFIRMED | 64ff708: posts 1, load_env 0 -> REFUSED; 5e9de0f: load_env 1 (pilot.py:1147) -> PASS; MET | - |
| 2 | RP32a selftest 16/16 (python, -O); mutants 7/7 | CONFIRMED | both green; 7 of 7 KILLED | - |
| 3 | k46 transport preflight INSIDE the dry-run, binding | CONFIRMED | RP32a (a) @fb1430d8 PASS (posts 8, load_env 1); (b) on `--leg rp20 --dry-run`, env-var K46_REPOST_ENV_ROOT: leg 1 OK on the fake host, leg 2 rc 1 refused -> PASS; my OK6 (refusal swallowed) KILLED | - |
| 4 | k46 identity gate on the store of record | CONFIRMED | own sqlite (immutable): 2,664 / ONE 818 / NONE 1,846 / A 1,039 B 1,022 TIE 600 INVALID 3 (all NONE) / 5,328 verdict rows / pool_id pv2_41dbd3dbcd399df0; dry-run IDENTITY GATE PASS; store sha256 44724d25 before = after (my dry-runs) | - |
| 5 | k46 bodies: C byte-identical, T one-span swap, T1 strip | CONFIRMED (by execution) | dry-run rp20: C 3,692 + T 3,692 slots; one: C1 1,636 + T1 1,636; 0 refusals | - |
| 6 | k46 counts / ceilings / day cap / --go / --budget | CONFIRMED | dry-run prints 3,692 m / 7,384 calls / ceiling 7,750; ONE 1,636 / 3,272 / 3,440; canary 1,260; DAY_CAP 14,000 over day_calls_<date>.json; --budget refused when absent and a hard cap in the poster (builder F1 + my OK3 KILLED) | - |
| 7 | ONE leg refuses without the go | CONFIRMED (static + selftest E4; my OK2 KILLED) | but a PRESENCE check of AUTHOR_GO_ONE (C-K2) | MEDIUM |
| 8 | k46 mutants 16/16; selftest 70 OK, 73/73 branches (python, -O) | CONFIRMED | re-run: 16 of 16 KILLED; selftest green both modes | - |
| 9 | k46 own mutants (8) | PARTLY | OK2, OK3, OK6 KILLED; OK8 (canary C1-v2 read on convention B) SURVIVED, decisive; OK4 (both-unusable not a difference) SURVIVED, decisive; OK5 (C0(b) kd census check removed) SURVIVED, decisive; OK1, OK7 SURVIVED, not decisive | MEDIUM (D3) |
| 10 | RP20/ONE interval form | UNDETERMINED in code | PRECONDITIONS interval_form=None -> every analysis refuses (fail-closed) | HIGH (C-K1) |
| 11 | pass-5 floors 26/21/28; pins of passes 1-4 | CONFIRMED | own script (immutable, convention A): 26/300, 21/300, 28/300; sha256 of pass 1-4 caches = the four pins | - |
| 12 | pass-5 selftest 44 OK, 19/19 branches; mutants 12/12; epoch-2 regression | CONFIRMED | green python and -O; 12 of 12 KILLED; --selftest-epoch2 green; canary_baseline_selftest 8 OK both modes | - |
| 13 | D1 (c6ee6155 M7) closed | CONFIRMED | M7 on a scratch copy of e1a307f2: new selftest AssertionError "ALARM STATE: NO ALARM" = KILLED | - |
| 14 | pass-5 own mutants (3) | PARTLY | OE1 date `>`: KILLED; OE3 transport after open_cache: KILLED; OE2 pilot errors dropped from the guard: SURVIVED, not decisive (--run refuses an uncached pilot job) | LOW |
| 15 | Support arithmetic (both registrations) | CONFIRMED to the digit | C1-v2 SE 0.01873, MDE 0.0524, bar p 0.1486; C1-v1 0.01759 / 0.0493; RP20 C1 0.01224 / 0.0343, n_eff 667.4, DEFF 1.885 from [0.7184,0.7840] (SE 0.01674 vs iid 0.01219), TOST 0.895 (0.867 at +0.5pp; 0.72 / 0.99 / 0.29 at DEFF 2.727 / 1.169 / 4.968; 0.82 / 0.69 at p_disc 0.12 / 0.15); C-ONE 0.03004 / 0.0841, n_eff 199.5, 0.113 at 4.934 | - |
| 16 | pool_guard cannot verify pv2 | CONFIRMED | `pool_guard.py --pool pv2_41dbd3dbcd399df0`: "not in the registry (known: p2dca21ab5f4ef3ae, paeec37aa28063c75)" | ruling R2 |

## Rulings on the builder's open points

- **R1 interval form.** RP20 C1 and C-ONE: the registration fixes it ("percentile form beside the normal form", L22786-L22810
  READOUTS): **normal decides**, percentile printed beside. RP21 C1-v2: the span is silent; **route to the registrar**, with
  the reviewer's reading "normal" (the same draft's convention; one match per component, so clustered = iid). `both_agree`
  is NOT implied: it adds an UNDETERMINED region the registered three-way rules do not have (a C-7 substitution).
- **R2 pool pinning.** Admissible substitute (stronger than the registry check): store run_meta pool_id + store sha256 + eval
  view sha e35b7518 (K46-KEY-READ's pins). Registrar brackets the HYGIENE words "verified by pool_guard.py --pool" in both spans.
- **R3 v0 reference-correct flag.** The draw does not use it; printing it at --analyze-canary (C2-v2 strata, done) instead of
  "with the set" changes nothing the draw decides. Admissible; registrar brackets RP21 INSTRUMENT pre-data.
- **R4 posting-order seeds.** Admissible builder's choice ("V2-NONE-TEMPLATE|20261002|", "REF-PAIRED-V2|20261002|"); the
  registration requires only "sha-pinned and printed". Registrar records the strings and the schedule shas of record (rp20
  5b9df7eeed023160..., one 1577f3a11b6e84dc..., as printed by my dry-runs) before any --go.
- **R5 three NOT BUILT readouts** (contested / cross-tier stratum; agreement with the reference side; the ONE leg's REF
  coefficient): all DESCRIPTIVE, none decides; each is printed "NOT BUILT" with its reason. Admissible only if the registrar
  brackets them pre-data (before any --go), so the omission is not post hoc.
- **R6 AUTHOR_GO_ONE.** Wire it in the C-K1 delta to the verbatim "Yes, include it", and make the gate a COUNT check: the
  quotation occurs exactly once under the heading `## Amendment 34` of docs/plan_2026-09-15.md (today: any truthy string passes).
- **R7 ceilings per script.** Admissible; the builder is right: atl.guard (iii) is an all-time combined statement
  (4,060 + every CEILINGS test's posted calls <= 14,000), so adding 1,260 / 630 / 7,750 / 3,440 there would refuse every
  other listed test after RP20 posts. The numbers in code equal the registration's. Registrar brackets "CEILINGS for
  accepted_tests_ledger.py" -> "enforced in the posting script".

## Conditions

- **C-E3-1** (canary-pass5, before the pass-5 READY gate file): after the merge, from main, run `transport_check.py --script
  tools/analysis/canary_baseline.py --dry-run-cmd "python tools/analysis/canary_baseline.py --pass 5 --dry-run"` ((b) PASS
  required) and the plain dry-run (pins UNCHANGED, floors REPRODUCED, date gate printed). Not run here: the worktree lacks the
  pass 1/2 caches.
- **C-E3-2** the reviewer writes `READY_canary_epoch3.md` naming G17-CANARY-V1E3 and sha256-lf16 5db7b3f4df19389a on the merged blob.
- **C-E3-3** pass 5 posts on its own day, not before 2026-10-08 (code), not on an RP20 posting day (run-operator; not enforced in code).
- **C-E3-4** `--budget 24` (pilot) then `--budget 576`; outcome only by --analyze-epoch3.
- **C-K1** (HIGH) one delta of k46_repost.py BEFORE ANY POSTING (caches pin script_sha16_lf in run_meta; a later delta
  refuses relaunch): PRECONDITIONS interval_form per R1 once the registrar rules; AUTHOR_GO_ONE per R6; D3 fixtures; D5-D9.
- **C-K2** (MEDIUM) R6's count gate, and print the combined RP20 + ONE statement (5,328 matches > 4,000, go: Amendment 34);
  (ii) is today per leg only.
- **C-K3** (MEDIUM) D3 closed: OK4, OK5, OK8 killed by the selftest (python and -O).
- **C-K4** the canary set file: `--freeze-canary` (zero calls, write-once) committed before the canary gate file (registration).
  Feasible: frame 2,661 -> alloc NONE/health 106 of 114 components, NONE/math 102 of 273, ONE/health 44 of 47, ONE/math 48 of 126;
  only NONE/math and ONE/math share components (6).
- **C-K5** registrar brackets R1 (RP21), R2, R3, R4, R5, R7 by insertion before the gate file.
- **C-K6** ordering of record: RP20 posts after RP21's C1-v2 is read (a FAILED C1-v2 re-registers RP20 pre-data), unless
  the research-lead relaxes it in the record.
- **C-K7** delta review of the C-K1 diff (re-run selftest, --mutants, OK4/OK5/OK8, transport_check (b) on all three legs),
  then `READY_k46_repost.md` naming K46-REPOST and the new LF sha16.

## Defects

- **D1 LOW** (rp32a) (b) leg 2 accepts any line containing "TRANSPORT: " as a refusal. Fix: require the preflight's own
  refusal prefix (`TRANSPORT PREFLIGHT: REFUSED` / `[...] TRANSPORT`), not a substring.
- **D2 LOW** (rp32a) (a) counts the selftest module's posting reference as reachable (k46: 1 of 8 is k46_repost_selftest.py:686).
  Fix: exclude `*_selftest.py` from reachability, or print them apart. (b) binds, so no verdict changes.
- **D3 MEDIUM** (k46) selftest misses three deciding wires: OK8 (C1-v2 read on convention B), OK4 (both-unusable pair not a
  difference; precedent `disagree_A` = 1), OK5 (C0(b) kd census 1,258/360 and 544/160 never asserted). Fix: a canary fixture with
  unusable rows where A != B, asserted by word; a both-INVALID pair asserted as 1; a cache whose kd census differs -> C0 FAIL.
- **D4 LOW** (both scripts) errored pilot jobs can be dropped from the pilot guard without a selftest failure (OK1, OE2). Not
  decisive: --run refuses an uncached pilot job. Fix: assert the guard line counts errors.
- **D5 LOW** (k46) the 20 extra seeds run at B/10 = 200 reps; registered "B 2,000 ... 20 more seeds beside". Fix: B.
- **D6 LOW** (k46) the kd census is read only at --analyze; a mismatch is found after 10,656 calls. Fix: print it in the dry-run
  (the sealed read K46-KEY-READ already made on the same store and view shas).
- **D7 LOW** (k46) the canary pilot guard allows 0 unusable of 12 matches (5% of matches); the registration says "5% unparsed"
  (per call would allow 1 of 24). Stricter side; registrar may bracket.
- **D8 LOW** (k46) draw stratum order (sorted) decides which of the 6 shared components goes to NONE/math; unregistered,
  fixed by the committed set.
- **D9 LOW** (both) headers/outcomes say "NOT REGISTERED at build time; built to the draft": cite 767ebb79 L22762-L22784 /
  L22786-L22810 in the C-K1 delta; for pass 5 the registrar brackets the outcome header.

## Commands (all zero-call; scratch = session scratchpad/rpp)

```
python tools/analysis/transport_check.py --acceptance | --selftest | -O --selftest | --mutants          (rp32a worktree)
python tools/analysis/transport_check.py --script tools/analysis/k46_repost.py --rev fb1430d8 --env-var K46_REPOST_ENV_ROOT \
   --dry-run-cmd "python <k46 worktree>/tools/analysis/k46_repost.py --leg rp20 --dry-run"   (TAXOARENA_DATA_ROOT=main) -> PASS
python tools/analysis/k46_repost.py --leg rp20 --dry-run ; --leg one --dry-run   (K46_REPOST_ENV_ROOT=fake .env) ; sha256sum store before/after
python tools/analysis/k46_repost.py --selftest ; python -O ... --selftest ; --mutants                        (k46 worktree)
python scratch/om_k46.py scratch/k   (OK1-OK8 on a git-archive copy) ; python scratch/om_e3.py scratch/cb (OE1-OE3)
python tools/analysis/canary_baseline.py --selftest-epoch3 | -O | --mutants-epoch3 | --selftest-epoch2 ; canary_baseline_selftest.py (both)
M7: scratch copy of e1a307f2 with alarm_state(c["floor"], c["floor"]) -> canary_baseline_selftest.py rc 1 "ALARM STATE: NO ALARM"
python - : sqlite immutable on pilot_k46_verdicts_run2.db (counts, strata, components) and on canary_baseline_pass{1..4}.db (floors)
python tools/analysis/pool_guard.py --pool pv2_41dbd3dbcd399df0 -> not in the registry
git cat-file blob <blob> | sha256sum ; sha256sum <worktree file> ; git diff --name-only 96d6ca1e <tip> | wc -l
```
