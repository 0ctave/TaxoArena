# POSTRUN_rp20_one: V2-NONE-TEMPLATE (RP20) and its ONE leg REF-PAIRED-V2, analysis 1d720062

Reviewer: adversarial-reviewer, 2026-10-02. Zero calls. Registration: prog L22786-L22810 (`## Registered 2026-10-01 (before any
code or call) — V2-NONE-TEMPLATE (RP20), with its ONE leg REF-PAIRED-V2: ...`) with the b3dd18ab brackets (NORMAL form decides C1
and C-ONE) and plan Amendment 34. Posting a501cdfe; void analysis aaf12c77 / 74683c20 / 11de1b45; fix READY_k46_analyze_fix eb3df72a.
Data object: the backup caches `experiment_results/_backup/rp20_one_20261002/` (k46_repost_rp20.db sha256 c836470213c40d5f, 7,384
rows; k46_repost_one.db 7f5d599c0c6f6d29, 3,272 rows; equal to the working copies), K46 store 44724d25aa8653b4 (unchanged after my
reads), RP21 canary caches v21/v22 (300 C rows each). Script of record: tools/analysis/k46_repost.py blob:74d5fd68de5f46bd (LF,
`git rev-parse HEAD:<path>`), sha256-lf16 011682b96d8d419f = the outcome header; working tree CRLF, sha256-crlf16 c74ce4896bb437df.

## Verdict

- **RP20 (V2-NONE-TEMPLATE): VALID.** C0 (a)-(f) PASS, re-derived. **C1 EQUIVALENT** (Delta_A +0.0143, 90% NORMAL [+0.0006,
  +0.0280], 1,258 key-decidable in 360 components, inside +-0.040). C2 "the sentence changes verdicts" is printed per the registered
  rule but is DESCRIPTIVE and margin-thin (W3). P5 FAILED is an unreachable prediction (D2). Conditions W1-W4.
- **ONE leg (REF-PAIRED-V2): VALID.** C0 PASS. **C-ONE LOSS** (Delta1_A -0.1599, 95% NORMAL [-0.2095, -0.1103], 544 in 160).
  P1, P2 FAILED; falsifier NOT FIRED (correct: it fires only on UNDETERMINED or GAIN). Conditions W5-W8.

## Deciding claims

| # | claim | result | mine | sev |
|---|---|---|---|---|
| 1 | C0(a) store sha equal before/after | CONFIRMED | 44724d25... now; outcome written only if store_after passes | - |
| 2 | C0(b) NONE 1,846 sched, kd 1,258 / 360; ONE 818, kd 544 / 160 | CONFIRMED | same (keys via K46-KEY-READ's sealed read, the record's key rule; all else my code) | - |
| 3 | C0(c) C 3,692/3,692, C1 1,636/1,636 byte-identical | CONFIRMED | cache payload_sha256 = stored_payload_sha256 = the store's verdict payload_sha256 on every C/C1 row; sha256(zlib body) = payload_sha256 on 7,384/7,384 and 3,272/3,272 | - |
| 4 | C0(d) T/T1 differ only in the swap / stripped reference | CONFIRMED | own JSON check vs the cached C body: system = C.replace(REF_SENTENCE, NOREF_SENTENCE) with exactly 1 occurrence, user identical (RP20) or C minus one contiguous block (ONE), other keys equal: 3,692/0 bad, 1,636/0 bad | - |
| 5 | C0(e) fingerprint 7,384 / 3,272 | CONFIRMED | provider azure:grok-4-1-fast-non-reasoning on all; finish stop on all; 0 INVALID / NON_TERMINATED / CONTENT_FILTER | - |
| 6 | C0(f) pilot guard 0 of 24 | CONFIRMED (vacuous-safe) | no unusable row in either cache at all, so the guard cannot have hidden one | - |
| 7 | Calls 7,384 / 3,272 | CONFIRMED | caches 7,384 / 3,272 = registered; day_calls_2026-10-02.json: V2-NONE-TEMPLATE 7,384 + REF-PAIRED-V2 3,272 = 10,656 (4 rows) <= 14,000; all created_at 2026-10-02 | - |
| 8 | RP20 C1 Delta_A +0.0143 (0.7719 - 0.7576) | CONFIRMED to the digit | +0.0143; discordant 61 (T right) vs 43 (C right), p_disc 0.0827 | - |
| 9 | RP20 90% NORMAL [+0.0006, +0.0280], SE 0.0083 | CONFIRMED (to rounding) | SE_lin 0.0085, own bootstrap (B 4,000, seed 20261002) 0.0087 -> 90% [+0.0001, +0.0286]; UB <= 0.0288 under every SE seen (seed 42 = 0.0083 is the minimum of the 21 seeds) | - |
| 10 | EQUIVALENT (not "with a detectable shift") | CONFIRMED | 95% LB -0.0020 (mine -0.0024 / -0.0027): includes 0 under every SE | - |
| 11 | DEFF 1.114 analytic, n_eff 1,129.6, MDE80 0.0233 | CONFIRMED | 1.114, Kish 4.968, n_eff 1,129.6; registered 1.885 / SE 0.01224 (re-derived) was conservative | - |
| 12 | Conv B Delta_B +0.0000 on 962 | CONFIRMED | +0.0000 / 962 | - |
| 13 | C2 d(T,C) 257/1846 = 0.1392; d(C,K46) 256 = 0.1387; reversals 1 | CONFIRMED | same; SE 0.0091 | - |
| 14 | "THE SENTENCE CHANGES VERDICTS": d - d_r = 0.1392 - 0.1000 = +0.0392, SE 0.0197, LB +0.0007 | CONFIRMED as registered, FRAGILE | d_r 30/300 = 0.1000 (POSTRUN_rp21_v2); my LB +0.0007..+0.0016 with the mixed floor; on the NONE-only floor (208 of the 300, d_r 0.1058, SE 0.0213) LB **-0.0120** | MEDIUM (W3) |
| 15 | P5 FAILED, max 0.119 over 37 | CONFIRMED | 0.1194 Mistral-7B-Instruct-v0.2 (n 67); 19 of 37 > 3pp. Null (within-match T/C sign flip, 2,000 reps): P(all <= 3pp) = 0.0000, max median 0.088, p95 0.123 | MEDIUM (D2) |
| 16 | P1-P4, P6 HELD | CONFIRMED | +0.0143; +0.0087; 0.1392 / +0.0392; 0.1387; 0 unusable | - |
| 17 | ONE C1 Delta1_A -0.1599 (0.7169 - 0.8768) | CONFIRMED to the digit | -0.1599; discordant 10 (T1 right) vs 97 (C1 right) | - |
| 18 | ONE 95% NORMAL [-0.2095, -0.1103], SE 0.0253 -> LOSS | CONFIRMED | own bootstrap SE 0.0253 -> [-0.2095, -0.1103]; SE_lin 0.0251. Still LOSS at the rho=1 bound (SE ~0.039, UB ~-0.083) | - |
| 19 | ONE DEFF 2.007, n_eff 271.0, MDE80 0.0708 | CONFIRMED | 2.007, Kish 4.934 | - |
| 20 | P1 FAILED (-16.0 < -15), P2 FAILED (+0.0789, n 38) | CONFIRMED | ref-wrong n 38 in 11 components, SE 0.118: P2 carries no information | LOW |
| 21 | No FALSIFIER line in rp20 file | NOT A DEFECT of substance | registered FALSIFIER paragraph has an EQUIVALENT branch; the file prints it verbatim ("C1 EQUIVALENT: reuse is admissible ..."); the token "FALSIFIER" is absent only on that branch (code L1628-L1631, blob 74d5fd68) | LOW (D1) |
| 22 | Disclosure: C1 values seen in the void files, reproduced to the digit | CONFIRMED | `diff` void vs valid: 20 changed lines (rp20), 12 (one), all header sha / C0(d) / C1 word / P-words / falsifier; every number line byte-identical | - |

## What the results mean (plain words)

- **RP20.** Swapping the false "the question carries a reference solution" sentence for PAIR-NOREF's no-reference instruction moves
  key accuracy by +1.4pp, inside +-4pp. On the 1,258 key-decidable matches the swap produced **zero** right<->wrong reversals: every
  change is TIE<->decisive (C->T: R->TIE 43, TIE->R 61, TIE->W 13, W->TIE 23). The sentence reshuffles about 14% of verdicts
  (d 0.139), but a byte-identical re-post against K46 reshuffles as many (d(C,K46) 0.139), and the within-session floor is 0.100.
  So "changes verdicts" means at most about 4pp of extra churn, all through ties, with no net accuracy effect.
- **ONE leg.** With the cached grok-reasoning reference in the prompt (C1), the judge picks the key-correct contestant on 87.7% of
  the 544 matches. With the reference removed and the no-reference instruction instead (T1), it does so on 71.7%: **16 points
  fewer correct picks.** Most of the drop is not wrong picks but lost decisions: of the 97 matches right with the reference and
  not right without it, 82 became TIE (the two presentation orders disagree: T1 votes FIRST 865 vs SECOND 659, C1 754 vs 743) and
  15 became wrong. On matches decisive in both arms (411), accuracy falls only 2.9pp (convention B). The reference was right on 506
  of 544 (93%); there the loss is 17.8pp. Read: a mostly-correct reference keeps this judge consistent across orderings and so
  decisive; without it the judge leans to the first-shown answer and its verdicts cancel to TIE.

## Wording conditions (registrar)

- **W1** RP20: "C1 EQUIVALENT: Delta_A +0.0143, 90% NORMAL [+0.0006, +0.0280] (component-clustered bootstrap SE 0.0083, B 2,000,
  seed 42), inside +-4pp; 1,258 key-decidable NONE matches in 360 CK-CLOSE components; DEFF 1.114 analytic, n_eff 1,130, MDE80
  0.0233". The disclosure of record is the registered one: "a false reference sentence, key accuracy equivalent within +-4pp (RP20)".
- **W2** Never "the N1 template improves accuracy" or "the 90% CI excludes 0": its LB sign depends on the bootstrap seed
  (+0.0006 at SE 0.0083, about -0.0002 at the 0.0088 of other seeds); the 95% includes 0.
- **W3** The C2 line is DESCRIPTIVE and must be quoted as "d(T,C) 0.139 exceeds RP21's mixed 300-match floor d_r 0.100 by
  +0.039 (95% LB +0.0007, between-sample)"; add "all changes are TIE<->decisive; zero key reversals; against a NONE-only floor
  (n 208) the excess is not shown (LB -0.012)". Never "the sentence changes verdicts" alone, and never beside EQUIVALENT as if it
  qualified the accuracy result.
- **W4** P5: "FAILED; unreachable at these per-contestant n (sign-flip null P(all <= 3pp) = 0; observed max 0.119 vs null p95 0.123)".
  Not evidence of contestant-specific leakage.
- **W5** ONE: cite the deciding 95% NORMAL [-0.2095, -0.1103] (the [-0.2015, -0.1183] of the brief is the 90%, printed beside).
- **W6** ONE: the contrast is a bundle: "the reference block plus the reference sentence vs neither plus N1". RP20 (EQUIVALENT on
  NONE) supports attributing it to the reference, but that is a cross-population inference: say so.
- **W7** ONE: always beside the 16pp: "mostly lost decisions (82 of 97 right->TIE); conv B -2.9pp on 411; reference correct on 93%".
  It is the content-closed v2 value of THIS cached reference, not the [P-FAM] +12.6pp replicated (do not cite them as agreeing).
- **W8** P1 FAILED in the stronger direction (-16.0 outside [-15, -5]); P2 FAILED is DESCRIPTIVE-ONLY (38 in 11 components, SE 0.12).

## Defects

- **D1 LOW** (code L1628-L1631, blob 74d5fd68) The EQUIVALENT branch prints no "FALSIFIER:" token, unlike the other three branches. Fix (record
  only, no re-run; outcome files are write-once): the registrar writes "FALSIFIER: NOT FIRED (C1 EQUIVALENT; the EQUIVALENT
  branch's consequence applies)" in the outcome section; future builds prefix the line.
- **D2 MEDIUM** (registration P5) The prediction "every contestant with >= 40 kd rows moves <= 3pp" was impossible at n ~50-90 per
  contestant (per-contestant SE ~0.035). A prediction unreachable at the planned n should have been DESCRIPTIVE-ONLY in Support;
  record it as such (W4). Registrar note for future drafts: compute the multiplicity null for any "every unit" prediction.
- **D3 LOW** The C2 floor is a mixed NONE/ONE set (208/92) while d(T,C) is NONE-only; registered as such, so not a deviation. The
  NONE-only floor reverses the reading (W3). Future registrations: floor on the same class as the statistic.

## Commands (all read-only; caches opened `mode=ro&immutable=1`)

```
sha256sum experiment_results/_backup/rp20_one_20261002/*.db experiment_results/archv2/k46_repost/k46_repost_{rp20,one}.db \
          experiment_results/archv2/pilot_k46/pilot_k46_verdicts_run2.db          # c8364702.. / 7f5d599c.. equal; store 44724d25..
python <scratch>/pr20/rc.py   # own store read, FIRST/SECOND->A/B map, combine (bad > TIE on flip), Delta_A, conv B, analytic DEFF/
                              # SE_lin, own cluster bootstrap B 4000 seed 20261002, d(T,C), d(C,K46), TIE share, P5, strata, RP21 floor;
                              # keys only via k46_repost.read_keys (K46-KEY-READ's sealed eval-view read)
python <scratch>/pr20/rc2.py  # own C0(d) JSON body check, payload==stored per arm, created_at days, vote counts, C->T transitions,
                              # P5 sign-flip null (2,000 reps), RP21 floor by class (NONE 208 d_r 0.1058; ONE 92 0.0870)
python -c "...sha256(zlib.decompress(body_zlib)) == payload_sha256..."         # 7384/7384, 3272/3272
python -c "...store verdict payload_sha256 == cache stored_payload_sha256..."   # 7384/7384, 3272/3272; C 3692/3692, C1 1636/1636
python -c "...sum day_calls_2026-10-02.json by test..."                         # 7384 + 3272 = 10656, 4 rows
diff incident_c0d_20261002/rp20_outcome_VOID_c0d.txt rp20_outcome.txt | grep -c '^[<>]'   # 20 (no number line); one: 12
git rev-parse HEAD:tools/analysis/k46_repost.py; git ls-files --eol ...         # blob 74d5fd68.., i/lf w/crlf
```
Own mutants: none (post-run review of an unchanged, reviewed script; the deciding numbers were recomputed by independent code
instead). Not re-derived (taken from eb3df72a / POSTRUN_rp21_v2 cb40d39e): the fix diff's inertness, the key rule, d_r = 30/300.
