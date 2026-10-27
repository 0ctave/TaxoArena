"""LEAF-SIGNALS — what MMLU-Pro (plus our 46-model eval rows) can tell a judge about a specific leaf (zero calls).

For every leaf of the clean bareq512_s42 tree (leaf = nearest centroid on the 512-slice, all keyed
questions), compute from the DATA — not from an LLM's description — the signals a leaf-specific
guideline could carry, and test which of them vary between sibling leaves within an anchor (a
guideline is worth making leaf-specific only where the signal is leaf-specific):

  S1 answer form      share of numeric-option questions; typical number of options; option spacing
                      (median |ratio| between the correct value and its nearest distractor)
  S2 error signature  for numeric questions: distribution of wrong/correct ratios chosen by the 46
                      models (factors 2, 10, sign, near-miss <10%) — the cell's arithmetic traps
  S3 attractor        share of wrong answers that land on the single most-chosen distractor (a strong
                      attractor = a specific misconception the judge should be warned about)
  S4 tier gap         accuracy of the top-tier models minus the bottom tier — how much the cell
                      separates capability (where a judge's mistakes cost the most)
  S5 surface cues     within-leaf logistic association of correctness with output features (length,
                      final-answer line present, hedging words, formula density) — which surface cues
                      are honestly diagnostic in THIS cell and which are not
  S6 reference shape  reference-reasoning length and step count (what a correct derivation looks like)

Readout: per-anchor spread of each signal across its leaves vs the spread across anchors; a signal is
"leaf-specific" if its within-anchor variance is at least half of its total variance (ANOVA-style).
Also prints three example leaf cards (Math, Physics, Law) as the data would write them.

  python tools/analysis/leaf_guideline_signals.py
"""
import os, sys, re, json, sqlite3, math
from collections import defaultdict, Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import rejudge_grok as rj
import leaf_profile_evidence as lpe
import free_tests_f4_f7 as ff

TOP = ["gemini-3.1-pro_5-shots", "arx_0314", "iask_pro", "gpt-4o-2024-08-06", "deepseek-chat-v2_5"]
NUM = re.compile(r"^\s*[-+]?\$?\s*(\d[\d,]*\.?\d*|\.\d+)\s*(e[-+]?\d+)?\s*[a-zA-Z%°/^²³]*\s*$")
HEDGE = re.compile(r"\b(might|may|possibly|perhaps|likely|not sure|approximately|roughly|assume)\b", re.I)
FORMULA = re.compile(r"[=×÷√∑∫^]|\\frac|\bsqrt\b|\bln\b|\blog\b")
FINAL = re.compile(r"(final answer|the answer is|answer:|therefore|thus)", re.I)


def parse_num(o):
    m = NUM.match(o or "")
    if not m: return None
    try: return float(m.group(1).replace(",", "")) * (10 ** int(m.group(2)[1:]) if m.group(2) else 1)
    except Exception: return None


def main():
    models, G, qs, leaf, anc = lpe.assign_leaves()
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    meta = {}
    for q, o, a in ev.execute("SELECT question_id, options_json, gt_answer FROM eval_results WHERE model_name='gpt-4o-2024-08-06'"):
        try: meta[q] = (json.loads(o) if o else [], (a or "").strip().upper()[:1])
        except Exception: pass
    preds = defaultdict(dict); feats = defaultdict(dict)
    for q, m, p, out, c in ev.execute("SELECT question_id, model_name, pred, model_output, is_correct FROM eval_results WHERE model_name != 'Meta-Llama-3-70B-Instruct'"):
        preds[q][m] = (p or "").strip().upper()[:1]
        t = rj.unwrap_envelope(out or "")
        feats[q][m] = (len(t), int(bool(FINAL.search(t))), len(HEDGE.findall(t)), len(FORMULA.findall(t)) / max(1, len(t) / 1000), int(c or 0))
    mp = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    cot = {}
    for qt, c in mp.execute("SELECT question, cot_content FROM mmlu_pro"): cot[qt] = c or ""
    qtext = {q: t for q, t in ev.execute("SELECT question_id, question_text FROM eval_results WHERE model_name='gpt-4o-2024-08-06'")}
    by_leaf = defaultdict(list)
    for q in qs:
        if q in meta: by_leaf[leaf[q]].append(q)
    rows = []
    for l, lq in by_leaf.items():
        if len(lq) < 40: continue
        numeric = 0; spacing = []; ratios = Counter(); attractor = []; tiergap = []; feat_rows = []; cot_len = []; cot_steps = []; nopt = []
        for q in lq:
            opts, key = meta[q]; ki = "ABCDEFGHIJ".find(key)
            if ki < 0 or ki >= len(opts): continue
            nopt.append(len(opts))
            vals = [parse_num(o) for o in opts]
            kv = vals[ki] if ki < len(vals) else None
            wrong = Counter(p for m, p in preds[q].items() if p and p != key and "ABCDEFGHIJ".find(p) < len(opts))
            nw = sum(wrong.values())
            if nw: attractor.append(wrong.most_common(1)[0][1] / nw)
            if kv is not None and sum(v is not None for v in vals) >= len(vals) * 0.7:
                numeric += 1
                others = [abs(v / kv) for v in vals if v is not None and v != kv and kv != 0]
                if others: spacing.append(min(abs(math.log10(x)) for x in others if x > 0) if any(x > 0 for x in others) else 0)
                for p, k in wrong.items():
                    v = vals["ABCDEFGHIJ".find(p)]
                    if v is None or kv == 0: continue
                    r = v / kv
                    if r == 0: ratios["zero"] += k; continue
                    tag = ("sign" if r < 0 else "x2" if abs(math.log2(abs(r)) - 1) < 0.12 else "/2" if abs(math.log2(abs(r)) + 1) < 0.12 else
                           "x10" if abs(math.log10(abs(r)) - 1) < 0.05 else "/10" if abs(math.log10(abs(r)) + 1) < 0.05 else "near(<10%)" if abs(math.log10(abs(r))) < 0.041 else "other")
                    ratios[tag] += k
            top_acc = np.mean([G[m][q] for m in TOP if m in G]); bot_acc = np.mean([G[m][q] for m in models if m not in TOP])
            tiergap.append(top_acc - bot_acc)
            for m, f in feats[q].items():
                if m in G: feat_rows.append(f)
            c = cot.get(qtext.get(q, ""), "")
            if c: cot_len.append(len(c)); cot_steps.append(len(re.findall(r"(?m)^\s*(\d+\.|step|first|then|next|finally)", c, re.I)))
        F = np.array(feat_rows, dtype=float)
        cues = {}
        if len(F) > 200:
            y = F[:, 4]
            for j, name in enumerate(["length", "final_line", "hedges", "formula_density"]):
                x = F[:, j]
                if x.std() > 0: cues[name] = float(np.corrcoef(x, y)[0, 1])
        ratio_share = {k: v / max(1, sum(ratios.values())) for k, v in ratios.items()}
        rows.append(dict(leaf=l, anchor=anc[lq[0]], n=len(lq), numeric=numeric / len(lq), nopt=np.median(nopt) if nopt else 0,
                         spacing=np.median(spacing) if spacing else float("nan"), ratios=ratio_share, attractor=np.mean(attractor) if attractor else float("nan"),
                         tiergap=np.mean(tiergap), cues=cues, cot_len=np.median(cot_len) if cot_len else 0, cot_steps=np.median(cot_steps) if cot_steps else 0))
    print("== LEAF-SIGNALS: %d leaves (>= 40 keyed questions), clean bareq512_s42 tree ==" % len(rows))
    # leaf-specificity: within-anchor variance share
    def spec(getter, name):
        vals = [(r["anchor"], getter(r)) for r in rows if getter(r) == getter(r)]
        tot = np.var([v for _, v in vals]) if len(vals) > 2 else 0
        by = defaultdict(list)
        for a, v in vals: by[a].append(v)
        within = np.mean([np.var(v) for v in by.values() if len(v) >= 2]) if tot else 0
        print("  %-28s total sd %.3f | mean within-anchor sd %.3f | within/total variance %.2f -> %s" % (name, math.sqrt(tot), math.sqrt(within), within / tot if tot else 0, "LEAF-SPECIFIC" if tot and within / tot >= 0.5 else "anchor-level"))
    spec(lambda r: r["numeric"], "S1 numeric-option share")
    spec(lambda r: r["spacing"], "S1 option spacing (log10)")
    spec(lambda r: r["ratios"].get("x2", 0) + r["ratios"].get("/2", 0), "S2 factor-2 error share")
    spec(lambda r: r["ratios"].get("sign", 0), "S2 sign error share")
    spec(lambda r: r["ratios"].get("near(<10%)", 0), "S2 near-miss share")
    spec(lambda r: r["attractor"], "S3 attractor strength")
    spec(lambda r: r["tiergap"], "S4 tier gap")
    spec(lambda r: r["cues"].get("length", float("nan")), "S5 length-correctness corr")
    spec(lambda r: r["cues"].get("hedges", float("nan")), "S5 hedging-correctness corr")
    spec(lambda r: r["cues"].get("formula_density", float("nan")), "S5 formula-density corr")
    spec(lambda r: r["cot_steps"], "S6 reference steps")
    print("\n  Length as a cue: leaves where longer outputs are MORE often correct (corr > +0.15): %d | LESS often (corr < -0.05): %d | neutral: %d"
          % (sum(1 for r in rows if r["cues"].get("length", 0) > 0.15), sum(1 for r in rows if r["cues"].get("length", 0) < -0.05), sum(1 for r in rows if -0.05 <= r["cues"].get("length", 0) <= 0.15)))
    for want in ("Math", "Physics", "Law"):
        cand = [r for r in rows if r["anchor"] == want]
        if not cand: continue
        r = max(cand, key=lambda r: r["n"])
        rr = ", ".join("%s %.0f%%" % (k, 100 * v) for k, v in sorted(r["ratios"].items(), key=lambda x: -x[1])[:4])
        print("\n  --- example leaf card: %s / %s (n=%d) ---" % (r["anchor"], r["leaf"], r["n"]))
        print("  answer form: numeric options %.0f%% | options %.0f | correct-vs-nearest-distractor spacing 10^%.2f" % (100 * r["numeric"], r["nopt"], r["spacing"] if r["spacing"] == r["spacing"] else float("nan")))
        print("  error signature (46 models' wrong picks): %s | attractor: %.0f%% of wrong answers land on one distractor" % (rr or "n/a", 100 * r["attractor"]))
        print("  tier gap (top-5 minus rest): %+.2f | reference reasoning: %.0f chars, %.0f steps" % (r["tiergap"], r["cot_len"], r["cot_steps"]))
        print("  surface cues vs correctness: " + ", ".join("%s %+.2f" % (k, v) for k, v in r["cues"].items()))
    json.dump([{k: (v if not isinstance(v, float) or v == v else None) for k, v in r.items()} for r in rows], open(os.path.join(ROOT, "experiment_results", "leaf_guideline_signals.json"), "w"), default=float, indent=1)


if __name__ == "__main__":
    main()
