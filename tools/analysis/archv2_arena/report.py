"""Output discipline: every output is WRITE-ONCE (refused if the path exists; opened with mode "x"), LF, and its first
line states that the readout is UNREGISTERED. Every printed decision word comes from a branch the selftest executes;
branch ids are counted in HITS so a selftest can require each one to have fired.
[REGISTERED 2026-09-24 at d6129cf (ARCH-V2-G22 and ARCH-V2-G23, docs/judge_v2_program.md L15208-L15265), inserted by
the engine-coder; the text above is kept and read with this bracket: the bars are registered and printed as such, a
record run uses the registered masters (ARCHV2-G22-REC-1 / ARCHV2-G23-REC-1) and R = 1,000, other runs print DEV RUN.]
"""
import os
import sys
from collections import defaultdict

HITS = defaultdict(int)


def hit(branch):
    HITS[branch] += 1
    return branch


class Out:
    def __init__(self, path, echo=True):
        self.path = path
        self.lines = []
        self.echo = echo
        if path is not None and os.path.exists(path):
            hit("WRITE_ONCE.REFUSED")
            raise SystemExit("[WRITE-ONCE] %s exists; an output is never overwritten. Refused." % path)

    def __call__(self, *lines):
        for s in lines:
            self.lines.append(s)
            if self.echo:
                print(s, flush=True)

    def text(self):
        return "\n".join(self.lines) + "\n"

    def write(self, streams=None):
        if self.path is None:
            return None
        write_once(self.path, self.text())
        if streams is not None:
            write_once(self.path + ".streams.tsv", streams.tsv())
        return self.path


def write_once(path, text):
    if os.path.exists(path):
        hit("WRITE_ONCE.REFUSED")
        raise SystemExit("[WRITE-ONCE] %s exists; an output is never overwritten. Refused." % path)
    d = os.path.dirname(os.path.abspath(path))
    if not os.path.isdir(d):
        raise SystemExit("[WRITE-ONCE] the directory %s does not exist" % d)
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)
    hit("WRITE_ONCE.WRITTEN")


def need(cond, msg):
    """A guard that holds under python -O (never an assert)."""
    if not cond:
        raise SystemExit("[CHECK] " + msg)


def quantiles(v, qs=(0.025, 0.5, 0.975)):
    import numpy as np
    v = np.asarray([x for x in v if x == x], dtype=float)
    if v.size == 0:
        return [float("nan")] * len(qs)
    return [float(np.quantile(v, q)) for q in qs]


def argv_line():
    return "  argv: " + " ".join(sys.argv)
