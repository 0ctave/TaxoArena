REVIEW: READY-1
REGISTRATION: BZ-AXIS-CONFIRM-MMLU
REGISTRATION-COMMIT: f53ec853
VERDICT: READY

# READY-1 review (pre-data): BZ-AXIS-CONFIRM-MMLU

Reviewer: adversarial reviewer, 2026-10-22, TaxoArena `_as_of 803c5b04`; benchzoom master 0086e9e (tree clean,
`git status --porcelain --untracked-files=no` = 0 lines). Zero LLM calls. No HELM prediction / per-instance stat / score
file and no tinyBenchmarks file opened; no HELM file fetched by me. Prior review: READY_BZ-AXIS-CONFIRM-MMLU.md (5109ef9c).

Reviewed blobs (benchzoom 0086e9e; `git hash-object` = LF of record; working tree CRLF, `--no-filters` beside):
`examples/axis_confirm_mmlu.py` blob:83b43094 (crlf 785b174e); `examples/fetch_zoom_data.py` blob:866ff876 (crlf
c7430c8e); `examples/mmlu_confirm_items.py` blob:4758147b; `examples/mmlu_confirm_census.py` blob:2efd7894;
`examples/mmlu_confirm_build.py` blob:d7973c5a; `tests/test_axis_confirm_mmlu.py` blob:988ca89a.

## Verdict

**READY** (READY-1): authorises the HELM / tinyBenchmarks fetch (`axis_confirm_mmlu.py fetch`) and the WORK mode ([A1])
only. No vault read: that needs READY-2 with conditions C1-C3 below. The known gaps of the brief are CLOSED: the
synthetic gate was re-run on the current runner blob (byte-identical, row 6) and the full suite was re-run at 0086e9e
(row 9).

## Per-claim table (deciding claims)

| # | claim | reviewer's number / finding | state | sev |
|---|---|---|---|---|
| 1 | tree: 184 nodes, 100 leaves, depth 5; pickle 900d12d8, tree.csv 9a97d530, manifest 8cdfb591 | sha256 all three equal; pickle: 184 nodes, 100 leaves; tree.csv: 184 rows, 100 leaves, max depth 5, leaves by depth {1:1,2:7,3:23,4:39,5:30}, leaves partition 14,042 items, per-L1 counts equal the census list; pickle `config` = MMLU-Pro manifest config (0 field diffs) and = the MMLU-Pro pickle-of-record config (0 diffs); `script.git_hash_object_lf` cef9440a; 512-d MRL prefix of 4096-d | CONFIRMED | - |
| 2 | built with blob cef9440a + src da3bf22 (route 1) | `benchzoom_build_da3bf22`: HEAD da3bf222, 0 dirty paths, `hash-object examples/identifiable_map.py` cef9440a, `HEAD:src` 187032bd; driver d7973c5a refuses a foreign HEAD / dirty src / other blob and asserts `benchzoom.__file__` lies in the pinned checkout | CONFIRMED | - |
| 3 | MMLU-Pro rebuild identical (sha differs only by `seconds` / last-ulp gate_stats) | `_repro_mmlu_pro` vs `axis_v1/_work/mmlu_pro_axis_seed0.pkl` (sha e1d0b00a): 147 / 147 nodes, 80 / 80 leaves, 0 nodes differing in (id, parent, depth, children, rows). Corroboration only: route 1 needs no bit-identity | CONFIRMED | - |
| 4 | split vault 5,614 / WORK 8,428; 83 dropped (>= 0.98, 4096-d); 5,531 kept | own script (no benchzoom split code): parquet sha 74a41822; vault 5,614 ids_sha d3a0b5ce, WORK 8,428 0ad5fd11, dropped 83 4ad91d7b (106 at 0.95, 58 at 0.995), kept 5,531. Id files: dup-key 54 / 26c4e7f6, Redux 369 / 18d06bfc, MMLU-Pro overlap 6,608 / f3595912 (spot check, all equal) | CONFIRMED (digit) | - |
| 5 | roster 79: jamba-1.5-mini dropped by E5 (v); E5 (iv) none refused; E5 (vi) 27 groups by order, 0 excluded | `census_instances/instances.json` (sha 2a4534fa): 80 models; 79 x (57 runs, 14,042 test instances, 14,042 matched, 0 unmatched, 27 by-order groups); jamba-1.5-mini 13,259 matched (< 13,902; miscellaneous instances.json HTTPError); `e5_iv_refused` [] ; `e5_vi_excluded_ids` []; roster ids_sha 9a2afba1 recomputed. 0 cais duplicate-key groups carry differing answers, so the 4 HELM-vs-cais key disagreements are NOT by-order mis-pairings | CONFIRMED | LOW (D6) |
| 6 | synthetic gate PASSED (of record on runner b6be86f5) | re-run on blob 83b43094, 4 BLAS threads, into E:/TaxoArena_tmp/ready1_mmlu_review/syn: gate.txt d482f304 and the 4 outcome.json (a0d7fd1a, 20f6133c, 921dfc15, 5f3d14d4) BYTE-IDENTICAL to the record. The b6be86f5 -> 83b43094 diff touches only `helm_matrix` (now `instance_join`) and an import; the synthetic path does not call it, so identity is expected; `helm_matrix` is executed by the tests (row 9) and killed mutant R3 | CONFIRMED | - |
| 7 | only run_spec.json and instances.json were read before READY-1 | code: `read_allowed` is the census's only HELM object reader and refuses any other name (mutant R8 killed); `_GcsFiles.read_json` streams to memory. Disk: `find` over E:/benchzoom_cache, E:/benchzoom_demo, E:/TaxoArena_backup_2026-10-21_axis_confirm_mmlu, E:/TaxoArena_tmp and both benchzoom trees for display_predictions / per_instance_stats / stats.json / scenario_state / lb.pickle / tinybench / instances.json / run_spec.json: 2 hits by count, both the census OUTPUT instances.json (30,720 B) and its backup; `E:/benchzoom_cache/mmlu_confirm` holds only `_raw` (no `helm/`, no `tinyb/`). Limit: a streamed network read leaves no disk trace; the claim rests on the code path | CONFIRMED | - |
| 8 | READY-1 gate strict; runner gates every data mode | `ready1_gate` = `fetch_zoom_data.ready1_refusal` first in fetch / work / vault, again in `load_real` and `run_fetch`; `_registration_commit_refusal('f53ec853')` None, ('5109ef9c') refuses; mutant R2 (VERDICT startswith) killed. Weakness: '803c5b04' (author-decisions commit) also passes (D3) | CONFIRMED | LOW (D3) |
| 9 | full suite after 0086e9e | benchzoom .venv, OMP/BLAS 1 thread, TMP in sandbox: **778 passed, 1 skipped, 4 deselected** (625.7 s; builder at 2de0b90: 777 + 1 + 4); benchzoom tree still clean after the run (0 porcelain lines) | CONFIRMED | - |
| 10 | Support at the census n | kept vault 5,531 x 79 models: SE = 0.0183072 x sqrt(4,654/5,531) = 0.01679; MDE80 3.84 x 0.01679 = 0.0645 < 0.10; n_eff 5,531/1.1257 = 4,913; stress 0.0628 x sqrt(1,960/5,531) = 0.0374, MDE80 0.144; DEFF at 79 models under constant ICC 1.446 (transport stays conservative). SCOREABLE stands; condition (f) remains the live risk (stress) | CONFIRMED | - |

## The three open choices (settled; pre-data, before any WORK read)

1. **Condition (f) = MEDIAN vault MDE80 of C-M1 over the 5 pseudo draws (min, max printed): ACCEPTED.** The draws are
   replicate estimates of ONE vault SE at the fixed full-WORK tau^2 (D2 fix); the median is the registered single
   "vault MDE80"; the condition reads SE only, never g, so no outcome enters. `max_reaches` stays printed. This file is
   the pre-data record; [A1] cites it.
2. **Z "net of its own cut-at-cells re-read" = G(cut_d | P) - G(P cells | P), paired per item: ACCEPTED, wording
   fixed.** For |L1 the depth-1 cut IS L1, so it coincides with D4 literally; for |L2 the cuts cross subjects and the
   parent re-read is the only nested artefact. Every Z quotation says "net of the parent's cells re-read". Z decides
   nothing. (C-M3's null sharing the leaf-within-L1 permutation: ACCEPTED, as the meter_axis parent.)
3. **SECTION_SHA "PENDING" until [A1]: ACCEPTED (fail-closed).** `vault_refusals` compares sha256(section text) with
   SECTION_SHA; no text hashes to "PENDING", so the vault refuses today (section sha at f53ec853 = at HEAD = 47d6f4c3,
   59 lines, recomputed). The registration GUARD names "the programme blob"; the section-text sha replaces it (the blob
   changes on every unrelated insertion): accepted substitution, recorded here (D4).

## Defects (none blocks READY-1)

- **D1 (MEDIUM; condition C1 for READY-2)** `vault_refusals` accepts any PASSED `calibration_synthetic/*/outcome.json`
  under `--out`; the meta records no runner blob, so the gate is not bound to the code that reads the vault (the record
  was written by b6be86f5). Fix: write `git hash-object` of the runner into the synthetic meta and refuse unless it
  equals the vault-time blob, or re-run synthetic into a fresh `--out` at the READY-2 blob.
- **D2 (LOW)** the vault clean-code list omits `examples/fetch_zoom_data.py` (its `ready1_refusal` is on the vault path)
  and `examples/mmlu_confirm_build.py`. Fix: add both.
- **D3 (LOW)** `ready1_gate` does not bind REGISTRATION-COMMIT to the runner's `REGISTRATION_COMMIT = "f53ec853"`;
  803c5b04 passes. Fix: require `f53ec853` as a prefix of the header value.
- **D4 (LOW)** GUARD substitution programme blob -> section sha (choice 3); disclose in [A1].
- **D5 (LOW)** the census doc's opening paragraph still says no `instances.json` / `run_spec.json` was read; the
  2026-10-22 instance census section supersedes it. Fix: insertion bracket on that paragraph.
- **D6 (LOW)** HELM's tagged reference differs from the cais answer on 4 of 14,042 items (not duplicate-key effects);
  no rule reads it. Fix: print the 4 ids in the WORK run.

## Conditions carried to READY-2 (vault)

C1 D1 fixed or the synthetic gate re-run at the vault-time blob. C2 SECTION_SHA = sha256 of the section after [A1],
and the section's diff vs f53ec853 insertion-only. C3 [A1] records settlements 1-3, D4, D6, and prints DEFF, n_eff and
MDE80 beside C-M1 (Support (b)).

## Own mutants (sandbox clone E:/TaxoArena_tmp/ready1_mmlu_review/mut at 0086e9e; tests = test_axis_confirm_mmlu + test_fetch_more)

R1 condition_f median -> min: killed (decisive). R2 VERDICT `!= "READY"` -> `startswith("READY")`: killed (decisive).
R3 by-order join cais pos reversed: killed (decisive). R4 drop the <= 1% unmatched clause: killed. R5 vault ignores a
failed synthetic gate: killed (decisive). R6 pseudo-vault built from `guard.open()` (vault leak): killed (decisive).
R7 null permutes leaf globally instead of within L1: killed (decisive). R8 `read_allowed` admits any file: killed
(pytest and census selftest). 8 / 8 killed; sandbox restored (`git status --short` 0 lines).

## Commands (read-only on every object of record)

```
sha256sum E:/benchzoom_demo/mmlu_confirm/{_work/mmlu_axis_seed0.pkl,tree/tree.csv,tree/manifest.json}
git -C benchzoom_build_da3bf22 rev-parse HEAD; status --short | wc -l; hash-object examples/identifiable_map.py
python -I scratchpad/split.py      # own split + near-dup from parquet + npz -> 5,614/8,428/83, shas
python -I scratchpad/repro.py      # repro vs e1d0b00a structure; MMLU config vs manifest; 184/100
python -I -c "<census_instances/instances.json counts>"   # 79 x 14,042, 0 unmatched, 27 by-order, 0 excluded
python -I scratchpad/dup.py        # 0 dup-key groups with differing answers
find <6 roots> \( -iname '*display_predictions*' -o ... \) | wc -l   # 2 (census outputs)
.venv/Scripts/python examples/axis_confirm_mmlu.py synthetic --out E:/TaxoArena_tmp/ready1_mmlu_review/syn; cmp x4 + diff gate.txt
.venv/Scripts/python -m pytest -q (OMP/BLAS 1 thread)    # row 9
python scratchpad/mut.py           # R1-R8
fetch_zoom_data._registration_commit_refusal('f53ec853' | '803c5b04' | '5109ef9c')
```
