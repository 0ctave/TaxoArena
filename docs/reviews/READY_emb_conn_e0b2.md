# READY review: emb-conn e7b0e04 (EMB-CONN) and emb-e0b2 2232f25 (E0b after READY_emb_e0b cd85961)

Adversarial reviewer, 2026-09-29. Zero calls, no real embed, no real-data run: every probe on the scripts' stub Ollama / stub
arms, `TAXOARENA_DATA_ROOT` = an empty scratch dir (`ls -A | wc -l` = 0 after), `OLLAMA_HOST=http://127.0.0.1:9` for every run
(no live server reachable). Reads of record: sha256 of the two source DBs and the DIR copy, row count of the W2 partial
(`mode=ro`). Delta review: emb-conn = `git diff 2332d29..e7b0e04` (1 file, +232/-10); emb-e0b2 = `git diff 2036725..2232f25`
(2 files, +486/-57; 2232f25 contains main 2036725 and e7b0e04). What READY_emb_e0b CONFIRMED on untouched code is cited, not re-derived.

## VERDICT

| object | verdict |
|---|---|
| e7b0e04 (embedder_arms 31a8378f) | MERGEABLE, but merge it only WITH 2232f25: alone on main it breaks E0b's IMPORT_PINS (main's cross_flat pins c8940349; refuses, fail-closed) |
| 2232f25 (embedder_arms 0546800f, embedder_cross_flat 27d95dc8) | MERGEABLE by path (2 files; hygiene grep = 0) |
| `--embed-card gemma_card` / `--embed-card nomic_card` `--target-dir experiment_results/embedder_cross --go` | READY-WITH-CONDITIONS W-1..W-5 (READY_emb_target2, carried) + WC-1..WC-3 below; one write at a time |
| nomic_raw copy (`--embed-missing nomic_raw --expect-missing 0 --target-dir ... --go`) | READY-WITH-CONDITIONS (same; posts only the 20 parity texts) |
| E0b `--run` (cpu / embed) once the registrar's pins are in | READY-WITH-CONDITIONS: C-E0B2-1 (registrar's D2 bracket, not yet in the programme) and C-E0B2-3 (F1 reading) are PRE-RUN; C-E0B2-2 before the outcome is read |

## PINS (LF of record; `git rev-parse <c>:<f>` = `git hash-object` on the clean worktree)

| file @ commit | blob | sha256-lf16 | sha256-crlf16 |
|---|---|---|---|
| embedder_arms.py @ e7b0e04 | 31a8378fc8ebba9ee448ffcc72e1f00a94578bce | f4a8390dc4083da9 | 3a7a109982e8ec44 |
| embedder_arms.py @ 2232f25 | 0546800f76437a537bff45e5d9590240bec87fae | 4bfd77986e4bfb92 (= cross_flat IMPORT_PINS) | 4dfc8dd59490dd15 |
| embedder_cross_flat.py @ 2232f25 | 27d95dc85232f0cd6b96c4f3c6056bcc0c0fb1b1 | 16fa66c89b9d44fa | 167be87317a41c10 |
| flat_mix_mmlu.py @ 2232f25 | 555ae3ac (unchanged, = IMPORT_PINS) | b80cec50c2eef49d | - |

Both worktrees `git status --porcelain | wc -l` = 0 before and after. Sources unchanged since the run log: gemma 3e9ce57772160749,
nomic 53d1540a811e819f, DIR gemma_raw copy 28f2e3a41e77312f; no -wal/-journal beside the sources (count 0). DIR holds 3 entries, 0
card files (the W2 partial is in incident_w2/).

## PER-CLAIM TABLE (deciding claims)

| # | claim | my result | status | sev |
|---|---|---|---|---|
| 1 | Retry never re-sends after a partial WRITE | the DB insert happens only after `ollama_embed` returns a 200 whose count equals the batch; commit per whole batch; a mid-batch refusal rolls the batch back (own probe: dim mismatch at item 6 of batch 2 -> 32 rows, 2 calls). A re-POST after a partial SEND or a lost response is a re-embed of the same inputs (stateless, nothing stored client-side). W2 partial (old code): 4,064 rows = 127 x 32 whole batches | CONFIRMED | - |
| 2 | No retry on a count or dimension mismatch | count check sits after the retry loop -> refuse, 1 POST (EA-CONN, log +1); dimension check is in write_vectors, outside the retry (own probe: 2 calls, refused) | CONFIRMED | - |
| 3 | Retry only on transient connection errors, bounded 220 s | OSError / HTTPException, or HTTP 400/500/502/503 whose body names a socket failure; 6 attempts; 2+8+30+60+120 = 220 s. But the 220 s is asserted only against itself (`slept == list(RETRY_BACKOFF_S)`): own OMC2 (2,8,1,1,1) SURVIVED | CONFIRMED in code; tail untested | LOW |
| 4 | Persistent keep-alive connection | EA-CONN: 4 batches over 1 stub connection; drop -> reset, reopened, client count = server count; builder mutant "new connection per request" KILLED | CONFIRMED | - |
| 5 | OLLAMA_HOST=0.0.0.0 normalised (incident W1) | own probe: `OLLAMA_HOST=0.0.0.0` -> `http://127.0.0.1:11434/api/embed`; 10 bind forms in EA-CONN | CONFIRMED | - |
| 6 | "Most TIME_WAIT sockets are Ollama's own server->runner dials" | client opened <= 1 connection per batch under urllib: about 110 (W1) + 128 (W2) + 67 (probe) + 32 singles, about 340 against 14,922 TIME_WAIT = about 2%; the 400 body is Ollama dialling its runner's /tokenize. Keep-alive removes about 2% of the load | CONFIRMED (arithmetic from the run log) | - |
| 7 | Retry "rides the exhaustion out" | plausible, not proven: W2 ran about 3 batches/s (server log 15:43:00-27) = about 100 inputs/s; ~1-3 server dials per input vs 16,384 ports / TIME_WAIT. TcpTimedWaitDelay is NOT set in the registry (reg query: key absent) so the OS default holds (120 s per the builder, 240 s on older docs: UNDETERMINED). Sockets expire oldest-first, so the first ports return about TIME_WAIT - 80 s after exhaustion: 40 s (120) or 160 s (240), both inside the 220 s. A card write (11,687 texts) exhausts the table about 2-3 times; during each window EVERY process on the machine fails to connect | PARTLY | MEDIUM (WC-1) |
| 8 | C-E0B-1 D2 | code: M1' in every output, CSV header, M1P_NOTE, FLAT values NOMINAL. Registrar bracket: `grep -c "M1'" docs/judge_v2_program.md` = 0, not recorded yet | MET in code; bracket OWED | HIGH (pre-run) |
| 9 | C-E0B-2 support tag vs the MEASURED bar | printed; (f) verbatim + NOMINAL + re-derived. But (a) the tag's bar = max(REGISTERED MDE 0.0186, spread), not the realised MDE80 the line prints; (b) own OMX1 (tag bar drops the spread) SURVIVED: the stub's qwen3 spread is 0, so the spread leg of the tag is untested. P1's tag (prior 0.020 vs bar >= 0.0186) is exactly where this decides | PARTLY | MEDIUM |
| 10 | C-E0B-3 OM1 / OM2 / OM8 killed | builder mutants 35/35 KILLED (reproduced); my control OMX0 (= OM1) KILLED under my harness | MET | - |
| 11 | C-E0B-4 preflight + floor before fits | dry-run REFUSES when /api/tags does not answer, before any arm read; floor fault refuses before FITTED, nothing written. Own OMX2 (listing without qwen3 accepted) SURVIVED: not decisive (the floor POST of an unlisted model gets a non-transient 404 -> refused before any fit) | MET | LOW |
| 12 | C-E0B-5 pins right after the pool line | E0-REFUSE: no "ARM qwen3_raw", no "READ SET" before the refusal. Own OMX3 (early_pins skips the cards) SURVIVED: not decisive (load_arm re-checks each pin before any fit) | MET | LOW |
| 13 | C-E0B-6 realised SE / MDE80 per line | (hi - lo) / 3.92 and 2.8 x SE printed on every WORSE line | MET | - |
| 14 | C-E0B-7 digest at the --go | provenance `model_digest` from /api/tags (stub test + 2 mutants KILLED); UNAVAILABLE is recorded, not refused; gemma_raw's copy has none (read: None) -> prints NOT RECORDED | MET for new writes | LOW (WC-3) |
| 15 | Selftests / mutants | emb-conn: selftest 94 PASSED, mutants 69/69; e0b2: EA selftest 95, mutants 71/71; E0b selftest 49, mutants 35/35; `grep -c SURVIVED` = 0 in all five outputs | CONFIRMED | - |
| 16 | D8: M2 WORSE lines DESCRIPTIVE-ONLY -> F1 unscoreable? | see ruling below | PARTLY | HIGH (pre-run, C-E0B2-3) |

## D8 RULING (F1)

The registration itself already says (Support (f), L21725) "every cross-arm contrast DESCRIPTIVE-ONLY", and it registers no prior
effect for any M2 contrast, so no power against a stated effect exists for F1's inputs; D8 makes this visible, it does not create it.
It does NOT make F1 unscoreable as registered: F1 is an EVENT ("WORSE beyond spread" = point below -spread AND the 95% CI wholly
below 0, for both nomic_raw and gemma_raw at k 14 on M2). A FIRING is a registered two-leg test outcome and needs no power claim
(it may overstate magnitude, winner's curse). A NON-FIRING is not evidence for "the method's": with no support computed it reads
"F1 did not fire; not shown", never "falsifier survived". Today the script prints "FALSIFIER F1 does not fire" with no qualifier while
its input lines are tagged DESCRIPTIVE-ONLY (inconsistent labels on one path). P5 (the prior that F1 fires, 0.35) stays scoreable either way.

## DEFECTS / CONDITIONS

- C-E0B2-1 (HIGH, before --run): the registrar records the orchestrator's D2 ruling (M1' = majority from the 8,125; FLAT's 0.0305 /
  0.00663 / 0.0186 NOMINAL) in the programme, by insertion. The code side is done.
- C-E0B2-3 (HIGH, before --run): the registrar brackets the F1 reading above; the engine-coder adds to the non-firing F1 line
  "(not shown; no support computed for M2 contrasts, registration (f): cross-arm DESCRIPTIVE-ONLY; not evidence for 'the method's')"
  and a unit check on it. Small delta, pin re-check only.
- C-E0B2-2 (MEDIUM, before the outcome is read): use bar = max(realised MDE80, registered MDE, spread_qwen3) in support_tag (or print
  both tags), and add a stub where qwen3's V spread exceeds the MDE so OMX1 dies. The registrar states which P1 label governs if the
  registered (f) (DESCRIPTIVE-ONLY) and the re-derived one (possibly SCOREABLE on the measured spread) disagree; decide it pre-data.
- WC-1 (MEDIUM, each write): pacing in code is not needed for correctness (bounded whole-batch retry, fail-closed), but the exhaustion
  is machine-wide. Either add inter-batch pacing (a printed PACE_S, e.g. 1.0 s after each batch of 32: about 25 inputs/s, a card
  write about 8 min instead of about 2) OR the operator: one write at a time, no judged run or other network job in the window,
  `netstat -an | grep -c TIME_WAIT` < 2,000 before each --go (wait otherwise; W1 -> W2 back to back is what exhausted), and the
  count of "retrying the WHOLE batch" lines + TIME_WAIT after each write in the run log. Any REFUSED write leaves a partial file:
  move it out of DIR by hand (W-2) before a retry.
- WC-2 (LOW): OLLAMA_HOST override no longer needed; the run log still prints the effective URL.
- WC-3 (LOW): each new provenance must carry a digest, not UNAVAILABLE; the registrar withholds that arm's pin otherwise.
- C-CONN-1 (LOW): OMC2 (backoff tail) and OMC1 (commit per row, a half batch persisted on a mid-batch refusal) SURVIVED the EA-CONN /
  EA-WRITE / EA-REFUSE / EA-PARITY selftests; assert `sum(RETRY_BACKOFF_S) >= 220` and a mid-batch dimension refusal leaving whole
  batches only. OMC3 (a malformed 200 JSON retried) SURVIVED: harmless, untested.
- C-CONN-2 (LOW): "EOF" in TRANSIENT_BODY is a loose substring; a deterministic 400 containing it costs 220 s then refuses. Per-request
  timeout 600 s x 6 attempts can hang about 1 h on a stuck server.
- CARRIED: W-1..W-5 (READY_emb_target2); pins of all four arms by the registrar before --run (ruling 19); READY_emb_e0b NOTE on the
  two nomic_raw fits (cpu vs embed) stands.

## OWN MUTANTS (full-file exec; EA ones on {EA-CONN, EA-WRITE, EA-REFUSE, EA-PARITY} with a null baseline SURVIVED; E0b ones on the full selftest with control OMX0 KILLED)

- OMC1 commit per row -> SURVIVED. Not decisive (a partial file has no provenance; every reader refuses).
- OMC2 backoff (2,8,1,1,1) -> SURVIVED. Decisive in kind for claim 7 (the ride-out budget).
- OMC3 ValueError retried -> SURVIVED. Not decisive.
- OMX1 support tag drops the measured spread -> SURVIVED. DECISIVE (P1's SCOREABLE tag).
- OMX2 preflight ignores "qwen3 not listed" -> SURVIVED. Not decisive (404 backstop before any fit).
- OMX3 early_pins skips card arms -> SURVIVED. Not decisive (load_arm pin backstop).

## COMMANDS (compact)

```
git diff --stat 2332d29 e7b0e04 ; git diff --stat 2036725 2232f25 ; git merge-base --is-ancestor 2036725 2232f25   # 1 / 2 files; ancestor
git rev-parse <c>:tools/analysis/<f> ; git show <c>:<f> | sha256sum ; ... | sed 's/$/\r/' | sha256sum             # pins above
git diff --name-only 2036725 2232f25 | grep -cE "application.yml|\.env|\.gitignore|experiment_results/"              # 0
export TAXOARENA_DATA_ROOT=<scratch>/nodata OLLAMA_HOST=http://127.0.0.1:9 OMP_NUM_THREADS=1
emb-conn: embedder_arms.py --selftest (94 PASSED) --mutants (69/69)
emb-e0b2: embedder_arms.py --selftest (95) --mutants (71/71); embedder_cross_flat.py --selftest (49) --mutants (35/35)
python <scratch>/e0b2/own_mut2.py ; own_mut3.py                                                                       # OMC1-3, OMX0-3
python (write_vectors, dim mismatch at item 6 of batch 2)                                                            # 32 rows, 2 calls
python -c "sqlite3 ...incident_w2/..__card.db?mode=ro: count(*)"                                                      # 4064 = 127 x 32
grep "/api/embed" incident_w2/ollama_server.log (15:43:00-15:43:27)                                                  # ~3 batches/s
reg query HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters /v TcpTimedWaitDelay                                # not set
grep -c "M1'" docs/judge_v2_program.md                                                                               # 0
ls -A experiment_results/embedder_cross | grep -c card                                                                # 0
```
