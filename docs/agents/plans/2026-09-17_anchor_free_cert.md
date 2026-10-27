# ANCHOR-FREE-CERT plan (research-lead, 2026-09-17)

Question: maximise the number of certified split sites of the anchor-free tree (af_s42: z 2.0, mcs 55, 256-dim slice, bar 0.025; 81 leaves; 16 of 69 certified at the 300-rep site null; anchored control 5 of 65). Zero judge calls.

## 1. Objective and guardrails
Certified sites as a COUNT and a SHARE of accepted split sites, at the registered null (anisotropy-preserving site null, 300 reps, certified = observed separation >= the site's unconditional p95), computed on the ARM'S OWN geometry. Guardrails, against the record's tree as control: G1 held-out purity >= 0.685 (record 0.715 - 3pp); G2 key-only leaf LOO Brier improvement >= +12.19 / 1000 (record +13.19 - 1); G3 leaves in [60, 100], median held-out top-1 support per leaf >= 30, >= 15 leaves at >= 50 questions.
Why the count alone is gameable: more sites at equal quality raise it and lower the share (MCS: 16/69 -> 18/94 -> 22/122); the null moves with the geometry (an all-but-top arm is scored against a deflated null); a wider slice tightens the isotropic null 1.7x per doubling. Why the share alone is gameable: pruning at the first uncertified site gives 100% by construction; a higher bar removes uncertified sites without adding certified ones.
Structural fact from the CSV: certified sites have median n 621, uncertified 259; the site p95 rises from ~0.028 at n ~4,500 to 0.05-0.09 below n ~400 while observed separations sit at 0.03-0.05. Only the null's width at fixed n (slice width, all-but-top) changes that; every other lever reshuffles which sites exist.

## 2. Levers
L0 certify by pruning (zero build): view A = maximal all-certified prefix (11 sites, 19 leaves, 100%); view B = every certified site + bridging uncertified ancestors (24 sites, 16 certified, 34 leaves). Predicted purity 0.60-0.65 / 0.66-0.70; key-only +7-9 / +10-12; support median ~180 / ~100: G2 and G3 fail; the only objects with measurable per-cell profiles.
L1 slice 512 at bar 0.025 (D1 d512 13/54, 13/57): predicted 22-27 of 56-66 (35-42%), leaves 68-78, G1-G3 hold. Confound: the flat bar is 6.2x the 512 iso floor vs 3.6x at 256.
L2 slice 512 bar-equalised 0.0145 (D2 rule 0.025 x 0.0040/0.0069): predicted 19-24 of 70-80 (26-31%); the width-at-equal-effective-bar control.
L3 slice 1024: TURNED in D3; not run.
L4 all-but-top-1: predicted 18-24 of 45-60; root no longer splits on the quantitative/discursive axis; purity -1 to -3pp; key-only -0.5 to -1.5 (G2 borderline).
L5 all-but-top-2: predicted 22-30 of 35-45 (55-70%); purity -2 to -4pp; key-only -1.5 to -2.5 -> G2 fails; cross-null (dropTop 0) predicted 14-20.
L6 bar 0.030: predicted 14-16 of 52-60; the bar cannot raise the count. Bar 0.035: G3 fails. Lower bars add only uncertified sites.
L7 max depth: inert (mcs binds first). L8 maxK: +0-2 uncertified sites. L9 mcs: done. L10 z: done (stage-2 knob). L11 data: ANCHOR-FREE-FULL, structural evidence only.

## 3. Ordered sweep
0 PRUNE (zero build) -> 1 af_d512 -> 2 af_abt1 (+ cross-null) -> 3 af_abt2 (+ cross-null) -> 4 af_bareq512 (only if arm 1 > 18) -> 5 af_bar030 -> 6 af_abt2d512 (only if arms 1 and 3 both > 16). Each: seed 42, label-free, anchorFree, own outputDir and ratings db, site null on the arm's geometry (-DsliceDim / -DdropTop must equal the build's [SLICE] line), readout with anchor_free_readout.py against af/seed_42 with --control-site-null site_null_af_s42.csv. ~4 h serialised.

## 4. Stopping rule
Stop when (i) an arm holds G1-G3 with count >= 22 and its confound control is within 3 sites: register stage 2 (winner + z 1.5; winner on the full corpus as structural evidence); or (ii) arms 1-3 have run and none exceeds 18 under G1-G3: skip 4-6 and close the line as "certification is bounded by site size, not by the knobs". Never a seventh knob without a new registration.

## 5. Expected synthesis
Certification is a function of site size under a null that widens as n falls; the levers that move the count are those that move the null at fixed n (width; all-but-top, bought with 1.5-2.5 / 1000 of key information and a deflated null); the bar, depth, k range and cell size only reshuffle sites; pruning maximises the share at 11 sites and gives the only measurable per-cell profiles at a purity and information cost. The honest maximum under the guardrails is expected at 512 dims, 20-27 certified (30-42%), reportable as "a certified trunk plus a functional fringe", not as a board, a routing gain or a tree-robust cell set.

## Author-side decisions taken by the orchestrator on 2026-09-17 (per the record's precedent)
(a) guardrails as above; (b) the bar-equalised count is "the" width number (D2's choice), the flat-bar count is reported beside it; (c) both cross-nulls run (zero calls); (d) no promotion inside this sweep; (e) the ANCHOR-FREE-FULL outcome is recorded before the CERT outcome.

## Delegation
tree-construction-specialist builds and reads each arm; adversarial-reviewer recomputes counts from the CSVs, checks the null geometry equals the build's, diffs the configs (one knob), confirms no DB of record changed; registrar records the outcome and the ledger row.
