"""The split side function, side = f(item) (FRAMEWORK.md Stage 0; item 18 SPLIT-FUNCTION-IMPL).

This module is the Python half of a two-language, byte-identical function. The Kotlin half is
src/main/kotlin/taxonomy/dataset/SplitSide.kt. Every constant below is a literal in exactly one
place per language and is pinned by experiment_configs/split_function_vectors.json, which this
module generates (`--write-vectors`) and both languages assert (`--selftest`,
SplitSideVectorsTest). A normaliser change is a NORMALISER_VERSION bump, never a silent re-split.

Two tiers, both write-once:
  (a) pinned corpora: EVAL iff the id is in the frozen list (or the item's stem key equals a
      pinned item's stem key: content closure); GATE iff side_hash(family_id or stem_key) lands
      in [GATE_LOWER, GATE_UPPER) among the non-EVAL items; TRAIN otherwise. Pool ids stay
      hashes of id lists (pool_guard.compute_pool_id) and are never recomputed from content.
  (b) items ingested after the pin: h = uint64(sha256(NORMALISER_VERSION || (family_id or
      content_key))) mod SIDE_MODULUS; EVAL iff h < EVAL_UPPER; GATE iff GATE_LOWER <= h <
      GATE_UPPER; TRAIN otherwise.

content_key = sha256(norm(stem) || sorted norm(options) || contract_id) with explicit
separators (U+001F between fields, U+001E before every option) so the concatenation is injective.
norm = NFKC, ASCII-only case folding (A-Z -> a-z; deliberately not full Unicode lowercasing,
on which the JVM and CPython disagree, e.g. U+0130), whitespace runs collapsed to one U+0020,
trimmed. Whitespace is the explicit set WHITESPACE_CLASS, not either runtime's isspace().
"""
import hashlib
import json
import os
import re
import sys
import unicodedata

NORMALISER_VERSION = "norm-v1"
KEY_RULE = "ck-v1"
SIDE_MODULUS = 1000
EVAL_UPPER = 300
GATE_LOWER = 300
GATE_UPPER = 400

FIELD_SEP = "\u001f"
OPTION_SEP = "\u001e"

EVAL, GATE, TRAIN = "EVAL", "GATE", "TRAIN"

# The explicit whitespace class, identical to SplitSide.WHITESPACE_CLASS. NFKC already maps
# U+00A0, U+2000-U+200A, U+202F, U+205F and U+3000 to U+0020; the rest are listed so the
# behaviour does not depend on the runtime's notion of whitespace.
WHITESPACE_CLASS = "[\\t\\n\\x0b\\x0c\\r \\x85\\xa0\\u1680\\u2000-\\u200a\\u2028\\u2029\\u202f\\u205f\\u3000]+"
_WS = re.compile(WHITESPACE_CLASS)
_ASCII_UPPER = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
VECTORS_PATH = os.path.join(ROOT, "experiment_configs", "split_function_vectors.json")


def norm(s):
    """NFKC, ASCII case fold, whitespace runs -> one U+0020, trimmed. Idempotent."""
    s = unicodedata.normalize("NFKC", s)
    s = s.translate(_ASCII_UPPER)
    s = _WS.sub(" ", s)
    return s.strip(" ")


def _utf8_order(s):
    return s.encode("utf-8")


def content_key(stem, options, contract_id):
    """hex sha256 over norm(stem) U+001F (U+001E norm(option) for each sorted option) U+001F contract_id.

    Options are sorted by their UTF-8 byte sequence (= code point order), which both languages
    can reproduce exactly; the JVM's default String order is UTF-16 code-unit order and differs
    above U+FFFF.
    """
    opts = sorted((norm(o) for o in options), key=_utf8_order)
    # Each option is PREFIXED by the separator so [] and [""] differ and the encoding is injective.
    payload = norm(stem) + FIELD_SEP + "".join(OPTION_SEP + o for o in opts) + FIELD_SEP + contract_id
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def stem_key(text):
    """Options-free key: content_key(text, [], ""). The tree guard keys on it because an embedding
    carries only the raw text; it is strictly more conservative than the full key."""
    return content_key(text, [], "")


def side_hash(key, normaliser_version=NORMALISER_VERSION):
    """uint64 of the first 8 big-endian bytes of sha256(normaliser_version U+001F key), mod SIDE_MODULUS."""
    d = hashlib.sha256((normaliser_version + FIELD_SEP + key).encode("utf-8")).digest()
    return int.from_bytes(d[:8], "big") % SIDE_MODULUS


def side_of_hash(h):
    """Exactly one side for every h below SIDE_MODULUS."""
    if h < EVAL_UPPER:
        return EVAL
    if GATE_LOWER <= h < GATE_UPPER:
        return GATE
    return TRAIN


def tier_b(family_id, content_key_hex):
    """Side of an item ingested after the pin."""
    return side_of_hash(side_hash(family_id if family_id else content_key_hex))


def tier_a(pinned_ids, pinned_stem_keys, item_id, item_stem_key, family_id=None):
    """Side of an item of a pinned corpus: EVAL by id or by content closure, GATE by the hash
    restricted to non-EVAL items, TRAIN otherwise."""
    if item_id in pinned_ids or item_stem_key in pinned_stem_keys:
        return EVAL
    h = side_hash(family_id if family_id else item_stem_key)
    if GATE_LOWER <= h < GATE_UPPER:
        return GATE
    return TRAIN


def function_stamp(pool_id=None):
    return {
        "normaliser_version": NORMALISER_VERSION,
        "key_rule": KEY_RULE,
        "modulus": SIDE_MODULUS,
        "eval_upper": EVAL_UPPER,
        "gate_lower": GATE_LOWER,
        "gate_upper": GATE_UPPER,
        "pool_id": pool_id,
    }


# ── per-row assertion at write time ────────────────────────────────────────────────────────

class SideMismatch(SystemExit):
    pass


def assert_row(stored_side, family_id, content_key_hex, where="item_side"):
    """Recompute a tier-b row's side and refuse a stored side that differs (FATAL)."""
    expected = tier_b(family_id, content_key_hex)
    if stored_side != expected:
        raise SideMismatch("[SPLIT-SIDE] %s: stored side %s != recomputed %s for key %s (family %s)"
                           % (where, stored_side, expected, content_key_hex[:16], family_id))
    return expected


ITEM_SIDE_DDL = """
CREATE TABLE IF NOT EXISTS item_side (
    content_key        TEXT NOT NULL,
    family_id          TEXT,
    side               TEXT NOT NULL CHECK (side IN ('EVAL','GATE','TRAIN')),
    contract_id        TEXT NOT NULL,
    cell               TEXT,
    pool_id_at_ingest  TEXT,
    normaliser_version TEXT NOT NULL,
    recorded_at        INTEGER NOT NULL,
    PRIMARY KEY (content_key)
) WITHOUT ROWID
"""


def record_sides(conn, rows, pool_id_at_ingest=None, now_millis=0):
    """Append tier-b rows (content_key, family_id, side, contract_id, cell) to item_side.

    Append-only and write-once: an existing row is never updated (INSERT OR IGNORE), and every
    row's side is recomputed and asserted before the insert. Returns the number of new rows.
    """
    conn.execute(ITEM_SIDE_DDL)
    n = 0
    for (ck, family_id, side, contract_id, cell) in rows:
        assert_row(side, family_id, ck, where="record_sides")
        existing = conn.execute("SELECT side FROM item_side WHERE content_key = ?", (ck,)).fetchone()
        if existing is not None:
            if existing[0] != side:
                raise SideMismatch("[SPLIT-SIDE] item_side already holds %s for %s, refusing %s" % (existing[0], ck[:16], side))
            continue
        conn.execute(
            "INSERT OR IGNORE INTO item_side (content_key, family_id, side, contract_id, cell, pool_id_at_ingest,"
            " normaliser_version, recorded_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (ck, family_id, side, contract_id, cell, pool_id_at_ingest, NORMALISER_VERSION, now_millis))
        n += 1
    return n


# ── vectors ────────────────────────────────────────────────────────────────────────────────

def _boundary_stem(target_h):
    """A stem 'boundary-<n>' whose stem_key hashes to exactly target_h (deterministic search)."""
    n = 0
    while True:
        stem = "boundary-%d" % n
        if side_hash(stem_key(stem)) == target_h:
            return stem
        n += 1


def build_vectors():
    cases = [
        ("ascii", "What is 2+2?", ["4", "5", "3", "22"], "MC_LETTER", None),
        ("case-fold-ascii", "WHAT Is 2+2?", ["4", "5", "3", "22"], "MC_LETTER", None),
        ("whitespace-runs", "  What   is\t2+2?\n", ["4 ", " 5", "3", "22"], "MC_LETTER", None),
        ("option-order", "What is 2+2?", ["22", "3", "5", "4"], "MC_LETTER", None),
        ("contract-change", "What is 2+2?", ["4", "5", "3", "22"], "IMPORTED:exact_match", None),
        ("empty-options", "Prove that sqrt(2) is irrational.", [], "IMPORTED:exact_match", None),
        ("nfc-composed", "café au lait", ["oui", "non"], "MC_LETTER", None),
        ("nfd-decomposed", "café au lait", ["oui", "non"], "MC_LETTER", None),
        ("nfkc-compat", "ＡＢＣ ①", ["ﬁ"], "MC_LETTER", None),
        ("dotted-capital-i", "İstanbul", ["a"], "MC_LETTER", None),
        ("cjk", "東京は日本の首都です。", ["はい", "いいえ"], "MC_LETTER", None),
        ("supplementary-sort", "emoji options", ["\U0001F600", "ﬁ", "z"], "MC_LETTER", None),
        ("family-override", "any stem", ["x"], "MC_LETTER", "family:bbh/navigate/template-7"),
        ("nbsp-and-ideographic-space", "a b　c d", ["e f"], "MC_LETTER", None),
    ]
    for label, target in (("boundary-299", 299), ("boundary-300", 300), ("boundary-399", 399), ("boundary-400", 400), ("boundary-0", 0), ("boundary-999", 999)):
        cases.append((label, _boundary_stem(target), [], "", None))
    out = []
    for label, stem, options, contract_id, family_id in cases:
        ck = content_key(stem, options, contract_id)
        sk = stem_key(stem)
        h = side_hash(family_id if family_id else ck)
        out.append({
            "label": label,
            "stem": stem,
            "options": options,
            "contract_id": contract_id,
            "family_id": family_id,
            "norm_stem": norm(stem),
            "content_key": ck,
            "stem_key": sk,
            "stem_h": side_hash(sk),
            "h": h,
            "side": side_of_hash(h),
        })
    return {
        "normaliser_version": NORMALISER_VERSION,
        "key_rule": KEY_RULE,
        "modulus": SIDE_MODULUS,
        "eval_upper": EVAL_UPPER,
        "gate_lower": GATE_LOWER,
        "gate_upper": GATE_UPPER,
        "field_sep": FIELD_SEP,
        "option_sep": OPTION_SEP,
        "whitespace_class": WHITESPACE_CLASS,
        "cases": out,
    }


def load_vectors(path=VECTORS_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def selftest(path=VECTORS_PATH):
    v = load_vectors(path)
    assert v["normaliser_version"] == NORMALISER_VERSION, "normaliser version drift"
    assert (v["modulus"], v["eval_upper"], v["gate_lower"], v["gate_upper"]) == (SIDE_MODULUS, EVAL_UPPER, GATE_LOWER, GATE_UPPER)
    assert v["field_sep"] == FIELD_SEP and v["option_sep"] == OPTION_SEP and v["whitespace_class"] == WHITESPACE_CLASS
    n = 0
    for case in v["cases"]:
        ck = content_key(case["stem"], case["options"], case["contract_id"])
        assert ck == case["content_key"], "content_key mismatch on %s" % case["label"]
        assert stem_key(case["stem"]) == case["stem_key"], "stem_key mismatch on %s" % case["label"]
        assert norm(case["stem"]) == case["norm_stem"], "norm mismatch on %s" % case["label"]
        assert norm(norm(case["stem"])) == norm(case["stem"]), "norm not idempotent on %s" % case["label"]
        h = side_hash(case["family_id"] if case["family_id"] else ck)
        assert h == case["h"], "h mismatch on %s" % case["label"]
        assert side_of_hash(h) == case["side"], "side mismatch on %s" % case["label"]
        assert tier_b(case["family_id"], ck) == case["side"]
        n += 1
    # bracket disjointness and coverage over the whole modulus
    counts = {EVAL: 0, GATE: 0, TRAIN: 0}
    for h in range(SIDE_MODULUS):
        counts[side_of_hash(h)] += 1
    assert counts == {EVAL: EVAL_UPPER, GATE: GATE_UPPER - GATE_LOWER, TRAIN: SIDE_MODULUS - GATE_UPPER}, counts
    # option order and contract sensitivity
    a = content_key("q", ["x", "y"], "c"); b = content_key("q", ["y", "x"], "c"); c = content_key("q", ["x", "y"], "d")
    assert a == b and a != c
    # boundary vectors landed where engineered
    by_label = {c_["label"]: c_ for c_ in v["cases"]}
    assert by_label["boundary-299"]["side"] == EVAL and by_label["boundary-300"]["side"] == GATE
    assert by_label["boundary-399"]["side"] == GATE and by_label["boundary-400"]["side"] == TRAIN
    # nfc == nfd
    assert by_label["nfc-composed"]["content_key"] == by_label["nfd-decomposed"]["content_key"]
    # the per-row assertion trips on a tampered side
    tampered = EVAL if by_label["ascii"]["side"] != EVAL else TRAIN
    try:
        assert_row(tampered, None, by_label["ascii"]["content_key"])
        raise AssertionError("assert_row accepted a tampered side")
    except SideMismatch:
        pass
    # record_sides refuses a tampered row and is append-only
    import sqlite3
    mem = sqlite3.connect(":memory:")
    ck0 = by_label["ascii"]["content_key"]
    assert record_sides(mem, [(ck0, None, by_label["ascii"]["side"], "MC_LETTER", None)]) == 1
    assert record_sides(mem, [(ck0, None, by_label["ascii"]["side"], "MC_LETTER", None)]) == 0
    try:
        record_sides(mem, [(ck0, None, tampered, "MC_LETTER", None)])
        raise AssertionError("record_sides accepted a tampered side")
    except SideMismatch:
        pass
    print("split_side selftest: %d vectors OK; brackets EVAL=%d GATE=%d TRAIN=%d over %d; normaliser %s"
          % (n, counts[EVAL], counts[GATE], counts[TRAIN], SIDE_MODULUS, NORMALISER_VERSION))
    return 0


def main(argv):
    if "--write-vectors" in argv:
        v = build_vectors()
        with open(VECTORS_PATH, "w", encoding="utf-8", newline="\n") as f:
            json.dump(v, f, indent=2, ensure_ascii=True)
            f.write("\n")
        print("wrote %d vectors to %s" % (len(v["cases"]), VECTORS_PATH))
        return 0
    if "--selftest" in argv:
        return selftest()
    print(__doc__)
    print("usage: split_side.py --selftest | --write-vectors")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
