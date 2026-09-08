"""Offline audit of answer-declaration redaction, for the option/answer-blind arm.

THE QUESTION. The arena judge never sees the reference answer or the option block
(verified: `buildJudgeUserPrompt` takes exactly (query, traceA, traceB), and
question_text carries an A-J option block in 1 of 400 sampled rows). But ~95% of
model traces END by declaring their own answer -- "The answer is (C)". So the judge
sees both models' answer letters and can pick the one it believes correct. That is
the mechanism behind "the judge decides on answer correctness".

A blind arm removes those declarations. This script asks whether that can be done
cleanly, BEFORE any judge call is spent, and reports the number that decides it:
the RESIDUAL LEAK RATE per model after redaction.

WHY PER MODEL AND NOT OVERALL. Redaction failure that correlates with capability
biases exactly the ranking the arm measures. A 95% overall rate is useless if it is
100% for the strong models and 83% for the weak ones -- the weak models would keep
declaring answers the strong ones had stripped. The per-model spread is the
acceptance criterion, not the mean.

WHAT COUNTS AS A LEAK. Only an explicit answer DECLARATION surviving redaction.
A trace that reasons its way to "$23,000" when option C is "$23,000" has revealed
its answer through reasoning, and that cannot be removed without destroying the
trace being judged. That channel is measured separately and reported as a bound,
not as something redaction is expected to fix.

METHOD. Two independent pattern sets, deliberately asymmetric:
  REDACT  -- precise, ordered, applied to fixpoint. What the blind arm would strip.
  DETECT  -- broad, recall-oriented, applied to the REDACTED text. Deliberately
             over-triggers, so residual leak is over-estimated rather than under.
Using the redactor as its own detector would report zero leak by construction.

Ground truth only: eval_results.pred is the model's own parsed answer, so a leak
can be checked against the letter the trace was actually scored on.
"""
import sqlite3, re, json, math, statistics, sys
from collections import defaultdict

# traces carry LaTeX and unicode maths; Windows cp1252 stdout cannot encode it
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

DB = 'mmlu_pro_dataset_cache_v2.db'
ROSTER = [
    'gemini-3.1-pro_5-shots', 'iask_pro', 'arx_3', 'claude-3.5-sonnet',
    'gpt-4o-2024-08-06', 'deepseek-chat-v2_5', 'gpt-4o-mini',
    'claude-3-5-sonnet-20241022', 'Qwen1.5-72B-Chat', 'Meta-Llama-3-8B-Instruct',
    'Qwen1.5-14B-Chat', 'Meta-Llama-3-8B',
]
ACCEPT_SPREAD = 2.0   # percentage points; the arm is clean below this

# ── REDACT: what the blind arm strips. Ordered, longest/most specific first. ────
REDACT = [
    r'(?i)\bthe\s+(?:correct\s+)?answer\s+is[:\s]*\(?[A-J]\)?[.\s]*',
    r'(?i)\b(?:so|thus|therefore|hence)[,\s]+the\s+answer\s+is[:\s]*\(?[A-J]\)?[.\s]*',
    r'(?i)\bfinal\s+answer[:\s]*\(?[A-J]\)?[.\s]*',
    r'(?i)\banswer[:\s]*\(?[A-J]\)?\s*$',
    r'(?i)\bthe\s+answer\s+(?:would\s+be|should\s+be|must\s+be)[:\s]*\(?[A-J]\)?[.\s]*',
    r'(?i)\b(?:option|choice)\s*\(?([A-J])\)?\s+is\s+(?:the\s+)?correct[.\s]*',
    r'(?i)\bcorrect\s+(?:option|choice|answer)\s+is[:\s]*\(?[A-J]\)?[.\s]*',
    r'(?i)\bi\s+(?:would\s+)?(?:choose|select|pick)[:\s]*\(?[A-J]\)?[.\s]*',
    r'(?i)\bwe\s+(?:choose|select|conclude)[:\s]*\(?[A-J]\)?[.\s]*',
    r'^\s*\(?([A-J])\)?[.\s]*$',
    r'(?m)^\s*\(?([A-J])\)?\s*$',
    r'\(([A-J])\)\s*$',
]

# ── DETECT: broad. Runs on redacted text; over-triggering is intended. ─────────
DETECT = [
    (r'(?i)answer\b.{0,30}?\b([A-J])\b',            'answer-near-letter'),
    (r'(?i)\b(?:option|choice)\b.{0,25}?\b([A-J])\b', 'option-near-letter'),
    (r'(?i)\b(?:correct|right)\b.{0,25}?\(([A-J])\)', 'correct-near-paren'),
    (r'(?i)\b(?:choose|select|pick|conclude)\b.{0,20}?\b([A-J])\b', 'choice-verb'),
    (r'\(([A-J])\)\s*[.!]?\s*$',                     'trailing-paren-letter'),
    (r'(?m)^\s*\(?([A-J])\)?[.\)]\s*$',              'lone-letter-line'),
]


def redact(text):
    """Strategy A, phrase-level. Apply REDACT to fixpoint.

    Returns (redacted_text, n_substitutions). Surgical: removes the declaration
    and leaves surrounding reasoning intact. Enumerating phrasings does not
    converge -- see the clustered survivors in the report -- so this is the
    conservative arm of the comparison, not the recommendation.
    """
    out, total = text, 0
    for _ in range(6):                     # fixpoint; 6 is far above observed need
        before = out
        for p in REDACT:
            out, n = re.subn(p, ' ', out)
            total += n
        if out == before:
            break
    return out, total


# Strategy B, sentence-level. Any sentence that names an option letter in an
# answer-bearing context is dropped whole. Higher recall than enumerating
# phrasings, at the cost of destroying some reasoning -- both costs are measured.
SENT_SPLIT = re.compile(r'(?<=[.!?])\s+|\n+')
SENT_KILL = re.compile(
    r'(?i)\b(?:option|choice|answer|answers)\b.{0,30}?\(?\b[A-J]\b\)?'
    r'|\(?\b[A-J]\b\)?.{0,20}?\bis\s+(?:the\s+)?(?:correct|right|answer)\b'
    r'|^\s*\(?[A-J]\)?[.\)]?\s*$'
)


def redact_sentences(text):
    """Strategy B. Returns (redacted_text, n_sentences_dropped, frac_chars_kept)."""
    sents = SENT_SPLIT.split(text)
    kept = [s for s in sents if not SENT_KILL.search(s)]
    dropped = len(sents) - len(kept)
    out = ' '.join(kept)
    frac = len(out) / len(text) if text else 1.0
    return out, dropped, frac


def detect(text):
    """Return list of (label, letter) answer declarations surviving in `text`."""
    hits = []
    for p, label in DETECT:
        for m in re.finditer(p, text):
            hits.append((label, m.group(1).upper()))
    return hits


def _pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    d = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / d if d else 0.0


def _ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0] * len(v)
    for j, i in enumerate(order):
        r[i] = j + 1
    return r


def main():
    db = sqlite3.connect(DB)
    import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
    from pool_guard import assert_frozen_pool; assert_frozen_pool(db)  # is_reserved mirrors the ACTIVE pool
    qs = ','.join('?' * len(ROSTER))
    rows = db.execute(
        f"""SELECT model_name, model_output, pred, gt_answer, options_json, is_correct
            FROM eval_results
            WHERE is_reserved=1 AND model_name IN ({qs})
              AND model_output IS NOT NULL AND model_output != ''""",
        ROSTER).fetchall()

    per = defaultdict(lambda: dict(n=0, declared=0, leak=0, nodecl=0,
                                   leak_is_pred=0, opt_restate=0, cuts=[],
                                   leakB=0, leakB_is_pred=0, keptB=[], ncorrect=0))
    samples = defaultdict(list)

    for model, out, pred, gt, opts, is_correct in rows:
        s = per[model]
        s['n'] += 1
        s['ncorrect'] += int(is_correct or 0)
        red, ncuts = redact(out)

        # Strategy B runs on the phrase-redacted text, so it is strictly stronger
        redB, _dropped, fracB = redact_sentences(red)
        s['keptB'].append(fracB)
        hitsB = detect(redB)
        if hitsB:
            s['leakB'] += 1
            if pred and any(l == str(pred).strip().upper() for _, l in hitsB):
                s['leakB_is_pred'] += 1

        declared = ncuts > 0
        if declared:
            s['declared'] += 1
            s['cuts'].append(ncuts)
        hits = detect(red)
        if hits:
            s['leak'] += 1
            # does a surviving declaration name the letter the model was scored on?
            if pred and any(l == str(pred).strip().upper() for _, l in hits):
                s['leak_is_pred'] += 1
            if len(samples[model]) < 6:
                frag = None
                for p, label in DETECT:
                    m = re.search(p, red)
                    if m:
                        a, b = max(0, m.start() - 55), min(len(red), m.end() + 25)
                        frag = (label, red[a:b].replace('\n', ' | '))
                        break
                samples[model].append((pred, frag))
        elif not declared:
            s['nodecl'] += 1

        # secondary, un-removable channel: the redacted trace restates the text of
        # the option the model picked. Reasoning, not a declaration -- reported as a
        # bound on what redaction can achieve, not as a redaction failure.
        try:
            o = json.loads(opts) if opts else []
        except Exception:
            o = []
        if o and pred and str(pred).strip().upper() in list('ABCDEFGHIJ'):
            i = ord(str(pred).strip().upper()) - 65
            if 0 <= i < len(o):
                t = str(o[i]).strip()
                if len(t) >= 12 and t.lower() in red.lower():
                    s['opt_restate'] += 1

    print('TRACE REDACTION AUDIT -- answer-declaration removal, held-out pool')
    print('%d traces, %d models\n' % (len(rows), len(per)))
    print('%-28s %6s %9s %9s %9s %9s' % (
        'model', 'n', 'declared', 'LEAK', 'leak=pred', 'no-decl'))
    print('-' * 76)

    leaks = []
    tot = dict(n=0, declared=0, leak=0, nodecl=0, leak_is_pred=0, opt_restate=0)
    for m in ROSTER:
        if m not in per:
            print('%-28s  (no rows)' % m)
            continue
        s = per[m]
        lr = 100.0 * s['leak'] / s['n']
        leaks.append((lr, m))
        for k in tot:
            tot[k] += s[k]
        print('%-28s %6d %8.1f%% %8.2f%% %8.2f%% %8.1f%%' % (
            m, s['n'], 100.0 * s['declared'] / s['n'], lr,
            100.0 * s['leak_is_pred'] / s['n'], 100.0 * s['nodecl'] / s['n']))

    print('-' * 76)
    print('%-28s %6d %8.1f%% %8.2f%% %8.2f%% %8.1f%%' % (
        'ALL', tot['n'], 100.0 * tot['declared'] / tot['n'],
        100.0 * tot['leak'] / tot['n'], 100.0 * tot['leak_is_pred'] / tot['n'],
        100.0 * tot['nodecl'] / tot['n']))

    leaks.sort()
    spread = leaks[-1][0] - leaks[0][0]
    print('\nSTRATEGY A (phrase-level) leak spread: %.2f pp  (%s %.2f%% .. %s %.2f%%)'
          % (spread, leaks[0][1], leaks[0][0], leaks[-1][1], leaks[-1][0]))

    print('\n\nSTRATEGY B -- sentence-level: drop any sentence naming an option letter')
    print('%-28s %6s %9s %9s %10s' % ('model', 'n', 'LEAK', 'leak=pred', 'text kept'))
    print('-' * 66)
    leaksB = []
    totB = dict(n=0, leakB=0, leakB_is_pred=0)
    keptall = []
    for m in ROSTER:
        if m not in per:
            continue
        s = per[m]
        lr = 100.0 * s['leakB'] / s['n']
        leaksB.append((lr, m))
        keptall += s['keptB']
        for k in totB:
            totB[k] += s[k]
        print('%-28s %6d %8.2f%% %8.2f%% %9.1f%%' % (
            m, s['n'], lr, 100.0 * s['leakB_is_pred'] / s['n'],
            100.0 * statistics.mean(s['keptB'])))
    print('-' * 66)
    print('%-28s %6d %8.2f%% %8.2f%% %9.1f%%' % (
        'ALL', totB['n'], 100.0 * totB['leakB'] / totB['n'],
        100.0 * totB['leakB_is_pred'] / totB['n'], 100.0 * statistics.mean(keptall)))

    leaksB.sort()
    spreadB = leaksB[-1][0] - leaksB[0][0]
    print('\nSTRATEGY B broad-leak spread: %.2f pp  (%s %.2f%% .. %s %.2f%%)'
          % (spreadB, leaksB[0][1], leaksB[0][0], leaksB[-1][1], leaksB[-1][0]))

    # ── ACCEPTANCE TEST ────────────────────────────────────────────────────────
    # The broad LEAK column deliberately over-triggers (units, few-shot echoes,
    # boilerplate), so it is a ceiling, not the decision. A surviving letter only
    # biases the judge if it is the letter that model was SCORED on: leak=pred.
    # And what breaks the arm is not the level but the SLOPE -- a residue that
    # tracks capability shifts the ranking being measured. So the test is
    # (i) leak=pred spread under the bar, and (ii) no correlation with accuracy.
    acc, lk = [], []
    for m in ROSTER:
        if m not in per:
            continue
        s = per[m]
        acc.append(100.0 * s['ncorrect'] / s['n'])
        lk.append(100.0 * s['leakB_is_pred'] / s['n'])
    r = _pearson(acc, lk)
    rs = _pearson(_ranks(acc), _ranks(lk))
    spread_p = max(lk) - min(lk)
    print('\nACCEPTANCE TEST (leak=pred, Strategy B)')
    print('  overall              %.2f%%' % (100.0 * totB['leakB_is_pred'] / totB['n']))
    print('  worst model          %.2f%%' % max(lk))
    print('  spread across roster %.2f pp   (bar: < %.1f pp)' % (spread_p, ACCEPT_SPREAD))
    print('  corr with accuracy   pearson %+.3f, spearman %+.3f  (n=%d)'
          % (r, rs, len(acc)))
    print('  mean text retained   %.1f%%' % (100.0 * statistics.mean(keptall)))
    clean = spread_p < ACCEPT_SPREAD and abs(r) < 0.5
    print('\nVERDICT: %s' % (
        'CLEAN -- full %d-model roster usable for the blind arm' % len(acc)
        if clean else 'NOT CLEAN -- restrict the roster'))

    print('\nSecondary channel (NOT removable by redaction):')
    print('  redacted trace restates the text of the option the model picked: '
          '%.1f%% overall' % (100.0 * tot['opt_restate'] / tot['n']))
    print('  This is reasoning revealing an answer, not a declaration. It bounds')
    print('  how blind any blind arm can be and must be reported with the result.')

    print('\nHand-audit samples (surviving declarations, redacted text):')
    for m in ROSTER:
        if samples.get(m):
            print('\n  == %s ==' % m)
            for pred, frag in samples[m][:3]:
                if frag:
                    print('    pred=%s  [%s]  ...%s...' % (pred, frag[0], frag[1]))


if __name__ == '__main__':
    sys.exit(main())
