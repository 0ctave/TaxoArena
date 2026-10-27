"""passage_closure: the passage-level closure edges of CK-CLOSE-v2 (ARCH-V2-CK-CLOSE-V2; docs/judge_v2_program.md L16101-L16130).

CK-CLOSE-v2 = CK-CLOSE-v1 (content_closure.py, unchanged, blob 1533cb5a) + the universe rule U (applied in data_v2.split)
+ three CLOSURE EDGES computed here and added to the split's union-find BEFORE the strata and the draw:

  P  passages in stems   items A != B are joined when some stem of A and some stem of B share a run of N = 20 or more
                         consecutive tokens, EVERY 8-shingle of which is UNMASKED; the run lies on one diagonal of both
                         texts (the same offset in both)
  O  options             the same rule, applied to each variant's options (options_sorted_json, joined by single spaces)
  D  degree normaliser   A and B are joined when split_side.stem_key(d(sA)) == split_side.stem_key(d(sB)) for some stems;
                         d = re.sub(r"\\s*" + re.escape("\\textdegree") + r"(\\{\\})?\\s*", "°", s), then
                         re.sub(r"\\s*°\\s*", "°", s). An EDGE, NOT a key change: stem_key, the item ids and
                         NORMALISER_VERSION stay norm-v1

TOKENS AND SHINGLES: tokens(s) = re.findall(r"\\w+", s.casefold()) (= judge_v2.induction._tokens). A shingle is an EXACT
8-tuple of consecutive tokens. Its identity here is exact: every token gets an integer id from a vocabulary, and the
shingle key is the 8 ids packed as big-endian unsigned 32-bit integers (injective; no hashing). Python hash() is never
used as an identity (the dicts below are keyed by those exact byte strings). collision_check() re-keys every distinct
shingle by sha256 over its tokens joined by U+001F and asserts that the two identities agree (0 collisions).

df(shingle) = the number of DISTINCT items of the universe (all corpora, all sides) holding it, per channel (stems for P,
option strings for O). MASKING (author choice 2):
  an item whose stratum source is BBH   a shingle is masked iff MORE THAN BBH_SHARE = 5% of the items of that item's own
                                        stratum (the BBH task) hold it; the global R does NOT apply
  any other item                        a shingle is masked iff df > R = 6 (global)
The stratum of an item is ITS OWN modal (source, domain) vote (the caller supplies it); the split's component strata come
later and are not used here.
A PAIR (A, B) USES a shingle only when it is unmasked for A AND unmasked for B (PAIR_RULE "both"). The registration states
the mask per item and does not say how a pair of items under two different mask rules (a BBH item and a non-BBH item)
combines them; "both" is the builder's reading, chosen because it REPRODUCES the registration's DEV-SIM before U exactly
(21,384 items -> 18,938 components, largest 14 BBH, MMLU-Pro largest 6; measured on the ED3 corpora, 2026-09-24), and
it is the conservative-against-template reading (a shingle a template-mask hides for one side is never evidence).

RESIDUAL (disclosed): pairs whose longest unmasked common run is 15-19 tokens are COUNTED (band_15_19), never joined.

No seed, no clock and no randomness enter this module; the edge set is returned sorted and its sha16 (edge_set_sha16) is
the determinism witness (K2).

    import passage_closure as pc   (data_v2.common loads it by path and pins its blob)
    r = pc.compute_edges(items, split_side.stem_key)
    # items: {item_id: {"stems": [...], "options": [...], "source": s, "stratum": (s, d)}}, the universe after U
    r["edges"]["P"], r["edges"]["O"], r["edges"]["D"]    # sorted (a, b) pairs with a < b
"""
import hashlib
import re
import struct
from collections import Counter, defaultdict

N = 20                   # minimum run, in tokens
K = 8                    # shingle length, in tokens
R = 6                    # global df cap: masked iff df > R
BBH_SOURCE = "BBH"
BBH_SHARE = 0.05         # BBH: masked iff MORE THAN 5% of the item's own stratum hold the shingle
PAIR_RULE = "both"       # a pair uses a shingle only if it is unmasked for both items
RUN_SHINGLES = N - K + 1  # 13 consecutive shingles = 20 tokens
BAND_LO = 15             # the disclosed residual band, in tokens
_TOKEN = re.compile(r"\w+")
_DEG1 = re.compile(r"\s*" + re.escape("\\textdegree") + r"(\{\})?\s*")
_DEG2 = re.compile(r"\s*°\s*")
_US = "\u001f"


def tokens(s):
    return _TOKEN.findall(s.casefold())


def degree_norm(s):
    return _DEG2.sub("°", _DEG1.sub("°", s))


class _Vocab:
    def __init__(self):
        self.ids = {}
        self.words = []

    def encode(self, toks):
        out = []
        for t in toks:
            i = self.ids.get(t)
            if i is None:
                i = self.ids[t] = len(self.words)
                self.words.append(t)
            out.append(i)
        return out


def _shingle_keys(ids):
    """Exact shingle keys of one token-id list: position -> 8 ids packed big-endian (injective)."""
    return [struct.pack(">8I", *ids[p:p + K]) for p in range(len(ids) - K + 1)]


def _channel(items, texts_of, out):
    """One channel (P over stems, O over option strings). Returns (edges set, band pairs set, df Counter-of-df,
    distinct shingles, vocab-decodable keys for the collision check)."""
    order = sorted(items)
    vocab = _Vocab()
    enc = {}                        # item -> list of shingle-key lists, one per distinct text
    df = Counter()
    sdf = Counter()                 # (stratum, key) -> BBH items of that stratum holding it
    for it in order:
        lists = []
        seen = set()
        for t in sorted(set(texts_of(it))):
            ks = _shingle_keys(vocab.encode(tokens(t)))
            if ks:
                lists.append(ks)
                seen.update(ks)
        enc[it] = lists
        for k in seen:
            df[k] += 1
        if items[it]["source"] == BBH_SOURCE:
            st = items[it]["stratum"]
            for k in seen:
                sdf[(st, k)] += 1
    n_stratum = Counter(items[it]["stratum"] for it in order)

    def masked(it, k):
        if items[it]["source"] == BBH_SOURCE:
            st = items[it]["stratum"]
            return sdf[(st, k)] > BBH_SHARE * n_stratum[st]
        return df[k] > R

    postings = defaultdict(list)    # key -> [(item index, text index, position)]
    idx = {it: n for n, it in enumerate(order)}
    for it in order:
        for ti, ks in enumerate(enc[it]):
            for p, k in enumerate(ks):
                if df[k] >= 2 and not masked(it, k):
                    postings[k].append((idx[it], ti, p))
    diag = defaultdict(list)
    for k in sorted(postings):
        occ = postings[k]
        if len({o[0] for o in occ}) < 2:
            continue
        for x in range(len(occ)):
            ia, ta, pa = occ[x]
            for y in range(x + 1, len(occ)):
                ib, tb, pb = occ[y]
                if ia == ib:
                    continue
                if ia < ib:
                    diag[(ia, ta, ib, tb, pa - pb)].append(pa)
                else:
                    diag[(ib, tb, ia, ta, pb - pa)].append(pb)
    best = {}
    for (ia, ta, ib, tb, _d), ps in diag.items():
        ps = sorted(set(ps))
        run = longest = 1
        for q in range(1, len(ps)):
            run = run + 1 if ps[q] == ps[q - 1] + 1 else 1
            longest = max(longest, run)
        toks = longest + K - 1
        if toks > best.get((ia, ib), 0):
            best[(ia, ib)] = toks
    edges = sorted((order[a], order[b]) for (a, b), t in best.items() if t >= N)
    band = sorted((order[a], order[b]) for (a, b), t in best.items() if BAND_LO <= t < N)
    df_table = Counter(df.values())
    return edges, band, df_table, df, vocab


def _collisions(df, vocab):
    """0 when the exact keys and sha256-over-U+001F keys induce the same partition of the distinct shingles."""
    seen = {}
    bad = 0
    for k in df:
        ids = struct.unpack(">8I", k)
        h = hashlib.sha256(_US.join(vocab.words[i] for i in ids).encode("utf-8")).digest()
        if h in seen and seen[h] != k:
            bad += 1
        seen[h] = k
    return bad + (len(df) - len(seen))


def degree_edges(items, stem_key):
    """D: items grouped by stem_key(degree_norm(stem)) over ALL their stems (a stem d() leaves unchanged keys to its own
    item's key, so it can only meet an item whose stem d() changed); each group becomes a chain of edges between its
    sorted items. stem_key is split_side.stem_key, passed by the caller (this module imports no pinned module)."""
    groups = defaultdict(set)
    for it in sorted(items):
        for s in sorted(set(items[it]["stems"])):
            groups[stem_key(degree_norm(s))].add(it)
    edges = set()
    for key in sorted(groups):
        g = sorted(groups[key])
        for a, b in zip(g, g[1:]):
            edges.add((a, b))
    return sorted(edges)


def edge_set_sha16(edges):
    h = hashlib.sha256()
    for kind in ("P", "O", "D"):
        for a, b in edges[kind]:
            h.update(("%s\t%s\t%s\n" % (kind, a, b)).encode("utf-8"))
    return h.hexdigest()[:16]


def compute_edges(items, stem_key, out=print):
    """items: {item_id: {"stems": [str], "options": [str], "source": str, "stratum": (source, domain)}} over the
    UNIVERSE (after U). Returns {"edges": {"P", "O", "D"}, "band_15_19": {"P", "O"}, "df_table": {"P", "O"},
    "distinct_shingles": {"P", "O"}, "collisions": {"P", "O"}, "edge_set_sha16"}."""
    res = {"edges": {}, "band_15_19": {}, "df_table": {}, "distinct_shingles": {}, "collisions": {}}
    for kind, texts_of in (("P", lambda it: items[it]["stems"]), ("O", lambda it: items[it]["options"])):
        e, band, dft, df, vocab = _channel(items, texts_of, out)
        res["edges"][kind] = e
        res["band_15_19"][kind] = len(band)
        res["df_table"][kind] = dict(sorted(dft.items()))
        res["distinct_shingles"][kind] = len(df)
        res["collisions"][kind] = _collisions(df, vocab)
    res["edges"]["D"] = degree_edges(items, stem_key)
    res["edge_set_sha16"] = edge_set_sha16(res["edges"])
    return res
