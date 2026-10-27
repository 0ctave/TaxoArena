"""CERT-UNDER-FILTER - does the answer-disagreement filter bias the separation certificate's edges AGAINST the key, beyond
what its loss of support explains? The zero-call refit FRAMEWORK L95 names as a precondition before the filtered schedule
is Stage 3's default. ZERO judge calls; no DB is written; no tree is built.

REGISTRATION OF RECORD: docs/judge_v2_program.md L13229-L13360 (heading "## Registered 2026-09-23 (before any code or
call) - CERT-UNDER-FILTER: ..."; commit 88a95d8); record docs/agents/results/CERT-UNDER-FILTER.json. The last bracket in
the programme file wins over anything restated here.
[RULINGS 2026-09-23: the registrar's section "## Registrar's rulings 2026-09-23 (amendment by insertion; zero calls; before
any real-data run; nothing above is rewritten) - CERT-UNDER-FILTER: ..." (programme L13576-L13642, commit 8469780, ledger
v139) rules R1-R6 on this build (4946646). Every reading below that a ruling changes carries a bracket naming it; the
bracket wins. The code implements the rulings.]

LAUNCH SEQUENCE (registration FLOW: registration -> build -> READY committed -> --dry-run -> --run -> review -> registrar):

  python tools/analysis/cert_under_filter.py --selftest            # synthetic fixtures under tempfile.mkdtemp(); opens NO
                                                                   # DB of record; every criterion / prediction / falsifier
                                                                   # print branch executed and listed
  python tools/analysis/cert_under_filter.py --dry-run [--workers N]
                                                                   # 0 calls, WRITES NOTHING: pool id, G1-G3, per-anchor
                                                                   # kept counts under A and B, per-anchor edge counts, the
                                                                   # measured wall time of ONE arm build and the extrapolation
  python tools/analysis/cert_under_filter.py --run [--workers N]   # the write-once outcome
                                                                   # experiment_results/x12_crossdomain/cert_under_filter_outcome.txt

  There is no --pilot and no judge cache: the test posts nothing, so the truncation guard, the pinned judge meta and the
  _PILOT / _partial files have no object. The outcome is written only after every arm, gate and readout has completed;
  a failed gate or any exception writes nothing. --run refuses BEFORE computing if the outcome path exists, and the file
  is opened with mode "x" (write-once).

HYGIENE (registration "HYGIENE"). First printed line: pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL). Read
mode=ro&immutable=1 only: the x12 verdict cache (experiment_results/x12_crossdomain/stack_v2_promptv2_x12all.db, the cache
systematic_budget.py reads), the eval DB (mmlu_pro_dataset_cache_v2.db: eval_results.pred for the filter and for A_eval;
eval_results.is_correct ONLY for the key direction and the McNemar labels, exactly as systematic_budget.build and
mcnemar_edge use it; reserved_pool for the eval-side questions), and snapshots.db for the promoted tree's anchor map. The
routing is the CSV r512.primary_routing reads. THE FILTER READS NO KEY. The WAL sidecar of each DB is reported on every
run (immutable=1 does not see a WAL tail; G1 / G2 are the data pins that would catch one).
  [CORRECTED 2026-09-23 by the registrar's ruling R6 (reading REFUSED): a NON-EMPTY -wal beside any input DB REFUSES the
  run (check_wal, before the pool guard and again at load); an absent or empty one is reported.]
  * stack_judge.py is NEVER imported. systematic_budget.py imports it at module level, so a stub module is installed in
    sys.modules["stack_judge"] BEFORE systematic_budget is imported; the stub's open_cache() refuses (it is the read-write
    open of STACK-JUDGE-RO-CACHE). The stub's identity is asserted after the imports.
    [RULED 2026-09-23 by the registrar, R3 (ADMITTED on three conditions, each executed by --selftest): (i) the stub
    raises StubRefusal on ANY non-dunder attribute read or write (open_cache, cache_path, PROMPT, an arbitrary name,
    getattr with a default, setattr); (ii) assert_stack_judge_not_loaded(): no module in sys.modules has a file named
    stack_judge.py and a call through systematic_budget.sj refuses; (iii) sqlite3.connect is wrapped BEFORE any import
    (the connection log): a DB opened at import refuses the process, the stack cache stack_v2_promptv2_x12all.db is
    refused and never enters the log, and the log is printed in the dry-run and in the outcome.]
    [RE-RULED 2026-09-23 by the registrar (review acd054a, D1; programme L14342-L14381, commit 8bbe6ce): R3 (iii)'s words
    contradicted the registration's permitted read of this very cache. stack_v2_promptv2_x12all.db is OPENED EXACTLY
    ONCE, BY load_real, WITH THE URI file:<path>?mode=ro&immutable=1, AFTER CHECKING THAT ITS -wal IS ABSENT OR EMPTY;
    any other open of it (a plain path, another URI, a second open, an open outside load_real) REFUSES, and
    connection_log applies the same rule (the log must hold that one open and no other). R3 (i) and (ii) stand. The
    selftest runs load_real on a SYNTHETIC stack_v2_promptv2_x12all.db in the tempdir: the immutable URI is admitted, a
    plain sqlite3.connect(path) is refused, a second open is refused, a non-empty -wal refuses.]
  * systematic_budget.main is replaced by a refusal in this process: this script never regenerates
    experiment_results/x12_crossdomain/systematic_budget.txt (sha256 c4c26a4d..., standing merge condition M2) nor
    systematic_budget_unfiltered.txt. No systematic_budget file of record can be written from here.

WHAT IS IMPORTED, NEVER RE-IMPLEMENTED (registration: "the board fit, the certificate and the McNemar are the FUNCTIONS OF
RECORD in systematic_budget.py"): judge_free_tests.board_from -> rejudge_grok.mm_fit (the board fit, prior 0.5 asserted);
systematic_budget.craw / cbud / fit / nll (the certificate and the widener); systematic_budget.mcnemar_edge / established
(the McNemar, integer arithmetic); calibration_status.status_word (FRAMEWORK L101's status word, one home);
a_redefine_refit.agreement / vec / vnll / vfit / cluster_boot / profile_lr / loao (A_eval and the b1 identification of
record). The shipped filter rule (MatchFilter.kt AnswerDisagreementFilter) is profile_r_filtered.norm_shipped / verdict,
EXTRACTED BY ast FROM THAT FILE AND EXECUTED (not imported: profile_r_filtered's import chain reaches x20_merged); their
LF sources are pinned by sha16.

THE ONE LOCAL COPY, AND ITS PIN. systematic_budget.build() cannot be called on an arm: it reads the whole verdict cache
through stack_judge.open_cache() (read-write), opens the eval DB mode=ro WITHOUT immutable=1, skips anchors below 200 rows
and edges whose ARM key gap is 0, and takes the key direction from the arm's own questions - whereas the registration
fixes the anchor set, the edge set, the established set and the key direction ONCE, FROM U. arm_edges() below is a
line-for-line copy of build()'s per-anchor bootstrap loop (B = 300, random.Random(42), the same draw order), run on an
arm's rows with U's anchors and U's edges. Its fidelity is asserted two ways: (1) build()'s LF source must hash to
BUILD_SRC_SHA16 or every mode refuses; (2) the --selftest runs the REAL systematic_budget.build() (through the stub, on a
synthetic in-memory cache) and requires arm_edges() in discovery mode to reproduce every field of every edge bit for bit.
[RULED 2026-09-23 by the registrar, R4 (ADMITTED on conditions): (a) build()'s LF source hash 128baa007a44a219 (the
source text extracted by ast from systematic_budget.py, CRLF normalised to LF before hashing) is asserted AT LAUNCH in
every mode, before anything else runs, and a mismatch refuses; (b) the bit-identity selftest (all edges, every field)
is executed in the READY; (c) THE COPY'S DELIBERATE DIFFERENCES, each tied to a registered requirement:
   D-a  no verdict cache is opened by the copy: it receives an arm's rows (read by load_real, mode=ro&immutable=1)
        - registration HYGIENE (read-only, immutable=1; stack_judge not imported);
   D-b  no eval DB is opened by the copy: K and P come from load_real (mode=ro&immutable=1) - HYGIENE;
   D-c  in fixed mode the key direction is U's la[a] > la[b], stored on each U edge (key_ab), never the arm's own -
        "THE ESTABLISHED SET IS FIXED ONCE, FROM U, AND HELD FIXED ACROSS ARMS";
   D-d  in fixed mode the edge list is U's 920 edges: the 200-row floor and the gap-0 / no-both-predictions cuts are
        applied ONCE, on U (discovery mode, which is build() itself), to define the edge set; under an arm an anchor
        below the floor is not refitted on another edge set - it is a REMOVED anchor under R2 (a);
   D-e  the arm's rows are a verdict SUBSET (F, or an R draw) - the registered design (U / F / R);
   D-f  one extra board per anchor, the point fit on the arm's full rows, printed beside (R5); it consumes no random
        draw, so the bootstrap stream is build()'s.]

THE DESIGN (registration "THE DESIGN"). U = all 9,142 valid x12 verdicts; F = the deployed filter, CONVENTION A (a match
is kept unless the two contestants' extracted predictions are EQUAL; a missing prediction is KEPT): 6,066 of 9,142 - THE
CONVENTION IN FORCE, printed on every run; CONVENTION B (missing dropped: 5,276 of 8,352) is run beside in full (F_B and
its own 20-draw control) and DECIDES NOTHING. R = per (anchor, unordered pair) cell a uniformly random subset of the
cell's U matches of EXACTLY F's kept count; K = 20 draws, random.Random(1000 + k), k = 1..20, cells visited in sorted
order, random.Random.sample on the cell's U rows in U order.
[CORRECTED 2026-09-23 by the registrar's ruling R6 (reading REFUSED): convention B's R is drawn from U's cells MINUS the
missing-prediction rows (the universe B's F selects from, base 8,352); G3 also refuses a B draw holding such a row.
Convention A's R is drawn from U's cells as written.]

READINGS FIXED BEFORE THE RUN, where the registration leaves a choice (each is printed in the outcome):
  (r1) EDGE DIRECTION. The registration writes W's direction as "the sign of theta_a - theta_b in the anchor's fit", and
       G1 pins U's 26 wrong-direction established edges, which are systematic_budget.build()'s `right` field: the
       bootstrap majority sign, p = share of the 300 question-bootstrap boards with theta_a > theta_b, direction a > b iff
       p > 0.5. The PRIMARY direction is that field (the certificate's own edge object, the one G1 reproduces). The sign
       of m (the bootstrap mean) and the sign of the single point fit on the arm's full rows are printed beside on every
       arm with their Delta_W point, deciding nothing. Key direction la_U[a] > la_U[b] from U, held fixed across arms.
       [RULED 2026-09-23 by the registrar, R5: the parenthetical was a transcription error; the MAJORITY sign over each
       arm's own bootstrap boards is PRIMARY, as built; the point-fit sign is printed beside, deciding nothing; G1 stands.]
  (r2) BOTH TIE CONVENTIONS. An edge with p exactly 0.5 is a direction tie; build()'s rule reads it as "b ahead". The
       count of such ties among the established edges is printed per arm, with W under ties-as-wrong and ties-excluded.
  (r3) "F and the 20 R draws recomputed in each replicate": every board in this test is fitted PER ANCHOR, so resampling
       anchors whole leaves each anchor's F and R values unchanged; a replicate's Delta_W is the sum of the resampled
       anchors' d_a = W_F,a - mean_k W_R,a,k. This IS the recomputation, not an approximation of it.
       numpy.random.default_rng(42), B = 2000, SE = sd(ddof = 1), interval = point +- 1.96 x SE; HELD iff hi < 0,
       FAILED iff lo > 0, UNDETERMINED iff lo <= 0 <= hi (disjoint and exhaustive). The percentile interval and the
       edge-level paired counts ("R majority" = wrong in MORE than 10 of the 20 draws) are printed beside.
  (r4) VALIDITY TRIGGERS FIRST (standing rule, 7da2ec5: they pre-empt the verdict expression). C1: fewer than 2 connected
       anchors -> UNDETERMINED BY TRIGGER, falsifier not evaluated. An anchor whose F comparison graph (the models of
       its U cell, linked by pairs with >= 1 kept match) is disconnected is UNDETERMINED BY CONSTRUCTION (FRAMEWORK L85:
       "a cell whose comparison graph is disconnected is REFUSED") and its edges leave the C1-C3 denominators and are
       counted (C4). R has F's zero cells by construction (G3), so R disconnects exactly where F does. C3: W_F <= 14
       events -> UNDETERMINED BY TRIGGER (registered Support (g): "at 14 or fewer events b1 is unidentifiable"); the fit
       numbers are printed beside, not read.
       [CORRECTED 2026-09-23 by the registrar's rulings R1 and R2: (R2 (a)) an anchor LEAVES the C1-C3 denominators if
       its comparison graph disconnects OR its kept rows fall below build()'s 200-row floor (per convention; F and its R
       draws have the same per-anchor counts by G3); (R2 (b)) C1's ONE registered trigger is SUPPORT: C1 is UNDETERMINED
       (BY TRIGGER: SUPPORT) iff FEWER THAN 12 of the 14 anchors remain (C1_MIN_ANCHORS = 12), evaluated FIRST, the
       interval printed and not scored, the falsifier not evaluated; the "fewer than 2" trigger is subsumed. (R1) there
       is NO trigger on C3: W_F <= 14 is printed as a DESCRIPTIVE flag "b1 structurally unidentifiable at this event
       count (Support (g))", deciding nothing.]
  (r5) SUPPORT, MEASURED. d_e = 1[wrong in F] - P_R(wrong)_e over the established edges of the connected anchors;
       SE_iid = sqrt(sum d_e^2) (registration (d)); SE = the cluster-bootstrap SE; MEASURED DEFF = SE^2 / SE_iid^2; n_eff =
       edges / DEFF; MDE = 2.80 x SE. The registered planning numbers (SE_iid 4.24, DEFF 1.6, MDE 15.0, break-even 1.82,
       pessimistic 3.0 / 20.6) are printed beside, and "UNDERPOWERED FOR ITS OWN BAR" is printed iff the measured DEFF
       exceeds the registered break-even 1.82. Kish's mean cluster size sum n_a^2 / sum n_a and the arithmetic 809 / 14
       are both printed (registration (a): "the dry-run prints the exact figure").
  (r6) C2, DESCRIPTIVE. Widener + decline = the widener's c~ >= 0.975 among the ESTABLISHED edges (KEY-TIE-DECLINE's
       decline is "not established", and the established set is fixed from U), so every wrong call there is established
       and prints W(W). The widener alone on all 920 edges is printed beside with wrong(established). Parameters are
       FIXED, not refitted per arm: the eval-side pair (-3.2172, +3.2921) as primary with A = A_eval, the stored Mistral
       pair and the 920 refit printed beside with the same A_eval. Status word: calibration_status.status_word(nominal,
       wrong). The U reference values (LOAO 646 / 3(2), 1.28; in-sample 651 / 2(1)) are the 920 pair on JUDGED A,
       recomputed here as reproduction lines (not gates).
  (r7) C3, DESCRIPTIVE. a_redefine_refit.profile_lr on F's established edges (connected anchors) with A_eval and F's m, s
       and direction; cluster bootstrap P(b1 <= 0) at the record's two conventions (600 reps numpy seed 11; 2000 reps
       seed 2026); U recomputed beside (record: 5.16, 0.0367 / 0.0315). Reading, as A-REDEFINE-REFIT: rejected by both /
       not rejected / tests disagree.
       [CORRECTED 2026-09-23 by the registrar's ruling R1: no C3 trigger; when no finite delta-deviance can be computed
       (no wrong or no right event among the edges) C3 reads NO FIT; the W_F <= 14 flag is descriptive. The C3 bootstrap
       conventions are ADMITTED (R6).]
       [CORRECTED 2026-09-23 by the registrar's ruling "'b1 unidentified' DEFINED as (quasi-)complete separation"
       (programme L13883-L13923, commit c669926, ledger v146): unidentified(es) checks the DATA BEFORE ANY FIT: zero
       wrong or zero right events, or max A(wrong) <= min A(right), or max A(right) <= min A(wrong) (a boundary tie is
       quasi-complete and counts); with a non-finite ddev these read "NO FIT (b1 unidentified: <reason>)". The optimiser
       still runs where it can and its b0 / b1 / ddev are printed as DESCRIPTIVE; the cluster bootstrap is not run on an
       unidentified set. |b1| and the profile curvature at the optimum are printed beside EVERY fit, descriptively (the
       ruling's disclosed limit: the likelihood also depends on m and s, so a fit can be flat without range separation;
       NOT a trigger). The same definition is applied on U, F, F_B and, as a data check, on every R draw of both
       conventions. DISCLOSED CONFLICT, not resolved in code: the synthetic case relayed as "b1 +720, ddev 1.06" is NOT
       range-separated (A(wrong) 0.382-0.634, A(right) 0.320-0.640); it is the disclosed limit (curvature 0) and reads
       identified under the definition as written; the selftest pins and prints this.]
       [CORRECTED 2026-09-23 by the registrar's ruling "'b1 unidentified' EXTENDED to SINGULAR OBSERVED INFORMATION"
       (programme L14034-L14069, commit 0ce8460, ledger v154), which supersedes, for the singular-information case, the
       sentence above that the flat profile is "NOT a trigger" and resolves the DISCLOSED CONFLICT: b1* = the optimiser's
       b1; l(b1) = the PROFILE log-likelihood (b0 re-maximised at each b1); I = -l''(b1*) by the central second
       difference with h = 1e-4 x max(1, |b1*|); the fit is UNIDENTIFIED ("b1 unidentified: singular observed
       information") iff I <= 0 OR I x h^2 <= 16 x eps x max(1, |l(b1*)|), eps = 2^-52 (SING_FACTOR = 16, registered by
       the ruling). This EXTENDS separation: either makes the fit NO FIT; separation / zero events are checked first on
       the data and name the reason when both hold. I, h, l(b1*), I x h^2 and the bound are printed beside EVERY fit (U,
       F, F_B and every R draw of both conventions, the R draws now fitted for this; descriptive there); the previous
       "profile curvature" print (step 1e-3, descriptive) is replaced by I at the ruling's step. INNER RE-MAXIMISATION:
       scipy Brent (minimize_scalar method "brent", bracket started at the optimiser's b0 +- 1, xtol 1e-12, Brent's
       absolute floor 1e-11, maxiter 2000); success is required, and its a-posteriori value error (the Newton decrement
       g^2 / (2c) at the inner optimum, g at step 6e-6 x max(1,|b0|), c at step 1e-4 x max(1,|b0|); |g| x step where
       c <= 0),
       x 4 (the 1, 2, 1 coefficients), must stay within the
       12 x eps x max(1, |l|) of the 16 the ruling leaves beyond the 4 x eps round-off bound; either failure REFUSES the
       run ([C3-INNER]). Where scipy finds no valid bracket because the nll is FLAT in b0 (every tau at the exp(20) cap,
       as on R draws of the favorable fixture), a scan of b0 at +- 1e-3 x max(1,|b0|) x 2^k (k = 0..30) either finds no
       strictly lower value (a PLATEAU: its value, error 0 at the scan's resolution, printed "plateau") or brackets the
       lowest scanned point for Brent (_inner_b0 states the rule). The +720 / ddev 1.06 case has I = -0.0 exactly (a plateau: every edge's tau is ~0 or at the
       exp(20) cap) and reads NO FIT via the I <= 0 limb. The script prints its own identity (sha256-lf16 and git blob of
       its LF rendering) at start, and the count of singular-information evaluations (> 0 required in --selftest and
       --run).]
       [CORRECTED 2026-09-23 by the registrar's rulings on review acd054a (programme L14342-L14381, commit 8bbe6ce),
       which supersede the bracket above where they differ. (D2) A failed inner re-maximisation of b0 (Brent not
       converged, a scan that finds no interior optimum, a non-finite scan) makes THAT FIT "NO FIT (b1 unidentified:
       inner re-maximisation not resolved: <reason>)", and a non-finite I makes it "NO FIT (b1 unidentified: non-finite
       observed information)"; P5 is UNDETERMINED if it is F's fit; C1 and every other readout are unaffected; NO
       refusal of the run arises from C3 (the [C3-INNER] / [C3-INFO] refusals are removed; branch ids
       INNER.BRENT_NOT_CONVERGED, INNER.NO_INTERIOR, INNER.NONFINITE_SCAN, SING.NONFINITE_I, C3.NO_FIT_INNER,
       C3.NO_FIT_NONFINITE_I, each executed by --selftest). (D5) INNER_MARGIN is removed; the ONE registered constant is
       16 (multiplicative, 4 x 4); the inner value-error estimate g^2 / (2c) is printed as DESCRIPTIVE beside every fit,
       with no check beyond Brent's convergence. (D3) the selftest fits a set with |b1*| < 1 and requires h == 1e-4.
       (D6) the execution witness is EXACT: the information assessments (counted in observed_information) must EQUAL
       the fits (counted in c3_fit), both printed; --run also requires 3 + 2 x 20 = 43 C3 fits attempted; --selftest
       pins its own exact counts. scipy Brent's absolute floor (1e-11) is checked once AT LAUNCH, beside the build()
       pin, not inside C3.]
  (r8) PREDICTIONS scored HELD / FAILED explicitly: P1 6 <= W_F <= 22; P2 24 <= mean W_R <= 38; P3 -26 <= Delta_W <= -6
       AND C1 HELD; P4 0 <= F's W(W) at 0.975 (widener + decline, primary pair) <= 4 AND 1.0 <= its nominal <= 2.0; P5 C3
       reads UNDETERMINED: ddev < 3.84, or no ddev computable under the C3 trigger; P6 0 anchors disconnect AND
       5 <= zero-kept edges <= 40 (of 920).
       [CORRECTED 2026-09-23 by the registrar's ruling R1 (b): P5 is scored ONLY on a computed delta-deviance: HELD iff
       ddev < 3.84, FAILED iff ddev >= 3.84; if none can be computed P5 is UNDETERMINED, NEVER HELD. P6 counts
       disconnected anchors only (unchanged by R2).]
       [CORRECTED 2026-09-23 by the separation ruling (L13883-L13923): P5 is UNDETERMINED whenever C3 reads NO FIT (b1
       unidentified: zero events, separation, or non-finite), even if the optimiser returned a finite ddev; that ddev is
       printed as descriptive. Guards and selftest checks are explicit raises (need() / SystemExit), never `assert`, so
       python -O cannot remove them.]
       [CORRECTED 2026-09-23 by the singular-information ruling (programme L14034-L14069, commit 0ce8460): "NO FIT (b1
       unidentified: singular observed information)" is a NO FIT like separation; P5 is UNDETERMINED on it, on every arm
       and under each convention; the optimiser's b1 and ddev are then DESCRIPTIVE.]
  (r9) The anchor set is U's (build()'s floor of 200 rows applied ONCE, on U); arms apply no floor. The filter counts
       (G2) are over all 9,142 valid verdicts; the arms are the routed rows of U's anchors (the count is printed).
       [CORRECTED 2026-09-23 by the registrar's rulings R2 (a) / R4: arms apply no floor to REFIT, but an anchor whose
       kept rows fall below 200 under a convention is REMOVED from that convention's C1-C3 denominators and counts
       toward the support trigger.]

GATES (refusals; a failed gate writes nothing; gates are not verdict clauses): G1 U = 920 edges, 809 established, 26
wrong among them; G2 6,066 of 9,142 (A) and 5,276 of 8,352 (B); G3 every R draw has exactly F's kept count in every cell.

Every registered criterion, prediction and falsifier line goes through a function that records a branch id; --selftest
executes all of them and fails unless every registered branch id was hit (the TOPIC-PARTITION-20NG D1 / D7 rule). No
computed value is identity-tested: every comparison is wrapped in bool().
"""
import argparse, ast, hashlib, itertools, json, math, os, random, sqlite3, sys, tempfile, time, types
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)


class CheckFailed(RuntimeError):
    """An explicit guard or selftest check failed. Raised by need(); never an `assert` (python -O strips asserts)."""


def need(cond, msg="check failed"):
    if not bool(cond):
        raise CheckFailed(msg if isinstance(msg, str) else repr(msg))


# ------------------------------------------------------------------------------------------ the connection log (R3 (iii))
# Installed BEFORE any other module is imported, so every sqlite3.connect made by this process - including any made by a
# module at import time - is logged. R3 (iii) AS RE-RULED (8bbe6ce, D1): the stack cache is opened EXACTLY ONCE, by
# load_real, as file:<path>?mode=ro&immutable=1 after its -wal is checked absent or empty; any other open of it refuses.
# Nothing may open a DB at import.
STACK_CACHE_NAME = "stack_v2_promptv2_x12all.db"
CONNECTIONS = []
REFUSED_CONNECTIONS = []
STACK_OPENS = []            # the admitted opens of the stack cache (at most one per process)
_STACK_AUTH = [None]        # the one URI load_real is about to open; None everywhere else
_REAL_CONNECT = sqlite3.connect


def stack_uri(path):
    return "file:%s?mode=ro&immutable=1" % str(path).replace("\\", "/")


def _logged_connect(db, *a, **k):
    s = str(db).replace("\\", "/")
    if STACK_CACHE_NAME in s:
        why = None
        if _STACK_AUTH[0] is None:
            why = "not opened by load_real"
        elif s != _STACK_AUTH[0] or not bool(k.get("uri")) or a:
            why = "not the URI file:<path>?mode=ro&immutable=1 (uri=True)"
        elif STACK_OPENS:
            why = "a second open (it is opened exactly once)"
        else:
            p = s[len("file:"):s.index("?")]
            if os.path.exists(p + "-wal") and bool(os.path.getsize(p + "-wal") > 0):
                why = "its -wal is non-empty (%d bytes)" % os.path.getsize(p + "-wal")
        if why is not None:
            REFUSED_CONNECTIONS.append(s)
            h = globals().get("hit")
            if h is not None:
                h("HYGIENE.STACK_REFUSED")
            raise SystemExit("[HYGIENE] refused to open the stack cache %s: %s (R3 (iii) as re-ruled, 8bbe6ce: opened "
                             "exactly once, by load_real, as file:<path>?mode=ro&immutable=1)" % (s, why))
        STACK_OPENS.append(s)
        h = globals().get("hit")
        if h is not None:
            h("HYGIENE.STACK_ADMITTED")
    CONNECTIONS.append(s)
    return _REAL_CONNECT(db, *a, **k)


sqlite3.connect = _logged_connect


# ------------------------------------------------------------------------------------------ stack_judge is never loaded (R3)
STUB_ACCESSES = []          # every refused non-dunder access to the stub, recorded even if a caller catches the refusal


def _stub_hit(name="?"):
    STUB_ACCESSES.append(name)
    h = globals().get("hit")
    if h is not None:
        h("STUB.REFUSED")


class StubRefusal(RuntimeError):
    """Raised by the stack_judge stub; deliberately NOT an AttributeError, so getattr(..., default) / hasattr cannot
    swallow it."""


class _RefusingModule(types.ModuleType):
    """The stub placed in sys.modules["stack_judge"] (R3 (i)): ANY attribute read or write raises. Only the module
    metadata dunders the import system itself reads (__name__, __spec__, __loader__, ...) behave as on a plain module;
    no function, constant or path of stack_judge exists on it."""

    def __getattr__(self, name):
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(name)
        _stub_hit(name)
        raise StubRefusal("[HYGIENE] stack_judge.%s refused: stack_judge.py is never loaded in cert_under_filter "
                          "(read-write open_cache, STACK-JUDGE-RO-CACHE; registrar's ruling R3)" % name)

    def __setattr__(self, name, value):
        if name.startswith("__") and name.endswith("__"):
            return types.ModuleType.__setattr__(self, name, value)
        _stub_hit(name)
        raise StubRefusal("[HYGIENE] setting stack_judge.%s refused (R3)" % name)


def _install_stack_judge_stub():
    cur = sys.modules.get("stack_judge")
    if cur is not None and not isinstance(cur, _RefusingModule):
        raise SystemExit("[HYGIENE] stack_judge.py is already imported in this process; the registration forbids it "
                         "(read-write open_cache, STACK-JUDGE-RO-CACHE). Refused.")
    if cur is None:
        cur = _RefusingModule("stack_judge")
        sys.modules["stack_judge"] = cur
    return cur


def assert_stack_judge_not_loaded():
    """R3 (ii): no module in sys.modules comes from a file named stack_judge.py, and the name resolves to the stub."""
    for name, m in list(sys.modules.items()):
        try:
            f = types.ModuleType.__getattribute__(m, "__dict__").get("__file__") if isinstance(m, types.ModuleType) else None
        except Exception:
            f = None
        if f and os.path.basename(str(f)).lower() == "stack_judge.py":
            raise SystemExit("[HYGIENE] module %s was loaded from %s: stack_judge.py must never be loaded (R3). Refused." % (name, f))
    if not isinstance(sys.modules.get("stack_judge"), _RefusingModule):
        raise SystemExit("[HYGIENE] sys.modules['stack_judge'] is not the refusing stub (R3). Refused.")


SJ_STUB = _install_stack_judge_stub()

import numpy as np                                   # noqa: E402
import rejudge_grok as rj                            # noqa: E402
import rubric_p8 as p8                               # noqa: E402
import rubric_512 as r512                            # noqa: E402
import judge_free_tests as jf                        # noqa: E402
import pool_guard                                    # noqa: E402
import systematic_budget as sb                       # noqa: E402
import a_redefine_refit as arr                       # noqa: E402
from calibration_status import status_word           # noqa: E402  FRAMEWORK L101, the one home

if sys.modules["stack_judge"] is not SJ_STUB:
    raise SystemExit("[HYGIENE] stack_judge.py was imported; refused")
if sb.sj is not SJ_STUB:
    raise SystemExit("[HYGIENE] systematic_budget bound the real stack_judge; refused")
assert_stack_judge_not_loaded()
IMPORT_CONNECTIONS = list(CONNECTIONS)
IMPORT_STUB_ACCESSES = list(STUB_ACCESSES)


def check_import_stub_accesses(accesses):
    """R3 confirmation (L13883 (3)): no non-dunder stack_judge attribute may be read or written while the modules load.
    Every refused access is logged by the stub even when a caller catches StubRefusal, so none can hide."""
    if accesses:
        raise SystemExit("[HYGIENE] a non-dunder stack_judge attribute was touched at import (R3 confirmation): %s. "
                         "Refused." % list(accesses))


check_import_stub_accesses(IMPORT_STUB_ACCESSES)
if IMPORT_CONNECTIONS:
    raise SystemExit("[HYGIENE] a module opened a DB at import (R3: none may): %s. Refused." % IMPORT_CONNECTIONS)


def _no_sb_main(*_a, **_k):
    raise SystemExit("[M2] systematic_budget.main is never called from cert_under_filter: systematic_budget.txt "
                     "(sha256 c4c26a4d...) is under merge condition M2 and must not be regenerated.")


sb.main = _no_sb_main

# ------------------------------------------------------------------------------------------ constants of record
OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "cert_under_filter_outcome.txt")
X12_CACHE = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "stack_v2_promptv2_x12all.db")
SB_PATH = os.path.abspath(sb.__file__)                                    # the module actually imported
PRF_PATH = os.path.join(os.path.dirname(SB_PATH), "profile_r_filtered.py")
TREE = "bareq512_s42"
POOL = pool_guard.MMLU_PRO_POOL
EXCLUDE = "Meta-Llama-3-70B-Instruct"
THRESH = sb.THRESH                 # 0.975
GAP = sb.GAP                       # 0.02
BOOT_B = sb.B                      # 300 question-bootstrap boards per anchor (the certificate fit)
ANCHOR_FLOOR = 200                 # build(): "if len(rs) < 200: continue", applied once, on U
K_DRAWS = 20
R_SEED0 = 1000
CLUSTER_B = 2000
CLUSTER_SEED = 42
Z = 1.96
MDE_K = 2.80
C3_EVENT_FLAG = 14                 # Support (g): a DESCRIPTIVE flag on C3, deciding nothing (ruling R1)
C1_MIN_ANCHORS = 12                # ruling R2 (b): C1 UNDETERMINED (BY TRIGGER: SUPPORT) iff fewer than 12 of 14 remain
C3_REPS = ((600, 11), (2000, 2026))
PAIR_EVAL = (-3.2172, 3.2921)      # A-REDEFINE-REFIT eval-side refit (891 set) - PRIMARY
PAIR_MISTRAL = (-3.2326, 3.3133)   # stored Mistral pair, FRAMEWORK L95
PAIR_920 = (-3.0438, 3.1980)       # 920 unfiltered refit
PAIRS = (("eval-side refit (PRIMARY)", PAIR_EVAL), ("stored Mistral pair", PAIR_MISTRAL), ("920 refit", PAIR_920))
PINS = dict(edges=920, established=809, wrong_est=26, n=9142, keptA=6066, keptB=5276, baseB=8352)
PLAN = dict(se_iid=4.24, deff=1.6, deff_pess=3.0, mde=15.0, mde_pess=20.6, break_even=1.82, pred_delta=-16.0,
            kish_reg=57.8)
U_REF = dict(loao=(646, 3, 2, 1.28), insample=(651, 2, 1), c3_ddev=5.16, c3_p=(0.0315, 0.0367))
REPRO = dict(all_wrong=60, filt_edges=891, filt_wrong=44, eval891=(-3.2172, 3.2921))
BUILD_SRC_SHA16 = "128baa007a44a219"          # LF source of systematic_budget.build at 0a1b44b
FILTER_SRC_SHA16 = {"norm_shipped": "8a57eed5d4c6bc5c", "verdict": "e2f9b94da1d1669e"}
# singular observed information (registrar's ruling, programme L14034-L14069, commit 0ce8460)
EPS64 = 2.0 ** -52                 # float64 machine epsilon, as registered
SING_FACTOR = 16.0                 # REGISTERED: 4 x eps x |l| round-off bound of the second difference x a 4x margin
INFO_STEP_REL = 1e-4               # h = 1e-4 x max(1, |b1*|)
INNER_XTOL = 1e-12                 # Brent relative x tolerance of the inner b0 re-maximisation
INNER_MINTOL = 1e-11               # Brent's absolute floor (scipy.optimize._optimize.Brent._mintol; checked at use)
INNER_MAXITER = 2000
SING_REASON = "singular observed information"
NONFINITE_REASON = "non-finite observed information"
INNER_PREFIX = "inner re-maximisation not resolved: "
SING_EVALS = [0]                   # execution witness: information assessments, counted in observed_information
FIT_COUNT = [0]                    # counted independently: c3_fit calls that produced a fit
C3_CALLS = [0]                     # c3_fit calls
_INNER_IMPL = [None]               # selftest-only override of the inner search (restored in a finally); None = _inner_min
INNER_PLATEAUS = [0]               # inner re-maximisations resolved as a plateau (printed beside the witness)

# ------------------------------------------------------------------------------------------ branch registry
REGISTERED_BRANCHES = (
    ["C1.HELD", "C1.FAILED", "C1.UNDETERMINED", "C1.TRIGGER", "C1.TRIGGER_NOT_FIRED",
     "FALSIFIER.FIRED", "FALSIFIER.DISCHARGE", "FALSIFIER.UNMET", "FALSIFIER.NOT_EVALUATED",
     "SUPPORT.UNDERPOWERED", "SUPPORT.WITHIN_BREAK_EVEN", "SUPPORT.DEFF_UNDEFINED",
     "C2.STATUS.LT3", "C2.STATUS.3TO9", "C2.STATUS.GE9",
     "C3.FLAG_LE14", "C3.NO_FIT", "C3.REJECTED", "C3.NOT_REJECTED", "C3.DISAGREE",
     "SEP.ZERO_EVENTS", "SEP.WRONG_BELOW_RIGHT", "SEP.RIGHT_BELOW_WRONG", "SEP.QUASI_TIE", "SEP.OVERLAP",
     "SING.I_NONPOS", "SING.ROUNDOFF", "SING.NONSINGULAR", "SING.NONFINITE_I",
     "INNER.BRENT_NOT_CONVERGED", "INNER.NO_INTERIOR", "INNER.NONFINITE_SCAN",
     "C3.NO_FIT_SINGULAR", "C3.NO_FIT_INNER", "C3.NO_FIT_NONFINITE_I",
     "HYGIENE.STACK_ADMITTED", "HYGIENE.STACK_REFUSED",
     "C4.NONE_DISCONNECTED", "C4.DISCONNECTED", "C4.FLOOR_REMOVED",
     "CONV.IN_FORCE", "CONV.B_BESIDE",
     "G1.REFUSED", "G2.REFUSED", "G3.REFUSED", "WRITE_ONCE.REFUSED", "BUILD_PIN.REFUSED", "WAL.REFUSED",
     "STUB.REFUSED", "P5.UNDETERMINED"]
    + ["P%d.%s" % (i, v) for i in range(1, 7) for v in ("HELD", "FAILED")])
HITS = defaultdict(int)


def hit(branch):
    if branch not in REGISTERED_BRANCHES:
        raise AssertionError("unregistered branch id %s" % branch)
    HITS[branch] += 1


# ------------------------------------------------------------------------------------------ source pins
def _func_source(path, name):
    txt = open(path, encoding="utf-8").read().replace("\r\n", "\n")
    for node in ast.parse(txt).body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(txt, node)
    raise SystemExit("[PIN] %s has no top-level function %s" % (path, name))


def sha16(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def script_identity(path=None):
    """This script's own pins, each named by its kind: sha256-lf16 = the first 16 hex of sha256 over the LF rendering;
    blob = git's blob id of the LF rendering (sha1 over "blob <len>" NUL + bytes, = `git hash-object` on the committed
    file); the working-tree bytes' own sha256-crlf16 is named beside only when they are not already LF."""
    raw = open(path or os.path.abspath(__file__), "rb").read()
    lf = raw.replace(b"\r\n", b"\n")
    return dict(sha256_lf16=hashlib.sha256(lf).hexdigest()[:16],
                blob=hashlib.sha1(b"blob %d\0" % len(lf) + lf).hexdigest(),
                worktree="LF" if raw == lf else "CRLF (sha256-crlf16:%s)" % hashlib.sha256(raw).hexdigest()[:16])


def identity_line():
    i = script_identity()
    return ("  script identity: cert_under_filter.py sha256-lf16:%s blob:%s (LF rendering; working tree %s)"
            % (i["sha256_lf16"], i["blob"], i["worktree"]))


def check_build_pin(src=None):
    got = sha16(src if src is not None else _func_source(SB_PATH, "build"))
    if got != BUILD_SRC_SHA16:
        hit("BUILD_PIN.REFUSED")
        raise SystemExit("[PIN] systematic_budget.build LF source hashes to %s, pinned %s: arm_edges() is a copy of its "
                         "per-anchor loop and is valid only against the pinned source. Refused; re-review." % (got, BUILD_SRC_SHA16))
    return got


def load_filter():
    ns = {}
    for name in ("norm_shipped", "verdict"):
        src = _func_source(PRF_PATH, name)
        if sha16(src) != FILTER_SRC_SHA16[name]:
            raise SystemExit("[PIN] profile_r_filtered.%s LF source hashes to %s, pinned %s. Refused."
                             % (name, sha16(src), FILTER_SRC_SHA16[name]))
        exec(compile(src, PRF_PATH, "exec"), ns)
    return ns["verdict"]


FILTER_VERDICT = load_filter()


# ------------------------------------------------------------------------------------------ data of record (read-only)
def ro(path):
    return sqlite3.connect("file:%s?mode=ro&immutable=1" % path.replace("\\", "/"), uri=True)


def wal_status(path):
    w = path + "-wal"
    if not os.path.exists(w):
        return "no WAL sidecar"
    return "WAL sidecar %d bytes" % os.path.getsize(w)


def check_wal(paths):
    """Registrar's R6: with mode=ro&immutable=1 SQLite IGNORES a -wal file, so a NON-EMPTY -wal beside any input would
    silently omit committed rows. A non-empty -wal REFUSES the run; an absent or empty one is reported."""
    for p in paths:
        w = p + "-wal"
        if os.path.exists(w) and bool(os.path.getsize(w) > 0):
            hit("WAL.REFUSED")
            raise SystemExit("[WAL] REFUSED: %s is non-empty (%d bytes); immutable=1 would ignore it and silently omit "
                             "committed rows. Nothing is read; checkpoint happens only in the writer's process, never here."
                             % (w, os.path.getsize(w)))
    return [(p, wal_status(p)) for p in paths]


INPUT_DBS = lambda: (X12_CACHE, rj.EVAL_DB, r512.SNAP_DB)


def _rel(p):
    try:
        return os.path.relpath(p, ROOT)
    except ValueError:                                  # another drive (the selftest's tempdir on Windows)
        return p


def load_real(say):
    need(abs(rj.PRIOR - 0.5) < 1e-12, "rj.PRIOR is %r, the record pins 0.5" % rj.PRIOR)
    models = sorted(p8.ARENA12)
    need(EXCLUDE not in models and len(models) == 12, models)
    for p, st_ in check_wal(INPUT_DBS()):
        say("  read-only source %s (mode=ro&immutable=1): %s (a non-empty -wal refuses the run)" % (_rel(p), st_))
    _STACK_AUTH[0] = stack_uri(X12_CACHE)                # R3 (iii) as re-ruled: the ONE admitted open of the cache
    try:
        con = ro(X12_CACHE)
    finally:
        _STACK_AUTH[0] = None
    rows = [(mid, a, b, q, w) for mid, a, b, q, w, iv in
            con.execute("SELECT match_id, model_a, model_b, qid, winner, invalid FROM verdicts") if not iv]
    con.close()
    need(not any(EXCLUDE in (r[1], r[2]) for r in rows), EXCLUDE)
    ev = ro(rj.EVAL_DB)
    K = defaultdict(dict); P1 = defaultdict(dict); Praw = defaultdict(dict)
    for q, m, pr_, c in ev.execute("SELECT question_id, model_name, pred, is_correct FROM eval_results"):
        if m in p8.ARENA12:
            K[q][m] = int(c or 0); P1[q][m] = (pr_ or "").strip().upper()[:1]; Praw[q][m] = pr_
    pool = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id = ?", (POOL,))}
    ev.close()
    route = r512.primary_routing(TREE)
    snap = r512.snapshot_id(TREE)
    sc = ro(r512.SNAP_DB)
    g = json.loads(sc.execute("SELECT graph FROM snapshots WHERE id=?", (snap,)).fetchone()[0])
    sc.close()
    lst = g["nodes"]; lst = lst if isinstance(lst, list) else list(lst.values())      # r512.load_graph's parse
    anchor_of = r512.anchor_fn({n["id"]: n for n in lst})
    anchor_q = {q: anchor_of(route[q]) for q in route}
    say("  routing %s: %d routed questions; pool %s: %d ids; routed set == pool: %s"
        % (TREE, len(route), POOL, len(pool), "yes" if set(route) == pool else "NO (eval side = pool AND routed)"))
    return dict(models=models, rows=rows, K=K, P1=P1, Praw=Praw, anchor_q=anchor_q, pool=pool)


# ------------------------------------------------------------------------------------------ the filter (no key read)
def apply_filter(rows, Praw):
    """Per row: AGREE / DISAGREE / UNDETERMINED on the shipped rule. Convention A keeps every row that is not AGREE
    (missing prediction KEPT); convention B keeps DISAGREE, base = rows with both predictions present."""
    keepA, keepB, missing = set(), set(), set()
    n = len(rows); agree = dis = und = 0
    for mid, a, b, q, _ in rows:
        v = FILTER_VERDICT(Praw.get(q, {}).get(a), Praw.get(q, {}).get(b))
        if v == "AGREE":
            agree += 1
        elif v == "DISAGREE":
            dis += 1; keepA.add(mid); keepB.add(mid)
        else:
            und += 1; keepA.add(mid); missing.add(mid)
    return keepA, keepB, dict(n=n, agree=agree, disagree=dis, undetermined=und, keptA=len(keepA), keptB=len(keepB),
                             baseB=agree + dis, missing=missing)


# ------------------------------------------------------------------------------------------ the arm boards
def connected(rs, nodes):
    """Is the comparison graph on `nodes` (pairs with >= 1 row in rs) connected?"""
    nodes = sorted(nodes)
    if len(nodes) <= 1:
        return True
    par = {m: m for m in nodes}

    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    for r in rs:
        a, b = r[-4], r[-3]
        if a in par and b in par:
            par[f(a)] = f(b)
    return len({f(m) for m in nodes}) == 1


def _votes(rs):
    return [(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0) for a, b, _, w in rs]


def arm_edges(by_anchor, anchors, models, K=None, P1=None, u_edges=None, B=BOOT_B, seed=42):
    """COPY of systematic_budget.build()'s per-anchor loop (LF source pinned by BUILD_SRC_SHA16; bit-identity with the
    real build() is asserted by --selftest). by_anchor[anc] = [(a, b, q, w)] in U order.

    Discovery mode (u_edges None, U only): returns build()'s edge dicts exactly (plus key_ab = la[a] > la[b]).
    Fixed mode (an arm): for every U edge returns (p, m, s) from the arm's 300 boards, and the point-fit difference."""
    rng = random.Random(seed)                        # same seed and draw order as systematic_budget.build
    anchor_qs = {}
    edges = [] if u_edges is None else {}
    point = {}
    for anc in anchors:
        rs = by_anchor.get(anc, [])
        qs = sorted({q for _, _, q, _ in rs})
        anchor_qs[anc] = qs
        byq = defaultdict(list)
        for r in rs:
            byq[r[2]].append(r)
        draws = []
        if qs:
            for _ in range(B):
                pick = [qs[rng.randrange(len(qs))] for _ in qs]
                sub = [r for q in pick for r in byq[q]]
                draws.append(jf.board_from([(a, b, 0.5 if w == "TIE" else (1.0 if w == a else 0.0), 1.0)
                                            for a, b, _, w in sub], models))
        th = jf.board_from(_votes(rs), models) if rs else {m: 0.0 for m in models}
        if u_edges is None:
            la = {}
            for m in models:
                v = [K[q].get(m) for q in qs if K[q].get(m) is not None]
                if v:
                    la[m] = sum(v) / len(v)
            for i, a in enumerate(models):
                for b in models[i + 1:]:
                    if a not in la or b not in la:
                        continue
                    gap = abs(la[a] - la[b])
                    if gap == 0:
                        continue
                    d = np.array([dr[a] - dr[b] for dr in draws])
                    p = float((d > 0).mean())
                    both = [q for q in qs if P1[q].get(a) and P1[q].get(b)]
                    if not both:
                        continue
                    agree = sum(1 for q in both if P1[q][a] == P1[q][b]) / len(both)
                    edges.append(dict(anchor=anc, a=a, b=b, p=p, m=float(d.mean()), s=float(d.std(ddof=1)),
                                      right=((p > 0.5) == (la[a] > la[b])), agree=agree, gap=gap, n=len(both),
                                      key_ab=(la[a] > la[b]), pt=th[a] - th[b]))
        else:
            for e in u_edges.get(anc, []):
                a, b = e[0], e[1]
                if draws:
                    d = np.array([dr[a] - dr[b] for dr in draws])
                    edges[(anc, a, b)] = (float((d > 0).mean()), float(d.mean()), float(d.std(ddof=1)), th[a] - th[b])
                else:
                    edges[(anc, a, b)] = (0.5, 0.0, float("nan"), 0.0)
    return edges, anchor_qs


def _arm_job(job):
    """Top-level worker (spawn-safe): one arm, fixed mode."""
    name, by_anchor, anchors, models, u_edges, B = job
    t0 = time.time()
    edges, _ = arm_edges(by_anchor, anchors, models, u_edges=u_edges, B=B)
    return name, edges, time.time() - t0


def r_draw(u_cells, f_counts, k):
    """Random same-size control, draw k: per cell (sorted), EXACTLY F's kept count, Random(1000 + k)."""
    rng = random.Random(R_SEED0 + k)
    keep = set()
    for key in sorted(u_cells):
        n = f_counts.get(key, 0)
        if n:
            keep.update(r[0] for r in rng.sample(u_cells[key], n))
    return keep


def check_b_universe(keep, missing, k):
    """Registrar's R6: convention B's R may never hold a missing-prediction row (B's F cannot select one)."""
    bad = keep & missing
    if bad:
        hit("G3.REFUSED")
        raise SystemExit("[G3] REFUSED: convention B's R draw %d contains %d missing-prediction rows (R6)" % (k, len(bad)))


def cell_key(anc, a, b):
    return (anc, a, b) if a < b else (anc, b, a)


def check_g3(u_cells, f_counts, keep, k, conv):
    got = defaultdict(int)
    for key, rs in u_cells.items():
        for r in rs:
            if r[0] in keep:
                got[key] += 1
    bad = [key for key in set(u_cells) | set(f_counts) if got.get(key, 0) != f_counts.get(key, 0)]
    if bad:
        hit("G3.REFUSED")
        raise SystemExit("[G3] REFUSED: R draw %d (convention %s) differs from F's kept count in %d cell(s), first %s"
                         % (k, conv, len(bad), sorted(bad)[:3]))


# ------------------------------------------------------------------------------------------ the pipeline
def prepare(D, say, pins=PINS, B=BOOT_B):
    """U (discovery), the filter, F and R row sets, gates G1-G3. Returns the prepared state."""
    models = D["models"]
    rows = D["rows"]
    keepA, keepB, fc = apply_filter(rows, D["Praw"])
    say("")
    say("--- THE FILTER (the shipped MatchFilter.kt rule, profile_r_filtered.verdict; NO key read) ---")
    hit("CONV.IN_FORCE")
    say("  CONVENTION IN FORCE: A (the deployed filter; a missing prediction is KEPT). Convention B (missing dropped) is run")
    say("  beside in full and DECIDES NOTHING.")
    say("  valid x12 verdicts %d: AGREE %d | DISAGREE %d | UNDETERMINED (missing prediction) %d"
        % (fc["n"], fc["agree"], fc["disagree"], fc["undetermined"]))
    say("  convention A kept %d of %d = %.1f%% | convention B kept %d of %d (both predictions present) = %.1f%%"
        % (fc["keptA"], fc["n"], 100.0 * fc["keptA"] / max(1, fc["n"]), fc["keptB"], fc["baseB"],
           100.0 * fc["keptB"] / max(1, fc["baseB"])))
    g2 = bool(fc["n"] == pins["n"] and fc["keptA"] == pins["keptA"] and fc["keptB"] == pins["keptB"] and fc["baseB"] == pins["baseB"])
    say("  G2 (filter counts reproduce %d of %d (A) and %d of %d (B)): %s"
        % (pins["keptA"], pins["n"], pins["keptB"], pins["baseB"], "PASS" if g2 else "FAIL"))
    if not g2:
        hit("G2.REFUSED")
        raise SystemExit("[G2] REFUSED: filter counts %s differ from the pins %s"
                         % ({k: v for k, v in fc.items() if k != "missing"}, pins))

    by_all = defaultdict(list)
    for r in rows:
        if r[3] in D["anchor_q"]:
            by_all[D["anchor_q"][r[3]]].append(r)
    anchors = sorted(a for a in by_all if len(by_all[a]) >= ANCHOR_FLOOR)
    u_rows = {a: by_all[a] for a in anchors}
    n_arm = sum(len(v) for v in u_rows.values())
    say("  rows in the arms (routed, in U's %d anchors of >= %d rows): %d of %d" % (len(anchors), ANCHOR_FLOOR, n_arm, len(rows)))

    t0 = time.time()
    u_edges, u_aq = arm_edges({a: [r[1:] for r in u_rows[a]] for a in anchors}, anchors, models, K=D["K"], P1=D["P1"], B=B)
    t_u = time.time() - t0
    est = sb.established(u_edges, D["K"], u_aq)
    est_keys = {(e["anchor"], e["a"], e["b"]) for e in est}
    wrong_est_u = sum(1 for e in est if not e["right"])
    g1 = bool(len(u_edges) == pins["edges"] and len(est) == pins["established"] and wrong_est_u == pins["wrong_est"])
    say("")
    say("--- G1: U reproduces the record (systematic_budget.build's edge object via the pinned copy) ---")
    say("  U: %d edges (pin %d), %d established by exact McNemar p < 0.05 on the anchor's JUDGED questions (pin %d), %d of"
        " them against the key (pin %d): %s" % (len(u_edges), pins["edges"], len(est), pins["established"], wrong_est_u,
                                                pins["wrong_est"], "PASS" if g1 else "FAIL"))
    say("  (one arm build = %d anchors x %d question-bootstrap boards: %.1f s wall)" % (len(anchors), B, t_u))
    if not g1:
        hit("G1.REFUSED")
        raise SystemExit("[G1] REFUSED: U does not reproduce 920 / 809 / 26")

    u_cells = defaultdict(list)
    for anc in anchors:
        for r in u_rows[anc]:
            u_cells[cell_key(anc, r[1], r[2])].append(r)
    # R's universe per convention (registrar's R6): A draws from U's cells; B draws from U's cells MINUS the
    # missing-prediction rows, the only universe B's F can select from (base 8,352 of 9,142).
    universe = {"A": dict(u_cells),
                "B": {key: [r for r in rs if r[0] not in fc["missing"]] for key, rs in u_cells.items()}}
    conv = {}
    for cname, keep in (("A", keepA), ("B", keepB)):
        cells = universe[cname]
        f_counts = {key: sum(1 for r in rs if r[0] in keep) for key, rs in u_cells.items()}
        f_counts = {k_: v for k_, v in f_counts.items() if v}
        draws = []
        for k in range(1, K_DRAWS + 1):
            kk = r_draw(cells, f_counts, k)
            check_g3(cells, f_counts, kk, k, cname)
            if cname == "B":
                check_b_universe(kk, fc["missing"], k)
            draws.append(kk)
        conv[cname] = dict(keep=keep, f_counts=f_counts, draws=draws, universe=cells)
    nB = sum(len(v) for v in universe["B"].values())
    say("  R universe: convention A = U's cells (%d rows); convention B = U's cells minus the %d missing-prediction rows"
        " (%d rows; ruling R6)" % (sum(len(v) for v in u_cells.values()), sum(len(v) for v in u_cells.values()) - nB, nB))
    say("  G3 (every R draw has exactly F's kept count in every (anchor, pair) cell, drawn from its convention's universe;"
        " %d draws x 2 conventions): PASS" % K_DRAWS)
    return dict(models=models, anchors=anchors, u_rows=u_rows, u_edges=u_edges, u_aq=u_aq, est_keys=est_keys,
                fc=fc, conv=conv, missing=fc["missing"], u_cells=u_cells, t_u=t_u, B=B, K=D["K"], P1=D["P1"], anchor_q=D["anchor_q"], pool=D["pool"])


def per_anchor_counts(S, say):
    say("")
    say("--- PER ANCHOR: kept matches under A and B, edges, established edges (U's key denominator = judged questions) ---")
    say("  %-20s %6s %7s %7s %6s %6s %6s %6s" % ("anchor", "U", "kept A", "kept B", "edges", "estab", "wrongU", "q_jdg"))
    for anc in S["anchors"]:
        ne = [e for e in S["u_edges"] if e["anchor"] == anc]
        nest = [e for e in ne if (anc, e["a"], e["b"]) in S["est_keys"]]
        ka = sum(1 for r in S["u_rows"][anc] if r[0] in S["conv"]["A"]["keep"])
        kb = sum(1 for r in S["u_rows"][anc] if r[0] in S["conv"]["B"]["keep"])
        say("  %-20s %6d %7d %7d %6d %6d %6d %6d" % (anc[:20], len(S["u_rows"][anc]), ka, kb, len(ne), len(nest),
                                                    sum(1 for e in nest if not e["right"]), len(S["u_aq"][anc])))
    sizes = [sum(1 for e in S["u_edges"] if e["anchor"] == anc and (anc, e["a"], e["b"]) in S["est_keys"]) for anc in S["anchors"]]
    tot = sum(sizes)
    say("  established edges per anchor: %s; arithmetic mean %.2f (= %d / %d; registration (a) 57.8); Kish mean cluster size"
        " sum n^2 / sum n = %.2f" % ("/".join(str(s) for s in sizes), tot / max(1, len(sizes)), tot, len(sizes),
                                     sum(s * s for s in sizes) / max(1, tot)))


def run_arms(S, workers, say, B=None):
    B = B or S["B"]
    anchors = S["anchors"]; models = S["models"]
    u_min = defaultdict(list)
    for e in S["u_edges"]:
        u_min[e["anchor"]].append((e["a"], e["b"]))
    jobs = []
    for cname in ("A", "B"):
        cv = S["conv"][cname]
        sets = [("F_" + cname, cv["keep"])] + [("R_%s_%02d" % (cname, k + 1), d) for k, d in enumerate(cv["draws"])]
        for name, keep in sets:
            by = {a: [r[1:] for r in S["u_rows"][a] if r[0] in keep] for a in anchors}
            jobs.append((name, by, anchors, models, dict(u_min), B))
    out = {}
    t0 = time.time()
    if workers > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=workers) as ex:
            for name, edges, dt in ex.map(_arm_job, jobs):
                out[name] = edges
                print("    arm %-8s %6.1f s (elapsed %.0f s)" % (name, dt, time.time() - t0), file=sys.stderr, flush=True)
    else:
        for j in jobs:
            name, edges, dt = _arm_job(j)
            out[name] = edges
            print("    arm %-8s %6.1f s (elapsed %.0f s)" % (name, dt, time.time() - t0), file=sys.stderr, flush=True)
    say("  %d arm boards built (F and %d R draws per convention) in %.0f s wall, %d worker(s)" % (len(jobs), K_DRAWS, time.time() - t0, workers))
    return out


# ------------------------------------------------------------------------------------------ readout functions (pure)
TRIGGER_C1 = "UNDETERMINED BY TRIGGER: SUPPORT"


def c1_verdict(n_remaining, lo, hi, min_anchors=C1_MIN_ANCHORS):
    """The registered trigger FIRST (ruling R2 (b): fewer than 12 of the 14 anchors remain in C1's denominator), then the
    interval against the bar 0 with its three disjoint outcomes."""
    if n_remaining < min_anchors:
        return TRIGGER_C1
    if bool(hi < 0):
        return "HELD"
    if bool(lo > 0):
        return "FAILED"
    return "UNDETERMINED"


def c1_stats(anchors_conn, est_by_anchor, wrongF, wrongR, B=CLUSTER_B, seed=CLUSTER_SEED):
    K = len(next(iter(wrongR.values()))) if wrongR else K_DRAWS
    d_a = []; WF = 0; WR = np.zeros(K); d_e = []; paired_fw = paired_rw = 0; nedges = 0
    for anc in anchors_conn:
        keys = est_by_anchor.get(anc, [])
        wf = sum(1 for k in keys if wrongF[k])
        wr = np.array([sum(1 for k in keys if wrongR[k][j]) for j in range(K)], dtype=float)
        d_a.append(wf - wr.mean()); WF += wf; WR += wr; nedges += len(keys)
        for k in keys:
            pr_ = sum(wrongR[k]) / K
            d_e.append((1.0 if wrongF[k] else 0.0) - pr_)
            maj = sum(wrongR[k]) > K / 2
            if wrongF[k] and not maj:
                paired_fw += 1
            if (not wrongF[k]) and maj:
                paired_rw += 1
    d_a = np.array(d_a, dtype=float)
    delta = float(d_a.sum())
    n = len(d_a)
    if n >= 2:
        rng = np.random.default_rng(seed)
        boots = np.array([d_a[rng.integers(0, n, n)].sum() for _ in range(B)])
        se = float(boots.std(ddof=1)); plo, phi = float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))
    else:
        se = float("nan"); plo = phi = float("nan")
    lo, hi = delta - Z * se, delta + Z * se
    se_iid = math.sqrt(sum(x * x for x in d_e))
    deff = (se * se) / (se_iid * se_iid) if se_iid > 0 and se == se else float("nan")
    return dict(delta=delta, d_a=d_a, WF=WF, WR_mean=float(WR.mean()), WR_draws=WR, se=se, lo=lo, hi=hi, plo=plo, phi=phi,
                se_iid=se_iid, deff=deff, n_eff=(nedges / deff) if deff == deff and deff > 0 else float("nan"),
                mde=MDE_K * se if se == se else float("nan"), n_edges=nedges, n_anchors=n,
                boundary=sum(1 for x in d_e if abs(x) > 1e-12), paired_fw=paired_fw, paired_rw=paired_rw)


def support_lines(say, st):
    say("  SUPPORT (registration (a)-(f); measured beside planned): edges %d in %d anchor clusters; boundary edges (d_e != 0) %d;"
        % (st["n_edges"], st["n_anchors"], st["boundary"]))
    say("    SE_iid = sqrt(sum d_e^2) = %.3f (planned 4.24) | cluster-bootstrap SE = %.3f | MEASURED DEFF = %s (planned 1.6,"
        " pessimistic 3.0) | n_eff = %s | MDE (2.80 x SE) = %s edges (planned 15.0; pessimistic 20.6)"
        % (st["se_iid"], st["se"], "%.3f" % st["deff"] if st["deff"] == st["deff"] else "undefined",
           "%.1f" % st["n_eff"] if st["n_eff"] == st["n_eff"] else "undefined",
           "%.2f" % st["mde"] if st["mde"] == st["mde"] else "undefined"))
    if not bool(st["deff"] == st["deff"]):
        hit("SUPPORT.DEFF_UNDEFINED")
        say("    DEFF UNDEFINED (SE_iid = 0 or fewer than 2 clusters): no boundary edge carries variance; the design effect")
        say("    cannot be measured on this object and the registered planning values are the only support statement.")
        return
    be_meas = (abs(PLAN["pred_delta"]) / (MDE_K * st["se_iid"])) ** 2 if st["se_iid"] > 0 else float("inf")
    if bool(st["deff"] > PLAN["break_even"]):
        hit("SUPPORT.UNDERPOWERED")
        say("    UNDERPOWERED FOR ITS OWN BAR: the measured DEFF %.3f exceeds the registered break-even DEFF 1.82 (at the"
            % st["deff"])
        say("    measured SE_iid the break-even is %.3f); the MDE %.2f edges against the predicted |Delta_W| 16 makes an"
            % (be_meas, st["mde"]))
        say("    UNDETERMINED by interval likely even if the prediction is right.")
    else:
        hit("SUPPORT.WITHIN_BREAK_EVEN")
        say("    measured DEFF %.3f is within the registered break-even 1.82 (break-even at the measured SE_iid: %.3f);"
            " MDE %.2f edges vs the predicted |Delta_W| 16." % (st["deff"], be_meas, st["mde"]))


def c1_lines(say, st, verdict, label="C1", decides=True):
    tag = "" if decides else " [CONVENTION B: DECIDES NOTHING]"
    say("  %s%s: Delta_W = W_F - mean W_R = %d - %.2f = %+.2f over %d established edges in %d remaining anchors"
        % (label, tag, st["WF"], st["WR_mean"], st["delta"], st["n_edges"], st["n_anchors"]))
    say("    DECIDING STATISTIC: %d-anchor cluster-bootstrap interval (anchors resampled whole; B %d, numpy seed %d; point +- 1.96"
        " x SE): [%+.2f, %+.2f] (SE %.3f) | percentile [%+.2f, %+.2f] (decides nothing)"
        % (st["n_anchors"], CLUSTER_B, CLUSTER_SEED, st["lo"], st["hi"], st["se"], st["plo"], st["phi"]))
    say("    edge-level paired counts (decide nothing): wrong in F and NOT in the R majority %d | right in F and wrong in the R"
        " majority %d | per-anchor d_a %s" % (st["paired_fw"], st["paired_rw"], " ".join("%+.2f" % x for x in st["d_a"])))
    say("    [support beside the deciding statistic: MEASURED DEFF %s, n_eff %s, MDE %s edges; planned DEFF 1.6, MDE 15.0]"
        % ("%.3f" % st["deff"] if st["deff"] == st["deff"] else "undefined",
           "%.1f" % st["n_eff"] if st["n_eff"] == st["n_eff"] else "undefined",
           "%.2f" % st["mde"] if st["mde"] == st["mde"] else "undefined"))
    if not decides:
        hit("CONV.B_BESIDE")
        say("    -> convention B reads %s; it decides nothing." % verdict)
        return
    if verdict == TRIGGER_C1:
        hit("C1.TRIGGER")
        say("    -> C1 UNDETERMINED (BY TRIGGER: SUPPORT): %d of the U anchors remain in C1's denominator, fewer than %d"
            % (st["n_anchors"], C1_MIN_ANCHORS))
        say("       (registrar's ruling R2 (b), evaluated FIRST under the standing rule 7da2ec5). The interval above is PRINTED,")
        say("       NOT SCORED; the falsifier is NOT evaluated.")
        return
    hit("C1.TRIGGER_NOT_FIRED")
    say("    support trigger (R2 (b)): %d anchors remain >= %d: not fired; the interval is scored."
        % (st["n_anchors"], C1_MIN_ANCHORS))
    if verdict == "HELD":
        hit("C1.HELD")
        say("    -> C1 HELD: the interval lies wholly BELOW 0. The filter's selection moves established edges TOWARD the key")
        say("       relative to random selection at equal support: no adverse selection bias.")
    elif verdict == "FAILED":
        hit("C1.FAILED")
        say("    -> C1 FAILED (ADVERSE): the interval lies wholly ABOVE 0. The filter points established edges against the key")
        say("       more often than random selection at the same support.")
    else:
        hit("C1.UNDETERMINED")
        say("    -> C1 UNDETERMINED: the interval contains 0.")


def falsifier_lines(say, verdict, st):
    say("")
    say("=== FALSIFIER ===")
    if verdict == TRIGGER_C1:
        hit("FALSIFIER.NOT_EVALUATED")
        say("  NOT EVALUATED: C1 is UNDETERMINED (BY TRIGGER: SUPPORT). The L95 precondition stays UNMET; the removed anchors")
        say("  (C4) are the finding about the density the filter leaves at deployment.")
    elif verdict == "FAILED":
        hit("FALSIFIER.FIRED")
        say("  FIRED: C1 FAILED overturns FILTER-BOARD's \"strictly safe\" AT THE CERTIFICATE LEVEL (its board rho and top-4")
        say("  readout stand) and FORBIDS making the filtered schedule the default under the current widener parameters; to be")
        say("  bracketed into FRAMEWORK L95 and the MATCH-FILTER row.")
    elif verdict == "HELD":
        hit("FALSIFIER.DISCHARGE")
        say("  NOT FIRED. C1 HELD DISCHARGES THE L95 PRECONDITION ON DIRECTION ONLY, bracketed as such: the safety leg (C2) and")
        say("  b1 (C3) stay DESCRIPTIVE, so the discharge is partial by registration, and making the filtered schedule the")
        say("  default remains the author's decision.")
    else:
        hit("FALSIFIER.UNMET")
        say("  NOT FIRED. C1 UNDETERMINED leaves the L95 precondition UNMET, recorded with the measured DEFF %s and MDE %s edges."
            % ("%.3f" % st["deff"] if st["deff"] == st["deff"] else "undefined",
               "%.2f" % st["mde"] if st["mde"] == st["mde"] else "undefined"))
    say("  NOT OVERTURNED in any branch: PROFILE-R-FILTERED's reliability numbers, A-REDEFINE-REFIT's consistency PASS,")
    say("  UNFILTERED-ADOPT's criteria, the board of record, any published edge.")


def c2_line(say, label, called, wrong, wrong_est, nominal, word=True):
    s = "  %-44s called %4d | wrong(established) %d(%d) | nominal sum(1 - c~) %.2f" % (label, called, wrong, wrong_est, nominal)
    if word:
        w = status_word(nominal, wrong)
        if w.startswith("UNDETERMINED (nominal < 3)"):
            hit("C2.STATUS.LT3")
        elif w.startswith("UNDETERMINED (power"):
            hit("C2.STATUS.3TO9")
        else:
            hit("C2.STATUS.GE9")
        s += " | status (FRAMEWORK L101): %s" % w
    say(s)


def unidentified(es):
    """Registrar's ruling of 2026-09-23 (programme L13883-L13923): "b1 UNIDENTIFIED" is (QUASI-)COMPLETE SEPARATION of
    the wrong / right established edges in the widener's covariate A, checked DETERMINISTICALLY ON THE DATA BEFORE ANY
    FIT, never by a threshold on a fitted value. A_w = A of the wrong edges, A_r = A of the right edges; separation iff
    max(A_w) <= min(A_r) OR max(A_r) <= min(A_w) (equality at the boundary = quasi-complete, and counts). Zero wrong or
    zero right events are the same class. Returns the reason, or None when the ranges overlap."""
    aw = [float(e["agree"]) for e in es if not e["right"]]
    ar = [float(e["agree"]) for e in es if e["right"]]
    if not aw or not ar:
        hit("SEP.ZERO_EVENTS")
        return "zero %s events (%d wrong, %d right)" % ("wrong" if not aw else "right", len(aw), len(ar))
    tie = bool(max(aw) == min(ar)) or bool(max(ar) == min(aw))
    if bool(max(aw) <= min(ar)):
        hit("SEP.WRONG_BELOW_RIGHT")
        if tie:
            hit("SEP.QUASI_TIE")
        return "%sseparation in A: max A(wrong) %.4f <= min A(right) %.4f" % ("quasi-complete " if tie else "complete ",
                                                                              max(aw), min(ar))
    if bool(max(ar) <= min(aw)):
        hit("SEP.RIGHT_BELOW_WRONG")
        if tie:
            hit("SEP.QUASI_TIE")
        return "%sseparation in A: max A(right) %.4f <= min A(wrong) %.4f" % ("quasi-complete " if tie else "complete ",
                                                                              max(ar), min(aw))
    hit("SEP.OVERLAP")
    return None


INNER_SCAN_K = 31                  # plateau scan: b0_start +- 1e-3 x max(1, |b0_start|) x 2^k, k = 0..30, both sides


class InnerUnresolved(Exception):
    """A failed inner re-maximisation of b0: that fit reads NO FIT (ruling D2, 8bbe6ce); never a refusal of the run."""


def _brent(f, bracket, maxiter=INNER_MAXITER):
    from scipy.optimize import minimize_scalar
    try:
        return minimize_scalar(f, bracket=bracket, method="brent", options=dict(xtol=INNER_XTOL, maxiter=maxiter))
    except Exception as ex:
        return ex


def check_scipy_brent():
    """AT LAUNCH (beside the build() pin): scipy Brent's absolute floor is the documented INNER_MINTOL."""
    from scipy.optimize._optimize import Brent
    if not bool(Brent(lambda z: z)._mintol == INNER_MINTOL):
        raise SystemExit("[PIN] scipy's Brent absolute tolerance is not %g; the documented inner tolerance does not hold."
                         " Refused." % INNER_MINTOL)


def _inner_b0(A, M, S_, R, b1, b0_start):
    """The inner re-maximisation of the profile: min over b0 of the nll at fixed b1 (arr.vnll, the vectorised copy
    asserted equal to sb.nll at the optimum). Returns (l = -nll, b0, value-error estimate (DESCRIPTIVE), how), or raises
    InnerUnresolved(reason).

    (1) Brent (scipy minimize_scalar "brent"), its bracket search started at b0_start +- 1, xtol INNER_XTOL (relative)
        with Brent's absolute floor INNER_MINTOL, maxiter INNER_MAXITER. The value error is ESTIMATED at x by the Newton
        decrement g^2 / (2c), g the central first difference at step 6e-6 x max(1, |x|) (~eps^(1/3)), c the central
        second difference at step 1e-4 x max(1, |x|) (~eps^(1/4)); where c <= 0, |g| x 6e-6 x max(1, |x|). PRINTED AS
        DESCRIPTIVE beside every fit; NO check on it (ruling D5): the registered 16 already carries the 4x margin.
    (2) If Brent does not succeed from that bracket (scipy finds no valid bracket when the nll is flat, e.g. every tau at
        the exp(20) cap), the nll is scanned at b0_start and b0_start +- 1e-3 x max(1, |b0_start|) x 2^k, k = 0..30.
        The lowest scanned point (b0_start itself when nothing scanned is strictly lower): strictly below both scan
        neighbours -> Brent on that three-point bracket, as in (1); tied with a neighbour -> a PLATEAU, its value,
        estimate 0 at the scan's resolution.
    UNRESOLVED (ruling D2: that fit reads NO FIT): Brent not converged on the scan bracket; the scan's lowest point at
    the scan's end (no interior optimum); a non-finite value on the scan."""
    impl = _INNER_IMPL[0] or _inner_min
    return impl(lambda z: arr.vnll((z, b1), A, M, S_, R), b0_start, b1)


def _inner_min(f, b0_start, b1, maxiter=INNER_MAXITER):
    """The rule of _inner_b0 on any objective f(b0) (split out so the selftest executes every path on crafted f)."""

    def bounded(r, how):
        x = float(r.x); fx = float(r.fun)
        if not (bool(r.success) and bool(math.isfinite(x)) and bool(math.isfinite(fx))):
            hit("INNER.BRENT_NOT_CONVERGED")
            raise InnerUnresolved("Brent did not converge (%s; success %r, nit %r, x %r, at b1 %r)"
                                  % (how, r.success, getattr(r, "nit", None), x, b1))
        kg = 6e-6 * max(1.0, abs(x))               # ~ eps^(1/3): the central first difference's optimal step
        kc = 1e-4 * max(1.0, abs(x))               # ~ eps^(1/4): the central second difference's optimal step
        g = (f(x + kg) - f(x - kg)) / (2.0 * kg)
        c = (f(x + kc) - 2.0 * fx + f(x - kc)) / (kc * kc)
        est = (g * g / (2.0 * c)) if bool(c > 0) else abs(g) * kg
        return -fx, x, est, how

    r = _brent(f, (b0_start - 1.0, b0_start + 1.0), maxiter)
    if not isinstance(r, Exception) and bool(r.success):
        return bounded(r, "brent")
    step = 1e-3 * max(1.0, abs(b0_start))
    xs = sorted([b0_start] + [b0_start + sg * step * 2.0 ** k for sg in (-1.0, 1.0) for k in range(INNER_SCAN_K)])
    fs = [f(x) for x in xs]
    if not all(bool(math.isfinite(v)) for v in fs):
        hit("INNER.NONFINITE_SCAN")
        raise InnerUnresolved("non-finite nll on the plateau scan at b1 %r" % b1)
    i0 = xs.index(b0_start)
    i = i0 if not bool(min(fs) < fs[i0]) else fs.index(min(fs))     # the start point wins ties with the minimum
    if i == 0 or i == len(xs) - 1:
        hit("INNER.NO_INTERIOR")
        raise InnerUnresolved("no interior optimum: the nll keeps decreasing to the end of the scan (b0 %r, at b1 %r)"
                              % (xs[i], b1))
    if bool(fs[i - 1] > fs[i]) and bool(fs[i + 1] > fs[i]):
        r2 = _brent(f, (xs[i - 1], xs[i], xs[i + 1]), maxiter)
        if isinstance(r2, Exception):
            hit("INNER.BRENT_NOT_CONVERGED")
            raise InnerUnresolved("Brent on the scan bracket failed (%s: %s, at b1 %r)" % (type(r2).__name__, r2, b1))
        return bounded(r2, "scan+brent")
    INNER_PLATEAUS[0] += 1
    return -fs[i], xs[i], 0.0, "plateau"


def singular_information(I, h, l):
    """THE RULING'S TEST (programme L14034-L14069): singular iff I <= 0 OR I x h^2 <= 16 x eps x max(1, |l(b1*)|).
    Returns "I <= 0", "I h^2 <= 16 eps max(1,|l|)", NONFINITE_REASON (ruling D2: that fit reads NO FIT, never a
    refusal) or None (not singular). Pure: the witness counts assessments in observed_information, not here."""
    if not (bool(math.isfinite(I)) and bool(math.isfinite(l)) and bool(math.isfinite(h)) and bool(h > 0)):
        hit("SING.NONFINITE_I")
        return NONFINITE_REASON
    if bool(I <= 0.0):
        hit("SING.I_NONPOS")
        return "I <= 0"
    if bool(I * h * h <= SING_FACTOR * EPS64 * max(1.0, abs(l))):
        hit("SING.ROUNDOFF")
        return "I h^2 <= 16 eps max(1,|l|)"
    hit("SING.NONSINGULAR")
    return None


def observed_information(es, b0, b1):
    """I = -l''(b1*) by the central second difference, h = 1e-4 x max(1, |b1*|), l = the PROFILE log-likelihood (b0
    re-maximised at each of b1* - h, b1*, b1* + h, each inner search started at the optimiser's b0). b1* = the
    optimiser's b1. Returns every printed quantity and the ruling's classification."""
    A, M, S_, R = arr.vec(es)
    h = INFO_STEP_REL * max(1.0, abs(b1))
    SING_EVALS[0] += 1                                      # the witness: one assessment per fit, resolved or not
    nan = float("nan")
    try:
        lm, _, em, hm = _inner_b0(A, M, S_, R, b1 - h, b0)
        l0, b0hat, e0, h0 = _inner_b0(A, M, S_, R, b1, b0)
        lp, _, ep, hp = _inner_b0(A, M, S_, R, b1 + h, b0)
    except InnerUnresolved as ex:                           # ruling D2: THAT FIT reads NO FIT; the run goes on
        return dict(I=nan, h=h, l=nan, Ih2=nan, bound=nan, inner=nan, b0_profile=nan, singular=None,
                    inner_how="unresolved", unresolved=str(ex))
    I = -((lp - 2.0 * l0 + lm) / (h * h))
    scale = max(1.0, abs(l0))
    bound = SING_FACTOR * EPS64 * scale
    inner = 4.0 * max(em, e0, ep)                           # DESCRIPTIVE (ruling D5): printed, never checked
    sing = singular_information(I, h, l0)
    return dict(I=I, h=h, l=l0, Ih2=I * h * h, bound=bound, inner=inner, b0_profile=b0hat, singular=sing,
                inner_how="/".join((hm, h0, hp)), unresolved=None)


def info_line(info):
    if info.get("unresolved"):
        return ("observed information NOT COMPUTED | h %.6g | %s%s -> NO FIT (ruling D2)"
                % (info["h"], INNER_PREFIX, info["unresolved"]))
    return ("observed information I = -l''(b1*) = %.6g | h %.6g | l(b1*) %.10g | I h^2 %.4g vs bound 16 eps max(1,|l|)"
            " %.4g | inner b0 (%s), value-error estimate x4 %.2g (DESCRIPTIVE, no check) | -> %s"
            % (info["I"], info["h"], info["l"], info["Ih2"], info["bound"], info["inner_how"], info["inner"],
               ("NO FIT (%s)" % info["singular"]) if info["singular"] == NONFINITE_REASON else
               ("SINGULAR (%s)" % info["singular"]) if info["singular"] else "not singular"))


def c3_status(ddev, p_boot, unident=None):
    """NO trigger on C3 (ruling R1). "NO FIT (b1 unidentified: <reason>)" when the data are separated / have zero events
    (checked before any fit) or the delta-deviance is non-finite; otherwise A-REDEFINE-REFIT's reading of the two tests.
    Descriptive only."""
    if unident:
        return "NO FIT (b1 unidentified: %s)" % unident
    if not bool(ddev == ddev) or not bool(abs(ddev) < float("inf")):
        return "NO FIT (b1 unidentified: non-finite delta-deviance)"
    lr = bool(ddev >= 3.84); bt = bool(p_boot < 0.025)
    if lr and bt:
        return "REJECTED"
    if (not lr) and (not bt):
        return "NOT REJECTED"
    return "DISAGREE"


def c3_lines(say, label, events, n_edges, fit, pboots, status):
    say("  %-4s established edges %d, wrong-direction events %d | b0 %s b1 %s | profile delta-deviance %s (bar 3.84) | cluster"
        " P(b1 <= 0) %s" % (label, n_edges, events,
                            "%+.4f" % fit["b0"] if fit else "n/a", "%+.4f" % fit["b1"] if fit else "n/a",
                            "%.2f" % fit["ddev"] if fit else "n/a",
                            " / ".join("%.4f (%d reps, seed %d)" % (p, r, s_) for p, r, s_ in pboots) or "n/a"))
    if fit:
        if fit.get("info"):
            say("       |b1| %.4f | %s" % (abs(fit["b1"]), info_line(fit["info"])))
        else:
            say("       |b1| %.4f | observed information not computed (a crafted print test, not a fit)" % abs(fit["b1"]))
    if bool(events <= C3_EVENT_FLAG):
        hit("C3.FLAG_LE14")
        say("       descriptive flag (Support (g); ruling R1: NOT a trigger, decides nothing): %d <= %d events: b1 structurally"
            " unidentifiable at this event count (Support (g))" % (events, C3_EVENT_FLAG))
    if status.startswith("NO FIT"):
        hit("C3.NO_FIT")
        say("       -> %s: %s. Any b0 / b1 / delta-deviance printed above is what the optimiser returned: DESCRIPTIVE, it"
            " decides nothing (rulings of 2026-09-23, L13883 and L14034)." % (label, status))
    elif status == "REJECTED":
        hit("C3.REJECTED")
        say("       -> %s: b1 = 0 REJECTED by both tests (descriptive only)." % label)
    elif status == "NOT REJECTED":
        hit("C3.NOT_REJECTED")
        say("       -> %s: b1 = 0 NOT rejected by either test: UNDETERMINED (descriptive only)." % label)
    else:
        hit("C3.DISAGREE")
        say("       -> %s: UNDETERMINED (the two tests disagree; descriptive only)." % label)


def c4_lines(say, rows, disconnected, zero_total, n_edges, label="A", floored=()):
    say("  %-20s %12s %10s %10s" % ("anchor", "zero-kept", "kept rows", "connected"))
    for row in rows:
        anc, z, c = row[:3]; kr = row[3] if len(row) > 3 else -1
        say("  %-20s %12d %10d %10s%s" % (anc[:20], z, kr, "yes" if c else "NO",
                                          "   <- below the %d-row floor" % ANCHOR_FLOOR if anc in floored else ""))
    say("  convention %s: edges with ZERO kept matches %d of %d; anchors whose comparison graph DISCONNECTS: %d; anchors"
        " below build()'s %d-row floor: %d" % (label, zero_total, n_edges, len(disconnected), ANCHOR_FLOOR, len(floored)))
    if label != "A":
        return
    if floored:
        hit("C4.FLOOR_REMOVED")
        say("  -> BELOW THE %d-ROW FLOOR under the deployed filter: %s. Not refitted on another edge set (ruling R4): each"
            % (ANCHOR_FLOOR, ", ".join(floored)))
        say("     leaves the C1-C3 denominators and counts toward the support trigger (ruling R2 (a)).")
    if disconnected:
        hit("C4.DISCONNECTED")
        say("  -> DISCONNECTED under the deployed filter: %s. Each is UNDETERMINED BY CONSTRUCTION for C1-C3 (refused per"
            % ", ".join(disconnected))
        say("     Stage 5's disconnected-graph rule, FRAMEWORK L85); its edges left every denominator above. This is a finding")
        say("     about the density the filter leaves at deployment.")
    else:
        hit("C4.NONE_DISCONNECTED")
        say("  -> every anchor's comparison graph stays CONNECTED under the deployed filter.")


def score(say, pid, text, observed, cond):
    """cond: True -> HELD, False -> FAILED, None -> UNDETERMINED (only P5 may pass None: ruling R1 (b))."""
    if cond is None:
        need(pid == "P5", "only P5 may read UNDETERMINED, got %s" % pid)
        word = "UNDETERMINED"
    else:
        word = "HELD" if bool(cond) else "FAILED"
    hit("%s.%s" % (pid, word))
    say("  %s %-58s observed %-34s -> %s" % (pid, text, observed, word))
    return word


def predictions(say, c1v, st, p4, c3, c4):
    say("")
    say("=== PREDICTIONS (the registrar's), scored ===")
    score(say, "P1", "W_F = 14 [6, 22]", "W_F = %d" % st["WF"], 6 <= st["WF"] <= 22)
    score(say, "P2", "mean W_R = 30 [24, 38]", "mean W_R = %.2f" % st["WR_mean"], 24 <= st["WR_mean"] <= 38)
    score(say, "P3", "Delta_W = -16 [-26, -6], C1 HELD", "Delta_W = %+.2f, C1 %s" % (st["delta"], c1v),
          bool(-26 <= st["delta"] <= -6) and c1v == "HELD")
    score(say, "P4", "F W(W) at 0.975 in [0, 4] (pt 1), nominal in [1.0, 2.0]",
          "called %d, W(W) %d(%d), nom %.2f" % (p4[0], p4[1], p4[1], p4[2]), bool(0 <= p4[1] <= 4) and bool(1.0 <= p4[2] <= 2.0))
    ddev = c3["fit"]["ddev"] if c3["fit"] else float("nan")
    computed = (not c3["status"].startswith("NO FIT")) and bool(ddev == ddev) and bool(abs(ddev) < float("inf"))
    # ruling R1 (b) + the separation ruling (L13883): scored ONLY on a computed, IDENTIFIED delta-deviance; a NO FIT
    # (zero events, separation, non-finite) -> UNDETERMINED, never HELD; a returned ddev is then descriptive only
    score(say, "P5", "C3: delta-deviance < 3.84 (UNDETERMINED)",
          "ddev %s, C3 %s" % ("%.2f" % ddev if computed else ("%.2f descriptive" % ddev if ddev == ddev else "none"),
                              c3["status"].split(" (")[0]),
          bool(ddev < 3.84) if computed else None)
    score(say, "P6", "C4: 0 anchors disconnect; zero-kept edges 15 [5, 40]",
          "%d disconnect, %d zero-kept" % (c4[0], c4[1]), c4[0] == 0 and bool(5 <= c4[1] <= 40))


# ------------------------------------------------------------------------------------------ the full readout
def edge_objects(S, arm_edges_, keys, A_eval):
    """Certificate edge dicts for an arm: p, m, s from the arm; A = A_eval; direction against U's key."""
    out = []
    kab = {(e["anchor"], e["a"], e["b"]): e["key_ab"] for e in S["u_edges"]}
    for k in keys:
        p, m, s, pt = arm_edges_[k]
        out.append(dict(anchor=k[0], a=k[1], b=k[2], p=p, m=m, s=s, agree=A_eval[k], right=((p > 0.5) == kab[k])))
    return out


def wrong_maps(S, arm, keys):
    kab = {(e["anchor"], e["a"], e["b"]): e["key_ab"] for e in S["u_edges"]}
    wp = {k: ((arm[k][0] > 0.5) != kab[k]) for k in keys}
    wm = {k: ((arm[k][1] > 0) != kab[k]) for k in keys}
    wt = {k: ((arm[k][3] > 0) != kab[k]) for k in keys}
    ties = {k for k in keys if arm[k][0] == 0.5}
    return wp, wm, wt, ties


def c2_block(say, S, arms, conn_keys_est, conn_keys_all, A_eval, cname="A"):
    """Returns F's (called, W, W(E), nominal) for the primary pair under widener + decline."""
    p4 = None
    for plabel, (b0, b1) in PAIRS:
        say("  pair: %s b0 %+.4f b1 %+.4f, A = A_eval" % (plabel, b0, b1))
        for arm_name in ("U", "F_" + cname):
            arm = arms[arm_name]
            es = edge_objects(S, arm, conn_keys_est, A_eval)
            called = [e for e in es if sb.cbud(e, b0, b1) >= THRESH]
            w = sum(1 for e in called if not e["right"])
            nom = sum(1 - sb.cbud(e, b0, b1) for e in called)
            c2_line(say, "%s widener + decline" % arm_name, len(called), w, w, nom)
            if arm_name == "F_" + cname and plabel.endswith("(PRIMARY)"):
                p4 = (len(called), w, nom)
            ea = edge_objects(S, arm, conn_keys_all, A_eval)
            ca = [e for e in ea if sb.cbud(e, b0, b1) >= THRESH]
            wa = [e for e in ca if not e["right"]]
            c2_line(say, "%s widener only (all edges)" % arm_name, len(ca), len(wa),
                    len(sb.established(wa, S["K"], S["u_aq"])), sum(1 - sb.cbud(e, b0, b1) for e in ca), word=False)
        cs, ws, ns = [], [], []
        for k in range(1, K_DRAWS + 1):
            es = edge_objects(S, arms["R_%s_%02d" % (cname, k)], conn_keys_est, A_eval)
            called = [e for e in es if sb.cbud(e, b0, b1) >= THRESH]
            cs.append(len(called)); ws.append(sum(1 for e in called if not e["right"]))
            ns.append(sum(1 - sb.cbud(e, b0, b1) for e in called))
        say("  %-44s called %6.1f | wrong(established) %.2f(%.2f) | nominal %.2f   (mean over %d draws)"
            % ("R widener + decline", float(np.mean(cs)), float(np.mean(ws)), float(np.mean(ws)), float(np.mean(ns)), K_DRAWS))
    return p4


def c3_fit(es, reps=C3_REPS):
    """The separation check FIRST, on the data; then the optimiser (descriptive when unidentified) and, on EVERY fit,
    the observed information at the optimiser's b1 (the singular-information ruling, L14034-L14069); the cluster
    bootstrap only when identified (a bootstrap of a non-existent MLE is not read)."""
    C3_CALLS[0] += 1
    events = sum(1 for e in es if not e["right"])
    sep = unidentified(es)
    reason = sep
    fit = None; pboots = []; sing = None
    if 0 < events < len(es):
        fit = dict(arr.profile_lr(es))
        FIT_COUNT[0] += 1                                   # the witness, counted independently of observed_information
        A, M, S_, R = arr.vec(es)
        need(abs(arr.vnll((fit["b0"], fit["b1"]), A, M, S_, R) - sb.nll((fit["b0"], fit["b1"]), es)) < 1e-6,
             "vectorised nll differs from systematic_budget.nll at the optimum")
        fit["info"] = observed_information(es, fit["b0"], fit["b1"])
        sing = fit["info"]["singular"]
        if reason is None and fit["info"]["unresolved"]:
            reason = INNER_PREFIX + fit["info"]["unresolved"]
            hit("C3.NO_FIT_INNER")
        if reason is None and sing == NONFINITE_REASON:
            reason = NONFINITE_REASON
            hit("C3.NO_FIT_NONFINITE_I")
        if reason is None and sing is not None:
            reason = SING_REASON
            hit("C3.NO_FIT_SINGULAR")
        if reason is None:
            for nrep, seed in reps:
                _, b1s, _ = arr.cluster_boot(es, reps=nrep, seed=seed)
                pboots.append((float((b1s <= 0).mean()) if len(b1s) else float("nan"), nrep, seed))
    p_first = pboots[0][0] if pboots else float("nan")
    status = c3_status(fit["ddev"] if fit else float("nan"), p_first, unident=reason)
    branch = ("ZERO_EVENTS" if sep and sep.startswith("zero") else "SEPARATION" if sep else
              "SINGULAR" if reason == SING_REASON else
              "INNER_UNRESOLVED" if (reason or "").startswith(INNER_PREFIX) else
              "NONFINITE_I" if reason == NONFINITE_REASON else
              "NON_FINITE" if status.startswith("NO FIT") else "IDENTIFIED")
    return dict(events=events, fit=fit, pboots=pboots, status=status, reason=reason, n=len(es), sep=sep, sing=sing,
                branch=branch, es=es)


def c3_block(say, S, arm, keys_est, A_eval, label, reps=C3_REPS):
    r = c3_fit(edge_objects(S, arm, keys_est, A_eval), reps=reps)
    c3_lines(say, label, r["events"], r["n"], r["fit"], r["pboots"], r["status"])
    return r


def c3_identification_summary(say, S, arms, keys_est, A_eval, cname):
    """The same definition on every R draw (rulings L13883 and L14034: every arm, each convention): the data check,
    then the optimiser and the observed information on every draw with a fit (no bootstrap). Descriptive only."""
    cats = defaultdict(int)
    for k in range(1, K_DRAWS + 1):
        r = c3_fit(edge_objects(S, arms["R_%s_%02d" % (cname, k)], keys_est, A_eval), reps=())
        cats[r["branch"]] += 1
        if r["fit"]:
            say("    R_%s_%02d: b1 %+.4f ddev %.3f | %s | %s" % (cname, k, r["fit"]["b1"], r["fit"]["ddev"],
                                                             info_line(r["fit"]["info"]), r["status"]))
        else:
            say("    R_%s_%02d: no fit | %s" % (cname, k, r["status"]))
    say("  R_%s draws, b1 identification by the same definition (separation / zero events on the data, then singular"
        " observed information on the fit): %s" % (cname, " | ".join("%s %d" % kv for kv in sorted(cats.items()))))


def a_eval_map(S):
    qs_eval = defaultdict(list)
    for q in sorted(S["pool"]):
        if q in S["anchor_q"]:
            qs_eval[S["anchor_q"][q]].append(q)
    out = {}
    for e in S["u_edges"]:
        v, n = arr.agreement(S["P1"], qs_eval[e["anchor"]], e["a"], e["b"])
        need(v is not None, "no eval-side question with both predictions for %s" % ((e["anchor"], e["a"], e["b"]),))
        out[(e["anchor"], e["a"], e["b"])] = v
    return out


def reproduction_lines(say, S, A_eval, loao=True):
    say("")
    say("=== REPRODUCTION LINES on U (the record; NOT gates, decide nothing) ===")
    ue = S["u_edges"]
    filt = [e for e in ue if e["gap"] >= GAP]
    wu_all = [e for e in ue if not e["right"]]; wu_f = [e for e in filt if not e["right"]]
    say("  920-set wrong(established) %d(%d) (record %d all-label) | gap >= 0.02 set %d edges / wrong(established) %d(%d)"
        " (record %d / %d all-label)" % (len(wu_all), len(sb.established(wu_all, S["K"], S["u_aq"])), REPRO["all_wrong"],
                                         len(filt), len(wu_f), len(sb.established(wu_f, S["K"], S["u_aq"])),
                                         REPRO["filt_edges"], REPRO["filt_wrong"]))
    fe = [dict(e, agree=A_eval[(e["anchor"], e["a"], e["b"])]) for e in filt]
    f0, f1 = sb.fit(fe)
    say("  eval-A refit on the gap >= 0.02 set: b0 %+.4f b1 %+.4f (record %+.4f / %+.4f)" % (f0, f1, REPRO["eval891"][0], REPRO["eval891"][1]))
    called = [e for e in ue if sb.cbud(e, *PAIR_920) >= THRESH]
    wr = [e for e in called if not e["right"]]
    say("  920 pair, judged A, in sample on 920: %d / %d(%d) (record %d / %d(%d))"
        % (len(called), len(wr), len(sb.established(wr, S["K"], S["u_aq"])), *U_REF["insample"]))
    if loao:
        oof, _ = arr.loao(ue, PAIR_920)
        lc = [e for e in ue if oof[id(e)] >= THRESH]
        lw = [e for e in lc if not e["right"]]
        say("  920 set, judged A, LEAVE-ONE-ANCHOR-OUT: %d / %d(%d), nominal %.2f (record %d / %d(%d), %.2f)"
            % (len(lc), len(lw), len(sb.established(lw, S["K"], S["u_aq"])), sum(1 - oof[id(e)] for e in lc), *U_REF["loao"]))


def readout(S, arms, say, c3_reps=C3_REPS, loao=True, min_anchors=C1_MIN_ANCHORS):
    A_eval = a_eval_map(S)
    est_by_anchor = defaultdict(list)
    for e in S["u_edges"]:
        k = (e["anchor"], e["a"], e["b"])
        if k in S["est_keys"]:
            est_by_anchor[e["anchor"]].append(k)
    all_by_anchor = defaultdict(list)
    for e in S["u_edges"]:
        all_by_anchor[e["anchor"]].append((e["anchor"], e["a"], e["b"]))

    # ---- C4 first: it defines the denominators of C1-C3
    say("")
    say("=== C4: DENSITY under the filter (printed, no bar; it defines the C1-C3 denominators) ===")
    say("  An anchor LEAVES the C1-C3 denominators if its comparison graph disconnects under the convention's arms, or if")
    say("  its kept rows fall below build()'s %d-row floor (ruling R2 (a); R has F's per-cell counts by G3, so F and every R"
        % ANCHOR_FLOOR)
    say("  draw of a convention agree on both). C1 is UNDETERMINED (BY TRIGGER: SUPPORT) iff fewer than %d anchors remain." % min_anchors)
    conn = {}; c4_summary = None
    for cname in ("A", "B"):
        fcnt = S["conv"][cname]["f_counts"]
        rows = []; disc = []; floored = []; zero = 0
        for anc in S["anchors"]:
            z = sum(1 for k in all_by_anchor[anc] if fcnt.get(cell_key(*k), 0) == 0)
            nodes = {m for r in S["u_rows"][anc] for m in (r[1], r[2])}
            kept = [r for r in S["u_rows"][anc] if r[0] in S["conv"][cname]["keep"]]
            c = connected(kept, nodes)
            rows.append((anc, z, c, len(kept))); zero += z
            if not c:
                disc.append(anc)
            if bool(len(kept) < ANCHOR_FLOOR):
                floored.append(anc)
            conn[(cname, anc)] = bool(c) and not bool(len(kept) < ANCHOR_FLOOR)
        c4_lines(say, rows, disc, zero, len(S["u_edges"]), label=cname, floored=floored)
        removed = [a for a in S["anchors"] if not conn[(cname, a)]]
        say("  convention %s: anchors REMOVED from C1-C3: %d (%s); remaining %d of %d"
            % (cname, len(removed), ", ".join(removed) or "none", len(S["anchors"]) - len(removed), len(S["anchors"])))
        if cname == "A":
            c4_summary = (len(disc), zero)
    u_conn = {anc: connected(S["u_rows"][anc], {m for r in S["u_rows"][anc] for m in (r[1], r[2])}) for anc in S["anchors"]}
    if not all(u_conn.values()):
        say("  NOTE: U itself is disconnected in %s (the record's object); stated, not refused."
            % ", ".join(a for a, c in u_conn.items() if not c))

    results = {}
    for cname in ("A", "B"):
        anchors_conn = [a for a in S["anchors"] if conn[(cname, a)]]
        keys_est = [k for a in anchors_conn for k in est_by_anchor[a]]
        keys_all = [k for a in anchors_conn for k in all_by_anchor[a]]
        wrongs = {}
        for arm_name in ["U", "F_" + cname] + ["R_%s_%02d" % (cname, k) for k in range(1, K_DRAWS + 1)]:
            wrongs[arm_name] = wrong_maps(S, arms[arm_name], keys_est)
        wrongF = wrongs["F_" + cname][0]
        wrongR = {k: [wrongs["R_%s_%02d" % (cname, j)][0][k] for j in range(1, K_DRAWS + 1)] for k in keys_est}
        st = c1_stats(anchors_conn, est_by_anchor, wrongF, wrongR)
        v = c1_verdict(len(anchors_conn), st["lo"], st["hi"], min_anchors=min_anchors)
        results[cname] = dict(st=st, v=v, anchors_conn=anchors_conn, keys_est=keys_est, keys_all=keys_all, wrongs=wrongs)

    # ---- C1
    say("")
    say("=== C1: THE SELECTION EFFECT ON DIRECTION (the one barred endpoint; bar 0) ===")
    say("  denominator: the %d established edges of U (fixed from U: exact McNemar p < 0.05 on the anchor's JUDGED questions),"
        % len(S["est_keys"]))
    say("  minus the edges of the removed anchors (C4); direction = the MAJORITY sign over each arm's own %d question-bootstrap"
        % S["B"])
    say("  boards, build()'s `right` rule (p > 0.5; ruling R5: PRIMARY; the point-fit sign is printed beside, deciding nothing)")
    say("  against U's key direction; every W below is a wrong(established) count by construction.")
    rA = results["A"]; st = rA["st"]
    wU = sum(1 for k in rA["keys_est"] if rA["wrongs"]["U"][0][k])
    say("  W_U = %d(%d) | W_F = %d(%d) | mean W_R = %.2f (draws %s)" % (wU, wU, st["WF"], st["WF"], st["WR_mean"],
                                                                     " ".join("%d" % x for x in st["WR_draws"])))
    for lab, idx in (("sign(m)", 1), ("point fit", 2)):
        wu = sum(1 for k in rA["keys_est"] if rA["wrongs"]["U"][idx][k])
        wf = sum(1 for k in rA["keys_est"] if rA["wrongs"]["F_A"][idx][k])
        wr = np.mean([sum(1 for k in rA["keys_est"] if rA["wrongs"]["R_A_%02d" % j][idx][k]) for j in range(1, K_DRAWS + 1)])
        say("  beside (reading r1, decides nothing): direction by %-9s W_U %d | W_F %d | mean W_R %.2f | Delta_W %+.2f"
            % (lab, wu, wf, wr, wf - wr))
    for arm_name in ("U", "F_A"):
        wp, _, _, ties = rA["wrongs"][arm_name]
        say("  tie conventions (reading r2), %s: %d established edges at p = 0.5 exactly | W ties-as-wrong %d | W ties-excluded %d"
            % (arm_name, len(ties), sum(1 for k in rA["keys_est"] if wp[k] or k in ties),
               sum(1 for k in rA["keys_est"] if wp[k] and k not in ties)))
    rt = [len(rA["wrongs"]["R_A_%02d" % j][3]) for j in range(1, K_DRAWS + 1)]
    say("  tie conventions, R: mean %.2f established edges at p = 0.5 exactly per draw" % float(np.mean(rt)))
    c1_lines(say, st, rA["v"])
    support_lines(say, st)
    say("")
    c1_lines(say, results["B"]["st"], results["B"]["v"], label="C1 (convention B)", decides=False)

    # ---- C2
    say("")
    say("=== C2: THE SAFETY LEG AT THE OPERATING POINT (DESCRIPTIVE-ONLY; convention A; remaining anchors) ===")
    say("  U reference of record (920 pair, judged A): LOAO %d / %d(%d), nominal %.2f; in-sample %d / %d(%d)"
        % (U_REF["loao"] + U_REF["insample"]))
    say("  registered power: at nominal ~1.3, P(X >= 4 | 1.3) = 0.043 is the first significant count; only a ~4x miscalibration")
    say("  is detectable. Parameters FIXED (reading r6).")
    p4 = c2_block(say, S, arms, rA["keys_est"], rA["keys_all"], A_eval, "A")
    say("  convention B beside (decides nothing):")
    c2_block(say, S, arms, results["B"]["keys_est"], results["B"]["keys_all"], A_eval, "B")

    # ---- C3
    say("")
    say("=== C3: b1 IDENTIFICATION ON F (DESCRIPTIVE-ONLY, registered expecting UNDETERMINED) ===")
    say("  U of record (A-REDEFINE-REFIT, eval A, 809 established / 26 events): delta-deviance %.2f; P(b1 <= 0) %.4f-%.4f"
        % (U_REF["c3_ddev"], U_REF["c3_p"][0], U_REF["c3_p"][1]))
    say("  b1 UNIDENTIFIED = (quasi-)complete separation of wrong / right edges in A, zero events, or a non-finite ddev,")
    say("  checked on the data BEFORE any fit (registrar's ruling of 2026-09-23, programme L13883-L13923), OR SINGULAR")
    say("  OBSERVED INFORMATION at the optimiser's b1: I = -l''(b1*) <= 0 or I h^2 <= 16 eps max(1,|l(b1*)|), h = 1e-4 x")
    say("  max(1,|b1*|), l the profile log-likelihood (programme L14034-L14069, commit 0ce8460).")
    c3_u = c3_block(say, S, arms["U"], rA["keys_est"], A_eval, "U", reps=c3_reps)
    c3 = c3_block(say, S, arms["F_A"], rA["keys_est"], A_eval, "F", reps=c3_reps)
    c3_identification_summary(say, S, arms, rA["keys_est"], A_eval, "A")
    say("  convention B beside (decides nothing):")
    c3_block(say, S, arms["F_B"], results["B"]["keys_est"], A_eval, "F_B", reps=c3_reps)
    c3_identification_summary(say, S, arms, results["B"]["keys_est"], A_eval, "B")

    falsifier_lines(say, rA["v"], st)
    predictions(say, rA["v"], st, p4, c3, c4_summary)
    reproduction_lines(say, S, A_eval, loao=loao)
    return dict(c1=rA["v"], c1_B=results["B"]["v"], st=st, c3=c3, c3_u=c3_u, c4=c4_summary, p4=p4)


# ------------------------------------------------------------------------------------------ write-once
def write_once(path, text):
    if os.path.exists(path):
        hit("WRITE_ONCE.REFUSED")
        raise SystemExit("[WRITE-ONCE] %s exists; an outcome of record is never overwritten. Refused." % path)
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)


def header(say):
    say("=== CERT-UNDER-FILTER (registered 2026-09-23, commit 88a95d8; docs/judge_v2_program.md L13229-L13360) ===")
    say(identity_line())
    say("  ZERO judge calls; no DB written; systematic_budget.main disabled in-process (M2); stack_judge.py not imported.")
    say("  systematic_budget.build LF source sha16 %s (pinned); filter sources profile_r_filtered.norm_shipped %s, verdict %s"
        % (check_build_pin(), FILTER_SRC_SHA16["norm_shipped"], FILTER_SRC_SHA16["verdict"]))


# ------------------------------------------------------------------------------------------ modes
def check_connection_log(conns, x12_path):
    """R3 (iii) as re-ruled: the entries naming the stack cache are EXACTLY ONE, and it is load_real's immutable URI."""
    st = [c for c in conns if STACK_CACHE_NAME in c]
    if st != [stack_uri(x12_path)]:
        raise SystemExit("[HYGIENE] connection log: the stack cache must appear exactly once, as %s; found %s"
                         % (stack_uri(x12_path), st))
    return st[0]


def check_witness(say, expect_calls=None, counts=None):
    """D6 (8bbe6ce): the information assessments (counted in observed_information) EQUAL the fits (counted in c3_fit);
    --run also requires exactly 3 + 2 x K_DRAWS C3 fits attempted (U, F_A, F_B and every R draw of both conventions)."""
    w = counts or dict(calls=C3_CALLS[0], fits=FIT_COUNT[0], assessments=SING_EVALS[0], plateaus=INNER_PLATEAUS[0])
    say("  EXECUTION WITNESS: c3_fit calls %d; fits %d (counted in c3_fit); information assessments %d (counted in"
        " observed_information); inner re-maximisations resolved as a plateau %d"
        % (w["calls"], w["fits"], w["assessments"], w["plateaus"]))
    if not bool(w["assessments"] == w["fits"]):
        raise SystemExit("[WITNESS] information assessments %d != fits %d; refused (nothing written)"
                         % (w["assessments"], w["fits"]))
    if expect_calls is not None and not bool(w["calls"] == expect_calls):
        raise SystemExit("[WITNESS] c3_fit calls %d != the %d expected; refused (nothing written)" % (w["calls"], expect_calls))
    return w


def connection_log(say):
    """R3 (iii) as re-ruled (8bbe6ce): every sqlite3.connect of this process, printed; the stack cache exactly once,
    as load_real's immutable URI."""
    assert_stack_judge_not_loaded()
    one = check_connection_log(CONNECTIONS, X12_CACHE)
    say("  CONNECTION LOG (R3 (iii) as re-ruled): %d sqlite3.connect call(s), %d at import; stack cache opened exactly once,"
        " %s; %d refused attempt(s); stack_judge.py never loaded:" % (len(CONNECTIONS), len(IMPORT_CONNECTIONS), one,
                                                                     len(REFUSED_CONNECTIONS)))
    for c in CONNECTIONS:
        say("    %s" % c)


def main_dry(workers):
    check_wal(INPUT_DBS())                    # a non-empty -wal refuses BEFORE anything is opened
    print("reserved_pool_id=%s" % pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL), flush=True)
    L = []; say = lambda s: (L.append(s), print(s, flush=True))
    header(say)
    say("  --dry-run: zero calls, WRITES NOTHING.")
    D = load_real(say)
    S = prepare(D, say)
    per_anchor_counts(S, say)
    n_arms = 2 * (1 + K_DRAWS)
    say("")
    say("  MEASURED WALL TIME of the dry-run's single replicate (one arm board build, U): %.1f s; the run builds %d more"
        % (S["t_u"], n_arms))
    say("  arm boards: about %.0f min at 1 worker, %.0f min at %d worker(s), plus C3's cluster bootstraps and the LOAO"
        % (S["t_u"] * n_arms / 60.0, S["t_u"] * n_arms / 60.0 / max(1, workers), max(1, workers)))
    say("  reproduction (14 refits). The C1 cluster bootstrap resamples per-anchor sums and costs seconds (reading r3).")
    connection_log(say)
    say("  DRY-RUN COMPLETE: nothing written.")


def main_run(workers):
    if os.path.exists(OUT):
        hit("WRITE_ONCE.REFUSED")
        raise SystemExit("[WRITE-ONCE] %s exists; refused before computing." % OUT)
    check_wal(INPUT_DBS())                    # a non-empty -wal refuses BEFORE anything is opened
    print("reserved_pool_id=%s" % pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL), flush=True)
    L = ["reserved_pool_id=%s" % POOL]; say = lambda s: (L.append(s), print(s, flush=True))
    header(say)
    say("  run started %s" % time.strftime("%Y-%m-%d %H:%M:%S"))
    D = load_real(say)
    S = prepare(D, say)
    per_anchor_counts(S, say)
    arms = run_arms(S, workers, say)
    arms["U"] = {(e["anchor"], e["a"], e["b"]): (e["p"], e["m"], e["s"], e["pt"]) for e in S["u_edges"]}
    readout(S, arms, say)
    say("")
    check_witness(say, expect_calls=3 + 2 * K_DRAWS)
    connection_log(say)
    say("  run finished %s" % time.strftime("%Y-%m-%d %H:%M:%S"))
    write_once(OUT, "\n".join(L) + "\n")
    print("[CERT-UNDER-FILTER] outcome written once: %s" % OUT, file=sys.stderr)


# ------------------------------------------------------------------------------------------ selftest
MODELS_SYN = ["m1_best", "m2_good", "m3_fair", "m4_poor"]
ACC_SYN = {"m1_best": 0.9, "m2_good": 0.7, "m3_fair": 0.5, "m4_poor": 0.3}


def synth(mode, anchors=("Alpha", "Beta"), n_q=110, seed=5, gamma_disconnect=False, delta_floor=False):
    """A synthetic 4-model board. mode: 'adverse' (DISAGREE verdicts go to the per-question WRONG model, AGREE verdicts to
    the key-better model: the filter keeps exactly the anti-key votes -> C1 FAILED), 'favorable' (the mirror -> HELD),
    'neutral' (every verdict to the key-better model, independent of agreement -> Delta_W = 0 -> UNDETERMINED).
    gamma_disconnect adds an anchor where m4 plays only m3 and always gives m3's answer: F isolates m4 (disconnects).
    delta_floor adds a small anchor (216 U rows >= 200) whose kept rows fall below the 200-row floor under F."""
    rng = random.Random(seed)
    K = defaultdict(dict); P1 = defaultdict(dict); Praw = defaultdict(dict); anchor_q = {}; pool = set(); rows = []
    mid = 0
    specs = [(a, False, n_q) for a in anchors] + ([("Gamma", True, 2 * n_q)] if gamma_disconnect else []) \
        + ([("Delta", False, 36)] if delta_floor else [])
    for ai, (anc, is_gamma, nq) in enumerate(specs):
        for i in range(nq + 25):
            q = 10000 * (ai + 1) + i
            anchor_q[q] = anc; pool.add(q)
            for m in MODELS_SYN:
                ok = rng.random() < ACC_SYN[m]
                pred = "A" if ok else "B"
                if is_gamma and m == "m4_poor":
                    ok = bool(K[q]["m3_fair"]); pred = Praw[q]["m3_fair"]
                elif rng.random() < 0.04 and not (is_gamma and m == "m3_fair"):
                    pred = ""                                 # missing extraction: kept by A, dropped by B
                K[q][m] = int(ok); Praw[q][m] = pred; P1[q][m] = (pred or "").strip().upper()[:1]
            if i >= nq:
                continue                                      # eval-side only (for A_eval), never judged
            pairs = list(itertools.combinations(MODELS_SYN, 2))
            if is_gamma:
                pairs = [p for p in pairs if "m4_poor" not in p] + [("m3_fair", "m4_poor")]
            for a, b in pairs:
                mid += 1
                better, worse = (a, b) if ACC_SYN[a] > ACC_SYN[b] else (b, a)
                pa, pb = Praw[q][a], Praw[q][b]
                agree = bool(pa) and bool(pb) and pa == pb
                one_right = K[q][a] != K[q][b]
                if mode == "neutral":
                    w = better
                elif mode == "adverse":
                    w = better if agree else ((a if not K[q][a] else b) if one_right else worse)
                else:
                    w = worse if agree else ((a if K[q][a] else b) if one_right else better)
                rows.append((mid, a, b, q, w))
    return dict(models=list(MODELS_SYN), rows=rows, K=K, P1=P1, Praw=Praw, anchor_q=anchor_q, pool=pool)


def synth_pins(D, B):
    """Pins for a fixture = its own counts (G1 / G2 are exercised for refusal separately with perturbed pins)."""
    keepA, keepB, fc = apply_filter(D["rows"], D["Praw"])
    by = defaultdict(list)
    for r in D["rows"]:
        by[D["anchor_q"][r[3]]].append(r)
    anchors = sorted(a for a in by if len(by[a]) >= ANCHOR_FLOOR)
    ue, aq = arm_edges({a: [r[1:] for r in by[a]] for a in anchors}, anchors, D["models"], K=D["K"], P1=D["P1"], B=B)
    est = sb.established(ue, D["K"], aq)
    return dict(edges=len(ue), established=len(est), wrong_est=sum(1 for e in est if not e["right"]), n=fc["n"],
                keptA=fc["keptA"], keptB=fc["keptB"], baseB=fc["baseB"])


class _PermissiveSJ(object):
    """Selftest-only test double handed to the REAL systematic_budget.build() for the bit-identity proof (sb.sj is
    swapped for the duration of that one call and restored). The refusing stub in sys.modules is never modified."""

    def __init__(self, con):
        self._con = con
        self.PROMPT = "v1"; self.ALL_X12 = False

    def open_cache(self):
        return self._con


def _build_equivalence(tmp, say):
    """The REAL systematic_budget.build() on a synthetic cache, against arm_edges() in discovery mode."""
    D = synth("adverse", n_q=80, seed=11)
    evp = os.path.join(tmp, "eval_syn.db")
    ev = sqlite3.connect(evp)
    ev.execute("CREATE TABLE eval_results (question_id INTEGER, model_name TEXT, pred TEXT, is_correct INTEGER)")
    for q in sorted(D["K"]):
        for m in MODELS_SYN:
            ev.execute("INSERT INTO eval_results VALUES (?,?,?,?)", (q, m, D["Praw"][q][m], D["K"][q][m]))
    ev.commit(); ev.close()
    mem = sqlite3.connect(":memory:")
    mem.execute("CREATE TABLE verdicts (match_id INTEGER PRIMARY KEY, model_a TEXT, model_b TEXT, qid INTEGER, winner TEXT, invalid INTEGER)")
    for mid, a, b, q, w in D["rows"]:
        mem.execute("INSERT INTO verdicts VALUES (?,?,?,?,?,0)", (mid, a, b, q, w))
    saved = (rj.EVAL_DB, r512.primary_routing, r512.snapshot_id, r512.load_graph, r512.anchor_fn, p8.ARENA12, sb.sj)
    try:
        rj.EVAL_DB = evp.replace("\\", "/")
        r512.primary_routing = lambda tree: {q: a for q, a in D["anchor_q"].items()}
        r512.snapshot_id = lambda tree: "syn"
        r512.load_graph = lambda sid: {}
        r512.anchor_fn = lambda nodes: (lambda leaf: leaf)
        p8.ARENA12 = list(MODELS_SYN)
        sb.sj = _PermissiveSJ(mem)
        models, K, P, by, edges_ref, aq_ref = sb.build()
    finally:
        rj.EVAL_DB, r512.primary_routing, r512.snapshot_id, r512.load_graph, r512.anchor_fn, p8.ARENA12, sb.sj = saved
    need(sb.sj is SJ_STUB and sys.modules["stack_judge"] is SJ_STUB, 'check failed: sb.sj is SJ_STUB and sys.modules["stack_judge"] is SJ_STUB')
    by2 = defaultdict(list)
    for r in D["rows"]:
        by2[D["anchor_q"][r[3]]].append(r[1:])
    anchors = sorted(a for a in by2 if len(by2[a]) >= ANCHOR_FLOOR)
    mine, aq = arm_edges(by2, anchors, D["models"], K=D["K"], P1=D["P1"])
    fields = ("anchor", "a", "b", "p", "m", "s", "right", "agree", "gap", "n")
    ok = len(mine) == len(edges_ref) and all(all(x[f] == y[f] for f in fields) for x, y in zip(mine, edges_ref)) \
        and {a: v for a, v in aq.items()} == dict(aq_ref)
    say("  build equivalence: REAL systematic_budget.build() vs arm_edges() discovery mode on a synthetic cache: %d vs %d edges,"
        " every field (%s) bit-identical: %s" % (len(mine), len(edges_ref), ", ".join(fields), "YES" if ok else "NO"))
    need(ok, "arm_edges() does not reproduce systematic_budget.build()")
    need(len(mine) >= 10, 'check failed: len(mine) >= 10')
    return len(mine)


def _pipeline(D, say, B, loao=False, c3_reps=((40, 11), (40, 2026)), min_anchors=None):
    pins = synth_pins(D, B)
    S = prepare(D, say, pins=pins, B=B)
    per_anchor_counts(S, say)
    arms = run_arms(S, 1, say, B=B)
    arms["U"] = {(e["anchor"], e["a"], e["b"]): (e["p"], e["m"], e["s"], e["pt"]) for e in S["u_edges"]}
    res = readout(S, arms, say, c3_reps=c3_reps, loao=loao,
                  min_anchors=min_anchors if min_anchors is not None else C1_MIN_ANCHORS)
    return S, pins, res, arms


def _expect_exit(fn, prefix, what):
    try:
        fn()
    except SystemExit as e:
        need(str(e).startswith(prefix), (what, e))
        return str(e)
    raise AssertionError("%s did not refuse" % what)


def _edge(a, right, m=0.2, s=0.2, anchor="x", i=0):
    return dict(anchor=anchor, a="a%d" % i, b="b%d" % i, p=0.9, m=m, s=s, agree=a, right=right)


def _separation_selftest(say, st_a):
    """The separation ruling (L13883), executed both ways, on crafted edge sets through the SAME functions the run uses."""
    E = lambda ws, rs: [_edge(a, False, i=i) for i, a in enumerate(ws)] + [_edge(a, True, i=100 + i) for i, a in enumerate(rs)]
    r1 = unidentified(E([0.20, 0.30], [0.50, 0.60]))
    r2 = unidentified(E([0.50, 0.60], [0.20, 0.30]))
    r3 = unidentified(E([0.20, 0.40], [0.40, 0.60]))
    r4 = unidentified(E([0.40, 0.60], [0.20, 0.40]))
    r5 = unidentified(E([0.30, 0.50], [0.40, 0.60]))
    r6 = unidentified(E([], [0.4, 0.5])); r7 = unidentified(E([0.4], []))
    need(r1.startswith("complete separation in A: max A(wrong) 0.3000 <= min A(right) 0.5000"), r1)
    need(r2.startswith("complete separation in A: max A(right) 0.3000 <= min A(wrong) 0.5000"), r2)
    need(r3.startswith("quasi-complete separation in A: max A(wrong) 0.4000 <= min A(right) 0.4000"), r3)
    need(r4.startswith("quasi-complete separation in A: max A(right) 0.4000 <= min A(wrong) 0.4000"), r4)
    need(r5 is None, r5)
    need(r6.startswith("zero wrong events") and r7.startswith("zero right events"), (r6, r7))
    print("[selftest] separation: wrong-below-right, right-below-wrong, both quasi-complete ties, zero events -> unidentified;"
          " overlap -> identified", flush=True)

    # a NON-separated overlap that FITS: widener-generated edges, seeded
    rng = random.Random(20260923)
    from scipy.stats import norm as _norm
    es = []
    for i in range(120):
        a = 0.3 + 0.6 * rng.random(); m = 0.25; s_ = 0.2
        pw = float(_norm.cdf(-m / math.sqrt(s_ * s_ + math.exp(-3.0 + 3.3 * a) ** 2)))
        es.append(_edge(a, rng.random() >= pw, m=m, s=s_, anchor="c%d" % (i % 6), i=i))
    r = c3_fit(es, reps=((60, 11), (60, 2026)))
    need(r["reason"] is None and not r["status"].startswith("NO FIT"), r["status"])
    need(r["fit"] is not None and bool(abs(r["fit"]["ddev"]) < float("inf")) and bool(math.isfinite(r["fit"]["info"]["I"])), r["fit"])
    c3_lines(say, "OVL", r["events"], r["n"], r["fit"], r["pboots"], r["status"])
    print("[selftest] overlap fits: %d events of %d, b1 %+.3f, ddev %.2f, observed information I %.3g -> %s"
          % (r["events"], r["n"], r["fit"]["b1"], r["fit"]["ddev"], r["fit"]["info"]["I"], r["status"]), flush=True)

    # C3 NO FIT on SEPARATION, with the optimiser's values printed descriptively, and P5 UNDETERMINED on it
    sep = [dict(e, right=bool(e["agree"] >= 0.6)) for e in es]
    rs = c3_fit(sep, reps=((20, 11),))
    need(rs["status"].startswith("NO FIT (b1 unidentified: complete separation in A"), rs["status"])
    need(rs["fit"] is not None and rs["pboots"] == [], rs)
    n0 = []
    c3_lines(n0.append, "SEP", rs["events"], rs["n"], rs["fit"], rs["pboots"], rs["status"])
    need(any("DESCRIPTIVE, it decides nothing" in x for x in n0), n0)
    for x in n0:
        say(x)
    for ddev_fake in (1.06, 6.0):
        pl = []
        forced = dict(rs, fit=dict(rs["fit"], ddev=ddev_fake))
        predictions(pl.append, "UNDETERMINED", dict(WF=4, WR_mean=5.0, delta=-1.0), (10, 0, 0.1), forced, (0, 0))
        p5 = [x for x in pl if x.lstrip().startswith("P5 ")][0]
        need(p5.endswith("-> UNDETERMINED") and "descriptive" in p5, p5)
    print("[selftest] separation -> C3 NO FIT (b1 unidentified: complete separation ...), optimiser values printed as"
          " descriptive, bootstrap not run; P5 UNDETERMINED with a returned ddev of 1.06 and of 6.0", flush=True)
    return es, sep


SING_IDS = ("SING.I_NONPOS", "SING.ROUNDOFF", "SING.NONSINGULAR")


def _sing_delta(before):
    return {b: HITS.get(b, 0) - before.get(b, 0) for b in SING_IDS}


def _no_interior_inner(f, b0s, b1):
    """Selftest-only inner search on the fit's own objective, reshaped: flat within 1.5 of the start (scipy finds no
    bracket) and decreasing beyond it on both sides, so the scan's lowest point is at its end: NO interior optimum."""
    f0 = f(b0s)
    return _inner_min(lambda z: f0 - (1e-3 * abs(z - b0s) if abs(z - b0s) > 1.5 else 0.0), b0s, b1)


def _singular_selftest(say, flat_es, ovl_es, sep_es, fav_lines):
    """The singular-information ruling (programme L14034-L14069), executed on (a) the flat +720 / ddev 1.06 fit, (b)
    the overlapping well-fitting set (b1 +5.39, ddev 9.95, I ~ 0.17), (c) a separation case, and (d) the classifier on
    crafted (I, h, l) at and around the registered bound. Every case is compared against its expected branch, reason and
    per-branch evaluation counts; nothing is only printed."""
    expected = {
        "a": dict(branch="SINGULAR", sing="I <= 0", sep=None,
                  counts={"SING.I_NONPOS": 1, "SING.ROUNDOFF": 0, "SING.NONSINGULAR": 0}),
        "b": dict(branch="IDENTIFIED", sing=None, sep=None,
                  counts={"SING.I_NONPOS": 0, "SING.ROUNDOFF": 0, "SING.NONSINGULAR": 1}),
        "c": dict(branch="SEPARATION", sing="I <= 0", sep="complete separation in A",
                  counts={"SING.I_NONPOS": 1, "SING.ROUNDOFF": 0, "SING.NONSINGULAR": 0}),
    }
    # the inner re-maximisation, every path executed on crafted objectives (h is not involved)
    q = _inner_min(lambda x: (x - 3.0) ** 2 + 1.0, 0.0, 0.0)
    need(q[3] == "brent" and bool(abs(q[1] - 3.0) < 1e-7) and bool(abs(q[0] + 1.0) < 1e-15) and bool(q[2] < 1e-15), q)
    # the DESCRIPTIVE estimate is computed, not zeroed: on (x - 3)^2 the Newton decrement is (x - 3)^2 itself
    need(bool(q[2] > 0.0) and bool(abs(q[2] - (q[1] - 3.0) ** 2) <= 0.1 * (q[1] - 3.0) ** 2),
         "inner value-error estimate %r, expected (x - 3)^2 = %r" % (q[2], (q[1] - 3.0) ** 2))
    q_brent = q
    p0 = INNER_PLATEAUS[0]
    q = _inner_min(lambda x: 7.0, 2.0, 0.0)
    need(q == (-7.0, 2.0, 0.0, "plateau") and INNER_PLATEAUS[0] == p0 + 1, q)
    q = _inner_min(lambda x: min(1.0, (x - 60.0) ** 2 / 400.0), 0.0, 0.0)      # flat at the start: scipy finds no bracket
    need(q[3] == "scan+brent" and bool(abs(q[1] - 60.0) < 1e-4) and bool(abs(q[0]) < 1e-12), q)
    q = _inner_min(lambda x: 1.0 if x < 10.0 else 0.5, 0.0, 0.0)
    need(q[3] == "plateau" and q[0] == -0.5 and bool(q[1] >= 10.0) and INNER_PLATEAUS[0] == p0 + 2, q)
    unres = {}
    for tag, fn, kw, want in (
            ("no interior", lambda x: -x if x > 5.0 else -5.0, {}, ("INNER.NO_INTERIOR", "no interior optimum")),
            ("non-finite scan", lambda x: float("nan") if abs(x) > 1.5 else 1.0, {}, ("INNER.NONFINITE_SCAN", "non-finite nll")),
            ("Brent maxiter 2", lambda x: (x - 3.0) ** 2 + 1.0, dict(maxiter=2), ("INNER.BRENT_NOT_CONVERGED", "Brent did not converge"))):
        h0_ = HITS.get(want[0], 0)
        try:
            got_ = _inner_min(fn, 0.0, 0.0, **kw)
        except InnerUnresolved as ex:
            unres[tag] = str(ex)
        else:
            raise CheckFailed("inner path %s was resolved (%r); expected unresolved" % (tag, got_))
        need(unres[tag].startswith(want[1]) and HITS.get(want[0], 0) == h0_ + 1, (tag, unres[tag]))
    print("[selftest] inner re-maximisation paths executed: brent (x = 3 to 1e-7; the descriptive estimate equals (x - 3)^2"
          " = %.3g), plateau (constant), scan+brent (a dip at 60 behind a flat start), lower plateau (a step); UNRESOLVED"
          " (no refusal): %s" % ((q_brent[1] - 3.0) ** 2, " | ".join("%s -> %s" % kv for kv in sorted(unres.items()))), flush=True)

    got = {}
    for case, es in (("a", flat_es), ("b", ovl_es), ("c", sep_es)):
        before = dict(HITS)
        r = c3_fit(es, reps=((20, 11),))
        d = _sing_delta(before)
        got[case] = (r, d)
        fired = ("separation / zero events (data, before the fit)" if r["branch"] in ("SEPARATION", "ZERO_EVENTS") else
                 "singular observed information (%s)" % r["sing"] if r["branch"] == "SINGULAR" else
                 "none: IDENTIFIED")
        info = r["fit"]["info"]
        print("[selftest] singular-information case (%s): b1* %+.4f ddev %.4f | I %.6g h %.6g l(b1*) %.10g I h^2 %.4g bound"
              " %.4g | separation check: %s | singular check: %s | BRANCH FIRED: %s | %s"
              % (case, r["fit"]["b1"], r["fit"]["ddev"], info["I"], info["h"], info["l"], info["Ih2"], info["bound"],
                 r["sep"] or "ranges overlap", r["sing"] or "not singular", fired, r["status"]), flush=True)
        print("[selftest]   counts of singular-branch outcomes in case (%s): got %s, expected %s"
              % (case, d, expected[case]["counts"]), flush=True)
        c3_lines(say, "(%s)" % case, r["events"], r["n"], r["fit"], r["pboots"], r["status"])
        e = expected[case]
        need(r["branch"] == e["branch"], "case (%s): branch %s, expected %s" % (case, r["branch"], e["branch"]))
        need(r["sing"] == e["sing"], "case (%s): singular check %r, expected %r" % (case, r["sing"], e["sing"]))
        need((r["sep"] is None) if e["sep"] is None else bool(str(r["sep"]).startswith(e["sep"])),
             "case (%s): separation %r, expected %r" % (case, r["sep"], e["sep"]))
        need(d == e["counts"], "case (%s): singular-branch counts %s, expected %s" % (case, d, e["counts"]))
        reg = 16.0 * 2.0 ** -52 * max(1.0, abs(info["l"]))           # the REGISTERED bound, written from the ruling's literals
        need(bool(info["bound"] == reg) and bool(info["h"] == 1e-4 * max(1.0, abs(r["fit"]["b1"]))),
             "case (%s): bound %r / h %r differ from the registered 16 x 2^-52 x max(1,|l|) = %r / 1e-4 x max(1,|b1*|)"
             % (case, info["bound"], info["h"], reg))

    # (a) the flat case: the fit relayed as "b1 +720, ddev 1.06"; ranges OVERLAP (not separation); I exactly 0
    ra = got["a"][0]
    aw = [e["agree"] for e in ra["es"] if not e["right"]]; ar = [e["agree"] for e in ra["es"] if e["right"]]
    need(bool(abs(ra["fit"]["b1"] - 720.5276) < 1e-3) and bool(abs(ra["fit"]["ddev"] - 1.0602) < 1e-3),
         "case (a) is not the +720 / 1.06 fit: %r" % ra["fit"])
    need(bool(abs(min(aw) - 0.3821) < 1e-3) and bool(abs(max(aw) - 0.6341) < 1e-3) and bool(abs(min(ar) - 0.3197) < 1e-3)
         and bool(abs(max(ar) - 0.64) < 1e-3), (min(aw), max(aw), min(ar), max(ar)))
    need(bool(ra["fit"]["info"]["I"] == 0.0), "case (a): I %r, expected exactly 0 (a plateau)" % ra["fit"]["info"]["I"])
    need(ra["status"] == "NO FIT (b1 unidentified: singular observed information)" and ra["pboots"] == [], ra["status"])
    need(any(x.startswith("  U    established edges 10, wrong-direction events 4") and "b1 +720.5276" in x
             and "profile delta-deviance 1.06" in x for x in fav_lines), "the favorable fixture's U line is not the +720 fit")
    need(any("-> U: NO FIT (b1 unidentified: singular observed information)" in x for x in fav_lines),
         "the favorable fixture's U fit did not read NO FIT (singular) inside the pipeline")
    pl = []
    predictions(pl.append, "UNDETERMINED", dict(WF=4, WR_mean=5.0, delta=-1.0), (10, 0, 0.1), ra, (0, 0))
    p5 = [x for x in pl if x.lstrip().startswith("P5 ")][0]
    need(p5.endswith("-> UNDETERMINED") and "1.06 descriptive" in p5, p5)
    for x in pl:
        say(x)
    print("[selftest] (a) FLAT +720 / ddev 1.06: A(wrong) %.4f-%.4f, A(right) %.4f-%.4f OVERLAP (not separation); I = %r"
          " -> NO FIT via the SINGULAR-INFORMATION branch (I <= 0); as F's fit P5 reads: %s"
          % (min(aw), max(aw), min(ar), max(ar), ra["fit"]["info"]["I"], p5.strip()), flush=True)

    # (b) the overlapping well-fitting set stays IDENTIFIED
    rb = got["b"][0]
    need(bool(abs(rb["fit"]["b1"] - 5.389) < 0.01) and bool(abs(rb["fit"]["ddev"] - 9.95) < 0.01), rb["fit"])
    need(bool(0.15 < rb["fit"]["info"]["I"] < 0.19), "case (b): I %r, expected ~0.17" % rb["fit"]["info"]["I"])
    need(bool(rb["fit"]["info"]["Ih2"] > 1e5 * rb["fit"]["info"]["bound"]), rb["fit"]["info"])     # ~2.1e5 x the bound
    need(not rb["status"].startswith("NO FIT") and len(rb["pboots"]) == 1, rb["status"])
    print("[selftest] (b) OVERLAP b1 %+.3f ddev %.2f: I = %.4f, I h^2 = %.3g = %.3g x the bound -> IDENTIFIED (%s)"
          % (rb["fit"]["b1"], rb["fit"]["ddev"], rb["fit"]["info"]["I"], rb["fit"]["info"]["Ih2"],
             rb["fit"]["info"]["Ih2"] / max(rb["fit"]["info"]["bound"], 1e-300), rb["status"]), flush=True)

    # (c) separation still reads NO FIT via SEPARATION (the reason named), the singular check evaluated beside
    rc = got["c"][0]
    need(rc["status"].startswith("NO FIT (b1 unidentified: complete separation in A"), rc["status"])
    print("[selftest] (c) SEPARATION: %s; the singular check on the same fit reads %r and does not replace the named reason"
          % (rc["status"], rc["sing"]), flush=True)

    # (d) the classifier itself at and around the registered bound (h a power of two, so I x h^2 is exact)
    before = dict(HITS)
    e = EPS64
    crafted = [((0.0, 1.0, 5.0), "I <= 0"), ((-1e-3, 1.0, 5.0), "I <= 0"),
               ((8 * e * 5.0, 1.0, 5.0), "I h^2 <= 16 eps max(1,|l|)"),
               ((16 * e * 5.0, 1.0, 5.0), "I h^2 <= 16 eps max(1,|l|)"),
               ((17 * e * 5.0, 1.0, 5.0), None),
               ((16 * e, 1.0, 0.25), "I h^2 <= 16 eps max(1,|l|)"),
               ((17 * e, 1.0, 0.25), None),
               ((16 * e * 5.0 / 2.0 ** -20, 2.0 ** -10, -5.0), "I h^2 <= 16 eps max(1,|l|)")]
    for (I_, h_, l_), want in crafted:
        g = singular_information(I_, h_, l_)
        need(g == want, "crafted (I %r, h %r, l %r): %r, expected %r" % (I_, h_, l_, g, want))
    dd = _sing_delta(before)
    want_d = {"SING.I_NONPOS": 2, "SING.ROUNDOFF": 4, "SING.NONSINGULAR": 2}
    need(dd == want_d, "crafted classifier counts %s, expected %s" % (dd, want_d))
    nf0 = HITS.get("SING.NONFINITE_I", 0)
    need(singular_information(float("nan"), 1.0, 5.0) == NONFINITE_REASON and HITS.get("SING.NONFINITE_I", 0) == nf0 + 1,
         "a non-finite I must read NONFINITE_REASON")
    print("[selftest] (d) classifier at the registered bound: I <= 0 x2, 0 < I h^2 <= 16 eps max(1,|l|) x4 (8x, exactly 16x,"
          " |l| < 1 uses 1, h = 2^-10), 17x not singular x2: counts %s = expected; a non-finite I reads '%s' (no refusal)"
          % (dd, NONFINITE_REASON), flush=True)

    # (e) D3: a fit with |b1*| < 1 -> h == 1e-4 exactly (kills h without the max(1, .) floor)
    from scipy.stats import norm as _norm
    rng = random.Random(2)
    es_e = []
    for i in range(300):
        a = 0.3 + 0.6 * rng.random(); m = 0.25; s_ = 0.2
        pw = float(_norm.cdf(-m / math.sqrt(s_ * s_ + math.exp(-1.0 + 0.3 * a) ** 2)))
        es_e.append(_edge(a, rng.random() >= pw, m=m, s=s_, anchor="c%d" % (i % 6), i=i))
    re_ = c3_fit(es_e, reps=())
    ie = re_["fit"]["info"]
    print("[selftest] (e) |b1*| < 1: b1* %+.4f ddev %.3f | h %r (required exactly 1e-4) | I %.4f | %s"
          % (re_["fit"]["b1"], re_["fit"]["ddev"], ie["h"], ie["I"], re_["status"]), flush=True)
    need(bool(abs(re_["fit"]["b1"]) < 1.0) and bool(abs(re_["fit"]["b1"] + 0.5117) < 1e-3), re_["fit"])
    need(bool(ie["h"] == 1e-4), "case (e): h %r, the registered 1e-4 x max(1, |b1*|) = 1e-4 exactly" % ie["h"])
    need(re_["branch"] == "IDENTIFIED" and ie["singular"] is None, re_["status"])

    # (f) D2: each NO FIT mapping, end to end through c3_fit, with the P5 consequence; no refusal anywhere
    saved = _INNER_IMPL[0]
    cases_f = (
        ("Brent not converged", lambda f, b0s, b1: _inner_min(f, b0s, b1, maxiter=2),
         "INNER_UNRESOLVED", "NO FIT (b1 unidentified: inner re-maximisation not resolved: Brent did not converge",
         "C3.NO_FIT_INNER", "INNER.BRENT_NOT_CONVERGED"),
        ("no interior optimum", _no_interior_inner,
         "INNER_UNRESOLVED", "NO FIT (b1 unidentified: inner re-maximisation not resolved: no interior optimum",
         "C3.NO_FIT_INNER", "INNER.NO_INTERIOR"),
        ("non-finite scan", lambda f, b0s, b1: _inner_min(lambda z: 1.0 if abs(z - b0s) < 1.5 else float("nan"), b0s, b1),
         "INNER_UNRESOLVED", "NO FIT (b1 unidentified: inner re-maximisation not resolved: non-finite nll",
         "C3.NO_FIT_INNER", "INNER.NONFINITE_SCAN"),
        ("non-finite I", lambda f, b0s, b1: (float("inf"), b0s, 0.0, "crafted"),
         "NONFINITE_I", "NO FIT (b1 unidentified: non-finite observed information)",
         "C3.NO_FIT_NONFINITE_I", "SING.NONFINITE_I"))
    try:
        for tag, impl, br, st_prefix, c3_id, inner_id in cases_f:
            _INNER_IMPL[0] = impl
            h_c3, h_in = HITS.get(c3_id, 0), HITS.get(inner_id, 0)
            rf = c3_fit(ovl_es, reps=((20, 11),))
            need(rf["branch"] == br and rf["status"].startswith(st_prefix) and rf["pboots"] == [],
                 "(f) %s: branch %s status %s" % (tag, rf["branch"], rf["status"]))
            need(HITS.get(c3_id, 0) == h_c3 + 1 and HITS.get(inner_id, 0) >= h_in + 1, "(f) %s: branch ids not hit" % tag)
            pl = []
            predictions(pl.append, "UNDETERMINED", dict(WF=4, WR_mean=5.0, delta=-1.0), (10, 0, 0.1), rf, (0, 0))
            p5 = [x for x in pl if x.lstrip().startswith("P5 ")][0]
            need(p5.endswith("-> UNDETERMINED") and "descriptive" in p5, p5)
            ll = []
            c3_lines(ll.append, "(f)", rf["events"], rf["n"], rf["fit"], rf["pboots"], rf["status"])
            need(any("-> (f): NO FIT" in x for x in ll), ll)
            for x in ll:
                say(x)
            print("[selftest] (f) %-20s -> %s | P5 %s" % (tag, rf["status"][:120], p5.rsplit("-> ", 1)[1]), flush=True)
    finally:
        _INNER_IMPL[0] = saved
    return got


WITNESS_EXPECTED = dict(calls=268, fits=215, assessments=215, plateaus=203)   # the selftest's EXACT counts (D6), pinned


def _load_real_selftest(tmp, say):
    """D1 (8bbe6ce): load_real on a SYNTHETIC stack_v2_promptv2_x12all.db in the tempdir. The fixture DBs are BUILT with
    the unlogged sqlite3 connect (fixture construction, tempdir only); every READ goes through the logged hook."""
    global X12_CACHE
    models = ["syn_model_%02d" % i for i in range(12)]
    x12 = os.path.join(tmp, STACK_CACHE_NAME)
    evp = os.path.join(tmp, "eval_for_load_real.db"); snp = os.path.join(tmp, "snapshots_for_load_real.db")
    c = _REAL_CONNECT(x12)
    c.execute("CREATE TABLE verdicts (match_id INTEGER PRIMARY KEY, model_a TEXT, model_b TEXT, qid INTEGER, winner TEXT,"
              " invalid INTEGER)")
    rows = [(1, models[0], models[1], 7, models[0], 0), (2, models[2], models[3], 8, "TIE", 0), (3, models[0], models[2], 7, models[2], 1)]
    c.executemany("INSERT INTO verdicts VALUES (?,?,?,?,?,?)", rows); c.commit(); c.close()
    c = _REAL_CONNECT(evp)
    c.execute("CREATE TABLE eval_results (question_id INTEGER, model_name TEXT, pred TEXT, is_correct INTEGER)")
    c.execute("CREATE TABLE reserved_pool (question_id INTEGER, pool_id TEXT)")
    for q in (7, 8):
        c.executemany("INSERT INTO eval_results VALUES (?,?,?,?)", [(q, m, "A", 1) for m in models])
        c.execute("INSERT INTO reserved_pool VALUES (?,?)", (q, POOL))
    c.commit(); c.close()
    c = _REAL_CONNECT(snp)
    c.execute("CREATE TABLE snapshots (id TEXT, graph TEXT)")
    c.execute("INSERT INTO snapshots VALUES (?,?)", ("syn", json.dumps({"nodes": [{"id": "leafA"}]})))
    c.commit(); c.close()
    saved = (X12_CACHE, rj.EVAL_DB, r512.SNAP_DB, r512.primary_routing, r512.snapshot_id, r512.anchor_fn, p8.ARENA12)
    n_before = len(CONNECTIONS)
    try:
        X12_CACHE = x12
        rj.EVAL_DB = evp; r512.SNAP_DB = snp
        r512.primary_routing = lambda tree: {7: "leafA", 8: "leafA"}
        r512.snapshot_id = lambda tree: "syn"
        r512.anchor_fn = lambda nodes: (lambda leaf: leaf)
        p8.ARENA12 = list(models)
        # each refusal reason of the hook, executed on its own (the message names the reason that fired)
        why = {}
        why["outside load_real (plain)"] = _expect_exit(lambda: sqlite3.connect(x12), "[HYGIENE]", "plain, outside load_real")
        why["outside load_real (immutable URI)"] = _expect_exit(lambda: ro(x12), "[HYGIENE]", "immutable URI, outside load_real")
        try:
            _STACK_AUTH[0] = stack_uri(x12)                 # as inside load_real, but with the wrong call
            why["authorised, plain path"] = _expect_exit(lambda: sqlite3.connect(x12), "[HYGIENE]", "authorised plain")
            why["authorised, mode=ro URI"] = _expect_exit(
                lambda: sqlite3.connect("file:%s?mode=ro" % x12.replace("\\", "/"), uri=True), "[HYGIENE]", "authorised mode=ro")
            with open(x12 + "-wal", "wb") as f_:
                f_.write(b"\x37\x7f\x06\x82" + b"\x00" * 28)
            why["authorised, non-empty -wal"] = _expect_exit(lambda: ro(x12), "[HYGIENE]", "authorised, -wal non-empty")
        finally:
            _STACK_AUTH[0] = None
        for k_, frag in (("outside load_real (plain)", "not opened by load_real"),
                         ("outside load_real (immutable URI)", "not opened by load_real"),
                         ("authorised, plain path", "not the URI"), ("authorised, mode=ro URI", "not the URI"),
                         ("authorised, non-empty -wal", "-wal is non-empty")):
            need(frag in why[k_], "hook refusal %s: %s (expected '%s')" % (k_, why[k_], frag))
        # a non-empty -wal beside the cache refuses load_real itself before anything is opened
        _expect_exit(lambda: load_real([].append), "[WAL]", "load_real with a non-empty stack-cache -wal")
        need(not STACK_OPENS and len(CONNECTIONS) == n_before, "a refused open or load_real opened something")
        os.remove(x12 + "-wal")
        D = load_real(say)                                  # the ONE admitted open
        need(len(D["rows"]) == 2 and STACK_OPENS == [stack_uri(x12)], (len(D["rows"]), STACK_OPENS))
        need([c_ for c_ in CONNECTIONS if STACK_CACHE_NAME in c_] == [stack_uri(x12)], CONNECTIONS)
        why["load_real a second time"] = _expect_exit(lambda: load_real([].append), "[HYGIENE]", "second load_real")
        need("a second open" in why["load_real a second time"], why["load_real a second time"])
        # every other open of it refuses: an immutable open outside load_real, a plain connect, a mode=ro-only URI
        _expect_exit(lambda: ro(x12), "[HYGIENE]", "second immutable open")
        _expect_exit(lambda: sqlite3.connect(x12), "[HYGIENE]", "plain connect after load_real")
        _expect_exit(lambda: sqlite3.connect("file:%s?mode=ro" % x12.replace("\\", "/"), uri=True), "[HYGIENE]", "mode=ro URI")
        need(STACK_OPENS == [stack_uri(x12)] and [c_ for c_ in CONNECTIONS if STACK_CACHE_NAME in c_] == [stack_uri(x12)],
             "a refused open reached the log")
        # connection_log's rule, both ways
        need(check_connection_log(CONNECTIONS, x12) == stack_uri(x12), "connection log rule")
        _expect_exit(lambda: check_connection_log([], x12), "[HYGIENE]", "log without the one open")
        _expect_exit(lambda: check_connection_log([stack_uri(x12), stack_uri(x12)], x12), "[HYGIENE]", "log with two opens")
        _expect_exit(lambda: check_connection_log(["file:%s?mode=ro" % x12.replace("\\", "/")], x12), "[HYGIENE]",
                     "log with a non-immutable open")
    finally:
        (_x, rj.EVAL_DB, r512.SNAP_DB, r512.primary_routing, r512.snapshot_id, r512.anchor_fn, p8.ARENA12) = saved
        X12_CACHE = x12                                     # stays the synthetic path: the selftest's final log check
    print("[selftest] D1 (R3 (iii) re-ruled): load_real on a synthetic %s: a non-empty -wal refuses first; the immutable URI"
          " is ADMITTED once (%d verdict rows, invalid dropped); refused, each for its own reason: %s; connection_log's rule"
          " refuses a log with 0, 2 or a non-immutable open"
          % (STACK_CACHE_NAME, len(D["rows"]), " | ".join("%s -> %s" % (k_, v_.split(": ", 1)[1].split(" (R3")[0])
                                                          for k_, v_ in sorted(why.items()))), flush=True)


def selftest():
    global OUT
    tmp = tempfile.mkdtemp(prefix="cuf_selftest_")
    OUT = os.path.join(tmp, "cert_under_filter_outcome.txt")         # never the file of record
    L = []; say = L.append
    t0 = time.time()
    print("[selftest]" + identity_line(), flush=True)
    print("[selftest] tempdir %s; NO DB of record is opened; the pool guard is not called" % tmp)
    logged_connect = sqlite3.connect
    opened = []

    def guarded_connect(db, *a, **k):
        p_ = str(db).replace("\\", "/")
        if p_ != ":memory:" and tmp.replace("\\", "/") not in p_:
            raise AssertionError("[selftest] refused to open %s: only the tempdir and :memory: are allowed" % db)
        con = logged_connect(db, *a, **k)            # a refused open raises here and is never recorded as opened
        opened.append(p_)
        return con
    sqlite3.connect = guarded_connect
    header(say)

    # ---- need() itself: every guard and check below goes through it, so it is proven first WITHOUT using it
    try:
        need(False, "probe")
    except CheckFailed:
        pass
    else:
        raise RuntimeError("[selftest] need(False) did not raise: every guard would be vacuous")
    need(True, "probe")
    print("[selftest] need(): raises CheckFailed on a false condition (explicit raise; survives python -O, sys.flags.optimize"
          " = %d)" % sys.flags.optimize, flush=True)

    # ---- R3: the stub refuses ANY attribute; stack_judge.py never loaded; the stack cache never in the log
    need(sys.modules["stack_judge"] is SJ_STUB and sb.sj is SJ_STUB and isinstance(SJ_STUB, _RefusingModule), 'check failed: sys.modules["stack_judge"] is SJ_STUB and sb.sj is SJ_STUB and isinstance(SJ_STUB, _RefusingModule)')
    names = ("open_cache", "cache_path", "PROMPT", "ALL_X12", "zz_arbitrary_attribute_%d" % os.getpid())
    for name in names:
        try:
            getattr(SJ_STUB, name); raise AssertionError("stub attribute %s did not refuse" % name)
        except StubRefusal:
            pass
    try:
        getattr(SJ_STUB, "anything_else", None); raise AssertionError("getattr with a default swallowed the refusal")
    except StubRefusal:
        pass
    try:
        SJ_STUB.PROMPT = "v2"; raise AssertionError("stub setattr did not refuse")
    except StubRefusal:
        pass
    try:
        sb.sj.open_cache(); raise AssertionError("a call through sb.sj did not refuse")
    except StubRefusal:
        pass
    assert_stack_judge_not_loaded()
    need(not IMPORT_CONNECTIONS, IMPORT_CONNECTIONS)
    need(IMPORT_STUB_ACCESSES == [], "non-dunder stub access at import: %r" % IMPORT_STUB_ACCESSES)
    _expect_exit(lambda: check_import_stub_accesses(["PROMPT"]), "[HYGIENE] a non-dunder stack_judge attribute",
                 "import-time stub access guard")
    need(STUB_ACCESSES[:len(names) + 3] == list(names) + ["anything_else", "PROMPT", "open_cache"],
         "stub access log %r" % STUB_ACCESSES)
    _expect_exit(lambda: sqlite3.connect(os.path.join(tmp, STACK_CACHE_NAME)), "[HYGIENE]", "plain stack cache open")
    need(not any(STACK_CACHE_NAME in c for c in CONNECTIONS), "a refused stack-cache attempt reached the log")
    _expect_exit(lambda: sb.main("unfiltered"), "[M2]", "sb.main")
    print("[selftest] R3: stub refuses %d attribute reads (incl. an arbitrary name) + getattr-with-default + setattr + a call"
          " through sb.sj (access log %s); 0 non-dunder stub accesses and 0 DB opens during import; stack_judge.py not"
          " loaded; a PLAIN stack-cache open (outside load_real) is refused and absent from the log"
          % (len(names), STUB_ACCESSES[:len(names) + 3]), flush=True)

    # ---- R4 (a): build()'s source hash, at launch
    sbcopy = os.path.join(tmp, "systematic_budget_mutated.py")
    src = open(SB_PATH, encoding="utf-8").read().replace("\r\n", "\n")
    need(src.count("    rng = random.Random(42)") == 1, 'check failed: src.count(" rng = random.Random(42)") == 1')
    open(sbcopy, "w", encoding="utf-8", newline="\n").write(src.replace("    rng = random.Random(42)", "    rng = random.Random(43)"))
    msg = _expect_exit(lambda: check_build_pin(_func_source(sbcopy, "build")), "[PIN]", "build() source hash")
    need(check_build_pin() == BUILD_SRC_SHA16, 'check failed: check_build_pin() == BUILD_SRC_SHA16')
    print("[selftest] R4 (a): a one-character change to build() (seed 42 -> 43) is REFUSED: %s" % msg[:92], flush=True)
    n_eq = _build_equivalence(tmp, say)
    print("[selftest] R4 (b): REAL systematic_budget.build() vs arm_edges(): %d edges, every field bit-identical (%.0f s)"
          % (n_eq, time.time() - t0), flush=True)

    # ---- R6: WAL refusal (non-empty) and admission (absent / empty)
    walp = os.path.join(tmp, "walcheck.db")
    con_ = sqlite3.connect(walp); con_.execute("CREATE TABLE t (x)"); con_.commit(); con_.close()
    need(check_wal([walp])[0][1] == "no WAL sidecar", 'check failed: check_wal([walp])[0][1] == "no WAL sidecar"')
    open(walp + "-wal", "wb").close()
    need(check_wal([walp])[0][1] == "WAL sidecar 0 bytes", 'check failed: check_wal([walp])[0][1] == "WAL sidecar 0 bytes"')
    with open(walp + "-wal", "wb") as f_:
        f_.write(b"\x37\x7f\x06\x82" + b"\x00" * 28)
    _expect_exit(lambda: check_wal([walp]), "[WAL]", "non-empty WAL")
    print("[selftest] R6 WAL: absent -> read; empty -> read; non-empty (32 bytes) -> REFUSED", flush=True)
    _load_real_selftest(tmp, say)

    # ---- the filter: missing prediction kept by A, dropped by B (and B's base excludes it)
    tiny = [(1, "x", "y", 1, "x"), (2, "x", "y", 2, "y"), (3, "x", "y", 3, "x")]
    kA, kB, fct = apply_filter(tiny, {1: {"x": "A", "y": "A"}, 2: {"x": "A", "y": "B"}, 3: {"x": "", "y": "C"}})
    need(kA == {2, 3} and kB == {2} and fct["missing"] == {3} and fct["baseB"] == 2, (kA, kB, fct))

    B = 60
    out = {}
    kept = {}
    for mode, expect in (("adverse", "FAILED"), ("neutral", "UNDETERMINED"), ("favorable", "HELD")):
        LL = []
        D = synth(mode)
        S, pins, res, arms = _pipeline(D, LL.append, B, loao=(mode == "adverse"), min_anchors=2)
        out[mode] = (res, LL)
        kept[mode] = (S, arms)
        for kk in S["conv"]["B"]["draws"]:
            need(not (kk & S["missing"]), "convention B's R contains missing-prediction rows")
        need(S["missing"] and any(S["missing"] & kk for kk in S["conv"]["A"]["draws"]), "fixture has no missing rows in A's R")
        print("[selftest] fixture %-9s -> C1 %-13s (expected %s) Delta_W %+.2f [%+.2f, %+.2f] W_F %d mean W_R %.2f (%.0f s)"
              % (mode, res["c1"], expect, res["st"]["delta"], res["st"]["lo"], res["st"]["hi"], res["st"]["WF"],
                 res["st"]["WR_mean"], time.time() - t0), flush=True)
        need(res["c1"] == expect, (mode, res["c1"]))
    need(any("C1 FAILED (ADVERSE)" in s for s in out["adverse"][1]), 'check failed: any("C1 FAILED (ADVERSE)" in s for s in out["adverse"][1])')
    need(any("-> C1 UNDETERMINED: the interval contains 0." in s for s in out["neutral"][1]), 'check failed: any("-> C1 UNDETERMINED: the interval contains 0." in s for s in out["neutral"][1])')
    need(any("-> C1 HELD" in s for s in out["favorable"][1]), 'check failed: any("-> C1 HELD" in s for s in out["favorable"][1])')
    fav_c3u = out["favorable"][0]["c3_u"]
    need(fav_c3u["branch"] == "SINGULAR" and fav_c3u["status"] == "NO FIT (b1 unidentified: singular observed information)",
         fav_c3u["status"])
    need(any(s.lstrip().startswith("P5 ") and s.endswith("-> UNDETERMINED") for s in out["favorable"][1]), "favorable F has 0 events: P5 must read UNDETERMINED")
    print("[selftest] the 2-anchor fixtures are scored at a support threshold of 2 anchors (the registered 12 of 14 is"
          " executed on the crafted path below); convention B's R never holds a missing-prediction row, A's does", flush=True)

    # --workers determinism: the arm boards are identical at 1 and 2 processes
    D = synth("adverse")
    S = prepare(D, [].append, pins=synth_pins(D, B), B=B)
    a1 = run_arms(S, 1, [].append, B=B); a2 = run_arms(S, 2, [].append, B=B)
    need(a1 == a2, "arm boards differ between 1 and 2 workers")
    print("[selftest] --workers 2 reproduces --workers 1 on all %d arm boards (spawned processes)" % len(a1), flush=True)

    # ---- R2: removal (disconnection + floor) and the support trigger BOTH WAYS, end to end on a 4-anchor board
    LL = []
    D = synth("adverse", gamma_disconnect=True, delta_floor=True)
    S, pins, res, arms = _pipeline(D, LL.append, B, min_anchors=2)
    need(S["anchors"] == ["Alpha", "Beta", "Delta", "Gamma"], S["anchors"])
    need(res["c4"][0] == 1 and any("DISCONNECTED under the deployed filter: Gamma" in s for s in LL), res["c4"])
    need(any("BELOW THE 200-ROW FLOOR under the deployed filter: Delta" in s for s in LL), 'check failed: any("BELOW THE 200-ROW FLOOR under the deployed filter: Delta" in s for s in LL)')
    kept_g = sum(1 for r in S["u_rows"]["Gamma"] if r[0] in S["conv"]["A"]["keep"])
    need(kept_g >= ANCHOR_FLOOR, "Gamma must be removed by DISCONNECTION alone (kept %d)" % kept_g)
    need(not any(s.startswith("  -> BELOW THE") and "Gamma" in s for s in LL), 'check failed: not any(s.startswith(" -> BELOW THE") and "Gamma" in s for s in LL)')
    need(res["st"]["n_anchors"] == 2 and res["c1"] != TRIGGER_C1, 'check failed: res["st"]["n_anchors"] == 2 and res["c1"] != TRIGGER_C1')
    LL3 = []
    res3 = readout(S, arms, LL3.append, c3_reps=((40, 11), (40, 2026)), loao=False, min_anchors=3)
    need(res3["c1"] == TRIGGER_C1 and any("NOT EVALUATED" in s for s in LL3) and any("PRINTED," in s for s in LL3), 'check failed: res3["c1"] == TRIGGER_C1 and any("NOT EVALUATED" in s for s in LL3) and any("PRINTED," in s for s in LL3)')
    print("[selftest] R2 end to end: Gamma (disconnected) and Delta (below the floor) removed, 2 of 4 remain -> scored at a"
          " threshold of 2 (%s); UNDETERMINED BY TRIGGER at 3, falsifier not evaluated" % res["c1"], flush=True)

    # gate refusals on a fixture with perturbed pins
    D = synth("neutral")
    good = synth_pins(D, B)
    _expect_exit(lambda: prepare(D, [].append, pins=dict(good, established=good["established"] + 1), B=B), "[G1]", "G1")
    _expect_exit(lambda: prepare(D, [].append, pins=dict(good, keptA=good["keptA"] + 1), B=B), "[G2]", "G2")
    S = prepare(D, [].append, pins=good, B=B)
    cv = S["conv"]["A"]; tampered = set(cv["draws"][0]); tampered.discard(next(iter(tampered)))
    _expect_exit(lambda: check_g3(S["u_cells"], cv["f_counts"], tampered, 1, "A"), "[G3]", "G3")
    miss_row = next(iter(S["missing"]))
    _expect_exit(lambda: check_b_universe(set(S["conv"]["B"]["draws"][0]) | {miss_row}, S["missing"], 1), "[G3]",
                 "G3 convention-B universe")

    # ---- branch completion on crafted values (each through the SAME print function the run uses)
    LL = []; s2 = LL.append
    st_a = out["adverse"][0]["st"]
    # R2 (b) with the REGISTERED constant: 11 of 14 -> trigger; 12 of 14 -> scored
    need(c1_verdict(11, -9.0, -1.0) == TRIGGER_C1, 'check failed: c1_verdict(11, -9.0, -1.0) == TRIGGER_C1')
    need(c1_verdict(12, -9.0, -1.0) == "HELD" and c1_verdict(14, 1.0, 9.0) == "FAILED" and c1_verdict(12, -1.0, 1.0) == "UNDETERMINED", 'check failed: c1_verdict(12, -9.0, -1.0) == "HELD" and c1_verdict(14, 1.0, 9.0) == "FAILED" and c1_verdict(12, -1.0, 1.0) == "UNDETERMINED"')
    c1_lines(s2, dict(st_a, n_anchors=11), c1_verdict(11, st_a["lo"], st_a["hi"]))
    c1_lines(s2, dict(st_a, n_anchors=12), c1_verdict(12, st_a["lo"], st_a["hi"]))
    need(any("11 of the U anchors remain" in s for s in LL) and any("12 anchors remain >= 12" in s for s in LL), 'check failed: any("11 of the U anchors remain" in s for s in LL) and any("12 anchors remain >= 12" in s for s in LL)')
    falsifier_lines(s2, TRIGGER_C1, st_a)
    st0 = c1_stats(["x"], {"x": [("x", "a", "b")]}, {("x", "a", "b"): True}, {("x", "a", "b"): [False] * K_DRAWS})
    support_lines(s2, st0)
    for f in ("HELD", "FAILED", "UNDETERMINED"):
        falsifier_lines(s2, f, st_a)
    big = dict(st_a, deff=5.0, mde=30.0); small = dict(big, deff=1.2, mde=10.0)
    support_lines(s2, big); support_lines(s2, small)
    c2_line(s2, "crafted nominal < 3", 10, 1, 1, 1.3)
    c2_line(s2, "crafted 3 <= nominal < 9", 100, 4, 3, 5.0)
    c2_line(s2, "crafted nominal >= 9", 500, 12, 10, 10.0)
    # R1: no trigger on C3; the <= 14 flag is descriptive; NO FIT when no ddev
    need(c3_status(5.0, 0.01) == "REJECTED" and c3_status(1.0, 0.30) == "NOT REJECTED" and c3_status(5.0, 0.30) == "DISAGREE", 'check failed: c3_status(5.0, 0.01) == "REJECTED" and c3_status(1.0, 0.30) == "NOT REJECTED" and c3_status(5.0, 0.30) == "DISAGREE"')
    need(c3_status(float("nan"), float("nan")).startswith("NO FIT (b1 unidentified: non-finite"), 'check failed: c3_status(float("nan"), float("nan")).startswith("NO FIT (b1 unidentified: non-finite")')
    need(c3_status(float("inf"), 0.0).startswith("NO FIT (b1 unidentified: non-finite"), 'check failed: c3_status(float("inf"), 0.0).startswith("NO FIT (b1 unidentified: non-finite")')
    need(c3_status(1.0, 0.30, unident="complete separation in A: x").startswith("NO FIT (b1 unidentified: complete separation"), 'check failed: c3_status(1.0, 0.30, unident="complete separation in A: x").startswith("NO FIT (b1 unidentified: complete separation")')
    for ev_, dd, pb in ((10, 5.0, 0.01), (30, 5.0, 0.01), (30, 1.0, 0.30), (30, 5.0, 0.30)):
        c3_lines(s2, "X", ev_, 809, dict(b0=-2.6, b1=2.1, ddev=dd), [(pb, 600, 11)], c3_status(dd, pb))
    need(any("REJECTED by both" in s for s in LL) and any("descriptive flag" in s for s in LL), 'check failed: any("REJECTED by both" in s for s in LL) and any("descriptive flag" in s for s in LL)')
    c3_lines(s2, "X", 0, 809, None, [], c3_status(float("nan"), float("nan")))
    ovl_es, sep_es = _separation_selftest(s2, st_a)
    _singular_selftest(s2, fav_c3u["es"], ovl_es, sep_es, out["favorable"][1])

    # (g) D2 end to end: EVERY inner search of a full readout fails; the readout completes, every C3 fit reads NO FIT
    # (inner), P5 is UNDETERMINED, and C1 is bit-identical to the unfailed readout
    Sa, arms_a = kept["adverse"]
    saved = _INNER_IMPL[0]
    LLg = []
    fits0, inner0 = FIT_COUNT[0], HITS.get("C3.NO_FIT_INNER", 0)
    try:
        _INNER_IMPL[0] = _no_interior_inner
        res_g = readout(Sa, arms_a, LLg.append, c3_reps=((40, 11), (40, 2026)), loao=False, min_anchors=2)
    finally:
        _INNER_IMPL[0] = saved
    res_a = out["adverse"][0]
    need(res_g["c1"] == res_a["c1"] == "FAILED" and res_g["st"]["delta"] == res_a["st"]["delta"]
         and res_g["st"]["lo"] == res_a["st"]["lo"] and res_g["st"]["hi"] == res_a["st"]["hi"],
         "(g) C1 changed when the inner search failed: %r vs %r" % (res_g["c1"], res_a["c1"]))
    n_fits_g = FIT_COUNT[0] - fits0; n_inner_g = HITS.get("C3.NO_FIT_INNER", 0) - inner0
    need(bool(n_fits_g > 0) and n_inner_g == n_fits_g and res_g["c3_u"]["branch"] == "INNER_UNRESOLVED",
         "(g) fits %d, NO FIT (inner) %d, U %s" % (n_fits_g, n_inner_g, res_g["c3_u"]["status"]))
    p5g = [x for x in LLg if x.lstrip().startswith("P5 ")][0]
    need(p5g.endswith("-> UNDETERMINED"), p5g)
    print("[selftest] (g) every inner search failed in a full readout: completed (no refusal); C1 %s Delta_W %+.2f [%+.2f, %+.2f]"
          " identical to the unfailed readout; %d of %d fits read NO FIT (inner), U '%s...'; F %s; P5 UNDETERMINED"
          % (res_g["c1"], res_g["st"]["delta"], res_g["st"]["lo"], res_g["st"]["hi"], n_inner_g, n_fits_g,
             res_g["c3_u"]["status"][:70], res_g["c3"]["status"]), flush=True)
    c4_lines(s2, [("a", 0, True, 300)], [], 3, 920); c4_lines(s2, [("a", 5, False, 150)], ["a"], 5, 920, floored=["a"])
    held = dict(WF=14, WR_mean=30.0, delta=-16.0)
    miss = dict(WF=40, WR_mean=10.0, delta=+30.0)
    n0 = len(LL)
    predictions(s2, "HELD", held, (600, 1, 1.4), dict(fit=dict(ddev=2.0), status="NOT REJECTED"), (0, 15))
    predictions(s2, "FAILED", miss, (600, 9, 4.0), dict(fit=dict(ddev=6.0), status="REJECTED"), (2, 90))
    predictions(s2, TRIGGER_C1, held, (600, 1, 1.4), dict(fit=None, status="NO FIT"), (0, 15))
    p5 = [s for s in LL[n0:] if s.lstrip().startswith("P5 ")]
    need([s.rsplit("-> ", 1)[1] for s in p5] == ["HELD", "FAILED", "UNDETERMINED"], p5)
    print("[selftest] R1: P5 HELD on ddev 2.0, FAILED on 6.0, UNDETERMINED (never HELD) with no ddev; C3 has no trigger", flush=True)

    # write-once
    write_once(OUT, "\n".join(L) + "\n")
    _expect_exit(lambda: write_once(OUT, "second"), "[WRITE-ONCE]", "write-once")
    need(open(OUT, encoding="utf-8").read() != "second", 'check failed: open(OUT, encoding="utf-8").read() != "second"')

    sqlite3.connect = logged_connect
    one = check_connection_log(CONNECTIONS, X12_CACHE)
    assert_stack_judge_not_loaded()
    print("[selftest] sqlite3.connect: %d open(s), all under the tempdir or :memory: (%s); connection log %d entries, the"
          " synthetic stack cache exactly once as %s" % (len(opened), ", ".join(sorted({os.path.basename(x.split("?")[0])
                                                                                       for x in opened})),
                                                         len(CONNECTIONS), one.split("/")[-1]))
    wl = []
    w = check_witness(wl.append)
    print("[selftest]" + wl[0], flush=True)
    need(w == WITNESS_EXPECTED, "EXECUTION WITNESS %s != the pinned exact counts %s" % (w, WITNESS_EXPECTED))
    _expect_exit(lambda: check_witness([].append, counts=dict(w, assessments=w["fits"] - 1)), "[WITNESS]",
                 "assessments != fits")
    _expect_exit(lambda: check_witness([].append, expect_calls=43, counts=dict(w, calls=42)), "[WITNESS]", "42 of 43 calls")
    need(check_witness([].append, expect_calls=43, counts=dict(w, calls=43)) == dict(w, calls=43), "witness admission")
    print("[selftest] EXECUTION WITNESS EXACT: %s == pinned %s; the witness refuses assessments != fits and 42 of 43"
          " calls, admits 43 of 43" % (w, WITNESS_EXPECTED), flush=True)
    missing = [b for b in REGISTERED_BRANCHES if not HITS.get(b)]
    print("[selftest] branch execution (registered id: times executed):")
    for b in REGISTERED_BRANCHES:
        print("    %-26s %d" % (b, HITS.get(b, 0)))
    if missing:
        raise SystemExit("[selftest] FAILED: registered branches never executed: %s" % missing)
    print("[selftest] PASS: %d of %d registered branches executed; 3 C1 fixtures read FAILED / UNDETERMINED / HELD as built;"
          " R2 removal + trigger both ways; R1 P5 UNDETERMINED; R3 stub; R4 pin + bit identity; R6 WAL + B universe;"
          " G1 / G2 / G3 / write-once refusals executed; singular information (a) flat -> UNIDENTIFIED (I <= 0),"
          " (b) overlap -> IDENTIFIED, (c) separation -> UNIDENTIFIED (separation), (d) bound x8, (e) |b1*| < 1 -> h 1e-4,"
          " (f) four NO FIT mappings, (g) C1 unaffected by inner failure; D1 load_real synthetic open once; witness exact;"
          " %.0f s"
          % (len(REGISTERED_BRANCHES) - len(missing), len(REGISTERED_BRANCHES), time.time() - t0))


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--selftest", action="store_true")
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("--workers", type=int, default=1, help="processes for the 42 arm boards (deterministic per arm)")
    a = ap.parse_args(argv)
    if a.workers < 1:
        raise SystemExit("--workers must be >= 1")
    return a


if __name__ == "__main__":
    A_ = parse_args()
    check_build_pin()                         # ruling R4 (a): build()'s source hash asserted AT LAUNCH, every mode
    check_scipy_brent()                       # the inner search's documented tolerance, AT LAUNCH (never inside C3)
    if A_.selftest:
        selftest()
    elif A_.dry_run:
        main_dry(A_.workers)
    else:
        main_run(A_.workers)
