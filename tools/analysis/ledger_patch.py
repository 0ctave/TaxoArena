"""ledger_patch.py - the ONLY safe way to edit docs/test_ledger.html (2026-09-17).

The ledger is patched by insertion. This module gives the record-keeper agent the helpers every v-patch since
v101 has used, with the two defects those patches hit already fixed:
  * a row's OUTCOME cell is found by structure (the cell before <td class="ev">), never by counting six cells
    (P5 is a four-cell row: the v93 patch put a note into LEAF-SS's row that way);
  * the version stamp uses the literal U+00B7 middle dot, not an entity (the v71-v76 stamps never applied).

Usage (from the repo root):
    import ledger_patch as lp
    L = lp.Ledger()                       # loads docs/test_ledger.html
    L.insert_outcome("KEY-TIE-DECLINE", "<b>[CORRECTED 2026-09-17]</b> ... ")     # bracket into the outcome cell
    L.add_row_before("FRAMEWORK", row_html)                                       # section 7 is newest-first
    L.stamp("v111", "<b>v111</b> (2026-09-17): what landed ...")                  # bumps the meta line, adds the note
    L.audit()                               # undefined chips, duplicate ids, row count; raises on a defect
    L.write()                               # writes the ledger (LF) and the scratchpad copy if SCRATCH is set

Chips: only the CSS classes ok / run / plan / warn / null exist; the chip text carries the narrative's qualifier
(PASS, FAIL, UNDETERMINED, DESCRIPTIVE, HELD, WITHDRAWN ...). Section-7 rows have SEVEN cells: id, question,
design, criteria (class nums), status (chips), observed (class nums), evidence (class ev). Entities, not raw
< > &; &mdash; not the em-dash character. Nothing is ever deleted: a correction is a dated bracket appended
into the observed cell; the last bracket wins.
"""
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LEDGER = os.path.join(ROOT, "docs", "test_ledger.html")
SCRATCH = os.environ.get("LEDGER_SCRATCH_COPY")   # optional second write target (the artifact publish file)
CHIP_CLASSES = {"ok", "run", "plan", "warn", "null"}


class Ledger:
    def __init__(self, path=LEDGER):
        self.path = path
        self.s = io.open(path, encoding="utf-8").read()

    # -- lookup -----------------------------------------------------------------------------------------------
    def rows(self, tid):
        return list(re.finditer(r'<tr><td class="id">%s</td>.*?</tr>' % re.escape(tid), self.s, re.S))

    def row(self, tid, which=0):
        ms = self.rows(tid)
        if not ms:
            raise KeyError("no row with id %r" % tid)
        return ms[which]

    def version(self):
        m = re.search(r'<p class="meta">v(\d+) ·', self.s)
        return int(m.group(1)) if m else None

    # -- edits (insertion only) ---------------------------------------------------------------------------------
    def insert_outcome(self, tid, html, which=0):
        """Insert at the START of the row's observed cell (the cell before <td class="ev">); for a row without an
        ev cell, the last cell. Safe for four-cell and seven-cell rows alike."""
        m = self.row(tid, which)
        r = m.group(0)
        cells = list(re.finditer(r"<td[^>]*>", r))
        ev = r.rfind('<td class="ev">')
        tgt = [c for c in cells if c.start() < ev][-1] if ev >= 0 else cells[-1]
        r2 = r[: tgt.end()] + html + r[tgt.end():]
        self.s = self.s[: m.start()] + r2 + self.s[m.end():]

    def replace_chip(self, tid, old_chip_html, new_chip_html, which=0):
        """Swap one chip's HTML inside a row (e.g. RUNNING -> SETTLED). Old text stays recoverable in git; use a
        bracket in the observed cell to say why."""
        m = self.row(tid, which)
        r = m.group(0)
        if r.count(old_chip_html) != 1:
            raise ValueError("chip %r occurs %d times in row %s" % (old_chip_html, r.count(old_chip_html), tid))
        self.s = self.s[: m.start()] + r.replace(old_chip_html, new_chip_html, 1) + self.s[m.end():]

    def add_row_before(self, anchor_tid, row_html):
        """Section 7 is newest-first: a new adjudicated row goes BEFORE the anchor row (e.g. the previous newest)."""
        anchor = '    <tr><td class="id">%s</td>' % anchor_tid
        if self.s.count(anchor) != 1:
            raise ValueError("anchor row %r occurs %d times" % (anchor_tid, self.s.count(anchor)))
        if not row_html.endswith("\n"):
            row_html += "\n"
        self.s = self.s.replace(anchor, row_html + anchor, 1)

    def stamp(self, new_version, note_html):
        """Bump '<p class="meta">vNNN ·' and insert the version note before the previous one."""
        cur = self.version()
        old = '<p class="meta">v%d ·' % cur
        if self.s.count(old) != 1:
            raise ValueError("version stamp not unique: %r x%d" % (old, self.s.count(old)))
        self.s = self.s.replace(old, '<p class="meta">%s ·' % new_version, 1)
        # the previous note's anchor; the v112 stamp was written "<br> <b>v112</b>" (a space), so optional whitespace
        # is tolerated (2026-09-18, v113 patch)
        ms = list(re.finditer(r"<br>\s*<b>v%d</b>" % cur, self.s))
        if len(ms) != 1:
            raise ValueError("previous version note not unique: v%d x%d" % (cur, len(ms)))
        at = ms[0].start()
        self.s = self.s[:at] + "<br>" + (note_html[4:] if note_html.startswith("<br>") else note_html) + self.s[at:]

    # -- audit and write -----------------------------------------------------------------------------------------
    def audit(self, expect_rows=None):
        used = {x.group(1) for x in re.finditer(r'class="chip ([a-z-]*)"', self.s)}
        css = set(re.findall(r"^\s*\.([a-z]+)\s*\{", self.s, re.M))
        undefined = sorted(u for u in used if u and u not in css and u not in CHIP_CLASSES)
        ids = re.findall(r'<tr><td class="id">([^<]+)</td>', self.s)
        dups = sorted({i for i in ids if ids.count(i) > 1} - {"J6"})   # J6 is a known, bracketed duplicate
        problems = []
        if undefined:
            problems.append("undefined chip classes: %s" % undefined)
        if dups:
            problems.append("duplicate row ids: %s" % dups)
        if "—" in self.s[self.s.find("<h2>7"):]:
            pass   # em-dash characters exist historically; new rows should use &mdash;
        if expect_rows is not None and len(ids) != expect_rows:
            problems.append("row count %d != expected %d" % (len(ids), expect_rows))
        if problems:
            raise AssertionError("; ".join(problems))
        print("ledger audit OK: v%s, %d rows, chips %s" % (self.version(), len(ids), sorted(used)))
        return len(ids)

    def write(self):
        io.open(self.path, "w", encoding="utf-8", newline="\n").write(self.s)
        if SCRATCH:
            io.open(SCRATCH, "w", encoding="utf-8", newline="\n").write(self.s)
        print("wrote", self.path, "(and scratch copy)" if SCRATCH else "")


def section7_row(tid, question, design, criteria, chips, observed, evidence):
    """Build a section-7 row. `chips` = list of (class, text); text and cells must already be entity-escaped."""
    assert all(c in CHIP_CLASSES for c, _ in chips), chips
    chip_html = " ".join('<span class="chip %s">%s</span>' % (c, t) for c, t in chips)
    return ('    <tr><td class="id">%s</td><td>%s</td><td>%s</td><td class="nums">%s</td><td>%s</td>'
            '<td class="nums">%s</td><td class="ev">%s</td></tr>\n' % (tid, question, design, criteria, chip_html, observed, evidence))


if __name__ == "__main__":
    L = Ledger()
    L.audit()
