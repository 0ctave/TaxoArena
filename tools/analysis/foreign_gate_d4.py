"""FOREIGN-GATE-D4 (FRAMEWORK.md "Tests to register before shipping", item 14; registered by reference at eaf1dbf).

  14. FOREIGN-GATE-D4. Trip rate of the FOREIGN gate at windows 50/100/200 on the D4 artefacts.
      Criterion: trips on the 94%-pure Law regions, not on the Philosophy hosts. 0 calls.

The gate, as the record states it (two forms):
  FRAMEWORK.md L53 : "if fewer than (leaf's own train-side purity minus 2 SD) of a leaf's last 200 arrivals carry a
                     declared cell matching its modal cell, arrivals file to FOREIGN/<leaf_key> ... never inherit the
                     host anchor's name (window and purity form are DESIGN; RESOLVE gives 0.60 as prose, untested)."
  RESOLVE.md  L145 : "share of its recent arrivals whose declared (source, domain) matches the leaf's modal
                     train-side (source, domain). Below 0.60 ... FOREIGN ... never attributed to the host anchor.
                     D4's Law hosts - 90-100% Law under a Philosophy anchor - trip this on the first window."
  FRAMEWORK.md L243: "17. FOREIGN gate. Incident: D4, Law absorbed into Philosophy (94%) and Other (72%) hosts."

Under-specified points and the reading taken (hardest on the programme's own claim; stated again in the output):
  REFERENCE CELL. Both texts compare the arrival's declared cell with the leaf's MODAL TRAIN-SIDE cell (reading B,
    literal). On the D4 artefacts the excluded domain's TRAIN questions are inside the tree (D4 withholds the anchor,
    not the questions), so a 94%-Law leaf's modal train-side cell is Law, Law arrivals MATCH, and the literal gate
    is a drift detector (arrivals vs the leaf's own composition), not a mislabelling detector. The claim "D4's Law
    hosts trip this" needs the reference to be the HOST ANCHOR the leaf reports under (reading A: "source and domain
    read off the leaf's ancestors", FRAMEWORK L53). Both are computed; the literal reading is the item's text and
    is the one scored first. Reading C (the reading most favourable to the programme) takes the leaf's modal cell
    among the arm's REGISTERED cells only - in the design's vocabulary an unregistered domain is not a cell, so the
    excluded domain's train members cannot be the mode; a leaf whose registered mode differs from its anchor is
    still matched against its own mode, not the anchor's name. A train-side check (reading T: leaf's modal train
    cell != its anchor, no arrivals needed) is printed as a diagnostic of what actually separates the D4 regions
    from the hosts.
  THRESHOLD. (R) RESOLVE fixed 0.60; (F) FRAMEWORK purity - 2 SD with purity = the leaf's train-side share in the
    reference cell and SD = sqrt(p(1-p)/w), the binomial SD of the arrival share over a window of w; (F2) the same
    with SD = sqrt(p(1-p)/n_train), the SD of the train-side purity estimate (criterion table and specificity only).
    A purity of 1.0 gives threshold 1.0 (any single foreign arrival trips) - reported, not repaired.
  WINDOW. "last w arrivals", w in {50, 100, 200}. STRICT: a window is evaluated only once w arrivals exist; every
    position t = w..n is a sliding window; trip rate = tripped windows / evaluated windows; "first window" = t = w.
    LENIENT (secondary): if n < w, the single partial window of all n arrivals is evaluated. Arrival order is the
    trickle order of MAIN_routing_diagnostics.txt; 20 seeded permutations give the order sensitivity.
  UNITS. The gate is per leaf (FRAMEWORK) but the criterion names REGIONS; both are read: a region's arrivals are
    the arrivals of its descendant leaves. "The 94%-pure Law regions" = the Law-arm regions with >= 90% Law
    train-side share among the twelve >= 60% regions of d4_outcome.txt (eleven; the Philosophy anchor n00000013
    at 0.94 is one of them). "The Philosophy hosts" is read three ways, all scored, the criterion requiring NO trip
    on any of them: (H1) the depth-1 anchors that host absorbed Philosophy in the Philosophy arm (Other, Psychology,
    Computer science, History; d4_outcome.txt); (H2) the ordinary (non-Philosophy-modal) leaves under those anchors
    - the gate's own unit; (H3) the Law arm's Philosophy-modal leaves under the Philosophy anchor (genuine host
    content). The four 77-81% Philosophy regions are printed beside them.
  DENOMINATOR. Arrivals = the 3,599 held-out (trickle) queries of each arm, routed top-1 to a leaf; train-side
    composition = leaf queryIds -> embeddings_cache.queries.ground_truth_category (memberships, as d4_arrival.py;
    the shared-category hazard is guarded: every member must carry a plain MMLU-Pro category and the recomputed
    region table must equal d4_outcome.txt). No wrong-direction counts exist in this test (no board edge is
    involved), so no McNemar-established count applies; the key denominators are arrivals per node and train
    memberships per node.

Zero calls. Reads: snapshots.db (graphs), embeddings_cache.db (categories), experiment_results/dimsweep4/
d4_outcome.txt and arrive_{law,philosophy}_s137/seed_137/{headless_run.log, validation/MAIN_routing_diagnostics.txt}.
Writes: experiment_results/x12_crossdomain/foreign_gate_d4.txt.

  python tools/analysis/foreign_gate_d4.py
"""
import os, sys, re, json, math, random, sqlite3
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import pool_guard

SWEEP = os.path.join(ROOT, "experiment_results", "dimsweep4")
SNAP_DB = os.path.join(ROOT, "snapshots.db")
EMB_DB = os.path.join(ROOT, "embeddings_cache.db")
OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "foreign_gate_d4.txt")
WINDOWS = (50, 100, 200)
FORMS = ("R", "F", "F2")
READINGS = ("A", "B", "C")   # A host anchor; B modal train cell (literal); C modal REGISTERED train cell
RESOLVE_T = 0.60
PERMS = 20
LAW_PURE = 0.90       # "the 94%-pure Law regions": the >= 90% (rounded, as the record counts them) members of the twelve >= 60% Law regions
REGION_SHARE = 0.60   # d4_arrival.py's region rule
REGION_MIN_N = 20
PHIL_HOSTS = ("Other", "Psychology", "Computer science", "History")   # d4_outcome.txt host anchors of Philosophy
MMLU_DOMAINS = {"math", "physics", "chemistry", "law", "engineering", "other", "economics", "health", "psychology",
                "business", "biology", "philosophy", "computer science", "history"}


def snapshot_id(run_dir):
    ids = re.findall(r"Snapshot ID: (\S+)", open(os.path.join(run_dir, "headless_run.log"), encoding="utf-8", errors="replace").read())
    return ids[-1]


def load_graph(snap_id):
    c = sqlite3.connect("file:%s?mode=ro" % SNAP_DB, uri=True)
    g = json.loads(c.execute("SELECT graph FROM snapshots WHERE id=?", (snap_id,)).fetchone()[0])
    lst = g["nodes"]; lst = lst if isinstance(lst, list) else list(lst.values())
    return {n["id"]: n for n in lst}


def query_categories():
    c = sqlite3.connect("file:%s?mode=ro" % EMB_DB, uri=True)
    return {i: (cat or "").strip().lower() for i, cat in c.execute("SELECT id, ground_truth_category FROM queries")}


def held_out_routes(run_dir):
    """(declared domain, top-1 leaf id) per held-out query, in the file's (trickle) order."""
    out = []; dom = None
    for line in open(os.path.join(run_dir, "validation", "MAIN_routing_diagnostics.txt"), encoding="utf-8", errors="replace"):
        if line.startswith("True Domain:"):
            dom = line.split(":", 1)[1].strip().lower()
        elif line.startswith("Top-1 Leaf:"):
            m = re.search(r"\(ID: (\S+)\)", line)
            out.append((dom, m.group(1) if m else None)); dom = None
    return out


def d4_outcome_regions(tag):
    """(node, n, share) rows of the arm's region table in d4_outcome.txt - the record this test must reproduce."""
    rows = {}; inarm = False
    for line in open(os.path.join(SWEEP, "d4_outcome.txt"), encoding="utf-8"):
        if line.startswith("== D4 "): inarm = tag in line
        m = re.match(r"\s+(n\d+) depth \d+ \S+\s+n=\s*(\d+) share ([\d.]+)", line)
        if inarm and m: rows[m.group(1)] = (int(m.group(2)), float(m.group(3)))
    return rows


class Arm:
    def __init__(self, domain):
        self.domain = domain
        self.tag = "arrive_%s_s137" % domain
        run_dir = os.path.join(SWEEP, self.tag, "seed_137")
        self.snap = snapshot_id(run_dir)
        self.nodes = load_graph(self.snap)
        qcat = query_categories()
        self.parent = {c: n["id"] for n in self.nodes.values() for c in n.get("childIds", [])}
        self.root = [n for n in self.nodes if self.nodes[n]["depth"] == 0][0]
        self.leaves = [n for n in self.nodes if not self.nodes[n].get("childIds")]
        self.anchor_of = {}
        for nid in self.nodes:
            n = self.nodes[nid]
            while n["depth"] > 1: n = self.nodes[self.parent[n["id"]]]
            self.anchor_of[nid] = n["label"].lower() if n["depth"] == 1 else "(root)"
        self._dl = {}
        self.comp = {}
        bad = Counter()
        for nid in self.nodes:
            cnt = Counter()
            for l in self.desc_leaves(nid):
                for q in self.nodes[l].get("queryIds", []):
                    c = qcat.get(q, "?"); cnt[c] += 1
                    if c not in MMLU_DOMAINS: bad[c] += 1
            self.comp[nid] = cnt
        assert not bad, "shared-category hazard: members carry non-MMLU-Pro categories %s" % dict(bad)
        routes = held_out_routes(run_dir)
        assert all(l in self.nodes for _, l in routes), "held-out route to an unknown leaf"
        self.routes = routes
        self.arrivals = defaultdict(list)          # node -> [declared domain] in arrival order
        for d, l in routes:
            n = l
            while True:
                self.arrivals[n].append(d)
                if n == self.root: break
                n = self.parent[n]
        self.anchors = sorted(self.nodes[c]["label"] for c in self.nodes[self.root]["childIds"])
        self.top1_anchor = sum(1 for d, l in routes if self.anchor_of[l] == d) / len(routes)

    def desc_leaves(self, nid):
        if nid in self._dl: return self._dl[nid]
        n = self.nodes[nid]
        r = [nid] if not n.get("childIds") else [l for c in n["childIds"] for l in self.desc_leaves(c)]
        self._dl[nid] = r; return r

    def n_train(self, nid): return sum(self.comp[nid].values())
    def modal(self, nid):
        c = self.comp[nid]; return c.most_common(1)[0][0] if c else "?"
    def share(self, nid, cell): return self.comp[nid][cell] / max(1, self.n_train(nid))
    def modal_registered(self, nid):
        """Modal train-side cell among the arm's REGISTERED cells (anchor names); the excluded domain is not a cell."""
        reg = set(a.lower() for a in self.anchors)
        c = [(k, v) for k, v in self.comp[nid].most_common() if k in reg]
        return c[0][0] if c else "?"
    def reference(self, nid, reading):
        if reading == "A": return self.anchor_of[nid]
        if reading == "C": return self.modal_registered(nid)
        return self.modal(nid)
    def regions(self):
        """d4_arrival.py's candidate regions: non-root nodes with >= 60% excluded-domain share, n >= 20."""
        out = []
        for nid in self.nodes:
            n = self.n_train(nid)
            if self.nodes[nid]["depth"] >= 1 and n >= REGION_MIN_N and self.share(nid, self.domain) >= REGION_SHARE:
                out.append(nid)
        return sorted(out, key=lambda x: -self.n_train(x))


def threshold(form, purity, w, n_train):
    if form == "R": return RESOLVE_T
    if form == "F": return purity - 2.0 * math.sqrt(purity * (1.0 - purity) / w)
    return purity - 2.0 * math.sqrt(purity * (1.0 - purity) / max(1, n_train))


def gate(arr, ref, form, purity, w, n_train, strict=True):
    """Evaluate the sliding gate on an arrival sequence. Returns dict(evaluated, tripped, first, ever, rate, share_end)."""
    n = len(arr); thr = threshold(form, purity, w, n_train)
    match = [1 if d == ref else 0 for d in arr]
    if n < w:
        if strict or n == 0:
            return dict(n=n, evaluated=0, tripped=0, first=None, ever=None, rate=None, thr=thr, share_end=(sum(match) / n if n else None), partial=True)
        s = sum(match) / n
        return dict(n=n, evaluated=1, tripped=int(s < thr), first=int(s < thr), ever=int(s < thr), rate=float(s < thr), thr=thr, share_end=s, partial=True)
    ps = [0]
    for m in match: ps.append(ps[-1] + m)
    ev = 0; tr = 0; first = None
    for t in range(w, n + 1):
        s = (ps[t] - ps[t - w]) / w
        hit = s < thr
        ev += 1; tr += int(hit)
        if first is None: first = int(hit)
    return dict(n=n, evaluated=ev, tripped=tr, first=first, ever=int(tr > 0), rate=tr / ev, thr=thr, share_end=(ps[n] - ps[n - w]) / w, partial=False)


def unit(arm, nid, reading, form, w, strict=True):
    ref = arm.reference(nid, reading); pur = arm.share(nid, ref)
    return gate(arm.arrivals[nid], ref, form, pur, w, arm.n_train(nid), strict), ref, pur


def perm_ever(arm, nid, reading, form, w, seed=137):
    """Order sensitivity: share of PERMS seeded permutations in which the strict gate ever trips."""
    arr = arm.arrivals[nid]
    if len(arr) < w: return None
    ref = arm.reference(nid, reading); pur = arm.share(nid, ref)
    rng = random.Random(seed); hits = 0
    for _ in range(PERMS):
        a = list(arr); rng.shuffle(a)
        hits += gate(a, ref, form, pur, w, arm.n_train(nid))["ever"]
    return hits / PERMS


def fmt(x, p="%.2f"):
    return "n/a" if x is None else (p % x)


def count_trips(arm, units, reading, form, w, strict):
    """(evaluable, tripped) over units; a lenient partial window counts as evaluable."""
    ev = tr = 0
    for l in units:
        g, _, _ = unit(arm, l, reading, form, w, strict)
        if g["evaluated"]: ev += 1; tr += g["ever"]
    return ev, tr


def main():
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)
    lines = []
    def P(s=""):
        print(s); lines.append(s)
    P("FOREIGN-GATE-D4 - trip rate of the FOREIGN gate at windows 50/100/200 on the D4 artefacts (item 14, registered by reference at eaf1dbf)")
    P("pool of record active: %s (analysis addresses the D4 artefacts by explicit snapshot id; the guard is a formality)" % pool_guard.FROZEN_POOL_ID)
    P("gate readings: reference A = host anchor the leaf reports under; B = leaf's modal train-side cell (LITERAL text of FRAMEWORK L53 / RESOLVE L145);")
    P("               C = leaf's modal train-side cell among REGISTERED cells only (the excluded domain is not a cell; most favourable reading);")
    P("               T = train-side check, modal train cell != anchor (no arrivals; diagnostic only)")
    P("thresholds: R = 0.60 fixed (RESOLVE prose); F = purity - 2*sqrt(p(1-p)/w) (FRAMEWORK form; purity = train-side share in the reference cell);")
    P("            F2 = purity - 2*sqrt(p(1-p)/n_train) (criterion table and specificity only)")
    P("windows: STRICT sliding windows of w arrivals (evaluated only once w arrivals exist); LENIENT = one partial window when n < w")
    P("no wrong-direction counts in this test (no board edge); key denominators = held-out arrivals per node (3,599 per arm) and train memberships per node")
    P()
    arms = {d: Arm(d) for d in ("law", "philosophy")}
    stats = {}
    for d, arm in arms.items():
        P("== arm %s | snapshot %s | %d nodes, %d leaves | anchors: %s | held-out arrivals %d (%s: %d) | Top-1 anchor precision %.3f" % (
            arm.tag, arm.snap, len(arm.nodes), len(arm.leaves), ", ".join(arm.anchors), len(arm.routes), d, sum(1 for x, _ in arm.routes if x == d), arm.top1_anchor))
        assert d not in [a.lower() for a in arm.anchors], "excluded domain was anchored"
        cnts = [len(arm.arrivals[l]) for l in arm.leaves]
        stats[d] = dict(max=max(cnts), ge=[sum(c >= w for c in cnts) for w in WINDOWS], nleaves=len(cnts))
        P("   arrivals per leaf: min %d median %d max %d | leaves with >= 50: %d, >= 100: %d, >= 200: %d of %d" % (
            min(cnts), sorted(cnts)[len(cnts) // 2], max(cnts), stats[d]["ge"][0], stats[d]["ge"][1], stats[d]["ge"][2], len(cnts)))
        # consistency with the record (guards the shared-category hazard as well)
        rec = d4_outcome_regions(arm.tag); mine = {r: (arm.n_train(r), round(arm.share(r, d), 2)) for r in arm.regions()}
        assert mine == rec, "region table differs from d4_outcome.txt: %s vs %s" % (mine, rec)
        P("   region table (>= 60%% %s, n >= 20) reproduces d4_outcome.txt exactly: %d regions" % (d, len(rec)))
    P()

    # ---------- the named units ----------
    law = arms["law"]; phi = arms["philosophy"]
    law_regions = law.regions()
    law_pure = [r for r in law_regions if round(law.share(r, "law"), 2) >= LAW_PURE]   # the record rounds: eleven at 90-100%
    P("Law arm: %d regions >= %.0f%% Law (n >= %d), of which %d at >= %.0f%% ('the 94%%-pure Law regions'): %s" % (
        len(law_regions), 100 * REGION_SHARE, REGION_MIN_N, len(law_pure), 100 * LAW_PURE, ", ".join(law_pure)))
    phi_hosts = [c for c in phi.nodes[phi.root]["childIds"] if phi.nodes[c]["label"] in PHIL_HOSTS]
    phi_regions = phi.regions()
    host_ord = [l for c in phi_hosts for l in phi.desc_leaves(c) if phi.modal(l) != "philosophy"]
    law_phil_anchor = [c for c in law.nodes[law.root]["childIds"] if law.nodes[c]["label"] == "Philosophy"][0]
    law_phil_leaves = [l for l in law.desc_leaves(law_phil_anchor) if law.modal(l) == "philosophy"]
    P("Philosophy arm: H1 host anchors of absorbed Philosophy = %s; H2 ordinary leaves under them = %d; Philosophy regions >= 60%% = %s" % (
        ", ".join("%s(%s)" % (phi.nodes[c]["label"], c) for c in phi_hosts), len(host_ord), ", ".join(phi_regions)))
    P("Law arm: Philosophy anchor %s has %d leaves, of which Philosophy-modal (H3, genuine host content): %d %s" % (
        law_phil_anchor, len(law.desc_leaves(law_phil_anchor)), len(law_phil_leaves), law_phil_leaves))
    P()

    def block(title, arm, units):
        P("---- %s ----" % title)
        P("   %-10s %-5s %-6s n_train share_dom train_pur(ref)  | arrivals | per window w: evaluated/tripped rate [first, ever] (perm-ever) thr ; lenient partial-window trip" % ("node", "depth", "kind"))
        for reading in READINGS:
            for form in ("R", "F"):
                P("  reading %s, threshold %s" % (reading, form))
                for nid in units:
                    parts = []
                    for w in WINDOWS:
                        g, ref, pur = unit(arm, nid, reading, form, w, True)
                        gl, _, _ = unit(arm, nid, reading, form, w, False)
                        pe = perm_ever(arm, nid, reading, form, w)
                        if g["evaluated"]:
                            parts.append("w%d: %d/%d %.2f [%d,%d] (%s) thr %.2f" % (w, g["evaluated"], g["tripped"], g["rate"], g["first"], g["ever"], fmt(pe), g["thr"]))
                        else:
                            parts.append("w%d: n=%d<w NOT EVALUABLE; lenient share %s thr %.2f -> %s" % (w, g["n"], fmt(g["share_end"]), g["thr"], "TRIP" if gl["evaluated"] and gl["tripped"] else "no trip"))
                    P("   %-10s %-5d %-6s %7d %9.2f %10.2f (%s) | %8d | %s" % (
                        nid, arm.nodes[nid]["depth"], "leaf" if not arm.nodes[nid].get("childIds") else "split", arm.n_train(nid),
                        arm.share(nid, arm.domain), pur, ref, len(arm.arrivals[nid]), " ; ".join(parts)))
        P()

    block("C1 units: the Law-arm Law regions (>= 60% Law; the >= 90% ones are the criterion's)", law, law_regions)
    block("C2 / H1 units: the Philosophy-arm host anchors of absorbed Philosophy (depth 1)", phi, phi_hosts)
    block("C2 secondary: the Philosophy-arm Philosophy regions (77-81%)", phi, phi_regions)
    if law_phil_leaves:
        block("C2 / H3 units: the Law arm's Philosophy-modal leaves under the Philosophy anchor", law, law_phil_leaves)
    P("---- C2 / H2 units: ordinary (non-Philosophy-modal) leaves under the four Philosophy host anchors, Philosophy arm: %d leaves ----" % len(host_ord))
    for reading in READINGS:
        for form in FORMS:
            row = []
            for w in WINDOWS:
                ev, tr = count_trips(phi, host_ord, reading, form, w, True); le, lt = count_trips(phi, host_ord, reading, form, w, False)
                row.append("w%d strict %d/%d tripped %d, lenient %d/%d" % (w, ev, len(host_ord), tr, lt, le))
            P("   reading %s thr %-2s | %s" % (reading, form, " | ".join(row)))
    P()

    # ---------- criterion table ----------
    P("==== CRITERION TABLE (strict windows; 'trips' = ever trips over the sliding windows; NOT EVALUABLE when n < w) ====")
    P("C1: trips on the %d Law regions at >= %.0f%% Law    C2: does NOT trip on the Philosophy hosts = H1 (%d anchors) + H2 (%d ordinary leaves under them) + H3 (%d leaves)" % (
        len(law_pure), 100 * LAW_PURE, len(phi_hosts), len(host_ord), len(law_phil_leaves)))
    verdicts = {}; table = {}
    for reading in READINGS:
        for form in FORMS:
            for w in WINDOWS:
                c1 = [unit(law, n, reading, form, w)[0] for n in law_pure]
                c1_ev = [g for g in c1 if g["evaluated"]]
                c1_trip = sum(g["ever"] for g in c1_ev); c1_first = sum(g["first"] for g in c1_ev)
                c1_len = [unit(law, n, reading, form, w, False)[0] for n in law_pure]
                c1_len_trip = sum(g["ever"] for g in c1_len if g["evaluated"])
                h1 = count_trips(phi, phi_hosts, reading, form, w, True); h2 = count_trips(phi, host_ord, reading, form, w, True)
                h3 = count_trips(law, law_phil_leaves, reading, form, w, True)
                c2_ev = h1[0] + h2[0] + h3[0]; c2_trip = h1[1] + h2[1] + h3[1]
                if not c1_ev: v = "NOT COMPUTED (no Law region has %d arrivals)" % w
                elif c1_trip == len(c1_ev) and c2_trip == 0 and c2_ev:
                    v = ("PASS" if len(c1_ev) == len(c1) else "PARTIAL") + " on the %d evaluable Law regions" % len(c1_ev) + ("" if len(c1_ev) == len(c1) else " (%d of %d not evaluable)" % (len(c1) - len(c1_ev), len(c1)))
                elif c1_trip == 0: v = "FAIL (gate never trips on a Law region)"
                elif c1_trip < len(c1_ev) and c2_trip: v = "FAIL (trips on %d of %d evaluable Law regions AND on %d hosts)" % (c1_trip, len(c1_ev), c2_trip)
                elif c2_trip: v = "FAIL (trips on %d Philosophy host unit(s): H1 %d/%d, H2 %d/%d, H3 %d/%d)" % (c2_trip, h1[1], h1[0], h2[1], h2[0], h3[1], h3[0])
                else: v = "FAIL (trips on %d of %d evaluable Law regions)" % (c1_trip, len(c1_ev))
                if c1_ev and h2[0] + h3[0] == 0:
                    v += " [C2 has no leaf-level unit with %d arrivals; its count rests on the H1 anchor-level units only]" % w
                verdicts[(reading, form, w)] = v
                table[(reading, form, w)] = dict(c1_ev=len(c1_ev), c1=len(c1), c1_trip=c1_trip, c1_first=c1_first, c1_len=c1_len_trip, h1=h1, h2=h2, h3=h3)
                P("  reading %s thr %-2s w=%3d | C1 evaluable %2d/%2d, ever-trip %2d, first-window trip %2d (lenient incl. partial: %2d/%2d) | C2 H1 %d/%d H2 %d/%d H3 %d/%d tripped/evaluable | %s" % (
                    reading, form, w, len(c1_ev), len(c1), c1_trip, c1_first, c1_len_trip, len(c1), h1[1], h1[0], h2[1], h2[0], h3[1], h3[0], v))
    P()

    # ---------- reading T: the train-side check ----------
    P("==== READING T (diagnostic): leaves whose modal TRAIN-side cell differs from the anchor they report under - needs no arrivals ====")
    tstat = {}
    for d, arm in arms.items():
        dom_leaves = [l for l in arm.leaves if arm.modal(l) == d]; ord_leaves = [l for l in arm.leaves if arm.modal(l) != d]
        dt = sum(1 for l in dom_leaves if arm.modal(l) != arm.anchor_of[l]); ot = sum(1 for l in ord_leaves if arm.modal(l) != arm.anchor_of[l])
        ot_list = Counter((arm.modal(l), arm.anchor_of[l]) for l in ord_leaves if arm.modal(l) != arm.anchor_of[l])
        rt = sum(1 for r in arm.regions() if arm.modal(r) != arm.anchor_of[r] or arm.nodes[r]["depth"] == 1)
        tstat[d] = (dt, len(dom_leaves), ot, len(ord_leaves), rt, len(arm.regions()))
        P("  arm %s: %s-modal leaves flagged %d/%d; ordinary leaves flagged %d/%d %s; regions >= 60%% %s flagged %d/%d (depth-1 anchors count as flagged: their label is the foreign name)" % (
            d, d, dt, len(dom_leaves), ot, len(ord_leaves), dict(ot_list) if ot_list else "", d, rt, len(arm.regions())))
    P()

    # ---------- specificity: all leaves and all anchors, per arm ----------
    P("==== SPECIFICITY: strict ever-trip counts over ALL leaves (and lenient partial-window trips), per arm, by (reading, threshold, window) ====")
    P("  a leaf is 'dominated by the excluded domain' when its modal train-side cell is the arm's excluded domain; 'ordinary' otherwise")
    spec = {}
    for d, arm in arms.items():
        dom_leaves = [l for l in arm.leaves if arm.modal(l) == d]; ord_leaves = [l for l in arm.leaves if arm.modal(l) != d]
        P("  arm %s: %d leaves = %d %s-modal + %d ordinary" % (d, len(arm.leaves), len(dom_leaves), d, len(ord_leaves)))
        for reading in READINGS:
            for form in FORMS:
                for w in WINDOWS:
                    de, dt = count_trips(arm, dom_leaves, reading, form, w, True); oe, ot = count_trips(arm, ord_leaves, reading, form, w, True)
                    dle, dlt = count_trips(arm, dom_leaves, reading, form, w, False); ole, olt = count_trips(arm, ord_leaves, reading, form, w, False)
                    spec[(d, reading, form, w)] = (de, dt, oe, ot)
                    P("    reading %s thr %-2s w=%3d | %s-modal leaves: strict tripped %d/%d evaluable ; lenient tripped %d/%d | ordinary leaves: strict tripped %d/%d evaluable ; lenient tripped %d/%d" % (
                        reading, form, w, d, dt, de, dlt, dle, ot, oe, olt, ole))
        P("  arm %s depth-1 anchors (train n, %s share, own-name train purity, arrivals): %s" % (d, d, "; ".join(
            "%s n=%d %.2f pur=%.2f arr=%d" % (arm.nodes[c]["label"], arm.n_train(c), arm.share(c, d), arm.share(c, arm.anchor_of[c]), len(arm.arrivals[c])) for c in arm.nodes[arm.root]["childIds"])))
        for reading in READINGS:
            for form in FORMS:
                row = []
                for w in WINDOWS:
                    trips = [arm.nodes[c]["label"] for c in arm.nodes[arm.root]["childIds"] if unit(arm, c, reading, form, w)[0]["ever"]]
                    spec[(d, reading, form, w, "anchors")] = len(trips)
                    row.append("w%d: %s" % (w, ", ".join(trips) if trips else "none"))
                P("    anchors tripping (strict, ever) reading %s thr %-2s | %s" % (reading, form, " | ".join(row)))
    P()

    # ---------- what the anchor-referenced gate quarantines (the cost of reading A) ----------
    P("==== READING A COST: share of ALL held-out arrivals that would be filed FOREIGN (arrival counted FOREIGN once its leaf has tripped, strict), per arm ====")
    cost = {}
    for d, arm in arms.items():
        for form in FORMS:
            for w in WINDOWS:
                filed = 0; filed_dom = 0; tripped = set(); counts = defaultdict(list)
                for dd, l in arm.routes:
                    counts[l].append(dd)
                    ref = arm.reference(l, "A"); pur = arm.share(l, ref); arr = counts[l]
                    if l not in tripped and len(arr) >= w:
                        s = sum(1 for x in arr[-w:] if x == ref) / w
                        if s < threshold(form, pur, w, arm.n_train(l)): tripped.add(l)
                    if l in tripped:
                        filed += 1; filed_dom += int(dd == d)
                ndom = sum(1 for x, _ in arm.routes if x == d)
                cost[(d, form, w)] = (len(tripped), filed, filed_dom, ndom)
                P("  arm %s thr %-2s w=%3d | leaves tripped %2d/%d | arrivals filed FOREIGN after the trip: %4d/%d (%.1f%%), of which %s: %d/%d" % (
                    d, form, w, len(tripped), len(arm.leaves), filed, len(arm.routes), 100 * filed / len(arm.routes), d, filed_dom, ndom))
    P()

    # ---------- interpretation, generated from the computed figures ----------
    lw, pw = stats["law"], stats["philosophy"]
    P("==== INTERPRETATION ====")
    P("1. WINDOW. The largest leaf arrival count is %d (Law arm) / %d (Philosophy arm); leaves with >= 50/100/200 arrivals: %d/%d/%d of %d and %d/%d/%d of %d." % (
        lw["max"], pw["max"], lw["ge"][0], lw["ge"][1], lw["ge"][2], lw["nleaves"], pw["ge"][0], pw["ge"][1], pw["ge"][2], pw["nleaves"]))
    P("   The FRAMEWORK gate's 'last 200 arrivals' is %s at leaf level on the D4 artefacts; Law regions with 200 arrivals: %d of %d." % (
        "never evaluable" if lw["ge"][2] == 0 and pw["ge"][2] == 0 else "evaluable on %d + %d leaves" % (lw["ge"][2], pw["ge"][2]),
        sum(1 for r in law_pure if len(law.arrivals[r]) >= 200), len(law_pure)))
    shares_B = [unit(law, r, "B", "R", 50, False)[0]["share_end"] for r in law_pure]
    tB = table[("B", "R", 50)]; tBF = table[("B", "F", 50)]
    P("2. LITERAL GATE (reading B: declared cell vs the leaf's modal TRAIN-side cell). The Law regions' modal train cell IS Law, so Law arrivals")
    P("   match (arrival Law share %.2f-%.2f over the 11 regions): at 0.60 the gate trips on %d of %d evaluable Law regions at w=50 and %d of %d at w=100." % (
        min(shares_B), max(shares_B), tB["c1_trip"], tB["c1_ev"], table[("B", "R", 100)]["c1_trip"], table[("B", "R", 100)]["c1_ev"]))
    bf = [(r, unit(law, r, "B", "F", 50)[0], perm_ever(law, r, "B", "F", 50)) for r in law_pure]
    bf_trips = [(r, g, pe) for r, g, pe in bf if g["evaluated"] and g["ever"]]
    P("   Under purity - 2 SD it trips on %d of %d evaluable regions at w=50: %s - trips by sampling noise against a threshold at or near the" % (
        len(bf_trips), tBF["c1_ev"], "; ".join("%s (train purity %.2f, thr %.2f, %.0f%% of windows, perm-ever %.2f)" % (r, law.share(r, "law"), g["thr"], 100 * g["rate"], pe) for r, g, pe in bf_trips) or "none"))
    P("   train purity, not by mislabelling. As written the gate is a drift detector and cannot be the 'fix for D4' (RESOLVE L145): D4's failure is")
    P("   train-side content that disagrees with the anchor name, and reading T finds it with no arrivals at all (%d/%d Law-modal leaves, %d/%d Law regions;" % (
        tstat["law"][0], tstat["law"][1], tstat["law"][4], tstat["law"][5]))
    P("   false flags on ordinary leaves: %d/%d Law arm, %d/%d Philosophy arm)." % (tstat["law"][2], tstat["law"][3], tstat["philosophy"][2], tstat["philosophy"][3]))
    tA50, tA100 = table[("A", "R", 50)], table[("A", "R", 100)]
    hosts_trip = [phi.nodes[c]["label"] + " %.2f" % phi.share(c, phi.anchor_of[c]) for c in phi_hosts if unit(phi, c, "A", "R", 50)[0]["ever"]]
    P("3. ANCHOR-REFERENCED GATE (reading A: declared cell vs the host anchor's name), 0.60 fixed: trips on %d/%d evaluable Law regions at w=50 and %d/%d at w=100," % (
        tA50["c1_trip"], tA50["c1_ev"], tA100["c1_trip"], tA100["c1_ev"]))
    P("   first-window trips %d/%d and %d/%d - the RESOLVE claim holds there. But it also trips %d of the %d Philosophy host anchors at w=50 (%s own-name train purity)," % (
        tA50["c1_first"], tA50["c1_ev"], tA100["c1_first"], tA100["c1_ev"], tA50["h1"][1], tA50["h1"][0], ", ".join(hosts_trip)))
    P("   %d/%d evaluable ordinary leaves under them, %d/%d (Law arm) and %d/%d (Philosophy arm) evaluable ORDINARY leaves overall at w=50, and %d / %d depth-1 anchors per arm:" % (
        tA50["h2"][1], tA50["h2"][0], spec[("law", "A", "R", 50)][3], spec[("law", "A", "R", 50)][2], spec[("philosophy", "A", "R", 50)][3], spec[("philosophy", "A", "R", 50)][2],
        spec[("law", "A", "R", 50, "anchors")], spec[("philosophy", "A", "R", 50, "anchors")]))
    P("   the tree's own routing precision (Top-1 anchor %.2f / %.2f) sits under 0.60 routinely, so a fixed 0.60 is not specific to a takeover." % (law.top1_anchor, phi.top1_anchor))
    P("   With purity - 2 SD (F: %d/%d, F2: %d/%d Law regions at w=50) reading A does not trip on the Law regions, because the train-side share in the anchor's cell" % (
        table[("A", "F", 50)]["c1_trip"], table[("A", "F", 50)]["c1_ev"], table[("A", "F2", 50)]["c1_trip"], table[("A", "F2", 50)]["c1_ev"]))
    P("   is already %.2f-%.2f there and the threshold falls to or below 0." % (min(law.share(r, law.anchor_of[r]) for r in law_pure), max(law.share(r, law.anchor_of[r]) for r in law_pure)))
    P("   Cost at leaf level (the gate's own unit): in the Law arm %d of %d held-out Law arrivals are filed FOREIGN at w=50 and %d at w=100 under 0.60, because" % (
        cost[("law", "R", 50)][2], cost[("law", "R", 50)][3], cost[("law", "R", 100)][2]))
    P("   most Law leaves never reach w arrivals inside the 3,599-query trickle; %.0f-100%% of held-out Law stays attributed to its host at every window." % (
        100 * (1 - cost[("law", "R", 50)][2] / cost[("law", "R", 50)][3])))
    tC50, tCF50 = table[("C", "R", 50)], table[("C", "F", 50)]
    P("3b. REGISTERED-MODAL GATE (reading C, the reading most favourable to the programme: the excluded domain is not a cell, so the Law regions'")
    P("   reference is their small registered remainder, %.2f-%.2f train share): at 0.60 it trips on %d/%d evaluable Law regions at w=50 (first window %d/%d) and %d/%d at w=100," % (
        min(law.share(r, law.modal_registered(r)) for r in law_pure), max(law.share(r, law.modal_registered(r)) for r in law_pure),
        tC50["c1_trip"], tC50["c1_ev"], tC50["c1_first"], tC50["c1_ev"], table[("C", "R", 100)]["c1_trip"], table[("C", "R", 100)]["c1_ev"]))
    P("   but still on H1 %d/%d, H2 %d/%d host units (an ordinary leaf whose own registered mode is under 0.60 of its arrivals trips regardless of reference)," % (
        tC50["h1"][1], tC50["h1"][0], tC50["h2"][1], tC50["h2"][0]))
    P("   %d/%d (Law arm) and %d/%d (Philosophy arm) evaluable ordinary leaves at w=50; under purity - 2 SD it trips on %d/%d Law regions (threshold at or below 0 again)." % (
        spec[("law", "C", "R", 50)][3], spec[("law", "C", "R", 50)][2], spec[("philosophy", "C", "R", 50)][3], spec[("philosophy", "C", "R", 50)][2], tCF50["c1_trip"], tCF50["c1_ev"]))
    both = [k for k, v in verdicts.items() if v.startswith("PASS") or v.startswith("PARTIAL")]
    P("4. %s (reading, threshold, window) combination satisfies both halves of the criterion%s. The two halves pull apart: the reference that makes" % (
        "No" if not both else "%d" % len(both), "" if not both else ": " + ", ".join("%s/%s/w%d" % k for k in both)))
    P("   the Law regions trip (the anchor's name) is the one on which ordinary leaves also fall under 0.60, and the threshold form that spares ordinary")
    P("   leaves (purity - 2 SD in the reference cell) is zero on the Law regions. What separates D4's regions from the hosts is the train-side")
    P("   disagreement between a leaf's modal declared cell and its anchor (reading T), which is a build-time property and not a property of any arrival window.")
    P()
    P("==== TRIP RATE (headline): leaves that ever trip / leaves with >= w arrivals (strict), and lenient partial-window trips / all leaves, per arm ====")
    for d, arm in arms.items():
        for reading in READINGS:
            for form in FORMS:
                row = []
                for w in WINDOWS:
                    de, dt, oe, ot = spec[(d, reading, form, w)]
                    le, lt = count_trips(arm, arm.leaves, reading, form, w, False)
                    row.append("w%d strict %d/%d (%s) lenient %d/%d (%.2f)" % (w, dt + ot, de + oe, fmt((dt + ot) / (de + oe)) if de + oe else "n/a", lt, le, lt / max(1, le)))
                P("  arm %-10s reading %s thr %-2s | %s" % (d, reading, form, " | ".join(row)))
    P()
    P("==== VERDICT ====")
    for reading, name in (("B", "Literal gate (reading B, modal train-side cell)"), ("A", "Anchor-referenced gate (reading A, host anchor's cell)"),
                          ("C", "Registered-modal gate (reading C, modal registered train-side cell)")):
        for f, fname in (("R", "0.60 fixed"), ("F", "purity - 2 SD, SD over the window"), ("F2", "purity - 2 SD, SD over n_train")):
            P("%s, %s: %s" % (name, fname, " ; ".join("w%d %s" % (w, verdicts[(reading, f, w)]) for w in WINDOWS)))
    w50 = [verdicts[k] for k in verdicts if k[2] == 50]; w100 = [verdicts[k] for k in verdicts if k[2] == 100]; w200 = [verdicts[k] for k in verdicts if k[2] == 200]
    def summ(vs):
        if all(v.startswith("NOT COMPUTED") for v in vs): return "NOT COMPUTED"
        if any(v.startswith("PASS") for v in vs): return "PASS under some reading"
        if any(v.startswith("PARTIAL") for v in vs): return "PARTIAL under some reading"
        return "FAIL under every reading"
    P("OVERALL: w=50 %s; w=100 %s; w=200 %s." % (summ(w50), summ(w100), summ(w200)))
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("written", OUT)


if __name__ == "__main__":
    main()
