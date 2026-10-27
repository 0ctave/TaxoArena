# POSTRUN review: BZ-METER (granularity meter), 2026-10-11

Reviewer: adversarial-reviewer. Authority: author_decisions/2026-10-09.md D-2026-10-11-9. Prior reviews:
`READY_BZ-METER.md` (6d918381), `READY_BZ-METER-BUILD.md` (e3d24fbd, READY with C1-C4).

## Verdict: NOT REVIEWABLE (no run happened). This is not VALID and not INVALID.

The operator returned BLOCKED and did not run either calibration or `--vault`. There is no output to review, so the
registration-precedes-outputs check, the single vault read, the deciding numbers, the verdict words and the
per-dataset/level summary are all UNDETERMINED until a run exists. I confirm that the BLOCKED state is correct
and that nothing was written or read.

## Per-claim table (operator's BLOCKED claims)

| # | Claim | Result | Evidence (cmd below) | Sev |
|---|---|---|---|---|
| 1 | benchzoom master at e6d420d, tree clean | CONFIRMED | (a): tip e6d420d; `status --porcelain \| wc -l` = 0 | - |
| 2 | registration has no D1 / grid-top bracket after the build review | CONFIRMED | (b): whole-file grep count = 1, and that one match is L26 ("design D1" of the memo), not the review's D1. Registration last touched 19:01:04, review e3d24fbd 19:15:21 | - |
| 3 | no registrar record after e3d24fbd | CONFIRMED | (a): TaxoArena tip = e3d24fbd | - |
| 4 | `E:/benchzoom_demo/meter_v1` absent, 0 files written | CONFIRMED | (c): ls = no such dir; files under E:/benchzoom_demo newer than the build review: count 0 | - |
| 5 | vault not read / not altered | PARTLY | (d): vault id lists pass `sha256sum -c` (integrity), mtimes 14:27. No output dir exists, so no read was recorded. A read without a write cannot be ruled out from the filesystem | LOW |
| 6 | stopping before the calibrations is required (write-once meta.json pins the meter.py blob; C3 forbids a second `--out`) | CONFIRMED in substance | READY_BZ-METER-BUILD C3/C4 L76-L81. If the registrar picks the widen option (b), `TAU_GRID` changes in src/ and the pinned blob stops matching | - |
| 7 | "D2 / D3 (LOW, optional)" | REFUTED in part | the build review grades **D2 MEDIUM** (it is on the deciding SE path, M6 survivor) and D3 LOW. D2 is optional only because C2 replaces it (the n_clusters check 1960 / 4625 after the run) | MEDIUM |
| 8 | the C1 route needs a delta review "if widened" | CONFIRMED | review D1: option (a), keep + disclose, is one bracket that also names the binding readers in Section 6, with no new REG_BLOB. Option (b) needs a new REG_BLOB and a delta review of that line | - |

## Defects / conditions for the run

- P1 (blocks): C1 is open. The registrar must write the D1 bracket (option a or b) into `docs/meter_registration.md`.
  Section 6 must name the binding readers whichever option is chosen. Option (b): new REG_BLOB plus a delta review first.
- P2 (MEDIUM): put D2 back at MEDIUM in any hand-back. If the D2 test is not added in the D1 commit, C2 is mandatory
  after the run: `n_clusters` = 1960 (MATH) and 4625 (MMLU-Pro) in each `outcome.json`, or the run is INVALID.
- P3: C4 order stays as it is: `--calibrate synthetic`, then `--calibrate work`, then `--vault`, all at the D1 commit,
  default `--out`, no edits between steps, backup with SHA256SUMS. Before `--vault`, record the vault's
  sha256sum and the `--out` listing (zero files) so the post-run review can prove there was exactly one read.
- P4: the post-run review comes after that. It recomputes every deciding L-line gain and z from `outcome.json`
  and the cache, re-measures DEFF from the cluster sizes, applies the verdict words mechanically, and writes the
  per-dataset/level summary.

## Commands
```
(a) git -C Z:/FAC/TUBerlin/benchzoom log --oneline -3; git -C .../benchzoom status --porcelain | wc -l;
    git -C Z:/FAC/TUBerlin/THESIS/TaxoArena log --oneline -3
(b) grep -n -i 'grid top\|grid-top\|binds\|\bD1\b' docs/meter_registration.md   (whole file; 1 line, L26)
    git log -1 --format=%ci -- docs/meter_registration.md ; git log -1 --format=%ci e3d24fbd
(c) ls E:/benchzoom_demo/meter_v1 ; find E:/benchzoom_demo -newer docs/reviews/READY_BZ-METER-BUILD.md -type f | wc -l  (0)
(d) cd E:/benchzoom_demo/research_probes && sha256sum -c vault/SHA256SUMS.txt   (2 x OK)
```
Zero LLM calls. Zero vault reads by the reviewer (sha256sum hashes the id lists only, never the responses).

---

# POSTRUN review, round 2: BZ-METER after [R16] (benchzoom 72a7e66), 2026-10-11

Prior: `READY_BZ-METER-R16.md` (ec445ba9, READY with C2-C6; C5 blocks `--calibrate synthetic`).

## Verdict: NOT REVIEWABLE (no run happened again). This is not VALID and not INVALID.

The operator returned BLOCKED on C5 (F1) and ran nothing. The checks the brief asks for (registration and D1
bracket precede the outputs, exactly one vault read, recomputed deciding numbers, verdict words applied
mechanically, the per-dataset and per-level summary) have no object, so all of them are UNDETERMINED. The D1 bracket
itself does exist now: [R16] in 72a7e66, before any output. The BLOCKED state is correct, and the reviewer confirms
that nothing was written or read.

## Per-claim table (operator's BLOCKED claims)

| # | Claim | Result | Evidence | Sev |
|---|---|---|---|---|
| 1 | benchzoom tip 72a7e66, tree clean | CONFIRMED | (a) rev-parse = 72a7e6602945...; porcelain count 0; `log --all 72a7e66..` count 0 | - |
| 2 | no C5/F1 settlement anywhere | CONFIRMED | (b) registration: count of `R17\|C5\|F1` = 0, `informational` = 0; author_decisions 2026-10-08/09: `F1\|C5` no file, `BZ-METER` count 0/0; TaxoArena `ec445ba9..HEAD` count 0 | - |
| 3 | `E:/benchzoom_demo/meter_v1` absent, 0 files written | CONFIRMED | (c) `test -e` = ABSENT; files under E:/benchzoom_demo newer than the R16 review (20:12:31): count 0; repo files newer (excluding .venv/.git): count 0 | - |
| 4 | vault reads 0 | PARTLY (as round 1) | (d) both vault id lists `sha256sum -c` OK, mtimes 14:27 (before every review). No output, so no read was recorded. A read without a write cannot be ruled out from the filesystem | LOW |
| 5 | C5 blocks `--calibrate synthetic`, so the run order stops before the vault | CONFIRMED | R16 review C4/C5 (L59-L81). Skipping calibration would break the C4 order. Running it with no written expectation is what C5 forbids | - |
| 6 | F1 restated: the null fixture's L1\|L0 flips SUPPORTED to INCONCLUSIVE; the planted L2\|L1 stays NOT SUPPORTED | CONFIRMED | matches R16 review F1 (L47-L54) | - |
| 7 | "test fixture `PLANTED` (`meter_test.py` L798-799)" | PARTLY | `PLANTED` is at `tests/test_meter.py` L528 (cat_sd .4, fine_sd .3). `examples/meter_test.py` L798-799 is the RUNNER fixture that option (b) changes (cat_sd .25, fine_sd .2). The pointer comes from the R16 review's own ambiguous wording | LOW |
| 8 | D4 still open | CONFIRMED | R16 review L56 | - |

## Conditions for the run (they carry forward; nothing new blocks)

- Q1 (blocks, the registrar's call): settle C5 in writing as F1 (a), (b) or (c), per the R16 review. (a) and (b)
  each need a delta review before C4 starts. (c) needs only the bracket with the expected calibration words, and the
  operator runs at 72a7e66.
- Q2: if (b) is chosen, the new runner fixture should match `tests/test_meter.py` L528 `PLANTED`, or a stated
  equivalent, and its expected words go into the bracket. Otherwise D4 (words are not a gate) leaves the
  calibration with no reader.
- Q3: C2 (n_clusters 1960 / 4625 in each `outcome.json`, any other count INVALID), C3 (default `--out` only) and
  C4 (dry-run, synthetic, work, pre-vault sums plus the empty listing recorded, `--vault` once, then SHA256SUMS and
  a backup) stand unchanged, at the commit that settles C5.
- Q4: the next post-run review recomputes each deciding L-line gain and z from `outcome.json`, re-measures DEFF
  from the vault cluster sizes (C6), applies the words mechanically, and writes the plain-language per-dataset and
  per-level summary (slope fix, category, declared finer labels, text over the difficulty/length control, tree leaves).

## Commands
```
(a) git -C Z:/FAC/TUBerlin/benchzoom rev-parse HEAD; status --porcelain | wc -l; log --all --oneline 72a7e66.. | wc -l
(b) grep -c "R17\|C5\|F1" docs/meter_registration.md (0); grep -c informational (0);
    grep -lE "F1|C5" docs/agents/author_decisions/* (none); grep -c BZ-METER (0,0); git log ec445ba9..HEAD | wc -l (0)
(c) test -e E:/benchzoom_demo/meter_v1 (ABSENT); find E:/benchzoom_demo -newer docs/reviews/READY_BZ-METER-R16.md -type f | wc -l (0);
    find benchzoom -path ./.venv -prune -o -path ./.git -prune -o -newer <same> -type f -print | wc -l (0)
(d) cd E:/benchzoom_demo/research_probes && sha256sum -c vault/SHA256SUMS.txt (2 x OK); ls --full-time vault/
(7) grep -rn "PLANTED\s*=" tests examples src (tests/test_meter.py:528); sed -n 795,800p examples/meter_test.py
```
Zero LLM calls. Zero vault response reads by the reviewer: sha256sum hashes the files and never parses them.
