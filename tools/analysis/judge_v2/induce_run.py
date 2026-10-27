"""ARCH-V2-INDUCE-RUBRIC-1: the LIVE rubric inducer (registered at b44227f, docs/judge_v2_program.md L15964-L15973, under
the judge-design-specialist's ruling L15957-L15962). Mints ONE MCQ rubric artefact for E-J's $rubric slot. A RECIPE
COMPONENT: no rubric-value or accuracy claim.

LAUNCH SEQUENCE (the run-operator; the READY pins EXPECTED_PAYLOAD_SHA from the dry-run):
    python tools/analysis/judge_v2/induce_run.py --dry-run                 # assemble and print the payload; posts nothing
    python tools/analysis/judge_v2/induce_run.py --run --go --expect-payload-sha <sha from the dry-run / the READY>
    python tools/analysis/judge_v2/induce_run.py --selftest                # synthetic fixture, stub poster; also under -O
No pilot mode: the run is 1 call (at most 3).

WHAT IT DOES
  (1) opens the gen_view of record READ-ONLY through data_v2.views.open_generation("induce") (sealed file, -wal / -journal
      refused, mode=ro&immutable=1) and REFUSES unless its sha256_bytes is the registered
      690d06b8fc108ccf99f01f1b460e18a2e4847f6ecbd6ab51d242050a96d86fc2 (data root: TAXOARENA_DATA_ROOT, else this checkout);
      [RE-PIN 2026-09-24, forced by the author's redraw under CK-CLOSE-v2 (Amendments 19-20; split of record 5a3e756, R4
      MET e2623b4), not a re-selection: the views of record are now REG_ARCHV2-SPLIT-2_2929bd46..., gen_view
      c2930c609c67d6c7e1f8b8fbcd8f6f1970478a28f844d086d0b0db169d10c0ec, eval_view
      e35b7518878205837bfd16266dfdd8a6e76a226ed67957796d1d33cb72b5e369 (manifest sha256 912eaa5f...); seed, sort key,
      population, dedup, component rule and n unchanged; the D1 list rebuilt on the new eval_view]
  (2) selects the inputs with judge_v2.induction: TRAIN ONLY (GATE refused and counted by select_inputs' witness; EVAL and
      the sentinels (EVAL units) are absent from gen_view by construction and counted from its salted EVAL key set);
      the registered seed ARCH-V2-INDUCE-SELECT-1; n = 40; corpus type MCQ only; every stem AND option passes
      assert_induction_inputs, and the inputs equal gen_view's rows (check_inputs_bound). The ordered input_variant_ids,
      their sha256 of the sorted set (induction's input_variant_ids_sha256) and of the order, are written (mode "x")
      BEFORE the first post, and printed by the dry-run;
  (3) asserts and prints INDUCTION_SYSTEM sha256 4c4bf36f...23e7 (429 characters) and INDUCTION_USER_TEMPLATE sha256
      7ed21eba...f7481 (139 characters);
  (4) builds the body with rejudge_reasoning.payload_bytes after judge_v2.payload.configure_rr() (grok-4-1-fast-non-
      reasoning, cap 8192, temperature OMITTED, recorded "omitted"); --run REFUSES unless sha256(body) equals
      --expect-payload-sha (the registered payload); posts ONLY through rejudge_reasoning.call_judge_full;
  (5) ATTEMPTS (the registration): a FORMAL FAILURE is a non-JSON reply (no fence stripping, no repair), a key other than
      exactly "rubric", finish_reason length, content_filter, or the SHINGLE-8 verbatim-copy refusal. On a formal failure
      the SAME body is re-posted; at most 3 attempts; ALL attempts are recorded in the attempt cache; the FIRST VALID reply
      is of record; there is no best-of-n and no edit path. Three failures read UNDETERMINED (the decision goes to the
      author). A transport error (call_judge_full raising) is not a reply: it is recorded and the run STOPS (fail closed);
  (6) VALIDITY (zero calls): V1 the verbatim audit (SHINGLE 8, hits 0); V2 a leak check of the rubric text against EVAL
      key material from the eval_view of record (opened read-only through open_eval AFTER the reply exists; nothing from it
      reaches the prompt): E-J's loader.MATERIAL_FORMS["key"] renderings of every EVAL response's gt_raw and answer_text,
      the raw EVAL answer texts of >= leakage.MIN_MATERIAL characters, the reference marker, and E-J's machine-field
      marker rules; 0 hits REQUIRED; V3 the content-key counts (TRAIN candidates, GATE excluded, EVAL keys, EVAL hits,
      not-TRAIN); V4 the artefact written with mode "x" (judge_v2.induction.write_artefact), artefact_sha256 and
      rubric_sha256 printed. Any of V1-V4 failing: NO artefact of record is written;
  (7) ACCOUNTING: accepted_tests_ledger.guard before the first post (ceiling ARCH-V2-INDUCE-RUBRIC-1 = 3; the 4,000-match
      rule; the combined posting-day statement against 14,000), printed pass or refuse; the posted count appended to the
      day ledger after the run (also on a stop).
[CORRECTED 2026-09-24 by the judge-design-specialist's rulings on findings 1-3 (eabbf45, programme L15996-L16007),
insertion only; where this bracket and the text above differ, this bracket rules:
  (1) SELECTION: judge_v2.induction.select_inputs (amended) collapses candidate rows to distinct variant_id (duplicates
      asserted identical), sorts by the unchanged key, keeps the first variant per COMPONENT; the witness prints candidate
      rows, distinct variants, duplicates collapsed, variants skipped by component; a repeated variant / item / component
      is refused as a backstop. Disclosure of record: "selection corrected before the first call (duplicate corpus rows);
      the registered seed kept".
  (2) TRANSPORT ERRORS (an invocation that RAISES): logged in the cache (timestamp, exception class and message, payload
      sha, "TRANSPORT, no reply"), NOT an attempt; the launch stops fail-closed and writes transport_stop_<k>.txt; a
      relaunch (the same command) re-posts the IDENTICAL body (payload sha asserted against the cache; the ids never
      re-selected); own limit 3: the 3rd reads UNDETERMINED BY INSTRUMENT (outcome written; the falsifier does not fire;
      a further relaunch needs a registrar bracket). Every invocation, errored or not, is counted on the day ledger; the
      shared guard's (i) sums both kinds, so the runner reads (i) per kind (attempts <= 3, transport errors <= 3) and
      refuses on (ii) / (iii).
  (3) V2 ORDER: eval_view is opened through open_eval with expect_sha256 from the manifest of record ONLY after the valid
      reply is committed; the reply's commit time and the eval_view open time are printed in that order and checked; a
      flag set on open refuses any later call_judge_full in this process; a V2 failure is NEVER a re-post; stage "judge"
      is a mislabel accepted for this run only (an "audit" stage is queued).
  The attempt cache now lives in judge_v2/induce_cache.py (tables meta / attempt / transport / event).]
[CORRECTED 2026-09-24 on the READY review 6b65efe (READY_induce_rubric_1.md C1-C5) and the ruling on its C4, insertion only;
where this bracket and the text above differ, this bracket rules:
  C1  WRITE-AHEAD: before every call_judge_full a PENDING invocation row is committed; the cache's triggers refuse the
      INVOCATION itself (a call after a valid reply, a 4th attempt, a 4th transport error, an unresolved orphan) BEFORE any
      post. Each invocation is resolved by an attempt row or a transport row; an unresolved one found on a relaunch is an
      ORPHAN, recorded as a transport error "no reply recorded", which consumes the transport limit and is disclosed.
      Posts are counted in a holder the `finally` reads, so the day ledger gets every post (KeyboardInterrupt included).
      LEDGER (ruling 1 of the review): (a) the ceiling of record is 6 (3 attempts + 3 transport errors) in
      accepted_tests_ledger, and the shared guard's (i) REFUSES (no longer filtered); (b) per launch, the day ledgers'
      count for this test must EQUAL the invocations recorded in the cache (0 on a fresh launch), else the launch REFUSES.
  C2  V2 also checks the EVAL REFERENCE rows: each row rendered "(<answer>) <option text>" in its SOLVER's ordering (the
      solver's response row, as loader.py renders it) and its option text, each kept when >= 12 characters.
  C4  POPULATION NARROWED (ruling on C4): only mmlu-pro-v2 MC_LETTER TRAIN variant rows are candidates (POPULATION); the
      seed, the sort key, the dedup, the component rule and n = 40 are unchanged; the witness prints the TRAIN rows
      excluded by corpus version and contract; the artefact is labelled "MCQ rubric, population mmlu-pro-v2 TRAIN" and its
      manifest records the population. Disclosure: "population narrowed to the judged corpus after the input list's source
      mix was seen; seed kept; no call".
  C5  the outcome discloses that the dry-run process opened eval_view before any call to size V2's material (counts only),
      and that the ruling on finding 3 (i) binds the run's process.
  The dry-run also prints the count of EVAL variant stems that share an 8-token run with the user turn.]
[CORRECTED 2026-09-24 by the ruling D1 (overlap exclusion; the registrar inserting), insertion only: the run and the
dry-run read the zero-call overlap audit's list (judge_v2.induce_overlap_audit, EXCL_REL), refusing a list whose own sha
is not EXCL_SHA or that was built on another eval_view / gen_view / threshold / population; the selection walks the
unchanged order, skips the listed variants (run of >= 8 consecutive tokens with one EVAL text) and REPLACES them; the
witness prints the inputs kept, the inputs replaced and the last rank; the artefact manifest records the list's sha. The
run process never opens eval_view before its reply: the list is a file of TRAIN ids, run lengths and EVAL variant ids.
Disclosure: "7 inputs sharing >= 8 consecutive tokens with EVAL texts excluded and replaced in sort order before the first
call; seed kept".]
OUTPUTS (write-once; a present path REFUSES the launch): <root>/experiment_results/archv2/induce_rubric_1/
    attempts.db                        the attempt cache (append-only: UPDATE / DELETE / a 4th attempt / an attempt after a
                                       valid one ABORT; created through data_v2.ro.create_new)
    input_variant_ids.json             the ordered ids, the sorted-set sha256 and the ordered sha256
    rubric_mcq_ARCH-V2-INDUCE-RUBRIC-1.json   the artefact of record (only when a valid reply passes V1-V4)
    outcome.txt                        attempts, P1, P2, the falsifier, V1-V4 (mode "x")
"""
import argparse
import hashlib
import json
import os
import re
import sys
import sqlite3
import zlib
from datetime import datetime, timezone

if __name__ == "__main__" and not __package__:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = "judge_v2"
    import judge_v2  # noqa: F401

from ._base import REFERENCE_MARKER, dv2views, git_blob_lf, refuse, rr, sha256_text, ROOT  # noqa: E402
from . import induce_cache as IC  # noqa: E402
from . import induce_overlap_audit as OA  # noqa: E402
from . import induction as I  # noqa: E402
from . import leakage as L  # noqa: E402
from . import loader as LD  # noqa: E402
from . import payload as P  # noqa: E402

TEST = "ARCH-V2-INDUCE-RUBRIC-1"
SELECT_REGISTRATION = "ARCH-V2-INDUCE-SELECT-1"
SEED = "ARCHV2-INDUCE-1:5abb79f55c3719d122b5310151f975493609f37b"
N = 40
CORPUS_TYPE = "mcq"
MAX_ATTEMPTS = 3
MAX_TRANSPORT = 3        # ruling on finding 2: errored invocations have their own limit
SPLIT_DIR = "data_v2/REG_ARCHV2-SPLIT-2_2929bd46aa271d883050bfe735f96e621ed55fd2"   # re-pin: SPLIT-1 c0303156 -> SPLIT-2
GEN_VIEW = SPLIT_DIR + "/gen_view_REG.db"
EVAL_VIEW = SPLIT_DIR + "/eval_view_REG.db"
GEN_SHA = "c2930c609c67d6c7e1f8b8fbcd8f6f1970478a28f844d086d0b0db169d10c0ec"      # SPLIT-2 manifest of record (was 690d06b8, b44227f)
EVAL_SHA = "e35b7518878205837bfd16266dfdd8a6e76a226ed67957796d1d33cb72b5e369"     # SPLIT-2 manifest of record (was 7c284b15, b51eb71)
MANIFEST = "data_v2/manifests/REG_ARCHV2-SPLIT-2_2929bd46aa271d883050bfe735f96e621ed55fd2.json"
SYSTEM_SHA = "4c4bf36f61f43f37f0057ce31e96b086528735aae338a60c1e19432a009823e7"
USER_TEMPLATE_SHA = "7ed21eba7b9b9e13222b275400d0808706a1a4217b7f30db87391ea2fb9f7481"
OUT_REL = "experiment_results/archv2/induce_rubric_1"
EXCL_REL = "experiment_results/archv2/induce_rubric_1_audit/overlap_exclusions_split2.json"   # induce_overlap_audit's output
EXCL_SHA = "68c0b960a4a7bedc76db079cdc2e0f01d5ef0b2fc4304f5486706cb27b71418a"     # SPLIT-2 (was a4f6e2b7 on SPLIT-1); the pinned list_sha256 of the overlap exclusion list of record (ruling D1)
DISCLOSURE_D1 = ("%d inputs sharing >= 8 consecutive tokens with EVAL texts excluded and replaced in sort order before the"
                 " first call; seed kept")      # the count is the witness's "replaced" (7 on the view of record)
FORMAL_FAILURES = ("NON_JSON", "KEY", "LENGTH", "CONTENT_FILTER", "VERBATIM")
P1_POINT = 0.8


def _data_root():
    return os.environ.get("TAXOARENA_DATA_ROOT", ROOT)


class Paths:
    def __init__(self, data_root=None, out_dir=None):
        root = data_root or _data_root()
        self.gen = os.path.join(root, *GEN_VIEW.split("/"))
        self.eval = os.path.join(root, *EVAL_VIEW.split("/"))
        self.manifest = os.path.join(ROOT, *MANIFEST.split("/"))
        self.out = out_dir or os.path.join(ROOT, *OUT_REL.split("/"))
        self.cache = os.path.join(self.out, "attempts.db")
        self.ids = os.path.join(self.out, "input_variant_ids.json")
        self.artefact = os.path.join(self.out, "rubric_mcq_%s.json" % TEST)
        self.outcome = os.path.join(self.out, "outcome.txt")
        self.excl = os.path.join(ROOT, *EXCL_REL.split("/"))
        self.check_manifest = True


def check_manifest(paths, gen_sha, eval_sha, out=print):
    """The manifest of record (b51eb71) names both views with the pinned shas (a cross-check of the constants)."""
    if not os.path.isfile(paths.manifest):
        refuse("the manifest of record %s is missing" % paths.manifest)
    m = json.load(open(paths.manifest, encoding="utf-8"))
    got = {o.get("kind"): o.get("sha256_bytes") for o in m.get("outputs", [])}
    out("[INDUCE-RUN] manifest of record %s: gen_view %s, eval_view %s" % (os.path.basename(paths.manifest),
                                                                          got.get("gen_view"), got.get("eval_view")))
    if got.get("gen_view") != gen_sha or got.get("eval_view") != eval_sha:
        refuse("the manifest of record does not name the pinned view shas (gen %s, eval %s)" % (gen_sha, eval_sha))


# ── (3) the prompt pins ──────────────────────────────────────────────────────────────────

def check_prompt_pins(out=print):
    got_s, got_u = sha256_text(I.INDUCTION_SYSTEM), sha256_text(I.INDUCTION_USER_TEMPLATE)
    out("[INDUCE-RUN] INDUCTION_SYSTEM sha256 %s (%d chars; registered %s) | INDUCTION_USER_TEMPLATE sha256 %s (%d chars;"
        " registered %s)" % (got_s, len(I.INDUCTION_SYSTEM), SYSTEM_SHA, got_u, len(I.INDUCTION_USER_TEMPLATE),
                             USER_TEMPLATE_SHA))
    if got_s != SYSTEM_SHA or got_u != USER_TEMPLATE_SHA:
        refuse("the induction prompt constants are not the registered ones (system %s, user template %s)" % (got_s, got_u))


# ── (1)(2) selection ─────────────────────────────────────────────────────────────────────

DISCLOSURE = "selection corrected before the first call (duplicate corpus rows); the registered seed kept"
DISCLOSURE_C4 = "population narrowed to the judged corpus after the input list's source mix was seen; seed kept; no call"
DISCLOSURE_C5 = ("the dry-run process opened eval_view before any call to size V2's material (counts only); the ruling on"
                 " finding 3 (i) binds the run's process")
POPULATION = {"corpus_version": "mmlu-pro-v2", "contracts": ["MC_LETTER"]}
ARTEFACT_LABEL = "MCQ rubric, population mmlu-pro-v2 TRAIN"


def select(gen_path, gen_sha, seed, registration, out=print, excl=None):
    """Open the gen_view of record (open_generation("induce"), sha-pinned), select the TRAIN inputs (judge_v2.induction as
    amended by the ruling on finding 1: distinct variant_id, first per component) and run every content-key check.
    Returns (inputs, witness, check, gen_meta, seed label). A repeated variant, item or component is REFUSED (backstop)."""
    label = I.resolve_seed(seed, registration)
    conn = dv2views.open_generation("induce", gen_path, gen_sha)
    witness = {}
    try:
        gmeta = dict(conn.execute("SELECT key, value FROM meta"))
        excl_set, excl_rec = excl if excl is not None else (None, None)
        if excl_set is None:
            refuse("select: the overlap exclusion list (ruling D1) is required")
        base = [r["variant_id"] for r in I.select_inputs(conn, CORPUS_TYPE, N, seed, I.DEFAULT_SIDES, None, POPULATION)]
        chosen = I.select_inputs(conn, CORPUS_TYPE, N, seed, I.DEFAULT_SIDES, witness, POPULATION, excl_set)
        kept = len(set(base) & {r["variant_id"] for r in chosen})
        witness.update({"kept_from_unexcluded": kept, "replaced": N - kept, "exclusion_list_sha256": excl_rec["list_sha256"]})
        if any(r["variant_id"] in excl_set for r in chosen):
            refuse("select: an excluded variant reached the selection")
        if len(chosen) != N:
            refuse("selection: %d inputs, the registration says n = %d" % (len(chosen), N))
        stems = [r["stem"] for r in chosen]
        opts = I._option_texts(chosen)
        check = I.assert_induction_inputs(conn, stems, I.DEFAULT_SIDES, option_texts=opts)
        I.check_inputs_bound(conn, chosen, CORPUS_TYPE)
        comps = {r["item_id"]: c for r in chosen for (c,) in
                 conn.execute("SELECT component_id FROM side WHERE item_id=?", (r["item_id"],))}
        srcs = sorted({x for r in chosen for (x,) in conn.execute(
            "SELECT DISTINCT source FROM source_row WHERE variant_id=?", (r["variant_id"],))})
        ctrs = sorted({r["contract_id"] for r in chosen})
    finally:
        conn.close()
    nv, ni, nc = len({r["variant_id"] for r in chosen}), len({r["item_id"] for r in chosen}), len(set(comps.values()))
    if not (nv == ni == nc == len(chosen)):
        refuse("selection: %d rows, %d distinct variants, %d items, %d components: the ruling's 40 distinct components are"
               " not met" % (len(chosen), nv, ni, nc))
    out("[INDUCE-RUN] population %s (%s); TRAIN rows excluded by corpus version and contract %s; the inputs' contracts %s,"
        " sources %s" % (json.dumps(POPULATION, sort_keys=True), DISCLOSURE_C4,
                         json.dumps(witness.get("excluded_by_population", {}), sort_keys=True), ctrs, srcs))
    out("[INDUCE-RUN] selection (%s): seed %s (%s); candidate rows %d, distinct variants %d, duplicates collapsed %d,"
        " variants skipped by component %d; %d inputs = %d variants = %d items = %d components; REFUSED and counted: GATE %d,"
        " other non-TRAIN %d; EVAL keys in the salted set %s (EVAL and sentinel rows are absent from gen_view); content-key"
        " check %d stems + %d option texts: EVAL hits %d, not TRAIN %d" % (
            DISCLOSURE, seed, label, witness["candidate_rows"], witness["distinct_variants"],
            witness["duplicates_collapsed"], witness["skipped_by_component"], len(chosen), nv, ni, nc,
            witness["gate_excluded"], witness["other_excluded"], gmeta.get("eval_key_count"), check["n_texts"],
            check["n_option_texts"], check["eval_hits"], check["not_gen_side"]))
    witness["input_sources"], witness["input_contracts"] = srcs, ctrs
    out("[INDUCE-RUN] overlap exclusion (ruling D1): list sha256 %s (%d excluded TRAIN variants, run >= %d); in the order:"
        " %d inputs kept, %d replaced, last rank %d (%s)" % (
            excl_rec["list_sha256"], len(excl_set), OA.THRESHOLD, witness["kept_from_unexcluded"], witness["replaced"],
            witness.get("last_rank", N), DISCLOSURE_D1 % witness["replaced"]))
    return chosen, witness, check, gmeta, label


def ids_record(chosen):
    ids = [r["variant_id"] for r in chosen]
    return {"registration": TEST, "selection_registration": SELECT_REGISTRATION, "n": len(ids), "input_variant_ids": ids,
            "input_variant_ids_sha256": sha256_text("\n".join(sorted(ids))),
            "input_variant_ids_ordered_sha256": sha256_text("\n".join(ids)), "disclosure": DISCLOSURE,
            "disclosure_population": DISCLOSURE_C4, "population": POPULATION, "artefact_label": ARTEFACT_LABEL}


# ── (4) the payload ──────────────────────────────────────────────────────────────────────

def build_payload(chosen):
    P.configure_rr()
    system, user = I.build_prompt(CORPUS_TYPE, chosen)
    if system != I.INDUCTION_SYSTEM:
        refuse("the built system prompt is not INDUCTION_SYSTEM")
    body = rr.payload_bytes(system, user)
    d = json.loads(body.decode("utf-8"))
    if list(d) != P.BODY_KEYS or d["model"] != P.JUDGE_REQUESTED or d["max_tokens"] != P.CAP or "temperature" in d:
        refuse("the induction body is not model / max_tokens / messages with the v2 judge, cap 8192 and no temperature")
    return system, user, body, hashlib.sha256(body).hexdigest()


# ── (5) attempts ─────────────────────────────────────────────────────────────────────────

def classify(content, finish_reason, chosen):
    """-> (failure class or None if VALID, the parsed rubric or None). No repair, no fence stripping: the reply is json.loads'
    input verbatim, exactly as judge_v2.induction.induce reads it."""
    if finish_reason == "content_filter":
        return "CONTENT_FILTER", None
    if finish_reason == "length":
        return "LENGTH", None
    try:
        d = json.loads(content)
    except (TypeError, ValueError):
        return "NON_JSON", None
    if not isinstance(d, dict) or set(d) != {"rubric"} or not isinstance(d["rubric"], str) or not d["rubric"].strip():
        return "KEY", None
    if I.verbatim_audit(d["rubric"], chosen):
        return "VERBATIM", None
    return None, d["rubric"]


# ruling on finding 3 (i): once eval_view is opened, this PROCESS makes no call_judge_full invocation (flag set on open)
_EVAL_OPENED = {"at": None}


def guarded(call_full):
    def g(system, user):
        if _EVAL_OPENED["at"] is not None:
            refuse("a call_judge_full invocation AFTER eval_view was opened (at %s) is refused (ruling on finding 3 (i))"
                   % _EVAL_OPENED["at"])
        return call_full(system, user)
    return g


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _event(conn, what, detail=""):
    at = _now()
    conn.execute("INSERT INTO event (at, what, detail) VALUES (?,?,?)", (at, what, detail))
    conn.commit()
    return at


def _write_ahead(conn, sha):
    """Insert and commit the PENDING invocation row BEFORE the post (READY C1). The cache's triggers refuse the invocation
    itself (a call after a valid reply, a 4th attempt, a 4th transport error, an unresolved orphan): nothing is posted."""
    seq = IC.state(conn)["n_invocations"] + 1
    try:
        conn.execute("INSERT INTO invocation VALUES (?,?,?,?)", (seq, _now(), sha, "PENDING"))
        conn.commit()
    except sqlite3.DatabaseError as e:
        conn.rollback()
        refuse("the attempt cache REFUSES invocation %d BEFORE any post: %s" % (seq, e))
    return seq


def resolve_orphans(conn, out=print):
    """On a relaunch: every invocation with no attempt and no transport row (posted, then the process died or the
    bookkeeping raised) becomes a TRANSPORT error 'no reply recorded': it consumes the transport limit and is disclosed."""
    st = IC.state(conn)
    for seq in st["orphans"]:
        n = IC.state(conn)["n_transport"] + 1
        if n > MAX_TRANSPORT:
            refuse("orphan invocation %d cannot be recorded: the transport limit is already reached" % seq)
        sha = conn.execute("SELECT payload_sha256 FROM invocation WHERE seq=?", (seq,)).fetchone()[0]
        conn.execute("INSERT INTO transport VALUES (?,?,?,?,?,?,?)", (n, seq, _now(), sha, "ORPHAN",
                                                                    "no reply recorded for invocation %d" % seq,
                                                                    IC.ORPHAN_NOTE))
        conn.commit()
        _event(conn, "orphan_resolved", "invocation %d -> transport error %d of %d" % (seq, n, MAX_TRANSPORT))
        out("[INDUCE-RUN] invocation %d was POSTED with no reply recorded (an orphan): counted as TRANSPORT ERROR %d of %d"
            " (%s)" % (seq, n, MAX_TRANSPORT, IC.ORPHAN_NOTE))
    return len(st["orphans"])


def attempts(conn, call_full, system, user, body, sha, chosen, out=print, posted=None):
    """Post the SAME body until the first VALID reply; attempts continue the cache's numbering (1..3). Before EVERY post a
    PENDING invocation row is committed (write-ahead); `posted["n"]` is incremented before the call, so the caller's
    `finally` ledgers every post even when this function raises (KeyboardInterrupt included). A RAISING invocation is a
    TRANSPORT error: logged (timestamp, class and message, payload sha, "TRANSPORT, no reply"), it does NOT consume an
    attempt, and the launch STOPS. Returns (new attempt rows, valid row or None, transport seq or None)."""
    posted = posted if posted is not None else {"n": 0}
    st = IC.state(conn)
    rows, valid = [], None
    call = guarded(call_full)
    for k in range(st["n_attempts"] + 1, MAX_ATTEMPTS + 1):
        if rr.payload_bytes(system, user) != body or hashlib.sha256(body).hexdigest() != sha:
            refuse("attempt %d: the body to post is not the registered body" % k)
        inv = _write_ahead(conn, sha)
        try:
            posted["n"] += 1
            content, provider, ctoks, lat, finish, msg = call(system, user)
        except Exception as e:  # noqa: BLE001  (SystemExit / KeyboardInterrupt are not Exceptions: they propagate)
            seq = IC.state(conn)["n_transport"] + 1
            conn.execute("INSERT INTO transport VALUES (?,?,?,?,?,?,?)", (seq, inv, _now(), sha, type(e).__name__,
                                                                        str(e)[:500], "TRANSPORT, no reply"))
            conn.commit()
            _event(conn, "transport_stop", "%d of %d" % (seq, MAX_TRANSPORT))
            out("[INDUCE-RUN] invocation %d: TRANSPORT ERROR %d of %d (%s: %s), payload sha256 %s, TRANSPORT, no reply: the"
                " launch STOPS fail-closed; the attempt is not consumed" % (inv, seq, MAX_TRANSPORT, type(e).__name__,
                                                                           str(e)[:120], sha))
            return rows, None, seq
        msg = msg or {}
        cls, _rubric = classify(content, finish, chosen)
        raw = content if content is not None else (msg.get("_refusal") or "")
        row = {"attempt_no": k, "payload_sha256": sha, "reply_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
               "finish_reason": finish, "response_id": msg.get("_response_id"), "provider": provider,
               "completion_tokens": ctoks, "failure_class": cls, "reply_text": raw}
        posted_at = _now()
        conn.execute("INSERT INTO attempt (attempt_no, invocation_seq, posted_at, committed_at, payload_sha256, body_zlib,"
                     " reply_text, reply_sha256, finish_reason, response_id, provider, completion_tokens, latency_s,"
                     " failure_class) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                     (k, inv, posted_at, _now(), sha, zlib.compress(body, 6), raw, row["reply_sha256"], finish,
                      row["response_id"], provider, ctoks, float(lat) if isinstance(lat, (int, float)) else None, cls))
        conn.commit()
        row["committed_at"] = _event(conn, "reply_committed" if cls is None else "attempt_committed",
                                     "attempt %d %s" % (k, cls or "VALID"))
        rows.append(row)
        out("[INDUCE-RUN] attempt %d of %d (invocation %d): finish_reason %r, response id %r, reply sha256 %s -> %s" % (
            k, MAX_ATTEMPTS, inv, finish, row["response_id"], row["reply_sha256"][:16],
            cls or "VALID (the reply of record)"))
        if cls is None:
            valid = row
            break
    return rows, valid, None


class Replay:
    """The model call handed to judge_v2.induction.induce AFTER the live attempt: it returns the stored reply of record
    and asserts the prompt is the posted one (zero calls; induce then re-runs the selection, the content-key checks and
    the verbatim audit and builds the artefact in its one format)."""

    def __init__(self, system, user, row, of_record):
        self.system, self.user, self.row = system, user, row
        self.calls = 0
        self.provenance = {"model": P.JUDGE_REQUESTED, "provider": row["provider"], "response_id": row["response_id"],
                           "finish_reason": row["finish_reason"], "attempt_of_record": row["attempt_no"],
                           "reply_sha256": row["reply_sha256"], "payload_sha256": row["payload_sha256"],
                           "max_tokens": P.CAP, "temperature_label": P.TEMPERATURE_LABEL, "of_record": of_record}

    def __call__(self, system, user):
        self.calls += 1
        if self.calls != 1 or system != self.system or user != self.user:
            refuse("replay: the artefact's prompt differs from the posted prompt (or a second call)")
        return self.row["reply_text"]


# ── (6) validity ─────────────────────────────────────────────────────────────────────────

def open_eval_for_audit(eval_path, eval_sha, conn=None, out=print):
    """Ruling on finding 3: the eval_view of record through data_v2.views.open_eval, expect_sha256 = the manifest of record's;
    the FLAG is set on open (no call_judge_full afterwards in this process); the open time is logged. Stage "judge" is a
    MISLABEL accepted for this run only (the ruling's (iv); an "audit" stage is queued)."""
    ev = dv2views.open_eval("judge", eval_path, eval_sha)
    _EVAL_OPENED["at"] = _now()
    if conn is not None:
        _event(conn, "eval_view_opened", "%s sha256 %s" % (os.path.basename(eval_path), eval_sha))
    out("[INDUCE-RUN] eval_view opened at %s: %s sha256_bytes %s (stage 'judge': a mislabel accepted for this run only;"
        " no call_judge_full is made after this point)" % (_EVAL_OPENED["at"], os.path.basename(eval_path), eval_sha))
    return ev


def _norm_text(x):
    return " ".join(str(x).casefold().split())


def reference_material(ev):
    """C2: every EVAL reference row rendered "(<answer>) <option text>" in its SOLVER's ordering (the solver's response
    row for the reference's legacy qid and variant, data_v2.ingest.SOLVER_MODEL, as loader.py renders it), and the option
    text itself; each kept when >= leakage.MIN_MATERIAL characters. Returns (set, counts)."""
    solver = {}
    for cv, q, v, sha in ev.execute("SELECT corpus_version, legacy_qid, seen_ck, options_ordered_sha FROM response WHERE"
                                    " model=?", (LD.dv2ingest.SOLVER_MODEL,)):
        solver[(cv, q, v)] = sha
    refs, n_rows, n_rendered, n_skipped = set(), 0, 0, 0
    for cv, vid, q, ans in ev.execute("SELECT corpus_version, variant_id, legacy_qid, answer FROM reference"):
        n_rows += 1
        a = (ans or "").strip()
        sha = solver.get((cv, q, vid))
        opts = LD._options_list(ev, sha) if sha is not None else None
        if not opts or not (len(a) == 1 and a in LD.LETTERS and LD.LETTERS.index(a) < len(opts)):
            n_skipped += 1
            if len(_norm_text(a)) >= L.MIN_MATERIAL:
                refs.add(_norm_text(a))
            continue
        n_rendered += 1
        for x in (LD.render_reference(a, opts), opts[LD.LETTERS.index(a)]):
            if len(_norm_text(x)) >= L.MIN_MATERIAL:
                refs.add(_norm_text(x))
    return refs, {"reference_rows": n_rows, "rendered": n_rendered, "not_renderable": n_skipped, "kept": len(refs)}


def eval_material(ev, eval_name, out=print):
    """V2's EVAL key material from an OPEN eval_view connection (closed by the caller): gt_raw / answer_text key
    renderings (loader.MATERIAL_FORMS), answer texts >= 12 characters, the EVAL reference rows (reference_material), the
    reference marker and the machine-field marker rules."""
    forms, texts, n_rows = set(), set(), 0
    for gt, at in ev.execute("SELECT DISTINCT gt_raw, answer_text FROM response"):
        n_rows += 1
        for v in (gt, at):
            if v:
                for f in LD.MATERIAL_FORMS["key"]:
                    forms.add(" ".join(f.format(v=v).casefold().split()))
        if at and len(" ".join(at.casefold().split())) >= L.MIN_MATERIAL:
            texts.add(" ".join(at.casefold().split()))
    refs, rc = reference_material(ev)
    out("[INDUCE-RUN] V2 material from %s: %d distinct (gt_raw, answer_text) pairs -> %d key renderings, %d answer texts of"
        " >= %d characters; EVAL reference rows %d (rendered in the solver's ordering %d, not renderable %d) -> %d reference"
        " strings; the reference marker, %d marker rules" % (eval_name, n_rows, len(forms), len(texts), L.MIN_MATERIAL,
                                                             rc["reference_rows"], rc["rendered"], rc["not_renderable"],
                                                             rc["kept"], len(L.MARKER_RULES)))
    return {"forms": forms, "texts": texts, "refs": refs, "ref_counts": rc}


def leak_check(rubric, material):
    """V2: the hits of the rubric text against the EVAL key material ([] passes)."""
    t = " ".join(rubric.casefold().split())
    hits = ["form:" + f for f in material["forms"] if f in t]
    hits += ["answer_text:" + x[:40] for x in material["texts"] if x in t]
    hits += ["reference:" + x[:40] for x in material.get("refs", ()) if x in t]
    if REFERENCE_MARKER.casefold() in rubric.casefold() or re.search(r"\[\s*Reference solution", rubric, re.I):
        hits.append("reference_marker")
    for name, rx in L._RULES:
        if rx.search(rubric):
            hits.append("marker:" + name)
    return sorted(hits)


# ── the launch ───────────────────────────────────────────────────────────────────────────

def _manifest_eval_sha(paths, eval_sha):
    if not paths.check_manifest:
        return eval_sha
    m = json.load(open(paths.manifest, encoding="utf-8"))
    got = {o.get("kind"): o.get("sha256_bytes") for o in m.get("outputs", [])}
    if got.get("eval_view") != EVAL_SHA:
        refuse("the manifest of record names eval_view %s, not the pinned %s" % (got.get("eval_view"), EVAL_SHA))
    return got["eval_view"]


def load_exclusions(paths, excl_sha, eval_sha, gen_sha, out=print):
    ex, rec = OA.load(paths.excl, excl_sha, eval_sha, gen_sha)
    out("[INDUCE-RUN] overlap exclusion list %s: sha256 %s = the pinned; built on eval_view %s; %d excluded" % (
        os.path.basename(paths.excl), rec["list_sha256"], rec["eval_view_sha256_bytes"], len(ex)))
    return ex, rec


def dry_run(paths=None, seed=SEED, registration=SELECT_REGISTRATION, gen_sha=GEN_SHA, eval_sha=EVAL_SHA, out=print,
            excl_sha=None):
    paths = paths or Paths()
    out("[INDUCE-RUN] %s DRY-RUN (posts nothing): gen_view %s (registered sha256_bytes %s)" % (TEST, paths.gen, gen_sha))
    if paths.check_manifest:
        check_manifest(paths, gen_sha, eval_sha, out)
    eval_sha = _manifest_eval_sha(paths, eval_sha)
    check_prompt_pins(out)
    excl = load_exclusions(paths, excl_sha or EXCL_SHA, eval_sha, gen_sha, out)
    chosen, witness, check, gmeta, label = select(paths.gen, gen_sha, seed, registration, out, excl)
    rec = ids_record(chosen)
    system, user, body, sha = build_payload(chosen)
    out("[INDUCE-RUN] input_variant_ids: n %d, sorted-set sha256 %s, ordered sha256 %s" % (
        rec["n"], rec["input_variant_ids_sha256"], rec["input_variant_ids_ordered_sha256"]))
    out("[INDUCE-RUN] payload: %d bytes, sha256 %s (model %s, max_tokens %d, temperature omitted); system sha256 %s, user"
        " sha256 %s" % (len(body), sha, P.JUDGE_REQUESTED, P.CAP, sha256_text(system), sha256_text(user)))
    out("[INDUCE-RUN] user turn (first 600 chars):\n" + user[:600])
    ev = open_eval_for_audit(paths.eval, eval_sha, None, out)
    try:
        mat = eval_material(ev, os.path.basename(paths.eval), out)
        sh = set()
        ut = I._tokens(user)
        sh.update(tuple(ut[i:i + I.SHINGLE]) for i in range(len(ut) - I.SHINGLE + 1))
        n_ev = n_hit = 0
        for (stem,) in ev.execute("SELECT DISTINCT stem FROM variant"):
            n_ev += 1
            t = I._tokens(stem)
            if any(tuple(t[i:i + I.SHINGLE]) in sh for i in range(len(t) - I.SHINGLE + 1)):
                n_hit += 1
        out("[INDUCE-RUN] EVAL variant stems sharing an %d-token run with the user turn: %d of %d (the review's row 4 count"
            " at the narrowed population; V1's audit refuses a rubric that copies one)" % (I.SHINGLE, n_hit, n_ev))
    finally:
        ev.close()
    return {"payload_sha256": sha, "ids": rec, "material_sizes": (len(mat["forms"]), len(mat["texts"])),
            "witness": witness, "check": check, "body": body, "ref_counts": mat["ref_counts"], "overlap": (n_hit, n_ev)}


def _launch_state(paths, rec, sha):
    """'fresh' (no output exists) or 'relaunch' (a TRANSPORT stop left the cache: the SAME ids, the SAME body, no valid
    reply, fewer than 3 attempts and fewer than 3 transport errors, no outcome and no artefact). Anything else REFUSES."""
    if not os.path.exists(paths.cache):
        for p in (paths.ids, paths.artefact, paths.outcome):
            if os.path.exists(p):
                refuse("%s exists without an attempt cache: refused" % p)
        return "fresh", None
    for p in (paths.artefact, paths.outcome):
        if os.path.exists(p):
            refuse("%s exists: the run reached its outcome; every output is written once" % p)
    old = json.load(open(paths.ids, encoding="utf-8")) if os.path.exists(paths.ids) else None
    if old is None or old.get("input_variant_ids") != rec["input_variant_ids"]:
        refuse("relaunch: the input ids differ from the first launch's (a relaunch never re-selects)")
    conn = IC.reopen(paths.cache)
    st = IC.state(conn)
    if st["meta"].get("payload_sha256") != sha:
        conn.close()
        refuse("relaunch: the payload sha256 %s is not the first launch's %s (the IDENTICAL body is re-posted, asserted)"
               % (sha, st["meta"].get("payload_sha256")))
    if st["valid"] or st["n_attempts"] >= MAX_ATTEMPTS:
        conn.close()
        refuse("relaunch: the run already has %s" % ("a valid reply" if st["valid"] else "3 attempts"))
    if st["n_transport"] >= MAX_TRANSPORT:
        conn.close()
        refuse("relaunch: %d transport errors: UNDETERMINED BY INSTRUMENT; a further relaunch needs a registrar bracket"
               % st["n_transport"])
    if st["n_transport"] + len(st["orphans"]) > MAX_TRANSPORT:
        conn.close()
        refuse("relaunch: %d transport error(s) and %d orphan invocation(s) exceed the transport limit %d"
               % (st["n_transport"], len(st["orphans"]), MAX_TRANSPORT))
    return "relaunch", conn


def run(call_full, expect_payload_sha, paths=None, seed=SEED, registration=SELECT_REGISTRATION, gen_sha=GEN_SHA,
        eval_sha=EVAL_SHA, ledger_dir=None, atl=None, out=print, excl_sha=None):
    """The live launch (call_full = rejudge_reasoning.call_judge_full in production; a stub in the selftest)."""
    paths = paths or Paths()
    if not callable(call_full):
        refuse("run: call_full must be rejudge_reasoning.call_judge_full (or the selftest's stub)")
    if paths.check_manifest:
        check_manifest(paths, gen_sha, eval_sha, out)
    eval_sha = _manifest_eval_sha(paths, eval_sha)
    check_prompt_pins(out)
    excl = load_exclusions(paths, excl_sha or EXCL_SHA, eval_sha, gen_sha, out)
    chosen, witness, check, gmeta, label = select(paths.gen, gen_sha, seed, registration, out, excl)
    rec = ids_record(chosen)
    system, user, body, sha = build_payload(chosen)
    out("[INDUCE-RUN] payload sha256 %s; registered (--expect-payload-sha) %s" % (sha, expect_payload_sha))
    if sha != expect_payload_sha:
        refuse("the payload sha256 %s is not the registered %s: nothing is posted" % (sha, expect_payload_sha))
    kind, conn = _launch_state(paths, rec, sha)
    st = IC.state(conn) if conn is not None else {"n_attempts": 0, "n_transport": 0, "n_invocations": 0, "orphans": []}
    planned = MAX_ATTEMPTS - st["n_attempts"]
    if atl is not None:
        # ruling 1 (b) of the READY review: the day ledgers' count for this test equals the invocations the cache records
        # (0 on a fresh launch); a lost, moved or never-written cache row cannot reset the limits
        led = atl.ledger_calls(TEST, ledger_dir)
        out("[INDUCE-RUN] ledger equality: day ledgers hold %d invocation(s) for %s; the cache records %d (%s launch)"
            % (led, TEST, st["n_invocations"], kind))
        if led != st["n_invocations"]:
            if conn is not None:
                conn.close()
            refuse("[ACCOUNT] REFUSED (0 calls posted): the day ledgers hold %d invocation(s) for %s but the cache records %d"
                   % (led, TEST, st["n_invocations"]))
        try:
            atl.guard(TEST, planned, {}, ledger_dir, "--run --go (%s)" % kind)   # ruling 1 (a): (i) REFUSES (ceiling 6)
        except SystemExit:
            if conn is not None:
                conn.close()
            raise
    if kind == "fresh":
        os.makedirs(paths.out, exist_ok=True)
        with open(paths.ids, "x", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(rec, indent=1, sort_keys=True) + "\n")
        meta = {"registration": TEST, "gen_view_sha256_bytes": gen_sha, "eval_view_sha256_bytes": eval_sha, "seed": seed,
                "seed_label": label, "n": N, "payload_sha256": sha, "system_sha256": SYSTEM_SHA,
                "user_template_sha256": USER_TEMPLATE_SHA, "judge_requested": P.JUDGE_REQUESTED, "max_tokens": P.CAP,
                "temperature_label": P.TEMPERATURE_LABEL, "max_attempts": MAX_ATTEMPTS, "max_transport": MAX_TRANSPORT,
                "script_blob": git_blob_lf(os.path.abspath(__file__)), "induction_blob": git_blob_lf(I.__file__),
                "input_variant_ids_sha256": rec["input_variant_ids_sha256"], "disclosure": DISCLOSURE}
        conn = IC.create(paths.cache, meta)
    _event(conn, "launch", kind)
    posted, tseq = {"n": 0}, None
    try:
        if kind == "relaunch":
            resolve_orphans(conn, out)
        st = IC.state(conn)
        if st["n_transport"] < MAX_TRANSPORT:
            rows, valid, tseq = attempts(conn, call_full, system, user, body, sha, chosen, out, posted)
        else:
            rows, valid = [], None
        st = IC.state(conn)
        if tseq is not None and tseq < MAX_TRANSPORT:
            lines = ["%s TRANSPORT STOP %d of %d (not an outcome): payload sha256 %s; TRANSPORT, no reply; attempts so far %d;"
                     " a relaunch re-posts the IDENTICAL body" % (TEST, tseq, MAX_TRANSPORT, sha, st["n_attempts"])]
            with open(os.path.join(paths.out, "transport_stop_%d.txt" % tseq), "x", encoding="utf-8", newline="\n") as f:
                f.write("\n".join(lines) + "\n")
            for ln in lines:
                out(ln)
            return {"rows": rows, "valid": None, "stopped": True, "transport_seq": tseq, "validity": {}, "outcome_lines": lines}
        all_rows = [dict(zip(("attempt_no", "failure_class", "finish_reason", "response_id", "reply_sha256", "reply_text",
                                "provider", "payload_sha256", "committed_at"), r)) for r in conn.execute(
            "SELECT attempt_no, failure_class, finish_reason, response_id, reply_sha256, reply_text, provider, payload_sha256,"
            " committed_at FROM attempt ORDER BY attempt_no")]
        transport = conn.execute("SELECT seq, at, exception_class, message FROM transport ORDER BY seq").fetchall()
        valid_row = next((r for r in all_rows if r["failure_class"] is None), None)
        if valid_row is not None:
            # the commit time of the cached reply: the event written right AFTER its insert was committed
            valid_row["committed_at"] = conn.execute("SELECT at FROM event WHERE what='reply_committed' ORDER BY seq DESC"
                                                     " LIMIT 1").fetchone()[0]
        res = finish(conn, all_rows, valid_row, transport, system, user, chosen, rec, paths, seed, registration, gen_sha,
                     eval_sha, witness, check, out, excl)
        if res["validity"].get("V2") is False:
            out("[INDUCE-RUN] V2 FAILED: the artefact is NOT OF RECORD; never a formal failure and NEVER a re-post (ruling on"
                " finding 3 (ii)); the slot question returns to the author")
        return res
    finally:
        if conn is not None:
            conn.close()
        if atl is not None and posted["n"]:
            atl.append(TEST, "--run --go", posted["n"], ledger_dir)


def finish(conn, rows, valid, transport, system, user, chosen, rec, paths, seed, registration, gen_sha, eval_sha, witness,
           check, out=print, excl=None):
    v = {"V1": None, "V2": None, "V3": None, "V4": None}
    art, hits, order = None, None, None
    if valid is not None:
        rp = Replay(system, user, valid, "REGISTERED %s (attempt %d of record)" % (TEST, valid["attempt_no"]))
        art = I.induce(CORPUS_TYPE, rp, paths.gen, gen_sha, n=N, seed=seed, registration=registration, out=out,
                       population=POPULATION, label=ARTEFACT_LABEL, exclude=excl[0],
                       exclude_ref={"list_sha256": excl[1]["list_sha256"], "n_excluded": len(excl[0]),
                                    "threshold": OA.THRESHOLD, "file": os.path.basename(paths.excl)})
        m = art["manifest"]
        if m["input_variant_ids_ordered_sha256"] != rec["input_variant_ids_ordered_sha256"] or \
                m["prompt_system_sha256"] != sha256_text(system) or m["prompt_user_sha256"] != sha256_text(user):
            refuse("the artefact's inputs or prompt differ from the posted ones")
        v["V1"] = bool(m["verbatim_audit"]["hits"] == 0 and not I.verbatim_audit(art["rubric"], chosen))
        # ruling on finding 3 (i): ORDER, WITNESSED: the cached reply's commit time, then the eval_view open time
        out("[INDUCE-RUN] V2 order witness: the reply of record (attempt %d) committed to the attempt cache at %s"
            % (valid["attempt_no"], valid["committed_at"]))
        ev = open_eval_for_audit(paths.eval, eval_sha, conn, out)
        try:
            hits = leak_check(art["rubric"], eval_material(ev, os.path.basename(paths.eval), out))
        finally:
            ev.close()
        order = (valid["committed_at"], _EVAL_OPENED["at"])
        if not order[0] < order[1]:
            refuse("V2 order: the eval_view open time %s is not after the reply's commit time %s" % (order[1], order[0]))
        v["V2"] = bool(not hits)
        v["V3"] = bool(check["eval_hits"] == 0 and check["not_gen_side"] == 0 and witness.get("train_candidates", 0) >= N)
        if v["V1"] and v["V2"] and v["V3"]:
            I.write_artefact(art, paths.artefact)
            v["V4"] = bool(os.path.exists(paths.artefact) and
                           I.load_artefact(paths.artefact, art["artefact_sha256"]).rubric_sha256 == art["rubric_sha256"])
        else:
            v["V4"] = False
    lines = outcome_lines(rows, valid, transport, v, art, hits, rec, witness, check, order, eval_sha)
    with open(paths.outcome, "x", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    for ln in lines:
        out(ln)
    return {"rows": rows, "valid": valid, "stopped": False, "transport": transport, "validity": v, "artefact": art,
            "hits": hits, "outcome_lines": lines, "order": order}


def outcome_lines(rows, valid, transport, v, art, hits, rec, witness, check, order, eval_sha):
    L_ = ["%s OUTCOME (zero-call validity; %d attempt(s) with a reply, %d transport error(s))" % (TEST, len(rows),
                                                                                              len(transport))]
    L_.append("  DISCLOSURE: %s" % DISCLOSURE)
    L_.append("  DISCLOSURE: %s" % DISCLOSURE_C4)
    L_.append("  DISCLOSURE: %s" % DISCLOSURE_C5)
    L_.append("  DISCLOSURE: %s" % (DISCLOSURE_D1 % witness.get("replaced", 0)))
    L_.append("  ARTEFACT LABEL: %s; population %s" % (ARTEFACT_LABEL, json.dumps(POPULATION, sort_keys=True)))
    for r in rows:
        L_.append("  attempt %d: finish_reason %r, response id %r, reply sha256 %s, class %s" % (
            r["attempt_no"], r["finish_reason"], r["response_id"], r["reply_sha256"], r["failure_class"] or "VALID"))
    for seq, at, cls, msg in transport:
        L_.append("  transport error %d at %s: %s: %s (%s; not an attempt)" % (
            seq, at, cls, msg[:120], "TRANSPORT, no reply recorded (orphan invocation)" if cls == "ORPHAN" else
            "TRANSPORT, no reply"))
    L_.append("  input_variant_ids: n %d, sorted-set sha256 %s, ordered sha256 %s" % (
        rec["n"], rec["input_variant_ids_sha256"], rec["input_variant_ids_ordered_sha256"]))
    by_instrument = bool(valid is None and len(transport) >= MAX_TRANSPORT)
    undetermined = bool(valid is None and not by_instrument and len(rows) >= MAX_ATTEMPTS)
    if valid is not None:
        L_.append("  the reply of record: attempt %d (the FIRST valid reply; no best-of-n, no edit)" % valid["attempt_no"])
    if by_instrument:
        L_.append("  UNDETERMINED BY INSTRUMENT: %d transport errors (not by the model); a further relaunch needs a registrar"
                  " bracket" % len(transport))
    if undetermined:
        L_.append("  UNDETERMINED: three formal failures; the decision goes to THE AUTHOR.")
    if order is not None:
        L_.append("  V2 order witness: reply committed %s < eval_view opened %s; eval_view sha256_bytes %s (the manifest of"
                  " record; stage 'judge' a mislabel accepted for this run only)" % (order[0], order[1], eval_sha))
    L_.append("  V1 verbatim audit (SHINGLE %d): %s" % (I.SHINGLE, _pf(v["V1"])))
    L_.append("  V2 leak check against EVAL key material: %s%s" % (_pf(v["V2"]), (" hits %s" % hits[:6]) if hits else ""))
    L_.append("  V3 content-key counts: candidate rows %s, distinct variants %s, duplicates collapsed %s, skipped by"
              " component %s, GATE refused %s, other non-TRAIN %s, EVAL hits %s, not TRAIN %s: %s" % (
                  witness.get("candidate_rows"), witness.get("distinct_variants"), witness.get("duplicates_collapsed"),
                  witness.get("skipped_by_component"), witness.get("gate_excluded"), witness.get("other_excluded"),
                  check.get("eval_hits"), check.get("not_gen_side"), _pf(v["V3"])))
    L_.append("  V4 artefact written with mode x: %s%s" % (_pf(v["V4"]), (" artefact_sha256 %s rubric_sha256 %s" % (
        art["artefact_sha256"], art["rubric_sha256"])) if (art is not None and v["V4"]) else ""))
    of_record = bool(valid is not None and v["V1"] and v["V2"] and v["V3"] and v["V4"])
    L_.append("  ARTEFACT OF RECORD: %s" % ("YES" if of_record else "NO (not of record)"))
    p1 = bool(len(rows) >= 1 and rows[0]["failure_class"] is None)
    if not rows:
        L_.append("  P1 (the first attempt is valid; point probability %.1f): NOT SCORED (no reply)" % P1_POINT)
    elif p1:
        L_.append("  P1 (the first attempt is valid; point probability %.1f): HELD" % P1_POINT)
    else:
        L_.append("  P1 (the first attempt is valid; point probability %.1f): FAILED" % P1_POINT)
    p2 = bool(valid is not None and v["V1"] and v["V2"] and v["V3"] and v["V4"])
    if valid is None:
        L_.append("  P2 (V1-V4 pass): NOT SCORED (no valid reply)")
    elif p2:
        L_.append("  P2 (V1-V4 pass): HELD")
    else:
        L_.append("  P2 (V1-V4 pass): FAILED")
    if undetermined:
        L_.append("  FALSIFIER (three formal failures): FIRED: the plan to fill the slot by one induction is overturned;"
                  " the slot question returns to the author")
    else:
        L_.append("  FALSIFIER (three formal failures): NOT FIRED%s" % (" (UNDETERMINED BY INSTRUMENT does not fire it)"
                                                                        if by_instrument else ""))
    L_.append("  LABEL: a RECIPE COMPONENT; no rubric-value or accuracy claim.")
    return L_


def _pf(x):
    return "PASS" if x is True else ("FAIL" if x is False else "NOT RUN")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--run", action="store_true")
    g.add_argument("--selftest", action="store_true")
    ap.add_argument("--go", action="store_true")
    ap.add_argument("--expect-payload-sha")
    ap.add_argument("--transcript")
    a = ap.parse_args(argv)
    if a.selftest:
        from . import induce_run_selftest as S
        return S.main(["--transcript", a.transcript] if a.transcript else [])
    if a.dry_run:
        r = dry_run()
        print("[INDUCE-RUN] DRY-RUN done: payload sha256 %s; 0 calls" % r["payload_sha256"])
        return 0
    if not a.go or not a.expect_payload_sha:
        refuse("--run needs --go and --expect-payload-sha <the registered payload sha>")
    import accepted_tests_ledger as atl
    rr.load_env()
    res = run(rr.call_judge_full, a.expect_payload_sha, ledger_dir=os.path.join(_data_root(), "experiment_results"),
              atl=atl)
    return 0 if res.get("valid") is not None else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
