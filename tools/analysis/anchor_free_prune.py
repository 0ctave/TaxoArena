"""ANCHOR-FREE-CERT arm 0, PRUNE: "certify by pruning" the anchor-free tree of record at ZERO build cost.
Registered 2026-09-17 at the END of docs/judge_v2_program.md (plan docs/agents/plans/2026-09-17_anchor_free_cert.md).
ZERO LLM calls; every DB is opened mode=ro; the only file written is --out.

  python tools/analysis/anchor_free_prune.py [--run experiment_results/anchorfree/af/seed_42]
         [--site-null experiment_results/anchorfree/site_null_af_s42.csv] [--pool p2dca21ab5f4ef3ae]
         [--out experiment_results/anchorfree/anchor_free_prune_readout.txt] [--dry-run]

Two VIEWS of the record's tree (af_s42: z 2.0, mcs 55, 256-dim slice; 81 leaves; 69 split sites, 16 certified at
the 300-rep site null, cert_site_p95):
  A  P2's maximal all-certified prefix: walk from the root; keep a split site iff it is certified AND every
     ancestor site is kept; cut at the first uncertified site.  (= the CSV's trunk_member column; asserted.)
  B  every certified site plus the uncertified sites on the path from the root to a certified one ("bridging").
A node is a leaf of a view iff it is reachable through kept sites and is not itself a kept site.

Per view, the readout's own functions (anchor_free_readout: load_tree, corpus, full_vectors, sliced, route,
score_cells; free_tests_f4_f7: keyed_questions, embed_matrix, loo_imp, boot_mean_ci) are applied with the
candidate set restricted to the view's leaf nodes (their vmfMu, unit-normalised, max cosine of the first-256 MRL
slice - route()'s rule verbatim):
  kept sites (id, depth, certified, n, observed_sep, p95); leaves (count, depth distribution, largest by train
  routing); held-out purity by majority-train leaf label with Wilson CI (train = 8,324 distinct non-pool texts;
  held-out = the 3,445-question pool of record); the F6 key-only leaf LOO Brier improvement x1000 on the 10,925
  keyed questions (F2-CLEAN caveat: LOO removes the scored question from its cell mean, not from the choice of
  boundaries) with the paired per-question difference against the record's 81-leaf routing (F6's bootstrap CI);
  per-leaf held-out top-1 support (median, min, leaves >= 50); certified share = kept certified / kept sites.
The record's 81-leaf numbers are printed beside as the control (its F6 number is computed both through the
readout's f6_block and through this script's view path, and the two are asserted equal).

Registered predictions (scored HELD / FAILED):
  view A: 11 sites / 19 leaves, purity 0.60-0.65, key-only +7 to +9, support median ~180 (G2, G3 FAIL)
  view B: 24 sites incl. 8 bridging, 16 certified, 34 leaves, purity 0.66-0.70, key-only +10 to +12, support ~100
"~" bands: the registration gives no tolerance; this script scores a "~x" support prediction as within +-20% of x
and prints the band.  Guardrails: G1 purity >= 0.685; G2 key-only >= +12.19; G3 leaves in [60, 100] AND median
held-out support >= 30 AND >= 15 leaves at >= 50.
If the view site counts differ from the plan's 11 / 24 the difference is printed, never reconciled.
"""
import os, sys, csv, argparse
from collections import Counter, defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import pool_guard                                   # noqa: E402
import anchor_free_readout as AR                    # noqa: E402  load_tree, corpus, full_vectors, sliced, route, score_cells, f6_block
import free_tests_f4_f7 as F                        # noqa: E402  keyed_questions, embed_matrix, loo_imp, boot_mean_ci

DEFAULT_RUN = os.path.join(ROOT, "experiment_results", "anchorfree", "af", "seed_42")
DEFAULT_CSV = os.path.join(ROOT, "experiment_results", "anchorfree", "site_null_af_s42.csv")
DEFAULT_OUT = os.path.join(ROOT, "experiment_results", "anchorfree", "anchor_free_prune_readout.txt")
ROOT_ID = "n00000001"

G1_PURITY = 0.685
G2_KEY = 12.19
G3_LEAVES = (60, 100)
G3_MEDIAN = 30
G3_N50 = 15
TILDE_BAND = 0.20
PRED = {
    "A": dict(sites=11, bridging=0, certified=11, leaves=19, purity=(0.60, 0.65), key=(7.0, 9.0), support=180),
    "B": dict(sites=24, bridging=8, certified=16, leaves=34, purity=(0.66, 0.70), key=(10.0, 12.0), support=100),
}


# ----------------------------------------------------------------------------------------------- sites
def site_rows(path):
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8")))
    return {r["node_id"]: r for r in rows}


def view_sites(tree, sites, cert):
    """A: maximal all-certified prefix from the root. B: certified sites + bridging ancestors."""
    byid = tree["byid"]
    parent = {c: n["id"] for n in byid.values() for c in n.get("childIds", [])}
    A = set()
    stack = [ROOT_ID]
    while stack:
        nid = stack.pop()
        if nid in cert:
            A.add(nid)
            stack += [c for c in byid[nid]["childIds"] if c in sites]
    B = set()
    for c in cert:
        n = c
        while n is not None:
            B.add(n)
            n = parent.get(n)
    return A, B


def view_leaves(tree, kept):
    """Leaf nodes of a view: children of kept sites that are not kept sites; the record when kept = all sites."""
    byid = tree["byid"]
    out = []
    stack = [ROOT_ID]
    while stack:
        nid = stack.pop()
        if nid in kept:
            stack += byid[nid]["childIds"]
        else:
            out.append(byid[nid])
    return sorted(out, key=lambda n: n["id"])


def as_view(tree, leaves):
    """A copy of load_tree's dict whose leaf level is the view's leaves; route() then restricts to them."""
    byid = tree["byid"]
    parent = {c: n["id"] for n in byid.values() for c in n.get("childIds", [])}

    def depth1(nid):
        n = byid[nid]
        while n["depth"] > 1:
            n = byid[parent[n["id"]]]
        return n["id"]
    M = np.asarray([n["vmfMu"] for n in leaves], dtype=np.float64)
    nn = np.linalg.norm(M, axis=1, keepdims=True); nn[nn == 0] = 1.0
    v = dict(tree)
    v.update(leaves=leaves, leaf_ids=[n["id"] for n in leaves], leaf_mu=M / nn,
             leaf_d1=[depth1(n["id"]) for n in leaves])
    return v


# ----------------------------------------------------------------------------------------------- measures
def f6_leaves(leaves, keyed):
    """f6_block's body on an explicit leaf list (F6's loaders and LOO formula; nothing re-implemented)."""
    models, G, cat, text, qs_all = keyed
    trip = [(n["id"], np.array(n["vmfMu"], dtype=np.float64)) for n in leaves]
    dim = len(trip[0][1])
    vec = F.embed_matrix(AR.EMB_DB, list(text.values()), dim)
    qs = [q for q in qs_all if text[q] in vec]
    Q = np.stack([vec[text[q]] for q in qs])
    M = np.stack([mu / (np.linalg.norm(mu) or 1) for _, mu in trip])
    idx = np.argmax(Q @ M.T, axis=1)
    leaf_p = {q: trip[i][0] for q, i in zip(qs, idx)}
    il = F.loo_imp(leaf_p, qs, models, G)
    return dict(n=len(qs), leaves=len(trip), dim=dim, leaf=float(il.mean()), per_q=dict(zip(qs, il)))


def measure(tree, kept, sites, cert, train, heldout, vec, keyed):
    leaves = view_leaves(tree, kept)
    v = as_view(tree, leaves)
    Qt = AR.sliced(vec, [t for t, _ in train], v["dim"])
    Qh = AR.sliced(vec, [t for t, _ in heldout], v["dim"])
    it = AR.route(v, Qt); ih = AR.route(v, Qh)
    key_t = [v["leaf_ids"][i] for i in it]; key_h = [v["leaf_ids"][i] for i in ih]
    pur = AR.score_cells(key_t, key_h, train, heldout)
    train_n = Counter(key_t); held_n = Counter(key_h)
    tc = defaultdict(Counter)
    for k, (_, c) in zip(key_t, train):
        tc[k][c] += 1
    major_share = {k: cnt.most_common(1)[0][1] / sum(cnt.values()) for k, cnt in tc.items()}
    support = [held_n.get(l, 0) for l in v["leaf_ids"]]
    f6 = f6_leaves(leaves, keyed)
    kept_rows = sorted((sites[s] for s in kept), key=lambda r: (int(r["depth"]), -int(r["n"])))
    return dict(kept=kept_rows, n_sites=len(kept), n_cert=len(kept & cert), n_bridge=len(kept - cert),
                leaves=leaves, n_leaves=len(leaves), depth_dist=Counter(n["depth"] for n in leaves),
                largest=max(train_n.items(), key=lambda kv: kv[1]), train_n=train_n, held_n=held_n, major_share=major_share,
                purity=pur, support=support, f6=f6, view=v)


# ----------------------------------------------------------------------------------------------- scoring
def in_band(x, lo, hi):
    return lo <= x <= hi


def score(tag, m, diff):
    P = PRED[tag]
    lines = []

    def s(name, ok, detail):
        lines.append("    %-46s %s   (%s)" % (name, "HELD" if ok else "FAILED", detail))
    s("sites %d" % P["sites"], m["n_sites"] == P["sites"], "observed %d" % m["n_sites"])
    if tag == "B":
        s("bridging %d / certified %d" % (P["bridging"], P["certified"]),
          m["n_bridge"] == P["bridging"] and m["n_cert"] == P["certified"],
          "observed %d / %d" % (m["n_bridge"], m["n_cert"]))
    s("leaves %d" % P["leaves"], m["n_leaves"] == P["leaves"], "observed %d" % m["n_leaves"])
    acc = m["purity"]["acc"]
    s("purity %.2f-%.2f" % P["purity"], in_band(acc, *P["purity"]), "observed %.3f" % acc)
    k = 1000 * m["f6"]["leaf"]
    s("key-only %+.0f to %+.0f" % P["key"], in_band(k, *P["key"]), "observed %+.3f" % k)
    med = float(np.median(m["support"]))
    lo, hi = P["support"] * (1 - TILDE_BAND), P["support"] * (1 + TILDE_BAND)
    s("support median ~%d [%.0f, %.0f]" % (P["support"], lo, hi), in_band(med, lo, hi), "observed %.0f" % med)
    return lines


def guardrails(m):
    acc = m["purity"]["acc"]; k = 1000 * m["f6"]["leaf"]
    med = float(np.median(m["support"])); n50 = sum(1 for x in m["support"] if x >= 50)
    g1 = acc >= G1_PURITY
    g2 = k >= G2_KEY
    g3a = G3_LEAVES[0] <= m["n_leaves"] <= G3_LEAVES[1]; g3b = med >= G3_MEDIAN; g3c = n50 >= G3_N50
    g3 = g3a and g3b and g3c
    return [
        "    G1 purity >= %.3f: %.3f -> %s" % (G1_PURITY, acc, "HOLD" if g1 else "FAIL"),
        "    G2 key-only >= %+.2f: %+.3f -> %s" % (G2_KEY, k, "HOLD" if g2 else "FAIL"),
        "    G3 leaves in [%d, %d] (%d: %s), median support >= %d (%.0f: %s), >= %d leaves at >= 50 (%d: %s) -> %s"
        % (G3_LEAVES[0], G3_LEAVES[1], m["n_leaves"], "ok" if g3a else "no", G3_MEDIAN, med, "ok" if g3b else "no",
           G3_N50, n50, "ok" if g3c else "no", "HOLD" if g3 else "FAIL"),
    ], (g1, g2, g3)


# ----------------------------------------------------------------------------------------------- main
def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", default=DEFAULT_RUN)
    ap.add_argument("--site-null", default=DEFAULT_CSV)
    ap.add_argument("--pool", default=pool_guard.MMLU_PRO_POOL)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--dry-run", action="store_true", help="sites and leaves of each view only; no embedding or key DB read")
    a = ap.parse_args(argv)

    L = []
    pid = pool_guard.assert_pool_of_record(a.pool)
    L.append("=== ANCHOR-FREE-CERT arm 0 PRUNE readout (registered 2026-09-17; zero LLM calls; zero builds) ===")
    L.append("  pool of record: %s | tree: %s | site null: %s" % (pid, AR.run_name(a.run), os.path.relpath(a.site_null, ROOT)))

    tree = AR.load_tree(a.run)
    if tree["multi_parent"]:
        raise SystemExit("[PRUNE] %d multi-parent nodes; the view walk assumes a tree" % tree["multi_parent"])
    sites = site_rows(a.site_null)
    internal = {n["id"] for n in tree["byid"].values() if not n["isLeaf"]}
    if set(sites) != internal:
        raise SystemExit("[PRUNE] site CSV rows (%d) != internal nodes of the final DAG (%d)" % (len(sites), len(internal)))
    for nid, r in sites.items():
        if int(r["k"]) != len(tree["byid"][nid]["childIds"]):
            raise SystemExit("[PRUNE] %s: CSV k %s != %d children" % (nid, r["k"], len(tree["byid"][nid]["childIds"])))
    cert = {s for s, r in sites.items() if r["cert_site_p95"] == "true"}
    trunk = {s for s, r in sites.items() if r["trunk_member"] == "true"}
    A, B = view_sites(tree, set(sites), cert)
    if A != trunk:
        raise SystemExit("[PRUNE] view A %s != CSV trunk_member %s" % (sorted(A), sorted(trunk)))
    L.append("  record: %d nodes / %d leaves / %d split sites, %d certified (cert_site_p95, %s reps); view A == CSV trunk_member: yes"
             % (tree["nodes"], len(tree["leaves"]), len(sites), len(cert), next(iter(sites.values()))["reps"]))
    views = {"A": A, "B": B, "record": set(sites)}
    for tag in ("A", "B"):
        P = PRED[tag]
        got = (len(views[tag]), len(views[tag] - cert), len(view_leaves(tree, views[tag])))
        exp = (P["sites"], P["bridging"], P["leaves"])
        L.append("  view %s: %d sites (%d bridging), %d leaves; plan expected %d (%d), %d -> %s"
                 % (tag, got[0], got[1], got[2], exp[0], exp[1], exp[2],
                    "MATCH" if got == exp else "DIFFERS FROM THE PLAN (reported, not reconciled)"))
    if a.dry_run:
        for tag in ("A", "B"):
            L.append("  view %s sites: %s" % (tag, ", ".join("%s(d%s%s)" % (s, sites[s]["depth"], "" if s in cert else ",bridge")
                                                              for s in sorted(views[tag], key=lambda s: (int(sites[s]["depth"]), s)))))
        print("\n".join(L)); return 0

    train, heldout, cs = AR.corpus(pid)
    vec = AR.full_vectors([t for t, _ in train] + [t for t, _ in heldout])
    miss = [t for t, _ in train + heldout if t not in vec]
    if miss:
        raise SystemExit("[PRUNE] %d corpus texts have no embedding" % len(miss))
    L.append("  corpus: %d mmlu_pro rows, %d distinct texts; held-out %d; train %d distinct texts; %d categories"
             % (cs["rows"], cs["distinct"], len(heldout), len(train), len({c for _, c in train})))
    keyed = F.keyed_questions()
    M = {tag: measure(tree, kept, sites, cert, train, heldout, vec, keyed) for tag, kept in views.items()}

    # the view path on the full site set must equal the readout's own instrument on the record
    rec_block = AR.f6_block(tree["run_dir"], keyed)
    if M["record"]["n_leaves"] != len(tree["leaves"]) or set(M["record"]["view"]["leaf_ids"]) != set(tree["leaf_ids"]):
        raise SystemExit("[PRUNE] the all-sites view does not reproduce the record's leaf set")
    if abs(rec_block["leaf"] - M["record"]["f6"]["leaf"]) > 1e-12 or rec_block["n"] != M["record"]["f6"]["n"]:
        raise SystemExit("[PRUNE] view-path F6 %.6f != f6_block %.6f" % (M["record"]["f6"]["leaf"], rec_block["leaf"]))
    L.append("  control check: the all-sites view = the record's 81 leaves; F6 via the view path %+.3f == f6_block %+.3f (n=%d)"
             % (1000 * M["record"]["f6"]["leaf"], 1000 * rec_block["leaf"], rec_block["n"]))

    # paired F6 differences against the record's 81-leaf routing
    diff = {}
    for tag in ("A", "B"):
        qs = [q for q in M[tag]["f6"]["per_q"] if q in M["record"]["f6"]["per_q"]]
        d = np.array([M[tag]["f6"]["per_q"][q] - M["record"]["f6"]["per_q"][q] for q in qs])
        lo, hi = F.boot_mean_ci(d)
        diff[tag] = (1000 * d.mean(), 1000 * lo, 1000 * hi, len(qs))

    # ---- kept sites
    for tag in ("A", "B"):
        m = M[tag]
        L.append("")
        L.append("  view %s kept sites (%d; %d certified, %d bridging): id depth cert n observed_sep site_p95"
                 % (tag, m["n_sites"], m["n_cert"], m["n_bridge"]))
        for r in m["kept"]:
            L.append("    %s  d%s  %-6s  n=%5s  sep %.4f  p95 %.4f  k=%s  %s"
                     % (r["node_id"], r["depth"], "cert" if r["node_id"] in cert else "BRIDGE", r["n"],
                        float(r["observed_sep"]), float(r["site_null_p95"]), r["k"], r["label"]))

    # ---- table
    W = 26
    L.append("")
    L.append("  %-52s %*s %*s %*s" % ("readout", W, "view A", W, "view B", W, "record (81 leaves)"))
    L.append("  " + "-" * (52 + 3 * W + 3))

    def row(name, f):
        L.append("  %-52s %*s %*s %*s" % (name, W, f(M["A"], "A"), W, f(M["B"], "B"), W, f(M["record"], "record")))
    row("kept sites / certified / bridging", lambda m, t: "%d / %d / %d" % (m["n_sites"], m["n_cert"], m["n_bridge"]))
    row("certified share (kept certified / kept sites)", lambda m, t: "%.1f%%" % (100 * m["n_cert"] / m["n_sites"]))
    row("leaves", lambda m, t: "%d" % m["n_leaves"])
    row("  leaf depth distribution (depth:count)",
        lambda m, t: " ".join("%d:%d" % (d, c) for d, c in sorted(m["depth_dist"].items())))
    row("  largest leaf by train routing (id, n, major)",
        lambda m, t: "%s %d %s" % (m["largest"][0], m["largest"][1], m["purity"]["major"][m["largest"][0]]))
    row("  leaves used by held-out / with no train member",
        lambda m, t: "%d / %d" % (m["purity"]["cells_heldout"], m["purity"]["cells_heldout_untrained"]))
    row("held-out purity, majority-train leaf label [Wilson]",
        lambda m, t: "%.3f [%.3f, %.3f]" % (m["purity"]["acc"], m["purity"]["lo"], m["purity"]["hi"]))
    row("  hits / n", lambda m, t: "%d / %d" % (m["purity"]["hits"], m["purity"]["n"]))
    row("  train-side purity of the leaf labels", lambda m, t: "%.3f" % m["purity"]["train_purity"])
    row("F6 key-only leaf LOO Brier improvement x1000 (n=%d)" % M["record"]["f6"]["n"],
        lambda m, t: "%+.3f" % (1000 * m["f6"]["leaf"]))
    row("  paired diff vs record x1000 [95% boot CI]",
        lambda m, t: "-" if t == "record" else "%+.3f [%+.3f, %+.3f]" % diff[t][:3])
    row("held-out top-1 support per leaf: median / min / max",
        lambda m, t: "%.0f / %d / %d" % (np.median(m["support"]), min(m["support"]), max(m["support"])))
    row("  leaves at >= 50 held-out questions", lambda m, t: "%d of %d" % (sum(1 for x in m["support"] if x >= 50), m["n_leaves"]))
    row("  leaves at >= 120 held-out questions (H6b SE 0.15 floor)",
        lambda m, t: "%d of %d" % (sum(1 for x in m["support"] if x >= 120), m["n_leaves"]))

    # ---- per-leaf support
    for tag in ("A", "B"):
        m = M[tag]
        L.append("")
        L.append("  view %s leaves (id depth held-out train majority-train label, its train share):" % tag)
        for n in sorted(m["leaves"], key=lambda n: -m["held_n"].get(n["id"], 0)):
            lid = n["id"]
            L.append("    %s d%d  held %4d  train %4d  %-16s %s" % (lid, n["depth"], m["held_n"].get(lid, 0), m["train_n"].get(lid, 0),
                                                                     m["purity"]["major"].get(lid, "-"),
                                                                     "%.2f" % m["major_share"][lid] if lid in m["major_share"] else "-"))

    # ---- predictions and guardrails
    L.append("")
    L.append("  Predictions (registered; '~' support scored within +-%.0f%%, this script's convention):" % (100 * TILDE_BAND))
    for tag in ("A", "B"):
        L.append("   view %s:" % tag)
        L += score(tag, M[tag], diff)
    L.append("")
    L.append("  Guardrails (a 'win' keeps all three):")
    for tag in ("A", "B", "record"):
        lines, g = guardrails(M[tag])
        L.append("   %s: %s" % ("view " + tag if tag != "record" else "record (control)",
                                "WIN" if all(g) else "no (%s)" % ", ".join(n for n, ok in zip(("G1", "G2", "G3"), g) if not ok)))
        L += lines
    L.append("")
    L.append("  Caveats: every tree here is STRUCTURAL EVIDENCE ONLY; purity is label-based (majority train category per view leaf);"
             " F6's LOO removes the scored question from its cell mean, not from the boundaries (F2-CLEAN); the record's split pool"
             " is %s, not the pool of record." % tree["manifest"].get("reserved_pool_id", "?"))

    txt = "\n".join(L)
    print(txt)
    if a.out:
        with open(a.out, "w", encoding="utf-8", newline="\n") as f:
            f.write(txt + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
