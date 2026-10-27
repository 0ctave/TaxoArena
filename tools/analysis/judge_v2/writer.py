"""judge_v2.writer: the v2 judge writer (ARCH-v2 E-J). Posts ONLY through an injected call function; zero calls here.

STORE. The E-D verdict store, unchanged (data_v2.verdicts.VerdictStore, pinned by blob in _base): ONE append-only DB per
registered run, the slot key (run_id, match_id, presentation_order, draw_index) (R7), the six-way positional enum (R6),
payload_sha256 a checked column, the posted body stored zlib-compressed, UPDATE / DELETE aborted by triggers, the schedule
fixed before the first call.

LIFECYCLE
  JudgeWriter.create(path, registration, run_id, specs, rubric, ctx, n_draws=1)
      writes run_meta (the E-D required keys + the recipe manifest + every pin) and the WHOLE schedule: for each match,
      draw_index 0..n_draws-1, orders 1 and 2 (order 1 shows A first). response_*_sha = sha256 of the trace text shown.
  JudgeWriter.open(path, specs, rubric, ctx)
      a RELAUNCH: data_v2.ro.open_run_writer (an unsealed v2 verdict DB only); the recipe identity in run_meta must equal
      the current one (judge, cap, temperature label, template / rubric / schema shas, payload / combiner / script blobs,
      parse version): a mismatch REFUSES, so a relaunch never mixes recipes in one run.
  writer.prescan()
      builds and scans EVERY pending slot's payload BEFORE the first post (the full-payload leakage scan on 100% of the
      bodies about to be posted); any hit refuses the whole launch; prints the [LEAK-SCAN] line pass or fail.
  writer.run(call_full)
      checks the rejudge_grok.combine_orders pin and the rejudge_reasoning configuration, prescans, then
      VerdictStore.drain(poster): exactly the PENDING slots (pending() = schedule minus verdict) are posted. An errored
      post is an attempt row, never a verdict (re-posted on the next launch); a CONTENT_FILTER is a verdict row, never
      re-posted (rule 10); a complete run posts NOTHING.

call_full(system, user) has rejudge_reasoning.call_judge_full's signature and return tuple (content, provider,
completion_tokens, latency_s, finish_reason, msg); in a run it IS rr.call_judge_full (CONTEXT rule 9), which posts
rr.payload_bytes(system, user): the poster asserts those bytes equal the stored body before every call. The selftest
injects a fake with the same shape. Nothing in this package supplies a live default.

CLASSIFICATION (the six-way enum; NON_TERMINATED and CONTENT_FILTER never become TIE, nor INVALID):
  finish_reason == "content_filter"  (call_judge_full's HTTP 400 refusal, or a 200 with that finish) -> CONTENT_FILTER
  finish_reason == "length"                                                                        -> NON_TERMINATED
  otherwise rejudge_grok.parse_judge(rr.strip_think(content)): "Model A" -> FIRST, "Model B" -> SECOND, TIE -> TIE,
  anything else (unparsed, empty, an unknown finish_reason) -> INVALID. The stored vote is POSITIONAL; the contestant
  frame and the match verdict are derived (combiner.combine; data_v2's match_verdict view).

PER-ROW PROVENANCE (data_v2.verdicts.VERDICT_FIELDS): payload_sha256 + body, prompt_template_blob (payload.py),
combiner_blob, script_blob, parse_version, judge_requested, provider, response_model (from call_judge_full's provider
string), response_id (msg["_response_id"]), finish_reason, completion_tokens, max_tokens 8192, temperature_sent NULL +
temperature_label "omitted", http_status (400 on a refusal), n_attempts, latency_ms, system / user template, rubric and
schema shas, reference row id + vintage, stem_key, session / batch id, pool / snapshot id.
NOT AVAILABLE through call_judge_full as pinned (blob:1339592a): system_fingerprint and prompt_tokens (it keeps only
usage.completion_tokens and drops the response's system_fingerprint); stored NULL. Surfacing them needs an additive,
reviewed change to rejudge_reasoning (open item), not a local copy of the call.

[CORRECTED 2026-09-24 on READY_archv2_EJ (2aba3ab) C2 / C3 / C4 / C8, insertion only:
  - create / open take a loader.Loaded (loader.load_matches over eval_view through open_eval("judge")), not raw specs:
    a spec whose provenance token does not verify is REFUSED, so only eval_view-built matches are judged (probe B);
  - every slot must carry leak material unless the registration declares material NONE (material_none_registration,
    recorded in run_meta.material_policy); the [LEAK-SCAN] line prints scans with and without material;
  - COVERAGE BY COUNT: prescan refuses unless the payloads scanned equal the pending slots; the poster refuses a post
    whose payload was not scanned; run refuses unless poster scans == posts and (without a NONE declaration) every scan
    carried material. Both counts are printed on every run, pass or fail;
  - the relaunch identity adds loader_blob, eval_view_sha256, board_vintage and material_policy;
  - match_verdicts returns run_id and takes its denominator from data_v2's match_status (PENDING included).]
[CORRECTED 2026-09-24 on the delta review 16212c4 D3 / D4, insertion only: an mcq slot must carry KEY material (not only
side material) unless material NONE is declared, checked at create and before each call; a material-NONE declaration
must name an entry of MATERIAL_NONE_REGISTRATIONS (empty: none registered) or a "DEV-" id (recorded as DEV, NOT OF
RECORD); any other value is REFUSED (probe H1's "anything").]
[CORRECTED 2026-09-24 on the delta-2 review d429c4b E1 / E2, insertion only: create / open refuse a Loaded with 0 matches
(an empty run is never created); mixed_strata checks schema_id before reading run_meta.]
[ADDED 2026-09-25 by JV2-PARALLEL-POSTING (registered bf9d80b, docs/judge_v2_program.md L19096-L19239; E-1 / E-3 / E-7),
insertion only: writer.run(call_full, out=print, workers=1).
  - workers == 1: TODAY'S PATH, VERBATIM (the plain callable; self.store.drain(self._poster_factory(call_full))), with ONE
    new printed line, pool.POOL_LINE_SEQUENTIAL "[POOL] workers 1 (sequential path)", before the pre-scan.
  - 2 <= workers <= pool.MAX_INFLIGHT: call_full must be a pool.TwoPhase transport (reserve / send / resolve) whose
    journal admits the N; the pre-scan runs unchanged; the pending list is read ONCE (store.pending()) and handed to
    pool.PostingPool, whose poster goes to store.drain UNCHANGED: every payload is built by _payload_for on the MAIN
    thread (the scan witness, the schedule check and the material checks unchanged), the verdict tuple is built by
    _pool_result (the same fields as _poster_factory's poster, key for key: an AST check in the pool selftest), and rows
    are inserted in key order. The C2 / C3 witnesses (poster scans == posts, material) are unchanged. After the drain the
    rr globals are compared with the pool's snapshot (E-7).
  - workers is NOT a recipe-identity key (a relaunch may change N). writer_blob IS one (unchanged list): this change moves
    its VALUE, so every store created before it REFUSES a relaunch under this writer (R1; by design).
  - pins_json of a NEW store adds judge_v2/pool.py (pin_table() of _base is unchanged; _pins() below).
  - [the coordinator's rate-control requirements, 2026-09-25, relayed during the build] run(..., rate=pool.RateConfig):
    a rate configuration makes the run POOLED at any workers, workers 1 included (the rate control of judge_v2.pool --
    Retry-After in both forms, full-jitter backoff pausing the whole pool, one global token bucket (max_rpm), the
    per-request timeout, the circuit breaker, adaptive concurrency, rr's retry loop neutralised -- then protects a single
    poster); without it, workers 1 is today's path verbatim.]
"""
import ast
import hashlib
import inspect
import json
import os
import textwrap
import time
from datetime import datetime, timezone

from ._base import dv2ro, dv2verdicts, git_blob_lf, pin_table, refuse, rj, rr, HERE
from . import combiner as K
from . import leakage as L
from . import loader as LD
from . import payload as P
from . import pool as POOL

CLASSIFY_VERSION = "jv2-classify-1"
MUTANT = None       # SELFTEST-ONLY (judge_v2/pool_selftest.py): "classify_429_invalid", "stale_pending"
_LAST_PENDING = {}  # SELFTEST-ONLY witness store for MUTANT "stale_pending" (never read otherwise)


def _pins():
    """pins_json of a new store: _base.pin_table() plus judge_v2/pool.py (JV2-PARALLEL-POSTING 2.6)."""
    t = pin_table()
    t["judge_v2/pool.py"] = "blob:" + git_blob_lf(os.path.join(HERE, "pool.py"))
    return t


def _ast_sha16(fn):
    src = textwrap.dedent(inspect.getsource(fn))
    return hashlib.sha256(ast.dump(ast.parse(src).body[0]).encode("utf-8")).hexdigest()[:16]


PARSE_VERSION = "%s+rj.parse_judge:ast16:%s+rr.strip_think:ast16:%s" % (CLASSIFY_VERSION, _ast_sha16(rj.parse_judge),
                                                                       _ast_sha16(rr.strip_think))
_POS = {"Model A": "FIRST", "Model B": "SECOND", "TIE": "TIE"}


def classify(content, finish_reason, msg=None):
    """-> (positional vote, raw_text). raw_text is never NULL except on a refusal with no body."""
    if finish_reason == "content_filter":
        raw = content if content else ((msg or {}).get("_refusal") or None)
        return "CONTENT_FILTER", raw
    if finish_reason == "length":
        return "NON_TERMINATED", content if content is not None else ""
    if content is None or finish_reason not in ("stop", None):
        return "INVALID", content if content is not None else ""
    winner, _conf = rj.parse_judge(rr.strip_think(content))
    return _POS.get(winner, "INVALID"), content


def _sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


IDENTITY_KEYS = ("judge_requested", "provider", "max_tokens", "temperature_label", "script_blob", "combiner_blob",
                 "prompt_template_blob", "parse_version", "system_template_sha", "user_template_sha", "schema_sha",
                 "rubric_sha", "rubric_corpus_type", "payload_version", "leakage_blob", "writer_blob", "system_persona_sha",
                 "loader_blob", "eval_view_sha256", "board_vintage", "material_policy")


# D4 (delta review 16212c4): a material-NONE declaration must name a REGISTERED entry (none is registered yet); a "DEV-"
# declaration is admitted for DEV runs and says so in run_meta. Any other value is REFUSED.
MATERIAL_NONE_REGISTRATIONS = {}


def material_policy(material_none_registration):
    if material_none_registration is None:
        return "required per slot (key material required for mcq)"
    if not isinstance(material_none_registration, str) or not material_none_registration:
        refuse("material_none_registration %r is not a registration id" % (material_none_registration,))
    if material_none_registration in MATERIAL_NONE_REGISTRATIONS:
        return "NONE declared by %s (%s)" % (material_none_registration,
                                             MATERIAL_NONE_REGISTRATIONS[material_none_registration])
    if material_none_registration.startswith("DEV-"):
        return "NONE declared by %s (DEV, NOT OF RECORD)" % material_none_registration
    refuse("material_none_registration %r is not registered (%s) and not a DEV- declaration" % (
        material_none_registration, sorted(MATERIAL_NONE_REGISTRATIONS)))


def _needs_key(inp):
    return inp.corpus_type == "mcq"


class JudgeWriter:
    def __init__(self, store, loaded, rubric, ctx, material_none_registration=None):
        self.store = store
        self.specs = dict(loaded.specs)
        self.materials = dict(loaded.materials)
        self.manifest = dict(loaded.manifest)
        self.rubric = rubric
        self.ctx = dict(ctx)
        self.material_none_registration = material_none_registration
        self.stats = L.ScanStats()
        self.posts = 0
        self.poster_scans = 0
        self.session_id = self.ctx.get("session_id") or "s:%s:%d" % (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"), os.getpid())

    # ── identity ──────────────────────────────────────────────────────────────────────
    @staticmethod
    def identity(rubric, ctx, manifest, material_none_registration=None):
        rm = P.recipe_manifest(rubric)
        return {"judge_requested": rm["judge_requested"], "provider": rm["provider"], "max_tokens": str(rm["max_tokens"]),
                "temperature_label": rm["temperature_label"], "script_blob": ctx["script_blob"],
                "combiner_blob": git_blob_lf(os.path.join(HERE, "combiner.py")),
                "prompt_template_blob": git_blob_lf(os.path.join(HERE, "payload.py")), "parse_version": PARSE_VERSION,
                "system_template_sha": rm["system_template_sha"], "user_template_sha": rm["user_template_sha"],
                "schema_sha": rm["schema_sha"], "rubric_sha": rm["rubric_sha"], "system_persona_sha": rm["system_persona_sha"],
                "rubric_corpus_type": rm["rubric_corpus_type"], "payload_version": rm["payload_version"],
                "leakage_blob": git_blob_lf(os.path.join(HERE, "leakage.py")),
                "writer_blob": git_blob_lf(os.path.join(HERE, "writer.py")),
                "loader_blob": git_blob_lf(os.path.join(HERE, "loader.py")),
                "eval_view_sha256": manifest.get("eval_view_sha256_bytes", ""),
                "board_vintage": manifest.get("board_vintage", ""),
                "material_policy": material_policy(material_none_registration)}

    @staticmethod
    def _check_loaded(loaded, rubric, material_none_registration):
        """C3 / C4: every spec came from loader.load_matches (a valid provenance token) and carries material unless the
        registration declares material NONE."""
        if not isinstance(loaded, LD.Loaded):
            refuse("the writer takes a loader.Loaded (loader.load_matches over eval_view), got %r" % type(loaded).__name__)
        if not loaded.specs:
            refuse("the Loaded carries 0 matches: an empty run is never created (E1, delta-2 review d429c4b)")
        no_tok = [mid for mid, inp in loaded.specs.items() if not LD.verify(inp)]
        if no_tok:
            refuse("%d spec(s) did not come from loader.load_matches (no valid provenance token), e.g. %s" % (
                len(no_tok), sorted(no_tok)[:3]))
        for mid, inp in loaded.specs.items():
            if mid != inp.match_id:
                refuse("spec key %r != its match_id %r" % (mid, inp.match_id))
            P.check_inputs(inp, rubric)
        material_policy(material_none_registration)
        no_mat = sorted(mid for mid in loaded.specs if not L._has_material(loaded.materials.get(mid)))
        if no_mat and not material_none_registration:
            refuse("%d slot(s) carry no leak material and no registration declares material NONE, e.g. %s" % (
                len(no_mat), no_mat[:3]))
        no_key = sorted(mid for mid, inp in loaded.specs.items() if _needs_key(inp) and mid not in no_mat and
                        not (loaded.materials.get(mid) and loaded.materials[mid].key))
        if no_key and not material_none_registration:
            refuse("%d mcq slot(s) carry no KEY material (D3: side material alone is not key coverage), e.g. %s" % (
                len(no_key), no_key[:3]))
        for k in ("eval_view_sha256_bytes", "board_vintage"):
            if not loaded.manifest.get(k):
                refuse("the loader manifest lacks %s" % k)

    @classmethod
    def create(cls, path, registration, run_id, loaded, rubric, ctx, n_draws=1, material_none_registration=None):
        for k in ("script_blob", "pool_id"):
            if not ctx.get(k):
                refuse("create: ctx lacks %s" % k)
        if not isinstance(n_draws, int) or n_draws < 1:
            refuse("create: n_draws %r" % (n_draws,))
        cls._check_loaded(loaded, rubric, material_none_registration)
        specs = loaded.specs
        meta = cls.identity(rubric, ctx, loaded.manifest, material_none_registration)
        meta.update({"run_id": run_id, "registration": registration, "pool_id": ctx["pool_id"],
                     "snapshot_id": ctx.get("snapshot_id") or "", "n_draws": str(n_draws), "n_matches": str(len(specs)),
                     "pins_json": json.dumps(_pins(), sort_keys=True),
                     "loader_manifest_json": json.dumps(loaded.manifest, sort_keys=True),
                     # D5 ruling (3): the ordering key per match ("MIXED:a|b" for a MIXED no-reference match); the E-D
                     # verdict table has no column for it, so it is recorded per match here, joinable by match_id
                     "question_options_json": json.dumps({m: x.question_options_sha for m, x in specs.items()},
                                                         sort_keys=True),
                     "reference_marker_sha": P.recipe_manifest(rubric)["reference_marker_sha"],
                     "rubric_artefact": rubric.artefact_id or "", "body_codec": P.BODY_CODEC})
        store = dv2verdicts.VerdictStore.create(path, meta)
        rows = []
        for mid in sorted(specs):
            inp = specs[mid]
            for draw in range(n_draws):
                for order in (1, 2):
                    first, second = (inp.contestant_a, inp.contestant_b) if order == 1 else (inp.contestant_b, inp.contestant_a)
                    tf, ts = (inp.trace_a, inp.trace_b) if order == 1 else (inp.trace_b, inp.trace_a)
                    rows.append({"match_id": mid, "presentation_order": order, "draw_index": draw,
                                 "variant_id": inp.variant_id, "stem_key": inp.stem_key, "component_id": inp.component_id,
                                 "contestant_a": inp.contestant_a, "contestant_b": inp.contestant_b,
                                 "shown_first": first, "shown_second": second, "response_first_sha": _sha(tf),
                                 "response_second_sha": _sha(ts),
                                 "reference_row_id": inp.reference.row_id if inp.reference else None,
                                 "reference_vintage": inp.reference.vintage if inp.reference else None,
                                 "batch_id": inp.batch_id})
        store.add_schedule(rows)
        return cls(store, loaded, rubric, ctx, material_none_registration)

    @classmethod
    def open(cls, path, loaded, rubric, ctx, material_none_registration=None):
        cls._check_loaded(loaded, rubric, material_none_registration)
        store = dv2verdicts.VerdictStore.open(path)
        meta = store.meta()
        want = cls.identity(rubric, ctx, loaded.manifest, material_none_registration)
        bad = ["%s: run %r, now %r" % (k, meta.get(k), want[k]) for k in IDENTITY_KEYS if meta.get(k) != want[k]]
        if bad:
            store.conn.close()
            refuse("relaunch of %s REFUSED: the recipe identity differs from the run's first launch: %s" % (path, "; ".join(bad)))
        return cls(store, loaded, rubric, ctx, material_none_registration)

    # ── the pre-call scan and the poster ──────────────────────────────────────────────
    def _payload_for(self, slot):
        mid = slot["match_id"]
        inp = self.specs.get(mid)
        if inp is None:
            refuse("slot %s has no match spec in this launch" % mid)
        pl = P.build_payload(inp, self.rubric, slot["presentation_order"])
        # the schedule was fixed at the first launch: the inputs of a relaunch must reproduce it
        want = (slot["shown_first"], slot["shown_second"], slot["response_first_sha"], slot["response_second_sha"],
                slot["variant_id"], slot["stem_key"],
                slot["reference_row_id"], slot["reference_vintage"])
        got = (pl.shown_first, pl.shown_second, _sha(pl.trace_first), _sha(pl.trace_second), inp.variant_id, inp.stem_key,
               inp.reference.row_id if inp.reference else None, inp.reference.vintage if inp.reference else None)
        if want != got:
            refuse("slot %s order %d: the launch inputs do not reproduce the fixed schedule (%s)" % (
                mid, slot["presentation_order"], [i for i, (a, b) in enumerate(zip(want, got)) if a != b]))
        if not L._has_material(self.materials.get(mid)) and not self.material_none_registration:
            refuse("slot %s order %d: no leak material and no registration declares material NONE (checked before any"
                   " call)" % (mid, slot["presentation_order"]))
        if _needs_key(inp) and not self.material_none_registration and not self.materials[mid].key:
            refuse("slot %s order %d: an mcq slot without KEY material (checked before any call)" % (
                mid, slot["presentation_order"]))
        L.scan(pl, inp, self.rubric, self.materials.get(mid), self.stats)
        return inp, pl

    def prescan(self, out=print):
        """Scan EVERY pending slot's payload before the first post. C2: refuses unless the scans counted equal the pending
        slots (a skipped order or slot is a refusal, not a silent gap); prints the count line pass or fail."""
        pend = self.store.pending()
        s0 = self.stats.scanned
        try:
            for row in pend:
                self._payload_for(dict(zip(dv2verdicts.SCHEDULE_COLS, row)))
        finally:
            out(self.stats.line() + " (pre-call: %d pending slots, %d scanned)" % (len(pend), self.stats.scanned - s0))
        if self.stats.scanned - s0 != len(pend):
            refuse("pre-scan coverage: %d payloads scanned for %d pending slots (every pending payload must be scanned)"
                   % (self.stats.scanned - s0, len(pend)))
        return len(pend)

    def _poster_factory(self, call_full):
        ident = self.identity(self.rubric, self.ctx, self.manifest, self.material_none_registration)

        def poster(slot):
            n0 = self.stats.scanned
            inp, pl = self._payload_for(slot)
            if self.stats.scanned != n0 + 1:
                refuse("slot %s order %d: the posted payload was not scanned (scan count %d -> %d)" % (
                    slot["match_id"], slot["presentation_order"], n0, self.stats.scanned))
            self.poster_scans += 1
            if rr.payload_bytes(pl.system, pl.user) != pl.body:
                refuse("slot %s: rejudge_reasoning.payload_bytes would post other bytes than the stored body" % slot["match_id"])
            self.posts += 1
            t0 = time.time()
            try:
                content, provider, ctoks, latency, finish, msg = call_full(pl.system, pl.user)
            except Exception as e:  # noqa: BLE001  (SystemExit is not an Exception: guards propagate)
                code = getattr(e, "code", None)
                return ("error", pl.sha256, code if isinstance(code, int) else None,
                        "%s%s" % (type(e).__name__, (":%s" % code) if code is not None else ""))
            msg = msg or {}
            vote, raw = classify(content, finish, msg)
            refusal = isinstance(provider, str) and provider.endswith(":refusal")
            resp_model = None
            if isinstance(provider, str) and ":" in provider and not refusal:
                resp_model = provider.split(":", 1)[1] or None
            ref = inp.reference
            fields = {
                "vote": vote, "raw_text": raw, "parse_version": PARSE_VERSION,
                "judge_requested": P.JUDGE_REQUESTED, "provider": P.PROVIDER, "response_model": resp_model,
                "system_fingerprint": msg.get("_system_fingerprint"), "response_id": msg.get("_response_id"),
                "finish_reason": finish, "prompt_tokens": msg.get("_prompt_tokens"), "completion_tokens": ctoks,
                "max_tokens": P.CAP, "temperature_sent": None, "temperature_label": P.TEMPERATURE_LABEL,
                "http_status": 400 if refusal else 200,
                "latency_ms": int(round(1000 * (latency if isinstance(latency, (int, float)) else time.time() - t0))),
                "system_template_sha": ident["system_template_sha"], "rubric_sha": ident["rubric_sha"],
                "user_template_sha": ident["user_template_sha"], "schema_sha": ident["schema_sha"],
                "prompt_template_blob": ident["prompt_template_blob"], "script_blob": ident["script_blob"],
                "combiner_blob": ident["combiner_blob"],
                "reference_row_id": ref.row_id if ref else None, "reference_vintage": ref.vintage if ref else None,
                "stem_key": inp.stem_key, "session_id": self.session_id, "batch_id": inp.batch_id,
                "pool_id": self.ctx["pool_id"], "snapshot_id": self.ctx.get("snapshot_id")}
            return ("verdict", pl.body, pl.sha256, fields)
        return poster

    def run(self, call_full, out=print, workers=1, rate=None):
        """Pre-scan, then post the pending slots. C2 / C3 witnesses, printed on every run and REFUSED on a mismatch: the
        pre-scan scanned every pending slot; the poster scanned every post (poster scans == posts); every scan carried
        material unless the registration declared material NONE.
        [JV2-PARALLEL-POSTING] workers == 1 and rate None: this path, verbatim, plus the one [POOL] line; workers > 1, or a
        pool.RateConfig given (the rate control at any workers, a single poster included): _pipelined_poster."""
        if not isinstance(workers, int) or isinstance(workers, bool) or not 1 <= workers <= POOL.MAX_INFLIGHT:
            refuse("run: workers %r (1 <= workers <= %d)" % (workers, POOL.MAX_INFLIGHT))
        if workers > 1 or rate is not None:
            return self._pipelined_poster(call_full, out, workers, rate)
        if not callable(call_full):
            refuse("run: call_full must be a callable with rejudge_reasoning.call_judge_full's signature")
        K.check_rj_pin()
        P.verify_rr_config()
        out(POOL.POOL_LINE_SEQUENTIAL)
        n = self.prescan(out)
        before, scans_before = self.posts, self.poster_scans
        try:
            self.store.drain(self._poster_factory(call_full))
        finally:
            posted, pscans = self.posts - before, self.poster_scans - scans_before
            out("[JUDGE-V2] run %s: pending %d at launch, posted %d, poster scans %d, pending now %d; %s" % (
                self.store.run_id, n, posted, pscans, len(self.store.pending()) if self.store.conn else -1,
                self.stats.line()))
        if pscans != posted:
            refuse("poster coverage: %d posts but %d poster scans" % (posted, pscans))
        if self.stats.without_material and not self.material_none_registration:
            refuse("material coverage: %d scan(s) ran without leak material and no registration declares material NONE"
                   % self.stats.without_material)
        return posted

    # ── [JV2-PARALLEL-POSTING] the pipelined path (workers > 1) ──────────────────────────────────────────────────
    def _pool_prepare(self, slot):
        """MAIN thread, before the slot's reservation: the poster's own scan witness, count and body check."""
        n0 = self.stats.scanned
        inp, pl = self._payload_for(slot)
        if self.stats.scanned != n0 + 1:
            refuse("slot %s order %d: the posted payload was not scanned (scan count %d -> %d)" % (
                slot["match_id"], slot["presentation_order"], n0, self.stats.scanned))
        self.poster_scans += 1
        if rr.payload_bytes(pl.system, pl.user) != pl.body:
            refuse("slot %s: rejudge_reasoning.payload_bytes would post other bytes than the stored body" % slot["match_id"])
        self.posts += 1
        return (inp, pl), pl.system, pl.user, pl.body

    def _pool_result(self, ident, ctx, ticket, outcome):
        """MAIN thread: the drain tuple of one resolved ticket; the verdict fields are _poster_factory's, key for key."""
        inp, pl = ctx
        if outcome.kind == "not_sent":
            return ("error", pl.sha256, None, "NotSent:%s" % POOL.NOT_SENT)
        if outcome.kind != "returned":
            e = outcome.value
            code = getattr(e, "code", None)
            if MUTANT == "classify_429_invalid" and code == 429:
                return ("verdict", pl.body, pl.sha256, self._pool_fields(ident, inp, "", "azure:", 0, 0.0, "stop", {}))
            return ("error", pl.sha256, code if isinstance(code, int) else None,
                    "%s%s" % (type(e).__name__, (":%s" % code) if code is not None else ""))
        content, provider, ctoks, latency, finish, msg = outcome.value
        if not isinstance(latency, (int, float)):
            latency = outcome.elapsed
        return ("verdict", pl.body, pl.sha256, self._pool_fields(ident, inp, content, provider, ctoks, latency, finish, msg))

    def _pool_fields(self, ident, inp, content, provider, ctoks, latency, finish, msg):
        msg = msg or {}
        vote, raw = classify(content, finish, msg)
        refusal = isinstance(provider, str) and provider.endswith(":refusal")
        resp_model = None
        if isinstance(provider, str) and ":" in provider and not refusal:
            resp_model = provider.split(":", 1)[1] or None
        ref = inp.reference
        fields = {
            "vote": vote, "raw_text": raw, "parse_version": PARSE_VERSION,
            "judge_requested": P.JUDGE_REQUESTED, "provider": P.PROVIDER, "response_model": resp_model,
            "system_fingerprint": msg.get("_system_fingerprint"), "response_id": msg.get("_response_id"),
            "finish_reason": finish, "prompt_tokens": msg.get("_prompt_tokens"), "completion_tokens": ctoks,
            "max_tokens": P.CAP, "temperature_sent": None, "temperature_label": P.TEMPERATURE_LABEL,
            "http_status": 400 if refusal else 200,
            "latency_ms": int(round(1000 * latency)),
            "system_template_sha": ident["system_template_sha"], "rubric_sha": ident["rubric_sha"],
            "user_template_sha": ident["user_template_sha"], "schema_sha": ident["schema_sha"],
            "prompt_template_blob": ident["prompt_template_blob"], "script_blob": ident["script_blob"],
            "combiner_blob": ident["combiner_blob"],
            "reference_row_id": ref.row_id if ref else None, "reference_vintage": ref.vintage if ref else None,
            "stem_key": inp.stem_key, "session_id": self.session_id, "batch_id": inp.batch_id,
            "pool_id": self.ctx["pool_id"], "snapshot_id": self.ctx.get("snapshot_id")}
        return fields

    def _pipelined_poster(self, transport, out, workers, rate=None):
        """E-3: the pipelined path. transport: a pool.TwoPhase whose max_inflight admits workers."""
        if not isinstance(transport, POOL.TwoPhase):
            refuse("run: the pooled path (workers %d) needs a pool.TwoPhase transport (reserve / send / resolve), got"
                   " %r" % (workers, type(transport).__name__))
        if workers > int(transport.max_inflight):
            refuse("run: workers %d > the transport's max_inflight %d: refused before any post" % (
                workers, int(transport.max_inflight)))
        K.check_rj_pin()
        P.verify_rr_config()
        out("[POOL] workers %d (pipelined path; journal max_inflight %d; registered maximum %d)" % (
            workers, int(transport.max_inflight), POOL.MAX_INFLIGHT))
        n = self.prescan(out)
        expected = [dict(zip(dv2verdicts.SCHEDULE_COLS, r)) for r in self.store.pending()]
        if MUTANT == "stale_pending" and self.store.path in _LAST_PENDING:
            expected = _LAST_PENDING[self.store.path]
        _LAST_PENDING[self.store.path] = expected
        ident = self.identity(self.rubric, self.ctx, self.manifest, self.material_none_registration)
        pool = POOL.PostingPool(transport, expected, workers, self._pool_prepare,
                                lambda ctx, t, o: self._pool_result(ident, ctx, t, o), out=out, rate_cfg=rate)
        self.last_pool = pool
        before, scans_before = self.posts, self.poster_scans
        interrupted = False
        try:
            self.store.drain(pool.poster)
        except KeyboardInterrupt:
            interrupted = True
            raise
        finally:
            pool.close(interrupted)
            posted, pscans = self.posts - before, self.poster_scans - scans_before
            out(pool.line())
            out("[JUDGE-V2] run %s: pending %d at launch, posted %d, poster scans %d, pending now %d; %s" % (
                self.store.run_id, n, posted, pscans, len(self.store.pending()) if self.store.conn else -1,
                self.stats.line()))
        pool.check_rr("after the run")
        if pool.stop is not None:
            raise pool.stop         # E-4: a stop met after the last reservation is raised once every ticket is recorded
        if pscans != posted:
            refuse("poster coverage: %d posts but %d poster scans" % (posted, pscans))
        if self.stats.without_material and not self.material_none_registration:
            refuse("material coverage: %d scan(s) ran without leak material and no registration declares material NONE"
                   % self.stats.without_material)
        return posted

    def close(self):
        if self.store.conn is not None:
            self.store.conn.close()
            self.store.conn = None


def mixed_strata(store_path):
    """D5 ruling (3) readout hook: the match_status classes of a run stratified by MIXED (question_options_sha starts
    "MIXED:") against same-ordering, from run_meta.question_options_json. Returns {"MIXED": {class: n}, "SAME": {...}}."""
    c = dv2ro.open_ro(store_path)
    try:
        has = c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='run_meta'").fetchone()
        sid = c.execute("SELECT value FROM run_meta WHERE key='schema_id'").fetchone() if has else None
        if sid is None or sid[0] != dv2ro.RUN_SCHEMA_ID:
            refuse("mixed_strata: %s is not a v2 verdict run DB (schema_id %r)" % (store_path, sid))
        row = c.execute("SELECT value FROM run_meta WHERE key='question_options_json'").fetchone()
    finally:
        c.close()
    if row is None:
        refuse("mixed_strata: %s carries no question_options_json" % store_path)
    q = json.loads(row[0])
    out = {"MIXED": {}, "SAME": {}}
    for x in match_verdicts(store_path):
        k = "MIXED" if str(q.get(x["match_id"], "")).startswith("MIXED:") else "SAME"
        out[k][x["status"]] = out[k].get(x["status"], 0) + 1
    return out


def match_verdicts(store_path):
    """C8: every SCHEDULED match of a run, with its run_id, from data_v2's match_status view (the denominator: PENDING
    included) beside this module's combiner on the same two order votes (None when an order is missing). Read-only
    (data_v2.ro.open_ro on a verdict run DB; lint_opens allowlist). Returns a list of dicts sorted by (run_id, match_id,
    draw_index): run_id, match_id, draw_index, status (match_status.combined: a class or 'PENDING'), n_order_verdicts,
    combiner, agree (combiner == status whenever both orders are present)."""
    c = dv2ro.open_ro(store_path)
    try:
        sid = c.execute("SELECT value FROM run_meta WHERE key='schema_id'").fetchone()
        if sid is None or sid[0] != dv2ro.RUN_SCHEMA_ID:
            refuse("match_verdicts: %s is not a v2 verdict run DB" % store_path)
        votes = {}
        for rid, mid, order, draw, vote in c.execute(
                "SELECT run_id, match_id, presentation_order, draw_index, vote FROM verdict"):
            votes[(rid, mid, draw, order)] = vote
        status = c.execute("SELECT run_id, match_id, draw_index, combined, n_order_verdicts FROM match_status"
                           " ORDER BY run_id, match_id, draw_index").fetchall()
    finally:
        c.close()
    out = []
    for rid, mid, draw, comb, n in status:
        v1, v2 = votes.get((rid, mid, draw, 1)), votes.get((rid, mid, draw, 2))
        ours = K.combine(v1, v2)[0] if (v1 is not None and v2 is not None) else None
        out.append({"run_id": rid, "match_id": mid, "draw_index": draw, "status": comb, "n_order_verdicts": n,
                    "combiner": ours, "agree": (ours == comb) if ours is not None else (comb == "PENDING")})
    return out
