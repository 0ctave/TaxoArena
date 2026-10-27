"""make_thesis_figures: thesis figures drawn from RECORDED outcomes only (zero calls; no statistic recomputed).

Registration: none (a presentation tool, not a test). It decides nothing; every plotted number is READ from the
record, never computed: from `docs/agents/results/<ID>.json` (`numbers_of_record` / `sentence_of_record`) or from
an outcome file of record whose sha256 (untracked outputs, pinned in the results JSON and the backup SHA256SUMS)
or git blob (tracked outputs) is asserted before any value is read. The only arithmetic is the unit change
proportion -> percentage points (x 100) for the axis.

Every value is located by a regex that must match EXACTLY ONCE in its source; zero or several matches, a missing
source, or a pin mismatch REFUSE (exit 2, nothing written). Verdict words are read the same way (a needle that must
occur in the named source), never typed in from memory.

Launch sequence (zero calls; opens no database):
    python tools/analysis/make_thesis_figures.py --selftest      parser and refusal checks (fixtures)
    python tools/analysis/make_thesis_figures.py --check         resolve and print every value; writes nothing
    python tools/analysis/make_thesis_figures.py                 write docs/figures/fig*.{pdf,png,caption.txt}
Options: --data-root <main checkout> (untracked outputs; default = the checkout owning the git common dir),
         --backup-root <dir> (default E:/), --out <dir> (default <repo>/docs/figures).
Temp files go under E:/TaxoArena_tmp (tools/analysis/scratch_dir.py, imported first).

Figures (record ids in each caption file):
  fig1_sq1_routing_gain        V2-DECLARED-CELLS C1, ARCH-V2-E-T-R2 G14, UNION-AF-ROUTE U1
  fig2_sq3_tree_vs_kmeans      DEEP-SPLIT-COMPARE C-AB, UNION-AF-ROUTE AK1/AK2, INTENT-TRANSFER-S1 T-C1/T-C1b,
                               ARCH-V2-E-T-R2 G13
  fig3_flatleaf_vs_descent     ARCH-V2-E-T-R2 G11, INTENT-TRANSFER-S1 T-C8
  fig4_sq5_nomic_minus_qwen3   EMBEDDER-CROSS-FLAT E1, E1-SPLIT-DRAWS SD1
  fig5_online_minus_batch      ONLINE-REPLAY-LOMO OL1 (stage 1), ONLINE-STAGE2 OS1 (stage 2)
Label status tags as in docs/drafts/2026-10-03_results_SQ3_SQ5.md: [LF] label-free, [AN] anchored (depth-2 =
declared classes), [DECL] declared labels, [LC] label-conditioned; "cross" = a cross-status comparison, never a
method ranking.

SELFTEST MUTANTS (2026-10-04; temporary edits, reverted; selftest run after each):
  M1 grab accepts the first of several matches (len(m) >= 1)            killed (S2)
  M2 grab returns None instead of refusing on zero matches              killed (S1)
  M3 sha256 pin check skipped                                           killed (S3)
  M4 git-blob check on CRLF bytes (no LF normalisation)                 killed (S4)
  M5 pp conversion dropped (values plotted as proportions)              killed (S5)
  M6 interval order lo/hi swapped in Row                                killed (S6)
  M7 verdict needle check skipped                                       killed (S7)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
try:
    import scratch_dir  # noqa: F401  (redirects tempfile to E:/TaxoArena_tmp; cleanup at exit)
except Exception as exc:  # pragma: no cover
    print(f"[make_thesis_figures] WARNING scratch_dir not importable: {exc}", file=sys.stderr)

N = r"([+-]?\d+(?:\.\d+)?)"


class Refusal(Exception):
    pass


# --------------------------------------------------------------------------- sources

def repo_root() -> Path:
    return Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=HERE, text=True).strip())


def main_checkout() -> Path:
    common = subprocess.check_output(["git", "rev-parse", "--git-common-dir"], cwd=HERE, text=True).strip()
    p = Path(common)
    if not p.is_absolute():
        p = (HERE / p).resolve()
    return p.parent


def git_blob_lf(data: bytes) -> str:
    data = data.replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


@dataclass
class OutcomeFile:
    key: str
    candidates: list  # list of (root_name, relative path)
    sha256: str | None = None  # full sha256 of the bytes (untracked outputs)
    blob: str | None = None  # git blob of the LF rendering (tracked outputs)
    record: str = ""  # where the pin is recorded


OUTCOMES = {
    "intent_s1": OutcomeFile(
        "intent_s1",
        [("data", "experiment_results/intent_transfer/s1_outcome.txt"),
         ("backup", "TaxoArena_backup_2026-10-03_intent_s1/outcome/s1_outcome.txt")],
        sha256="a25c6227e67e872ec7c39b30271d856cfa8b4e8e07f7763f221fd8281a807338",
        record="INTENT-TRANSFER-S1.json run.outcome_file (a25c6227...) + backup SHA256SUMS.txt"),
    "online_s1": OutcomeFile(
        "online_s1",
        [("data", "experiment_results/online_replay_lomo/outcome.txt"),
         ("backup", "TaxoArena_backup_2026-10-03_online_replay/outcome.txt")],
        sha256="63ae0f8f10a72434067e2ce294ff31754abe33a71feaa8d89baf7e18d1640e08",
        record="ONLINE-REPLAY-LOMO.json run.outcome_file (63ae0f8f...) + backup SHA256SUMS.txt"),
    "online_s2": OutcomeFile(
        "online_s2",
        [("data", "experiment_results/online_stage2/outcome.txt"),
         ("backup", "TaxoArena_backup_2026-10-03_online_stage2/outcome.txt")],
        sha256="19e8a87aac609f424b9762639a323cbbcc490bd3675675c6cd1cee30b23187ff",
        record="ONLINE-STAGE2.json run.outcome_file (19e8a87a...) + backup SHA256SUMS.txt"),
    "g11": OutcomeFile(
        "g11", [("repo", "experiment_results/archv2/rp12_r2/g11_outcome.txt")],
        blob="8559e9377ae0e818c599a20d5d84fbac88bd5e80", record="ARCH-V2-E-T-R2.json run.outcome_file (blob:8559e937)"),
    "g13": OutcomeFile(
        "g13", [("repo", "experiment_results/archv2/rp12_r2/g13_outcome.txt")],
        blob="ff8fa43973940450c3fa1ddded2e09e963c43d6f", record="ARCH-V2-E-T-R2.json run.outcome_file (blob:ff8fa439)"),
    "g14": OutcomeFile(
        "g14", [("repo", "experiment_results/archv2/rp12_r2/g14/v2_declared_cells_G14_outcome.txt")],
        blob="92e57c8ade516a54ced166aa99db0a00c53277c9", record="ARCH-V2-E-T-R2.json run.outcome_file (blob:92e57c8a)"),
}


class Record:
    """Read-only access to the results JSONs and pinned outcome files."""

    def __init__(self, repo: Path, data: Path, backup: Path, results_dir: Path | None = None,
                 outcomes: dict | None = None):
        self.roots = {"repo": repo, "data": data, "backup": backup}
        self.results_dir = results_dir or repo / "docs/agents/results"
        self.outcomes = outcomes if outcomes is not None else OUTCOMES
        self._json: dict = {}
        self._text: dict = {}
        self.used: dict = {}  # source key -> provenance line (for the captions)

    def json(self, test_id: str) -> dict:
        if test_id not in self._json:
            p = self.results_dir / f"{test_id}.json"
            if not p.exists():
                raise Refusal(f"results JSON missing: {p}")
            self._json[test_id] = json.loads(p.read_text(encoding="utf-8"))
        return self._json[test_id]

    def text(self, source: str) -> str:
        """source = 'json:<ID>:<numbers_of_record key>' | 'sentence:<ID>' | 'file:<outcome key>'."""
        if source in self._text:
            return self._text[source]
        kind, _, rest = source.partition(":")
        if kind == "json":
            tid, _, key = rest.partition(":")
            nor = self.json(tid).get("numbers_of_record") or {}
            if key not in nor:
                raise Refusal(f"{tid}.json numbers_of_record has no key {key!r}")
            txt = str(nor[key])
            self.used[source] = f"docs/agents/results/{tid}.json numbers_of_record[{key!r}]"
        elif kind == "sentence":
            txt = str(self.json(rest).get("sentence_of_record") or "")
            if not txt:
                raise Refusal(f"{rest}.json has no sentence_of_record")
            self.used[source] = f"docs/agents/results/{rest}.json sentence_of_record"
        elif kind == "file":
            of = self.outcomes[rest]
            txt, where = self._read_pinned(of)
            pin = f"sha256 {of.sha256}" if of.sha256 else f"blob:{of.blob} (LF)"
            self.used[source] = f"{where} ({pin}; pin of record: {of.record})"
        else:
            raise Refusal(f"unknown source kind {source!r}")
        self._text[source] = txt
        return txt

    def _read_pinned(self, of: OutcomeFile):
        tried = []
        for root_name, rel in of.candidates:
            p = self.roots[root_name] / rel
            if not p.exists():
                tried.append(f"{p} (absent)")
                continue
            data = p.read_bytes()
            if of.sha256 is not None:
                got = hashlib.sha256(data).hexdigest()
                if got != of.sha256:
                    tried.append(f"{p} (sha256 {got[:16]} != pin {of.sha256[:16]})")
                    continue
            if of.blob is not None:
                got = git_blob_lf(data)
                if got != of.blob:
                    tried.append(f"{p} (blob {got[:8]} != pin {of.blob[:8]})")
                    continue
            label = {"repo": "<repo>/", "data": "<main checkout>/", "backup": "E:/"}[root_name]
            return data.decode("utf-8"), label + rel
        raise Refusal(f"no pinned copy of outcome {of.key!r}: " + "; ".join(tried))


def grab(text: str, pattern: str, label: str, flags: int = re.M):
    """Exactly one match or refuse; returns the groups."""
    m = list(re.finditer(pattern, text, flags))
    if len(m) != 1:
        raise Refusal(f"{label}: pattern matched {len(m)} times (need exactly 1): {pattern!r}")
    return m[0].groups(), m[0].group(0)


def need(text: str, needle: str, label: str) -> str:
    if needle not in text:
        raise Refusal(f"{label}: verdict needle {needle!r} not found in its source")
    return needle


# --------------------------------------------------------------------------- rows

@dataclass
class Row:
    label: str
    est: float  # in percentage points
    lo: float
    hi: float
    status: str  # label-status tag for the legend
    verdict: str
    record_id: str
    provenance: list = field(default_factory=list)
    marker: str = "o"
    group: str = ""

    def __post_init__(self):
        if not (self.lo <= self.est <= self.hi):
            raise Refusal(f"{self.label}: interval [{self.lo}, {self.hi}] does not contain the point {self.est}")


def read_row(rec: Record, *, label, source, pattern, scale, status, record_id, verdict_source=None,
             verdict_needle=None, verdict_group=None, verdict_show=None, marker="o", group=""):
    txt = rec.text(source)
    groups, matched = grab(txt, pattern, f"{record_id} {label}")
    est, lo, hi = (float(groups[0]) * scale, float(groups[1]) * scale, float(groups[2]) * scale)
    prov = [f"{rec.used[source]}: \"{matched.strip()}\""]
    if verdict_group is not None:
        verdict = groups[verdict_group]
    else:
        vtxt = rec.text(verdict_source)
        need(vtxt, verdict_needle, f"{record_id} {label}")
        prov.append(f"verdict needle \"{verdict_needle}\" found in {rec.used[verdict_source]}")
        verdict = verdict_show or verdict_needle
    return Row(label, est, lo, hi, status, verdict, record_id, prov, marker, group)


PP = 100.0  # proportion -> percentage points
ONE = 1.0  # already in pp


def rows_fig1(rec):
    return [
        read_row(rec, label="[DECL] declared (source, domain) cells", source="json:V2-DECLARED-CELLS:C1_G",
                 pattern=rf"^{N}pp \(.*?\), two-stage 95% \[{N}, {N}\]", scale=ONE, status="[DECL]",
                 record_id="V2-DECLARED-CELLS C1", verdict_source="sentence:V2-DECLARED-CELLS",
                 verdict_needle="C1 HELD"),
        read_row(rec, label="[AN] anchored v2 tree cells (B0 flatLeaf)", source="json:ARCH-V2-E-T-R2:G_tree",
                 pattern=rf"^{N}pp two-stage \[{N}, {N}\]", scale=ONE, status="[AN]",
                 record_id="ARCH-V2-E-T-R2 G14", verdict_source="file:g14", verdict_needle="G14 -> HELD", verdict_show="G14 HELD"),
        read_row(rec, label="[LF] anchor-free federated tree AF-U", source="json:UNION-AF-ROUTE:U1",
                 pattern=rf"^G_AF {N}pp, two-stage 95% \[{N}, {N}\]", scale=ONE, status="[LF]",
                 record_id="UNION-AF-ROUTE U1", verdict_source="sentence:UNION-AF-ROUTE",
                 verdict_needle="U1 HELD"),
    ]


def rows_fig2(rec):
    A, B = "vs unsupervised k-means (matched cells)", "vs label-conditioned prototypes"
    r = [
        read_row(rec, label="Union: anchored vMF vs flat sph. k-means (C-AB)", source="json:DEEP-SPLIT-COMPARE:C_AB",
                 pattern=rf"^D_AB {N}, 95% \[{N}, {N}\]", scale=PP, status="[AN] vs [AN]",
                 record_id="DEEP-SPLIT-COMPARE C-AB", verdict_source="sentence:DEEP-SPLIT-COMPARE",
                 verdict_needle="C-AB HELD", group=A),
        read_row(rec, label="Union: AF-U vs global k-means (AK1)", source="json:UNION-AF-ROUTE:AK",
                 pattern=rf"^D_AU {N} \[{N}, {N}\]", scale=PP, status="[LF] vs [LF]",
                 record_id="UNION-AF-ROUTE AK1", verdict_source="sentence:UNION-AF-ROUTE",
                 verdict_needle="AK1 / AK2 UNDETERMINED", verdict_show="AK1 UNDETERMINED", group=A),
        read_row(rec, label="Union: AF-U vs per-source k-means (AK2)", source="json:UNION-AF-ROUTE:AK",
                 pattern=rf"; D_AUs {N} \[{N}, {N}\] \(spread 0\.0165\)", scale=PP, status="[LF] vs [LF]",
                 record_id="UNION-AF-ROUTE AK2", verdict_source="sentence:UNION-AF-ROUTE",
                 verdict_needle="AK1 / AK2 UNDETERMINED", verdict_show="AK2 UNDETERMINED; F-AK FIRES",
                 group=A),
    ]
    for corp, tag in (("massive", "MASSIVE"), ("clinc", "CLINC150")):
        r.append(read_row(rec, label=f"{tag}: AF tree vs k-means, NMI (T-C1)", source="file:intent_s1",
                          pattern=rf"^T-C1 {corp} \([MC]-AF\): D1 {N} = .*?; 95% CI \[{N}, {N}\];.*?-> (\w+)",
                          scale=PP, status="[LF] vs [LF]", record_id=f"INTENT-TRANSFER-S1 T-C1 {tag}",
                          verdict_group=3, marker="s", group=A))
    r.append(read_row(rec, label="Union: anchored tree vs class-cond. k-means (G13)", source="json:ARCH-V2-E-T-R2:D13",
                      pattern=rf"^{N} \[{N}, {N}\]; spread_KC", scale=PP, status="[AN] vs [LC] (cross)",
                      record_id="ARCH-V2-E-T-R2 G13", verdict_source="file:g13", verdict_needle="G13: FAILED", verdict_show="G13 FAILED",
                      group=B))
    for corp, tag in (("massive", "MASSIVE"), ("clinc", "CLINC150")):
        r.append(read_row(rec, label=f"{tag}: AF tree vs per-class prototypes (T-C1b)", source="file:intent_s1",
                          pattern=rf"^T-C1b {corp}: D13' {N} = .*?; 95% CI \[{N}, {N}\];.*?-> (\w+)",
                          scale=PP, status="[LF] vs [LC] (cross)", record_id=f"INTENT-TRANSFER-S1 T-C1b {tag}",
                          verdict_group=3, group=B))
    return r


def rows_fig3(rec):
    r = [read_row(rec, label="Union v2 tree (6,139 EVAL)", source="json:ARCH-V2-E-T-R2:D_fd",
                  pattern=rf"^{N} \[{N}, {N}\] \(paired", scale=PP, status="[AN]",
                  record_id="ARCH-V2-E-T-R2 G11", verdict_source="file:g11", verdict_needle="G11: HELD", verdict_show="G11 HELD")]
    for corp, tag in (("massive", "MASSIVE (4,946 EVAL)"), ("clinc", "CLINC150 (6,672 EVAL)")):
        r.append(read_row(rec, label=tag, source="file:intent_s1",
                          pattern=rf"^T-C8 {corp}: D_fd {N} = .*?; 95% CI \[{N}, {N}\]; n .*?-> (\w+)",
                          scale=PP, status="[LF]", record_id=f"INTENT-TRANSFER-S1 T-C8 {corp}", verdict_group=3))
    return r


def rows_fig4(rec):
    r = [read_row(rec, label="E1: af_clean_s42 split (descriptive 4th point)", source="json:EMBEDDER-CROSS-FLAT:E1_FILING",
                  pattern=rf"top-1 {N}, Wald 95% \[{N}, {N}\]", scale=PP, status="[LF]",
                  record_id="EMBEDDER-CROSS-FLAT E1", verdict_source="json:EMBEDDER-CROSS-FLAT:E1_FILING",
                  verdict_needle="N-raw minus af_clean_s42 flatLeaf top-1")]
    r[0].verdict = "DESCRIPTIVE"
    for k in (1, 2, 3):
        r.append(read_row(rec, label=f"Re-drawn split {k}", source="json:E1-SPLIT-DRAWS:G",
                          pattern=rf"G{k} {N} \[{N}, {N}\]", scale=PP, status="[LF]",
                          record_id=f"E1-SPLIT-DRAWS G{k}", verdict_source="sentence:E1-SPLIT-DRAWS",
                          verdict_needle="SD1 NEITHER"))
    (gbar,), m1 = grab(rec.text("json:E1-SPLIT-DRAWS:Gbar"), rf"^{N}$", "E1-SPLIT-DRAWS Gbar")
    (spn,), m2 = grab(rec.text("json:E1-SPLIT-DRAWS:spreads"), rf"spread_N {N} ", "E1-SPLIT-DRAWS spread_N")
    extra = {"Gbar": float(gbar) * PP, "spread_N": float(spn) * PP,
             "prov": [f"{rec.used['json:E1-SPLIT-DRAWS:Gbar']}: \"{m1}\"",
                      f"{rec.used['json:E1-SPLIT-DRAWS:spreads']}: \"{m2.strip()}\""]}
    return r, extra


MEMBERS = ["MMLU_PRO_LB", "BBH", "MATH", "MUSR", "IFEVAL", "GPQA"]


def rows_fig5(rec):
    r = []
    for m in MEMBERS:
        r.append(read_row(rec, label=m, source="file:online_s1",
                          pattern=(rf"^  -{m} \(AF-U tree\): .*?P_fl online [\d.]+ vs batch [\d.]+, "
                                   rf"D_m {N}  95% \[{N}, {N}\]"),
                          scale=PP, status="stage 1", record_id=f"ONLINE-REPLAY-LOMO -{m}",
                          verdict_source="sentence:ONLINE-REPLAY-LOMO", verdict_needle="OL1 DIFFERENT (LOSS)",
                          group=m))
        r[-1].verdict = "per-member, descriptive"
        r.append(read_row(rec, label=m, source="file:online_s2",
                          pattern=(rf"^  -{m} \(AF-U tree\): .*?P_fl online [\d.]+ vs batch [\d.]+, "
                                   rf"D_m {N}  95% \[{N}, {N}\]"),
                          scale=PP, status="stage 2", record_id=f"ONLINE-STAGE2 -{m}",
                          verdict_source="sentence:ONLINE-STAGE2", verdict_needle="OS1 DIFFERENT (LOSS)",
                          marker="s", group=m))
        r[-1].verdict = "per-member, descriptive"
    pooled = [
        read_row(rec, label="pooled (6 replays)", source="json:ONLINE-REPLAY-LOMO:OL1",
                 pattern=rf"^D {N}, 95% \[{N}, {N}\]", scale=PP, status="stage 1",
                 record_id="ONLINE-REPLAY-LOMO OL1", verdict_source="sentence:ONLINE-REPLAY-LOMO",
                 verdict_needle="OL1 DIFFERENT (LOSS)", group="pooled"),
        read_row(rec, label="pooled (6 replays)", source="json:ONLINE-STAGE2:OS1",
                 pattern=rf"^D {N}, 95% \[{N}, {N}\]", scale=PP, status="stage 2",
                 record_id="ONLINE-STAGE2 OS1", verdict_source="sentence:ONLINE-STAGE2",
                 verdict_needle="OS1 DIFFERENT (LOSS)", marker="s", group="pooled"),
    ]
    return r + pooled


# --------------------------------------------------------------------------- drawing

# Okabe-Ito (colour-blind safe)
OI = {"black": "#000000", "orange": "#E69F00", "sky": "#56B4E9", "green": "#009E73", "blue": "#0072B2",
      "vermillion": "#D55E00", "purple": "#CC79A7"}
STATUS_COLOUR = {
    "[DECL]": OI["purple"], "[AN]": OI["blue"], "[LF]": OI["orange"],
    "[AN] vs [AN]": OI["blue"], "[LF] vs [LF]": OI["orange"],
    "[AN] vs [LC] (cross)": OI["sky"], "[LF] vs [LC] (cross)": OI["vermillion"],
    "stage 1": OI["orange"], "stage 2": OI["blue"],
}


def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                         "pdf.fonttype": 42, "ps.fonttype": 42, "svg.hashsalt": "taxoarena",
                         "font.family": "DejaVu Sans"})
    return plt


def forest(ax, rows, xlabel, annotate=True):
    ys = list(range(len(rows)))[::-1]
    seen = set()
    for y, r in zip(ys, rows):
        c = STATUS_COLOUR[r.status]
        lab = r.status if r.status not in seen else None
        seen.add(r.status)
        ax.errorbar(r.est, y, xerr=[[r.est - r.lo], [r.hi - r.est]], fmt=r.marker, color=c, ecolor=c,
                    capsize=3, ms=5, lw=1.2, label=lab)
        if annotate:
            ax.annotate(f"{r.est:+.2f} [{r.lo:+.2f}, {r.hi:+.2f}]  {r.verdict}", xy=(1.0, y),
                        xycoords=("axes fraction", "data"), xytext=(6, 0), textcoords="offset points",
                        va="center", fontsize=7.5)
    ax.axvline(0, color="0.5", lw=0.8, ls="--")
    ax.set_yticks(ys)
    ax.set_yticklabels([r.label for r in rows])
    ax.set_xlabel(xlabel)
    ax.set_ylim(-0.7, len(rows) - 0.3)


def save(fig, out: Path, name: str, caption: str, written: list):
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{name}.pdf", bbox_inches="tight", metadata={"CreationDate": None, "ModDate": None})
    fig.savefig(out / f"{name}.png", bbox_inches="tight", dpi=200, metadata={"Software": None})
    (out / f"{name}.caption.txt").write_text(caption, encoding="utf-8", newline="\n")
    written += [f"{name}.pdf", f"{name}.png", f"{name}.caption.txt"]


def caption_text(title, body, rows, rec, ids, extra_prov=()):
    lines = [title, "", body, "", "Record IDs: " + ", ".join(ids), "",
             "Plotted values (pp; whiskers = the recorded 95% interval; read from the record, nothing recomputed):"]
    for r in rows:
        lines.append(f"- {r.record_id} | {r.label} | {r.status} | {r.est:+.2f} [{r.lo:+.2f}, {r.hi:+.2f}] | {r.verdict}")
        for p in r.provenance:
            lines.append(f"    source: {p}")
    for p in extra_prov:
        lines.append(f"- source: {p}")
    lines += ["", "Sentences of record (verbatim, last bracket wins):"]
    for tid in dict.fromkeys(i.split()[0] for i in ids):
        lines.append(f"- {tid}: {rec.json(tid).get('sentence_of_record', '')}")
    lines += ["", "Made by tools/analysis/make_thesis_figures.py (zero calls)."]
    return "\n".join(lines) + "\n"


def build(rec: Record, out: Path, write: bool = True):
    written: list = []
    r1, r2, r3 = rows_fig1(rec), rows_fig2(rec), rows_fig3(rec)
    r4, e4 = rows_fig4(rec)
    r5 = rows_fig5(rec)
    if not write:
        for rows in (r1, r2, r3, r4, r5):
            for r in rows:
                print(f"{r.record_id:38s} {r.status:22s} {r.est:+8.3f} [{r.lo:+8.3f}, {r.hi:+8.3f}] {r.verdict}")
        print(f"E1-SPLIT-DRAWS Gbar {e4['Gbar']:+.2f}pp spread_N {e4['spread_N']:.2f}pp")
        return written
    plt = _plt()

    # Figure 1
    fig, ax = plt.subplots(figsize=(6.6, 1.9))
    forest(ax, r1, "Routing gain over the best single model (pp)")
    ax.legend(title="label status", loc="lower left", fontsize=7.5, title_fontsize=7.5, frameon=False,
              bbox_to_anchor=(0, 1.0), ncol=3)
    save(fig, out, "fig1_sq1_routing_gain", caption_text(
        "Figure 1 (SQ1). Per-cell routing gain over the best single model (Qwen2.5-72B-Instruct) on the content-closed v2 union EVAL.",
        "Each policy is fitted on TRAIN; n 5,907 items in 5,404 components; whiskers are the recorded two-stage 95% intervals. "
        "[DECL] declared (source, domain) cells; [AN] the anchored v2 tree's cells (depth-2 = declared classes); [LF] the anchor-free "
        "federated tree AF-U. A cross-status comparison is not a method ranking.",
        r1, rec, ["V2-DECLARED-CELLS C1", "ARCH-V2-E-T-R2 G14", "UNION-AF-ROUTE U1"]), written)
    plt.close(fig)

    # Figure 2
    groups = list(dict.fromkeys(r.group for r in r2))
    fig, axes = plt.subplots(2, 1, figsize=(6.6, 4.4), sharex=True,
                             gridspec_kw={"height_ratios": [sum(r.group == g for r in r2) for g in groups]})
    handles = {}
    for ax, g in zip(axes, groups):
        sub = [r for r in r2 if r.group == g]
        forest(ax, sub, "")
        ax.set_title(f"tree {g}", fontsize=8.5, loc="left")
        for h, l in zip(*ax.get_legend_handles_labels()):
            handles.setdefault(l, h)
    axes[-1].set_xlabel("Tree minus comparator (pp); circle = filing precision, square = NMI")
    fig.legend(handles.values(), handles.keys(), title="label status", loc="lower center", ncol=2, fontsize=7.5,
               title_fontsize=7.5, frameon=False, bbox_to_anchor=(0.35, -0.12))
    save(fig, out, "fig2_sq3_tree_vs_kmeans", caption_text(
        "Figure 2 (SQ3). Tree minus k-means and tree minus label-conditioned prototypes, on the benchmark union and two intent corpora.",
        "Union rows: content-closed v2 union EVAL, 6,139 items in 5,628 components, filing precision. Intent rows (MASSIVE 4,946 / 4,923; "
        "CLINC150 6,672 / 6,672): T-C1 is the fine NMI against k-means at k = the tree's leaves (84 / 139), decided by a 90% TOST "
        "(the whisker is the recorded 95% CI); T-C1b is filing precision against per-class prototypes. Upper panel: like with like "
        "([AN] vs [AN], [LF] vs [LF]). Lower panel: cross-status ([LC] comparators read labels), never a method ranking. "
        "EQUIVALENT means inside the stated margin by TOST, never 'the same'.",
        r2, rec, ["DEEP-SPLIT-COMPARE C-AB", "UNION-AF-ROUTE AK1", "UNION-AF-ROUTE AK2", "INTENT-TRANSFER-S1 T-C1",
                  "ARCH-V2-E-T-R2 G13", "INTENT-TRANSFER-S1 T-C1b"]), written)
    plt.close(fig)

    # Figure 3
    fig, ax = plt.subplots(figsize=(6.6, 1.9))
    forest(ax, r3, "flatLeaf minus descent filing precision (pp)")
    ax.legend(title="label status", loc="lower left", fontsize=7.5, title_fontsize=7.5, frameon=False,
              bbox_to_anchor=(0, 1.0), ncol=2)
    save(fig, out, "fig3_flatleaf_vs_descent", caption_text(
        "Figure 3. Filing gap: flatLeaf (nearest leaf) minus top-down descent, same tree, paired on the same EVAL items.",
        "Union: the content-closed v2 anchored tree, 6,139 EVAL items in 5,628 components. Intent: the label-free anchor-free tree on "
        "MASSIVE and CLINC150 (UNROUTED counted wrong). Whiskers are the recorded 95% intervals.",
        r3, rec, ["ARCH-V2-E-T-R2 G11", "INTENT-TRANSFER-S1 T-C8"]), written)
    plt.close(fig)

    # Figure 4
    fig, ax = plt.subplots(figsize=(6.6, 2.1))
    forest(ax, r4, "nomic_raw minus qwen3 anchor-free tree filing, top-1 (pp)")
    ax.axvline(e4["Gbar"], color=OI["black"], lw=0.8, ls=":",
               label=f"Gbar of the 3 re-draws {e4['Gbar']:+.2f} (spread_N {e4['spread_N']:.2f})")
    ax.legend(title="label status", loc="lower left", fontsize=7.5, title_fontsize=7.5, frameon=False,
              bbox_to_anchor=(0, 1.0), ncol=2)
    save(fig, out, "fig4_sq5_nomic_minus_qwen3", caption_text(
        "Figure 4 (SQ5). Per-split filing gap of the nomic_raw anchor-free tree minus the qwen3 tree on MMLU-Pro.",
        "E1 is the af_clean_s42 split (n 3,445; a descriptive 4th point, never pooled into SD1). Splits 1-3 are three re-drawn "
        "CK-CLOSE splits, each on its own held-out set (3,598 / 3,522 / 3,500); whiskers are the recorded paired Wald 95% intervals. "
        "The dotted line is the recorded Gbar of the three re-draws; SD1 reads NEITHER because |Gbar| lies inside spread_N.",
        r4, rec, ["EMBEDDER-CROSS-FLAT E1", "E1-SPLIT-DRAWS SD1"], e4["prov"]), written)
    plt.close(fig)

    # Figure 5
    fig, ax = plt.subplots(figsize=(6.6, 3.2))
    order = MEMBERS + ["pooled"]
    base = {g: (len(order) - 1 - i) for i, g in enumerate(order)}
    seen = set()
    for r in r5:
        y = base[r.group] + (0.17 if r.status == "stage 1" else -0.17)
        c = STATUS_COLOUR[r.status]
        lab = None
        if r.status not in seen:
            lab = {"stage 1": "stage 1: online mean refit (ONLINE-REPLAY-LOMO)",
                   "stage 2": "stage 2: frozen means + OOS buffer (ONLINE-STAGE2)"}[r.status]
            seen.add(r.status)
        ax.errorbar(r.est, y, xerr=[[r.est - r.lo], [r.hi - r.est]], fmt=r.marker, color=c, ecolor=c,
                    capsize=2.5, ms=4.5, lw=1.1, label=lab, mfc=c if r.marker == "s" else "white")
    ax.axvline(0, color="0.5", lw=0.8, ls="--")
    ax.axhline(0.5, color="0.8", lw=0.6)
    ax.set_yticks([base[g] for g in order])
    ax.set_yticklabels([f"held-out {g}" if g != "pooled" else "pooled (6,139 / 5,628)" for g in order])
    ax.set_xlabel("Online minus batch AF-U filing precision of the held-out member (pp)")
    ax.legend(title="[LF] AF-U tree", loc="lower left", fontsize=7.5, title_fontsize=7.5, frameon=False,
              bbox_to_anchor=(0, 1.0), ncol=1)
    save(fig, out, "fig5_online_minus_batch", caption_text(
        "Figure 5. Online replay of a left-out union member minus a batch rebuild, stage 1 vs stage 2 (label-free AF-U tree).",
        "Leave-one-member-out over the six union members (content-closed v2 union EVAL; one draw). Per-member rows are descriptive; "
        "the pooled rows decide OL1 and OS1. The online arm is transductive on the held-out EVAL (favours it). The stage 1 -> stage 2 "
        "change is descriptive only; nothing is credited to freezing. Whiskers are the recorded 95% intervals (MUSR stage 1 and IFEVAL "
        "stage 2 are degenerate, SE 0).",
        r5, rec, ["ONLINE-REPLAY-LOMO OL1", "ONLINE-STAGE2 OS1"]), written)
    plt.close(fig)
    return written


# --------------------------------------------------------------------------- selftest

def selftest() -> int:
    import tempfile
    fails = []

    def check(name, cond):
        print(f"  {name}: {'PASS' if cond else 'FAIL'}")
        if not cond:
            fails.append(name)

    def refuses(fn):
        try:
            fn()
        except Refusal:
            return True
        return False

    # S1 zero matches refuse; S2 two matches refuse
    check("S1 grab refuses on zero matches", refuses(lambda: grab("abc", rf"x {N}", "t")))
    check("S2 grab refuses on two matches", refuses(lambda: grab("x 1.0\nx 2.0", rf"^x {N}", "t")))
    g, _ = grab("x 1.25\ny 2.0", rf"^x {N}", "t")
    check("S2b grab returns the unique value", g == ("1.25",))
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / "res").mkdir()
        (td / "res/T.json").write_text(json.dumps({
            "numbers_of_record": {"G": "D -0.0326, 95% [-0.0446, -0.0205] (6,139)"},
            "sentence_of_record": "OS1 DIFFERENT (LOSS), D -0.0326"}), encoding="utf-8")
        body = b"line\r\nT-C8 massive: D_fd +0.07258 = P 0.78 - P 0.70; 95% CI [+0.06313, +0.08198]; n 4946 -> HELD\r\n"
        (td / "o.txt").write_bytes(body)
        good = OutcomeFile("o", [("data", "o.txt")], sha256=hashlib.sha256(body).hexdigest())
        bad = OutcomeFile("b", [("data", "o.txt")], sha256="0" * 64)
        lf_blob = git_blob_lf(body)
        crlf_blob = hashlib.sha1(b"blob %d\0" % len(body) + body).hexdigest()
        blob_ok = OutcomeFile("c", [("data", "o.txt")], blob=lf_blob)
        rec = Record(td, td, td, results_dir=td / "res", outcomes={"o": good, "b": bad, "c": blob_ok})
        check("S3 sha256 pin mismatch refuses", refuses(lambda: rec.text("file:b")))
        check("S4 git blob is the LF rendering", lf_blob != crlf_blob and "T-C8" in rec.text("file:c"))
        row = read_row(rec, label="x", source="json:T:G", pattern=rf"^D {N}, 95% \[{N}, {N}\]", scale=PP,
                       status="stage 2", record_id="T", verdict_source="sentence:T",
                       verdict_needle="OS1 DIFFERENT (LOSS)")
        check("S5 proportion -> pp (x100)", abs(row.est - (-3.26)) < 1e-9)
        check("S6 interval order lo <= est <= hi", abs(row.lo - (-4.46)) < 1e-9 and abs(row.hi - (-2.05)) < 1e-9)
        check("S6b inverted interval refuses",
              refuses(lambda: Row("x", 0.0, 1.0, -1.0, "[LF]", "v", "T")))
        check("S7 missing verdict needle refuses", refuses(lambda: read_row(
            rec, label="x", source="json:T:G", pattern=rf"^D {N}, 95% \[{N}, {N}\]", scale=PP, status="stage 2",
            record_id="T", verdict_source="sentence:T", verdict_needle="OS1 HELD")))
        r8 = read_row(rec, label="m", source="file:o",
                      pattern=rf"^T-C8 massive: D_fd {N} = .*?; 95% CI \[{N}, {N}\]; n .*?-> (\w+)", scale=PP,
                      status="[LF]", record_id="T", verdict_group=3)
        check("S8 outcome-file row value and verdict", abs(r8.est - 7.258) < 1e-9 and r8.verdict == "HELD")
    print(f"SELFTEST {'PASS' if not fails else 'FAIL'} ({len(fails)} failed)")
    return 0 if not fails else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check", action="store_true", help="resolve and print every value; write nothing")
    ap.add_argument("--data-root", type=Path, default=None)
    ap.add_argument("--backup-root", type=Path, default=Path("E:/"))
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    repo = repo_root()
    rec = Record(repo, a.data_root or main_checkout(), a.backup_root)
    out = a.out or repo / "docs/figures"
    print("make_thesis_figures: zero calls; reads the record only; nothing recomputed")
    try:
        written = build(rec, out, write=not a.check)
    except Refusal as exc:
        print(f"REFUSED: {exc}")
        return 2
    for s, p in rec.used.items():
        print(f"  read {s}: {p}")
    for w in written:
        print(f"  wrote {out / w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
