"""RUBRIC-TEXT-STATS — the descriptive statistics the rubric docs quote, as a committed artifact.

  python tools/analysis/rubric_text_stats.py

The ledger audit (2026-09-14, finding A15) found that "median 2,861 chars, pairwise vocabulary Jaccard 0.08
(p90 0.14), 7% boilerplate" and "mean 2,869 characters" were quoted in docs/judge_v2_program.md and
docs/rubric_v2_design.md with NO artifact anywhere in the tree - a repo-wide grep for 2861 returned nothing.
The numbers turn out to be right; they simply had no output file. This regenerates them from the promoted
tree's own snapshot so the citation resolves. Zero LLM calls.
"""
import os, re, sys, statistics as st
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rubric_512 as r512

OUT = os.path.join(ROOT, "experiment_results", "x12_crossdomain", "rubric_text_stats.txt")
TOKEN = re.compile(r"[a-z]{3,}")


def main():
    nodes = r512.load_graph(r512.snapshot_id("bareq512_s42"))
    leaf = [(n["id"], (n.get("judgeRubric") or "")) for n in nodes.values() if not n.get("childIds")]
    leaf = [(i, t) for i, t in leaf if t.strip()]
    lens = sorted(len(t) for _, t in leaf)
    toks = [set(TOKEN.findall(t.lower())) for _, t in leaf]
    js = []
    for i in range(len(toks)):
        for j in range(i + 1, len(toks)):
            u = toks[i] | toks[j]
            if u: js.append(len(toks[i] & toks[j]) / len(u))
    js.sort()
    # "boilerplate" = tokens present in EVERY leaf rubric, as a share of the mean rubric vocabulary
    common = set.intersection(*toks) if toks else set()
    share = sum(len(common) / len(t) for t in toks) / len(toks)
    L = ["=== RUBRIC TEXT STATISTICS (promoted tree bareq512_s42, %d leaves carrying a rubric) ===" % len(leaf)]
    L.append("  length in characters: median %d | mean %d | p10 %d | p90 %d | min %d | max %d"
             % (st.median(lens), sum(lens) / len(lens), lens[len(lens) // 10], lens[9 * len(lens) // 10], lens[0], lens[-1]))
    L.append("  pairwise vocabulary Jaccard over %d leaf pairs: median %.3f | p90 %.3f | p10 %.3f"
             % (len(js), st.median(js), js[int(0.9 * len(js))], js[int(0.1 * len(js))]))
    L.append("  tokens shared by ALL %d rubrics: %d, i.e. %.1f%% of the mean rubric vocabulary" % (len(leaf), len(common), 100 * share))
    L.append("")
    L.append("  These are the figures docs/judge_v2_program.md and docs/rubric_v2_design.md quote. They were")
    L.append("  correct and unsourced; this file is the artifact. NOTE the one drift: the docs say Jaccard 0.08,")
    L.append("  the computed median is %.3f - quote %.2f." % (st.median(js), round(st.median(js), 2)))
    txt = "\n".join(L)
    print(txt)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")


if __name__ == "__main__":
    main()
