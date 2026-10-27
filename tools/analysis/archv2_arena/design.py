"""Candidate designs of the budget memo (section 3) and their simulation.

A design is a list of PARTS; a part = (corpus, roster, strata, N matches per (stratum, pair), filter). The memo's five:

  D4          mmlu,  the 20-model merged roster, 7 anchors,  N 3   (3,990 matches in the memo)
  D1-stage1   mmlu,  the 46-model roster,        7 anchors,  N 2   (13,826)
  D1-full     mmlu,  the 46-model roster,        14 anchors, N 2   (27,650)
  D0          union, the 18-model roster,        52 strata,  N 10  (79,600)
  D2          D1-full + union BBH / MUSR strata, 18 models,  N 3   (~40,000)

Strata are MMLU-Pro CATEGORIES (cells DECLARED: author decision 4 / synthesis decision 5) and union (source, domain).
SUPPLY (EVAL questions per stratum) is a PARAMETER: explicit per-stratum counts (--supply-json), or a corpus total (the
E-D DEV manifest's eval_units) allocated in proportion to the stratum sizes by largest remainder (printed as ARITHMETIC,
not the split's per-anchor counts, which the real draw fixes later). The EVAL questions of a replicate are a seeded
random subset of the stratum's questions of that size.

SCHEDULE (fixed before any verdict, from free data only): the filter is convention A (a match is kept unless both
extracted answers are non-blank and EQUAL; a missing answer keeps it), extracted answers as systematic_budget.build()
normalises them (NOT MatchFilter.kt's norm_shipped: a disclosed simplification). For each pair, in a seeded random
order, N eligible questions with the fewest uses so far (ties by a seeded random key): a balanced design under
reuse. A pair with fewer than N eligible questions takes all it has (EXHAUSTED).
"""
import json
import subprocess

import numpy as np

from . import cert, data
from .verdict_model import match_type

MEMO_DESIGNS = {
    "D4": [dict(corpus="mmlu", roster="x20merged", strata=7, N=3)],
    "D1-stage1": [dict(corpus="mmlu", roster="mmlu46", strata=7, N=2)],
    "D1-full": [dict(corpus="mmlu", roster="mmlu46", strata=14, N=2)],
    "D0": [dict(corpus="union", roster="union18", strata=52, N=10)],
    "D2": [dict(corpus="mmlu", roster="mmlu46", strata=14, N=2),
           dict(corpus="union", roster="union18", strata="BBH|MUSR", N=3)],
}
MEMO_NOMINAL_PMX = {"D0": (7.2, 6.5, 10.5), "D4": (1.1, 1.1, 1.8), "D1-stage1": (2.6, 5.9, 9.5),
                    "D1-full": (5.3, 11.9, 19.1), "D2": (9.0, 15.3, 24.5)}


# ------------------------------------------------------------------------------------------------- supply
def manifest_from_git(spec):
    """spec '<rev>:<path>' read with `git show` (read-only)."""
    out = subprocess.run(["git", "show", spec], capture_output=True, text=True, cwd=data.ROOT)
    if out.returncode != 0:
        raise SystemExit("[DESIGN] git show %s failed: %s" % (spec, out.stderr.strip()))
    return json.loads(out.stdout)


def manifest_eval_units(man):
    for o in man.get("outputs", []):
        if o.get("kind") == "split_v2":
            pc = o["checks"]["per_corpus"]
            return {k: int(v["eval_units"]) for k, v in pc.items()}, man.get("label"), man.get("of_record")
    raise SystemExit("[DESIGN] the manifest has no split_v2 output")


def allocate(total, sizes):
    """Largest-remainder allocation of `total` in proportion to sizes (dict stratum -> size)."""
    tot = float(sum(sizes.values()))
    raw = {k: total * v / tot for k, v in sizes.items()}
    base = {k: int(np.floor(x)) for k, x in raw.items()}
    left = total - sum(base.values())
    for k in sorted(raw, key=lambda k: (-(raw[k] - base[k]), k))[:left]:
        base[k] += 1
    return base


def choose_strata(supply, n, rng):
    """n of the strata, stratified by size: sort by supply, cut into n consecutive groups, one drawn per group."""
    names = sorted(supply, key=lambda k: (-supply[k], k))
    if n >= len(names):
        return names
    groups = np.array_split(np.arange(len(names)), n)
    return sorted(names[int(rng.choice(g))] for g in groups)


# ------------------------------------------------------------------------------------------------ schedule
def schedule_stratum(qs, models, Parr, N, rng):
    """qs: EVAL question ids of the stratum; Parr (Q, M) extracted answers ('' blank). Returns a list of (i, j, qrow)
    and the EXHAUSTED pair count."""
    Q, M = Parr.shape
    use = np.zeros(Q, dtype=int)
    pairs = [(i, j) for i in range(M) for j in range(i + 1, M)]
    order = rng.permutation(len(pairs))
    out = []; exhausted = 0
    for k in order:
        i, j = pairs[k]
        pa, pb = Parr[:, i], Parr[:, j]
        elig = np.flatnonzero(~((pa != "") & (pb != "") & (pa == pb)))
        if elig.size < N:
            exhausted += 1
        if elig.size == 0:
            continue
        key = rng.random(elig.size)
        pick = elig[np.lexsort((key, use[elig]))][:N]
        use[pick] += 1
        for q in pick:
            # which model is 'a' is itself random (the schedule of record shuffles the deck)
            out.append((i, j, int(q)) if rng.random() < 0.5 else (j, i, int(q)))
    return out, exhausted


# --------------------------------------------------------------------------------------------- simulation
class DesignBoard:
    """A simulated board with Board's interface (by, votes, K, P, L, models) for data.edges_fast."""

    def __init__(self, models, label):
        self.models = list(models); self.label = label
        self.by = {}; self.votes = {}; self.K = {}; self.P = {}; self.L = {}


MUTANT = None          # SELFTEST-ONLY switch (None in every real run): keyacc_cell


def model_level_keyacc(correct, n, present):
    """RULING A (4b25059): keyacc is MODEL-LEVEL. correct (G, M) = convention-A correct counts per (anchor, model)
    over the anchor's judged questions (a design: its EVAL supply), n (G,) = the anchor's question count, present (G, M)
    = the models present in the anchor. keyacc_m = sum_g correct[g, m] / sum_g n[g] (pooled over ALL anchors),
    broadcast to every anchor and CENTRED PER ANCHOR over the models present (0 where absent)."""
    correct = np.asarray(correct, dtype=float); n = np.asarray(n, dtype=float); present = np.asarray(present, bool)
    if MUTANT == "keyacc_cell":
        KA = correct / np.maximum(n, 1.0)[:, None]
    else:
        KA = np.repeat((correct.sum(axis=0) / max(1.0, n.sum()))[None, :], correct.shape[0], axis=0)
    out = np.zeros_like(KA)
    for g in range(KA.shape[0]):
        if present[g].any():
            out[g, present[g]] = KA[g, present[g]] - KA[g, present[g]].mean()
    return out


def simulate_part(part, keytab, strata_qs, vm, rng_sched, rng_verdict, u, label):
    """strata_qs: dict stratum -> list of EVAL question ids (this replicate). Returns (DesignBoard, stats)."""
    models = part["models"]
    board = DesignBoard(models, label)
    n_match = 0; n_q_used = 0; exhausted = 0
    strata = sorted(strata_qs)
    arrays = {st: keytab.arrays(models, strata_qs[st]) for st in strata}
    KAd = None
    if hasattr(vm, "beta"):
        # fresh-judge v2, ruling A (4b25059): MODEL-LEVEL keyacc over the design's WHOLE EVAL supply (all its strata),
        # convention A (a missing key row counts wrong), broadcast and centred per stratum
        KAd = model_level_keyacc(np.array([(arrays[st][0] == 1).sum(axis=0) for st in strata]),
                                 np.array([len(strata_qs[st]) for st in strata]),
                                 np.ones((len(strata), len(models)), bool))
    for g, st in enumerate(strata):
        qs = strata_qs[st]
        K, P, L = arrays[st]
        sched, ex = schedule_stratum(qs, models, P, part["N"], rng_sched)
        exhausted += ex
        if not sched:
            continue
        I = np.array([s[0] for s in sched]); J = np.array([s[1] for s in sched]); R = np.array([s[2] for s in sched])
        ka, kb = K[R, I].astype(int), K[R, J].astype(int)
        t = np.array([match_type(x, y, p1, p2) for x, y, p1, p2 in zip(ka, kb, P[R, I], P[R, J])])
        kd = np.where((ka >= 0) & (kb >= 0), ka - kb, 0).astype(float)
        dl = (L[R, I] - L[R, J]) / 1000.0
        dl = np.where(np.isfinite(dl), dl, 0.0)
        S = dict(g=np.full(I.size, g), a=I, b=J, t=t, kd=kd, dl=dl)
        if KAd is not None:
            S["ka"] = KAd[g, I] - KAd[g, J]
        sim = vm.simulate(S, rng_verdict, mode="random", u=u)
        rows = []; votes = []
        for k in range(I.size):
            a, b, q = models[I[k]], models[J[k]], qs[R[k]]
            w = a if sim["wa"][k] == 1.0 else (b if sim["wa"][k] == 0.0 else "TIE")
            rows.append((a, b, q, w))
            votes.append(({0: "Model A", 1: "Model B", 2: "TIE"}[int(sim["y1"][k])],
                          {0: "Model A", 1: "Model B", 2: "TIE"}[int(sim["y2"][k])]))
        board.by[st] = rows; board.votes[st] = votes
        n_match += I.size; n_q_used += int(np.unique(R).size)
        for r, q in enumerate(qs):
            board.K[q] = {m: int(K[r, c]) for c, m in enumerate(models) if K[r, c] >= 0}
            board.P[q] = {m: str(P[r, c]) for c, m in enumerate(models)}
            board.L[q] = {m: float(L[r, c]) for c, m in enumerate(models) if np.isfinite(L[r, c])}
    return board, dict(matches=n_match, questions_used=n_q_used, reuse=(n_match / n_q_used if n_q_used else float("nan")),
                       exhausted_pairs=exhausted)


def frontier_mask(edges, gap=0.017):
    """Frontier-internal edges (both endpoints in the stratum's top KEY tier by the 0.017 adjacency rule): BANDED by
    rule, never called, excluded from nominal."""
    by = {}
    for e in edges:
        by.setdefault(e["anchor"], {}).update({e["a"]: e["la"][0], e["b"]: e["la"][1]})
    top = {}
    for anc, acc in by.items():
        top[anc] = set(cert.key_tiers(acc, sorted(acc), gap)[0])
    return np.array([e["a"] in top[e["anchor"]] and e["b"] in top[e["anchor"]] for e in edges], dtype=bool)
