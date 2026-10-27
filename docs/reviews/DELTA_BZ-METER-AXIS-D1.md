# DELTA review: BZ-METER-AXIS D1 fix (benchzoom f04f549)

Prior review: `POSTRUN_BZ-METER-AXIS.md` (1260cf3a), D4. Reviewer: adversarial reviewer, 2026-10-20. Zero API calls;
no vault read; the guard was never armed. Delta: `git diff 096d43d..f04f549` = 15 insertions in 2 files
(`examples/meter_test.py` +3, `tests/test_meter_axis.py` +12). LF blobs: meter_test.py `f3a5a3b7`, test `eeaee39c`.
The run of record's `code.script_blob` in granularity_work/meta.json is `f3a5a3b7`, so the fix was in place for that run.

## Verdict

**CORRECT, MERGEABLE.** `--axis vault` with any `--out` that does not resolve to `OUT_AXIS` raises `SystemExit
REFUSED`. It fires right after `parse_args` and `import meter_axis`, which loads no data (module level holds
constants and imports only), and before `axis_main`, the first data load. The insertion sits inside `if a.axis:` and
only the `vault` value reaches it, so the other modes are unchanged.

| # | Claim | Own result | Verdict | Sev |
|---|---|---|---|---|
| 1 | vault refuses another --out | test_vault_refuses_other_out_dir passes; `axis_main` is replaced by an assertion sentinel that is never reached | CONFIRMED | - |
| 2 | fires before any data load | lines 1086-1091 run before `axis_main`; `meter_axis` import has no loader at module level | CONFIRMED | - |
| 3 | no change to other modes | diff confined to the `a.axis == "vault"` condition; test_meter_axis 19/19 pass in the sandbox | CONFIRMED | - |

## Own mutants (sandbox git copy, TMP redirected; control 19/19 pass)

- B1 refusal removed (`if False:`): killed (decisive).
- B2 `!=` changed to `==`: killed (decisive).
- B3 `"vault"` changed to `"work"`: killed (decisive).
- B4 refuse every vault run (`if a.axis == "vault":`): **survived**. No test shows that the registered directory gets
  past the D1 gate. This is non-decisive: it fails closed, and D-2026-10-20-4 forbids a further read.

## Defects

- E1 (LOW): add a positive test, `--axis vault` with no `--out` (or `--out OUT_AXIS`) reaches a stubbed `axis_main`;
  it kills B4.
- E2 (LOW, pre-existing, outside the delta): argparse's default `allow_abbrev=True` means `--ou X` is not seen as
  "given", so `out` silently becomes `OUT_AXIS`. For vault mode this fails safe; in work and synthetic modes it
  redirects to the record directory, where the write-once refusals still apply. Fix: `allow_abbrev=False`.

## Commands

```
git -C benchzoom show f04f549; git rev-parse f04f549:examples/meter_test.py f04f549:tests/test_meter_axis.py
git archive 0aba06e -> scratch sbB; git init; pytest tests/test_meter_axis.py (19 passed)
mutants B1-B4: one-line replacement of the D1 condition; pytest -k "vault_refuses_other_out_dir or vault_refusals_before_any_data"
```
