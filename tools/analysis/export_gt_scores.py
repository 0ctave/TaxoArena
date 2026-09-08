"""Export ground-truth accuracy per model per MMLU-Pro domain.

Provenance: eval_results.is_correct in mmlu_pro_dataset_cache_v2.db — the upstream
MMLU-Pro evaluation outputs, not anything this project computed. Two views are
written because they differ for the weak models:

  acc            is_correct as stored. A blank/unparsed `pred` counts as incorrect.
  acc_parsed     blanks excluded from the denominator.

Blank-pred rates run 8-19% for four models and under 1% for the rest, so `acc`
deflates those four by 4-11 points. The RANKING is identical under both views
(12/12 positions unchanged on the reserved pool), which is why rank-based results
in the thesis are unaffected. Both columns are exported so the reader can see it.

Rows are written for the reserved (held-out) pool and for the full corpus
separately; the thesis uses reserved.
"""
import sqlite3, csv, os

DB = 'mmlu_pro_dataset_cache_v2.db'
OUT = 'model_domain_scores.csv'

ROSTER = [
    'gemini-3.1-pro_5-shots', 'iask_pro', 'arx_3', 'claude-3-5-sonnet-20241022',
    'claude.3.5.sonnet', 'gpt-4o-2024-08-06', 'deepseek-chat-v2_5', 'gpt-4o-mini',
    'Qwen1.5-72B-Chat', 'Meta-Llama-3-8B-Instruct', 'Qwen1.5-14B-Chat', 'Meta-Llama-3-8B',
]
ROSTER[4] = 'claude-3.5-sonnet'

con = sqlite3.connect(DB)
import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from pool_guard import assert_frozen_pool; assert_frozen_pool(con)  # is_reserved mirrors the ACTIVE pool
rows = []
for split, where in (('reserved', 'AND is_reserved=1'), ('full', '')):
    for m in ROSTER:
        q = f"""SELECT category, pred, is_correct FROM eval_results
                WHERE model_name=? {where}"""
        by = {}
        for cat, pred, ic in con.execute(q, (m,)):
            d = by.setdefault(cat, [0, 0, 0])          # n, correct, blank
            d[0] += 1
            d[1] += ic
            if pred is None or not str(pred).strip():
                d[2] += 1
        # per-domain rows
        for cat in sorted(by):
            n, c, b = by[cat]
            parsed = n - b
            rows.append({
                'split': split, 'model': m, 'domain': cat, 'n_questions': n,
                'n_correct': c, 'n_blank_pred': b,
                'acc': round(c / n, 4) if n else '',
                'acc_parsed': round(c / parsed, 4) if parsed else '',
                'blank_rate': round(b / n, 4) if n else '',
            })
        # overall row
        n = sum(v[0] for v in by.values())
        c = sum(v[1] for v in by.values())
        b = sum(v[2] for v in by.values())
        parsed = n - b
        rows.append({
            'split': split, 'model': m, 'domain': 'ALL', 'n_questions': n,
            'n_correct': c, 'n_blank_pred': b,
            'acc': round(c / n, 4) if n else '',
            'acc_parsed': round(c / parsed, 4) if parsed else '',
            'blank_rate': round(b / n, 4) if n else '',
        })

with open(OUT, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['split', 'model', 'domain', 'n_questions',
                                      'n_correct', 'n_blank_pred', 'acc',
                                      'acc_parsed', 'blank_rate'])
    w.writeheader()
    w.writerows(rows)

print(f'wrote {OUT}: {len(rows)} rows, {len(ROSTER)} models')
res = [r for r in rows if r['split'] == 'reserved']
print(f"reserved: {len({r['domain'] for r in res}) - 1} domains + ALL")

# console summary: reserved, per domain, ranked
print()
doms = sorted({r['domain'] for r in res if r['domain'] != 'ALL'})
hdr = 'model'.ljust(30) + ''.join(d[:9].rjust(10) for d in doms) + 'ALL'.rjust(9)
print(hdr)
for m in sorted(ROSTER, key=lambda m: -next(
        (r['acc'] for r in res if r['model'] == m and r['domain'] == 'ALL'), 0)):
    line = m[:29].ljust(30)
    for d in doms:
        v = next((r['acc'] for r in res if r['model'] == m and r['domain'] == d), None)
        line += (f'{v*100:9.1f}' if v != '' and v is not None else '        -') + ' '
    a = next((r['acc'] for r in res if r['model'] == m and r['domain'] == 'ALL'), '')
    line += f'{a*100:8.1f}' if a != '' else '       -'
    print(line)
