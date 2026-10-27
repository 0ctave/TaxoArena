READY-WITH-CONDITIONS: K46-REPOST, tools/analysis/k46_repost.py sha256-lf16 dd8152585fd7f0d7 (blob 8c5ce9db5f7cf39577264e222450a3e1f599eae6, LF of record; k46-repost2 30f86150)

# Launch-gate file for K46-REPOST (C-K7 of docs/reviews/READY_paid_prereqs.md, 89b50493)

Reviewer: adversarial-reviewer, 2026-10-01. The evidence is in docs/reviews/READY_k46_repost2_e1configs.md (delta review of
30f86150). This file is parsed by k46_repost.py's ready_gate: the first verdict line above names the test and the LF sha16.

Scope of the go:
- RP21 G17-CANARY v2 leg (`--leg canary --pass v2-1 / v2-2`): pilot 12 then run, under the registration L22762-L22784 and the
  committed set (300 matches, set hash 10e027fe046e2a07..., order sha 4fa3bc0e23ce2025...), ceiling 1,260.
- RP20 V2-NONE-TEMPLATE (`--leg rp20`, ceiling 7,750) and its ONE leg REF-PAIRED-V2 (`--leg one`, ceiling 3,440; go of record
  plan Amendment 34 "Yes, include it", combined 5,328 matches > 4,000): only AFTER RP21's C1-v2 is read (C-K6, enforced in code).

Conditions binding the run-operator:
- C-K8: before an rp20 / one posting launch, the `C1-v2:` line of the canary outcome of record must read HELD or UNDETERMINED;
  "UNDETERMINED BY VALIDITY" means not read: no rp20 / one posting until the research-lead rules in the record (the code admits it).
- C-K9: RP21 and RP20 post from the same checkout (main, after the merge of 30f86150 by path).
- C-E3-3: RP20 does not post on pass 5's day. Day cap 14,000 calls per posting day; zero-call transport preflight in every dry-run.
- Any change to tools/analysis/k46_repost.py changes its LF sha16 and voids this file (a new delta review is required).

[INSERTED 2026-10-01 by the registrar (G17-CANARY), D2 of docs/reviews/POSTRUN_rp21_v2.md (cb40d39e); insertion only, the first verdict line and everything above untouched; it states substance already verified, it adds no check]
- transport configuration (zero-call): transport_check (b) PASS on the canary v2-1, rp20 and one dry-runs at 30f86150 (docs/reviews/READY_k46_repost2_e1configs.md #9, 80d9bedf); dry-run preflight PASS: both RP21 v2 dry-runs printed TRANSPORT PREFLIGHT: OK (real host, grok-4-1-fast-non-reasoning) (POSTRUN_rp21_v2 D2).
- provider behaviour (pilot): left to each leg's pilot 12 under the truncation guard (refuses above 5% unparsed); RP21 v2: both pilots 24 of 24 usable (POSTRUN_rp21_v2 C0(f)).

[INSERTED 2026-10-02 by the adversarial-reviewer (k46-deff), docs/reviews/READY_k46_deff.md; insertion only, the first verdict line and everything above untouched]
- Analysis-only gate entry: tools/analysis/k46_repost.py sha256-lf16 58f621dc4582616b (blob 4159d62eb62c6705de0132da9f336d9df365dcc0, LF of record; k46-deff e0669e57) is reviewed for `--analyze-canary` / `--analyze-rp20` / `--analyze-one` ONLY (D1 of POSTRUN_rp21_v2: analytic DEFF; deciding SE and intervals byte-identical on RP21 v2). It is NOT a posting go: `--go` stays gated on the first verdict line (dd8152585fd7f0d7). Merge k46-deff by path only after RP20 and the ONE leg have finished posting.

[INSERTED 2026-10-02 by the adversarial-reviewer (k46-analyze-fix), docs/reviews/READY_k46_analyze_fix.md; insertion only, the first verdict line and everything above untouched]
- Analysis-only gate entry: tools/analysis/k46_repost.py sha256-lf16 011682b96d8d419f (blob 74d5fd68de5f46bd3ed3ded26f9c675b56fe32a2, LF of record; sha256-crlf16 c74ce4896bb437df is the worktree's CRLF rendering; k46-analyze-fix 2d9e83e8) is reviewed for `--analyze-canary` / `--analyze-rp20` / `--analyze-one` ONLY (incident aaf12c77: configure_rr() on the --analyze paths; [BODY-RECHECK] failures printed). It supersedes 58f621dc4582616b for analysis. It is NOT a posting go: `--go` stays gated on the first verdict line (dd8152585fd7f0d7).
