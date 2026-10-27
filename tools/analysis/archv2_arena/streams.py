"""Pinned random streams (the D-1 lesson of CERT-UNDER-FILTER, review 605675c: "a registered decision should integrate
over, or pin and report, EVERY random stream that feeds it").

Every stream is NAMED; its seed is the first 8 bytes (big-endian) of sha256("<master>|<name>"), so a stream is a pure
function of the master string and its name, independent of the order in which streams are requested and of the
number of worker processes. A name may be requested ONCE per process (a second request would silently replay the same
draws into a second use); streams of record with a fixed seed (e.g. systematic_budget.build()'s random.Random(42)) are
logged under their own name with the seed of record. The full log is written beside every output (<out>.streams.tsv)
and summarised in the output by its count and its sha256.
"""
import hashlib
import random

import numpy as np


class Streams:
    def __init__(self, master):
        if not isinstance(master, str) or not master:
            raise SystemExit("[STREAMS] a non-empty master string is mandatory")
        self.master = master
        self.log = {}           # name -> (seed, kind)

    def seed(self, name):
        h = hashlib.sha256(("%s|%s" % (self.master, name)).encode("utf-8")).digest()
        return int.from_bytes(h[:8], "big")

    def _note(self, name, seed, kind):
        if name in self.log:
            raise SystemExit("[STREAMS] stream %r requested twice; every use gets its own name" % name)
        self.log[name] = (seed, kind)

    def np(self, name):
        s = self.seed(name)
        self._note(name, s, "numpy.PCG64")
        return np.random.Generator(np.random.PCG64(s))

    def py(self, name):
        s = self.seed(name)
        self._note(name, s, "random.Random")
        return random.Random(s)

    def of_record(self, name, seed):
        """A stream whose seed is fixed by the record (not derived from the master)."""
        self._note(name, int(seed), "random.Random (seed of record)")
        return random.Random(seed)

    def merge(self, other_log):
        """Adopt the log of a worker process (names are unique by construction: they carry the replicate index)."""
        for name, (seed, kind) in other_log.items():
            if name in self.log and self.log[name] != (seed, kind):
                raise SystemExit("[STREAMS] worker stream %r disagrees with the parent's" % name)
            self.log[name] = (seed, kind)

    def tsv(self):
        return "".join("%s\t%d\t%s\n" % (n, s, k) for n, (s, k) in sorted(self.log.items()))

    def digest(self):
        return hashlib.sha256(self.tsv().encode("utf-8")).hexdigest()

    def summary(self, head=6):
        names = sorted(self.log)
        out = ["  RANDOM STREAMS (master %r): %d named streams, log sha256 %s (full list in the .streams.tsv beside this"
               " file); seed = sha256(master|name)[:8] big-endian unless 'of record'" % (self.master, len(names), self.digest())]
        for n in names[:head]:
            out.append("    %-60s %20d  %s" % (n, self.log[n][0], self.log[n][1]))
        if len(names) > head:
            out.append("    ... %d more" % (len(names) - head))
        return out
