"""CK-CLOSE-v1: the content-closure rule for every new pool, construction and policy fit (Python half).

Rule of record: docs/judge_v2_program.md L14280-L14340 (CONTENT-DISJOINT-SPLIT-AUDIT, 6f24e04; proposed there), with the
four conditions of the review docs/reviews/2026-09-23_content_disjoint_split_audit_review.md (1df2cf1) and the follow-ups
at L14455-L14487 (SPLIT-FOLLOWUPS). Adopted by the author on 2026-09-23 (recorded by the registrar at c017a31).
READY review: docs/reviews/READY_content_closure.md (e9fe11c, READY WITH CONDITIONS at blob 5324cbe); conditions C1-C4
and D5-D10 are lifted in this build (see "READY conditions" below).

THE RULE (and where each clause lives in this module):
  key       split_side.stem_key (norm-v1, ck-v1, options-FREE), reused, never re-implemented   -> ck_key()
            (options are dropped on purpose: 367 of 382 GPQA twins on paeec have their options shuffled;
            an EMPTY stem is refused: it would collapse every such id into one key)
  global    the key set is computed over ALL corpora and pools of one build (review condition 2:
            3 MATH reserved ids have MMLU-Pro generation-side twins on paeec)                     -> build_closure()
  sentinel  the key set is EVERY held-out item, routing-only sentinels included (condition 1, D6:
            otherwise 96 GEN rows stay twinned to sentinels on p2dca)                             -> closed_complement()
  direction closure moves GENERATION-side items to routing-only; the reserved (scored) set and the
            pool id are UNCHANGED
  family    where families exist (BFCL base-scenario index family, Multi-SWE org/repo) the family
            is closed too (condition 3); iterated to a fixed point                                -> family_of=
  cluster   within the reserved side, twin groups are CLUSTERED (a cluster id per key), never
            dropped (condition 4); the Kish figure is sum(n^2)/n = DEFF at rho = 1, an UPPER BOUND
            (review D7), never a measured DEFF                                                    -> reserved_clusters()
  answers   answer-TEXT differences within a stem_key group are CLASSIFIED; only an identical
            prompt (same stem, same option set) with a different answer is called a label conflict -> label_conflicts()
  one row   copies of one stem collapsed to one row per stem_key with subset tags (GPQA diamond /
            main / extended); a tool for INGESTING a new pool, never applied to a pinned one       -> one_row_per_key()
  guard     a train side that still shares a key (or a family) with a reserved OR a sentinel id is
            REFUSED by an explicit ContentLeak(SystemExit "[CK-CLOSE] ..."), never an `assert` (holds
            under -O); the sentinel set is a SEPARATE, REQUIRED argument (review D2); the guard prints
            its line on every run, pass or fail (CONTEXT rule 11)                                 -> assert_content_disjoint()

LIMITS (named, not fixed here): near-duplicates below norm-v1 (paraphrase, punctuation beyond NFKC / whitespace / ASCII
case, quoted replies) are not caught; MinHash is out of scope. The options-free key OVER-closes where a generic stem is
shared by unrelated questions ("Which of the following is true?"): on paeec 54 of the 543 moves share no option with any
held twin (21 with stems under 80 characters; review D10). That is a property of the adopted rule, printed by the audit
as a descriptive line. Multi-SWE has NO content key (its stem is the instance id, review D4): its guarantee is the
repo-family closure alone.

text_of / family_of / target_of / tag_of are a mapping or a callable over ids. A text value is a str (the stem) or a
(stem, options) pair, whose options are IGNORED by the key (label_conflicts reads them to classify). Ids must be unique
across the corpora of a build (build_closure refuses a collision rather than guessing a namespace). Every id collection
this module returns is SORTED (ints before strings, each in natural order), so outputs do not depend on the hash seed.

IMPORT: the module does not touch sys.path. It loads tools/analysis/split_side.py by file location (or reuses an already
imported split_side after checking it is that same file, and refuses otherwise). Only the --audit CLI imports pool_guard,
whose own import inserts tools/analysis into sys.path (pool_guard's behaviour, unchanged here).

    import content_closure as cc
    r = cc.build_closure({"GPQA": {"gen": g1, "reserved": r1, "sentinel": ()}, "MATH": {...}}, text_of, family_of=None)
    train = r["closed_gen"]; routing_only = r["routing_only"]      # reserved ids unchanged, pool id unchanged
    cc.assert_content_disjoint(train, reserved, sentinels, text_of, where="before the fit")   # sentinels: REQUIRED
    cluster_of, kish = cc.reserved_clusters(reserved, text_of)     # cluster ids for question-clustered SEs

CLI (zero calls; every DB opened through pool_guard.open_ro: -wal / -journal checked first, then mode=ro&immutable=1):
    python tools/analysis/content_closure.py --selftest            # synthetic, opens no DB; run under python and python -O
    python tools/analysis/content_closure.py --audit --pool p2dca21ab5f4ef3ae
    python tools/analysis/content_closure.py --audit --pool paeec37aa28063c75
    python tools/analysis/content_closure.py --audit --pool p2035adddedd1becb   # BFCL (family closure)
    python tools/analysis/content_closure.py --audit --pool p79fb71114b5c67c2   # Multi-SWE (repo-family closure)
    python tools/analysis/content_closure.py --audit --pool pf844849e133cda4e   # 20NG: NOT IMPLEMENTED (exit 4)
The audit prints the pool id first, the closure, the sentinel leg, the clusters and the answer classes, and each figure
the reviews recorded beside the one computed (MATCH / MISMATCH; a mismatch is reported, never tuned). It writes no
file. Exit codes: 0 all recorded figures match, 1 mismatch (or a guard refusal), 4 not implemented. Worktrees set
TAXOARENA_DATA_ROOT.

WHERE TO CALL IT (consumers that should call this module in future runs; listed 2026-09-23, NONE is changed by this
module, and the pinned ones stay pinned until a new registration):
  Python policy fits and split consumers
    router_clean_policy.py L316-L349 (TRAIN = routed minus pool, L348-L349) and the fits L455-L458 (ROUTER-CLEAN-POLICY,
        route (c)): build_closure + assert_content_disjoint before fit_policies; reserved_clusters for its bootstraps.
    multicorpus_router_e2e.py L86-L93 (MC-E2E) and multicorpus_router.py L27-L38: own 0.30 split, best() fitted on train.
    multicorpus_leaf_router.py (TRAIN side of the union leaves, L7); union_profile_home.py (candidate by grep, unread).
    router_regret.py L35 (train = not in pool).
    rubric_ladder.py L88-L143, rubric_kit.py (L4), rubric_kit2.py L86, j6_rubrics.py: induction material withheld by exact
        text / id, not by stem_key with sentinels.
    stable_cell_set.py L657-L673 (its keyed_train "clean" count); topic_partition.py L466 / L1436 (20NG own split, zero
        by ingest rule (3)).
    profile_interval_union.py: candidate for reserved_clusters (clustered SEs; by grep, unverified).
    PINNED (records or upcoming runs; future versions only): cert_corpus.py, cert_direction_stream.py,
        cert_under_filter.py, split_exposure_*.py (on its branch), pool_guard.py, split_side.py, stack_judge.py.
  Kotlin (the separate item; sentinel and global-closure extension)
    MMLUDatasetFetcher.finishSplit L863-L901: keys every test item INCLUDING sentinels (hence 171) but is called per
        fetcher (L783 seeded split, L816 file split): no global closure across corpora, no family closure, no clusters.
    TrainOnlyGuard (model/TrainOnlyGuard.kt L36-L80) takes its key set from the callers: HeadlessBenchmarkRunner
        L585-L593 (test-set texts incl. sentinels + pool texts), L1128-L1129 (union graft: getReservedQuestionTexts only),
        TaxonomySnapshotManager L615-L616 and L802-L824 (getReservedQuestionTexts), TuiGatewayImpl L192-L193, PoolPin L46.
        Whether getReservedQuestionTexts carries sentinel texts is UNVERIFIED (condition 1).

READY conditions lifted (e9fe11c): C1/D3 key->family chain in the selftest (kills R6); C2/D2 explicit required sentinel
argument + the p2dca sentinel leg (refuses with 96 when the reserved twins are removed; kills R4b); C3/D1 answer-text
classes (paeec 2 real / 4 formatting / 7 punctuation / 76 option sets differ); C4/D4 one_row_per_key with a GPQA-like
nested fixture; D5 p2dca 75 / 96 / 70 pinned in the audit record; D6 direct and component cross-corpus counts; D7 empty
stem refused; D8 no sys.path mutation, sorted outputs; D9 20NG prints NOT IMPLEMENTED; D10 the over-closure line.
"""
import importlib.util
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))


def _load_sibling(name):
    """tools/analysis/<name>.py without touching sys.path: reuse sys.modules[name] only when it IS that file."""
    path = os.path.join(HERE, name + ".py")
    m = sys.modules.get(name)
    if m is not None:
        f = getattr(m, "__file__", None)
        if f is None or os.path.normcase(os.path.abspath(f)) != os.path.normcase(path):
            raise SystemExit("[CK-CLOSE] a module named %s is already imported from %r, not %s" % (name, f, path))
        return m
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


split_side = _load_sibling("split_side")  # the function of record: norm-v1 / ck-v1

RULE = "CK-CLOSE-v1"
KEY_NAME = "split_side.stem_key (%s, %s, options-free)" % (split_side.NORMALISER_VERSION, split_side.KEY_RULE)

# Reasons a generation-side id becomes routing-only, in priority order (the first that applies is recorded).
TWIN_RESERVED = "twin_of_reserved"        # its key equals a reserved id's key
TWIN_SENTINEL = "twin_of_sentinel"        # its key equals a routing-only sentinel's key (condition 1)
FAMILY_RESERVED = "family_of_reserved"    # its family holds a reserved id (condition 3)
FAMILY_SENTINEL = "family_of_sentinel"    # its family holds a sentinel
TWIN_MOVED = "twin_of_moved"              # fixed-point round: key of an id moved earlier (e.g. by family closure)
FAMILY_MOVED = "family_of_moved"          # fixed-point round: family of an id moved earlier (e.g. by key closure)
REASONS = (TWIN_RESERVED, TWIN_SENTINEL, FAMILY_RESERVED, FAMILY_SENTINEL, TWIN_MOVED, FAMILY_MOVED)

# Classes of answer-text differences within one stem_key group (label_conflicts). Only CONFLICT is a label conflict.
PUNCTUATION_ONLY = "punctuation_only"     # equal once every non-alphanumeric character is dropped
FORMATTING_ONLY = "formatting_only"       # equal once LaTeX formatting is normalised (\dfrac / \tfrac -> \frac, ...)
CONFLICT = "conflict"                     # identical prompt (same stem, same option set) and a different answer text
OPTION_SETS_DIFFER = "option_sets_differ" # the option sets differ, so the answer text may differ by construction
ANSWER_CLASSES = (CONFLICT, FORMATTING_ONLY, PUNCTUATION_ONLY, OPTION_SETS_DIFFER)


class ContentLeak(SystemExit):
    """The guard's refusal: a SystemExit ("[CK-CLOSE] ...") that also carries its counts."""

    def __init__(self, msg, **counts):
        super().__init__("[CK-CLOSE] " + msg)
        self.counts = counts


def _refuse(msg):
    raise SystemExit("[CK-CLOSE] " + msg)


def _idkey(i):
    """A total order over mixed id types: ints (not bools) first in numeric order, then everything else by str."""
    if isinstance(i, int) and not isinstance(i, bool):
        return (0, i, "")
    return (1, 0, str(i))


def _sorted(ids):
    return sorted(ids, key=_idkey)


def _getter(m, what):
    """A mapping or a callable over ids -> a function; a missing id is a refusal, never a default."""
    if m is None:
        return None
    if callable(m) and not hasattr(m, "__getitem__"):
        return m

    def get(i):
        try:
            return m[i]
        except (KeyError, IndexError):
            _refuse("%s has no entry for id %r" % (what, i))
    return get


def _stem_of(value):
    if isinstance(value, str):
        return value
    if isinstance(value, (tuple, list)) and len(value) == 2 and isinstance(value[0], str):
        return value[0]
    _refuse("a text value must be a str or a (stem, options) pair, got %r" % (type(value).__name__,))


def _options_of(value):
    if isinstance(value, (tuple, list)) and len(value) == 2 and isinstance(value[0], str):
        return [o if isinstance(o, str) else json.dumps(o, sort_keys=True) for o in (value[1] or [])]
    return []


def ck_key(value):
    """The CK-CLOSE key of one item: split_side.stem_key of the STEM. A (stem, options) pair keys on the stem only:
    the options are deliberately dropped (an options-bearing key misses shuffled twins: GPQA 367 of 382). An empty
    stem (after norm-v1) is REFUSED: it would make every empty text one twin group."""
    stem = _stem_of(value)
    if split_side.norm(stem) == "":
        _refuse("an empty stem (after %s) has no content key" % split_side.NORMALISER_VERSION)
    return split_side.stem_key(stem)


def _keys(ids, text_of):
    get = _getter(text_of, "text_of")
    out = {}
    for i in ids:
        try:
            out[i] = ck_key(get(i))
        except SystemExit as e:
            raise SystemExit("%s (id %r)" % (e, i))
    return out


def _families(ids, family_of):
    get = _getter(family_of, "family_of")
    out = {}
    for i in ids:
        f = get(i)
        if f is not None and f != "":
            out[i] = f
    return out


def closed_complement(gen_ids, reserved_ids, sentinel_ids, text_of, family_of=None):
    """Close the generation side toward the reserved side.

    A generation-side id whose key equals the key of a reserved id OR a routing-only sentinel becomes routing-only; with
    family_of, so does every generation-side id whose family holds a reserved id, a sentinel or an id already moved, and
    every generation-side id whose key equals a moved id's key; the rounds repeat to a fixed point. The reserved ids are
    never touched.

    Returns a dict: closed_gen (sorted tuple: the generation side after closure), moved ({id: reason}, in sorted id
    order), routing_only (sorted tuple: sentinels + moved), counts (dict)."""
    gen = frozenset(gen_ids)
    res = frozenset(reserved_ids)
    sen = frozenset(sentinel_ids)
    for a, b, an, bn in ((gen, res, "generation", "reserved"), (gen, sen, "generation", "sentinel"), (res, sen, "reserved", "sentinel")):
        both = a & b
        if both:
            _refuse("%d id(s) are on both the %s and the %s side (e.g. %r): a side assignment is not a closure input"
                    % (len(both), an, bn, _sorted(both)[:3]))
    key = _keys(_sorted(gen | res | sen), text_of)
    fam = _families(_sorted(gen | res | sen), family_of) if family_of is not None else {}
    k_res = {key[i] for i in res}
    k_sen = {key[i] for i in sen}
    f_res = {fam[i] for i in res if i in fam}
    f_sen = {fam[i] for i in sen if i in fam}
    moved = {}
    k_mov, f_mov = set(), set()
    rounds = 0
    gen_order = _sorted(gen)
    while True:
        rounds += 1
        new = {}
        for i in gen_order:
            if i in moved:
                continue
            k = key[i]; f = fam.get(i)
            if k in k_res:
                new[i] = TWIN_RESERVED
            elif k in k_sen:
                new[i] = TWIN_SENTINEL
            elif f is not None and f in f_res:
                new[i] = FAMILY_RESERVED
            elif f is not None and f in f_sen:
                new[i] = FAMILY_SENTINEL
            elif k in k_mov:
                new[i] = TWIN_MOVED
            elif f is not None and f in f_mov:
                new[i] = FAMILY_MOVED
        if not new:
            break
        moved.update(new)
        for i in new:
            k_mov.add(key[i])
            if i in fam:
                f_mov.add(fam[i])
    moved = {i: moved[i] for i in _sorted(moved)}
    closed = tuple(i for i in gen_order if i not in moved)
    by_reason = Counter(moved.values())
    counts = {
        "rule": RULE, "key": KEY_NAME,
        "n_gen": len(gen), "n_reserved": len(res), "n_sentinel": len(sen),
        "n_moved": len(moved), "n_closed_gen": len(closed), "n_routing_only": len(sen) + len(moved),
        "by_reason": {r: by_reason.get(r, 0) for r in REASONS},
        "reserved_keys": len(k_res), "sentinel_keys": len(k_sen),
        "families": bool(family_of is not None), "rounds": rounds,
    }
    return {"closed_gen": closed, "moved": moved, "routing_only": tuple(_sorted(sen | set(moved))), "counts": counts}


def build_closure(parts, text_of, family_of=None):
    """GLOBAL closure over the corpora of one build (condition 2): parts = {corpus: {"gen": ids, "reserved": ids,
    "sentinel": ids}}. Ids must be unique across corpora (a collision is refused). One closed_complement call over the
    union. The result adds per-corpus counts and two cross-corpus counts (review D6):
      cross_corpus_direct     a KEY-twin move (twin_of_reserved / twin_of_sentinel) none of whose key partners on the
                              held side sits in the id's own corpus;
      cross_corpus_component  any move whose connected component (ids linked by equal key or equal family, over the held
                              side and the moved ids) holds no held id of the id's own corpus: it includes CHAIN moves."""
    corpus_of = {}
    gen, res, sen = set(), set(), set()
    for corpus in sorted(parts):
        p = parts[corpus]
        unknown = set(p) - {"gen", "reserved", "sentinel"}
        if unknown:
            _refuse("part %s carries unknown field(s) %s" % (corpus, sorted(unknown)))
        for side, acc in (("gen", gen), ("reserved", res), ("sentinel", sen)):
            for i in p.get(side, ()):
                if i in corpus_of:
                    _refuse("id %r appears in corpus %s and in corpus %s: namespace the ids before a global closure"
                            % (i, corpus_of[i], corpus))
                corpus_of[i] = corpus
                acc.add(i)
    r = closed_complement(gen, res, sen, text_of, family_of)
    held = res | sen
    nodes = _sorted(set(r["moved"]) | held)
    key = _keys(nodes, text_of)
    fam = _families(nodes, family_of) if family_of is not None else {}
    holders = defaultdict(set)
    for i in held:
        holders[key[i]].add(corpus_of[i])
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in nodes:
        a = find(("k", key[i]))
        if i in fam:
            b = find(("f", fam[i]))
            if a != b:
                parent[b] = a
    comp_corpora = defaultdict(set)
    for i in held:
        comp_corpora[find(("k", key[i]))].add(corpus_of[i])
    by_corpus = defaultdict(Counter)
    direct, component = Counter(), Counter()
    for i, why in r["moved"].items():
        c = corpus_of[i]
        by_corpus[c][why] += 1
        if why in (TWIN_RESERVED, TWIN_SENTINEL) and c not in holders[key[i]]:
            direct[c] += 1
        if c not in comp_corpora[find(("k", key[i]))]:
            component[c] += 1
    r["corpus_of"] = corpus_of
    r["moved_by_corpus"] = {c: sum(by_corpus[c].values()) for c in sorted(parts)}
    r["moved_by_corpus_reason"] = {c: dict(by_corpus[c]) for c in sorted(parts)}
    r["cross_corpus_direct"] = {c: direct.get(c, 0) for c in sorted(parts)}
    r["cross_corpus_component"] = {c: component.get(c, 0) for c in sorted(parts)}
    return r


def assert_content_disjoint(train_ids, reserved_ids, sentinel_ids, text_of, family_of=None, where="", out=print):
    """REFUSE (ContentLeak, a SystemExit "[CK-CLOSE] ...", never an assert) a train side that shares an id, a key or
    (with family_of) a family with the reserved side OR the sentinel side. sentinel_ids is REQUIRED and SEPARATE (pass
    an explicit empty collection when a pool has none; None is refused), so a caller cannot drop the sentinel arm by
    merging sets (review D2). Prints its line on every run, pass or fail. Returns 0 on a pass.
    ContentLeak.counts: n_overlap, n_twins, n_twins_reserved, n_twins_sentinel_only, n_keys, n_family."""
    if sentinel_ids is None:
        _refuse("assert_content_disjoint: sentinel_ids is required (pass an explicit empty collection when there are none)")
    tr = frozenset(train_ids)
    res = frozenset(reserved_ids)
    sen = frozenset(sentinel_ids)
    held = res | sen
    tag = (" " + where) if where else ""
    both = tr & held
    if both:
        msg = "content-disjoint%s: REFUSED, %d id(s) are on both sides (e.g. %r)" % (tag, len(both), _sorted(both)[:3])
        out("[CK-CLOSE] " + msg)
        raise ContentLeak(msg, n_overlap=len(both), n_twins=0, n_twins_reserved=0, n_twins_sentinel_only=0, n_keys=0, n_family=0)
    key = _keys(_sorted(tr | held), text_of)
    res_keys = {key[i] for i in res}
    sen_keys = {key[i] for i in sen}
    tw_res = [i for i in _sorted(tr) if key[i] in res_keys]
    tw_sen = [i for i in _sorted(tr) if key[i] in sen_keys and key[i] not in res_keys]
    twins = _sorted(tw_res + tw_sen)
    n_fam = 0
    if family_of is not None:
        fam = _families(_sorted(tr | held), family_of)
        held_fams = {fam[i] for i in held if i in fam}
        n_fam = sum(1 for i in tr if fam.get(i) in held_fams)
    if twins or n_fam:
        msg = ("content-disjoint%s: REFUSED, %d train id(s) over %d key(s) are content twins of held ids (%d of reserved,"
               " %d of sentinels only; e.g. %r); %d train id(s) share a family with them; apply closed_complement first"
               % (tag, len(twins), len({key[i] for i in twins}), len(tw_res), len(tw_sen), twins[:3], n_fam))
        out("[CK-CLOSE] " + msg)
        raise ContentLeak(msg, n_overlap=0, n_twins=len(twins), n_twins_reserved=len(tw_res), n_twins_sentinel_only=len(tw_sen),
                          n_keys=len({key[i] for i in twins}), n_family=n_fam)
    out("[CK-CLOSE] content-disjoint%s: PASS, %d train / %d reserved / %d sentinel ids; 0 twins under %s; 0 shared families%s"
        % (tag, len(tr), len(res), len(sen), KEY_NAME, "" if family_of is not None else " (no families given)"))
    return 0


def _kish(sizes):
    n = sum(sizes)
    if n == 0:
        return {"n": 0, "n_clusters": 0, "n_in_twin_groups": 0, "twin_groups": 0, "excess": 0, "max_cluster": 0,
                "kish": float("nan"), "n_eff_rho1": float("nan")}
    k = sum(s * s for s in sizes) / n
    return {"n": n, "n_clusters": len(sizes), "n_in_twin_groups": sum(s for s in sizes if s > 1),
            "twin_groups": sum(1 for s in sizes if s > 1), "excess": sum(s - 1 for s in sizes if s > 1),
            "max_cluster": max(sizes), "kish": k, "n_eff_rho1": n / k}


def reserved_clusters(reserved_ids, text_of, family_of=None):
    """A cluster id for EVERY reserved id (twins are clustered, never dropped): the stem_key of its group; with family_of,
    the connected component of key-equality and family-equality (cluster id = the smallest key in it). Returns
    (cluster_of in sorted id order, stats); stats["by_key"] always, stats["combined"] and stats["by_family"] with
    families. "kish" = sum(n^2)/n is DEFF at rho = 1, an UPPER bound (review D7): the design effect lies in [1, kish],
    n_eff in [n / kish, n]."""
    ids = _sorted(dict.fromkeys(reserved_ids))
    key = _keys(ids, text_of)
    by_key = Counter(key[i] for i in ids)
    stats = {"by_key": _kish(list(by_key.values())), "bound": "DEFF at rho = 1 (upper bound), not a measured DEFF"}
    if family_of is None:
        return {i: key[i] for i in ids}, stats
    fam = _families(ids, family_of)
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)
    for i in ids:
        find(("k", key[i]))
        if i in fam:
            union(("k", key[i]), ("f", fam[i]))
    comp_min_key = {}
    for i in ids:
        r = find(("k", key[i]))
        if r not in comp_min_key or key[i] < comp_min_key[r]:
            comp_min_key[r] = key[i]
    cluster_of = {i: comp_min_key[find(("k", key[i]))] for i in ids}
    stats["combined"] = _kish(list(Counter(cluster_of.values()).values()))
    stats["by_family"] = _kish(list(Counter(fam.get(i, "\x00id:%r" % (i,)) for i in ids).values()))
    return cluster_of, stats


_LATEX_FRAC = re.compile(r"\\[dt]frac")
_LATEX_NOISE = re.compile(r"\\left|\\right|\\displaystyle|\\[!,;: ]|\$")
_NON_ALNUM = re.compile(r"[^0-9a-z]")


def _alnum(s):
    return _NON_ALNUM.sub("", s)


def _latex_plain(s):
    return _alnum(_LATEX_NOISE.sub("", _LATEX_FRAC.sub(r"\\frac", s)))


def label_conflicts(ids, text_of, target_of):
    """Answer-TEXT differences within a stem_key group, CLASSIFIED (review D1: these counts are an upper bound on label
    conflicts, never label conflicts as such). Every group of two or more ids whose normalised (norm-v1) answer texts
    differ gets exactly one class, tested in this order:
      punctuation_only    equal once every non-alphanumeric character is dropped (a trailing period, a comma);
      formatting_only     equal once LaTeX formatting is normalised (\\dfrac / \\tfrac -> \\frac, \\left / \\right /
                          spacing / $ dropped), then non-alphanumerics dropped;
      conflict            an IDENTICAL prompt (same stem key and the same normalised option SET, including both empty):
                          a real label conflict, FLAGGED, never resolved here;
      option_sets_differ  otherwise: the members carry different option sets, so the answer text may differ by design.
    For multiple choice the caller passes the ANSWER TEXT, not the letter (shuffled options move the letter); the options
    are read from a (stem, options) text value. A None target is skipped. Returns a list of {"key", "ids", "targets",
    "class"} sorted by key; label_classes() counts them."""
    ids = _sorted(dict.fromkeys(ids))
    get = _getter(text_of, "text_of")
    val = {i: get(i) for i in ids}
    key = {i: ck_key(val[i]) for i in ids}
    tget = _getter(target_of, "target_of")
    groups = defaultdict(list)
    for i in ids:
        groups[key[i]].append(i)
    out = []
    for k in sorted(groups):
        g = groups[k]
        if len(g) < 2:
            continue
        tg = {}
        for i in g:
            t = tget(i)
            if t is None:
                continue
            tg[i] = split_side.norm(t if isinstance(t, str) else json.dumps(t, sort_keys=True))
        if len(set(tg.values())) <= 1:
            continue
        members = _sorted(tg)
        if len({_alnum(tg[i]) for i in members}) == 1:
            cls = PUNCTUATION_ONLY
        elif len({_latex_plain(tg[i]) for i in members}) == 1:
            cls = FORMATTING_ONLY
        elif len({tuple(sorted((split_side.norm(o) for o in _options_of(val[i])), key=lambda s: s.encode("utf-8"))) for i in members}) == 1:
            cls = CONFLICT
        else:
            cls = OPTION_SETS_DIFFER
        out.append({"key": k, "ids": _sorted(g), "targets": sorted(set(tg.values())), "class": cls})
    return out


def label_classes(groups):
    c = Counter(g["class"] for g in groups)
    return {k: c.get(k, 0) for k in ANSWER_CLASSES}


def one_row_per_key(ids, text_of, tag_of, prefer=None):
    """Collapse copies to ONE ROW PER STEM_KEY with subset tags (the queue item's "GPQA one row per stem_key"; GPQA ships
    nested subsets diamond within main within extended, so one question appears up to three times, often with its options
    shuffled). Returns {key: {"row": representative id, "ids": sorted ids, "tags": sorted tags}} in key order. The
    representative is the first id under `prefer` (a sort key over ids; default: the natural id order). This is an
    INGESTION tool for a NEW pool: applied to a pinned pool it would change the id list and therefore the pool id, so
    this module never applies it to one (the audit prints the collapse descriptively)."""
    ids = _sorted(dict.fromkeys(ids))
    key = _keys(ids, text_of)
    tget = _getter(tag_of, "tag_of")
    groups = defaultdict(list)
    for i in ids:
        groups[key[i]].append(i)
    out = {}
    for k in sorted(groups):
        g = groups[k]
        order = sorted(g, key=prefer) if prefer is not None else g
        tags = set()
        for i in g:
            t = tget(i)
            if t is None or t == "":
                _refuse("one_row_per_key: id %r has no subset tag" % (i,))
            tags.add(t)
        out[k] = {"row": order[0], "ids": list(g), "tags": sorted(tags)}
    return out


# ── the audit of a pool of record (read-only) ───────────────────────────────────────────────

# Agent pools are not in experiment_configs/reserved_pools.json (the registry is not edited here); their id files and
# DBs are named once, and the audit re-hashes the id file to the pool id before use.
AGENT_POOLS = {
    "p2035adddedd1becb": {"corpus": "BFCL", "db": "experiment_results/agent/bfcl_result_2025-12-16.db",
                          "id_file": "experiment_configs/reserved_pool_frozen_bfcl_p2035adddedd1becb.json"},
    "p79fb71114b5c67c2": {"corpus": "MULTISWE", "db": "experiment_results/agent/multiswe_result_2026-09-22.db",
                          "id_file": "experiment_configs/reserved_pool_frozen_multiswe_p79fb71114b5c67c2.json"},
}
NG20_POOL = "pf844849e133cda4e"
NG20_DB = "twenty_newsgroups_cache_v1.db"
EXIT_NOT_IMPLEMENTED = 4

# The reviewed figures (review 1df2cf1; READY review e9fe11c; programme L14280-L14340) printed beside the computed ones.
# Never tuned.
RECORD = {
    "paeec37aa28063c75": {"moved": 543, "moved_GPQA": 346, "moved_MMLU_PRO": 185, "moved_MATH": 10, "moved_BBH": 2,
                          "cross_direct": 13, "res_with_gen_twin": 478, "res_twin_keys": 432,
                          "within_res_in_twin_groups": 215, "kish_all": "1.0367", "kish_GPQA": "1.380",
                          "answer_conflict": 2, "answer_formatting_only": 4, "answer_punctuation_only": 7,
                          "answer_option_sets_differ": 76, "overclosure_no_shared_option": 54, "overclosure_short_stem": 21},
    "p2dca21ab5f4ef3ae": {"moved": 171, "moved_twin_of_reserved": 75, "moved_twin_of_sentinel": 96, "test": 3770,
                          "train": 8230, "gate": 843, "train_excl_gate": 7387, "res_with_gen_twin": 70,
                          "sentinel_leg": 96, "answer_conflict": 0, "answer_formatting_only": 0, "answer_punctuation_only": 7,
                          "answer_option_sets_differ": 77},
    "p2035adddedd1becb": {"moved": 0, "kish_family": "4.000", "kish_key": "3.377"},
    "p79fb71114b5c67c2": {"moved": 0, "kish_family": "37.76"},
}


def _pg():
    return _load_sibling("pool_guard")


def _check(record, name, got, out):
    exp = record.get(name)
    if exp is None:
        return True
    if isinstance(exp, str):
        places = len(exp.split(".")[1]) if "." in exp else 0
        g = "%.*f" % (places, got)
        ok = (g == exp)
    else:
        g = got; ok = (got == exp)
    out("    record %-30s %-8s computed %-8s %s" % (name, exp, g, "MATCH" if ok else "MISMATCH"))
    return bool(ok)


def _letter_answer(target, options):
    """The answer TEXT behind a letter target ('C' or '(C)') when options exist; else the target itself."""
    if target is None:
        return None
    t = target.strip()
    L = "ABCDEFGHIJKLMNOP"
    if options:
        if len(t) == 1 and t in L and L.index(t) < len(options):
            return options[L.index(t)]
        if len(t) == 3 and t[0] == "(" and t[2] == ")" and t[1] in L and L.index(t[1]) < len(options):
            return options[L.index(t[1])]
    return t


def _load_paeec(pg, pool):
    pg.assert_pool_of_record(pool)
    reserved = set(pg.eval_ids(pool))
    sentinels = {q for v in pg.pool_file_ids(pool).values() for q in v if q <= 0}
    conn = pg.open_ro(pg.db_path(pool))
    try:
        rows = conn.execute("SELECT question_id, source, task, text, options_json, target FROM corpus_questions").fetchall()
    finally:
        conn.close()
    text, target, src, task = {}, {}, {}, {}
    for q, s, tk, t, oj, tg in rows:
        opts = json.loads(oj) if oj else []
        opts = [o if isinstance(o, str) else json.dumps(o, sort_keys=True) for o in opts]
        text[q] = (t, opts); src[q] = s; task[q] = tk; target[q] = _letter_answer(tg, opts)
    missing = (reserved | sentinels) - set(text)
    if missing:
        _refuse("%d pool ids of %s are not in corpus_questions" % (len(missing), pool))
    parts = defaultdict(lambda: {"gen": set(), "reserved": set(), "sentinel": set()})
    for q in text:
        side = "reserved" if q in reserved else "sentinel" if q in sentinels else "gen"
        parts[src[q]][side].add(q)
    return dict(parts), text, None, target, "corpus_questions (%d rows)" % len(rows), {"source": src, "task": task}


def _load_p2dca(pg, pool):
    pg.assert_pool_of_record(pool)
    listed = {q for v in pg.pool_file_ids(pool).values() for q in v}
    reserved = {q for q in listed if q > 0}
    sentinels = listed - reserved
    conn = pg.open_ro(pg.db_path(pool))
    try:
        rows = conn.execute("SELECT m.id, m.question, m.options, m.answer, l.question_id FROM mmlu_pro m"
                            " LEFT JOIN eval_question_link l ON m.id = l.mmlu_pro_row_id ORDER BY m.id ASC").fetchall()
    finally:
        conn.close()
    # MMLUDatasetFetcher.loadFromDb L493-L556: a linked row carries its eval question_id, an unlinked one the sentinel
    # UNLINKED_QUERY_ID_BASE - rowid = -1,000,000 - rowid. Keyed by id, last row wins (the review's universe of 12,000).
    text, target = {}, {}
    for mid, t, oj, ans, lq in rows:
        q = lq if (lq is not None and lq > 0) else -1000000 - mid
        opts = json.loads(oj) if oj else []
        text[q] = (t, opts); target[q] = _letter_answer(ans, opts)
    missing = listed - set(text)
    if missing:
        _refuse("%d listed ids of %s are not in the mmlu_pro universe" % (len(missing), pool))
    part = {"gen": set(text) - listed, "reserved": reserved, "sentinel": sentinels}
    return ({"MMLU_PRO": part}, text, None, target,
            "mmlu_pro LEFT JOIN eval_question_link (%d join rows, %d ids)" % (len(rows), len(text)), {})


def _agent_ids(pg, pool):
    e = AGENT_POOLS[pool]
    with open(os.path.join(pg.ROOT, e["id_file"]), "r", encoding="utf-8") as f:
        ids = json.load(f)
    got = pg.compute_pool_id(pg.judgeable(ids))
    if got != pool:
        _refuse("%s hashes to %s, not %s" % (e["id_file"], got, pool))
    return e, ids


def _load_bfcl(pg, pool):
    e, ids = _agent_ids(pg, pool)
    conn = pg.open_ro(os.path.join(pg.DATA_ROOT, e["db"]))
    try:
        rows = conn.execute("SELECT task_id, family_id, stem FROM tasks").fetchall()
    finally:
        conn.close()
    text = {t: s for t, _f, s in rows}
    fam = {t: f for t, f, _s in rows}
    reserved = {"multi_turn_%s_%d" % (k.split("/", 1)[1], i) for k, v in ids.items() for i in v if i > 0}
    if reserved - set(text):
        _refuse("%d BFCL pool ids do not resolve to tasks" % len(reserved - set(text)))
    return ({"BFCL": {"gen": set(text) - reserved, "reserved": reserved, "sentinel": set()}}, text, fam, None,
            "tasks (%d rows; text = stem; family = base-scenario index)" % len(rows), {})


def _load_multiswe(pg, pool):
    e, ids = _agent_ids(pg, pool)
    conn = pg.open_ro(os.path.join(pg.DATA_ROOT, e["db"]))
    try:
        rows = conn.execute("SELECT instance_id, language, org, repo, pr, family_id FROM tasks").fetchall()
    finally:
        conn.close()
    by = {("MULTISWE/%s/%s__%s" % (lang, org, repo), pr): i for i, lang, org, repo, pr, _f in rows}
    reserved = set()
    for k, v in ids.items():
        for p in v:
            if (k, p) not in by:
                _refuse("Multi-SWE pool entry %s:%d does not resolve to a task" % (k, p))
            reserved.add(by[(k, p)])
    # No content key exists for Multi-SWE (review D4): the DB's key rule is stem_key over the instance id. The text used
    # here is therefore the instance id, and the guarantee is the org/repo family closure.
    text = {i: i for i, *_r in rows}
    fam = {i: f for i, _l, _o, _r, _p, f in rows}
    return ({"MULTISWE": {"gen": set(text) - reserved, "reserved": reserved, "sentinel": set()}}, text, fam, None,
            "tasks (%d rows; text = instance id, NO content key; family = org/repo)" % len(rows), {})


def _audit_loaded(pool, parts, text, fam, target, record, out, extra=None):
    """The audit body over loaded data (the selftest runs it on a synthetic pool). Returns True when every recorded
    figure matches and every leg behaves as the rule requires."""
    extra = extra or {}
    r = build_closure(parts, text, fam)
    c = r["counts"]
    ok = True
    out("  closure: gen %d, reserved %d, sentinel %d -> moved %d (%s); closed gen %d; routing-only %d; rounds %d"
        % (c["n_gen"], c["n_reserved"], c["n_sentinel"], c["n_moved"],
           ", ".join("%s %d" % (k, v) for k, v in c["by_reason"].items() if v) or "none", c["n_closed_gen"], c["n_routing_only"], c["rounds"]))
    out("  moved by corpus: %s" % ", ".join("%s %d" % kv for kv in r["moved_by_corpus"].items()))
    out("  cross-corpus moves: direct (key twin, no partner in its own corpus) %d [%s]; by component (includes chain moves) %d [%s]"
        % (sum(r["cross_corpus_direct"].values()), ", ".join("%s %d" % kv for kv in r["cross_corpus_direct"].items()),
           sum(r["cross_corpus_component"].values()), ", ".join("%s %d" % kv for kv in r["cross_corpus_component"].items())))
    ok &= _check(record, "moved", c["n_moved"], out)
    for reason, n in c["by_reason"].items():
        ok &= _check(record, "moved_" + reason, n, out)
    for corpus, n in r["moved_by_corpus"].items():
        ok &= _check(record, "moved_" + corpus, n, out)
    ok &= _check(record, "cross_direct", sum(r["cross_corpus_direct"].values()), out)
    ok &= _check(record, "cross_component", sum(r["cross_corpus_component"].values()), out)
    reserved = set().union(*(p["reserved"] for p in parts.values()))
    sentinels = set().union(*(p["sentinel"] for p in parts.values()))
    gen = set().union(*(p["gen"] for p in parts.values()))
    test = reserved | sentinels | set(r["moved"])
    train = set(r["closed_gen"])
    gate = sum(1 for q in train if split_side.GATE_LOWER <= split_side.side_hash(ck_key(text[q])) < split_side.GATE_UPPER)
    out("  sides after closure: test %d (reserved %d + sentinel %d + moved %d) / train %d (gate %d, excl. gate %d)"
        " [gate = split_side.side_hash(stem_key) in [%d, %d), as finishSplit; family ids are not used for it here]"
        % (len(test), len(reserved), len(sentinels), len(r["moved"]), len(train), gate, len(train) - gate,
           split_side.GATE_LOWER, split_side.GATE_UPPER))
    ok &= _check(record, "test", len(test), out)
    ok &= _check(record, "train", len(train), out)
    ok &= _check(record, "gate", gate, out)
    ok &= _check(record, "train_excl_gate", len(train) - gate, out)
    if "scored_unchanged" in extra:
        same = bool(extra["scored_unchanged"](reserved))
        out("  scored set unchanged (%d ids) and pool id unchanged: %s" % (len(reserved), same))
        ok &= same
    # (1) the guard on the closed split must pass
    try:
        assert_content_disjoint(train, reserved, sentinels, text, fam, where="%s after closure" % pool, out=out)
    except ContentLeak:
        ok = False
    # (2) the guard on the unclosed split must refuse exactly when something moved
    try:
        assert_content_disjoint(gen, reserved, sentinels, text, fam, where="%s WITHOUT closure (must refuse when moved > 0)" % pool, out=out)
        unclosed = None
    except ContentLeak as e:
        unclosed = e.counts
    out("  the guard on the unclosed split: %s (moved = %d)" % ("REFUSED" if unclosed is not None else "passed", c["n_moved"]))
    ok &= (bool(unclosed is not None) == bool(c["n_moved"] > 0))
    # (3) the SENTINEL leg (review D2): remove only the reserved twins; the guard must still refuse, with exactly the
    # sentinel-only twins; a guard (or a call) that leaves the sentinels out passes here and fails the audit
    n_ts = c["by_reason"][TWIN_SENTINEL]
    if sentinels and n_ts:
        leg_train = gen - {i for i, why in r["moved"].items() if why == TWIN_RESERVED}
        try:
            assert_content_disjoint(leg_train, reserved, sentinels, text, fam,
                                    where="%s SENTINEL LEG (reserved twins removed; must refuse with the sentinel twins)" % pool, out=out)
            leg = None
        except ContentLeak as e:
            leg = e.counts
        got = leg["n_twins_sentinel_only"] if leg is not None else 0
        leg_ok = bool(leg is not None and leg["n_twins_reserved"] == 0 and got == n_ts)
        out("  sentinel leg: %s with %d sentinel-only twin(s); expected %d (the twin_of_sentinel moves): %s"
            % ("REFUSED" if leg is not None else "PASSED (WRONG)", got, n_ts, "OK" if leg_ok else "FAILED"))
        ok &= leg_ok
        ok &= _check(record, "sentinel_leg", got, out)
    else:
        out("  sentinel leg: not applicable (%d sentinels, %d sentinel-only twins)" % (len(sentinels), n_ts))
        ok &= _check(record, "sentinel_leg", 0, out)
    # cross-side twins, reserved view
    key = _keys(_sorted(gen | reserved | sentinels), text)
    gk = {key[q] for q in gen}
    rt = [q for q in reserved if key[q] in gk]
    out("  reserved ids with a generation-side twin (before closure): %d over %d keys" % (len(rt), len({key[q] for q in rt})))
    ok &= _check(record, "res_with_gen_twin", len(rt), out)
    ok &= _check(record, "res_twin_keys", len({key[q] for q in rt}), out)
    # over-closure by generic stems (review D10: a property of the adopted rule, descriptive)
    held_by = defaultdict(list)
    for q in reserved | sentinels:
        held_by[key[q]].append(q)
    optn = lambda q: {split_side.norm(o) for o in _options_of(text[q])}
    oc = [q for q in r["moved"] if _options_of(text[q]) and held_by[key[q]]
          and all(_options_of(text[h]) for h in held_by[key[q]]) and all(not (optn(q) & optn(h)) for h in held_by[key[q]])]
    short = sum(1 for q in oc if len(_stem_of(text[q])) < 80)
    out("  over-closure (descriptive; the rule's generic-stem property): %d moved ids share NO option with any held twin"
        " (both sides option-bearing); %d of them with a stem under 80 characters" % (len(oc), short))
    ok &= _check(record, "overclosure_no_shared_option", len(oc), out)
    ok &= _check(record, "overclosure_short_stem", short, out)
    # clusters within the reserved side
    cl, st = reserved_clusters(reserved, text, fam)
    b = st["by_key"]
    out("  reserved clusters by key: n %d, clusters %d, ids in twin groups %d (%d groups, excess %d), max %d; Kish sum(n^2)/n"
        " %.4f -> n_eff(rho=1) %.1f [%s]" % (b["n"], b["n_clusters"], b["n_in_twin_groups"], b["twin_groups"], b["excess"],
                                            b["max_cluster"], b["kish"], b["n_eff_rho1"], st["bound"]))
    ok &= bool(len(cl) == len(reserved))
    ok &= _check(record, "within_res_in_twin_groups", b["n_in_twin_groups"], out)
    ok &= _check(record, "kish_all", b["kish"], out)
    ok &= _check(record, "kish_key", b["kish"], out)
    if fam is not None:
        f = st["by_family"]; cb = st["combined"]
        out("  reserved clusters by family: n %d, families %d, Kish %.4f -> n_eff(rho=1) %.1f; key+family components %d, Kish %.4f"
            % (f["n"], f["n_clusters"], f["kish"], f["n_eff_rho1"], cb["n_clusters"], cb["kish"]))
        ok &= _check(record, "kish_family", f["kish"], out)
        fams_split = defaultdict(set)
        for q in gen | reserved | sentinels:
            if q in fam:
                fams_split[fam[q]].add("R" if q in reserved | sentinels else "G")
        out("  families spanning sides (before closure): %d of %d" % (sum(1 for s in fams_split.values() if len(s) > 1), len(fams_split)))
    for corpus in sorted(parts):
        rc = parts[corpus]["reserved"]
        if not rc or len(parts) == 1:
            continue
        _, s = reserved_clusters(rc, text)
        out("    %-10s reserved %5d clusters %5d ids in twin groups %4d Kish %.4f n_eff(rho=1) %.1f"
            % (corpus, s["by_key"]["n"], s["by_key"]["n_clusters"], s["by_key"]["n_in_twin_groups"], s["by_key"]["kish"], s["by_key"]["n_eff_rho1"]))
        ok &= _check(record, "kish_" + corpus, s["by_key"]["kish"], out)
    if target is not None:
        lc = label_conflicts(_sorted(gen | reserved | sentinels), text, target)
        cls = label_classes(lc)
        span = sum(1 for g in lc if any(q in reserved | sentinels for q in g["ids"]) and any(q in gen for q in g["ids"]))
        out("  answer-text differences within a stem_key group (an UPPER BOUND on label conflicts, never conflicts as such):"
            " %d groups over %d ids, %d spanning the sides" % (len(lc), sum(len(g["ids"]) for g in lc), span))
        out("    classes: conflict (identical prompt, different answer) %d; formatting-only %d; punctuation-only %d;"
            " option sets differ %d" % (cls[CONFLICT], cls[FORMATTING_ONLY], cls[PUNCTUATION_ONLY], cls[OPTION_SETS_DIFFER]))
        for g in lc:
            if g["class"] == CONFLICT:
                out("    CONFLICT (flagged, not resolved): ids %s answers %s" % (g["ids"], g["targets"]))
        for k_ in ANSWER_CLASSES:
            ok &= _check(record, "answer_" + k_, cls[k_], out)
    else:
        out("  answer-text differences: not computed (no target column in this corpus's task table)")
    if "task" in extra and "source" in extra:
        g = [q for q in text if extra["source"].get(q) == "GPQA"]
        if g:
            rows1 = one_row_per_key(g, text, extra["task"])
            prof = Counter(tuple(v["tags"]) for v in rows1.values())
            out("  GPQA one row per stem_key (descriptive; an ingestion tool, not applied to the pinned pool): %d rows -> %d"
                " stem keys; tag profiles %s" % (len(g), len(rows1), ", ".join("%s %d" % ("+".join(k_), v) for k_, v in sorted(prof.items()))))
    return bool(ok)


def audit(pool, out=print):
    """Print the content check of a pool of record, read-only. Returns 0 when every recorded figure matches, 1 on any
    mismatch or guard refusal, 4 (NOT IMPLEMENTED) for the 20NG pool."""
    out("pool %s" % pool)
    if pool == NG20_POOL:
        pg = _pg()
        db = os.path.join(pg.DATA_ROOT, NG20_DB)
        state = ", ".join("%s %s" % (s, ("%d bytes" % os.path.getsize(db + s)) if os.path.exists(db + s) else "absent")
                          for s in ("-wal", "-journal"))
        out("[CK-CLOSE] audit %s: NOT IMPLEMENTED (no loader for the 20NG DB; it was never opened to verify one). The DB is"
            " not opened; sidecars: %s. Its cross-side zero holds by ingest rule (3) (review D5)." % (pool, state))
        return EXIT_NOT_IMPLEMENTED
    pg = _pg()
    if pool in AGENT_POOLS:
        loader = _load_bfcl if AGENT_POOLS[pool]["corpus"] == "BFCL" else _load_multiswe
    elif pool == pg.UNION_POOL:
        loader = _load_paeec
    elif pool == pg.MMLU_PRO_POOL:
        loader = _load_p2dca
    else:
        _refuse("no audit loader for pool %s (known: %s)" % (pool, ", ".join(sorted([pg.MMLU_PRO_POOL, pg.UNION_POOL, NG20_POOL] + list(AGENT_POOLS)))))
    parts, text, fam, target, universe, extra = loader(pg, pool)
    if pool in (pg.UNION_POOL, pg.MMLU_PRO_POOL):
        extra["scored_unchanged"] = lambda res: (pg.compute_pool_id(pg.judgeable(pg.pool_file_ids(pool))) == pool
                                                 and set(res) == set(pg.eval_ids(pool)))
    out("[CK-CLOSE] %s; key %s; universe %s; families %s" % (RULE, KEY_NAME, universe, "yes" if fam is not None else "none"))
    ok = _audit_loaded(pool, parts, text, fam, target, RECORD.get(pool, {}), out, extra)
    out("[CK-CLOSE] audit %s: %s" % (pool, "every recorded figure MATCHES" if ok else "MISMATCH against the record (reported, not tuned)"))
    return 0 if ok else 1


# ── selftest (synthetic; opens no DB) ───────────────────────────────────────────────────────

def selftest(out=print):
    results = []

    def check(cond, label):
        results.append((bool(cond), label))
        out("  [%s] %s" % ("PASS" if cond else "FAIL", label))

    def refuses(fn):
        try:
            fn()
        except SystemExit as e:
            return str(e).startswith("[CK-CLOSE] ")
        return False

    def leak_counts(fn):
        try:
            fn()
        except ContentLeak as e:
            return e.counts
        return None

    quiet = lambda *_a, **_k: None
    out("content_closure selftest (%s; key %s); python -O: %s" % (RULE, KEY_NAME, not __debug__))
    T = {
        # reserved side
        "r1": "What is the capital of France?",
        "r2": ("Which particle mediates the strong force?", ["photon", "gluon", "W boson", "graviton"]),
        "r3": "Compute 17 * 23.",
        "r4": "compute   17 * 23.",                         # norm-v1 twin of r3, both RESERVED
        "m1": "Solve x^2 = 4 for positive x.",                # a MATH reserved id
        # sentinels (routing-only, never scored)
        "s1": "Name the largest planet in the solar system.",
        # generation side
        "g1": "what is the capital of   FRANCE?",             # twin of r1 (reserved)
        "g2": "Name the largest planet in the solar system.", # twin of sentinel s1 (condition 1)
        "g3": ("Which particle mediates the strong force?", ["gluon", "graviton", "photon", "W boson"]),  # GPQA shuffle
        "g4": "An unrelated generation question.",
        "g5": ("Which particle mediates the strong force?", ["pion", "gluon", "electron", "neutrino"]),  # stem-only variant
        "p1": "SOLVE x^2 = 4 for positive x.",                # MMLU-Pro GEN twin of a MATH reserved id (condition 2)
        "f1": "Scenario 7, base dialogue.",                   # family member of a reserved family
        "f2": "Scenario 8, augmented dialogue, missing tool.",# another family (F8): stays
        "f3": "Scenario 7, base dialogue.",                   # key twin of f1 only (TWIN_MOVED round)
        "fr": "Scenario 7, long-context variant.",            # RESERVED member of family F7
    }
    F = {"f1": "F7", "fr": "F7", "f2": "F8", "f3": None, "g4": None}
    tgt = {"r1": "Paris", "g1": "Lyon", "r3": "391", "r4": "391", "r2": "gluon", "g3": "gluon"}

    # (1) a GEN twin of a reserved id moves; (3) a cross-corpus twin moves; (5) the GPQA-style shuffled twin moves
    parts = {"GPQA": {"gen": {"g3", "g5"}, "reserved": {"r2"}, "sentinel": set()},
             "MMLU_PRO": {"gen": {"g1", "g2", "g4", "p1"}, "reserved": {"r1", "r3", "r4"}, "sentinel": {"s1"}},
             "MATH": {"gen": set(), "reserved": {"m1"}, "sentinel": set()}}
    r = build_closure(parts, T)
    mv = r["moved"]
    check(mv.get("g1") == TWIN_RESERVED, "a generation twin of a RESERVED id moves (g1, reason %s)" % mv.get("g1"))
    check(mv.get("g2") == TWIN_SENTINEL, "a generation twin of a SENTINEL moves (condition 1; g2, reason %s)" % mv.get("g2"))
    check(mv.get("p1") == TWIN_RESERVED and r["cross_corpus_direct"]["MMLU_PRO"] == 1,
          "a CROSS-CORPUS twin moves (condition 2; MMLU-Pro p1 of MATH m1; direct cross-corpus moves %s)" % r["cross_corpus_direct"])
    check(mv.get("g3") == TWIN_RESERVED, "an options-SHUFFLED twin (GPQA-style) is caught by the stem key (g3; an ORDERED options key misses it)")
    check(mv.get("g5") == TWIN_RESERVED, "a stem-only variant (same stem, another option set; MMLU-Pro-style) moves (g5; a SORTED options key misses it)")
    check("g4" in r["closed_gen"] and "g4" not in mv, "an unrelated generation id stays on the generation side (g4)")
    check(r["counts"]["n_moved"] == 5 and r["counts"]["n_closed_gen"] == 1 and r["routing_only"] == ("g1", "g2", "g3", "g5", "p1", "s1"),
          "counts: moved 5, closed gen 1, routing-only = sentinels + moved, SORTED (%s)" % (r["routing_only"],))
    check(set().union(*(p["reserved"] for p in parts.values())) == {"r1", "r2", "r3", "r4", "m1"} and not (set(mv) & {"r1", "r2", "r3", "r4", "m1"}),
          "the reserved (scored) set is untouched by the closure")
    per = set()
    for c_, p in parts.items():
        per |= set(closed_complement(p["gen"], p["reserved"], p["sentinel"], T)["moved"])
    check("p1" not in per and "p1" in mv, "control: a per-corpus closure would have missed p1 (the global one moves it)")
    ro = closed_complement([5, -3, 12, "b", "a"], [100], [], {5: "x", -3: "y", 12: "z", "b": "w", "a": "v", 100: "q"})
    check(ro["closed_gen"] == (-3, 5, 12, "a", "b"), "outputs are SORTED over mixed id types (%s)" % (ro["closed_gen"],))

    # (4) family closure, iterated to a fixed point
    fr = closed_complement({"f1", "f2", "f3", "g4"}, {"fr"}, set(), T, family_of=F)
    check(fr["moved"].get("f1") == FAMILY_RESERVED, "FAMILY closure: f1 shares reserved fr's family F7 and moves (%s)" % fr["moved"].get("f1"))
    check(fr["moved"].get("f3") == TWIN_MOVED, "fixed point, family -> key: f3, a key twin of the family-moved f1, moves (%s)" % fr["moved"].get("f3"))
    check("f2" not in fr["moved"] and "g4" not in fr["moved"] and fr["counts"]["rounds"] >= 2,
          "a different family (F8) and an unrelated id stay; rounds %d" % fr["counts"]["rounds"])
    nofam = closed_complement({"f1", "f2", "f3", "g4"}, {"fr"}, set(), T, family_of=None)
    check(not nofam["moved"], "control: without family_of nothing in that family moves (the stems differ)")
    # (4b) the KEY -> FAMILY chain (READY C1 / D3): r -> c1 (key twin, family FA) -> c2 (family FA) -> c3 (key twin of c2)
    # -> c4 (family FB of c3)
    CT = {"cr": "Chain root question.", "c1": "chain ROOT question.", "c2": "Chain second stem.", "c3": "chain second stem.",
          "c4": "Chain fourth stem.", "c5": "Chain unrelated stem."}
    CF = {"cr": None, "c1": "FA", "c2": "FA", "c3": "FB", "c4": "FB", "c5": "FC"}
    ch = closed_complement({"c1", "c2", "c3", "c4", "c5"}, {"cr"}, set(), CT, family_of=CF)
    want = {"c1": TWIN_RESERVED, "c2": FAMILY_MOVED, "c3": TWIN_MOVED, "c4": FAMILY_MOVED}
    check(ch["moved"] == want and "c5" in ch["closed_gen"],
          "fixed point, key -> family chain: c1 twin_of_reserved, c2 family_of_moved, c3 twin_of_moved, c4 family_of_moved; c5 stays (%s)"
          % (ch["moved"],))

    # cross-corpus chains are counted by component, not only direct (D6)
    XT = {"xa": "Cross stem X.", "xb1": "cross stem x.", "xb2": "Other stem in family FB.", "xc": "other stem in family fb."}
    XF = {"xa": None, "xb1": "FB", "xb2": "FB", "xc": None}
    xr = build_closure({"A": {"reserved": {"xa"}}, "B": {"gen": {"xb1", "xb2"}}, "C": {"gen": {"xc"}}}, XT, XF)
    check(sorted(xr["moved"]) == ["xb1", "xb2", "xc"] and xr["cross_corpus_direct"] == {"A": 0, "B": 1, "C": 0}
          and xr["cross_corpus_component"] == {"A": 0, "B": 2, "C": 1},
          "cross-corpus: direct counts key twins only (B 1), by component includes the chain (B 2, C 1): %s / %s"
          % (xr["cross_corpus_direct"], xr["cross_corpus_component"]))

    # (6) reserved twins are clustered, never dropped
    cl, st = reserved_clusters(["r1", "r2", "r3", "r4", "m1"], T)
    check(set(cl) == {"r1", "r2", "r3", "r4", "m1"} and st["by_key"]["n"] == 5,
          "every reserved id keeps a cluster id (n = %d, none dropped)" % st["by_key"]["n"])
    check(cl.get("r3") is not None and cl.get("r3") == cl.get("r4") and len(set(cl.values())) == 4 and st["by_key"]["n_in_twin_groups"] == 2,
          "the reserved twins r3 / r4 share ONE cluster (4 clusters over 5 ids)")
    check(abs(st["by_key"]["kish"] - (4 + 1 + 1 + 1) / 5.0) < 1e-12 and abs(st["by_key"]["n_eff_rho1"] - 5 / 1.4) < 1e-12,
          "Kish sum(n^2)/n = 1.4, n_eff(rho=1) = 3.571 (an upper-bound DEFF)")
    clf, stf = reserved_clusters(["fr", "f1x"], {"fr": "a", "f1x": "b"}, family_of={"fr": "F7", "f1x": "F7"})
    check(clf["fr"] == clf["f1x"] and stf["combined"]["n_clusters"] == 1 and stf["by_key"]["n_clusters"] == 2,
          "with families, two stems of one family form ONE cluster")

    # (7) answer-text differences are CLASSIFIED; only an identical prompt with a different answer is a conflict
    LT = {"a1": ("Is the sky blue?", ["Yes", "No"]), "a2": ("is the sky  blue?", ["No", "Yes"]),          # conflict
          "b1": "Simplify 6/8.", "b2": ("simplify 6/8.", ["\\frac{3}{4}", "\\frac{1}{2}"]),                    # formatting
          "c1": ("Name the author.", ["Tolstoy.", "Chekhov"]), "c2": ("Name the author.", ["Tolstoy", "Gogol"]),  # punctuation
          "d1": ("Pick the gas.", ["neon", "iron"]), "d2": ("pick the gas.", ["argon", "gold"]),                # option sets differ
          "e1": "Same answer.", "e2": "same answer."}
    LA = {"a1": "Yes", "a2": "No", "b1": "\\dfrac{3}{4}", "b2": "\\frac{3}{4}", "c1": "Tolstoy.", "c2": "Tolstoy",
          "d1": "neon", "d2": "argon", "e1": "x", "e2": "x"}
    lc = label_conflicts(list(LT), LT, LA)
    byc = {tuple(g["ids"]): g["class"] for g in lc}
    check(byc == {("a1", "a2"): CONFLICT, ("b1", "b2"): FORMATTING_ONLY, ("c1", "c2"): PUNCTUATION_ONLY, ("d1", "d2"): OPTION_SETS_DIFFER}
          and label_classes(lc) == {CONFLICT: 1, FORMATTING_ONLY: 1, PUNCTUATION_ONLY: 1, OPTION_SETS_DIFFER: 1},
          "answer-text differences are classed: conflict 1 (identical prompt, options shuffled), formatting 1 (\\dfrac), "
          "punctuation 1, option sets differ 1; equal answers are no group (%s)" % sorted(byc.values()))
    lc0 = label_conflicts(["r1", "g1", "r3", "r4", "r2", "g3", "g4"], T, tgt)
    check(len(lc0) == 1 and lc0[0]["ids"] == ["g1", "r1"] and lc0[0]["targets"] == ["lyon", "paris"] and lc0[0]["class"] == CONFLICT,
          "a same-text pair with different targets is a CONFLICT: %s" % [(g["ids"], g["targets"], g["class"]) for g in lc0])

    # (C4) one row per stem_key with subset tags on a GPQA-like nested fixture (diamond within main within extended)
    GT = {1: ("Q-alpha?", ["a", "b", "c", "d"]), 2: ("q-alpha?", ["d", "c", "b", "a"]), 3: ("Q-ALPHA?", ["b", "a", "d", "c"]),
          4: ("Q-beta?", ["w", "x", "y", "z"]), 5: ("q-beta?", ["z", "y", "x", "w"]), 6: ("Q-gamma?", ["m", "n", "o", "p"])}
    GS = {1: "gpqa_diamond", 2: "gpqa_main", 3: "gpqa_extended", 4: "gpqa_main", 5: "gpqa_extended", 6: "gpqa_extended"}
    orow = one_row_per_key(list(GT), GT, GS)
    got = sorted((v["row"], tuple(v["ids"]), tuple(v["tags"])) for v in orow.values())
    check(got == [(1, (1, 2, 3), ("gpqa_diamond", "gpqa_extended", "gpqa_main")), (4, (4, 5), ("gpqa_extended", "gpqa_main")),
                  (6, (6,), ("gpqa_extended",))],
          "one row per stem_key: 6 GPQA-like copies -> 3 rows with nested subset tags, shuffled options collapsed (%s)" % got)
    pref = one_row_per_key(list(GT), GT, GS, prefer=lambda i: (GS[i] != "gpqa_extended", i))
    check(sorted(v["row"] for v in pref.values()) == [3, 5, 6], "a prefer= order picks the representative (extended copies: 3, 5, 6)")
    check(refuses(lambda: one_row_per_key([1, 2], GT, {1: "gpqa_main", 2: None})), "a copy without a subset tag is refused")

    # (8) the guard refuses a leaking split, and passes the closed one; the sentinel arm is a separate required argument
    check(refuses(lambda: assert_content_disjoint({"g1", "g4"}, {"r1"}, {"s1"}, T, out=quiet)),
          "assert_content_disjoint REFUSES a split that leaks a reserved twin")
    lk = leak_counts(lambda: assert_content_disjoint({"g2", "g4"}, {"r1"}, {"s1"}, T, out=quiet))
    check(lk is not None and lk["n_twins_sentinel_only"] == 1 and lk["n_twins_reserved"] == 0,
          "assert_content_disjoint REFUSES a split that leaks a SENTINEL twin, and reports it as sentinel-only (%s)" % (lk,))
    check(refuses(lambda: assert_content_disjoint({"g2", "g4"}, {"r1"}, None, T, out=quiet)),
          "assert_content_disjoint REFUSES sentinel_ids = None (the argument is required)")
    check(refuses(lambda: assert_content_disjoint({"f1"}, {"fr"}, (), T, family_of=F, out=quiet)),
          "assert_content_disjoint REFUSES a shared family")
    check(refuses(lambda: assert_content_disjoint({"g4", "r1"}, {"r1"}, (), T, out=quiet)),
          "assert_content_disjoint REFUSES an id on both sides")
    lines = []
    ok_pass = (not refuses(lambda: assert_content_disjoint(r["closed_gen"], {"r1", "r2", "r3", "r4", "m1"}, {"s1"}, T, out=lines.append)))
    check(ok_pass and len(lines) == 1 and "PASS" in lines[0], "assert_content_disjoint PASSES the closed split and prints its line")
    check(refuses(lambda: closed_complement({"g1"}, {"g1"}, set(), T)), "closed_complement refuses an id on two sides")
    check(refuses(lambda: build_closure({"A": {"gen": {"x"}}, "B": {"reserved": {"x"}}}, {"x": "t"})),
          "build_closure refuses an id collision across corpora")
    check(refuses(lambda: closed_complement({"zz"}, set(), set(), T)), "a missing text is a refusal, not a default")
    check(refuses(lambda: closed_complement({"e"}, {"f"}, set(), {"e": "  \t", "f": "x"})) and refuses(lambda: ck_key(("", ["a"]))),
          "an EMPTY stem (after norm-v1) is refused (D7)")

    # (9) the audit body on a synthetic pool: the sentinel leg must REFUSE with the sentinel-only twins (D2 / R4b)
    AP = {"S": {"gen": {"g1", "g2", "g4"}, "reserved": {"r1"}, "sentinel": {"s1"}}}
    alines = []
    aok = _audit_loaded("pselftest", AP, T, None, None, {"moved": 2, "moved_twin_of_reserved": 1, "moved_twin_of_sentinel": 1,
                                                          "sentinel_leg": 1, "res_with_gen_twin": 1}, alines.append)
    check(aok and any("sentinel leg: REFUSED with 1 sentinel-only twin(s); expected 1" in l for l in alines),
          "the audit's SENTINEL LEG refuses with the sentinel-only twin on a synthetic pool (audit ok = %s)" % aok)

    n_ok = sum(1 for c_, _ in results if c_)
    out("content_closure selftest: %d / %d checks PASS" % (n_ok, len(results)))
    return 0 if n_ok == len(results) else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--audit" in argv:
        if "--pool" not in argv or argv.index("--pool") + 1 >= len(argv):
            _refuse("--audit needs --pool <id>")
        return audit(argv[argv.index("--pool") + 1])
    print(__doc__)
    print("usage: content_closure.py --selftest | --audit --pool <id>")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
