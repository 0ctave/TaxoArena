"""PROMPT-AUDIT — is the eval set's own ranking confounded by prompt configuration? (registered 2026-09-14)

  python tools/analysis/prompt_audit.py

Zero LLM calls. (1) catalogue by declared configuration; (2) within-family spread; (3) the CONTROLLED paired
estimate from REGEN (same model, same questions, two prompts); (4) which frontier gaps the ground truth cannot
safely support. The pool is addressed by its explicit id (there is no per-row flag), so a concurrent construction
cannot perturb it.
"""
import os, re, sys, math, sqlite3
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); sys.path.insert(0, HERE)
import rejudge_grok as rj
import pool_guard

POOL = "p2dca21ab5f4ef3ae"
SHOT = re.compile(r"(\d+)\s*-?shots?", re.I)


def config_of(name):
    m = SHOT.search(name)
    return "%s-shot (declared)" % m.group(1) if m else "undeclared"


def main():
    ev = sqlite3.connect("file:%s?mode=ro" % rj.EVAL_DB, uri=True)
    pool = {q for (q,) in ev.execute("SELECT question_id FROM reserved_pool WHERE pool_id=?", (POOL,))}
    stat = defaultdict(lambda: [0, 0, 0, 0])   # model -> [n, correct, trace chars, missing pred]
    for q, m, p, c, l in ev.execute("SELECT question_id, model_name, pred, is_correct, LENGTH(model_output) FROM eval_results"):
        if q not in pool or m == "Meta-Llama-3-70B-Instruct": continue
        s = stat[m]; s[0] += 1; s[1] += int(c or 0); s[2] += (l or 0); s[3] += 0 if (p or "").strip() else 1
    models = [m for m, s in stat.items() if s[0] > 0.95 * len(pool)]
    acc = {m: stat[m][1] / stat[m][0] for m in models}
    tl = {m: stat[m][2] / stat[m][0] for m in models}
    miss = {m: stat[m][3] / stat[m][0] for m in models}

    print("=== (1) CATALOGUE by declared prompt configuration (pool %s, %d models) ===" % (POOL, len(models)))
    byc = defaultdict(list)
    for m in models: byc[config_of(m)].append(m)
    for c in sorted(byc, key=lambda c: -max(acc[m] for m in byc[c])):
        ms = sorted(byc[c], key=lambda m: -acc[m])
        print("  %-20s n=%2d | accuracy %.3f..%.3f | mean trace %4.0f..%4.0f chars | missing pred %.1f%%..%.1f%%"
              % (c, len(ms), acc[ms[-1]], acc[ms[0]], min(tl[m] for m in ms), max(tl[m] for m in ms),
                 100 * min(miss[m] for m in ms), 100 * max(miss[m] for m in ms)))
        for m in ms[:6]: print("      %-34s %.3f | trace %4.0f | missing %.1f%%" % (m, acc[m], tl[m], 100 * miss[m]))

    print("\n=== (2) WITHIN-FAMILY spread (version and configuration are partly confounded in these names) ===")
    fam = defaultdict(list)
    for m in models:
        k = SHOT.sub("", m); k = re.sub(r"[_\-\(\)0-9:.]+", "", k).lower()
        fam[k].append(m)
    for k, v in sorted(fam.items()):
        if len(v) < 2: continue
        a = [acc[m] for m in v]
        print("  %-14s spread %.3f | %s" % (k[:14], max(a) - min(a), ", ".join("%s %.3f" % (m[:28], acc[m]) for m in sorted(v, key=lambda m: -acc[m]))))

    print("\n=== (3) CONTROLLED paired estimate: the SAME model, SAME questions, two prompts (REGEN) ===")
    try:
        old = {q: c for q, c in sqlite3.connect("file:%s?mode=ro" % os.path.join(ROOT, "experiment_results", "judge_solve", "grok-reasoning.db"), uri=True).execute("SELECT question_id, correct FROM answers")}
        new = {q: c for q, c in sqlite3.connect("file:%s?mode=ro" % os.path.join(ROOT, "experiment_results", "judge_solve", "grok-reasoning-cot.db"), uri=True).execute("SELECT question_id, correct FROM answers")}
        both = sorted(set(old) & set(new) & pool)
        b = sum(1 for q in both if old[q] and not new[q]); c_ = sum(1 for q in both if new[q] and not old[q])
        ao = sum(old[q] for q in both) / len(both); an = sum(new[q] for q in both) / len(both)
        se = math.sqrt((b + c_)) / len(both)
        print("  n=%d paired questions (REGEN complete: %d of 3,445 answered)" % (len(both), len(new)))
        print("  answer-only prompt %.3f | chain-of-thought prompt %.3f | paired difference %+.3f +- %.3f"
              % (ao, an, an - ao, se))
        print("  flips: answer-only right and CoT wrong %d | CoT right and answer-only wrong %d" % (b, c_))
        eff = abs(an - ao)
    except Exception as e:
        print("  REGEN comparison unavailable: %s" % str(e)[:90]); eff = None

    print("\n=== (4) IMPACT: frontier gaps against the controlled prompt effect ===")
    T4 = ["gemini-3.1-pro_5-shots", "arx_0314", "iask_pro", "gpt-4o-2024-08-06"]
    T4 = [m for m in T4 if m in acc]; T4.sort(key=lambda m: -acc[m])
    for i in range(len(T4) - 1):
        g = acc[T4[i]] - acc[T4[i + 1]]
        v = "" if eff is None else ("  <- SMALLER than the prompt effect: unsafe" if g < eff else ("  <- comparable to the prompt effect: marginal" if g < 2 * eff else "  <- safe"))
        print("  %-30s over %-24s gap %.3f%s" % (T4[i][:30], T4[i + 1][:24], g, v))
    if eff is not None:
        print("\n  controlled prompt effect used as the yardstick: %.3f" % eff)
    print("  NOTE: gemini-3.1-pro is the only one of these four whose name declares a shot count (5-shot).")


if __name__ == "__main__":
    pool_guard.assert_pool_of_record(pool_guard.MMLU_PRO_POOL)   # the pool of record, by id; fail loudly if it does not reproduce
    main()
