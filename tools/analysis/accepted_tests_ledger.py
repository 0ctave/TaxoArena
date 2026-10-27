"""The accounting guard shared by the two tests the author accepted on 2026-09-23 (plan Amendment 12): CANARY-EPOCH2-RUNG
(tools/analysis/canary_baseline.py --pass 3|4) and TRACE-TRUNCATION (tools/analysis/trace_truncation.py).

RULED by the registrar at b0b5d0d (docs/judge_v2_program.md L15188-L15206, "THE ACCOUNTING FILE"): the 2026-09-23 night ledger
(experiment_results/night_calls_2026-09-23.json, 4,060 at close) is NOT the count of record for calls posted later. The count
of record for a call is the ledger of its POSTING DATE, experiment_results/day_calls_<YYYY-MM-DD>.json (a JSON list, one row
per launch: test, launch, calls, ts), CREATED WRITE-ONCE when absent (mode "x") and otherwise only appended to (the old rows
are asserted to be an unchanged prefix of the new file). Before every posting launch the guard REFUSES on ANY of:
  (i)   the test's own registered ceiling (CANARY-EPOCH2-RUNG 1,200; TRACE-TRUNCATION 2,184), its posted calls counted as the
        LARGER of its own cache(s) (rows x 2) and its rows in every ledger (the 2026-09-23 file and every day_calls_*.json);
  (ii)  the 4,000-match rule (CONTEXT.md section 4 rule 5): the test's posted matches + this launch's <= 4,000;
  (iii) THE COMBINED STATEMENT: 4,060 (the closed 2026-09-23 total) + the calls posted by BOTH tests (each counted as in (i))
        + this launch <= 14,000.
All three numbers are printed on every launch, pass or refuse (rule 11), and returned so the outcome can print them too.
Pure standard library; no database is opened for writing; a cache is read with mode=ro.
"""
import glob
import json
import os
import sqlite3
import time

CLOSED_NIGHT_TOTAL = 4060                 # experiment_results/night_calls_2026-09-23.json at close (registrar, b0b5d0d)
NIGHT_FILE = "night_calls_2026-09-23.json"
COMBINED_CEILING = 14000
MATCH_RULE = 4000
CEILINGS = {"CANARY-EPOCH2-RUNG": 1260, "TRACE-TRUNCATION": 2184}   # CANARY 1,200 -> 1,248 -> 1,260: amendments CANARY-EPOCH2-RUNG-CEILING-1 and -2 (2026-09-24)
CEILINGS["ARCH-V2-INDUCE-RUBRIC-1"] = 6   # 3 attempts + 3 transport errors: ruling on finding 2 (eabbf45) as read by READY_induce_rubric_1 ruling 1 (a) (6b65efe); counted from the day ledgers
CEILINGS["ARCH-V2-INDUCE-RUBRIC-2"] = 6   # at most 6 invocations (3 attempts + 3 transport errors): the registration 7e13897 (programme L16326-L16348, COST AND CONSEQUENCE); counted from the day ledgers
CEILINGS["ARCH-V2-INDUCE-RUBRIC-3"] = 6   # at most 6 invocations (3 attempts + 3 transport errors): the registration 39c81c0 (programme L17008-L17110, COST AND CONSEQUENCE); counted from the day ledgers


def default_caches(root):
    """test -> the cache files whose rows are that test's posted dual-order matches (2 calls per row)."""
    x12 = os.path.join(root, "experiment_results", "x12_crossdomain")
    mc = os.path.join(root, "experiment_results", "multicorpus")
    return {"CANARY-EPOCH2-RUNG": [os.path.join(x12, "canary_baseline_pass3.db"), os.path.join(x12, "canary_baseline_pass4.db")],
            "TRACE-TRUNCATION": [os.path.join(mc, "trace_truncation.db")]}


CEILINGS["JUDGEBENCH-REASONING-SIDE"] = 1540   # posted calls, both arms (G + S1), transport retries included: the registration 6134573 (programme L17449-L17461, COST: 1,400 + 10% = 1,540 / 8,470 cce); counted from the day ledgers (tools/analysis/judgebench_side.py)
CEILINGS["JV2-RATE-PROBE"] = 400   # invocations (the unit of record; HTTP attempts are a diagnostic): the registration bf9d80b (programme L18979-L19094, 1.2 ACCOUNTING and THE ITEM: at most 398, ceiling 400; R7); enforced by its journal's cap trigger; counted from the day ledgers (tools/analysis/jv2_rate_probe.py)


def day_ledger_path(ledger_dir, day=None):
    return os.path.join(ledger_dir, "day_calls_%s.json" % (day or time.strftime("%Y-%m-%d")))


def _rows(path):
    if not os.path.exists(path):
        return []
    try:
        rows = json.load(open(path, encoding="utf-8"))
        for r in rows:
            int(r["calls"])
        return rows
    except Exception as e:  # noqa: BLE001
        raise SystemExit("[LEDGER] REFUSED: %s is unreadable (%s: %s); nothing is posted." % (path, type(e).__name__, str(e)[:120]))


def ledger_files(ledger_dir):
    files = sorted(glob.glob(os.path.join(ledger_dir, "day_calls_*.json")))
    night = os.path.join(ledger_dir, NIGHT_FILE)
    return ([night] if os.path.exists(night) else []) + files


def ledger_calls(test, ledger_dir):
    return sum(int(r["calls"]) for f in ledger_files(ledger_dir) for r in _rows(f) if r.get("test") == test)


def cache_calls(paths):
    n = 0
    for p in paths:
        if not os.path.exists(p):
            continue
        con = sqlite3.connect("file:%s?mode=ro" % os.path.abspath(p).replace("\\", "/"), uri=True)
        try:
            n += 2 * con.execute("SELECT COUNT(*) FROM verdicts").fetchone()[0]
        except sqlite3.Error:
            pass
        finally:
            con.close()
    return n


def posted(test, caches, ledger_dir):
    """(counted, from cache, from ledgers): the test's posted calls, the larger of the two sources."""
    c, l_ = cache_calls(caches.get(test, [])), ledger_calls(test, ledger_dir)
    return max(c, l_), c, l_


def guard(test, planned, caches, ledger_dir, what, refuse=True):
    """The three checks, printed on both branches; returns the numbers. SystemExit on any breach when refuse=True."""
    if test not in CEILINGS:
        raise SystemExit("[LEDGER] unknown test %r" % test)
    own, own_c, own_l = posted(test, caches, ledger_dir)
    both = {t: posted(t, caches, ledger_dir) for t in CEILINGS}
    combined = CLOSED_NIGHT_TOTAL + sum(v[0] for v in both.values()) + planned
    nums = dict(test=test, planned=planned, own=own, own_cache=own_c, own_ledger=own_l, ceiling=CEILINGS[test],
                own_after=own + planned, matches_after=(own + planned) // 2 + (own + planned) % 2, match_rule=MATCH_RULE,
                combined=combined, combined_ceiling=COMBINED_CEILING,
                both={t: v[0] for t, v in both.items()}, day_ledger=day_ledger_path(ledger_dir))
    breaches = []
    if nums["own_after"] > nums["ceiling"]:
        breaches.append("(i) %s would reach %d calls > its registered ceiling %d" % (test, nums["own_after"], nums["ceiling"]))
    if nums["matches_after"] > MATCH_RULE:
        breaches.append("(ii) %d matches > the %d-match rule" % (nums["matches_after"], MATCH_RULE))
    if combined > COMBINED_CEILING:
        breaches.append("(iii) %d (closed 09-23 total) + %s + this launch %d = %d > %d"
                        % (CLOSED_NIGHT_TOTAL, " + ".join("%s %d" % kv for kv in sorted(nums["both"].items())), planned, combined, COMBINED_CEILING))
    print("[ACCOUNT] %s (%s): (i) own %d (cache %d, ledgers %d) + %d = %d of %d | (ii) matches %d of %d | (iii) %d + %s + %d = %d of %d "
          "| ledger of record for today's posts: %s -> %s"
          % (test, what, own, own_c, own_l, planned, nums["own_after"], nums["ceiling"], nums["matches_after"], MATCH_RULE,
             CLOSED_NIGHT_TOTAL, " + ".join("%s %d" % kv for kv in sorted(nums["both"].items())), planned, combined, COMBINED_CEILING,
             nums["day_ledger"], "OK" if not breaches else "REFUSED: " + "; ".join(breaches)), flush=True)
    if breaches and refuse:
        raise SystemExit("[ACCOUNT] REFUSED, not trimmed (0 calls posted): " + "; ".join(breaches))
    nums["breaches"] = breaches
    return nums


def summary_line(test, caches, ledger_dir):
    """The three numbers for an outcome header (0 planned)."""
    n = guard(test, 0, caches, ledger_dir, "outcome", refuse=False)
    return ("ACCOUNTING (b0b5d0d): (i) %s %d of %d calls | (ii) %d of %d matches | (iii) %d + %s = %d of %d"
            % (test, n["own"], n["ceiling"], n["matches_after"], MATCH_RULE, CLOSED_NIGHT_TOTAL,
               " + ".join("%s %d" % kv for kv in sorted(n["both"].items())), n["combined"], COMBINED_CEILING))


def append(test, launch, calls, ledger_dir, day=None):
    """Append one row to the POSTING-DATE ledger: created write-once ("x") when absent; otherwise the old rows must be an
    unchanged prefix of what is written."""
    path = day_ledger_path(ledger_dir, day)
    row = {"test": test, "launch": launch, "calls": int(calls), "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
    if not os.path.exists(path):
        try:
            with open(path, "x", encoding="utf-8") as f:
                json.dump([row], f, indent=1)
            print("[ACCOUNT] created %s (write-once) with %d posted calls for %s %s" % (path, calls, test, launch), flush=True)
            return path
        except FileExistsError:
            pass
    old = _rows(path)
    new = old + [row]
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(new, f, indent=1)
    if json.load(open(tmp, encoding="utf-8"))[:len(old)] != old:
        raise SystemExit("[ACCOUNT] the append would not preserve %s's rows; nothing replaced" % path)
    os.replace(tmp, path)
    print("[ACCOUNT] appended %d posted calls for %s %s to %s" % (calls, test, launch, path), flush=True)
    return path
