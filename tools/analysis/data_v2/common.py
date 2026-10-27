"""data_v2.common: pinned reuse of the functions of record, hash-derived ids, the declared option extractor, labels.

REUSED, NEVER RE-IMPLEMENTED (CK-CLOSE-v1, programme L15013-L15025):
  content_closure.py  blob:1533cb5a56c8e001ddc65d3e2ec0cc4b56aa87e3 (merged 3fdc11b): build_closure, closed_complement,
                      assert_content_disjoint, reserved_clusters, label_conflicts, one_row_per_key, ck_key
  split_side.py       blob:05224b5a4b76e74353bc3931ec69f0b14f0e340b: norm (norm-v1), stem_key, content_key (ck-v1)
  passage_closure.py  (CK-CLOSE-v2, 2026-09-24): the U / P / O / D closure edges; its blob is pinned in PINS like the others
All are loaded BY FILE LOCATION (content_closure's own rule; sys.path is not touched), and each file's LF blob is checked
against the pin above. A different blob is REFUSED: a v2 build names the instrument it ran, and a new version of either
module needs a new pin here (and a review), not a silent pickup.

IDS (hash-derived; no AUTOINCREMENT and no upstream numbering is ever an id; data §1):
  item_id        "i:" + split_side.stem_key(stem)                      the unit of the split and of clustering
  variant_id     "v:" + split_side.content_key(stem, options, contract) the judgeable object; options SORTED by the key
  source_row_id  "r:" + sha256(corpus_version US table US upstream_pk)[:32]   one per upstream row, sentinels included
  response_id    "x:" + sha256(corpus_version US model US legacy_qid)[:32]    one per upstream response row
  component_id   "c:" + the smallest stem_key in the component          (split.py)

OPTION EXTRACTOR opt-v1 (declared; a new rule is a version bump): an option that is the repr of an lm-eval harness
argument pair "{'arg_0': <prompt>, 'arg_1': <continuation>}" contributes its arg_1 continuation; any other str is kept
as is; a non-str option is json.dumps(sort_keys=True). Why: the union corpus's BBH options_json carries the harness pairs,
whose arg_0 is the few-shot prompt rendered in EACH MODEL'S CHAT TEMPLATE (92,176 of 388,908 union eval rows differ from
corpus_questions only by that rendering). Keying on the raw pair would make every chat template its own variant; the
answer contract is the continuation. The raw options_json is kept VERBATIM for every source_row (its own column) and every
response (in the content-addressed table options_ordered, keyed by options_ordered_sha; a response row carries the sha, and
the sha alone is NOT the verbatim text: the table is). [CORRECTED 2026-09-24 on the data-steward's check of 5618b78: the
first version stored only the sha for responses while this docstring called it verbatim.]

DEV LABEL: every output of a seed that starts with "DEV-" carries OF_RECORD_DEV = "DEV, NOT OF RECORD" in its meta, its
file names and its manifest.
"""
import ast
import hashlib
import importlib.util
import json
import os
import sys
import zlib

from . import ro

HERE = os.path.dirname(os.path.abspath(__file__))
ANALYSIS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(ANALYSIS))
DATA_ROOT = os.environ.get("TAXOARENA_DATA_ROOT", ROOT)

PINS = {
    "content_closure": "1533cb5a56c8e001ddc65d3e2ec0cc4b56aa87e3",
    "split_side": "05224b5a4b76e74353bc3931ec69f0b14f0e340b",
    # CK-CLOSE-v2's passage edges (U / P / O / D; ARCH-V2-CK-CLOSE-V2, programme L16101-L16130); a NEW module, its own pin
    "passage_closure": "003d5d4ef28bd6f5ed9b5020b669e206d995d92e",
}
OPTION_EXTRACTOR = "opt-v1"
OF_RECORD_DEV = "DEV, NOT OF RECORD"
US = "\u001f"

QUARANTINED = {
    "Meta-Llama-3-70B-Instruct": "CONTEXT rule 6 / memory eval-id-space-repair: its eval rows carry the text of other"
                                 " question ids; re-keyed by its own text here, returned only on an explicit flag",
}


def _refuse(msg):
    raise SystemExit("[DATA-V2] " + msg)


# The retired upstream eval_results.is_reserved flag (the pre-v2 id-split marker). It lives ONLY in its own table of the
# corpus DB, as a legacy alias for audits of the old id split (the family of the G2 positive control); the v2 split and
# view code never reads it. Two locks: (1) guard_retired, called by split.load_corpora on every corpus it opens, REFUSES a
# `response` table that carries the column; (2) gates.py --selftest scans the source of split.py and views.py and refuses
# if either names it.
RETIRED_NAMES = ("retired_legacy_flag", "legacy_is_reserved")


def guard_retired(conn, where):
    cols = {r[1] for r in conn.execute("PRAGMA table_info(response)")}
    bad = sorted(cols & set(RETIRED_NAMES))
    if bad:
        _refuse("%s: the response table carries retired column(s) %s; the v2 split never reads them" % (where, bad))
    return 0


def _load_by_path(name):
    path = os.path.join(ANALYSIS, name + ".py")
    blob = ro.git_blob_lf(path)
    if blob != PINS[name]:
        _refuse("%s blob:%s is not the pinned blob:%s; a new version needs a new pin in data_v2/common.py"
                % (path, blob, PINS[name]))
    m = sys.modules.get(name)
    if m is not None:
        f = getattr(m, "__file__", None)
        if f is None or os.path.normcase(os.path.abspath(f)) != os.path.normcase(path):
            _refuse("a module named %s is already imported from %r, not %s" % (name, f, path))
        return m
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


cc = _load_by_path("content_closure")
split_side = _load_by_path("split_side")
if cc.split_side is not split_side:
    _refuse("content_closure did not load the pinned split_side")
pc = _load_by_path("passage_closure")


def h32(*parts):
    return hashlib.sha256(US.join(str(p) for p in parts).encode("utf-8")).hexdigest()[:32]


def item_id_of_key(stem_key):
    return "i:" + stem_key


def variant_id_of_key(ck):
    return "v:" + ck


def source_row_id(corpus_version, table, upstream_pk):
    return "r:" + h32(corpus_version, table, upstream_pk)


def response_id(corpus_version, model, legacy_qid):
    return "x:" + h32(corpus_version, model, legacy_qid)


def extract_option(o):
    if isinstance(o, str):
        if o.startswith("{'arg_0'") or o.startswith('{"arg_0"'):
            try:
                d = ast.literal_eval(o)
            except (ValueError, SyntaxError):
                return o
            if isinstance(d, dict) and isinstance(d.get("arg_1"), str):
                return d["arg_1"]
        return o
    return json.dumps(o, sort_keys=True)


def extract_options(options_json):
    if options_json is None or options_json == "":
        return []
    v = json.loads(options_json)
    if not isinstance(v, list):
        _refuse("options_json is not a list: %r" % (options_json[:80],))
    return [extract_option(o) for o in v]


def sorted_norm_options(options):
    return sorted((split_side.norm(o) for o in options), key=lambda s: s.encode("utf-8"))


def options_ordered_sha(options_json):
    """Content address of one raw options_json: sha256("N") for NULL, sha256("S" + raw) otherwise, first 32 hex (a NULL
    and an empty string differ, so the stored text is reconstructed verbatim)."""
    tag = "N" if options_json is None else "S" + options_json
    return hashlib.sha256(tag.encode("utf-8")).hexdigest()[:32]


def options_raw(conn, sha):
    """The verbatim options_json behind options_ordered_sha (None for a NULL); refuses a row whose bytes do not hash back
    to its key."""
    row = conn.execute("SELECT is_null, options_json_zlib FROM options_ordered WHERE options_ordered_sha=?", (sha,)).fetchone()
    if row is None:
        _refuse("options_ordered has no row %s" % sha)
    raw = None if row[0] else zlib.decompress(row[1]).decode("utf-8")
    if options_ordered_sha(raw) != sha:
        _refuse("options_ordered row %s does not hash back to its key" % sha)
    return raw


LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def answer_text(target, options):
    """The answer TEXT behind a letter target ('C' or '(C)') when options exist; else the target itself (the rule of
    content_closure._letter_answer, restated because that helper is private)."""
    if target is None:
        return None
    t = target.strip()
    if options:
        if len(t) == 1 and t in LETTERS and LETTERS.index(t) < len(options):
            return options[LETTERS.index(t)]
        if len(t) == 3 and t[0] == "(" and t[2] == ")" and t[1] in LETTERS and LETTERS.index(t[1]) < len(options):
            return options[LETTERS.index(t[1])]
    return t


class KeyCache:
    """stem_key / content_key memoised by the raw strings (eval rows repeat one text across up to 47 models)."""

    def __init__(self):
        self._stem = {}
        self._ck = {}

    def stem(self, text):
        k = self._stem.get(text)
        if k is None:
            if split_side.norm(text) == "":
                _refuse("an empty stem (after norm-v1) has no content key")
            k = split_side.stem_key(text)
            self._stem[text] = k
        return k

    def variant(self, text, options_json, contract):
        key = (text, options_json, contract)
        v = self._ck.get(key)
        if v is None:
            opts = extract_options(options_json)
            v = (variant_id_of_key(split_side.content_key(text, opts, contract)), opts)
            self._ck[key] = v
        return v


def is_dev_seed(seed):
    return isinstance(seed, str) and seed.startswith("DEV-")
