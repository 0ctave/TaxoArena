"""judge_v2.loader: eval_view -> MatchInputs + LeakMaterial, the ONLY source of judged matches (READY_archv2_EJ C3 / C4).

OPENS ONLY THROUGH data_v2.views.open_eval("judge", path, expect_sha256): a sealed file whose own meta says view_kind =
eval (EVAL items only). No other opener, no sqlite3.connect (lint_opens.py refuses one).

load_matches(requests, eval_view_path, expect_sha256, corpus_type, board_vintage, ...) -> Loaded(specs, materials, manifest)
  requests: [{"match_id", "variant_id", "model_a", "model_b", optional "batch_id", optional "corpus_version"}], the
  schedule fixed BEFORE any verdict from free data (E-A). Every request is resolved from eval_view rows; ANY refused request
  REFUSES THE WHOLE LOAD (raise SystemExit listing the reasons with counts): a run is never launched on a partial schedule.
  Per request:
    variant   a row of eval_view.variant (a TRAIN / GATE variant is not in the file: refused "not an EVAL variant"); its
              item's split side is EVAL; its contract maps to the corpus type (payload.CONTRACT_TYPES; unknown refused);
    responses exactly one ACTIVE response of model_a and one of model_b whose seen_ck IS the variant (a routing-only
              sentinel has none: refused "not judgeable"; a quarantined model is refused);
    question  variant.stem (payload re-keys it to item.stem_key: failure 12);
    traces    rejudge_grok.robust_trace(output, pred, options), options = the response's OWN verbatim ordered options
              (data_v2.common.options_raw by the row's options_ordered_sha), exactly as v1 built them from options_json;
    ordering  question_options_sha = the ordering the two contestants' rows carry when they agree, else
              "MIXED:<a>|<b>" (then no reference can match it and a reference-bearing match is refused);
    reference choose_reference() below (the ruling); rendered as rejudge_reference.with_reference's block: the marker, then
              "(<answer>) <option text>", the option text indexed in the ordered options the SOLVER saw (the
              options_ordered of the solver's response row, data_v2.ingest.SOLVER_MODEL), never options_sorted.
  Reference columns READ: variant_id, vintage, source_key, item_id, legacy_qid, answer, state, finish_reason, side_at_mint
  (recorded as legacy text only). gt, correct and raw are NEVER selected (REF_COLS; choose_reference refuses a row that
  carries them).

choose_reference(rows, board_vintage="grok-reasoning-v0", ...) — THE RULING (coordinator 2026-09-24, registrar inserting):
  keep only rows of the judged variant_id whose vintage == board_vintage (other vintages IGNORED, never a fallback);
  0 rows -> None (reference_state NONE, counted and printed); 1 row -> that row; > 1 -> REFUSE (no tie-break).
  REFUSE also when: the answer is empty or outside the variant's option range (the solver's ordered options); state is
  NON_TERMINATED; finish_reason is length or content_filter; item_id or stem_key disagrees with the slot.
  grok-reasoning-v1 is NEVER selected: a board naming it is REFUSED unless a separate registration id is given
  (v1_registration). Any other vintage is refused.
  A match judged on a variant with no solver row for its board-vintage reference (the resolution 'unique_active_variant':
  the solver's ordering is unknown) gets NONE, counted; a match on a non-solver variant has no row and gets NONE.

MATERIAL (C3; the scan's material legs, leakage.LeakMaterial), built here from the SAME rows, rendered by MATERIAL_FORMS:
  key     the response rows' gt_raw and answer_text (the key) in machine-field renderings ("gt_raw: X", "answer_text: X",
          '"gt_raw": "X"', ...);
  side    per contestant, its is_correct / is_correct_mathfix in model-tagged machine renderings;
  other   the full reference block (marker + rendering) of every OTHER reference row of the same item (other vintages,
          other variants) that renders and is not a substring of the chosen block.
  Renderings shorter than leakage.MIN_MATERIAL are dropped and COUNTED (they cannot be scanned by substring). A match whose
  material is empty is flagged; writer.create refuses it unless the registration declares material NONE.

PROVENANCE: every MatchInputs carries a token (HMAC-SHA256 under a per-process secret over its canonical fields);
writer.JudgeWriter refuses a spec whose token is missing or does not verify, so only loader-built matches are judged.
The manifest records the eval_view file (basename, sha256-bytes, meta), the board vintage, and every count.

[CORRECTED 2026-09-24 on the delta review 16212c4 (D4, D5, D6), insertion only:
  - D6: choose_reference runs on EVERY path; the solver's ordering is resolved inside it (n_options may be a callable),
    and an UNKNOWN solver ordering (no solver response row, e.g. resolution 'unique_active_variant') is REFUSED, never
    NONE. The "NONE, counted" sentence above for that case is withdrawn; NONE is only "no row of the board's vintage".
  - D5: a referenced match whose shown ordering is MIXED (the contestants saw different orderings) or differs from the
    solver's is EXCLUDED PER MATCH (counted, listed in manifest.excluded), not a whole-load refusal; the class of a MIXED
    referenced match awaits the judge-design-specialist's ruling. Every other refusal still refuses the whole load.
  - D4: signing is private (_sign, called only by load_matches); the public name sign() REFUSES; the selftest uses
    _sign_for_selftest, which refuses any other caller; lint_opens counts references to the signing functions outside
    loader.py. The token is an INTEGRITY guard against accidents, not authentication.
  - D3: the manifest and the [LOADER] line count key, side and other-reference material separately.]
[CORRECTED 2026-09-24 by the D5 MIXED ruling (coordinator; the registrar inserting), insertion only:
  (1) ORDERING EQUALITY is ordering_key(): option lists equal entry by entry after str(x).strip(); question_options_sha
      and Reference.options_ordered_sha hold that key ("ok1:..."), not a byte sha, so byte-only differences are not MIXED.
  (2) A REFERENCE-BEARING match where either contestant's ordering differs from the solver's is REFUSED PER MATCH
      (manifest.excluded, counted per model and per variant, printed); an unknown solver ordering (no solver row) and a
      defective reference row are per-match refusals too; board-level vintage errors still refuse the whole load.
  (3) A NO-REFERENCE match may be MIXED: each trace is resolved in its own ordering (rejudge_grok.robust_trace, the record's
      builder); question_options_sha is "MIXED:a|b"; writer.create records it per match in run_meta and
      writer.mixed_strata() stratifies MIXED against same-ordering.
  (4) BBH is REFUSED from the judged path (by the response source, and by harness-shaped options as a backstop) until its
      responses are normalised.
  The judge never sees an options list: the question block is the stem only; "the ordering behind the question block"
  above means the ordering the contestants' traces are resolved in.]
[CORRECTED 2026-09-24 by the delta-2 review d429c4b (E1 HIGH, E2), insertion only; this SUPERSEDES the per-match sentence
of (2) above for everything but the two ordering classes:
  - per-match exclusion exists ONLY for the reason codes EXCLUSION_CODES (excluded_MIXED_referenced,
    excluded_ordering_differs_from_solver), set by the loader's own ordering check, never parsed from a message;
  - EVERY choose_reference refusal refuses the WHOLE load: >1 row, item / stem mismatch, empty or out-of-range answer,
    NON_TERMINATED, length / content_filter, and an UNKNOWN solver ordering (a missing or broken solver join);
  - load_matches takes the scheduler's expected_exclusions {match_id: code} (default none) and refuses the whole load when
    the realised exclusions (ids and classes) differ from it, or when 0 matches are loaded;
  - the BBH source test is case-insensitive (refused_source).]
"""
import hashlib
import hmac
import json
import os
import zlib
from dataclasses import asdict, dataclass, replace

from ._base import REFERENCE_MARKER, dv2c, dv2ingest, dv2ro, dv2views, refuse, rj
from . import leakage as L
from . import payload as P

LOADER_VERSION = "jv2-loader-1"
BOARD_VINTAGE_DEFAULT = "grok-reasoning-v0"
V1_VINTAGE = "grok-reasoning-v1"
REF_COLS = ("variant_id", "vintage", "source_key", "item_id", "legacy_qid", "answer", "state", "finish_reason",
            "side_at_mint", "resolution")
FORBIDDEN_REF_COLS = ("gt", "correct", "raw")
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_SECRET = os.urandom(32)

MATERIAL_FORMS = {
    "key": ("gt_raw: {v}", "gt_raw={v}", '"gt_raw": "{v}"', "answer_text: {v}", "answer_text={v}", '"answer_text": "{v}"'),
    "side": ("{m}.is_correct={v}", "{m} is_correct: {v}"),
    "side_mathfix": ("{m}.is_correct_mathfix={v}", "{m} is_correct_mathfix: {v}"),
}


@dataclass
class Loaded:
    specs: dict
    materials: dict
    manifest: dict


def _canon(inp):
    d = asdict(replace(inp, provenance=None))
    return json.dumps(d, sort_keys=True, ensure_ascii=True).encode("utf-8")


def _sign(inp):
    return replace(inp, provenance="jv2-loader:" + hmac.new(_SECRET, _canon(inp), hashlib.sha256).hexdigest())


def sign(inp):
    """D4 (delta review 16212c4): signing is PRIVATE to load_matches. The old public name REFUSES (probe H1)."""
    refuse("loader.sign is private to load_matches: a hand-built MatchInputs is never signed (integrity token, D4)")


def _sign_for_selftest(inp):
    """The selftest's one use (a validly signed spec with an edited trace, to exercise the schedule-reproduction
    refusal). Refused unless the caller is judge_v2.selftest; lint_opens counts every other reference."""
    import sys as _sys
    g = _sys._getframe(1).f_globals
    caller = g.get("__name__", "")
    here = os.path.normcase(os.path.join(os.path.dirname(os.path.abspath(__file__)), "selftest.py"))
    as_main = caller == "__main__" and os.path.normcase(os.path.abspath(g.get("__file__") or "")) == here
    if not (caller == "judge_v2.selftest" or caller.endswith(".judge_v2.selftest") or as_main):
        refuse("loader._sign_for_selftest is for judge_v2.selftest only (called from %r)" % caller)
    return _sign(inp)


def verify(inp):
    tok = getattr(inp, "provenance", None)
    if not isinstance(tok, str) or not tok.startswith("jv2-loader:"):
        return False
    want = "jv2-loader:" + hmac.new(_SECRET, _canon(inp), hashlib.sha256).hexdigest()
    return hmac.compare_digest(tok, want)


def ordering_key(options):
    """The D5 ruling's equality key: two orderings are the SAME when their option lists are equal entry by entry after
    str(x).strip() (byte-only differences are NOT MIXED). Returned as "ok1:" + sha256 over the stripped list's JSON."""
    t = [str(x).strip() for x in options]
    return "ok1:" + hashlib.sha256(json.dumps(t, ensure_ascii=True).encode("utf-8")).hexdigest()[:32]


REFUSED_SOURCES = {"BBH": "BBH options / preds are lm-eval argument dicts ({'arg_0': ...}); robust_trace would leak the"
                          " harness prompt into the trace. Refused until its responses are normalised (D5 ruling (4))"}


def _harness_shaped(options):
    return any(isinstance(o, str) and (o.startswith("{'arg_0'") or o.startswith('{"arg_0"')) for o in options)


def check_board(board_vintage, v1_registration=None):
    """The board-level half of the ruling, checked once per load (a whole-load refusal)."""
    if board_vintage == V1_VINTAGE:
        if not v1_registration:
            refuse("choose_reference: board vintage %s is never selected without a separate registration" % V1_VINTAGE)
    elif board_vintage != BOARD_VINTAGE_DEFAULT:
        refuse("choose_reference: board vintage %r is not %s (nor a registered %s)" % (board_vintage, BOARD_VINTAGE_DEFAULT,
                                                                                      V1_VINTAGE))


def _options_list(conn, sha):
    raw = dv2c.options_raw(conn, sha)
    if raw is None or raw == "":
        return []
    v = json.loads(raw)
    if not isinstance(v, list):
        refuse("options_ordered %s is not a list" % sha)
    return v


def choose_reference(rows, board_vintage=BOARD_VINTAGE_DEFAULT, variant_id=None, item_id=None, stem_key=None,
                     n_options=None, contract_is_letter=True, v1_registration=None):
    """The ONE reference of a judged slot (the ruling; module docstring). rows: dicts of REF_COLS for the judged item.
    n_options: the number of options in the SOLVER's ordering, or a callable(row) -> that number or None (the loader's
    solver-row lookup). None means the solver's ordering is UNKNOWN: REFUSED, never NONE (delta review 16212c4 D6:
    the ruling's NONE covers only "no row of the board's vintage"). Every other refusal runs BEFORE the solver lookup, so
    no path skips them. Returns (row or None, reason)."""
    check_board(board_vintage, v1_registration)
    for r in rows:
        bad = [c for c in FORBIDDEN_REF_COLS if c in r]
        if bad:
            refuse("choose_reference: a reference row carries %s; gt / correct / raw are never read" % bad)
    keep = [r for r in rows if r["variant_id"] == variant_id and r["vintage"] == board_vintage]
    if not keep:
        return None, "NONE: no %s row for the judged variant" % board_vintage
    if len(keep) > 1:
        refuse("choose_reference: %d %s rows for variant %s (%s): more than one is REFUSED, never tie-broken"
               % (len(keep), board_vintage, variant_id, [r["source_key"] for r in keep]))
    r = keep[0]
    ans = (r.get("answer") or "").strip()
    if not ans:
        refuse("choose_reference: the %s reference of %s has an empty answer" % (board_vintage, variant_id))
    if (r.get("state") or "") == "NON_TERMINATED":
        refuse("choose_reference: the reference of %s is NON_TERMINATED" % variant_id)
    if (r.get("finish_reason") or "") in ("length", "content_filter"):
        refuse("choose_reference: the reference of %s finished %r" % (variant_id, r.get("finish_reason")))
    if item_id is not None and r["item_id"] != item_id:
        refuse("choose_reference: reference item %s != the slot's item %s" % (r["item_id"], item_id))
    if stem_key is not None and r["item_id"] != dv2c.item_id_of_key(stem_key):
        refuse("choose_reference: reference item %s does not carry the slot's stem_key %s" % (r["item_id"], stem_key))
    if contract_is_letter:
        n = n_options(r) if callable(n_options) else n_options
        if n is None:
            refuse("choose_reference: the SOLVER's ordering of the %s reference of %s is unknown (no solver response row,"
                   " resolution %r): REFUSED, never guessed and never NONE" % (board_vintage, variant_id, r.get("resolution")))
        if not (len(ans) == 1 and ans in LETTERS and LETTERS.index(ans) < n):
            refuse("choose_reference: answer %r of %s is outside the option range (%s options)" % (ans, variant_id, n))
    return r, "ONE"


def render_reference(answer, solver_options):
    """rejudge_reference.with_reference's rendering after the marker: "(<answer>) <option text>"."""
    return "(%s) %s" % (answer, solver_options[LETTERS.index(answer)])


def _forms(kind, **kw):
    return [f.format(**kw) for f in MATERIAL_FORMS[kind]]


# E1 (delta-2 review d429c4b): the ONLY per-match exclusion classes (reason codes set by the loader's own ordering check,
# never parsed from a message); every other refusal refuses the WHOLE load
EXCLUSION_CODES = ("excluded_MIXED_referenced", "excluded_ordering_differs_from_solver")


def refused_source(src):
    """The BBH refusal by response source, case-insensitive (E2)."""
    return isinstance(src, str) and src.strip().upper() in REFUSED_SOURCES


def load_matches(requests, eval_view_path=None, expect_sha256=None, corpus_type="mcq", board_vintage=BOARD_VINTAGE_DEFAULT,
                 v1_registration=None, expected_exclusions=None, out=print):
    """expected_exclusions: the scheduler's {match_id: reason code} of the matches it knows are excluded (default: none).
    The realised exclusions (ids AND classes) must equal it, else the WHOLE load is refused (E1); a load with 0 matches is
    refused."""
    if corpus_type not in P.CORPUS_TYPES:
        refuse("load_matches: corpus_type %r" % (corpus_type,))
    expected_exclusions = dict(expected_exclusions or {})
    bad_codes = sorted({c for c in expected_exclusions.values() if c not in EXCLUSION_CODES})
    if bad_codes:
        refuse("load_matches: expected_exclusions names class(es) %s; the only per-match classes are %s" % (
            bad_codes, list(EXCLUSION_CODES)))
    check_board(board_vintage, v1_registration)
    conn = dv2views.open_eval("judge", eval_view_path, expect_sha256)
    path = eval_view_path or os.environ.get("TAXOARENA_V2_EVAL_VIEW")
    try:
        meta = dict(conn.execute("SELECT key, value FROM meta"))
        active = {(cv, m) for cv, m, st in conn.execute("SELECT corpus_version, model, status FROM model_registry")
                  if st == "ACTIVE"}
        side = {iid: s for iid, s in conn.execute("SELECT item_id, side FROM side")}
        specs, materials, reasons = {}, {}, {}
        counts = {"requests": len(requests), "loaded": 0, "reference_ONE": 0, "reference_NONE": 0,
                  "excluded_MIXED_referenced": 0, "excluded_ordering_differs_from_solver": 0,
                  "loaded_MIXED_no_reference": 0,
                  "material_strings": 0, "material_dropped_short": 0, "matches_without_material": 0}
        mat_counts = {"key": 0, "side": 0, "other": 0, "matches_without_key": 0}
        none_reasons = {}
        excluded = {}
        excl_by_model, excl_by_variant = {}, {}
        seen_ids = set()

        def bad(req, why):
            reasons.setdefault(why, []).append(req.get("match_id"))

        for req in requests:
            mid, vid = req.get("match_id"), req.get("variant_id")
            ma, mb = req.get("model_a"), req.get("model_b")
            if not mid or mid in seen_ids:
                bad(req, "missing or duplicate match_id")
                continue
            seen_ids.add(mid)
            vrows = conn.execute("SELECT corpus_version, item_id, contract_id, stem FROM variant WHERE variant_id=?",
                                 (vid,)).fetchall()
            if req.get("corpus_version"):
                vrows = [r for r in vrows if r[0] == req["corpus_version"]]
            if not vrows:
                bad(req, "not an EVAL variant (absent from eval_view)")
                continue
            if len(vrows) > 1:
                bad(req, "variant in several corpus versions: name corpus_version")
                continue
            cv, iid, contract, stem = vrows[0]
            if side.get(iid) != "EVAL":
                bad(req, "item side %r is not EVAL" % side.get(iid))
                continue
            if P.CONTRACT_TYPES.get(contract) != corpus_type:
                bad(req, "contract %r is not corpus type %s" % (contract, corpus_type))
                continue
            sk = conn.execute("SELECT stem_key FROM item WHERE corpus_version=? AND item_id=?", (cv, iid)).fetchone()
            if sk is None:
                bad(req, "no item row")
                continue
            stem_key = sk[0]
            comp = conn.execute("SELECT component_id FROM side WHERE item_id=?", (iid,)).fetchone()
            resp = {}
            for m in (ma, mb):
                if (cv, m) not in active:
                    resp[m] = None
                    continue
                rows = conn.execute("SELECT response_id, pred, options_ordered_sha, gt_raw, answer_text, is_correct,"
                                    " is_correct_mathfix, output_zlib, source FROM response WHERE corpus_version=? AND"
                                    " model=? AND seen_ck=?", (cv, m, vid)).fetchall()
                resp[m] = rows[0] if len(rows) == 1 else ("MULTI" if rows else None)
            if ma == mb or any(resp[m] is None for m in (ma, mb)):
                bad(req, "not judgeable (no ACTIVE response of both contestants on this variant; sentinel or quarantine)")
                continue
            if any(resp[m] == "MULTI" for m in (ma, mb)):
                bad(req, "a contestant has several responses on this variant")
                continue
            srcs = sorted({str(resp[m][8]) for m in (ma, mb) if refused_source(resp[m][8])})
            opts_of = {m: _options_list(conn, resp[m][2]) for m in (ma, mb)}
            if srcs or any(_harness_shaped(opts_of[m]) for m in (ma, mb)):
                bad(req, "source %s refused from the judged path: %s" % (srcs or ["harness-shaped options"],
                                                                         REFUSED_SOURCES["BBH"]))
                continue
            traces, okey = {}, {}
            for m in (ma, mb):
                _rid, pred, sha, _gt, _at, _ok, _okm, oz, _src = resp[m]
                # each trace is resolved in its OWN ordering (rejudge_grok.robust_trace, the record's builder); the judge
                # never sees an options list: the question block is the stem only
                traces[m] = rj.robust_trace(zlib.decompress(oz).decode("utf-8"), pred, opts_of[m])
                okey[m] = ordering_key(opts_of[m])
            q_opts = okey[ma] if okey[ma] == okey[mb] else "MIXED:%s|%s" % (okey[ma], okey[mb])
            # the reference (the ruling)
            refrows = [dict(zip(REF_COLS, r)) for r in conn.execute(
                "SELECT %s FROM reference WHERE corpus_version=? AND item_id=?" % ", ".join(REF_COLS), (cv, iid))]
            ref = None
            chosen_block = None
            solver = {}

            def solver_n(r, cv=cv, vid=vid, solver=solver):
                if r["legacy_qid"] is None:
                    return None
                srow = conn.execute("SELECT options_ordered_sha FROM response WHERE corpus_version=? AND model=? AND"
                                    " legacy_qid=? AND seen_ck=?", (cv, dv2ingest.SOLVER_MODEL, r["legacy_qid"],
                                                                    vid)).fetchone()
                if srow is None:
                    return None
                solver["opts"] = _options_list(conn, srow[0])
                solver["key"] = ordering_key(solver["opts"])
                return len(solver["opts"])

            def exclude(reason, models=()):
                if reason not in EXCLUSION_CODES:
                    refuse("load_matches: %r is not a per-match exclusion class" % (reason,))
                counts[reason] = counts.get(reason, 0) + 1
                excluded[mid] = reason
                for m in models:
                    excl_by_model[m] = excl_by_model.get(m, 0) + 1
                excl_by_variant[vid] = excl_by_variant.get(vid, 0) + 1

            # choose_reference runs on EVERY path (D6). EVERY refusal it raises (>1 row, item / stem mismatch, empty or
            # out-of-range answer, NON_TERMINATED, length / content_filter, an UNKNOWN solver ordering) refuses the WHOLE
            # load (E1, delta-2 review d429c4b): no row-level refusal is ever turned into a per-match exclusion
            row, why = choose_reference(refrows, board_vintage, vid, iid, stem_key, solver_n,
                                        contract_is_letter=(corpus_type == "mcq"), v1_registration=v1_registration)
            if row is not None:
                if corpus_type == "mcq":
                    rendered = render_reference(row["answer"].strip(), solver["opts"])
                    osha_ref = solver["key"]
                else:
                    rendered = row["answer"].strip()
                    osha_ref = q_opts
                ref = P.Reference(row_id="ref:%s|%s|%s" % (vid, row["vintage"], row["source_key"]), variant_id=vid,
                                  stem_key=stem_key, vintage=row["vintage"], kind="cached_solve", rendered=rendered,
                                  options_ordered_sha=osha_ref, item_id=iid, side_v2=side.get(row["item_id"]))
                chosen_block = REFERENCE_MARKER + "\n" + rendered
            # D5 ruling (2): a REFERENCE-BEARING match where either contestant's ordering differs from the solver's
            # (under ordering_key) is REFUSED PER MATCH, counted per model and per variant, never judged, never NONE
            if ref is not None and (okey[ma] != ref.options_ordered_sha or okey[mb] != ref.options_ordered_sha):
                exclude("excluded_MIXED_referenced" if q_opts.startswith("MIXED:") else
                        "excluded_ordering_differs_from_solver",
                        [m for m in (ma, mb) if okey[m] != ref.options_ordered_sha])
                continue
            if row is not None:
                counts["reference_ONE"] += 1
            else:
                counts["reference_NONE"] += 1
                none_reasons[why] = none_reasons.get(why, 0) + 1
                # D5 ruling (3): a no-reference match may be MIXED (each trace resolved in its own ordering)
                if q_opts.startswith("MIXED:"):
                    counts["loaded_MIXED_no_reference"] += 1
            inp = P.MatchInputs(match_id=mid, variant_id=vid, stem_key=stem_key, component_id=comp[0] if comp else None,
                                corpus_type=corpus_type, question=stem, contestant_a=ma, contestant_b=mb,
                                trace_a=traces[ma], trace_b=traces[mb], reference=ref, batch_id=req.get("batch_id"),
                                question_options_sha=q_opts, item_id=iid)
            # material
            strings = {"key": [], "side": {}, "other": []}
            dropped = 0
            for m in (ma, mb):
                _rid, _pred, _sha, gt, at, ok, okm, _oz, _src = resp[m]
                for v in (gt, at):
                    if v:
                        strings["key"].extend(_forms("key", v=v))
                strings["side"][m] = _forms("side", m=m, v=ok) + (_forms("side_mathfix", m=m, v=okm) if okm is not None else [])
            for r in refrows:
                if r is row or r.get("answer") in (None, ""):
                    continue
                if r["legacy_qid"] is None:
                    continue
                s2 = conn.execute("SELECT options_ordered_sha FROM response WHERE corpus_version=? AND model=? AND"
                                  " legacy_qid=? AND seen_ck=?", (cv, dv2ingest.SOLVER_MODEL, r["legacy_qid"],
                                                                  r["variant_id"])).fetchone()
                a = r["answer"].strip()
                if s2 is None or corpus_type != "mcq":
                    continue
                o2 = _options_list(conn, s2[0])
                if not (len(a) == 1 and a in LETTERS and LETTERS.index(a) < len(o2)):
                    continue
                blk = REFERENCE_MARKER + "\n" + render_reference(a, o2)
                if chosen_block is None or blk not in chosen_block:
                    strings["other"].append(blk)

            def keep(lst):
                nonlocal dropped
                k = []
                for x in dict.fromkeys(lst):
                    if len(" ".join(x.casefold().split())) >= L.MIN_MATERIAL:
                        k.append(x)
                    else:
                        dropped += 1
                return k
            mat = L.LeakMaterial(side={m: keep(v) for m, v in strings["side"].items()}, key=keep(strings["key"]),
                                 other_references=keep(strings["other"]))
            n = len(mat.key) + len(mat.other_references) + sum(len(v) for v in mat.side.values())
            counts["material_strings"] += n
            counts["material_dropped_short"] += dropped
            if n == 0:
                counts["matches_without_material"] += 1
            mat_counts["key"] += len(mat.key)
            mat_counts["side"] += sum(len(v) for v in mat.side.values())
            mat_counts["other"] += len(mat.other_references)
            if not mat.key:
                mat_counts["matches_without_key"] += 1
            specs[mid] = _sign(inp)
            materials[mid] = mat if n else None
            counts["loaded"] += 1
        if reasons:
            refuse("load_matches REFUSED %d of %d requests (the whole load is refused): %s" % (
                sum(len(v) for v in reasons.values()), len(requests),
                "; ".join("%s: %d (e.g. %s)" % (k, len(v), v[:3]) for k, v in sorted(reasons.items()))))
        if excluded != expected_exclusions:
            diff = sorted(set(excluded.items()) ^ set(expected_exclusions.items()))
            refuse("load_matches REFUSED (the whole load): the realised per-match exclusions %s differ from the scheduler's"
                   " expected_exclusions %s (symmetric difference %s)" % (json.dumps(excluded, sort_keys=True),
                                                                          json.dumps(expected_exclusions, sort_keys=True),
                                                                          diff[:6]))
        if counts["loaded"] == 0:
            refuse("load_matches REFUSED: 0 matches loaded out of %d requests (an empty run is never created)" % len(requests))
        manifest = {"loader_version": LOADER_VERSION, "eval_view": os.path.basename(path),
                    "eval_view_sha256_bytes": dv2ro.file_sha256(path),
                    "eval_view_meta": {k: meta.get(k) for k in ("view_kind", "of_record", "seed", "split_sha256_bytes",
                                                               "views_blob", "content_check")},
                    "corpus_type": corpus_type, "board_vintage": board_vintage, "v1_registration": v1_registration,
                    "counts": counts, "reference_none_reasons": none_reasons, "excluded": excluded,
                    "excluded_by_model": excl_by_model, "excluded_by_variant": excl_by_variant,
                    "material_counts": mat_counts, "ordering_key": "ok1: sha256 of the str(x).strip() option list"}
        out("[LOADER] %s: %d requests -> %d matches; reference ONE %d / NONE %d %s; EXCLUDED per match: %s by model %s by"
            " variant %s; MIXED no-reference loaded %d" % (
                os.path.basename(path), len(requests), counts["loaded"], counts["reference_ONE"], counts["reference_NONE"],
                json.dumps(none_reasons), json.dumps({k: v for k, v in sorted(counts.items()) if k.startswith("excluded_")}),
                json.dumps(excl_by_model, sort_keys=True), json.dumps(excl_by_variant, sort_keys=True),
                counts["loaded_MIXED_no_reference"]))
        out("[LOADER] material: excluded ids %s; material strings %d (key %d, side %d, other-reference %d; dropped"
            " short %d), matches without material %d, without key material %d" % (
                json.dumps(sorted(excluded)), counts["material_strings"], mat_counts["key"], mat_counts["side"],
                mat_counts["other"], counts["material_dropped_short"], counts["matches_without_material"],
                mat_counts["matches_without_key"]))
        return Loaded(specs, materials, manifest)
    finally:
        conn.close()
