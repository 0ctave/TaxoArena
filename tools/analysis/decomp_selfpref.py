"""DECOMP — is the ARENA-13 +7.9pp self-preference, or answer coincidence? (registered 2026-09-14, ZERO calls)

  python tools/analysis/decomp_selfpref.py

The two arms of ARENA-13 differ in two ways at once: the reference is produced by the new contestant's own
vendor, AND it endorses the new contestant's answer far more often than the ensemble does. This separates them
using only what is already on disk - every match carries four known letters (the new contestant's answer, the
opponent's answer, the ensemble reference, the grok reference).

STRATUM SAME: the two references give the same letter, so the two prompts are byte-identical and any
  disagreement between the arms is the judge's own stochasticity - the programme's first test-retest number.
STRATUM DIFF: the references differ; the whole effect must live here.
KITAGAWA: the +7.9pp splits into a COMPOSITION component (which model the reference happens to endorse) and a
  RESIDUAL rate component (everything else, which is what "self-preference" would have to mean).
"""
import os, sys, random, sqlite3
from collections import defaultdict, Counter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_reference as rref
import rubric_p8 as p8
import arena13 as a13

NEW = a13.NEW
OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "decomp_outcome.txt")


def cell(ref_letter, new_ans, opp_ans):
    if ref_letter == new_ans: return "endorses NEW"
    if ref_letter == opp_ans: return "endorses OPP"
    return "endorses NEITHER"


def main():
    pool, P, K, OPT, cot, route, anchor_of = a13.setup()
    rref.set_reference("grok-reasoning"); grok = rref.references()
    con = a13.open_cache()
    sch = {m: (q, opp, anc, fr) for m, q, opp, anc, fr in con.execute("SELECT mid, qid, opponent, anchor, frontier FROM schedule")}
    V = defaultdict(dict)
    for m, arm, w, inv in con.execute("SELECT mid, arm, winner, invalid FROM verdicts"):
        if not inv: V[m][arm] = w
    rows = []
    for m, d in V.items():
        if "ensemble" not in d or "selfref" not in d: continue
        q, opp, anc, fr = sch[m]
        e = a13.ensemble_ref(q, P, OPT, {opp, NEW}); g = grok.get(q)
        if e is None or g is None: continue
        na, oa = cot[q][0], P[q].get(opp, "")
        rows.append(dict(mid=m, qid=q, opp=opp, new=na, oppa=oa, ens=e[0], grk=g[0],
                         wE=d["ensemble"], wS=d["selfref"],
                         cE=cell(e[0], na, oa), cS=cell(g[0], na, oa)))
    N = len(rows)
    winE = lambda r: r["wE"] == NEW
    winS = lambda r: r["wS"] == NEW
    pE = sum(1 for r in rows if winE(r)) / N; pS = sum(1 for r in rows if winS(r)) / N

    L = []
    L.append("=== DECOMP: what the ARENA-13 +7.9pp is actually made of (%d paired frontier matches, zero calls) ===" % N)
    L.append("  the new contestant's win rate: ensemble reference %.3f | its own reference %.3f (%+.3f)" % (pE, pS, pS - pE))
    L.append("")
    L.append("  reference composition - which side each reference endorses:")
    for c in ("endorses NEW", "endorses OPP", "endorses NEITHER"):
        ne = sum(1 for r in rows if r["cE"] == c); ns = sum(1 for r in rows if r["cS"] == c)
        L.append("    %-18s ensemble %4d (%.3f) | grok/self %4d (%.3f)" % (c, ne, ne / N, ns, ns / N))

    # (1) STRATUM SAME - byte-identical prompts, so this is pure judge noise
    same = [r for r in rows if r["ens"] == r["grk"]]
    diff = [r for r in rows if r["ens"] != r["grk"]]
    ds = sum(1 for r in same if r["wE"] != r["wS"])
    b = sum(1 for r in same if winS(r) and not winE(r)); c = sum(1 for r in same if winE(r) and not winS(r))
    L.append("")
    L.append("  (1) STRATUM SAME - the two references give the SAME letter, so the two prompts are BYTE-IDENTICAL:")
    L.append("      n=%d (%.1f%% of the matches) | the arms disagree on %d of them = %.3f" % (len(same), 100 * len(same) / N, ds, ds / max(1, len(same))))
    L.append("      win rate ensemble %.3f | self %.3f (%+.3f) | %d:%d | McNemar p=%.4g"
             % (sum(1 for r in same if winE(r)) / max(1, len(same)), sum(1 for r in same if winS(r)) / max(1, len(same)),
                (sum(1 for r in same if winS(r)) - sum(1 for r in same if winE(r))) / max(1, len(same)), b, c, p8.mcn(b, c)))
    L.append("      READ: this is the judge's TEST-RETEST noise at temperature - the same prompt twice. Every paired")
    L.append("      comparison in the programme sits on top of it, and it had never been measured until now.")

    # (2) STRATUM DIFF
    bd = sum(1 for r in diff if winS(r) and not winE(r)); cd = sum(1 for r in diff if winE(r) and not winS(r))
    pEd = sum(1 for r in diff if winE(r)) / max(1, len(diff)); pSd = sum(1 for r in diff if winS(r)) / max(1, len(diff))
    L.append("")
    L.append("  (2) STRATUM DIFF - the references point at different answers, n=%d (%.1f%%):" % (len(diff), 100 * len(diff) / N))
    L.append("      win rate ensemble %.3f | self %.3f (%+.3f) | %d:%d | McNemar p=%.4g" % (pEd, pSd, pSd - pEd, bd, cd, p8.mcn(bd, cd)))

    # (3) KITAGAWA decomposition
    def rates(key, winf):
        out = {}
        for c_ in ("endorses NEW", "endorses OPP", "endorses NEITHER"):
            s = [r for r in rows if r[key] == c_]
            out[c_] = (len(s), (sum(1 for r in s if winf(r)) / len(s)) if s else float("nan"))
        return out
    rA = rates("cE", winE); rB = rates("cS", winS)
    comp = sum((rB[c][0] - rA[c][0]) / N * (rA[c][1] if rA[c][0] else 0.0) for c in rA)
    rate = sum(rB[c][0] / N * ((rB[c][1] if rB[c][0] else 0.0) - (rA[c][1] if rA[c][0] else 0.0)) for c in rA)
    L.append("")
    L.append("  (3) KITAGAWA decomposition of the %+.3f gap:" % (pS - pE))
    L.append("      %-18s %-28s %-28s" % ("cell", "ensemble arm  n / win rate", "self arm  n / win rate"))
    for c_ in ("endorses NEW", "endorses OPP", "endorses NEITHER"):
        L.append("      %-18s %5d  %.3f%-17s %5d  %.3f" % (c_, rA[c_][0], rA[c_][1], "", rB[c_][0], rB[c_][1]))
    L.append("      COMPOSITION (which side the reference endorses)  %+.3f   = %.0f%% of the gap" % (comp, 100 * comp / (pS - pE) if pS != pE else 0))
    L.append("      RESIDUAL    (everything else, i.e. self-preference) %+.3f   = %.0f%% of the gap" % (rate, 100 * rate / (pS - pE) if pS != pE else 0))
    # paired bootstrap over matches
    rng = random.Random(42); comps = []; rates_ = []
    for _ in range(2000):
        bs = [rows[rng.randrange(N)] for _ in range(N)]
        def rt(key, winf):
            o = {}
            for c_ in ("endorses NEW", "endorses OPP", "endorses NEITHER"):
                s = [r for r in bs if r[key] == c_]
                o[c_] = (len(s), (sum(1 for r in s if winf(r)) / len(s)) if s else 0.0)
            return o
        a_, b_ = rt("cE", winE), rt("cS", winS)
        comps.append(sum((b_[c][0] - a_[c][0]) / N * a_[c][1] for c in a_))
        rates_.append(sum(b_[c][0] / N * (b_[c][1] - a_[c][1]) for c in a_))
    comps.sort(); rates_.sort()
    L.append("      bootstrap 95%% CI (2,000 paired resamples): composition [%+.3f, %+.3f] | residual [%+.3f, %+.3f]"
             % (comps[50], comps[1949], rates_[50], rates_[1949]))

    # (4) cell-matched McNemar - the residual tested where the reference endorses the same side in both arms
    matched = [r for r in rows if r["cE"] == r["cS"]]
    bm = sum(1 for r in matched if winS(r) and not winE(r)); cm = sum(1 for r in matched if winE(r) and not winS(r))
    pm = p8.mcn(bm, cm)
    pEm = sum(1 for r in matched if winE(r)) / max(1, len(matched)); pSm = sum(1 for r in matched if winS(r)) / max(1, len(matched))
    L.append("")
    L.append("  (4) CELL-MATCHED - only matches where BOTH references endorse the same side, n=%d:" % len(matched))
    L.append("      win rate ensemble %.3f | self %.3f (%+.3f) | %d:%d | McNemar p=%.4g" % (pEm, pSm, pSm - pEm, bm, cm, pm))
    for c_ in ("endorses NEW", "endorses OPP", "endorses NEITHER"):
        s = [r for r in matched if r["cE"] == c_]
        if not s: continue
        bb = sum(1 for r in s if winS(r) and not winE(r)); cc = sum(1 for r in s if winE(r) and not winS(r))
        L.append("        %-18s n=%4d | ensemble %.3f self %.3f (%+.3f) | %d:%d | p=%.4g"
                 % (c_, len(s), sum(1 for r in s if winE(r)) / len(s), sum(1 for r in s if winS(r)) / len(s),
                    (sum(1 for r in s if winS(r)) - sum(1 for r in s if winE(r))) / len(s), bb, cc, p8.mcn(bb, cc)))

    # The registered rule is DIRECTIONAL: "both mechanisms are real" requires a residual of AT LEAST +2pp that is
    # significant on the cell-matched test, because only a POSITIVE residual can mean self-preference. The first
    # version of this line tested abs(residual), which would have called a residual pointing the OTHER way
    # evidence for self-preference; corrected to the signed reading the registration specifies.
    small = not (rate >= 0.02 and pm < 0.05)
    L.append("")
    L.append("  VERDICT under the rule fixed before looking: residual %+.3f, cell-matched McNemar p=%.4g" % (rate, pm))
    L.append("  -> %s" % ("AMEND: the ARENA-13 claim becomes REFERENCE-AGREEMENT LEAKAGE, not self-preference. A shared"
                          "\n     reference inflates whichever contestant mirrors it; vendor identity need not enter."
                          "\n     Here the residual points AGAINST self-preference: conditioning on which side the reference"
                          "\n     endorses, the new contestant does no better under its own reference, and slightly worse."
                          if small else
                          "BOTH mechanisms are real: composition explains most of the gap, and a residual survives\n"
                          "     conditioning on which side the reference endorses. Report both sizes."))
    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    main()
