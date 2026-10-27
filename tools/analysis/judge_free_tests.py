"""J5 / J4 — the two zero-judge-call judge tests (docs/judge_improvement_proposals.md,
criteria frozen at commit 7a4391a BEFORE this script existed).

Data: the live verdict exports of R2 (experiment_results/x12_profile/seed_45/judging/
MAIN_verdicts.csv, 27,657 rows carrying both per-order votes; the 9,235 resumed rows lost
them and are excluded) and x12 (seed_44, 3,184 live). Ground truth = key accuracy per
model over the FROZEN reserved pool (ids from reserved_leaf_assignments.csv, so this is
independent of whichever pool is active in the DB).

J5 — order aggregation instead of forced ties.
  Board A (current rule): the shipped winner, POSITION_FLIP disagreements forced to TIE.
  Board B (order-aggregated): each presentation order is one half-weight observation
  (WinAFirst, WinASecond in {0, 0.5, 1}); no verdict is discarded.
  REGISTERED: PASS iff rho(B, GT) >= rho(A, GT) AND the number of top-4 pairwise
  order violations vs GT under B <= under A. Paired bootstrap over matches (B=200)
  for the rho difference is descriptive. Descriptive: single-order position bias
  P(first-shown wins | decisive) and the flip rate by |GT accuracy gap|.

J4 — length-covariate BT (LC-AlpacaEval move).
  P(a beats b) = sigmoid(theta_a - theta_b + beta_len * (len_a - len_b)/1000), ties as
  two half-weight outcomes; theta reported at delta-length = 0.
  REGISTERED: PASS iff the top-4 order under LC-BT has <= 1 adjacent violation vs GT in
  BOTH x12 and R2. AMENDMENT (stated here before the numbers were seen): the second
  clause as registered — "beta_len on the residual is within CI of 0" — is tautological
  for a joint fit (the residual of the model that includes the length term has no length
  effect by construction), so it is replaced by the informative reading: beta_len must be
  identified (|z| >= 2) so that the board actually absorbs length. Descriptive: the
  length-matching threshold sweep (100/200/300/500/800 chars) that has been post-hoc
  since 2026-09-07.
"""
import os, sys, csv, math, random, sqlite3
from collections import defaultdict, Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj  # mm_fit, spearman, EVAL_DB

R2 = os.path.join(ROOT, "experiment_results", "x12_profile", "seed_45", "judging", "MAIN_verdicts.csv")
X12 = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "seed_44", "judging", "MAIN_verdicts.csv")
ASSIGN = os.path.join(ROOT, "reserved_leaf_assignments.csv")
TOP4 = ["iask_pro", "gemini-3.1-pro_5-shots", "gpt-4o-2024-08-06", "arx_0314"]


def load_live(path):
    out = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["Rationale"].startswith("Reconstructed"):
                continue
            w = r["Winner"]
            out.append(dict(q=int(r["QueryId"]), a=r["ModelA"], b=r["ModelB"],
                            w=("TIE" if w == "TIE" else (r["ModelA"] if w == "Model A" else r["ModelB"])),
                            w1=float(r["WinAFirst"]), w2=float(r["WinASecond"]),
                            flip=r["PositionFlip"] == "true", src=r["TieSource"]))
    return out


def frozen_pool():
    with open(ASSIGN, newline="", encoding="utf-8") as f:
        return {int(r["question_id"]) for r in csv.DictReader(f)}


def gt_and_lengths(models):
    pool = frozen_pool()
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    ok, n, L = Counter(), Counter(), {}
    for q, m, ln, c in ev.execute("SELECT question_id, model_name, length(model_output), is_correct FROM eval_results"):
        if m not in models:
            continue
        L[(q, m)] = ln or 0
        if q in pool:
            ok[m] += c or 0
            n[m] += 1
    acc = {m: ok[m] / n[m] for m in models}
    return acc, L


def board_from(rows_votes, models):
    """rows_votes: iterable of (a, b, winsA, n) contributions."""
    agg = defaultdict(lambda: [0.0, 0.0])
    for a, b, wa, n in rows_votes:
        if a > b:
            a, b, wa = b, a, n - wa
        rec = agg[(a, b)]
        rec[0] += wa
        rec[1] += n
    return rj.mm_fit({k: tuple(v) for k, v in agg.items()}, models)


def current_votes(rows):
    for r in rows:
        yield r["a"], r["b"], (0.5 if r["w"] == "TIE" else (1.0 if r["w"] == r["a"] else 0.0)), 1.0


def order_votes(rows):
    for r in rows:
        yield r["a"], r["b"], 0.5 * r["w1"], 0.5
        yield r["a"], r["b"], 0.5 * r["w2"], 0.5


def violations(theta, gt_order):
    """pairwise (Kendall-discordant) and adjacent violations of the top-4 vs GT order."""
    order = sorted(gt_order, key=lambda m: -theta[m])
    pos = {m: i for i, m in enumerate(order)}
    pair = sum(1 for i in range(4) for j in range(i + 1, 4) if pos[gt_order[i]] > pos[gt_order[j]])
    adj = sum(1 for i in range(3) if pos[gt_order[i]] > pos[gt_order[i + 1]])
    return order, pair, adj


def rho(theta, acc, models):
    return rj.spearman([theta[m] for m in models], [acc[m] for m in models])


# ── J5 ─────────────────────────────────────────────────────────────────────────
def j5(rows, acc, models, gt_order, tag, B=200, seed=42):
    print("\n== J5 [%s]: order-aggregated BT vs forced-tie rule (n=%d live verdicts) ==" % (tag, len(rows)))
    tA = board_from(current_votes(rows), models)
    tB = board_from(order_votes(rows), models)
    rA, rB = rho(tA, acc, models), rho(tB, acc, models)
    oA, pA, aA = violations(tA, gt_order)
    oB, pB, aB = violations(tB, gt_order)
    print("  GT top-4 (key accuracy on frozen pool): %s" % " > ".join(gt_order))
    print("  A current rule : rho=%.4f | top-4 %s | pair viol %d adj %d" % (rA, " > ".join(oA), pA, aA))
    print("  B order-agg    : rho=%.4f | top-4 %s | pair viol %d adj %d" % (rB, " > ".join(oB), pB, aB))
    rng = random.Random(seed)
    diffs = []
    for _ in range(B):
        samp = [rows[rng.randrange(len(rows))] for _ in range(len(rows))]
        diffs.append(rho(board_from(order_votes(samp), models), acc, models)
                     - rho(board_from(current_votes(samp), models), acc, models))
    diffs.sort()
    print("  paired bootstrap rho(B)-rho(A): mean %+.4f, 95%% [%+.4f, %+.4f]"
          % (sum(diffs) / B, diffs[int(0.025 * B)], diffs[int(0.975 * B) - 1]))
    passed = rB >= rA and pB <= pA
    print("  REGISTERED J5 -> %s (rho %s, pair violations %d -> %d)"
          % ("PASS" if passed else "FAIL", "up" if rB > rA else ("equal" if rB == rA else "DOWN"), pA, pB))
    # descriptive: position bias per order and flip rate by GT gap
    first = [r for r in rows if r["w1"] in (0.0, 1.0)]
    second = [r for r in rows if r["w2"] in (0.0, 1.0)]
    # order 1 shows A first: first-shown wins iff w1 == 1; order 2 shows B first: first-shown wins iff w2 == 0
    p1 = sum(r["w1"] == 1.0 for r in first) / max(1, len(first))
    p2 = sum(r["w2"] == 0.0 for r in second) / max(1, len(second))
    print("  position: P(first-shown wins | decisive) order1 %.3f (n=%d), order2 %.3f (n=%d); pooled %.3f"
          % (p1, len(first), p2, len(second), (p1 * len(first) + p2 * len(second)) / max(1, len(first) + len(second))))
    # scheduler asymmetry check: how often is ModelA the GT-weaker model?
    weakerA = sum(acc[r["a"]] < acc[r["b"]] for r in rows) / len(rows)
    print("  scheduler: ModelA is the GT-weaker model in %.1f%% of matches (explains raw WinAFirst skew)" % (100 * weakerA))
    bins = [(0, 0.02), (0.02, 0.05), (0.05, 0.10), (0.10, 0.20), (0.20, 1.0)]
    print("  flip rate by |GT accuracy gap|:")
    for lo, hi in bins:
        sub = [r for r in rows if lo <= abs(acc[r["a"]] - acc[r["b"]]) < hi]
        if sub:
            print("    [%.2f,%.2f) n=%5d flip %.3f  emitted-tie %.3f"
                  % (lo, hi, len(sub), sum(r["flip"] for r in sub) / len(sub),
                     sum(r["src"] in ("JUDGE_EMITTED", "SEMANTIC_OVERRIDE") for r in sub) / len(sub)))
    return passed


# ── J4 ─────────────────────────────────────────────────────────────────────────
def lc_bt(rows, L, models):
    """Logistic BT with a length-difference covariate; last model is the reference (theta=0)."""
    idx = {m: i for i, m in enumerate(models)}
    k = len(models) - 1
    X, Y, W = [], [], []
    for r in rows:
        la, lb = L.get((r["q"], r["a"])), L.get((r["q"], r["b"]))
        if la is None or lb is None:
            continue
        x = np.zeros(k + 1)
        if idx[r["a"]] < k: x[idx[r["a"]]] += 1
        if idx[r["b"]] < k: x[idx[r["b"]]] -= 1
        x[k] = (la - lb) / 1000.0
        if r["w"] == "TIE":
            X += [x, x]; Y += [1.0, 0.0]; W += [0.5, 0.5]
        else:
            X.append(x); Y.append(1.0 if r["w"] == r["a"] else 0.0); W.append(1.0)
    X, Y, W = np.array(X), np.array(Y), np.array(W)
    beta = np.zeros(k + 1)
    for _ in range(60):
        p = 1 / (1 + np.exp(-np.clip(X @ beta, -30, 30)))
        g = X.T @ (W * (Y - p))
        H = (X * (W * p * (1 - p))[:, None]).T @ X + 1e-9 * np.eye(k + 1)
        step = np.linalg.solve(H, g)
        beta += step
        if np.max(np.abs(step)) < 1e-9:
            break
    cov = np.linalg.inv(H)
    theta = {m: (beta[idx[m]] if idx[m] < k else 0.0) for m in models}
    return theta, beta[k], math.sqrt(cov[k, k]), len(Y)


def j4(rows, acc, L, models, gt_order, tag):
    print("\n== J4 [%s]: length-covariate BT (n=%d live verdicts) ==" % (tag, len(rows)))
    raw = board_from(current_votes(rows), models)
    oR, pR, aR = violations(raw, gt_order)
    theta, bl, se, n = lc_bt(rows, L, models)
    oL, pL, aL = violations(theta, gt_order)
    print("  GT top-4: %s" % " > ".join(gt_order))
    print("  raw BT : rho=%.4f | top-4 %s | pair viol %d adj %d" % (rho(raw, acc, models), " > ".join(oR), pR, aR))
    print("  LC-BT  : rho=%.4f | top-4 %s | pair viol %d adj %d | beta_len %+.4f/1k (z=%+.1f, n=%d)"
          % (rho(theta, acc, models), " > ".join(oL), pL, aL, bl, bl / se, n))
    print("  -- length-matched top-4 refit, threshold sweep (descriptive) --")
    for thr in (100, 200, 300, 500, 800):
        sub = [r for r in rows if r["a"] in TOP4 and r["b"] in TOP4
               and (r["q"], r["a"]) in L and (r["q"], r["b"]) in L
               and abs(L[(r["q"], r["a"])] - L[(r["q"], r["b"])]) <= thr]
        if len(sub) < 50:
            print("    |dlen|<=%4d n=%5d (too few)" % (thr, len(sub))); continue
        t = board_from(current_votes(sub), TOP4)
        o, p, a = violations(t, gt_order)
        print("    |dlen|<=%4d n=%5d  %s  (pair viol %d adj %d)" % (thr, len(sub), " > ".join(o), p, a))
    return aL <= 1, abs(bl / se) >= 2


def main():
    r2, x12 = load_live(R2), load_live(X12)
    models = sorted({m for r in r2 for m in (r["a"], r["b"])})
    acc, L = gt_and_lengths(set(models))
    gt_order = sorted(TOP4, key=lambda m: -acc[m])
    print("ground truth (key accuracy on the frozen pool, %d models): %s"
          % (len(models), ", ".join("%s %.3f" % (m, acc[m]) for m in sorted(models, key=lambda m: -acc[m]))))
    j5_r2 = j5(r2, acc, models, gt_order, "R2")
    j5_x12 = j5(x12, acc, sorted({m for r in x12 for m in (r["a"], r["b"])}), gt_order, "x12")
    a_r2, b_r2 = j4(r2, acc, L, models, gt_order, "R2")
    a_x, b_x = j4(x12, acc, L, sorted({m for r in x12 for m in (r["a"], r["b"])}), gt_order, "x12")
    print("\nSUMMARY")
    print("  J5 registered (R2, primary dataset): %s | x12 (secondary): %s" % ("PASS" if j5_r2 else "FAIL", "PASS" if j5_x12 else "FAIL"))
    print("  J4 registered (<=1 adjacent violation in BOTH): %s | beta_len identified in both: %s"
          % ("PASS" if (a_r2 and a_x) else "FAIL", "yes" if (b_r2 and b_x) else "no"))


if __name__ == "__main__":
    main()


# ── exploratory (post-hoc, labelled): LC-BT on the top-4 subset only ─────────────
def j4_top4():
    r2, x12 = load_live(R2), load_live(X12)
    models = sorted({m for r in r2 for m in (r["a"], r["b"])})
    acc, L = gt_and_lengths(set(models))
    gt_order = sorted(TOP4, key=lambda m: -acc[m])
    print("\n== EXPLORATORY: LC-BT fitted on top-4 matches only (beta identified within the cluster) ==")
    for tag, rows in (("R2", r2), ("x12", x12)):
        sub = [r for r in rows if r["a"] in TOP4 and r["b"] in TOP4]
        raw = board_from(current_votes(sub), TOP4)
        theta, bl, se, n = lc_bt(sub, L, TOP4)
        oR, pR, _ = violations(raw, gt_order)
        oL, pL, _ = violations(theta, gt_order)
        both = [r for r in sub if r["w"] != "TIE"]
        print("  %s top-4 matches n=%d | raw %s (viol %d) | LC %s (viol %d) | beta_len %+.3f/1k z=%+.1f"
              % (tag, len(sub), " > ".join(oR), pR, " > ".join(oL), pL, bl, bl / se))
        # mean length per model on this subset's questions
        ml = {m: np.mean([L[(r["q"], m)] for r in sub if (r["q"], m) in L and m in (r["a"], r["b"])]) for m in TOP4}
        print("      mean answer length (chars): " + ", ".join("%s %.0f" % (m.split("-")[0], ml[m]) for m in gt_order))


if __name__ == "__main__" and "--top4" in sys.argv:
    j4_top4()


# ── J4b (registered in docs/judge_improvement_proposals.md, commit e840c8f, BEFORE this ran) ──
def lc_bt_tiered(rows, L, acc, models, cut=0.10):
    idx = {m: i for i, m in enumerate(models)}
    k = len(models) - 1
    X, Y, W = [], [], []
    for r in rows:
        la, lb = L.get((r["q"], r["a"])), L.get((r["q"], r["b"]))
        if la is None or lb is None:
            continue
        x = np.zeros(k + 2)
        if idx[r["a"]] < k: x[idx[r["a"]]] += 1
        if idx[r["b"]] < k: x[idx[r["b"]]] -= 1
        narrow = abs(acc[r["a"]] - acc[r["b"]]) < cut
        x[k if narrow else k + 1] = (la - lb) / 1000.0
        if r["w"] == "TIE":
            X += [x, x]; Y += [1.0, 0.0]; W += [0.5, 0.5]
        else:
            X.append(x); Y.append(1.0 if r["w"] == r["a"] else 0.0); W.append(1.0)
    X, Y, W = np.array(X), np.array(Y), np.array(W)
    beta = np.zeros(k + 2)
    for _ in range(80):
        p = 1 / (1 + np.exp(-np.clip(X @ beta, -30, 30)))
        g = X.T @ (W * (Y - p))
        H = (X * (W * p * (1 - p))[:, None]).T @ X + 1e-9 * np.eye(k + 2)
        step = np.linalg.solve(H, g)
        beta += step
        if np.max(np.abs(step)) < 1e-9:
            break
    cov = np.linalg.inv(H)
    theta = {m: (beta[idx[m]] if idx[m] < k else 0.0) for m in models}
    return theta, (beta[k], math.sqrt(cov[k, k])), (beta[k + 1], math.sqrt(cov[k + 1, k + 1]))


def pair_violations_all(theta, acc, models):
    ms = sorted(models, key=lambda m: -acc[m])
    return sum(1 for i in range(len(ms)) for j in range(i + 1, len(ms)) if theta[ms[i]] < theta[ms[j]])


def j4b():
    r2, x12 = load_live(R2), load_live(X12)
    models = sorted({m for r in r2 for m in (r["a"], r["b"])})
    acc, L = gt_and_lengths(set(models))
    gt_order = sorted(TOP4, key=lambda m: -acc[m])
    print("\n== J4b (registered e840c8f): LC-BT with beta_len x GT-gap tier (<0.10 narrow / >=0.10 wide) ==")
    prim = []
    for tag, rows in (("R2", r2), ("x12", x12)):
        ms = sorted({m for r in rows for m in (r["a"], r["b"])})
        raw = board_from(current_votes(rows), ms)
        theta, (bn, sn), (bw, sw) = lc_bt_tiered(rows, L, acc, ms)
        vr, vl = pair_violations_all(raw, acc, ms), pair_violations_all(theta, acc, ms)
        oR, pR, _ = violations(raw, gt_order)
        oL, pL, _ = violations(theta, gt_order)
        n_narrow = sum(abs(acc[r["a"]] - acc[r["b"]]) < 0.10 for r in rows)
        print("  %s: beta_narrow %+.3f/1k (z=%+.1f, n=%d) | beta_wide %+.3f/1k (z=%+.1f) | ratio %.1fx"
              % (tag, bn, bn / sn, n_narrow, bw, bw / sw, bn / bw if bw else float("inf")))
        print("      12-model board pairwise violations vs GT: raw %d -> tiered-LC %d (of %d pairs) | rho %.4f -> %.4f"
              % (vr, vl, len(ms) * (len(ms) - 1) // 2, rho(raw, acc, ms), rho(theta, acc, ms)))
        print("      top-4: raw %s (viol %d) | tiered-LC %s (viol %d)" % (" > ".join(oR), pR, " > ".join(oL), pL))
        prim.append(vl < vr)
    print("  REGISTERED J4b PRIMARY (violations strictly below raw on BOTH): %s" % ("PASS" if all(prim) else "FAIL"))


if __name__ == "__main__" and "--j4b" in sys.argv:
    j4b()


# ── J4c (registered d024f0f BEFORE this ran): beta_len x key status (non-discriminative vs decidable) ──
def load_key_status(path):
    st = {}
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["Rationale"].startswith("Reconstructed"):
                continue
            ca, cb = r["CorrectA"] == "true", r["CorrectB"] == "true"
            st[(int(r["QueryId"]), r["ModelA"], r["ModelB"])] = "decidable" if ca != cb else "nondisc"
    return st


def lc_bt_keyed(rows, L, status, models):
    idx = {m: i for i, m in enumerate(models)}
    k = len(models) - 1
    X, Y, W = [], [], []
    for r in rows:
        la, lb = L.get((r["q"], r["a"])), L.get((r["q"], r["b"]))
        s = status.get((r["q"], r["a"], r["b"]))
        if la is None or lb is None or s is None:
            continue
        x = np.zeros(k + 2)
        if idx[r["a"]] < k: x[idx[r["a"]]] += 1
        if idx[r["b"]] < k: x[idx[r["b"]]] -= 1
        x[k if s == "nondisc" else k + 1] = (la - lb) / 1000.0
        if r["w"] == "TIE":
            X += [x, x]; Y += [1.0, 0.0]; W += [0.5, 0.5]
        else:
            X.append(x); Y.append(1.0 if r["w"] == r["a"] else 0.0); W.append(1.0)
    X, Y, W = np.array(X), np.array(Y), np.array(W)
    beta = np.zeros(k + 2)
    for _ in range(80):
        p = 1 / (1 + np.exp(-np.clip(X @ beta, -30, 30)))
        g = X.T @ (W * (Y - p))
        H = (X * (W * p * (1 - p))[:, None]).T @ X + 1e-9 * np.eye(k + 2)
        step = np.linalg.solve(H, g)
        beta += step
        if np.max(np.abs(step)) < 1e-9:
            break
    cov = np.linalg.inv(H)
    theta = {m: (beta[idx[m]] if idx[m] < k else 0.0) for m in models}
    return theta, (beta[k], math.sqrt(cov[k, k])), (beta[k + 1], math.sqrt(cov[k + 1, k + 1]))


def j4c():
    r2, x12 = load_live(R2), load_live(X12)
    models = sorted({m for r in r2 for m in (r["a"], r["b"])})
    acc, L = gt_and_lengths(set(models))
    gt_order = sorted(TOP4, key=lambda m: -acc[m])
    print("\n== J4c (registered d024f0f): LC-BT with beta_len x key status (non-discriminative / decidable) ==")
    prim, sec = [], None
    for tag, rows, path in (("R2", r2, R2), ("x12", x12, X12)):
        ms = sorted({m for r in rows for m in (r["a"], r["b"])})
        status = load_key_status(path)
        raw = board_from(current_votes(rows), ms)
        theta, (bn, sn), (bd, sd) = lc_bt_keyed(rows, L, status, ms)
        vr, vl = pair_violations_all(raw, acc, ms), pair_violations_all(theta, acc, ms)
        oR, pR, _ = violations(raw, gt_order)
        oL, pL, aL = violations(theta, gt_order)
        n_nd = sum(1 for r in rows if status.get((r["q"], r["a"], r["b"])) == "nondisc")
        print("  %s: beta_nondisc %+.3f/1k (z=%+.1f, n=%d) | beta_decidable %+.3f/1k (z=%+.1f) | ratio %.1fx"
              % (tag, bn, bn / sn, n_nd, bd, bd / sd, bn / bd if bd else float("inf")))
        print("      12-model violations vs GT: raw %d -> keyed-LC %d | rho %.4f -> %.4f"
              % (vr, vl, rho(raw, acc, ms), rho(theta, acc, ms)))
        print("      top-4: raw %s (viol %d) | keyed-LC %s (viol %d, adj %d)"
              % (" > ".join(oR), pR, " > ".join(oL), pL, aL))
        prim.append(vl < vr)
        if tag == "R2":
            sec = aL <= 1 and pL <= 1
    print("  REGISTERED J4c PRIMARY (violations strictly below raw on BOTH): %s | SECONDARY (R2 top-4 within one adjacent swap): %s"
          % ("PASS" if all(prim) else "FAIL", "PASS" if sec else "FAIL"))


if __name__ == "__main__" and "--j4c" in sys.argv:
    j4c()
