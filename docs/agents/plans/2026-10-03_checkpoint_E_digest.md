# Checkpoint E: digest of the 10-hour window (2026-10-02 evening → 2026-10-03)

Zero judge calls. Each result went through READY → run → post-run review → registrar.

## Results recorded (all VALID)
| Test | Verdict | One line |
|---|---|---|
| DEEP-SPLIT-COMPARE | C-AB HELD (thin, W1); C-DB HELD; F-RULE FIRES | The tree's split beats k-means within the anchors by 1.3pp. The gap to class prototypes is depth-2 fit-set membership, not label use below depth 2 (W2). |
| JUDGE-SOLVED-SPLIT | JS1 UNDETERMINED | Reference right: 0.93 judge-solved vs 0.91 unsolved; not shown either way. Convention B reverses the sign. |
| OOS-BASELINES | EQUIVALENT to labelled baselines; S0-BETTER than label-free baselines | Flat k-means cells only, not the tree; caveats at k=1 and K50. |
| GOLD-LEVEL-EMB | F-GL FIRED (PROMPT, EMBEDDER not invariant); QUANT invariant; DIM undetermined | "Coarse structure robust" is not supported. |
| CERT-POSITIVE-CONTROL | PC1 CERTIFIED; F-PC FIRED | The certificate certifies the 14 declared groups at one member root. The sensitivity-limit reading is overturned at root scale only. |
| E1-ROUTE builds | N-raw and N-card VALID | Criteria await the E1 readout. |

## Built and READY, blocked on the author's WAL checkpoint (mmlu_pro_dataset_cache_v2.db-wal, 8,272 B)
- E1 readout: merged, READY bcb7f2f8.
- UNION-AF-ROUTE (RP13): build and reader merged af3def2a.
- FITSET-FAITHFUL stage 0: registered c1ed61d5; it also waits on the author's scope answer.

## Built, not READY
- INTENT-TRANSFER-S1: engine, exporter and configs on branch intent-s1 43bf914e. The readout still needs three definitions; it runs after E1 and RP13.

## Framing consequences (reframing memo plus brackets)
- Change #8 "replace deep splits" withdrawn; #8' "keep depth-2 cells faithful" speculative (FITSET-FAITHFUL).
- Change 7 "certificate as a false-discovery guard" bracketed: the certificate works at root scale; depth-1 sizes are untested.
- Abstention (#6): supported on flat cells only.
- SQ5: name prompt and embedder as the families that move the coarse level.

## Author decisions open
WAL checkpoint · D2 (gates RP19) · D6 / withdrawal of #8 · FITSET-FAITHFUL scope · #6 into FRAMEWORK.md · SLOTSWAP data leg · J-COMPLETE (29 calls).
