"""K-SELECTION readout (docs/judge_v2_program.md, "Registered 2026-09-19 (before any code or call) - K-SELECTION",
programme L8224-L8390, commit 8fde7fa; the pre-build naming bracket L8765 fixes the file names below; plan
docs/agents/plans/2026-09-18_reframing_and_next.md S2 R2 / S5). ZERO LLM calls; nothing here reads the pool while an
arm builds (the chain calls --run after the last arm); every DB is opened read-only through anchor_free_redraw /
anchor_free_readout (snapshots.db mode=ro&immutable=1; embeddings_cache.db and mmlu_pro_dataset_cache_v2.db mode=ro).

QUESTION (registration). Is the quantitative depth-1 site's 3-of-4 certification (ANCHOR-FREE-REDRAW: R1 accepted k = 2
at 1.006x the bar and was uncertified at 0.746) the greedy first-k-that-passes rule's or the corpus's?  The arms rebuild
R1 / R2 / R3 with EXACTLY ONE added key, proposalAcceptMultiplier = 1.05 (creation-side hysteresis; merged 967a936).

ARMS (experiment_results/anchorfree/redraw/kselect/; the naming bracket L8765):
  R1'  af_clean_s42_k105/seed_42    twin R1 af_clean_s42 (pool of record by reservedPoolFile; the only clean arm)
  R2'  af_s137_k105/seed_137        twin R2 af_s137      (own pool pd610c9ad05255f16; purity is in-sample, identity only)
  R3'  af_s2048_k105/seed_2048      twin R3 af_s2048     (own pool p19d9f473b5a610a0; idem)
  I2   i2/seed_42                   the inertness build (key ABSENT); its verdict is k_selection_inert.py's i2_inertness.txt
Inputs per primed arm: <arm>/seed_<seed>/{dag_snapshots.jsonl, headless_run.log, diagnostics/run_manifest.json,
  diagnostics/proposals.csv}, site_null_<arm>.csv (reps == 300, snapshot_id == the build's; anything else = UNDETERMINED),
  anchor_free_<arm>_readout.txt (anchor_free_readout.py vs af/seed_42), <arm>.build.out (the chain's build log: the
  [K-SELECTION] warn line and the [NO-SPLIT] lines carrying bar_eff=).  The unprimed twins are read from
  experiment_results/anchorfree/redraw/ exactly as ANCHOR-FREE-REDRAW read them (loaders and the identity rule imported
  from anchor_free_redraw.py unchanged; its one edit: REASON_RE accepts the primed rows' `,bar_eff=` group).
  I1 = the suite line of experiment_results/suite_2026-09-19.log ("suite: tests N failures F errors E") or --suite-line.

WHAT IS PRINTED, per arm and for the sweep (exactly the registration's C0-C3 / P1-P10 numbers):
  C0  I1 (suite; failures 0, errors 0, tests >= 424) and I2 (i2_inertness.txt: INERT).  If C0 is not HELD nothing
      primed is read as a verdict (everything is still printed, labelled).
  C1  the arm's depth-1 site with the BEST Jaccard to the record's n00000004 over ALL depth-1 sites on the shared train
      texts (the naming bracket's matching rule; the certified-only reading of REDRAW's site_identity printed beside):
      n, accepted k (the last ACCEPTED GROW row's dV in proposals.csv, cross-checked against the snapshot's childIds),
      joint sepScore / bar, the min-pair EXACT at k = 2 (min-pair == joint) or the INTERVAL [1.05 x bar, joint / bar] at
      k > 2 (the engine records the accepted min-pair only when it fails), every refused-k row at the site (sep, bar,
      bar_eff, k, emK, iterations; a row with bar <= sep < bar_eff is "refused by the rule only"), observed_sep, p95,
      margin = observed / p95, certified.  C1 HELD per arm iff certified; sweep HELD iff every built arm HELD (3 of 3).
  C2  n00000005's match (same rule) and the root: certified in every arm; margins printed against the recorded bands
      (discursive 2.10-2.13, root 1.12-1.14; outside by more than the null's draw spread 0.02 = printed as a CHANGE,
      C2 still HELD if certified).
  C3  the RE-DRAW-STABLE certified set over R1' / R2' / R3' (record certified sites reproducing in all three at
      Jaccard >= 0.5, one-to-one greedy on shared train texts: REDRAW's rule): CONTAINS the record's five (n00000001,
      n00000005, n00000017, n00000016, n00000032) -> HELD.
  P1  R1' quantitative site accepted k = 3 and margin observed / p95 in [1.6, 1.8].  P2 discursive and root margins in
      the bands in every arm.  P3 the stable set is 6 and adds n00000004.  P4 certified count per arm within +-2 of the
      twin's (R1 14 of 69, R2 12 of 64, R3 10 of 66, read from the REDRAW CSVs and asserted).  P5 readout purity per arm
      within 1 pp of the twin's (0.727 / 0.738 / 0.749; R2' / R3' in-sample, overlap printed).  P6 I2 INERT.  P7 the
      rule-only refusals (NO_PROPOSAL rows with bar <= sep < bar_eff, every site, every iteration) 1-4 per arm; distinct
      (site, k, emK, sep) and the build.out line counts beside.  P8 twin leaves reproduced in the arm at Jaccard >= 0.9
      (one-to-one greedy on shared train texts) >= 70; the twin's certified sites reproduced in the arm at >= 0.5 as a
      table.  P9 R1' leaves in [78, 88].  P10 n00000043 NOT in the stable set (its best Jaccard per arm printed).
  mu-match of the record's 81 leaves at cos >= 0.95 per arm (no band registered; printed).
SCORING: HELD / FAILED / UNDETERMINED explicitly; an arm without a completed build or without a 300-rep site null is
  UNDETERMINED, the denominator is reduced and named.  The VERDICT RULE sentence is written only when C0, C1, C2 and C3
  are all HELD on the full denominator (3 of 3 arms built).  Every tree here is STRUCTURAL EVIDENCE ONLY.
OUTCOME: experiment_results/anchorfree/redraw/kselect/k_selection_outcome.txt, WRITE-ONCE (--run refuses if it exists).

Launch sequence (the run-operator; every step zero calls):
  python tools/analysis/k_selection_readout.py --selftest     # scratch stand-ins built from the REDRAW arms (R1 as a fake
                                                              # primed arm with fabricated bar_eff rows), the whole readout
                                                              # asserted; writes only under the scratch dir
  python tools/analysis/k_selection_readout.py --dry-run      # pool id first; inputs per arm present / ABSENT; exit 0
  python tools/analysis/k_selection_readout.py --run [--suite-line "suite: tests 434 failures 0 errors 0 []"]
      --undetermined <arm>   declare an arm that the chain never reached (otherwise --run refuses on an ABSENT arm)
"""
import os, sys, re, csv, json, glob, shutil, argparse
from collections import defaultdict, Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
import pool_guard                                   # noqa: E402
import anchor_free_redraw as afd                    # noqa: E402  loaders (read_site_null, load_graph, members, analyse_tree), site_identity, REASON_RE

POOL = afd.POOL
REDRAW = afd.REDRAW
KS = os.path.join(REDRAW, "kselect")
SUITE_LOG = os.path.join(ROOT, "experiment_results", "suite_2026-09-19.log")
MULT = 1.05
BAR = afd.BAR
JACCARD = afd.JACCARD           # 0.5, the REDRAW identity rule
LEAF_J = 0.9                    # P8
SUITE_MIN_TESTS = 424           # the suite at registration (424; 434 after the flag's 10 tests)
REC_ROOT, REC_Q, REC_D, REC_43 = "n00000001", "n00000004", "n00000005", "n00000043"
REC_FIVE = ("n00000001", "n00000005", "n00000017", "n00000016", "n00000032")
BAND_DISC, BAND_ROOT, DRAW_SPREAD = (2.10, 2.13), (1.12, 1.14), 0.02
P1_BAND, P7_BAND, P9_BAND = (1.6, 1.8), (1, 4), (78, 88)

ARMS = [
    dict(arm="af_clean_s42_k105", tag="R1'", seed=42, twin="af_clean_s42", twin_tag="R1", clean=True, twin_cert=(14, 69), twin_purity=0.727, twin_repro=7),
    dict(arm="af_s137_k105", tag="R2'", seed=137, twin="af_s137", twin_tag="R2", clean=False, twin_cert=(12, 64), twin_purity=0.738, twin_repro=8),
    dict(arm="af_s2048_k105", tag="R3'", seed=2048, twin="af_s2048", twin_tag="R3", clean=False, twin_cert=(10, 66), twin_purity=0.749, twin_repro=8),
]
I2 = dict(arm="i2", tag="I2", seed=42, twin="af_clean_s42")


def rel(p):
    try:
        return os.path.relpath(p, ROOT).replace("\\", "/")
    except ValueError:                       # another drive (the selftest's scratch root)
        return p.replace("\\", "/")


def V(ok):
    if ok == "printed":
        return "PRINTED"
    return "UNDETERMINED" if ok is None else ("HELD" if ok else "FAILED")


def in_range(x, lo, hi):
    return x is not None and lo <= x <= hi


# ----------------------------------------------------------------------------------------------- paths and states
def arm_paths(a, ks=None):
    ks = ks or KS
    run_dir = os.path.join(ks, a["arm"], "seed_%d" % a["seed"])
    return dict(run_dir=run_dir,
                manifest=os.path.join(run_dir, "diagnostics", "run_manifest.json"),
                proposals=os.path.join(run_dir, "diagnostics", "proposals.csv"),
                log=os.path.join(run_dir, "headless_run.log"),
                jsonl=os.path.join(run_dir, "dag_snapshots.jsonl"),
                csv=os.path.join(ks, "site_null_%s.csv" % a["arm"]),
                readout=os.path.join(ks, "anchor_free_%s_readout.txt" % a["arm"]),
                build_out=os.path.join(ks, "%s.build.out" % a["arm"]),
                twin_dir=os.path.join(REDRAW, a["twin"], "seed_%d" % a["seed"]),
                twin_csv=os.path.join(REDRAW, "site_null_%s.csv" % a["twin"]),
                twin_readout=os.path.join(REDRAW, "anchor_free_%s_readout.txt" % a["twin"]))


def i2_paths(ks=None):
    ks = ks or KS
    return dict(run_dir=os.path.join(ks, I2["arm"], "seed_%d" % I2["seed"]), verdict=os.path.join(ks, "i2_inertness.txt"),
                build_out=os.path.join(ks, "%s.build.out" % I2["arm"]), manifest=os.path.join(ks, I2["arm"], "seed_%d" % I2["seed"], "diagnostics", "run_manifest.json"))


def arm_state(a, p, declared=()):
    """('ABSENT' | 'UNDETERMINED' | 'READY', why).  ABSENT = the chain never reached the arm (refused by --run unless
    declared --undetermined); UNDETERMINED = a build that did not complete, or no 300-rep site null / readout."""
    if a["arm"] in declared:
        return "UNDETERMINED", "declared --undetermined by the operator"
    if not os.path.isdir(p["run_dir"]) and not os.path.exists(p["build_out"]):
        return "ABSENT", "no run dir and no %s (the chain has not reached this arm)" % os.path.basename(p["build_out"])
    if not os.path.exists(p["manifest"]):
        return "UNDETERMINED", "no diagnostics/run_manifest.json (the build did not complete)"
    m = json.load(open(p["manifest"], encoding="utf-8"))
    if m.get("exit_reason") != "completed":
        return "UNDETERMINED", "manifest exit_reason=%r" % m.get("exit_reason")
    if m.get("proposal_accept_multiplier") != MULT:
        return "UNDETERMINED", "manifest proposal_accept_multiplier=%r, the registered primed arm carries %.2f" % (m.get("proposal_accept_multiplier"), MULT)
    if not os.path.exists(p["jsonl"]) or not os.path.exists(p["log"]):
        return "UNDETERMINED", "dag_snapshots.jsonl / headless_run.log missing"
    sid = afd.snapshot_id_from_log(p["log"])
    if sid is None:
        return "UNDETERMINED", "no 'Snapshot ID:' in headless_run.log (no snapshot saved)"
    if not os.path.exists(p["csv"]):
        return "UNDETERMINED", "no site null %s (a null not complete at %d reps is never read)" % (rel(p["csv"]), afd.REPS)
    try:
        sn = afd.read_site_null(p["csv"])
    except SystemExit as e:
        return "UNDETERMINED", "site null refused: %s" % e
    if sn["snapshot"] != sid:
        return "UNDETERMINED", "site null on snapshot %s, the build log says %s" % (sn["snapshot"], sid)
    if not os.path.exists(p["readout"]):
        return "UNDETERMINED", "no %s (anchor_free_readout.py did not run)" % rel(p["readout"])
    for k in ("twin_dir", "twin_csv"):
        if not os.path.exists(p[k]):
            raise SystemExit("[KSEL] %s: the unprimed twin input %s is missing (the REDRAW arm of record)" % (a["tag"], rel(p[k])))
    return "READY", "manifest completed (multiplier %.2f), snapshot %s, site null %d sites at %d reps (%d certified), readout present" % (MULT, sid, sn["sites"], afd.REPS, len(sn["cert"]))


# ----------------------------------------------------------------------------------------------- C0 inputs
def suite_state(line_arg=None, path=SUITE_LOG):
    """('HELD'|'FAILED'|'UNDETERMINED', the line, the source)."""
    if line_arg:
        line, src = line_arg.strip(), "--suite-line"
    elif os.path.exists(path):
        lines = [l.rstrip("\n") for l in open(path, encoding="utf-8", errors="replace") if l.startswith("suite:")]
        if not lines:
            return None, "(no 'suite:' line in %s)" % rel(path), rel(path)
        line, src = lines[-1], rel(path)
    else:
        return None, "(%s absent)" % rel(path), rel(path)
    m = re.search(r"suite:\s*tests\s+(\d+)\s+failures\s+(\d+)\s+errors\s+(\d+)", line)
    if not m:
        return None, line + "  (unparsed)", src
    n, f, e = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return (f == 0 and e == 0 and n >= SUITE_MIN_TESTS), line, src


def i2_state(path):
    """('HELD'|'FAILED'|None, verdict line, extra lines)."""
    if not os.path.exists(path):
        return None, "(absent: %s)" % rel(path), []
    lines = [l.rstrip("\n") for l in open(path, encoding="utf-8", errors="replace")]
    vl = [l for l in lines if l.startswith("I2 INERTNESS VERDICT:")]
    extra = [l for l in lines if l.startswith("I2 run_manifest.json proposal_accept_multiplier") or l.startswith("leaves") or "leaf member sets" in l or l.startswith("R1 site null")]
    if not vl:
        return None, "(no 'I2 INERTNESS VERDICT:' line in %s)" % rel(path), extra
    v = vl[-1]
    ok = True if re.search(r"VERDICT:\s*INERT\b", v) else (False if "NOT INERT" in v else None)
    return ok, v, extra


# ----------------------------------------------------------------------------------------------- proposals.csv readers
def accepted_grow(proposals_path):
    """site -> [(iter, dV)] of ACCEPTED GROW rows (dV = the accepted k)."""
    acc = defaultdict(list)
    with open(proposals_path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["decision"] == "ACCEPTED" and r["type"] == "GROW":
                acc[r["site_id"]].append((int(r["iter"]), int(float(r["dV"]))))
    return acc


def rule_only_refusals(proposals_path):
    """Every NO_PROPOSAL min-pair row (all sites, all iterations) parsed with anchor_free_redraw.REASON_RE.
    Returns (rows_in_band, n_rows_with_bar_eff, n_minpair_rows, distinct_in_band) where in band = bar <= sep < bar_eff."""
    band, n_eff, n_mp = [], 0, 0
    with open(proposals_path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["decision"] != "NO_PROPOSAL":
                continue
            m = afd.REASON_RE.search(r["reason"] or "")
            if not m:
                continue
            n_mp += 1
            sep, bar, be, k, emk = float(m.group(1)), float(m.group(2)), m.group(3), int(m.group(4)), int(m.group(5))
            if be is None:
                continue
            n_eff += 1
            be = float(be)
            if bar <= sep < be:
                band.append(dict(site=r["site_id"], label=r["site_label"], iter=int(r["iter"]), sep=sep, bar=bar, bar_eff=be, k=k, emK=emk, n=int(r["n_site"] or 0)))
    distinct = {(x["site"], x["k"], x["emK"], x["sep"]) for x in band}
    return band, n_eff, n_mp, len(distinct)


def build_out_counts(path):
    if not os.path.exists(path):
        return None
    ks = be = 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for l in f:
            ks += "[K-SELECTION]" in l
            be += "bar_eff=" in l
    return dict(kselection=ks, bar_eff=be)


# ----------------------------------------------------------------------------------------------- matching rules
def jacc(A, B):
    u = len(A | B)
    return (len(A & B) / u) if u else 0.0


def d1_match(rec, blk, rec_site):
    """The naming bracket's C1 rule: the arm's depth-1 site with the best Jaccard to the record site over ALL depth-1
    sites on the shared train texts; REDRAW's certified-only reading (site_identity) beside."""
    shared = rec["all_members"] & blk["all_members"]
    S = rec["members"][rec_site] & shared
    rows = []
    for t in blk["d1"]:
        tr = next(x for x in blk["trunk"] if x["id"] == t)
        rows.append(dict(site=t, label=blk["graph"]["byid"][t]["label"], j=jacc(S, blk["members"][t] & shared), n=len(blk["members"][t]),
                         cert=tr["cert"], observed=tr["observed"], p95=tr["p95"], margin=tr["margin"], in_csv=tr["in_csv"]))
    rows.sort(key=lambda r: (-r["j"], r["site"]))
    best = rows[0] if rows else None
    tie = len(rows) > 1 and abs(rows[0]["j"] - rows[1]["j"]) < 1e-9
    cert_only = blk["identity"]["match"].get(rec_site)            # (arm site, J) or None
    cert_best = blk["identity"]["best"][rec_site]                 # (J, arm site)
    return dict(rec_site=rec_site, best=best, rows=rows, tie=tie, cert_only=cert_only, cert_best=cert_best, shared=len(shared))


def leaf_sets(blk):
    g = blk["graph"]["byid"]
    return {i: blk["members"][i] for i, n in g.items() if not (n.get("childIds") or [])}


def leaf_identity(twin, arm):
    """P8: twin leaves reproduced in the arm at Jaccard >= 0.9 on shared train texts, one-to-one greedy by Jaccard."""
    shared = twin["all_members"] & arm["all_members"]
    TL, AL = leaf_sets(twin), leaf_sets(arm)
    pairs = []
    for s, S in TL.items():
        S = S & shared
        for t, T in AL.items():
            pairs.append((jacc(S, T & shared), s, t))
    pairs.sort(key=lambda x: (-x[0], x[1], x[2]))
    used_s, used_t, match = set(), set(), {}
    for j, s, t in pairs:
        if j <= 0.0:
            break
        if s in used_s or t in used_t:
            continue
        match[s] = (t, j); used_s.add(s); used_t.add(t)
    js = sorted((j for _, j in match.values()), reverse=True)
    hist = Counter("1.00" if j >= 1.0 - 1e-12 else "[0.9,1)" if j >= LEAF_J else "[0.5,0.9)" if j >= 0.5 else "<0.5" for j in js)
    return dict(twin_leaves=len(TL), arm_leaves=len(AL), matched=len(match), at_09=sum(1 for j in js if j >= LEAF_J), shared=len(shared),
                hist=dict(hist), median=(js[len(js) // 2] if js else 0.0), match=match)


# ----------------------------------------------------------------------------------------------- one arm
def analyse_arm(a, p, ctx, rec):
    blk = afd.analyse_tree(a["arm"], p["run_dir"], p["csv"], ctx, record=rec, readout_path=p["readout"])
    blk["record_rows"] = rec["record_rows"]
    twin = afd.analyse_tree(a["twin"], p["twin_dir"], p["twin_csv"], ctx, record=rec,
                            readout_path=p["twin_readout"] if os.path.exists(p["twin_readout"]) else None)
    twin["record_rows"] = rec["record_rows"]
    if (twin["cert"], twin["sites"]) != a["twin_cert"]:
        raise SystemExit("[KSEL] %s: the unprimed twin %s reads %d of %d certified; ANCHOR-FREE-REDRAW recorded %d of %d (the loaders changed?)"
                         % (a["tag"], a["twin"], twin["cert"], twin["sites"], a["twin_cert"][0], a["twin_cert"][1]))
    if twin["identity"]["reproduced"] != a["twin_repro"]:
        raise SystemExit("[KSEL] %s: the unprimed twin %s reproduces %d of 16 record sites; REDRAW recorded %d (the identity rule changed?)"
                         % (a["tag"], a["twin"], twin["identity"]["reproduced"], a["twin_repro"]))
    acc = accepted_grow(p["proposals"])
    q = d1_match(rec, blk, REC_Q)
    d = d1_match(rec, blk, REC_D)
    for m in (q, d):
        if m["best"] is not None:
            s = m["best"]["site"]
            e = blk["exist"][s]
            last = max(acc.get(s, []), key=lambda x: x[0], default=None)
            m["exist"] = e
            m["accepted"] = last                                     # (iter, dV)
            m["k_snapshot"] = e["k"]
            m["k_consistent"] = (last is None and e["k"] == 0) or (last is not None and last[1] == e["k"])
            if e["k"] == 2:
                m["minpair"] = ("EXACT", e["joint"] / BAR, e["joint"] / BAR)
            elif e["k"] > 2:
                m["minpair"] = ("INTERVAL", MULT, e["joint"] / BAR)
            else:
                m["minpair"] = ("LEAF", None, None)
            m["rule_only_here"] = [r for r in e["refused"] if r.get("bar_eff") is not None and r["bar"] <= r["sep"] < r["bar_eff"]]
    root_tr = blk["trunk"][0]
    root_acc = max(acc.get(blk["root"], []), key=lambda x: x[0], default=None)
    band, n_eff, n_mp, n_distinct = rule_only_refusals(p["proposals"])
    ident_tw = afd.site_identity(twin, blk)          # the twin's certified sites reproduced among the arm's certified sites
    ident_aw = afd.site_identity(blk, twin)          # the arm's certified sites reproduced among the twin's (what the rule added)
    leaves = leaf_identity(twin, blk)
    return dict(a=a, p=p, blk=blk, twin=twin, q=q, d=d, root=root_tr, root_acc=root_acc, band=band, n_eff=n_eff, n_mp=n_mp, n_distinct=n_distinct,
                build_out=build_out_counts(p["build_out"]), ident_tw=ident_tw, ident_aw=ident_aw, leaves=leaves)


# ----------------------------------------------------------------------------------------------- formatting
def fmt_match(m, tag, what):
    L = []
    if m["best"] is None:
        L.append("    %s: NO depth-1 site in the arm (root is a leaf)" % what); return L
    b = m["best"]
    L.append("    %s -> arm site %s [%s] by best Jaccard %.3f over ALL %d depth-1 sites on %d shared train texts%s" % (
        what, b["site"], b["label"][:24], b["j"], len(m["rows"]), m["shared"], "  (TIE at the top: printed, the first id taken)" if m["tie"] else ""))
    L.append("        all depth-1 sites: " + "; ".join("%s J %.3f n %d %s" % (r["site"], r["j"], r["n"], "CERT" if r["cert"] else "not cert") for r in m["rows"]))
    co = m["cert_only"]; cb = m["cert_best"]
    L.append("        certified-only reading (REDRAW site_identity, Jaccard >= %.2f one-to-one): %s" % (
        JACCARD, "reproduces at %s (J %.3f)" % (co[0], co[1]) if co else "NOT reproduced (best over the arm's certified sites %s J %.3f)" % (cb[1] or "-", cb[0])))
    e = m["exist"]
    acc = m["accepted"]
    L.append("        n %d | accepted k %s (proposals.csv last ACCEPTED GROW row iter %s dV %s; snapshot childIds %d%s) | joint sepScore %s = %sx bar %.3f" % (
        b["n"], acc[1] if acc else "-", acc[0] if acc else "-", acc[1] if acc else "-", m["k_snapshot"],
        "" if m["k_consistent"] else "  <- INCONSISTENT with the accepted dV (a later merge?)",
        "%.6f" % e["joint"] if e["joint"] is not None else "-", "%.3f" % (e["joint"] / BAR) if e["joint"] is not None else "-", BAR))
    kind, lo, hi = m["minpair"]
    if kind == "EXACT":
        L.append("        accepted min-pair == joint at k = 2: %.3fx bar (EXACT)%s" % (lo, "  <- BELOW the 1.05x rule: not a primed acceptance" if lo < MULT - 1e-9 else ""))
    elif kind == "INTERVAL":
        L.append("        accepted min-pair NOT recorded at k = %d: in [%.2f, %.3f]x bar (INTERVAL: the rule's floor to the joint score)" % (m["k_snapshot"], lo, hi))
    else:
        L.append("        LEAF (never split)")
    for r in e["refused"]:
        flag = ""
        if r.get("bar_eff") is not None:
            flag = "  <- REFUSED BY THE RULE ONLY (nominal bar would accept)" if r["bar"] <= r["sep"] < r["bar_eff"] else ""
        L.append("        refused k=%d emK=%d: min-pair sep %.5f = %.3fx bar (bar %.5f, bar_eff %s; iter %s; n_site %d)%s" % (
            r["k"], r["emK"], r["sep"], r["sep"] / BAR, r["bar"], "%.5f" % r["bar_eff"] if r.get("bar_eff") is not None else "absent (UNPRIMED ROW)",
            ",".join(map(str, r["iters"])), r["n"], flag))
    if e["other"]:
        L.append("        other refusals: %s" % ", ".join("%s x%d" % kv for kv in sorted(e["other"].items())))
    if b["in_csv"]:
        L.append("        site null: observed_sep %.6f | p95 %.6f | margin %.3f | %s" % (b["observed"], b["p95"], b["margin"], "CERTIFIED" if b["cert"] else "NOT certified"))
    else:
        L.append("        site null: NOT IN the CSV (leaf?)")
    return L


def fmt_arm(R):
    a, blk, twin = R["a"], R["blk"], R["twin"]
    m = blk["manifest"]
    L = []
    L.append("--- %s %s (primed, proposalAcceptMultiplier %.2f; STRUCTURAL EVIDENCE ONLY) | %s | snapshot %s | manifest: seed %s, split pool %s, train %s / test %s, multiplier %s, commit %s"
             % (a["tag"], a["arm"], MULT, blk["run_name"], blk["snapshot"], m.get("seed"), m.get("reserved_pool_id"), m.get("train_size"), m.get("test_size"),
                m.get("proposal_accept_multiplier"), str(m.get("commit", "?"))[:8]))
    L.append("    twin %s %s | snapshot %s | certified %d of %d | leaves %d | purity %.3f" % (a["twin_tag"], a["twin"], twin["snapshot"], twin["cert"], twin["sites"], twin["leaves"], twin["purity"]["acc"]))
    L.append("    site null %s (%d sites, %d reps) | readout %s | build log %s" % (rel(R["p"]["csv"]), blk["sites"], afd.REPS, rel(R["p"]["readout"]), rel(R["p"]["build_out"])))
    L.append("    leaves %d / nodes %d / max depth %d / iterations %d | certified %d of %d sites (%.1f%%) | members %d; pool of record among members %d of %d (%.1f%%)%s"
             % (blk["leaves"], blk["nodes"], blk["depth"], blk["iteration"], blk["cert"], blk["sites"], 100 * blk["share"], len(blk["all_members"]),
                blk["overlap"], blk["pool_n"], 100 * blk["overlap"] / blk["pool_n"], " (clean split)" if blk["overlap"] == 0 else " (IN-SAMPLE: identity of the purity number only)"))
    L.append("    held-out purity (leaf, flatLeaf, pool of record) recomputed %.3f [%.3f, %.3f] | readout %.3f (F6 leaf %+.3f/1000) | twin readout / recomputed %s / %.3f"
             % (blk["purity"]["acc"], blk["purity"]["lo"], blk["purity"]["hi"], blk["readout"]["purity"], blk["readout"]["f6_leaf"],
                "%.3f" % twin["readout"]["purity"] if twin["readout"] else "-", twin["purity"]["acc"]))
    L.append("  C1 quantitative depth-1 site (record %s):" % REC_Q)
    L += fmt_match(R["q"], a["tag"], "record %s" % REC_Q)
    L.append("  C2 discursive depth-1 site (record %s) and the root:" % REC_D)
    L += fmt_match(R["d"], a["tag"], "record %s" % REC_D)
    rt = R["root"]
    ra = R["root_acc"]
    er = blk["exist"][blk["root"]]
    L.append("    root %s: accepted k %s (dV %s, snapshot childIds %d) | joint %.6f = %.3fx bar | observed %.6f p95 %.6f margin %.3f | %s" % (
        blk["root"], ra[1] if ra else "-", ra[1] if ra else "-", er["k"], er["joint"], er["joint"] / BAR, rt["observed"] or 0, rt["p95"] or 0, rt["margin"] or 0, "CERTIFIED" if rt["cert"] else "NOT certified"))
    ax = blk["axis"]
    L.append("    trunk axis: root k = %d | quantitative cell %s | discursive cell %s | %s | %d of 12 scored categories on the record's side"
             % (ax["root_k"], ax["qcell"], ax["dcell"], "axis present" if ax["axis_present"] else "AXIS ABSENT", ax["on_side"]))
    L.append("  P7 rule-only refusals (NO_PROPOSAL rows with bar <= sep < bar_eff; every site, every iteration): %d rows (%d distinct site/k/emK/sep) | min-pair rows %d, of them carrying bar_eff %d | %s"
             % (len(R["band"]), R["n_distinct"], R["n_mp"], R["n_eff"],
                "build.out: [K-SELECTION] lines %d, bar_eff= lines %d" % (R["build_out"]["kselection"], R["build_out"]["bar_eff"]) if R["build_out"] else "build.out ABSENT"))
    for x in R["band"]:
        L.append("        iter %d %s [%s] k=%d emK=%d sep %.5f (bar %.5f, bar_eff %.5f) = %.3fx bar, n_site %d" % (x["iter"], x["site"], x["label"][:24], x["k"], x["emK"], x["sep"], x["bar"], x["bar_eff"], x["sep"] / BAR, x["n"]))
    if R["n_eff"] == 0:
        L.append("        NOTE: no min-pair refusal row carries bar_eff: either the primed engine never refused a min-pair, or this is not a primed build (manifest multiplier printed above)")
    idn = blk["identity"]
    L.append("  (d) certified-site identity vs the RECORD (REDRAW rule): %d of %d record sites reproduce (shared train texts %d); twin %s: %d of 16"
             % (idn["reproduced"], idn["of"], idn["shared"], a["twin_tag"], twin["identity"]["reproduced"]))
    L.append("      %-11s d  %5s  %-7s  %-11s  %-8s  %s" % ("record site", "n", "margin", "arm site", "Jaccard", "verdict"))
    rr_ = blk["record_rows"]
    for s in sorted(rr_, key=lambda s: -rr_[s]["observed"] / rr_[s]["p95"]):
        if not rr_[s]["cert"]:
            continue
        if s in idn["match"]:
            t, j = idn["match"][s]; L.append("      %-11s %d  %5d  %7.3f  %-11s  %8.3f  reproduces" % (s, rr_[s]["depth"], rr_[s]["n"], rr_[s]["observed"] / rr_[s]["p95"], t, j))
        else:
            j, t = idn["best"][s]; L.append("      %-11s %d  %5d  %7.3f  %-11s  %8.3f  NOT reproduced (best over the arm's certified sites)" % (s, rr_[s]["depth"], rr_[s]["n"], rr_[s]["observed"] / rr_[s]["p95"], t or "-", j))
    tw = R["ident_tw"]; aw = R["ident_aw"]
    L.append("  P8 primed vs unprimed twin (%s vs %s): shared train texts %d | twin certified sites reproduced in the arm at Jaccard >= %.2f: %d of %d | arm certified sites reproduced in the twin: %d of %d"
             % (a["tag"], a["twin_tag"], tw["shared"], JACCARD, tw["reproduced"], tw["of"], aw["reproduced"], aw["of"]))
    L.append("      %-11s d  %5s  %-7s  %-11s  %-8s  %s" % ("twin site", "n", "margin", "arm site", "Jaccard", "verdict"))
    trows = twin["sitenull"]["rows"]
    for s in sorted(twin["cert_ids"], key=lambda s: -trows[s]["observed"] / trows[s]["p95"]):
        if s in tw["match"]:
            t, j = tw["match"][s]; L.append("      %-11s %d  %5d  %7.3f  %-11s  %8.3f  reproduces" % (s, trows[s]["depth"], trows[s]["n"], trows[s]["observed"] / trows[s]["p95"], t, j))
        else:
            j, t = tw["best"][s]; L.append("      %-11s %d  %5d  %7.3f  %-11s  %8.3f  NOT reproduced (best over the arm's certified sites)" % (s, trows[s]["depth"], trows[s]["n"], trows[s]["observed"] / trows[s]["p95"], t or "-", j))
    added = [t for t in blk["cert_ids"] if t not in {v[0] for v in tw["match"].values()}]
    if added:
        arows = blk["sitenull"]["rows"]
        L.append("      arm certified sites with no twin match: %s" % ", ".join("%s(d%d, n=%d, margin %.2f)" % (t, arows[t]["depth"], arows[t]["n"], arows[t]["observed"] / arows[t]["p95"]) for t in added))
    lf = R["leaves"]
    L.append("      leaf identity: twin leaves %d, arm leaves %d, one-to-one matched %d, at Jaccard >= %.1f: %d | histogram %s | median J %.3f"
             % (lf["twin_leaves"], lf["arm_leaves"], lf["matched"], LEAF_J, lf["at_09"], lf["hist"], lf["median"]))
    L.append("  (e) mu-match of the record's %d leaves to this tree at cos >= %.2f: %d of %d (median best cos %.3f) | twin %d of %d"
             % (blk["mu"]["n"], afd.MU_COS, blk["mu"]["matched"], blk["mu"]["n"], blk["mu"]["median"], twin["mu"]["matched"], twin["mu"]["n"]))
    return L


# ----------------------------------------------------------------------------------------------- scoring
def score(res, states, c0, i2v, suite):
    """res: arm -> analysis or None.  Returns (lines, verdict_written)."""
    L = []
    built = [a for a in ARMS if res.get(a["arm"]) is not None]
    undet = [a for a in ARMS if res.get(a["arm"]) is None]
    denom = "%d of %d arms built%s" % (len(built), len(ARMS), "" if not undet else " (UNDETERMINED: %s)" % ", ".join("%s %s: %s" % (a["tag"], a["arm"], states[a["arm"]][1]) for a in undet))
    full = len(built) == len(ARMS)
    L.append("")
    L.append("=== Criteria (registered L8298-L8309; denominator %s) ===" % denom)
    L.append("  C0 INERTNESS: I1 %s -> %s | %s -> %s | C0 %s%s" % (suite[1], V(suite[0]), i2v[1], V(i2v[0]), V(c0),
             "" if c0 else "   <- nothing primed is READ as a verdict (registration: 'If C0 fails nothing is read'); the numbers below are printed, labelled"))
    c1 = {}
    for a in built:
        R = res[a["arm"]]; b = R["q"]["best"]
        c1[a["arm"]] = bool(b and b["cert"])
        L.append("  C1 QUANT D1 %-4s %-18s site %s (J %.3f to %s) accepted k %s | observed %.6f p95 %.6f margin %.3f -> %s | certified-only reading: %s"
                 % (a["tag"], a["arm"], b["site"] if b else "-", b["j"] if b else 0, REC_Q, R["q"]["accepted"][1] if R["q"].get("accepted") else "-",
                    b["observed"] or 0, b["p95"] or 0, b["margin"] or 0, V(c1[a["arm"]]),
                    "reproduces" if R["q"]["cert_only"] else "NOT reproduced (best J %.3f)" % R["q"]["cert_best"][0]))
    for a in undet:
        L.append("  C1 QUANT D1 %-4s %-18s UNDETERMINED (%s)" % (a["tag"], a["arm"], states[a["arm"]][1]))
    c1_all = bool(c1) and all(c1.values())
    L.append("  C1 sweep: certified in %d of %d built arms (registration: 3 of 3) -> %s%s" % (sum(c1.values()), len(c1), V(c1_all if c1 else None),
             "   [F1 FIRES: R1' uncertified at the quantitative depth-1 site]" if c1.get("af_clean_s42_k105") is False else ""))
    c2 = {}; p2 = {}
    for a in built:
        R = res[a["arm"]]; d = R["d"]["best"]; rt = R["root"]
        dm, rm = (d["margin"] if d else None), rt["margin"]
        ok = bool(d and d["cert"] and rt["cert"])
        c2[a["arm"]] = ok
        p2[a["arm"]] = in_range(dm, *BAND_DISC) and in_range(rm, *BAND_ROOT)
        chg = []
        if dm is not None and not in_range(dm, BAND_DISC[0] - DRAW_SPREAD, BAND_DISC[1] + DRAW_SPREAD): chg.append("discursive margin %.3f outside %.2f-%.2f by more than %.2f: CHANGE" % (dm, BAND_DISC[0], BAND_DISC[1], DRAW_SPREAD))
        if rm is not None and not in_range(rm, BAND_ROOT[0] - DRAW_SPREAD, BAND_ROOT[1] + DRAW_SPREAD): chg.append("root margin %.3f outside %.2f-%.2f by more than %.2f: CHANGE" % (rm, BAND_ROOT[0], BAND_ROOT[1], DRAW_SPREAD))
        L.append("  C2 DISC+ROOT %-4s %-18s discursive %s %s margin %.3f (band %.2f-%.2f) | root %s margin %.3f (band %.2f-%.2f) -> %s%s"
                 % (a["tag"], a["arm"], d["site"] if d else "-", "CERT" if d and d["cert"] else "not cert", dm or 0, BAND_DISC[0], BAND_DISC[1],
                    "CERT" if rt["cert"] else "not cert", rm or 0, BAND_ROOT[0], BAND_ROOT[1], V(ok), ("   " + "; ".join(chg)) if chg else ""))
    for a in undet:
        L.append("  C2 DISC+ROOT %-4s %-18s UNDETERMINED" % (a["tag"], a["arm"]))
    c2_all = bool(c2) and all(c2.values())
    L.append("  C2 sweep: discursive site and root certified in %d of %d built arms -> %s" % (sum(c2.values()), len(c2), V(c2_all if c2 else None)))
    stable = None
    if full:
        stable = [s for s in res[ARMS[0]["arm"]]["blk"]["identity"]["match"] if all(s in res[a["arm"]]["blk"]["identity"]["match"] for a in ARMS)]
        rr_ = res[ARMS[0]["arm"]]["blk"]["record_rows"]
        c3 = all(s in stable for s in REC_FIVE)
        L.append("  C3 STABLE SET (record sites reproducing in R1', R2' and R3' at Jaccard >= %.2f): %d of 16: %s" % (JACCARD, len(stable),
                 ", ".join("%s(d%d, n=%d, margin %.2f)" % (s, rr_[s]["depth"], rr_[s]["n"], rr_[s]["observed"] / rr_[s]["p95"]) for s in sorted(stable)) or "none"))
        L.append("  C3 contains the record's five %s: %s -> %s" % (", ".join(REC_FIVE), ", ".join("%s %s" % (s, "in" if s in stable else "MISSING") for s in REC_FIVE), V(c3)))
    else:
        c3 = None
        L.append("  C3 STABLE SET: not computable (an arm is UNDETERMINED: the set is defined over R1', R2' and R3') -> UNDETERMINED")
    # ---- predictions
    L.append("")
    L.append("=== Predictions (registered L8311-L8323, blind; scored HELD / FAILED with the number beside) ===")

    def P(tag, text, ok, num):
        L.append("  %-4s %-62s %-12s %s" % (tag, text, V(ok), num))
    r1 = res.get("af_clean_s42_k105")
    if r1 is not None:
        q = r1["q"]; b = q["best"]; k = q["accepted"][1] if q.get("accepted") else None
        P("P1", "R1' quantitative site accepted k = 3 and margin obs/p95 in [1.6, 1.8]", k == 3 and in_range(b["margin"], *P1_BAND),
          "k %s, margin %.3f (twin R1: k 2, 0.746; record / R2 / R3 1.69-1.73)" % (k, b["margin"] or 0))
    else:
        P("P1", "R1' quantitative site accepted k = 3 and margin obs/p95 in [1.6, 1.8]", None, "R1' UNDETERMINED")
    for a in ARMS:
        R = res.get(a["arm"])
        if R is None:
            P("P2", "%s discursive 2.10-2.13 and root 1.12-1.14" % a["tag"], None, "UNDETERMINED"); continue
        d = R["d"]["best"]
        P("P2", "%s discursive 2.10-2.13 and root 1.12-1.14" % a["tag"], p2[a["arm"]], "discursive %.3f, root %.3f" % (d["margin"] if d else 0, R["root"]["margin"] or 0))
    if stable is not None:
        P("P3", "stable set grows to 6 (adds %s)" % REC_Q, len(stable) == 6 and REC_Q in stable, "%d sites; %s %s" % (len(stable), REC_Q, "in" if REC_Q in stable else "NOT in"))
    else:
        P("P3", "stable set grows to 6 (adds %s)" % REC_Q, None, "not computable")
    for a in ARMS:
        R = res.get(a["arm"])
        if R is None:
            P("P4", "%s certified count within +-2 of twin %s (%d of %d)" % (a["tag"], a["twin_tag"], a["twin_cert"][0], a["twin_cert"][1]), None, "UNDETERMINED"); continue
        b = R["blk"]; t = R["twin"]
        P("P4", "%s certified count within +-2 of twin %s (%d of %d)" % (a["tag"], a["twin_tag"], a["twin_cert"][0], a["twin_cert"][1]), abs(b["cert"] - t["cert"]) <= 2,
          "%d of %d (%.1f%%) vs twin %d of %d: delta %+d" % (b["cert"], b["sites"], 100 * b["share"], t["cert"], t["sites"], b["cert"] - t["cert"]))
    for a in ARMS:
        R = res.get(a["arm"])
        if R is None:
            P("P5", "%s readout purity within 1 pp of twin's %.3f" % (a["tag"], a["twin_purity"]), None, "UNDETERMINED"); continue
        b = R["blk"]; pr = b["readout"]["purity"]
        P("P5", "%s readout purity within 1 pp of twin's %.3f" % (a["tag"], a["twin_purity"]), abs(pr - a["twin_purity"]) <= 0.01 + 1e-9,
          "%.3f (recomputed %.3f [%.3f, %.3f]) delta %+.1f pp%s" % (pr, b["purity"]["acc"], b["purity"]["lo"], b["purity"]["hi"], 100 * (pr - a["twin_purity"]),
          "; clean split" if b["overlap"] == 0 else "; IN-SAMPLE overlap %d of %d (%.1f%%): identity of the number only" % (b["overlap"], b["pool_n"], 100 * b["overlap"] / b["pool_n"])))
    P("P6", "I2 byte-identical leaf membership (INERT)", i2v[0], i2v[1])
    tot = 0
    for a in ARMS:
        R = res.get(a["arm"])
        if R is None:
            P("P7", "%s rule-only refusals (bar <= sep < bar_eff) 1-4" % a["tag"], None, "UNDETERMINED"); continue
        n = len(R["band"]); tot += n
        P("P7", "%s rule-only refusals (bar <= sep < bar_eff) 1-4" % a["tag"], in_range(n, *P7_BAND),
          "%d rows over all iterations (%d distinct); build.out [K-SELECTION] %s, bar_eff= %s%s" % (n, R["n_distinct"], R["build_out"]["kselection"] if R["build_out"] else "-", R["build_out"]["bar_eff"] if R["build_out"] else "-",
          "   [> 10: the fringe moves]" if n > 10 else ""))
    P("P7", "total rule-only refusals over the built arms (no band; printed)", "printed", "%d rows over %d arms" % (tot, len(built)))
    for a in ARMS:
        R = res.get(a["arm"])
        if R is None:
            P("P8", "%s twin leaves reproduced at Jaccard >= 0.9 >= 70" % a["tag"], None, "UNDETERMINED"); continue
        lf = R["leaves"]
        P("P8", "%s twin leaves reproduced at Jaccard >= 0.9 >= 70" % a["tag"], lf["at_09"] >= 70, "%d of %d twin leaves (arm %d leaves; histogram %s)" % (lf["at_09"], lf["twin_leaves"], lf["arm_leaves"], lf["hist"]))
    if r1 is not None:
        P("P9", "R1' leaves in [78, 88]", in_range(r1["blk"]["leaves"], *P9_BAND), "leaves %d (twin R1 82)" % r1["blk"]["leaves"])
    else:
        P("P9", "R1' leaves in [78, 88]", None, "R1' UNDETERMINED")
    if stable is not None:
        P("P10", "%s NOT rescued into the stable set" % REC_43, REC_43 not in stable,
          "%s; best Jaccard over certified sites per arm: %s" % ("NOT in" if REC_43 not in stable else "IN the stable set",
           ", ".join("%s %.3f" % (a["tag"], res[a["arm"]]["blk"]["identity"]["best"][REC_43][0]) for a in ARMS)))
    else:
        P("P10", "%s NOT rescued into the stable set" % REC_43, None, "not computable; best Jaccard per built arm: %s" % (", ".join("%s %.3f" % (a["tag"], res[a["arm"]]["blk"]["identity"]["best"][REC_43][0]) for a in built) or "-"))
    for a in built:
        R = res[a["arm"]]
        P("mu", "%s mu-match of the record's 81 leaves at cos >= 0.95 (no band; printed)" % a["tag"], "printed", "%d of %d (twin %d)" % (R["blk"]["mu"]["matched"], R["blk"]["mu"]["n"], R["twin"]["mu"]["matched"]))
    # ---- verdict rule
    L.append("")
    L.append("=== Verdict rule (registered L8306-L8309) ===")
    all_held = bool(c0) and c1_all and c2_all and bool(c3)
    written = False
    if all_held and full:
        L.append("  C0, C1, C2 and C3 all HELD on 3 of 3 arms -> \"the quantitative depth-1 site certifies on every draw under hysteresis at 1.05 x bar\": a stated recipe property; REDRAW's C3 depth-1 chip and L6418-6423 take a bracket by insertion; plan S1.1(a)'s \"k-selection-fragile at the bar\" becomes \"k-selection at the bar, resolved by a geometric hysteresis rule (K-SELECTION)\"")
        written = True
    elif all_held and not full:
        L.append("  C0-C3 HELD on the REDUCED denominator (%s): the VERDICT RULE sentence is NOT written (the registration fixes C1 at 3 of 3; the registrar reads the components)" % denom)
    elif not c0:
        L.append("  C0 %s -> nothing is read (registration: 'If C0 fails nothing is read'); no verdict sentence" % V(c0))
    elif c1_all is False:
        L.append("  C1 FAILED -> FALSIFIER F1: the fragility is the CORPUS's (the quantitative mass does not separate above the null when k = 2 is refused, or the rule costs the discursive certification); REDRAW's sentence of record stands (\"the quantitative depth-1 site is 3/4 (k-selection at the bar)\"); the flag stays inert and absent from every config, or is removed (the author's call)")
    elif c2_all is False:
        L.append("  C2 FAILED -> FALSIFIER F1 (the discursive site or the root lost certification in an arm): REDRAW's sentence of record stands; no recipe-property sentence")
    else:
        L.append("  C3 %s (C0, C1, C2 %s / %s / %s): no verdict sentence; the registrar reads the components" % (V(c3), V(c0), V(c1_all if c1 else None), V(c2_all if c2 else None)))
    L.append("  Not overturned by any outcome here: REDRAW's C1, C2, C5; the 5-site stable set; CAP-PRUNE.  Not shown by HELD: a board on any primed tree; a union routing gain; that 1.05 is the right multiplier.")
    L.append("  Every tree read here is STRUCTURAL EVIDENCE ONLY; no registration may judge on a primed tree without naming K-SELECTION.")
    return L, written, dict(c0=c0, c1=c1, c2=c2, c3=c3, stable=stable, full=full)


def header(cs, suite, i2v):
    return ["=== K-SELECTION readout (registered 2026-09-19, programme L8224-L8390, naming bracket L8765; zero LLM calls; STRUCTURAL EVIDENCE ONLY) ===",
            "  pool of record: %s | corpus: %d mmlu_pro rows, %d distinct texts, held-out 3445 | record: %s, %s (16 certified of 69)" % (POOL, cs["rows"], cs["distinct"], rel(afd.RECORD_DIR), rel(afd.RECORD_CSV)),
            "  rule: proposalAcceptMultiplier %.2f (creation side only) | bar %.3f | identity Jaccard >= %.2f on shared train texts, one-to-one greedy (anchor_free_redraw.site_identity, unchanged) | leaf identity at >= %.1f | mu-match cos >= %.2f" % (MULT, BAR, JACCARD, LEAF_J, afd.MU_COS),
            "  C1 matching rule (naming bracket): the arm's depth-1 site with the best Jaccard to the record's %s over ALL depth-1 sites; the certified-only reading beside" % REC_Q,
            "  I1: %s (%s) | I2: %s" % (suite[1], suite[2], i2v[1]),
            "  inputs: %s (arms), %s (twins), snapshots.db mode=ro&immutable=1" % (rel(KS), rel(REDRAW))]


# ----------------------------------------------------------------------------------------------- modes
def dry_run(suite_arg, declared):
    print(pool_guard.assert_pool_of_record(POOL))
    print("=== K-SELECTION readout dry-run (zero calls; nothing written; every arm ABSENT is the expected state before the chain) ===")
    suite = suite_state(suite_arg)
    i2v = i2_state(i2_paths()["verdict"])
    print("  I1 suite: %s (%s) -> %s | I2: %s -> %s" % (suite[1], suite[2], V(suite[0]), i2v[1], V(i2v[0])))
    ip = i2_paths()
    print("  I2   %-18s run dir %s: %s | verdict file %s: %s | build.out %s" % (I2["arm"], rel(ip["run_dir"]), "present" if os.path.isdir(ip["run_dir"]) else "ABSENT",
          rel(ip["verdict"]), "present" if os.path.exists(ip["verdict"]) else "ABSENT", "present" if os.path.exists(ip["build_out"]) else "ABSENT"))
    ready = True
    for a in ARMS:
        p = arm_paths(a)
        state, why = arm_state(a, p, declared)
        print("  %-4s %-18s twin %s %s | state %s (%s)" % (a["tag"], a["arm"], a["twin_tag"], a["twin"], state, why))
        for k in ("run_dir", "manifest", "proposals", "csv", "readout", "build_out"):
            print("       %-9s %s : %s" % (k, rel(p[k]), "present" if os.path.exists(p[k]) else "ABSENT"))
        for k in ("twin_dir", "twin_csv", "twin_readout"):
            print("       %-9s %s : %s" % (k, rel(p[k]), "present" if os.path.exists(p[k]) else "ABSENT"))
        if state == "ABSENT":
            ready = False
    out = os.path.join(KS, "k_selection_outcome.txt")
    print("  outcome %s: %s (write-once)" % (rel(out), "EXISTS (--run would refuse)" if os.path.exists(out) else "absent"))
    print("  --run would %s" % ("REFUSE (an arm is ABSENT: the chain has not reached it; declare --undetermined <arm> only for an arm the chain will never run)" if not ready else
                                 ("REFUSE (outcome exists)" if os.path.exists(out) else "proceed (UNDETERMINED arms scored as such, denominator named)")))
    print("  dry-run: nothing written")
    return 0


def run(suite_arg, declared, ks=None, outcome=None, quiet=False):
    ks = ks or KS
    outcome = outcome or os.path.join(ks, "k_selection_outcome.txt")
    print(pool_guard.assert_pool_of_record(POOL))
    if os.path.exists(outcome):
        raise SystemExit("[KSEL] %s exists: the outcome is WRITE-ONCE; nothing recomputed, nothing written (move it aside by hand only with a registrar's note)" % rel(outcome))
    states = {}
    for a in ARMS:
        states[a["arm"]] = arm_state(a, arm_paths(a, ks), declared)
        if states[a["arm"]][0] == "ABSENT":
            raise SystemExit("[KSEL] %s %s ABSENT: %s; --run refuses (declare --undetermined %s only for an arm the chain will never run)" % (a["tag"], a["arm"], states[a["arm"]][1], a["arm"]))
    suite = suite_state(suite_arg)
    i2v = i2_state(i2_paths(ks)["verdict"])
    c0 = (True if (suite[0] and i2v[0]) else (None if (suite[0] is None or i2v[0] is None) and not (suite[0] is False or i2v[0] is False) else False))
    ctx, cs = afd.load_corpus_ctx()
    rec = afd.analyse_record(ctx)
    L = header(cs, suite, i2v)
    L.append("  arms: %s | %s" % (", ".join("%s=%s (%s)" % (a["tag"], a["arm"], states[a["arm"]][0]) for a in ARMS), i2v[1]))
    res = {}
    for a in ARMS:
        st, why = states[a["arm"]]
        if st != "READY":
            res[a["arm"]] = None
            L.append("  %s %s: UNDETERMINED (%s)" % (a["tag"], a["arm"], why))
            continue
        res[a["arm"]] = analyse_arm(a, arm_paths(a, ks), ctx, rec)
    for a in ARMS:
        if res[a["arm"]] is not None:
            L.append(""); L += fmt_arm(res[a["arm"]])
    SL, written, summary = score(res, states, c0, i2v, suite)
    L += SL
    txt = "\n".join(L)
    if not quiet:
        print(txt)
    os.makedirs(os.path.dirname(outcome), exist_ok=True)
    with open(outcome, "w", encoding="utf-8", newline="\n") as f:
        f.write(txt + "\n")
    print("  written: %s (write-once)" % rel(outcome))
    return res, summary, txt


# ----------------------------------------------------------------------------------------------- selftest (scratch stand-ins)
def selftest(scratch):
    """The REDRAW arms as stand-ins for the primed arms (copied into a scratch kselect layout, manifests patched to carry
    proposal_accept_multiplier 1.05, R1's proposals.csv given fabricated bar_eff rows, a fabricated INERT verdict), the
    whole --run executed against the scratch root and asserted.  Nothing under experiment_results is written."""
    print(pool_guard.assert_pool_of_record(POOL))
    ks = os.path.join(scratch, "kselect")
    if os.path.isdir(ks):
        shutil.rmtree(ks)
    os.makedirs(ks)
    # (i) the regex on both forms (anchor_free_redraw.REASON_RE)
    m_old = afd.REASON_RE.search("min_pair_sep_below_bar(sep=0.02410,bar=0.02500,k=2,emK=2)")
    m_new = afd.REASON_RE.search("min_pair_sep_below_bar(sep=0.02515,bar=0.02500,bar_eff=0.02625,k=2,emK=3)")
    assert m_old.groups() == ("0.02410", "0.02500", None, "2", "2") and m_new.groups() == ("0.02515", "0.02500", "0.02625", "2", "3")
    print("  REASON_RE: unprimed and primed rows parse (bar_eff None / 0.02625)")
    # (ii) stand-ins
    fab = {"af_clean_s42_k105": [("3", "n00000004", "Emergent Concept #3", "0.02515", "0.02625", "2", "2", "3837"),      # in band: rule-only refusal
                                 ("4", "n00000017", "Emergent Concept #16", "0.02600", "0.02625", "2", "3", "1647"),     # in band
                                 ("4", "n00000017", "Emergent Concept #16", "0.02000", "0.02625", "2", "2", "1647")]}    # below the bar: not rule-only
    for a in ARMS:
        src = os.path.join(REDRAW, a["twin"], "seed_%d" % a["seed"])
        dst = os.path.join(ks, a["arm"], "seed_%d" % a["seed"])
        os.makedirs(os.path.join(dst, "diagnostics"))
        for f in ("dag_snapshots.jsonl", "headless_run.log"):
            shutil.copyfile(os.path.join(src, f), os.path.join(dst, f))
        shutil.copyfile(os.path.join(src, "diagnostics", "proposals.csv"), os.path.join(dst, "diagnostics", "proposals.csv"))
        m = json.load(open(os.path.join(src, "diagnostics", "run_manifest.json"), encoding="utf-8"))
        m["proposal_accept_multiplier"] = MULT
        json.dump(m, open(os.path.join(dst, "diagnostics", "run_manifest.json"), "w", encoding="utf-8"))
        for row in fab.get(a["arm"], []):
            it, site, label, sep, be, k, emk, n = row
            with open(os.path.join(dst, "diagnostics", "proposals.csv"), "a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow([it, "GROW", site, label, "", "", "", "", "NO_PROPOSAL", "min_pair_sep_below_bar(sep=%s,bar=0.02500,bar_eff=%s,k=%s,emK=%s)" % (sep, be, k, emk), n])
        shutil.copyfile(os.path.join(REDRAW, "site_null_%s.csv" % a["twin"]), os.path.join(ks, "site_null_%s.csv" % a["arm"]))
        ro = open(os.path.join(REDRAW, "anchor_free_%s_readout.txt" % a["twin"]), encoding="utf-8").read()
        ro = ro.replace("%s/seed_%d" % (a["twin"], a["seed"]), "%s/seed_%d" % (a["arm"], a["seed"]))
        open(os.path.join(ks, "anchor_free_%s_readout.txt" % a["arm"]), "w", encoding="utf-8").write(ro)
        n_fab = len(fab.get(a["arm"], []))
        with open(os.path.join(ks, "%s.build.out" % a["arm"]), "w", encoding="utf-8") as f:
            f.write("[K-SELECTION] creation-side hysteresis ACTIVE: proposals accepted only at min-pair >= 1.05 x bar (fabricated)\n")
            for i in range(n_fab):
                f.write("[NO-SPLIT] 'x' reason=min-pair n=1 k=2 emK=2 sep=0.0250 bar=0.0250 bar_eff=0.0263 (fabricated)\n")
    open(os.path.join(ks, "i2_inertness.txt"), "w", encoding="utf-8").write("SELFTEST stand-in (fabricated)\nI2 INERTNESS VERDICT: INERT (C0 / P6 HELD)\n")
    print("  stand-ins: %s (copied from the REDRAW arms; manifests patched to %.2f; R1' given %d fabricated bar_eff rows, 2 in band)" % (rel(ks) if ks.startswith(ROOT) else ks, MULT, len(fab["af_clean_s42_k105"])))
    # (iii) the states
    for a in ARMS:
        st, why = arm_state(a, arm_paths(a, ks))
        assert st == "READY", (a["arm"], st, why)
    absent = arm_state(ARMS[0], arm_paths(ARMS[0], os.path.join(scratch, "nowhere")))
    assert absent[0] == "ABSENT", absent
    # (iv) the run
    res, S, txt = run(None, (), ks=ks, outcome=os.path.join(ks, "k_selection_outcome.txt"), quiet=True)
    checks = []
    r1, r2, r3 = (res[a["arm"]] for a in ARMS)
    checks.append(("C0 HELD (real suite line, fabricated INERT)", S["c0"] is True))
    q1 = r1["q"]
    checks.append(("R1' C1 site = n00000004 by best Jaccard over ALL depth-1 sites (J > 0.9), NOT certified, margin 0.746 -> FAILED",
                   q1["best"]["site"] == "n00000004" and q1["best"]["j"] > 0.9 and q1["best"]["cert"] is False and abs(q1["best"]["margin"] - 0.746) < 5e-4 and S["c1"]["af_clean_s42_k105"] is False))
    checks.append(("R1' certified-only reading: NOT reproduced, best n00000001 J 0.467 (REDRAW L81)", q1["cert_only"] is None and q1["cert_best"][1] == "n00000001" and abs(q1["cert_best"][0] - 0.467) < 5e-4))
    checks.append(("R1' accepted k 2 (dV) == snapshot k, min-pair EXACT 1.006x (below the 1.05 rule)", q1["accepted"][1] == 2 and q1["k_consistent"] and q1["minpair"][0] == "EXACT" and abs(q1["minpair"][1] - 1.006) < 1e-3))
    checks.append(("R1' fabricated refusal at n00000004 parsed with bar_eff 0.02625 and flagged rule-only",
                   any(r.get("bar_eff") == 0.02625 and r["sep"] == 0.02515 for r in q1["exist"]["refused"]) and len(q1["rule_only_here"]) == 1))
    checks.append(("R2' / R3' C1 HELD at n00000004, k 3, INTERVAL [1.05, joint/bar], margins 1.703 / R3 > 1",
                   all(r["q"]["best"]["site"] == "n00000004" and r["q"]["best"]["cert"] and r["q"]["accepted"][1] == 3 and r["q"]["minpair"][0] == "INTERVAL" and r["q"]["minpair"][1] == MULT for r in (r2, r3))
                   and abs(r2["q"]["best"]["margin"] - 1.703) < 5e-4 and S["c1"]["af_s137_k105"] and S["c1"]["af_s2048_k105"]))
    checks.append(("C2 HELD in all three; R1' discursive 2.097 / root 1.141, R2' 2.115 / 1.138, R3' root 1.127 (REDRAW)",
                   all(S["c2"].values()) and abs(r1["d"]["best"]["margin"] - 2.097) < 5e-4 and abs(r1["root"]["margin"] - 1.141) < 5e-4
                   and abs(r2["d"]["best"]["margin"] - 2.115) < 5e-4 and abs(r2["root"]["margin"] - 1.138) < 5e-4 and abs(r3["root"]["margin"] - 1.127) < 5e-4))
    checks.append(("C3 HELD: stable set = REDRAW's five exactly", S["c3"] is True and sorted(S["stable"]) == sorted(REC_FIVE)))
    checks.append(("P7: R1' 2 rows in band (2 distinct), R2' 0, R3' 0; build.out counts 1 / 3", len(r1["band"]) == 2 and r1["n_distinct"] == 2 and len(r2["band"]) == 0 and len(r3["band"]) == 0
                   and r1["build_out"] == dict(kselection=1, bar_eff=3) and r1["n_eff"] == 3))
    checks.append(("P4: certified counts equal the twins' (14/69, 12/64, 10/66)", all((r["blk"]["cert"], r["blk"]["sites"]) == a["twin_cert"] for r, a in zip((r1, r2, r3), ARMS))))
    checks.append(("P5: readout purities 0.727 / 0.738 / 0.749", all(abs(r["blk"]["readout"]["purity"] - a["twin_purity"]) < 5e-4 for r, a in zip((r1, r2, r3), ARMS))))
    checks.append(("P8: leaf identity twin vs itself 82/82, 79/79, 81/81 at J = 1.0; certified-site table 14/14, 12/12, 10/10",
                   all(r["leaves"]["at_09"] == r["leaves"]["twin_leaves"] == r["leaves"]["arm_leaves"] == n for r, n in zip((r1, r2, r3), (82, 79, 81)))
                   and all(r["ident_tw"]["reproduced"] == r["ident_tw"]["of"] == a["twin_cert"][0] for r, a in zip((r1, r2, r3), ARMS))))
    checks.append(("P9 R1' leaves 82; P10 n00000043 not in the stable set, best J 0.652 / 0.646 in R1' / R2' (REDRAW L82 / L195)",
                   r1["blk"]["leaves"] == 82 and REC_43 not in S["stable"] and abs(r1["blk"]["identity"]["best"][REC_43][0] - 0.652) < 5e-4 and abs(r2["blk"]["identity"]["best"][REC_43][0] - 0.646) < 5e-4))
    checks.append(("twin identity vs the record reproduces REDRAW's 7 / 8 / 8 of 16; mu-match 55 / 61 / 58 of 81",
                   [r["twin"]["identity"]["reproduced"] for r in (r1, r2, r3)] == [7, 8, 8] and [r["blk"]["mu"]["matched"] for r in (r1, r2, r3)] == [55, 61, 58]))
    checks.append(("no VERDICT RULE sentence (C1 FAILED at R1'); F1 line printed", "recipe property" not in txt.split("=== Verdict rule")[1] and "FALSIFIER F1" in txt))
    checks.append(("outcome written under the scratch root only; write-once refusal on a second --run", os.path.exists(os.path.join(ks, "k_selection_outcome.txt")) and _refuses(ks)))
    print("")
    print("=== SELFTEST (REDRAW arms as stand-ins) ===")
    bad = 0
    for name, ok in checks:
        print("  %-4s %s" % ("PASS" if ok else "FAIL", name)); bad += (not ok)
    print("  SELFTEST %s (%d of %d checks); scratch outcome: %s" % ("PASS" if not bad else "FAIL", len(checks) - bad, len(checks), os.path.join(ks, "k_selection_outcome.txt")))
    return 0 if not bad else 2


def _refuses(ks):
    try:
        run(None, (), ks=ks, outcome=os.path.join(ks, "k_selection_outcome.txt"), quiet=True)
    except SystemExit as e:
        return "WRITE-ONCE" in str(e)
    return False


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true", help="inputs per arm; nothing written; exit 0 with every arm ABSENT")
    g.add_argument("--selftest", action="store_true", help="the REDRAW arms as stand-ins in a scratch layout; asserts the whole readout")
    g.add_argument("--run", action="store_true", help="the readout -> k_selection_outcome.txt (write-once)")
    ap.add_argument("--suite-line", default=None, help='I1: the suite line ("suite: tests N failures F errors E"); default the last such line of %s' % rel(SUITE_LOG))
    ap.add_argument("--undetermined", action="append", default=[], metavar="ARM", help="declare an arm the chain will never run (scored UNDETERMINED)")
    ap.add_argument("--scratch", default=None, help="(--selftest) scratch root; default $CLAUDE_SCRATCHPAD or the system temp dir")
    a = ap.parse_args(argv)
    for x in a.undetermined:
        if x not in {y["arm"] for y in ARMS}:
            raise SystemExit("[KSEL] unknown arm %r; arms: %s" % (x, ", ".join(y["arm"] for y in ARMS)))
    if a.selftest:
        import tempfile
        scratch = a.scratch or os.environ.get("CLAUDE_SCRATCHPAD") or os.path.join(tempfile.gettempdir(), "k_selection_selftest")
        return selftest(os.path.join(scratch, "k_selection_selftest"))
    if a.dry_run:
        return dry_run(a.suite_line, set(a.undetermined))
    run(a.suite_line, set(a.undetermined))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
