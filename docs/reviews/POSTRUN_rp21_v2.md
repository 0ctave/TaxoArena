# POSTRUN_rp21_v2: G17-CANARY (RP21), v2 leg, run f8530b54

Reviewer: adversarial-reviewer, 2026-10-01. Zero calls. Registration: prog L22762-L22784 (`## Registered 2026-10-01 (before any
code or call) — G17-CANARY (RP21): ...`), brackets of b3dd18ab (interval form NORMAL, R2-R5, R7). Gate: READY_k46_repost.md
(lf16 dd8152585fd7f0d7), evidence READY_k46_repost2_e1configs.md (80d9bedf).

## Verdict

**VALID.** C0 (a)-(f) PASS, all six re-derived from the caches. **C1-v2 HELD, DESCRIPTIVE-ONLY** (wording W1-W3 below):
d_r = 30/300 = 0.1000, 95% NORMAL [0.0658, 0.1342] (component-clustered bootstrap SE 0.0174), upper bound <= 0.15.
Falsifier not fired. **RP20's order gate (C-K6 / C-K8) may open**: the `C1-v2:` line reads `HELD` (not `UNDETERMINED BY
VALIDITY`); `order_gate` on main prints "RP21's C1-v2 reads HELD: RP20 may post" for `rp20` and `one`. C-K9 holds (RP21 posted
from main, HEAD 2b6591bb). RP20 still not on 2026-10-01 (RP21's day) and not on pass 5's day (C-E3-3).

Data object: the two leg caches, read from the backup copies `experiment_results/_backup/rp21_v2_20261001/`
(k46_repost_canary_v21.db sha256 e24df0c5187e1f64..., v22 f2db9fa04408f65a..., equal to the working copies; 600 rows each, keys =
the 300 set matches x 2 orders, arm C only), the K46 store (sha256 44724d25aa8653b4, unchanged after my reads) and the set file
g17_v2_canary_set.json (300 matches, 300 distinct components, set_hash 10e027fe046e2a07, order 4fa3bc0e23ce2025). Script blob of
record unchanged since the READY: tools/analysis/k46_repost.py blob 8c5ce9db5f7cf395..., sha256-lf16 dd8152585fd7f0d7 (LF, of
record; the main working tree is CRLF, sha256-crlf16 06eccdf43ed00ddb); every cache row carries script_sha16_lf dd8152585fd7f0d7.

## Deciding claims

| # | claim (outcome file / brief) | result | mine | severity |
|---|---|---|---|---|
| 1 | C0(a) set hash / order sha reproduced | CONFIRMED | run_meta set_hash = set file set_hash in both caches; 300 matches / 300 components; draw re-derived independently by 80d9bedf (taken as given) | - |
| 2 | C0(b) store sha equal before/after | CONFIRMED | 44724d25... before (logs) and now (my sha256sum) | - |
| 3 | C0(c) 1,200 of 1,200 bodies byte-identical | CONFIRMED | 1,200/1,200: cache payload_sha256 = stored_payload_sha256 = K46 payload_sha256, zlib-decoded body = K46 decoded body, sha256(body) = payload_sha256 | - |
| 4 | C0(d) every call azure:grok-4-1-fast-non-reasoning | CONFIRMED | provider/response_model 1,200/1,200; finish stop 1,200; max_tokens 8192; temperature "omitted"; 1,200 distinct response_id | LOW (D3) |
| 5 | C0(e) v2-2 within 7,200 s of v2-1 | CONFIRMED | v2-2 started_ts - v2-1 last row = 12.7 s (first v2-2 row 16.4 s); each pass spans ~247 s | - |
| 6 | C0(f) pilots pass the truncation guard | CONFIRMED | 0 unusable in 12 + 12; 0 unusable in all 1,200 rows | - |
| 7 | d_r = 30/300 = 0.1000 | CONFIRMED to the digit | 30/300 (conv A); conv B 30/300 (no unusable rows, A = B) | - |
| 8 | 95% NORMAL [0.0658, 0.1342], SE 0.0174 -> HELD | CONFIRMED (gap 0.0003 on bounds) | analytic iid SE 0.01732 -> [0.0661, 0.1339]; own bootstrap (B 20,000, seed 20261001) SE 0.01726; analyzer SE 0.0174 (seed 42), seeds 43-62 0.0169-0.0179. HELD under every SE | - |
| 9 | brief: "90% NORMAL [0.0713, 0.1287] against the bar" | **REFUTED as the deciding interval** | registration C1-v2 decides on the 95% bounds; the 90% interval is printed but decides nothing | MEDIUM (W1) |
| 10 | DEFF 1.053 "MEASURED", n_eff 284.8, MDE80 0.0488 | **PARTLY** | DEFF = 1.000 BY CONSTRUCTION (one match per component; Kish 1.00). `boot_mean` draws the clustered and iid resamples with the same seed over two different orderings (sorted component keys vs match order), so 1.053 = (0.0174/0.0170)^2 is Monte-Carlo noise between two B = 2,000 streams (sd of a bootstrap SE ratio ~2.2%), not a design effect. n_eff 300; MDE80 = 2.80 x 0.01732 = 0.0485 | LOW (D1) |
| 11 | registered Support: SE 0.01873, MDE80 0.0524 at DEFF 1.169 transported | CONFIRMED (arithmetic) | sqrt(0.1 x 0.9/300) x sqrt(1.169) = 0.01873; x 2.80 = 0.0524 > 0.05 -> HELD DESCRIPTIVE-ONLY at the prediction, as registered | - |
| 12 | calls 1,200 of 1,260 | CONFIRMED | day ledger 24 + 576 + 24 + 576 = 1,200; rows 1,200; counted = invocations of call_judge_full. Hidden HTTP retries excluded by latency: max 5,724 ms < the >= 6 s a 3 s-backoff retry needs | - |
| 13 | C2/C3 descriptive: d_e 32/300 = 0.1067, Delta +0.0067, reversals 1 / 0, TIE 0.1933 / 0.1900 / 0.2167, alarm bar 0.1597 | CONFIRMED (spot, descriptive) | identical counts; alarm bar 0.1601 at the analytic SE 0.0178 vs 0.1597 at the bootstrap SE 0.0177 | LOW (W4) |
| 14 | strata NONE 22/208, ONE 8/92 (7/81 + 1/11), health 11/150, math 19/150 | CONFIRMED (spot; ONE correct/wrong split not re-derived, needs the v0 flag) | NONE 22/208, ONE 8/92, health 11/150, math 19/150 | - |
| 15 | P6 "fingerprint on 1,200 of 1,200 -> HELD" | PARTLY | registered P6 is "1,800 of 1,800" over BOTH legs; the v2 half holds; P6 and P5 stay OPEN until pass 5 | LOW (W3) |

## Scored or descriptive-only HELD (decision)

**DESCRIPTIVE-ONLY HELD.** The registration fixed it before data (Support (f): "HELD is DESCRIPTIVE-ONLY at the prediction
(0.05 < 0.0524 ...)"; (g): "a scoreable HELD at 0.10 would need about 330 matches"). The observed point is the prediction (0.1000),
so the pre-data line applies exactly. The post-run support (DEFF 1.00, MDE80 0.0485 < the 0.05 distance) would make it scoreable,
but that is a post-data re-reading of the Support by 1.5 thousandths; under C-7 it is not promoted. The interval rule is MET (the
HELD is a legitimate verdict of the registered three-way rule, and it is what C-K6 reads); "descriptive-only" binds its standing as
evidence and its ledger chip. READY_k46_repost2_e1configs #13 labelled "MDE80 0.0524 vs bar 0.15 (SCOREABLE)": wrong word for
HELD (it is FAILED that is scoreable); correct by insertion (D4).

## Wording conditions (registrar)

- **W1** Cite the deciding interval as "95% NORMAL [0.0658, 0.1342] (component-clustered bootstrap SE 0.0174; B 2,000, seed 42)";
  the 90% [0.0713, 0.1287] may appear only as "printed beside, decides nothing".
- **W2** Chip / outcome text: "C1-v2 HELD (DESCRIPTIVE-ONLY per the registered Support (f)); d_r(v2) = 30/300 = 0.100". Never
  "scored HELD"; never "floor of record" for d_r (C3: the floor of record is d_e(v2) = 0.1067, not yet live).
- **W3** P1-P4 scored on this leg; P6 "v2 half: 1,200 of 1,200"; P5 and P6 (whole) OPEN until pass 5.
- **W4** Support beside the statistic: "DEFF 1.00 by construction (one match per component); the printed 1.053 is bootstrap
  noise; n_eff 300; MDE80 0.0485". C3 alarm bar 0.1597 with its SE source (bootstrap SE 0.0177); analytic 0.1601 beside.
- **W5** Split word: pool pv2_41dbd3dbcd399df0, "content-closed under CK-CLOSE-v2 with the residual disclosed"; this is a floor
  measurement, not fidelity (registration "WHAT THIS RESULT WILL NOT SHOW").
- **W6** Pin the uncommitted caches in the record: v21 sha256 e24df0c5187e1f64..., v22 f2db9fa04408f65a... (backup on the same
  physical disk).

## Defects

- **D1 LOW** `support_text` reports DEFF = (se/se_iid)^2 where both are bootstrap SEs from different RNG mappings; on a
  one-per-component set it prints noise as "MEASURED". Fix: when k == n print "DEFF 1.00 (one per component)"; else compute se_iid
  analytically (sqrt(p(1-p)/n)) or from the same resample indices. Matters for RP20 (1,258 in 360 components), where the DEFF is
  real and is read against the registered 1.885.
- **D2 LOW** (the brief's LOW item) `transport_check.py --ready docs/reviews/READY_k46_repost.md` -> (c) REFUSED (my re-run: no
  line naming "transport configuration" + "zero-call", none naming "provider behaviour" + "pilot"). Not a condition of record
  (C-K7 required (b) only; (b) PASS x3 at 80d9bedf) and the substance held: both dry-runs print `TRANSPORT PREFLIGHT: OK` (real
  host, grok-4-1-fast-non-reasoning) and both pilots posted 24/24 usable. Does NOT affect validity. But the operator ran the lint,
  got exit 1 and proceeded without a written waiver (rp21_v2_runlog.txt: "exit 1" then "exit 0"). Fix before RP20's --go: the
  reviewer appends two lines to READY_k46_repost.md by insertion (first verdict line untouched; the gate re-reads it tracked and
  clean): "- transport configuration (zero-call): transport_check (b) PASS on rp20 / one dry-runs" and "- provider behaviour
  (pilot): left to each leg's pilot 12", then re-runs (c) to PASS; or the orchestrator records a waiver.
- **D3 LOW** HYGIENE says "the provider fingerprint recorded per call"; the canary verdict table has no system_fingerprint column
  (the K46 store has one); C0(d) reads the provider label + response_model. Disclose in the outcome record; no re-run.
- **D4 LOW** READY_k46_repost2_e1configs.md #13 "(SCOREABLE)" for C1-v2: insertion bracket "HELD is DESCRIPTIVE-ONLY at the
  prediction; FAILED is SCOREABLE (registration Support (f))".
- Carried, unchanged: D-K1 MEDIUM (order_gate admits UNDETERMINED BY VALIDITY) -> C-K8 still binds RP20 / one launches; moot today
  (the line reads HELD).

No own mutants: post-run review, the code blob is unchanged since its READY (0 changed files 30f86150..HEAD), every deciding
number re-derived independently from the caches. Run commit hygiene: 12 files, 0 of them .db / application.yml / .env /
.gitignore (count, `git show f8530b54 --name-only --format= | grep -c`).

## Commands (zero-call; S = session scratchpad)

```
sed -n 22762,22784p docs/judge_v2_program.md ; git show f8530b54 --stat
sha256sum experiment_results/archv2/k46_repost/*.db experiment_results/_backup/rp21_v2_20261001/*.db \
          experiment_results/archv2/pilot_k46/pilot_k46_verdicts_run2.db               (equal pairs; store 44724d25 before/after)
git show HEAD:tools/analysis/k46_repost.py | sha256sum ; git hash-object ... ; sha256sum <working tree>   (dd815258 / 8c5ce9db / 06eccdf4)
git diff --name-only 30f86150 HEAD -- tools/analysis/k46_repost.py tools/analysis/k46_repost_selftest.py | wc -l      (0)
python S/rp21.py   # own read (mode=ro&immutable=1) of set file + K46 schedule/verdict + both backup caches: C0(a)-(f), own
                   # FIRST/SECOND->contestant map and combine (bad > TIE on flip), d_r, conv B, analytic + own bootstrap SE,
                   # d_e, Delta, reversals, TIE shares, strata, MDE
python - (latency_ms max per cache: 5,724 / 5,431 ms; response_id 600 distinct per cache)
python -c "import k46_repost as K; c=K.real_cfg(); K.order_gate(c,'rp20'); K.order_gate(c,'one')"   (tools/analysis; ADMITTED, HELD)
python tools/analysis/transport_check.py --ready docs/reviews/READY_k46_repost.md          (c) REFUSED, rc 1
grep -h "TRANSPORT PREFLIGHT" experiment_results/archv2/k46_repost/rp21_v2-*_dryrun.log  (OK x2, real host)
```
