# POSTRUN review: BZ-METER run of record meter_v1, 2026-10-11

Reviewer: adversarial-reviewer. Authority: author_decisions/2026-10-09.md D-2026-10-11-9. Reviewed objects: benchzoom
master 868ea73 (registrar settlement) + e1fb080 (operator record); outputs `E:/benchzoom_demo/meter_v1`. Prior
reviews: READY_BZ-METER-R17.md (e12f5149), POSTRUN_BZ-METER.md (rounds 1-2, NOT REVIEWABLE). Zero LLM calls.

## Verdict: VALID. State of record: HARNESS FAILED (MATH, [R7]). No real-label result exists.

The run followed the registered order. The registration and the settlement were committed before every output.
The vault was opened exactly once per dataset. I recomputed the one deciding statistic (the MATH harness) to the
digit, and FAILED is the correct mechanical reading of the registered rule: |G| 0.016671 > 2 SE = 0.014982. The run
stopped before the nulls, as [R7] requires. There is no null, no level word, no depth word and no slope word for
the vault. Not one BZ-METER prediction or falsifier was decided.

## Per-claim table (deciding claims)

| # | Claim | Result | Mine vs claimed | Sev |
|---|---|---|---|---|
| 1 | Registration precedes outputs | CONFIRMED | reg a5dd424 20:50:53, settlement 868ea73 21:06:53; first output (calibration_synthetic/null) 21:10:49, vault outputs 21:40:46-21:43:44. meta.json (vault and calibrate work): commit 868ea73, dirty "", reg_blob a192f65d = `git show 868ea73:docs/meter_registration.md \| git hash-object --stdin` (LF; the working-tree file hashes the same, so no CRLF rendering differs). Runner LF 90cb83ce, meter.py 1b6c7385 = the READY_R17 pins | - |
| 2 | Exactly one vault read | CONFIRMED | log `reads=1` for both datasets. `VaultGuard.open()` is the only path to vault rows and increments `reads`. meter_core calls it once per dataset (L495-496) and asserts reads==0 before meta.json (L470). Write-once: outcome.json exists, so a second `--vault` is REFUSED (L464) | - |
| 3 | MATH harness G -0.0167 SE 0.0075 tau2 0.005, FAILED | CONFIRMED to the digit | own G/SE/DEFF arithmetic (cmd A): G -0.016671, SE 0.007491, SE_iid 0.007234, tau2 0.005, n 1960, 135,240 cells, 69 models; \|G\|/SE 2.226 > 2, so FAILED | - |
| 4 | MMLU-Pro harness PASSED (G 0, SE 0, tau2 0) | CONFIRMED | tau2 0.0 selected, so the pass is by the registered clause "tau2 = 0" (the intended no-signal pass, not vacuous by the registration); 107,042 cells, 23 models | - |
| 5 | Clusters MATH 1960/1960, MMLU-Pro 4625/4654 | CONFIRMED | K 1960 (max cluster 1); K 4625, 29 two-item clusters, max 2 | - |
| 6 | DEFF re-measured | CONFIRMED | MATH DEFF 1.0724 (claimed 1.0724), n_eff 1827.7. All clusters are singletons, so DEFF > 1 comes from item-weighting against cell-iid, not from clustering. MMLU-Pro DEFF NaN (SE 0, degenerate). Harness MDE at the 2 SE bar = 0.0150 x1e-3 nats. No deciding real-label statistic exists, so there is no real-label MDE | - |
| 7 | Words applied mechanically | CONFIRMED | `harness_check` L571 = [R7] text (reg L182): pass iff tau2 = 0 or \|G\| <= 2 SE. Any FAILED stops before the nulls (L517-521). outcome.json state "HARNESS FAILED"; harness.json holds only harness fields | - |
| 8 | Synthetic gate PASSED to the [R17] digits; work harness PASSED | CONFIRMED (spot) | gate.txt last line PASSED; calibration_work/outcome.txt harness lines match the record | - |
| 9 | Settlement D4: fixtures MATCH | CONFIRMED | own check: `calibration_synthetic/{null,planted}/meta.json` fixture == SYNTH_FIXTURES: True, True | - |
| 10 | Vault sums OK, backup identical | CONFIRMED | vault 31c111e3/4bcd0baf unchanged; `sha256sum -c` meter_v1/SHA256SUMS 5/5 OK; backup SHA256SUMS.txt 38 lines, 0 non-OK; `diff -rq meter_v1 backup/meter_v1` empty | - |
| 11 | Settlement is insertion-only, before the run, names the main session | CONFIRMED | 868ea73 = 1 new file, 32 insertions (`git diff a5dd424 868ea73 --name-only \| wc -l` = 1); bracket S1 names the TaxoArena MAIN SESSION and D-2026-10-11-9. Registration and runner untouched | - |

## Plain-language summary per dataset and level (vault of record)

The vault gives no result at any level for either dataset, because the run stopped at the leak check:
- **MATH:** difficulty slope, category (L1), declared finer labels (L2 / L2a), text beyond difficulty/length
  control (L3t / L3k), tree leaves: **NOT MEASURED.** The leak check with random vectors gave a small *negative*
  gain. That means the random-vector reader did slightly worse on the vault, which looks like overfitting at the
  smallest tau2 = 0.005. A leak would show up as a positive gain. Under the two-sided registered rule it still FAILS.
- **MMLU-Pro:** the leak check passed (no random-vector signal was fitted). Every level is **NOT MEASURED**,
  because the run stops on any failed harness.
- The pseudo-vault words in calibration_work (MATH L1/L2/L3k SUPPORTED, DEPTH L3; MMLU-Pro L1/L2 SUPPORTED, L3k
  NOT SUPPORTED, DEPTH L2) are a dress rehearsal on WORK rows. The registration calls them "not evidence", and they
  must not be quoted as BZ-METER results.

## Defects

- **F1 LOW (agree with the operator).** `--vault` returns 0 after HARNESS FAILED (L885-886). Fix: return 1 when
  `oc["state"] != "READ"`, and add a test.
- **F2 MEDIUM (design, binds any re-registration).** [R7] is a two-sided 2 SE rule on a statistic whose expected
  value is negative once tau2 > 0 is selected by CV (optimism). So the rule fails on overfitting, which is not leak
  evidence. WORK-only check (cmd B, no vault row): 30 random-vector draws on the MATH pseudo-vault gave 1/30
  FAILED (seed 12, z -2.65). 9 of 30 selected tau2 > 0, and 7 of those 9 had G < 0. The vault MATH draw (z -2.23)
  matches this pattern. Fix for a new registration: a one-sided rule (fail iff G > 2 SE), or K draws with a
  pre-computed false-fail rate. This is a design change, so it needs a new registration and its own review. It
  cannot be applied to meter_v1 (C-7: the registered rule binds).
- **F3 LOW.** `calibration_synthetic/{null,planted}/meta.json` carry no `code`/`reg_blob` (both None). Provenance
  rests on mtimes after 868ea73 and on the digits matching [R17]. Fix: write `code_state()` + reg_blob there too.
- **F4 LOW (record wording).** The operator's "fails ~5% by chance" is the Gaussian two-sided figure. The
  empirical rate (cmd B) is about 3% for MATH, and MMLU-Pro cannot fail while tau2 = 0. Descriptive only.
- **Reviewer disclosure.** Cmd A re-opened the vault matrices in memory (once per dataset, in a scratch process,
  nothing written) and computed only the [R7] harness contrast. No null and no real-label contrast was computed.
  The vault sha256 sums and every meter_v1 file were unchanged before and after (cmd C).

## Author decisions (unchanged from the operator's, sharpened)
1. meter_v1 is closed as HARNESS FAILED. Any re-read is a new registration on vault rows already opened. No real-label statistic was ever computed or written, so nothing seen has to be hidden. Adopt the F2 fix before any re-run.
2. D1 (slope wording) is still open. It is moot for meter_v1 because no slope word was produced.

## Commands (benchzoom, PYTHONPATH=src; scripts in the session scratchpad, read-only)
```
git log --format='%h %ad %s' --date=iso -8; git show --stat 868ea73 e1fb080
git show 868ea73:docs/meter_registration.md | git hash-object --stdin; git hash-object docs/meter_registration.md examples/meter_test.py src/benchzoom/meter.py
ls -la --time-style=full-iso E:/benchzoom_demo/meter_v1 E:/benchzoom_demo/meter_v1/*/
A: harness_recompute.py  -> load_dataset (pins checked), guard.open once, M.chain(cv), random vectors [NULL_SEED,0,0], M._restep;
   own log-loss diff, item means, cluster sums over d.groups, CR1 SE, cell-iid SE, DEFF, |G|/SE (3m00s)
B: harness_rate_pseudo.py 30 -> pseudo_vault(math) (orig guard reads 0), 30 random-vector draws, M.contrast_stats -> fails 1/30
C: sha256sum <probes>/vault/*.json meter_v1/*.json + file counts before/after A: diff empty; git status --short | wc -l = 0
python -c "...meta.json fixture == T.SYNTH_FIXTURES[nm]" -> True True
cd meter_v1 && sha256sum -c SHA256SUMS (5 OK); backup: sha256sum -c SHA256SUMS.txt | grep -vc ': OK$' = 0; wc -l = 38; diff -rq (empty)
```
