# AUDIT: results drafts SQ3/SQ5 (5bb6f173) and SQ1/SQ2 (a59b1b65) against the record, 2026-10-04

Zero calls. Read-only. HEAD 0f4a290b, ledger v380. Sources: `docs/agents/results/<ID>.json` (criteria, numbers_of_record,
sentence_of_record, brackets, does_not_show; last bracket wins), POSTRUN W-lines, memo v3 with its brackets,
`docs/reviews/RULING_w0_p2dca_family.md`. 0f4a290b (registrar consistency check, landed during this audit) was diffed: it moves
chips, states and READY pointers only, no number or sentence of record (sentence_of_record_E1: same length, same content).

## Verdict

**NOT CITABLE AS-IS: 4 HIGH, 11 MEDIUM, 8 LOW.** Every printed deciding number in both drafts matches its results JSON
(digit check over ~180 figures: no wrong digit found). The defects are wording against W-lines, [P-FAM] numbers without the
bracket, a misplaced object, and results recorded after each draft was written.

Timing: the SQ3/SQ5 draft (20:44 on 10-03) came AFTER ONLINE-STAGE2 (recorded 20:19) and GEMMA-OWN-BAR (20:22). It includes
both, correctly worded, so the brief's premise is wrong for those two. It came BEFORE CERT-PC-K2-KNOWN (23:54), CELL-FLIPS,
NEARDUP-AUDIT (03:0x on 10-04), CERT-K2-DEFLATED (05:39) and COVERAGE-AUDIT (11:30). The SQ1/SQ2 draft (05:42 on 10-04)
came before COVERAGE-AUDIT only.

## Issue table

| # | Sev | Draft | Line / sentence | Issue | Correct value / wording | Source |
|---|---|---|---|---|---|---|
| 1 | HIGH | SQ3 | L62-63 "They read as 'below one supervised centroid per class'" | Contradicts W-4 and the draft's own quote two lines later: the tree's coarse filing is AT OR ABOVE one supervised centroid per class (0.872 / 0.941 vs 0.867 / 0.855) and below label-conditioned per-class PROTOTYPES. G13's comparator is class-conditional k-means, not one centroid. (Memo v3 L45 and L109 carry the same misreading.) | "They read as 'below label-conditioned per-class prototypes' (T-C1b: at or above one supervised centroid per class, W-4; G13: below class-conditional k-means), not as a method loss" | POSTRUN_intent_s1 W-4; INTENT-TRANSFER-S1 sentence_of_record + chip "TREE >= ONE SUPERVISED CENTROID" |
| 2 | HIGH | SQ3 | L191-192 "(CERT-PC-K2-KNOWN is built, not run)" | SUPERSEDED. It ran (VALID 07721b48), and CERT-K2-DEFLATED ran too (VALID 761e606c) | "k = 2 sensitivity of the plain site null stays UNDETERMINED: CERT-PC-K2-KNOWN G-KS NOT-A-CONTROL 3/3, KK1 / KK2 NO-CONTROL (no chosen pair qualified as a known-strength control); CERT-K2-DEFLATED DF1 ELONGATION-CONFOUNDED, DF2 = axis variance; the deflated null is not a usable certificate for data-driven splits; the plain J site null stays the certificate of record" | CERT-PC-K2-KNOWN, CERT-K2-DEFLATED .json SOR; memo v3 brackets 2026-10-04 |
| 3 | HIGH | SQ1 | L127 MC-LEAF "-0.9 +- 0.3pp", qualifier "reserved side not re-verified" only | The last bracket (2026-09-23) is missing: ROUTER-CLEAN-POLICY C3 re-reads leaf minus domain on the split of record as -0.09pp [-1.09, +0.91] (DESCRIPTIVE; replicate mean -0.78). "Its -0.9 +- 0.3pp (i.i.d.) is not reproduced as a decided result." | add to the qualifier: "i.i.d. SE; not reproduced as a decided result (ROUTER-CLEAN-POLICY C3 -0.09pp [-1.09, +0.91], descriptive)" | MC-LEAF.json bracket 2026-09-23 #2; ROUTER-CLEAN-POLICY C3 |
| 4 | HIGH | SQ2 | L245-246 "Three levers were sized and the arx / iask pair stayed at 0.50" | [P-FAM] numbers without the bracket. FRONTIER (class Z, L316), ORACLE (A, L209) and AGGREGATE (A, L212) are full family members. This settles the draft's own open item 5, and the draft breaks its header rule "No [P-FAM] number is restated as evidence" | keep the refusal without numbers: "The order inside the frontier band is declined by rule (FRONTIER, AGGREGATE, ORACLE; a refusal, RULING §3.2)"; the numbers go in only with the family bracket (author's words) | RULING_w0_p2dca_family.md L151, L254-L255; KNOWLEDGE §1 "History, never evidence" |
| 5 | MED | SQ3 | L118-123 and Table 3.3 (L97-104) | SUPERSEDED in part: the certificate table stops at CERT-PC-K2. Two rows are missing, and so is the "never 'uninformative' / 'insensitive'" line on G12 | add rows: CERT-PC-K2-KNOWN: G-KS NOT-A-CONTROL 3/3 (STRONG full k_d 14, p 0.0498, margin 0.000180 < SD 0.002022); KK1 / KK2 NO-CONTROL; merged-pair null p95 0.081-0.127 (descriptive). CERT-K2-DEFLATED: DF0 VALID-NULL 0/20 (a collapse check); DF1 ELONGATION-CONFOUNDED (pairs and PC1 median-cut controls 5/5); DF2 0/3 (axis variance); P1 0.0555. Add: "G12's 0/60 is never 'uninformative' or 'insensitive'; nothing about it beyond the registered WOULD NOT" | CERT-PC-K2-KNOWN, CERT-K2-DEFLATED numbers_of_record, does_not_show |
| 6 | MED | SQ3 | L93-94 "per-source k-means comparator was filed by true source ... (disclosure D-4, against AF)" | SUPERSEDED in part: COVERAGE-AUDIT now measures member mixing for AF-U against K_0 | add beside D-4: "AF-U and K_0 (mirrored filing) mix members equivalently within +/-0.020: D_X +0.00322, 90% [-0.00017, +0.00690] (5,907 / 5,404; DEFF 0.99); never 'equal'; the nearest-of-all D_X -0.0051 carries the IFEVAL one-cell asymmetry; GPQA n 34" | COVERAGE-AUDIT.json CV1, SOR, does_not_show |
| 7 | MED | SQ1 | L57-58 same D-4 sentence | as #6 (the SQ1 draft predates COVERAGE-AUDIT by 6 h) | as #6 | COVERAGE-AUDIT.json |
| 8 | MED | SQ3 | L186-195 "What is not shown" | SUPERSEDED in part: NEARDUP-AUDIT bears on "reproducible cell addresses" (L26) used for blocking | add: "that the tree is a safe blocking index (NEARDUP-AUDIT ND1 UNDETERMINED, R1-dependent: BLOCK-LOSS 0.071 (5/70) [0.014, 0.129]; primary-leaf-only 0.114 reads LOSES); k-means 0.009 descriptive [AN]" | NEARDUP-AUDIT.json SOR, W-1, W-3 |
| 9 | MED | SQ3 | L147 OOS-BASELINES status "flat [LF] cells" | Label status: OB-a / OB-b read 150 class labels, so they are [LF] vs [LC], a cross-status comparison, and are not marked *cross* | status "[LF] vs [LC], cross (a, b); [LF] vs [LF] (c, d)" | OOS-BASELINES SOR "(a), (b) read 150 class labels, S0 reads none but K" |
| 10 | MED | SQ5 | L211 "Quantisation does not move them at the gold coarse level" | Drops the margin. The record says INVARIANT within +/-0.025 NMI (TOST), and the header bars "same / equal" readings | "Quantisation (Q8_0 vs Q4_K_M) is INVARIANT within +/-0.025 NMI at the gold coarse level (TOST)" | GOLD-LEVEL-EMB GL1-QUANT, SOR |
| 11 | MED | SQ1 | L128 ROUTER-CLEAN-POLICY qualifier "worst-case bound 1.32pp (6.66% of EVAL visible to construction)" | Wrong object. The 1.32pp bounds the union tree's routing HEADLINE (Top-1 81.58% -> 80.26%), not a policy gain. ROUTER-CLEAN-POLICY's own empirical twin bound is the one of record | "id-disjoint only (471 EVAL content twins); twin-removal sensitivity +2.68 to +3.40, all above 0" (the 1.32pp only as "routing-accuracy bound, MC-E2E") | MC-E2E bracket 2026-09-23 (blocker A1); ROUTER-CLEAN-POLICY twin_sensitivity, chip "C1 SURVIVES TWIN REMOVAL" |
| 12 | MED | SQ1 | L133-134 "The record states that the +2.92 / +3.09 'stay id-disjoint-only history, not revised'" | Quotes the CONSEQUENCE clause of V2-DECLARED-CELLS F1, which applies only if C1 is not HELD. F1 did NOT fire | "V2-DECLARED-CELLS is 'a sensitivity and wording conversion, not a replication' (F1 not fired); ROUTER-CLEAN-POLICY stays split-disjoint by id, not by content" | V2-DECLARED-CELLS falsifier text + outcome; ROUTER-CLEAN-POLICY chips |
| 13 | MED | SQ1 | L21 "Unless a row names another pool ... v2 split (draw 5a3e756)"; Table 1.2 L69-70 (SuperGPQA) | Split word (S3): SuperGPQA reads its own split, which is not draw 5a3e756, and no row names it | name it on both SuperGPQA rows: "SuperGPQA split sg893684444c6df3e9 (CK-CLOSE-v1, 0.30 EVAL per field) minus 1,251 MMLU-Pro collisions" | SUPERGPQA-STAGE0b.json run.pool |
| 14 | MED | SQ2 | L266 "read beside a judge retest noise of 5.7%" | 5.7% (DECOMP) is a named family number (RULING §3.1 item 4) and is quoted without the bracket, against the draft's header | quote it as "5.7% [P-FAM]", or use the v2 floor: "RP21 d_r 0.100 [0.0658, 0.1342], DESCRIPTIVE-ONLY" | RULING L86; G17-CANARY d_r_v2 |
| 15 | MED | SQ2 | L165 Claim "Removing the cached reference costs 16pp of convention-A accuracy, mostly as lost decisions" | W6 is missing in the claim: the ONE contrast is a bundle, and attributing it to the reference is a cross-population inference | append: "(a bundle: reference block plus reference sentence vs neither plus N1; attribution to the reference leans on RP20, cross-population)" | POSTRUN_rp20_one W6; V2-NONE-TEMPLATE SOR |
| 16 | LOW | SQ3 | L47 AK1 / AK2 "UNDETERMINED x2" | D-4 bracket: AK1 decides nothing (not like with like); only AK2 decides F-AK | mark AK1 "decides nothing (D-4)" | UNION-AF-ROUTE bracket 2026-10-02 (D-4) |
| 17 | LOW | SQ3 | L26 "It gives reproducible cell addresses" | D6 is the author's wording and is not adopted. G10 is "byte-identical for 7 pairs, never 'deterministic'"; OL2: ids stay stable only with frozen means | "reproducible addresses (G10: 7 pairs byte-identical; T-C7 EQUIVALENT under slot swaps; stable online only with frozen means)" | ARCH-V2-E-T-R2 SOR; ONLINE-REPLAY-LOMO OL2; memo v3 §4 D6 (author's) |
| 18 | LOW | SQ5 | L241-253 E0b k 14 | Omits gemma_raw M1' k 14 WORSE firing on seed 0 only (mean-over-seeds -0.0309 inside spread), which the sq5_reading keeps ("not parity") | add the clause to L252-253 | EMBEDDER-CROSS-FLAT numbers_of_record sq5_reading |
| 19 | LOW | SQ5 | L214 "The separation bar belongs to the embedder" | Claim paragraph without W-2 / W-3 (bar_g may be inflated by the k-way vs min-pair mismatch; nulls at 0.025); memo change 6 says "belong to a cell set's identity" | "under the registered bar rule gemma's bar is stricter (W-2: bar_g may be inflated)" | GEMMA-OWN-BAR W-2, W-3; memo v3 change 6 |
| 20 | LOW | SQ1 | L134-135 "+0.18pp ... agrees with ROUTER-REGRET-MMLU's 'nothing to route'" | Cross-roster (12 / 46 models, gemini dominant, vs 18-model union) and descriptive against id-only; "agrees" invites a joined reading (S4 spirit) | "is, like ROUTER-REGRET-MMLU (different roster, id-only), not separated from zero" | V2-DECLARED-CELLS C1 bracket; ROUTER-REGRET-MMLU |
| 21 | LOW | SQ1 | L125 ROUTER-REGRET-MMLU qualifier | RULING §3.1 item 5: key-only readouts that read anchors also carry "filed by a qwen3 tree" | add "filed by a qwen3 tree" | RULING L87-L90 |
| 22 | LOW | SQ2 | L197 caption "Paired tests on the same bodies" | JS1 is a between-item split (solved vs unsolved) read from K46 at zero calls; it is neither paired nor a same-session post | move JS1 out of the caption's scope, or caption "Judged contrasts" | JUDGE-SOLVED-SPLIT criteria |
| 23 | LOW | SQ2 | L221 "The reference-wrong stratum (38 matches in 11 components) carries no information" | Stronger than the record: W8 says DESCRIPTIVE-ONLY (SE 0.12); the stratum's value +0.0789 is descriptive | "is DESCRIPTIVE-ONLY (38 in 11 components, SE 0.12)" | POSTRUN_rp20_one W8; V2-NONE-TEMPLATE C_ONE |

No banned word is misused in the drafts' own sentences ("equal", "replicates", "as good as", "no worse", "parity", "certified" for
deflated). Each hit is a negation, a verbatim record quote, or a plain-null CERTIFIED (PC1, PS1/PS2). Label status elsewhere is
correct ([AN] B0, [LC] KC / K_0 / prototypes, [LF] AF-U / intent AF), except #9.

## Checks that passed (spot list; deciding numbers recomputed against JSON to the printed digit)

T-C1/T-C7/T-C8/T-C2/T-C9/T-C1b; G11/G13/G14/G12; U1/U2/U3b/AK; C-AB/C-DB/B-gt; PC1/PS1/PS2/PK; FF1/FF2/FI1; OB-a..d (signs
flipped to S0-minus-peer, as declared); OT1; RC1 (+0.00497 -> +0.50pp; 0.00004); OL1/OL2; OS1/OS2; GOLD four families; E0b
k14/k82; E1 0.6813/0.7269; SD1 G1-G3, Gbar, spreads; GEMMA bar_g 0.043748 (1.75x = 0.043748/0.025), 0.42x/1.00x; C1 +2.67
(0.6316-0.6049), BBH 0.728, C2/C3; CF1 7/101, 273 (0.0462), tau 0.5861; SuperGPQA C1/C2, 1,251/26,529; FLAT-GENERALITY x3;
K46 0.8787/0.9391/0.9249/0.2632/0.7512/0.9292, 69.3% (1,846/2,664 = 0.6929); RP20 C1/C-ONE/C2; JS1/JS2; G17 d_r/d_e/alarm.

## Notes for the orchestrator (outside the two drafts)

- Memo v3 L45 and L109 carry the W-4 misreading of #1 (and D6 bullet 2 says "does not reach one supervised centroid").
  A registrar bracket is owed so the misreading does not reach the methods draft or report text.
- The untracked `docs/drafts/2026-10-04_methods_limitations.md` repeats #4 (L473, L486: frontier numbers) and #19 (L260).

## Commands

```
# per-ID dump of criteria / numbers_of_record / SOR / brackets / does_not_show (read-only)
PYTHONIOENCODING=utf-8 python scratch/dump.py <ID ...>      # 36 IDs, docs/agents/results/<ID>.json
git log --format='%h %ci %s' -- docs/drafts/                 # 5bb6f173 10-03 20:44; a59b1b65 10-04 05:42
git log -1 --format='%h %ci' -- docs/agents/results/<ID>.json  # recording times (ONLINE-STAGE2 f27d758e 20:19; GEMMA 61c5a7c2 20:22; ...)
git show 0f4a290b --format= -- docs/agents/results/*.json | grep '^[+-]'   # chips/state only; E1 SOR difflib: equal
sed -n 64,95p docs/reviews/POSTRUN_intent_s1.md              # W-4 verbatim (#1)
sed -n 250,257p docs/reviews/RULING_w0_p2dca_family.md       # class A: L209 ORACLE, L212 AGGREGATE; class Z: L316 FRONTIER, L207 DECOMP (#4, #14)
sed -n 80,90p docs/reviews/RULING_w0_p2dca_family.md         # "the 5.7% (DECOMP) ... retest floors" are family numbers
sed -n 64,70p docs/reviews/POSTRUN_cert_pc_k2.md; sed -n 75,80p docs/reviews/POSTRUN_rp20_one.md   # W-2; W6-W8
grep -n "not revised" docs/agents/results/V2-DECLARED-CELLS.json   # F1 consequence clause (#12)
grep -n -i -E "equal|replicat|as good as|no worse|certif|parity|..." docs/drafts/2026-10-0{3,4}_results_*.md   # banned-word scan, all hits read
```
