import sys, json, hashlib
sys.path.insert(0, r'Z:\FAC\TUBerlin\THESIS\TaxoArena\.claude\worktrees\agent-ac04323cdcce696f8\tools\analysis')
sys.path.insert(0, sys.argv[1])
from judge_v2 import induce_fitness as F
blob = open(sys.argv[1] + '/heldout.json', newline='').read()
assert hashlib.sha256(blob.encode()).hexdigest() == '4b44076086d53856ce6cba4651b9128cc068d69aae71c1f59e3075a845d94e29'
d = json.loads(blob)
print('V5', F.V5_VERSION, F.regex_list_sha256())
for grp, want in (('fit', True), ('unfit', False)):
    miss = 0
    for k in sorted(d[grp], key=lambda s: int(s.split(grp[0].upper())[-1])):
        r = F.v5(d[grp][k]); ok = r['pass'] == want; miss += (not ok)
        print(k, 'PASS' if r['pass'] else 'FAIL', 'ok' if ok else 'MISS', 'a=%s b=%s c=%s' % (r['a'], r['b'], r['c']), r['b_matches'])
    print('==', grp, 'misses', miss, 'of', len(d[grp]))
