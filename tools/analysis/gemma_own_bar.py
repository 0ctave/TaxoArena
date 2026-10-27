"""gemma_own_bar.py: GEMMA-OWN-BAR's bar calibration readout, G-AF build config and GO1 readout. ZERO LLM / judge calls; no
construction (the operator launches the null legs and the one build from the printed plans); no arena pool read.

REGISTRATION OF RECORD: docs/judge_v2_program.md L23915-L23927 (_as_of d50c47d4), section "## Registered 2026-10-03 (before any
code or call) — GEMMA-OWN-BAR: with a separation bar calibrated for gemma 768 by the record's own bar rule on TRAIN-only nulls, does a
gemma anchor-free MASSIVE tree build beyond M-AF-g's 4 leaves and partition as well as gemma k-means at matched k (S1's T-C1 rule)?"
(results record docs/agents/results/GEMMA-OWN-BAR.json). What this file implements from it:
  HOW THE BAR IS DERIVED: bar_g = 0.025 x p95_null(gemma 768, MASSIVE TRAIN root) / p95_null(qwen3 256, MASSIVE TRAIN root), each
    p95 from the site null's moment-matched generator through the production splitSingleNode, 300 reps, on S1's MASSIVE TRAIN items
    only; computed, printed and hashed BEFORE the build. Printed beside (descriptive): the width-only isotropic bar at 768.
    The null legs are the Kotlin arm `gemmaOwnBar - ...` of SeparationNullBySizeTest (task `gradlew gemmaOwnBar`; its file half
    src/test/kotlin/taxonomy/GemmaOwnBarNull.kt); --calibrate reads their outputs and writes the bar file (write-once).
  INSTRUMENT "Build G-AF: S1's M-AF-g TOML with proposalSeparationBar = bar_g (all else unchanged)": --write-config.
  READOUTS AND CRITERIA: GO1 (DECIDING; S1's T-C1 rule verbatim, imported from tools/analysis/intent_transfer_s1.py blob 4e9d9d05:
    phase_gate (delta_c on GATE, k-means at k = L TRAIN-fit, seeds 0-19), t_c1, tost_verdict); "degenerate tree" below 10 leaves;
    F-GO; DESCRIPTIVE: G-AF's leaf count against M-AF-g's 4 and M-AF's 84, bar_g and the width-only bar, T-C7 / T-C9 rows; P1-P3.

BUILDER'S READINGS (points the registered text leaves open; each printed in the outputs; the registrar confirms or brackets):
  GOB-K1 THE NULLS' BAR. The splitter's marginalEps / coarsening loop reads the bar, so the null needs one. Both TRAIN-root nulls run
     at the recipe's 0.025 (the harness default; the bar the rule scales; the D1 width rule's isoNullByDim also ran every width at
     0.025). Running gemma's null at bar_g would be circular.
  GOB-K2 POPULATION. "S1's MASSIVE TRAIN items" = the DISTINCT TRAIN texts of S1's salt-1 MASSIVE build DB (9,826 = the construction's
     root population, B2), the SAME text set for both legs (asserted: equal TRAIN text-set sha256 on both legs, equal to the
     re-derivation from the pinned ingest DB, and the build DB's table sha equal to the derivation's). GATE rows are never read.
  GOB-K3 SEEDS. siteNull's plain-null formula cpcSeed(20260908, "MASSIVE_TRAIN_ROOT", rep), the same stream on both legs (common
     random numbers for the ratio); node depth 1 and kappa 10 as every site-null replicate (runReplicate).
  GOB-B1 BAR PRECISION. The TOML carries bar_g rounded to 6 decimals ("%.6f"); P1 is scored on the unrounded bar_g.
  GOB-B2 BUILD DB. The TOML keeps corpusDbPath "intent_s1_build/m_af_g.db" byte-identical; the operator writes it FRESH in this run's
     DATA_ROOT (intent_s1_export.py --export M-AF-g; its table sha must equal S1's 6ce9bdf8...), never S1's used file (the JVM
     writes reserved_pool rows into its build DB).
  GOB-R1 SEEDS 0-4. The registration's INSTRUMENT says "k-means at k = L in gemma 768; seeds 0-4"; GO1 is "S1's T-C1 rule
     verbatim": D1 against the mean over seeds 0-19, spread_K over seeds 0-4 (both as T-C1). Read as T-C1 verbatim.
  GOB-R2 L = 10. Support (f) "SCOREABLE ... PROVIDED G-AF builds at least 10 leaves; with fewer leaves ... 'degenerate tree'" and
     the falsifier "<= 10 leaves": degenerate iff L < 10; F-GO's leaf clause iff L <= 10 (the results JSON's paraphrase "'degenerate
     tree' if <= 10 leaves" differs at L = 10 only; the programme text is applied; flagged to the registrar).

HYGIENE: reads only pinned inputs (ingest DB and intent_emb_gemma.db / intent_emb_qwen3.db through S1's pin_check, strict; the null
legs' status files name the working copies' sha256, checked = the pins), the G-AF run dir and DATA_ROOT/snapshots.db read-only
(a non-empty -wal refuses). Every fit goes through S1's fit_idx (TRAIN or GATE; EVAL / OOS / dropped REFUSES; FIT_LOG printed). EVAL is
read only after the GATE constants are frozen (S1's phase guard). REFUSES while a java.exe runs (--run, --dry-run). Threads
OMP/OPENBLAS/MKL = 1 (set by the S1 import).

OUTPUTS (DATA_ROOT = TAXOARENA_DATA_ROOT or this checkout; NEVER committed: pinned by sha256 and backed up by the operator):
  experiment_results/gemma_own_bar/cal/{iso,null_qwen3_256,null_gemma768}/   the Kotlin legs (status.txt, replicates)
  experiment_results/gemma_own_bar/bar_g.json                                --calibrate, WRITE-ONCE (mode x)
  experiment_configs/gemma_own_bar/g_af.toml                                 --write-config, WRITE-ONCE (identical bytes left alone)
  experiment_results/gemma_own_bar/g_af/seed_42/                             the build (bootRun)
  experiment_results/gemma_own_bar/gob_outcome.txt                           --run, WRITE-ONCE (mode x; lexists refuses first)
No judge call is made, so there is no cache, pilot or truncation guard (the --pilot / --analyze pattern does not apply); --run is
all-or-nothing.

LAUNCH SEQUENCE (operator; rule 7 W1-W5 for each JVM leg and the build; one heavy process at a time; backup first):
  python tools/analysis/gemma_own_bar.py --selftest ; --mutants
  python tools/analysis/gemma_own_bar.py --calibrate-plan            # prints the three gradlew gemmaOwnBar legs; launches nothing
  (the three legs)                                                    # iso, qwen3_256, gemma768
  python tools/analysis/gemma_own_bar.py --calibrate --dry-run       # validates and prints bar_g; writes nothing
  python tools/analysis/gemma_own_bar.py --calibrate                 # writes bar_g.json (write-once); record its sha256
  python tools/analysis/gemma_own_bar.py --write-config [--dry-run]  # g_af.toml from m_af_g.toml + the bar file
  python tools/analysis/gemma_own_bar.py --check-config
  python tools/analysis/gemma_own_bar.py --launch-plan               # prints the export + bootRun route; launches nothing
  (the build)
  python tools/analysis/gemma_own_bar.py --run --dry-run             # presence, pins, census, config, L, GATE; no EVAL statistic
  python tools/analysis/gemma_own_bar.py --run [--s1-data-root DIR]  # the outcome of record (write-once)

SELFTEST: the cases are SELFTEST_DOC below (printed by --selftest; 68 value checks, fixtures only).
SELFTEST MUTANTS (2026-10-03, --mutants: in-process source edits, one at a time; 38 of 38 KILLED): p95 rank floor-1 | p95 = max |
bar ratio inverted | deciding bar from the iso leg | legs swapped | reps not checked | sepBar not checked | emb pin not checked |
TRAIN set not checked | table sha not checked | printed p95 not checked | iso slice count not checked | non-positive p95 admitted
(crash-killed: ZeroDivisionError, fails closed) | bar file lexists check off (crash-killed by mode x) | calibrate dry run writes |
TOML bar 4 dp | identity uses 3 dp | config keeps the old outputDir | config keeps the old bar | two-change check off | source TOML
blob not checked | config overwrite allowed (crash-killed by mode x) | check_config ignores bytes | degenerate at <= 10 | F-GO leaf
clause < 10 | F-GO ignores LOSS | F-GO only on plain LOSS | bands exclusive | Brier on the wrong event | P1 on the TOML bar | T-C1 on
a tree-only NMI | GATE constants after EVAL | outcome lexists check off (crash-killed) | build config not checked | slice not
checked | dry run computes GO1 | L from the wrong source | need_km off. Withdrawn as EQUIVALENT: "bar file / outcome opened 'w'"
(each is behind an lexists refusal that fires first; the lexists-off mutants are the live ones).
The Kotlin half's mutants (GemmaOwnBarArmTest) are tabled in the commit message.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "ingest"))
import intent_transfer_s1 as IS1        # noqa: E402  (sets OMP/OPENBLAS/MKL = 1 at import)

import argparse                          # noqa: E402
import contextlib                        # noqa: E402
import hashlib                           # noqa: E402
import io                                # noqa: E402
import json                              # noqa: E402
import math                              # noqa: E402
import re                                # noqa: E402
import shutil                            # noqa: E402
import tempfile; import scratch_dir                          # noqa: E402
import tomllib                           # noqa: E402

import numpy as np                       # noqa: E402

S0, EX, SS = IS1.S0, IS1.EX, IS1.SS

TAG = "[GOB]"
DATA_ROOT = os.environ.get("TAXOARENA_DATA_ROOT", ROOT)
REGISTRATION = ("docs/judge_v2_program.md L23915-L23927 (_as_of d50c47d4), \"## Registered 2026-10-03 (before any code or call) — "
                "GEMMA-OWN-BAR: ...\"")
PINNED_CODE = {"intent_transfer_s1.py": "4e9d9d05fbdf14d0a85966b4c897cfbfd779186d",
               "intent_s1_export.py": "75310a98afe87788ca01f45c56a19b9ceb045698"}
SRC_CONFIG_REL = "experiment_configs/intent_s1/m_af_g.toml"
SRC_CONFIG_BLOB = "53a569481afea41527ea7ed49d18a54cf01557c9"
CONFIG_REL = "experiment_configs/gemma_own_bar/g_af.toml"
OUT_REL = "experiment_results/gemma_own_bar"
G_AF_OUT = OUT_REL + "/g_af"
CAL_DIRS = {"iso": "cal/iso", "qwen3_256": "cal/null_qwen3_256", "gemma768": "cal/null_gemma768"}
BAR_FILE = "bar_g.json"
OUTCOME = "gob_outcome.txt"
S1_TABLE_SHA = "6ce9bdf8494be7d966f7dae8eeaa00b659186e14e9d98e837c52fd27e5bd570d"   # S1's MASSIVE salt-1 build table (export manifest)
REG_REPS = 300
BAR_OF_RECORD = 0.025
MCS = 55
LEG = {"qwen3_256": {"emb": "qwen3", "model": "qwen3-embedding:latest", "slice": 256},
       "gemma768": {"emb": "gemma", "model": "embeddinggemma:latest", "slice": 768}}
ISO = {"n": 406, "sigma": 0.5, "dims": (256, 512, 768)}
RECORD_ISO = {256: 0.0069, 512: 0.0040}          # docs/v2_validation_plan.md L246 (D1): p95 at n = 406; 512 -> bar 0.0145
RECORD_BAR_512 = 0.0145
SLICE_G = 768
LEAVES_REF = {"M-AF-g": 4, "M-AF": 84}            # S1 (POSTRUN_intent_s1 Q-1; P1 leaves)
S1_SLUG = {"M-AF-g": "m_af_g", "M-AF": "m_af"}
DEGENERATE_BELOW = 10                             # Support (f): SCOREABLE provided >= 10 leaves (GOB-R2)
FGO_LEAVES_AT_MOST = 10                           # FALSIFIER: <= 10 leaves (GOB-R2)
BANDS = {"P1": (0.007, 0.020), "P2": (15, 90), "P3": (-0.025, 0.015)}
PROB = {"EQUIVALENT": 0.50, "LOSS": 0.15}
REG_SUPPORT = {"n": 4946, "G": 4923, "deff": 1.0093, "se_total": 0.0025, "delta_c_plan": 0.017, "reach": 0.013}
SENT_FGO_FIRED = ("the anchor-free recipe does not transfer to gemma 768 even with an embedder-calibrated bar; M-AF-g's reading "
                  "narrows from \"qwen3-tuned bar\" to \"the recipe, not only the bar\"")
SENT_FGO_NOT = "M-AF-g's 4 leaves are attributed to the bar"
DOES_NOT_SHOW = ("which embedder is better (D3 the author's); CLINC or other corpora; card prompts; a certified gemma tree; anything "
                 "about MMLU-Pro")


def refuse(msg):
    print("%s REFUSING: %s" % (TAG, msg))
    raise SystemExit("%s REFUSED: %s" % (TAG, msg))


def blob(path):
    d = open(path, "rb").read().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(d) + d).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def check_code_pins(here=HERE):
    for name, want in PINNED_CODE.items():
        got = blob(os.path.join(here, name))
        if got != want:
            refuse("%s blob %s != the pinned %s (the instrument is imported unchanged)" % (name, got, want))
    IS1.check_code_pins()


def p95(xs):
    """The harness's quantile rule (SeparationNullBySizeTest.percentile): the ceil(0.95 n)-th order statistic."""
    s = sorted(float(x) for x in xs)
    if not s:
        return float("nan")
    rank = min(max(int(math.ceil(0.95 * len(s))), 1), len(s))
    return s[rank - 1]


def text_set_sha(texts):
    """GemmaOwnBarNull.textSetSha: sha256 of the texts sorted by UTF-8 bytes, joined by '\\n'."""
    return hashlib.sha256(b"\n".join(sorted(t.encode("utf-8") for t in texts))).hexdigest()


# ================================================================================================ calibration
def read_status(d):
    p = os.path.join(d, "status.txt")
    if not os.path.isfile(p):
        refuse("%s ABSENT (the leg has not run)" % p)
    lines = open(p, encoding="utf-8").read().replace("\r\n", "\n").split("\n")
    if lines[0] != "COMPLETE":
        refuse("%s reads %r, not COMPLETE" % (p, lines[0]))
    return {l.split("=", 1)[0]: l.split("=", 1)[1] for l in lines[1:] if "=" in l}


def read_reps(path, col=-1, key=None):
    if not os.path.isfile(path):
        refuse("%s ABSENT" % path)
    rows = [l.split(",") for l in open(path, encoding="utf-8").read().replace("\r\n", "\n").split("\n")[1:] if l.strip()]
    out = {}
    for r in rows:
        k = r[0] if key is not None else "all"
        out.setdefault(k, []).append(float(r[col]))
    return out


def derived_train(db=None, pins_file=None):
    """MASSIVE salt-1 TRAIN, re-derived from the pinned ingest DB (S1's exporter): (table sha, TRAIN text-set sha, n TRAIN texts)."""
    items, _sha, _db = EX.inputs(db, pins_file)
    d = EX.derive(items)[("massive", 1)]
    tr = [r["text"] for r in d["rows"] if r["side"] == SS.TRAIN]
    return {"table_sha": d["table_sha"], "text_sha": text_set_sha(tr), "n": len(tr)}


def emb_pins(pins_file=None):
    return {e: EX.pin_of("emb", e, pins_file) for e in ("qwen3", "gemma")}


def calibrate(data_root=None, write=False, derived=None, pins=None, out=print):
    """Validates the three legs, computes bar_g (deciding) and the width-only bar (descriptive), writes the bar file (write-once)."""
    root = os.path.join(data_root or DATA_ROOT, OUT_REL)
    bar_path = os.path.join(root, BAR_FILE)
    if write and os.path.lexists(bar_path):
        refuse("%s exists: the bar file is write-once" % bar_path)
    out("%s CALIBRATE (%s): zero calls; %s" % (TAG, "writes the bar file" if write else "DRY RUN, writes nothing", REGISTRATION))
    derived = derived or derived_train()
    pins = pins or emb_pins()
    legs, files = {}, {}
    for leg, spec in LEG.items():
        d = os.path.join(root, CAL_DIRS[leg])
        st = read_status(d)
        want = {"leg": "null", "arm": leg, "embedder": spec["emb"], "model": spec["model"], "sliceDim": str(spec["slice"]),
                "sepBar": repr(BAR_OF_RECORD), "minClusterSize": str(MCS), "reps": str(REG_REPS)}
        bad = {k: (st.get(k), v) for k, v in want.items() if st.get(k) != v}
        if bad:
            refuse("leg %s: status fields off the registration (got, want): %s" % (leg, bad))
        if st.get("emb_sha256") != pins[spec["emb"]] or not pins[spec["emb"]]:
            refuse("leg %s: the working copy's sha256 %s != the pin %s" % (leg, st.get("emb_sha256"), pins[spec["emb"]]))
        if st.get("build_table_sha256") != derived["table_sha"]:
            refuse("leg %s: the build DB's table sha %s != the re-derived MASSIVE salt-1 table %s" % (leg, st.get("build_table_sha256"), derived["table_sha"]))
        if st.get("train_text_set_sha256") != derived["text_sha"] or st.get("n_train") != str(derived["n"]):
            refuse("leg %s: the TRAIN population read (%s texts, set sha %s) != the re-derived MASSIVE salt-1 TRAIN (%d, %s): TRAIN-ONLY"
                   % (leg, st.get("n_train"), st.get("train_text_set_sha256"), derived["n"], derived["text_sha"]))
        reps = read_reps(os.path.join(d, "replicates.csv"))["all"]
        if len(reps) != REG_REPS:
            refuse("leg %s: %d replicates, not the registered %d" % (leg, len(reps), REG_REPS))
        q = p95(reps)
        if q != float(st.get("p95", "nan")):
            refuse("leg %s: p95 recomputed %r != the leg's printed %r" % (leg, q, st.get("p95")))
        legs[leg] = {"p95": q, "n": int(st["n_train"]), "reached": sum(1 for x in reps if x > 0), "max": max(reps), "status": st}
        for f in ("status.txt", "replicates.csv"):
            files["%s/%s" % (CAL_DIRS[leg], f)] = sha256_file(os.path.join(d, f))
    if legs["qwen3_256"]["status"]["train_text_set_sha256"] != legs["gemma768"]["status"]["train_text_set_sha256"]:
        refuse("the two legs read different TRAIN populations")
    di = os.path.join(root, CAL_DIRS["iso"])
    sti = read_status(di)
    if sti.get("leg") != "iso" or sti.get("reps") != str(REG_REPS) or sti.get("n") != str(ISO["n"]) or sti.get("sepBar") != repr(BAR_OF_RECORD):
        refuse("iso leg status off the registration: %s" % {k: sti.get(k) for k in ("leg", "reps", "n", "sepBar")})
    iso_reps = read_reps(os.path.join(di, "iso_replicates.csv"), key=0)
    iso = {}
    for dim in ISO["dims"]:
        xs = iso_reps.get(str(dim), [])
        if len(xs) != REG_REPS:
            refuse("iso leg slice %d: %d replicates, not %d" % (dim, len(xs), REG_REPS))
        iso[dim] = p95(xs)
        if iso[dim] != float(sti.get("p95_iso_%d" % dim, "nan")):
            refuse("iso leg slice %d: p95 recomputed %r != printed %r" % (dim, iso[dim], sti.get("p95_iso_%d" % dim)))
    for f in ("status.txt", "iso_replicates.csv"):
        files["%s/%s" % (CAL_DIRS["iso"], f)] = sha256_file(os.path.join(di, f))
    pq, pg = legs["qwen3_256"]["p95"], legs["gemma768"]["p95"]
    if not (pq > 0 and pg > 0):
        refuse("a TRAIN-root null p95 is not positive (qwen3 %r, gemma %r): the ratio is undefined" % (pq, pg))
    bar_g = BAR_OF_RECORD * pg / pq
    bar_width = BAR_OF_RECORD * iso[768] / iso[256]
    bar_512 = BAR_OF_RECORD * iso[512] / iso[256]
    ident = {dim: round(iso[dim], 4) == RECORD_ISO[dim] for dim in RECORD_ISO}
    bar_toml = "%.6f" % bar_g
    res = {"schema": "gemma_own_bar/bar/v1", "registration": REGISTRATION, "rule": "bar_g = 0.025 x p95_null(gemma 768) / p95_null(qwen3 256), "
           "MASSIVE TRAIN root, moment-matched site null, 300 reps", "p95_null_gemma768": pg, "p95_null_qwen3_256": pq, "bar_g": bar_g,
           "bar_toml": bar_toml, "p95_iso": {str(k): v for k, v in iso.items()}, "bar_width_only_768": bar_width,
           "bar_width_only_512": bar_512, "iso_identity_vs_D1": {str(k): bool(v) for k, v in ident.items()},
           "n_train": derived["n"], "train_text_set_sha256": derived["text_sha"], "build_table_sha256": derived["table_sha"],
           "emb_sha256": {e: pins[e] for e in ("qwen3", "gemma")}, "input_sha256": files,
           "script": "tools/analysis/gemma_own_bar.py blob:%s (LF)" % blob(os.path.abspath(__file__)),
           "readings": "GOB-K1 nulls at 0.025; GOB-K2 the distinct TRAIN texts; GOB-K3 siteNull seeds; GOB-B1 TOML 6 dp"}
    out("%s TRAIN-ONLY: both legs read the %d distinct MASSIVE salt-1 TRAIN texts (set sha256 %s = the re-derivation; build table %s); "
        "no GATE or EVAL text" % (TAG, derived["n"], derived["text_sha"][:16], derived["table_sha"][:16]))
    for leg in ("qwen3_256", "gemma768"):
        L = legs[leg]
        out("%s NULL %-9s slice %d: p95 %.6f (rank %d of %d; max %.6f; reached %d of %d); working copy sha256 %s = pin"
            % (TAG, leg, LEG[leg]["slice"], L["p95"], int(math.ceil(0.95 * REG_REPS)), REG_REPS, L["max"], L["reached"], REG_REPS,
               L["status"]["emb_sha256"][:16]))
    out("%s DECIDING BAR bar_g = 0.025 x %.6f / %.6f = %.6f (the TOML carries %s; GOB-B1)" % (TAG, pg, pq, bar_g, bar_toml))
    out("%s WIDTH-ONLY BAR (descriptive; isotropic, n %d): 0.025 x p95_iso(768) %.6f / p95_iso(256) %.6f = %.6f; at 512 %.6f "
        "(record %.4f)" % (TAG, ISO["n"], iso[768], iso[256], bar_width, bar_512, RECORD_BAR_512))
    out("%s D1 identity (descriptive): p95_iso(256) %.4f vs record %.4f %s; p95_iso(512) %.4f vs record %.4f %s"
        % (TAG, iso[256], RECORD_ISO[256], "REPRODUCED" if ident[256] else "NOT REPRODUCED", iso[512], RECORD_ISO[512],
           "REPRODUCED" if ident[512] else "NOT REPRODUCED"))
    if write:
        os.makedirs(root, exist_ok=True)
        with open(bar_path, "x", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(res, indent=1, sort_keys=True) + "\n")
        out("%s bar file written: %s sha256 %s" % (TAG, bar_path, sha256_file(bar_path)))
    else:
        out("%s DRY RUN: bar file NOT written (would be %s)" % (TAG, bar_path))
    return res


def load_bar(data_root=None):
    p = os.path.join(data_root or DATA_ROOT, OUT_REL, BAR_FILE)
    if not os.path.isfile(p):
        refuse("%s ABSENT: run --calibrate first (the bar is fixed before the build)" % p)
    b = json.load(open(p, encoding="utf-8"))
    if b.get("schema") != "gemma_own_bar/bar/v1" or b.get("bar_toml") != "%.6f" % b.get("bar_g", float("nan")):
        refuse("%s: schema or bar_toml inconsistent" % p)
    return b, sha256_file(p), p


# ================================================================================================ the G-AF config
OUTDIR_OLD = 'outputDir     = "experiment_results/intent_transfer/s1/m_af_g"'
OUTDIR_NEW = 'outputDir     = "%s"' % G_AF_OUT
BAR_OLD = "proposalSeparationBar = 0.025"


def config_text(src_text, bar_toml, bar_sha):
    """g_af.toml bytes: m_af_g.toml with its header comment replaced and EXACTLY two key lines changed (bar, outputDir)."""
    lines = src_text.replace("\r\n", "\n").split("\n")
    i = 0
    while i < len(lines) and lines[i].startswith("#"):
        i += 1
    body = lines[i:]
    for old in (OUTDIR_OLD, BAR_OLD):
        if body.count(old) != 1:
            refuse("the source TOML holds %r %d times (exactly once required)" % (old, body.count(old)))
    body = [OUTDIR_NEW if l == OUTDIR_OLD else ("proposalSeparationBar = %s" % bar_toml if l == BAR_OLD else l) for l in body]
    head = [
        "# GEMMA-OWN-BAR build G-AF. %s." % REGISTRATION,
        "# GENERATED by tools/analysis/gemma_own_bar.py --write-config (write-once; --check-config re-derives these bytes) from",
        "# %s (blob %s) with EXACTLY two keys changed: proposalSeparationBar = bar_g (bar file" % (SRC_CONFIG_REL, SRC_CONFIG_BLOB[:8]),
        "# %s/%s sha256 %s) and outputDir. Everything else byte-identical, including corpusDbPath (GOB-B2: a FRESH" % (OUT_REL, BAR_FILE, bar_sha),
        "# intent_s1_export.py --export M-AF-g in this run's DATA_ROOT, never S1's used file), reservedPoolFile, pool and embeddingSliceDim.",
        "# ZERO judge / LLM calls; label-free. Launch: tools/analysis/gemma_own_bar.py --launch-plan.",
        "#",
    ]
    return ("\n".join(head + body)).encode("utf-8")


def check_two_changes(src_bytes, new_bytes):
    """Every non-comment line equal except outputDir and proposalSeparationBar; tomllib keys equal except those two."""
    a = [l for l in src_bytes.decode("utf-8").replace("\r\n", "\n").split("\n") if not l.startswith("#")]
    b = [l for l in new_bytes.decode("utf-8").replace("\r\n", "\n").split("\n") if not l.startswith("#")]
    if len(a) != len(b):
        refuse("config line count differs (%d vs %d)" % (len(a), len(b)))
    diff = [(x, y) for x, y in zip(a, b) if x != y]
    ta, tb = tomllib.loads("\n".join(a)), tomllib.loads("\n".join(b))
    kd = sorted(k for k in set(ta) | set(tb) if ta.get(k) != tb.get(k))
    if len(diff) != 2 or kd != ["outputDir", "proposalSeparationBar"]:
        refuse("the config differs from m_af_g.toml in %d lines / keys %s (exactly outputDir and proposalSeparationBar allowed)" % (len(diff), kd))
    return tb


def regen_config(data_root=None):
    root = data_root or DATA_ROOT
    src = os.path.join(root, SRC_CONFIG_REL)
    if not os.path.isfile(src) or blob(src) != SRC_CONFIG_BLOB:
        refuse("%s is absent or not blob %s (S1's committed M-AF-g TOML)" % (src, SRC_CONFIG_BLOB))
    b, bsha, _p = load_bar(root)
    sb = open(src, "rb").read()
    nb = config_text(sb.decode("utf-8"), b["bar_toml"], bsha)
    t = check_two_changes(sb, nb)
    if repr(t["proposalSeparationBar"]) != repr(float(b["bar_toml"])):
        refuse("the generated bar %r != the bar file's %s" % (t["proposalSeparationBar"], b["bar_toml"]))
    return nb, b, bsha


def write_config(data_root=None, write=True, out=print):
    root = data_root or DATA_ROOT
    nb, b, bsha = regen_config(root)
    p = os.path.join(root, CONFIG_REL)
    out("%s config %s: proposalSeparationBar = %s (bar file sha256 %s), outputDir = %s; all else = %s" % (TAG, p, b["bar_toml"], bsha[:16], G_AF_OUT, SRC_CONFIG_REL))
    if os.path.lexists(p):
        if open(p, "rb").read().replace(b"\r\n", b"\n") == nb:
            out("%s config already present and identical (left alone)" % TAG)
            return p
        refuse("%s exists with different bytes (write-once)" % p)
    if not write:
        out("%s DRY RUN: config NOT written" % TAG)
        return p
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "xb") as fh:
        fh.write(nb)
    out("%s config written: %s blob %s" % (TAG, p, blob(p)))
    return p


def check_config(data_root=None, out=print):
    root = data_root or DATA_ROOT
    nb, _b, _s = regen_config(root)
    p = os.path.join(root, CONFIG_REL)
    if not os.path.isfile(p) or open(p, "rb").read().replace(b"\r\n", b"\n") != nb:
        refuse("%s is absent or differs from the regenerated bytes" % p)
    out("%s config check: %s = the regenerated bytes (blob %s)" % (TAG, p, blob(p)))
    return 0


# ================================================================================================ plans (print only)
def calibrate_plan(out=print):
    root = DATA_ROOT
    pins = emb_pins()
    cal = os.path.join(root, OUT_REL)
    out("%s CALIBRATION PLAN (NOT launched; rule 7 W1-W5 per leg; one JVM at a time; -PjvmThreads per the THREAD-CAP):" % TAG)
    out("  0. DATA_ROOT %s holds the pinned ingest DB and intent_emb_{qwen3,gemma}.db (S1's run layout) and a FRESH" % root)
    out("     intent_s1_build/m_af_g.db: python tools/analysis/intent_s1_export.py --export M-AF-g (table sha must be %s)" % S1_TABLE_SHA[:16])
    out("  1. working copies: copy intent_emb_qwen3.db (pin %s) and intent_emb_gemma.db (pin %s) to %s/gemma_own_bar_work/cal_<ts>/;"
        % (pins["qwen3"], pins["gemma"], root))
    out("     each copy's sha256 = its pin (the arm re-checks and refuses otherwise)")
    out("  2. gradlew.bat gemmaOwnBar -PjvmThreads=<cap> -DgobArm=iso -DoutDir=%s/%s" % (cal, CAL_DIRS["iso"]))
    for leg, spec in LEG.items():
        out("  %d. gradlew.bat gemmaOwnBar -PjvmThreads=<cap> -DsiteNullHeap=<per [SITENULL-HEAP]> -DgobArm=%s -DoutDir=%s/%s"
            " -DgobBuildDb=%s/intent_s1_build/m_af_g.db -DgobEmbDb=<copy of intent_emb_%s.db> -DgobEmbSha256=%s"
            % (3 if leg == "qwen3_256" else 4, leg, cal, CAL_DIRS[leg], root, spec["emb"], pins[spec["emb"]]))
    out("  5. python tools/analysis/gemma_own_bar.py --calibrate --dry-run ; then --calibrate (bar_g.json, write-once; pin its sha256)")
    preflight(root, pins, out)
    return 0


def preflight(root, pins, out=print):
    """Operator aid, print-only (nothing decided, nothing written): the re-derived MASSIVE salt-1 TRAIN, the build DB if present, and
    the TRAIN coverage of both pinned embedding DBs (read-only, immutable, after the sidecar check)."""
    der = derived_train()
    out("%s PREFLIGHT re-derived MASSIVE salt-1 TRAIN: %d distinct texts, set sha256 %s, table sha %s (%s S1's export manifest)"
        % (TAG, der["n"], der["text_sha"][:16], der["table_sha"][:16], "=" if der["table_sha"] == S1_TABLE_SHA else "DIFFERS FROM"))
    bdb = os.path.join(root, EX.BUILD_DIR_NAME, "m_af_g.db")
    texts = None
    if not os.path.isfile(bdb):
        out("%s PREFLIGHT build DB %s ABSENT (export it fresh: intent_s1_export.py --export M-AF-g)" % (TAG, bdb))
    else:
        try:
            con = EX.II.open_db_ro(bdb)
        except SystemExit as e:
            out("%s PREFLIGHT build DB %s NOT READABLE: %s (GOB-B2: a fresh export, never S1's used file)" % (TAG, bdb, e))
        else:
            try:
                meta = dict(con.execute("SELECT key, value FROM intent_build_meta").fetchall())
                texts = [r[0] for r in con.execute("SELECT question FROM intent_corpus WHERE side = 'TRAIN' ORDER BY id")]
            finally:
                con.close()
            ok = meta.get("table_sha256") == der["table_sha"] and len(texts) == der["n"] and text_set_sha(texts) == der["text_sha"]
            out("%s PREFLIGHT build DB %s: arm %s, %d TRAIN rows, set sha256 %s, table sha %s -> %s"
                % (TAG, bdb, meta.get("arm"), len(texts), text_set_sha(texts)[:16], (meta.get("table_sha256") or "")[:16], "MATCHES" if ok else "DIFFERS"))
    if texts is None:
        items, _s, _d = EX.inputs()
        texts = [r["text"] for r in EX.derive(items)[("massive", 1)]["rows"] if r["side"] == SS.TRAIN]
    for e in ("qwen3", "gemma"):
        p = os.path.join(root, EX.EMB_FILE[e])
        if not os.path.isfile(p):
            out("%s PREFLIGHT %s ABSENT" % (TAG, p))
            continue
        have, meta = EX.coverage(p, texts)
        out("%s PREFLIGHT %s: model %s native_dim %s; %d of %d TRAIN texts have a vector; pin %s" % (TAG, p, meta.get("model"), meta.get("native_dim"),
                                                                                                  have, len(texts), pins[e][:16]))
    return 0


def launch_plan(out=print):
    root = DATA_ROOT
    pin = emb_pins()["gemma"]
    out("%s BUILD PLAN G-AF (NOT launched; after --calibrate and --write-config; rule 7 W1-W5; a backup first):" % TAG)
    out("  1. python tools/analysis/gemma_own_bar.py --check-config   (%s = m_af_g.toml + bar_g, two keys)" % CONFIG_REL)
    out("  2. build DB %s/intent_s1_build/m_af_g.db: the FRESH export of step 0 of --calibrate-plan (GOB-B2); intent_s1_export.py"
        " verify passes; table sha %s" % (root, S1_TABLE_SHA[:16]))
    out("  3. copy intent_emb_gemma.db (sha256 must be %s) -> %s/intent_s1_work/g_af_<ts>/intent_emb_gemma.db; copy sha256 = pin" % (pin, root))
    out("  4. gradlew.bat bootRun -PjvmThreads=<cap> -Dtaxoarena.embeddingCacheFile=<copy> -Dtaxoarena.embeddingCacheSourceSha256=%s"
        " -Dtaxoadapt.llm.embedding-model=embeddinggemma:latest -Dranking.db.path=%s/%s/seed_42/ratings_intent_s1.db"
        " --args=\"--config %s\"" % (pin, root, G_AF_OUT, CONFIG_REL))
    out("  5. after exit: the pinned emb DBs and the ingest DB re-hashed unchanged; '[INTENT] fetched' with 9826 / 1676; then --run --dry-run")
    return 0


# ================================================================================================ GO1 readout
def verdict_lines(R):
    """Every registered print branch (GO1 verdict, degenerate tree, F-GO, predictions) from a result dict."""
    r1, L = R["T-C1"], R["L"]
    out = []
    degenerate = bool(L < DEGENERATE_BELOW)
    out.append("GO1 (DECIDING; S1's T-C1 rule verbatim): %s%s" % (r1["verdict"], " (degenerate tree)" if degenerate else ""))
    out.append("  VERDICT LINE (registered Support (f)): GO1 SCOREABLE provided G-AF builds at least %d leaves; L = %d -> %s"
               % (DEGENERATE_BELOW, L, "GO1 read but marked \"degenerate tree\"" if degenerate else "SCOREABLE"))
    leaf_clause = bool(L <= FGO_LEAVES_AT_MOST)
    loss_clause = bool(r1["loss"])
    if leaf_clause or loss_clause:
        why = " and ".join(([("G-AF built %d <= %d leaves under its own bar" % (L, FGO_LEAVES_AT_MOST))] if leaf_clause else []) +
                           (["GO1 flags LOSS (%s)" % r1["verdict"]] if loss_clause else []))
        out.append("F-GO FIRES (%s): %s" % (why, SENT_FGO_FIRED))
    else:
        out.append("F-GO does not fire (L = %d > %d; no LOSS flag): %s" % (L, FGO_LEAVES_AT_MOST, SENT_FGO_NOT))
    out.extend(prediction_lines(R))
    return out


def in_band(x, lo, hi):
    return bool(np.isfinite(x) and lo <= x <= hi)


def prediction_lines(R):
    r1 = R["T-C1"]
    out = []
    for pid, x, fmt in (("P1", R["bar_g"], "bar_g %.6f"), ("P2", R["L"], "G-AF leaves %d"), ("P3", r1["D"], "D1 %+.5f")):
        lo, hi = BANDS[pid]
        out.append("%s %s in [%s, %s]: %s" % (pid, fmt % x, lo, hi, "HELD" if in_band(float(x), lo, hi) else "MISSED"))
    for word, key in (("EQUIVALENT", "eq"), ("LOSS", "loss")):
        ev = bool(r1[key])
        out.append("P3 GO1 %s p %.2f: event %s, Brier %.4f" % (word, PROB[word], "occurred" if ev else "did not occur", (PROB[word] - float(ev)) ** 2))
    return out


def support_lines(R):
    r1 = R["T-C1"]
    deff = r1["kish"]
    reach = r1["delta"] - IS1.Z90 * r1["se_total"]
    return ["SUPPORT (measured beside registered): EVAL n %d / components %d (registered %d / %d); Kish DEFF %.4f (registered %.4f), "
            "n_eff %.0f; SE_boot %.5f, SE_total %.5f (registered ~%.4f); MDE80 2.8 x SE_total = %.5f; TOST reach delta_c - 1.645 SE_total "
            "= %.5f (registered %.3f at planning delta_c %.3f)" % (r1["n"], r1["G"], REG_SUPPORT["n"], REG_SUPPORT["G"], deff,
                                                                  REG_SUPPORT["deff"], r1["n"] / deff, r1["se_boot"], r1["se_total"],
                                                                  REG_SUPPORT["se_total"], r1["mde"], reach, REG_SUPPORT["reach"],
                                                                  REG_SUPPORT["delta_c_plan"]),
            "DENOMINATOR: MASSIVE EVAL items with a gemma vector (components = CK-CLOSE components; component bootstrap B %d); "
            "wrong(established) / tie conventions: not applicable (an NMI contrast, no pairwise verdicts)" % S0.BOOT_B]


def compute_go(W, T, sid, diag_path, bar, leaves_ref, slice_g=SLICE_G):
    """Phase 1 (TRAIN / GATE: delta_c, k-means at k = L) -> freeze -> phase 2 (EVAL: T-C1; T-C7 / T-C9 descriptive)."""
    if T["d"] != slice_g:
        refuse("G-AF's slice %d != %d" % (T["d"], slice_g))
    IS1.STATE["gate_frozen"] = False
    del IS1.FIT_LOG[:]
    A = IS1.make_arm(W, "M-AF-g", T, sid)         # MASSIVE, salt 1, gemma vectors; the tree is G-AF's
    A["name"] = "G-AF"
    A = IS1.phase_gate(A, False, diag_path=diag_path, need_km=True)
    gate = dict(A["gate"])
    IS1.STATE["gate_frozen"] = True
    r1 = IS1.t_c1(A)
    r7 = IS1.t_c7(A, W)
    r9 = IS1.t_c9(A, W, r7=r7)
    return {"L": A["L"], "d": T["d"], "T-C1": r1, "T-C7": {k: v for k, v in r7.items() if k not in ("same_t", "oi", "Xv")}, "T-C9": r9, "gate": gate,
            "accept": A["accept"], "bar_g": float(bar["bar_g"]), "bar": bar, "leaves_ref": leaves_ref, "fit_log": list(IS1.FIT_LOG),
            "sid": sid}


def render(R, meta):
    r1, r7, r9, g, b = R["T-C1"], R["T-C7"], R["T-C9"], R["gate"], R["bar"]
    L = ["GEMMA-OWN-BAR outcome (zero calls). %s" % REGISTRATION]
    for k in sorted(meta):
        L.append("  %s: %s" % (k, meta[k]))
    L.append("BAR (fixed before the build; bar file sha256 %s): bar_g = 0.025 x %.6f / %.6f = %.6f (TOML %s); width-only bar at 768 "
             "%.6f (descriptive)" % (meta.get("bar file sha256", "?"), b["p95_null_gemma768"], b["p95_null_qwen3_256"], b["bar_g"],
                                     b["bar_toml"], b["bar_width_only_768"]))
    L.append("G-AF: snapshot %s, %d leaves, slice %d; GATE descent agreement %.5f (%d of %d; printed, not required)"
             % (R["sid"], R["L"], R["d"], R["accept"]["agree"], R["accept"]["k"], R["accept"]["n"]))
    L.append("GATE CONSTANTS (fixed before any EVAL statistic): n_gate %d; NMI_fine(supervised) %.5f; mean_s NMI_fine(k-means at k = L, "
             "seeds 0-19) %.5f; delta_c = 0.25 x (sup - km) = %.5f; T-C9 threshold %.5f" % (g["n_gate"], g["nmi_sup"], g["nmi_km_mean"],
                                                                                         g["delta_c"], g["thr_tree"]))
    L.append("T-C1 / GO1: D1 = NMI_fine(G-AF, flatLeaf) %.5f - mean_s NMI_fine(k-means k = L) %.5f = %+.5f; TOST 90%% [%+.5f, %+.5f] "
             "vs +/- delta_c %.5f; 95%% CI [%+.5f, %+.5f]; spread_K (seeds 0-4) %.5f; bar max(MDE80, spread_K) %.5f"
             % (r1["n_tree"], r1["n_km_mean"], r1["D"], r1["lo90"], r1["hi90"], r1["delta"], r1["lo"], r1["hi"], r1["spread_K"], r1["bar"]))
    L.extend(support_lines(R))
    L.extend(verdict_lines(R))
    ref = R["leaves_ref"]
    L.append("DESCRIPTIVE leaves: G-AF %d vs M-AF-g %s (qwen3-tuned bar 0.025, gemma 768) vs M-AF %s (qwen3 256)"
             % (R["L"], ref["M-AF-g"], ref["M-AF"]))
    L.append("DESCRIPTIVE T-C7: D7 %+.5f [%+.5f, %+.5f]; S(tree) %.5f, S(km) %.5f; ceiling %.5f, floor (K = 60) %.5f, delta %.5f -> %s"
             % (r7["D"], r7["lo"], r7["hi"], r7["S_tree"], r7["S_km_mean"], r7["ceiling"], r7["floor"], r7["delta"], r7["verdict"]))
    L.append("DESCRIPTIVE T-C9: D9 %+.5f [%+.5f, %+.5f] (abstained %d, kept %d; threshold %.5f) -> %s"
             % (r9["D9"], r9["lo"], r9["hi"], r9["n_abstained"], r9["n_kept"], r9["thr"], r9["verdict"]))
    L.append("TRAIN-ONLY AUDIT: " + "; ".join("%s on %s n=%d sides %s" % f for f in R["fit_log"]))
    L.append("WHAT THIS RESULT WILL NOT SHOW: %s" % DOES_NOT_SHOW)
    L.append("BUILDER'S READINGS: GOB-K1 GOB-K2 GOB-K3 GOB-B1 GOB-B2 GOB-R1 GOB-R2 (see the script docstring)")
    return L


def g_af_presence(data_root):
    rd = os.path.join(data_root, G_AF_OUT, "seed_42")
    sid, why = IS1.snapshot_id_of(rd)
    need = {"validation/MAIN_routing_diagnostics.txt": os.path.isfile(os.path.join(rd, "validation", "MAIN_routing_diagnostics.txt")),
            "dag_snapshots.jsonl": os.path.isfile(os.path.join(rd, "dag_snapshots.jsonl")),
            "diagnostics/run_manifest.json": os.path.isfile(os.path.join(rd, "diagnostics", "run_manifest.json")),
            "diagnostics/config.toml": os.path.isfile(os.path.join(rd, "diagnostics", "config.toml"))}
    miss = [k for k, v in need.items() if not v]
    if sid is None or miss:
        refuse("G-AF build ABSENT or incomplete at %s: %s" % (rd, why if sid is None else "missing " + ", ".join(miss)))
    return {"present": True, "sid": sid, "rd": rd, "why": ""}


def check_build_config(rd, data_root):
    nb, b, bsha = regen_config(data_root)
    got = open(os.path.join(rd, "diagnostics", "config.toml"), "rb").read().replace(b"\r\n", b"\n")
    if got != nb:
        refuse("the build's diagnostics/config.toml != g_af.toml regenerated from the bar file (the build did not use bar_g %s)" % b["bar_toml"])
    return b, bsha


def s1_leaves(s1_root):
    out = dict(LEAVES_REF)
    note = "record values (POSTRUN_intent_s1)"
    if s1_root:
        got = {}
        for n, slug in S1_SLUG.items():
            lv = IS1.last_dag_leaves(os.path.join(s1_root, EX.OUT_ROOT, slug, "seed_42"))
            got[n] = len(lv) if lv is not None else None
        note = "re-read from %s: %s (%s)" % (s1_root, got, "= record" if got == LEAVES_REF else "DIFFERS from the record %s" % LEAVES_REF)
        out = {n: (got[n] if got[n] is not None else LEAVES_REF[n]) for n in LEAVES_REF}
    return out, note


def load_inputs(data_root, snap_db):
    """The real loader: S1's load_world / census / load_tree_checked on the G-AF run dir."""
    pres = g_af_presence(data_root)
    W = IS1.load_world(["M-AF-g"], None, None, None)
    cen, bad = IS1.census(W)
    if bad:
        refuse("census off by more than 5%%: %s" % "; ".join(bad))
    D_ex = IS1.derive_inputs(W["db"])
    pins = {e[4:]: s for e, s in W["pins"].items() if e.startswith("emb_")}
    T, _g = IS1.load_tree_checked("M-AF-g", pres, snap_db, D_ex, pins)
    return {"W": W, "T": T, "sid": pres["sid"], "rd": pres["rd"], "census": cen, "pins": W["pins"]}


def run(data_root=None, snap_db=None, write=True, s1_root=None, out_dir=None, skip_heavy=False, loader=None, slice_g=SLICE_G, out=print):
    root = data_root or DATA_ROOT
    out_dir = out_dir or os.path.join(root, OUT_REL)
    path = os.path.join(out_dir, OUTCOME)
    if write and os.path.lexists(path):
        refuse("%s exists: the outcome is write-once" % path)
    out("%s %s: zero calls. %s" % (TAG, "RUN" if write else "DRY RUN (no EVAL statistic; nothing written)", REGISTRATION))
    check_code_pins()
    if not skip_heavy:
        IS1.check_heavy()
    bar, bsha, bpath = load_bar(root)
    out("%s bar file %s sha256 %s: bar_g %.6f (TOML %s)" % (TAG, bpath, bsha, bar["bar_g"], bar["bar_toml"]))
    inp = (loader or load_inputs)(root, snap_db or os.path.join(root, "snapshots.db"))
    check_build_config(inp["rd"], root)
    out("%s build config = g_af.toml regenerated from the bar file (bar %s, two keys changed from m_af_g.toml)" % (TAG, bar["bar_toml"]))
    T = inp["T"]
    L = len(T["leaves"])
    out("%s G-AF snapshot %s: %d nodes, %d leaves, slice %d" % (TAG, inp["sid"], len(T["nodes"]), L, T["d"]))
    leaves_ref, note = s1_leaves(s1_root)
    diag = os.path.join(inp["rd"], "validation", "MAIN_routing_diagnostics.txt")
    if not write:
        IS1.STATE["gate_frozen"] = False
        A = IS1.make_arm(inp["W"], "M-AF-g", T, inp["sid"])
        A["name"] = "G-AF"
        A = IS1.phase_gate(A, False, diag_path=diag, need_km=False)
        out("%s GATE: n %d; T-C9 thr %.5f; descent agreement %.5f; delta_c and GO1 computed at --run; S1 leaves %s"
            % (TAG, A["gate"]["n_gate"], A["gate"]["thr_tree"], A["accept"]["agree"], note))
        out("%s DRY RUN complete: no EVAL statistic computed; 0 files written" % TAG)
        return None, None, None
    R = compute_go(inp["W"], T, inp["sid"], diag, bar, leaves_ref, slice_g=slice_g)
    meta = {"script": "tools/analysis/gemma_own_bar.py blob:%s (LF)" % blob(os.path.abspath(__file__)),
            "instrument": ", ".join("%s blob:%s" % kv for kv in sorted(PINNED_CODE.items())),
            "pins (sha256-bytes)": json.dumps(inp.get("pins", {}), sort_keys=True), "census": json.dumps(inp.get("census", {}), sort_keys=True),
            "bar file sha256": bsha, "S1 leaves": note}
    lines = render(R, meta)
    os.makedirs(out_dir, exist_ok=True)
    with open(path, "x", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    for l in lines:
        out(l)
    out("%s outcome written: %s sha256 %s" % (TAG, path, sha256_file(path)))
    return R, lines, path


# ================================================================================================ selftest (fixtures only)
SELFTEST_CASES = ("ST-CAL", "ST-CFG", "ST-VERD", "ST-E2E")
SELFTEST_DOC = """SELFTEST (fixtures only; no repo DB read): ST-CAL (the real calibrate() on three fixture leg dirs with known replicates:
p95 = the 285th of 300 and of 301 values, bar_g = 0.025 x p95_g / p95_q to the bit, the width-only bar and the D1 identity words,
the TOML string; refusals: reps 299, sepBar 0.0145, a slice off, an emb sha off the pin, a TRAIN set off the re-derivation (GATE
admitted), n_train off, the build table off, a printed p95 off, the two legs' populations differing, an iso slice short, a
non-positive p95; write-once (a second write refuses, bytes unchanged); the dry run writes nothing), ST-CFG (write_config on the
real m_af_g.toml: exactly two non-comment lines and two tomllib keys differ, the bar and outputDir values; write-once; identical
re-write left alone; check_config catches one changed byte; a missing bar file and a foreign source TOML refuse), ST-VERD (every
GO1 / degenerate / F-GO / prediction print branch on derived result dicts: L 9 / 10 / 11, EQUIVALENT, EQUIVALENT / LOSS-FLAGGED,
LOSS, GAIN, UNDETERMINED; band boundaries inclusive; Brier values), ST-E2E (the real run() on S1's fixture world with injected
trees: D1 equals an independent NMI computation, the verdict word equals the T-C1 rule applied here to the printed numbers, the
GATE constants line precedes every EVAL line, L, F-GO and P-lines by value, a random tree fires LOSS and F-GO, a 4-leaf tree is
degenerate; write-once; a build config off the bar refuses; the dry run computes no EVAL statistic and writes nothing)."""


def _write_leg(root, leg, reps, **over):
    d = os.path.join(root, OUT_REL, CAL_DIRS[leg])
    os.makedirs(d, exist_ok=True)
    if leg == "iso":
        st = {"leg": "iso", "n": "406", "sigma": "0.5", "reps": str(len(reps[256])), "minClusterSize": "55", "sepBar": "0.025"}
        for dim, xs in reps.items():
            st["p95_iso_%d" % dim] = repr(p95(xs))
        with open(os.path.join(d, "iso_replicates.csv"), "w", encoding="utf-8") as f:
            f.write("dim,rep,stat\n" + "".join("%d,%d,%r\n" % (dim, i, x) for dim, xs in reps.items() for i, x in enumerate(xs)))
    else:
        spec = LEG[leg]
        st = {"leg": "null", "arm": leg, "embedder": spec["emb"], "model": spec["model"], "sliceDim": str(spec["slice"]), "sepBar": "0.025",
              "minClusterSize": "55", "reps": str(len(reps)), "n_train": "120", "build_table_sha256": "T" * 64,
              "train_text_set_sha256": text_set_sha(["t%d" % i for i in range(120)]), "emb_sha256": spec["emb"][0] * 64, "p95": repr(p95(reps))}
        with open(os.path.join(d, "replicates.csv"), "w", encoding="utf-8") as f:
            f.write("rep,stat\n" + "".join("%d,%r\n" % (i, x) for i, x in enumerate(reps)))
    st.update(over)
    with open(os.path.join(d, "status.txt"), "w", encoding="utf-8") as f:
        f.write("COMPLETE\n" + "".join("%s=%s\n" % kv for kv in st.items()))
    return d


def _cal_fixture(td, rng):
    q = rng.permutation(np.arange(300) / 10000.0 + 0.0100)          # p95 = 285th smallest = 0.0384
    g = rng.permutation(np.arange(300) / 20000.0 + 0.0050)          # p95 = 0.0192
    iso = {256: rng.permutation(np.arange(300) / 100000.0 + 0.0041),   # p95 0.00694 -> 4 dp 0.0069
           512: rng.permutation(np.arange(300) / 100000.0 + 0.0012),   # p95 0.00404 -> 0.0040
           768: rng.permutation(np.arange(300) / 100000.0 + 0.0001)}   # p95 0.00294
    _write_leg(td, "qwen3_256", q.tolist())
    _write_leg(td, "gemma768", g.tolist())
    _write_leg(td, "iso", {k: v.tolist() for k, v in iso.items()})
    return {"table_sha": "T" * 64, "text_sha": text_set_sha(["t%d" % i for i in range(120)]), "n": 120}, {"qwen3": "q" * 64, "gemma": "g" * 64}


def _flat_tree(C, X, side, d, mus, kappa=30.0):
    tr = np.nonzero(C.kept & ~C.oos & (side == SS.TRAIN))[0]
    lab = S0.assign(X[tr], mus) if len(mus) else np.zeros(0, dtype=int)
    nodes, root, kids = [], "n00000001", []
    for j in range(len(mus)):
        lid = "n%08d" % (j + 2)
        qids = ["q_%s" % hashlib.sha256(C.text[i].encode()).hexdigest()[:16] for i in tr[lab == j]]
        nodes.append({"id": lid, "childIds": [], "parentIds": [root], "sliceDim": d, "vmfMu": [float(x) for x in mus[j]], "vmfKappa": kappa,
                      "queryIds": qids, "queryWeights": {q: 1.0 for q in qids}})
        kids.append(lid)
    nodes.append({"id": root, "childIds": kids, "parentIds": [], "sliceDim": d, "vmfMu": S0.unit(X[tr].mean(0)[None, :])[0].tolist(),
                  "vmfKappa": 5.0, "queryIds": [], "queryWeights": {}})
    settings = {"membershipFloor": 0.25, "routingBeamGamma": 0.2, "descentMargin": 0.12, "maxLeafAssignments": 5, "dagMode": "DAG_MAX"}
    return IS1.tree_of({"rootId": root, "nodes": nodes}, settings)


def _e2e_world(td):
    with contextlib.redirect_stdout(io.StringIO()):
        W, _trees, _graphs, _diags = IS1.build_fixture(td)
    C = W["CS"]["massive"]
    side = IS1.arm_sides(C, 1)
    R, have = IS1.raw_matrix(C, W["vecs"]["gemma"], 16)
    X = IS1.sliced(R, 16)
    return W, C, side, X, have


def _e2e_case(td, name, W, C, side, X, mus, data_root):
    T = _flat_tree(C, X, side, 16, mus)
    rd = os.path.join(data_root, G_AF_OUT + "_" + name, "seed_42")
    os.makedirs(os.path.join(rd, "diagnostics"), exist_ok=True)
    ga = np.nonzero(C.kept & ~C.oos & (side == SS.GATE))[0]
    texts, idx, seen = [], [], set()
    for i in ga:
        if C.text[i] not in seen:
            seen.add(C.text[i]); texts.append(C.text[i]); idx.append(i)
    IS1._write_diag(os.path.join(rd, "validation", "MAIN_routing_diagnostics.txt"), texts, IS1.Descent(T).top1(X[np.array(idx, dtype=int)]))
    nb, _b, _s = regen_config(data_root)
    with open(os.path.join(rd, "diagnostics", "config.toml"), "wb") as f:
        f.write(nb)
    return T, rd


def selftest(only=None, quiet=False):
    sel = set(only or SELFTEST_CASES)
    n_ok = [0]

    def check(cond, what):
        if not cond:
            raise AssertionError("SELFTEST FAILED: %s" % what)
        n_ok[0] += 1

    def refused(fn, needle):
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                fn()
        except SystemExit as e:
            check(needle in str(e), "refusal %r lacks %r" % (str(e), needle))
            return
        raise AssertionError("SELFTEST FAILED: no refusal (wanted %r)" % needle)

    rng = np.random.default_rng(3)
    src_toml = open(os.path.join(ROOT, SRC_CONFIG_REL), "rb").read()

    def fresh_root():
        td = tempfile.mkdtemp(prefix="gob_st_")
        os.makedirs(os.path.join(td, os.path.dirname(SRC_CONFIG_REL)))
        with open(os.path.join(td, SRC_CONFIG_REL), "wb") as f:
            f.write(src_toml)
        return td

    roots = []
    try:
        if "ST-CAL" in sel:
            check(p95(list(range(300))) == 284 and p95(list(range(301))) == 285 and p95([5.0]) == 5.0, "p95 rank rule (300 -> 285th; 301 -> 286th)")
            td = fresh_root(); roots.append(td)
            der, pins = _cal_fixture(td, rng)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                res = calibrate(td, write=False, derived=der, pins=pins, out=print)
            txt = buf.getvalue()
            check(not os.path.exists(os.path.join(td, OUT_REL, BAR_FILE)), "the calibrate dry run writes nothing")
            pq, pg = 0.0100 + 284 / 10000.0, 0.0050 + 284 / 20000.0
            check(res["p95_null_qwen3_256"] == pq and res["p95_null_gemma768"] == pg, "the two null p95s (285th of 300)")
            check(res["bar_g"] == 0.025 * pg / pq and abs(res["bar_g"] - 0.0125) < 1e-12, "bar_g = 0.025 x p95_g / p95_q (0.0125)")
            check(res["bar_toml"] == "0.012500", "the TOML bar string")
            i256, i512, i768 = 0.0041 + 284e-5, 0.0012 + 284e-5, 0.0001 + 284e-5
            check(res["bar_width_only_768"] == 0.025 * i768 / i256 and res["bar_width_only_512"] == 0.025 * i512 / i256, "width-only bars")
            check(res["iso_identity_vs_D1"] == {"256": True, "512": True}, "D1 identity words")
            check("DECIDING BAR bar_g = 0.025 x 0.019200 / 0.038400 = 0.012500" in txt, "deciding bar line by value")
            check("p95_iso(256) 0.0069 vs record 0.0069 REPRODUCED" in txt and "WIDTH-ONLY BAR" in txt, "identity and width-only lines")
            with contextlib.redirect_stdout(io.StringIO()):
                calibrate(td, write=True, derived=der, pins=pins)
            bp = os.path.join(td, OUT_REL, BAR_FILE)
            b0 = open(bp, "rb").read()
            check(json.loads(b0)["bar_g"] == res["bar_g"], "bar file value")
            refused(lambda: calibrate(td, write=True, derived=der, pins=pins), "write-once")
            check(open(bp, "rb").read() == b0, "a refused re-write leaves the bar file unchanged")
            # each refusal on its own fresh fixture
            cases = [
                ("qwen3_256", {"reps": "299"}, "status fields off"),
                ("gemma768", {"sepBar": "0.0145"}, "status fields off"),
                ("gemma768", {"sliceDim": "256"}, "status fields off"),
                ("gemma768", {"emb_sha256": "x" * 64}, "!= the pin"),
                ("qwen3_256", {"train_text_set_sha256": text_set_sha(["t%d" % i for i in range(130)])}, "TRAIN-ONLY"),
                ("gemma768", {"n_train": "130"}, "TRAIN-ONLY"),
                ("gemma768", {"build_table_sha256": "U" * 64}, "table sha"),
                ("qwen3_256", {"p95": "0.05"}, "p95 recomputed"),
            ]
            for leg, over, needle in cases:
                tdx = fresh_root(); roots.append(tdx)
                derx, pinsx = _cal_fixture(tdx, rng)
                st = os.path.join(tdx, OUT_REL, CAL_DIRS[leg], "status.txt")
                lines = open(st, encoding="utf-8").read().split("\n")
                lines = [("%s=%s" % (l.split("=", 1)[0], over[l.split("=", 1)[0]]) if "=" in l and l.split("=", 1)[0] in over else l) for l in lines]
                open(st, "w", encoding="utf-8").write("\n".join(lines))
                refused(lambda: calibrate(tdx, derived=derx, pins=pinsx), needle)
            tdx = fresh_root(); roots.append(tdx)
            derx, pinsx = _cal_fixture(tdx, rng)
            _write_leg(tdx, "qwen3_256", list(np.arange(299) / 1000.0))
            refused(lambda: calibrate(tdx, derived=derx, pins=pinsx), "status fields off")      # reps 299 in status and file
            tdx = fresh_root(); roots.append(tdx)
            derx, pinsx = _cal_fixture(tdx, rng)
            _write_leg(tdx, "iso", {256: [0.001] * 300, 512: [0.001] * 300, 768: [0.001] * 299})
            refused(lambda: calibrate(tdx, derived=derx, pins=pinsx), "iso leg")
            tdx = fresh_root(); roots.append(tdx)
            derx, pinsx = _cal_fixture(tdx, rng)
            _write_leg(tdx, "qwen3_256", [0.0] * 300)
            refused(lambda: calibrate(tdx, derived=derx, pins=pinsx), "not positive")
            tdx = fresh_root(); roots.append(tdx)
            derx, pinsx = _cal_fixture(tdx, rng)
            refused(lambda: calibrate(tdx, derived=dict(derx, text_sha=text_set_sha(["t%d" % i for i in range(120)] + ["gate text"])), pins=pinsx), "TRAIN-ONLY")
            tdx = fresh_root(); roots.append(tdx)
            derx, pinsx = _cal_fixture(tdx, rng)
            os.remove(os.path.join(tdx, OUT_REL, CAL_DIRS["gemma768"], "status.txt"))
            refused(lambda: calibrate(tdx, derived=derx, pins=pinsx), "ABSENT")

        if "ST-CFG" in sel:
            td = fresh_root(); roots.append(td)
            refused(lambda: write_config(td), "ABSENT: run --calibrate first")
            der, pins = _cal_fixture(td, rng)
            with contextlib.redirect_stdout(io.StringIO()):
                calibrate(td, write=True, derived=der, pins=pins)
                write_config(td, write=False)
            check(not os.path.exists(os.path.join(td, CONFIG_REL)), "write_config dry run writes nothing")
            with contextlib.redirect_stdout(io.StringIO()):
                p = write_config(td)
            nb = open(p, "rb").read()
            a = [l for l in src_toml.decode().replace("\r\n", "\n").split("\n") if not l.startswith("#")]
            b = [l for l in nb.decode().split("\n") if not l.startswith("#")]
            diff = sorted((x, y) for x, y in zip(a, b) if x != y)
            check(len(a) == len(b) and diff == sorted([(OUTDIR_OLD, OUTDIR_NEW), (BAR_OLD, "proposalSeparationBar = 0.012500")]), "exactly two lines differ: %s" % diff)
            t = tomllib.loads(nb.decode())
            ts = tomllib.loads(src_toml.decode())
            check(t["proposalSeparationBar"] == 0.0125 and t["outputDir"] == G_AF_OUT, "the two new values")
            check(sorted(k for k in set(t) | set(ts) if t.get(k) != ts.get(k)) == ["outputDir", "proposalSeparationBar"], "tomllib keys")
            check(t["embeddingSliceDim"] == 768 and t["corpusDbPath"] == "intent_s1_build/m_af_g.db" and t["anchorFree"] is True and
                  t["pool"] == ts["pool"], "slice / build DB / anchorFree / pool unchanged")
            check(sha256_file(os.path.join(td, OUT_REL, BAR_FILE)) in nb.decode(), "the header names the bar file sha256")
            with contextlib.redirect_stdout(io.StringIO()):
                check(write_config(td) == p and open(p, "rb").read() == nb, "an identical re-write is left alone")
                check(check_config(td) == 0, "check_config passes")
            open(p, "wb").write(nb.replace(b"0.012500", b"0.012501"))
            refused(lambda: check_config(td), "differs from the regenerated")
            refused(lambda: write_config(td), "write-once")
            open(os.path.join(td, SRC_CONFIG_REL), "ab").write(b"\n# foreign\n")
            refused(lambda: regen_config(td), "not blob")
            refused(lambda: check_two_changes(src_toml, src_toml.replace(b"minClusterSize        = 55", b"minClusterSize        = 56")), "exactly outputDir")

        if "ST-VERD" in sel:
            def R_of(L, D, lo90, hi90, eq, loss, gain, verdict, bar_g=0.012):
                return {"L": L, "bar_g": bar_g, "T-C1": {"D": D, "lo90": lo90, "hi90": hi90, "eq": eq, "loss": loss, "gain": gain, "verdict": verdict}}
            v = verdict_lines(R_of(11, -0.003, -0.007, 0.001, True, False, False, "EQUIVALENT"))
            check(v[0] == "GO1 (DECIDING; S1's T-C1 rule verbatim): EQUIVALENT", "GO1 EQUIVALENT line")
            check(v[1].endswith("L = 11 -> SCOREABLE"), "scoreable at 11")
            check(v[2] == "F-GO does not fire (L = 11 > 10; no LOSS flag): " + SENT_FGO_NOT, "F-GO not fired sentence")
            v = verdict_lines(R_of(10, -0.003, -0.007, 0.001, True, False, False, "EQUIVALENT"))
            check("(degenerate tree)" not in v[0] and v[1].endswith("L = 10 -> SCOREABLE"), "L = 10 is not degenerate (Support f)")
            check(v[2].startswith("F-GO FIRES (G-AF built 10 <= 10 leaves under its own bar): ") and v[2].endswith(SENT_FGO_FIRED), "L = 10 fires F-GO")
            v = verdict_lines(R_of(9, -0.003, -0.007, 0.001, False, False, False, "UNDETERMINED"))
            check(v[0].endswith("UNDETERMINED (degenerate tree)") and "GO1 read but marked \"degenerate tree\"" in v[1], "L = 9 degenerate")
            v = verdict_lines(R_of(40, -0.04, -0.05, -0.03, False, True, False, "LOSS"))
            check(v[2] == "F-GO FIRES (GO1 flags LOSS (LOSS)): " + SENT_FGO_FIRED, "LOSS fires F-GO")
            v = verdict_lines(R_of(40, -0.012, -0.015, -0.009, True, True, False, "EQUIVALENT / LOSS-FLAGGED"))
            check(v[0].endswith("EQUIVALENT / LOSS-FLAGGED") and v[2].startswith("F-GO FIRES (GO1 flags LOSS"), "joined LOSS-FLAGGED fires F-GO")
            v = verdict_lines(R_of(4, -0.04, -0.05, -0.03, False, True, False, "LOSS"))
            check(v[2].startswith("F-GO FIRES (G-AF built 4 <= 10 leaves under its own bar and GO1 flags LOSS (LOSS))"), "both clauses")
            v = verdict_lines(R_of(40, 0.03, 0.02, 0.04, False, False, True, "GAIN"))
            check(v[0].endswith(": GAIN") and v[2].startswith("F-GO does not fire"), "GAIN branch")
            p = prediction_lines(R_of(15, -0.025, 0, 0, True, False, False, "EQUIVALENT", bar_g=0.007))
            check(p[0] == "P1 bar_g 0.007000 in [0.007, 0.02]: HELD" and p[1] == "P2 G-AF leaves 15 in [15, 90]: HELD" and
                  p[2] == "P3 D1 -0.02500 in [-0.025, 0.015]: HELD", "bands inclusive at the lower edge: %s" % p[:3])
            check(p[3] == "P3 GO1 EQUIVALENT p 0.50: event occurred, Brier 0.2500" and p[4] == "P3 GO1 LOSS p 0.15: event did not occur, Brier 0.0225", "Briers: %s" % p[3:])
            p = prediction_lines(R_of(91, 0.0151, 0, 0, False, True, False, "LOSS", bar_g=0.0201))
            check([x.split(": ")[-1] for x in p[:3]] == ["MISSED", "MISSED", "MISSED"] and p[4].endswith("event occurred, Brier 0.7225"), "bands exclusive above: %s" % p)
            p = prediction_lines(R_of(90, 0.015, 0, 0, False, False, False, "UNDETERMINED", bar_g=0.020))
            check([x.split(": ")[-1] for x in p[:3]] == ["HELD", "HELD", "HELD"], "bands inclusive at the upper edge")

        if "ST-E2E" in sel:
            td = fresh_root(); roots.append(td)
            der, pins = _cal_fixture(td, rng)
            with contextlib.redirect_stdout(io.StringIO()):
                calibrate(td, write=True, derived=der, pins=pins)
            W, C, side, X, have = _e2e_world(td)
            tr = np.nonzero(C.kept & ~C.oos & (side == SS.TRAIN) & have)[0]
            ev = np.nonzero(C.kept & ~C.oos & (side == SS.EVAL) & have)[0]

            def go(name, mus, write=True):
                T, rd = _e2e_case(td, name, W, C, side, X, mus, td)
                inj = lambda _r, _s: {"W": W, "T": T, "sid": "sid_" + name, "rd": rd, "census": {}, "pins": {}}
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    R, lines, path = run(td, write=write, out_dir=os.path.join(td, "out_" + name), skip_heavy=True, loader=inj, slice_g=16)
                return T, R, lines, path, buf.getvalue()

            # (a) a good tree: k-means centroids at L = 12 (seed 7, not one of the comparator's seeds)
            mus = S0.skmeans(X[tr], 12, 7)
            T, R, lines, path, txt = go("good", mus)
            truth = S0.codes(C.fine[ev])
            n_tree = S0.nmi(truth, np.argmax(X[ev] @ T["leaf_mu"].T, axis=1))
            n_km = [S0.nmi(truth, S0.assign(X[ev], S0.skmeans(X[tr], 12, s))) for s in range(20)]
            D = n_tree - float(np.mean(n_km))
            r1 = R["T-C1"]
            check(abs(r1["D"] - D) < 1e-12 and R["L"] == 12, "D1 = an independent NMI computation (%r vs %r)" % (r1["D"], D))
            outc = open(path, encoding="utf-8").read().split("\n")
            gl = [i for i, l in enumerate(outc) if l.startswith("GATE CONSTANTS")]
            el = [i for i, l in enumerate(outc) if l.startswith(("T-C1 / GO1", "GO1 ", "DESCRIPTIVE T-C7", "DESCRIPTIVE T-C9"))]
            check(len(gl) == 1 and el and gl[0] < min(el), "the GATE constants line precedes every EVAL line")
            t1 = [l for l in outc if l.startswith("T-C1 / GO1")][0]
            check(("= %+.5f;" % D) in t1, "the printed D1 by value")
            lo90, hi90 = D - IS1.Z90 * r1["se_total"], D + IS1.Z90 * r1["se_total"]
            eq = bool(r1["delta"] > 0 and -r1["delta"] < lo90 and hi90 < r1["delta"])
            loss = bool(D < -r1["bar"] and r1["hi"] < 0)
            gain = bool(D > r1["bar"] and r1["lo"] > 0)
            word = " / ".join((["EQUIVALENT"] if eq else []) + (["LOSS-FLAGGED" if eq else "LOSS"] if loss else []) +
                              (["GAIN-FLAGGED" if eq else "GAIN"] if gain else [])) or "UNDETERMINED"
            check([l for l in outc if l.startswith("GO1 ")][0] == "GO1 (DECIDING; S1's T-C1 rule verbatim): " + word, "the verdict word = the rule here (%s)" % word)
            check(any(l.startswith("F-GO") for l in outc) and any(l.startswith("P3 GO1 LOSS") for l in outc), "F-GO and P3 lines printed")
            check(("F-GO FIRES" in txt) == bool(loss), "F-GO fires iff LOSS at L = 12")
            check("P1 bar_g 0.012500 in [0.007, 0.02]: HELD" in outc and "P2 G-AF leaves 12 in [15, 90]: MISSED" in outc, "P1 / P2 by value")
            check(any(l.startswith("DESCRIPTIVE leaves: G-AF 12 vs M-AF-g 4") and "M-AF 84" in l for l in outc), "descriptive leaves")
            check(any(l.startswith("TRAIN-ONLY AUDIT") and "EVAL" not in l and "G-AF GATE" in l for l in outc), "TRAIN-ONLY audit printed, no EVAL fit")
            refused(lambda: run(td, out_dir=os.path.join(td, "out_good"), skip_heavy=True, loader=lambda *_: None, slice_g=16), "write-once")
            # (b) a random tree at L = 12: LOSS and F-GO
            mus_r = S0.unit(np.random.default_rng(99).normal(size=(12, 16)))
            T, R, lines, path, txt = go("random", mus_r)
            check(R["T-C1"]["loss"] and "F-GO FIRES (GO1 flags LOSS" in txt, "a random tree fires LOSS and F-GO (D %r)" % R["T-C1"]["D"])
            # (c) a 4-leaf tree: degenerate, F-GO on the leaf clause
            T, R, lines, path, txt = go("four", S0.skmeans(X[tr], 4, 7))
            check("(degenerate tree)" in txt and "F-GO FIRES (G-AF built 4 <= 10 leaves" in txt, "4 leaves: degenerate and F-GO")
            # (d) dry run: no EVAL statistic, nothing written
            IS1.STATE["gate_frozen"] = False
            T, R, lines, path, txt = go("dry", mus, write=False)
            check(R is None and not os.path.exists(os.path.join(td, "out_dry")) and not IS1.STATE["gate_frozen"], "the dry run computes no EVAL statistic and writes nothing")
            # (e) a build config off the bar refuses
            T5, rd5 = _e2e_case(td, "offbar", W, C, side, X, mus, td)
            cp = os.path.join(rd5, "diagnostics", "config.toml")
            open(cp, "wb").write(open(cp, "rb").read().replace(b"proposalSeparationBar = 0.012500", b"proposalSeparationBar = 0.025"))
            refused(lambda: run(td, out_dir=os.path.join(td, "out_offbar"), skip_heavy=True, slice_g=16,
                                loader=lambda *_: {"W": W, "T": T5, "sid": "s", "rd": rd5, "census": {}, "pins": {}}), "did not use bar_g")
            check(not os.path.exists(os.path.join(td, "out_offbar", OUTCOME)), "no outcome after a refusal")
            # (f) a slice off 768 refuses at the real slice
            refused(lambda: run(td, out_dir=os.path.join(td, "out_slice"), skip_heavy=True,
                                loader=lambda *_: {"W": W, "T": _e2e_case(td, "slice", W, C, side, X, mus, td)[0], "sid": "s",
                                                   "rd": _e2e_case(td, "slice", W, C, side, X, mus, td)[1], "census": {}, "pins": {}}), "slice 16 != 768")
    finally:
        for r in roots:
            shutil.rmtree(r, ignore_errors=True)
    if not quiet:
        print("%s SELFTEST OK: %d value checks (%s)" % (TAG, n_ok[0], ", ".join(c for c in SELFTEST_CASES if c in sel)))
    return 0


MUTANTS = (
    ("p95 rank floor-1 (284th)", "rank = min(max(int(math.ceil(0.95 * len(s))), 1), len(s))", "rank = min(max(int(math.ceil(0.95 * len(s))) - 1, 1), len(s))", ("ST-CAL",)),
    ("p95 = max", "    return s[rank - 1]\n", "    return s[-1]\n", ("ST-CAL",)),
    ("bar ratio inverted", "bar_g = BAR_OF_RECORD * pg / pq", "bar_g = BAR_OF_RECORD * pq / pg", ("ST-CAL",)),
    ("deciding bar from the iso leg", "bar_g = BAR_OF_RECORD * pg / pq", "bar_g = BAR_OF_RECORD * iso[768] / iso[256]", ("ST-CAL",)),
    ("legs swapped", 'pq, pg = legs["qwen3_256"]["p95"], legs["gemma768"]["p95"]', 'pg, pq = legs["qwen3_256"]["p95"], legs["gemma768"]["p95"]', ("ST-CAL",)),
    ("reps not checked", '"reps": str(REG_REPS)}', '}', ("ST-CAL",)),
    ("sepBar not checked", '"sepBar": repr(BAR_OF_RECORD), "minClusterSize"', '"minClusterSize"', ("ST-CAL",)),
    ("emb pin not checked", 'if st.get("emb_sha256") != pins[spec["emb"]] or not pins[spec["emb"]]:', "if False:", ("ST-CAL",)),
    ("TRAIN set not checked", 'if st.get("train_text_set_sha256") != derived["text_sha"] or st.get("n_train") != str(derived["n"]):', "if False:", ("ST-CAL",)),
    ("table sha not checked", 'if st.get("build_table_sha256") != derived["table_sha"]:', "if False:", ("ST-CAL",)),
    ("printed p95 not checked", 'if q != float(st.get("p95", "nan")):', "if False:", ("ST-CAL",)),
    ("iso slice count not checked", "if len(xs) != REG_REPS:\n            refuse(\"iso leg", "if False:\n            refuse(\"iso leg", ("ST-CAL",)),
    ("non-positive p95 admitted", "if not (pq > 0 and pg > 0):", "if False:", ("ST-CAL",)),
    ("bar file lexists check off", "if write and os.path.lexists(bar_path):", "if False:", ("ST-CAL",)),
    ("calibrate dry run writes", "    if write:\n        os.makedirs(root, exist_ok=True)", "    if True:\n        os.makedirs(root, exist_ok=True)", ("ST-CAL",)),
    ("TOML bar 4 dp", 'bar_toml = "%.6f" % bar_g', 'bar_toml = "%.4f" % bar_g', ("ST-CAL",)),
    ("identity uses 3 dp", "round(iso[dim], 4) == RECORD_ISO[dim]", "round(iso[dim], 3) == RECORD_ISO[dim]", ("ST-CAL",)),
    ("config keeps the old outputDir", "body = [OUTDIR_NEW if l == OUTDIR_OLD else", "body = [OUTDIR_OLD if l == OUTDIR_OLD else", ("ST-CFG",)),
    ("config keeps the old bar", '("proposalSeparationBar = %s" % bar_toml if l == BAR_OLD else l)', "(l)", ("ST-CFG",)),
    ("two-change check off", 'if len(diff) != 2 or kd != ["outputDir", "proposalSeparationBar"]:', "if False:", ("ST-CFG",)),
    ("source TOML blob not checked", "if not os.path.isfile(src) or blob(src) != SRC_CONFIG_BLOB:", "if not os.path.isfile(src):", ("ST-CFG",)),
    ("config overwrite allowed", 'refuse("%s exists with different bytes (write-once)" % p)', "pass", ("ST-CFG",)),
    ("check_config ignores bytes", 'if not os.path.isfile(p) or open(p, "rb").read().replace(b"\\r\\n", b"\\n") != nb:', "if not os.path.isfile(p):", ("ST-CFG",)),
    ("degenerate at <= 10", "degenerate = bool(L < DEGENERATE_BELOW)", "degenerate = bool(L <= DEGENERATE_BELOW)", ("ST-VERD",)),
    ("F-GO leaf clause < 10", "leaf_clause = bool(L <= FGO_LEAVES_AT_MOST)", "leaf_clause = bool(L < FGO_LEAVES_AT_MOST)", ("ST-VERD",)),
    ("F-GO ignores LOSS", 'loss_clause = bool(r1["loss"])', "loss_clause = False", ("ST-VERD",)),
    ("F-GO only on plain LOSS", 'loss_clause = bool(r1["loss"])', 'loss_clause = r1["verdict"] == "LOSS"', ("ST-VERD",)),
    ("bands exclusive", "return bool(np.isfinite(x) and lo <= x <= hi)", "return bool(np.isfinite(x) and lo < x < hi)", ("ST-VERD",)),
    ("Brier on the wrong event", '(("EQUIVALENT", "eq"), ("LOSS", "loss"))', '(("EQUIVALENT", "loss"), ("LOSS", "eq"))', ("ST-VERD",)),
    ("P1 on the TOML bar", 'R["bar_g"], "bar_g %.6f"', 'round(R["bar_g"], 2), "bar_g %.6f"', ("ST-VERD",)),
    ("T-C1 on a tree-only NMI", "    r1 = IS1.t_c1(A)\n", "    r1 = IS1.t_c1(A)\n    r1 = dict(r1, D=r1[\"n_tree\"])\n", ("ST-E2E",)),
    ("GATE constants after EVAL", '    L.extend(support_lines(R))\n    L.extend(verdict_lines(R))\n',
     '    L.extend(support_lines(R))\n    L.extend(verdict_lines(R))\n    L.append(L.pop([i for i, x in enumerate(L) if x.startswith(\"GATE CONSTANTS\")][0]))\n', ("ST-E2E",)),
    ("outcome lexists check off", "    if write and os.path.lexists(path):\n", "    if False:\n", ("ST-E2E",)),
    ("build config not checked", "    check_build_config(inp[\"rd\"], root)\n", "", ("ST-E2E",)),
    ("slice not checked", "    if T[\"d\"] != slice_g:\n", "    if False:\n", ("ST-E2E",)),
    ("dry run computes GO1", "    if not write:\n        IS1.STATE", "    if False:\n        IS1.STATE", ("ST-E2E",)),
    ("L from the wrong source", '"L": A["L"]', '"L": A["L"] + 1', ("ST-E2E",)),
    ("need_km off", "A = IS1.phase_gate(A, False, diag_path=diag_path, need_km=True)", "A = IS1.phase_gate(A, False, diag_path=diag_path, need_km=False)", ("ST-E2E",)),
)


def run_mutants():
    src = open(os.path.abspath(__file__), encoding="utf-8").read().replace("\r\n", "\n")
    cut, end = src.index("\nMUTANTS = ("), src.index("\n\ndef run_mutants")
    head = src[:cut] + src[end:]
    killed = 0
    for name, old, new, tests in MUTANTS:
        if head.count(old) != 1:
            raise SystemExit("%s mutant %r: target occurs %d times" % (TAG, name, head.count(old)))
        ns = {"__name__": "gob_mutant", "__file__": os.path.abspath(__file__)}
        try:
            exec(compile(head.replace(old, new), "<mutant>", "exec"), ns)
            with contextlib.redirect_stdout(io.StringIO()):
                ns["selftest"](only=set(tests), quiet=True)
            res = "SURVIVED"
        except BaseException as ex:            # noqa: B902
            kind = "assert" if isinstance(ex, AssertionError) else ("refusal" if isinstance(ex, SystemExit) else "CRASH " + type(ex).__name__)
            res = "KILLED(%s) | %s" % (kind, (str(ex).splitlines() or [""])[0][:100])
        killed += res.startswith("KILLED")
        print("  %-40s %s" % (name, res))
    print("MUTANTS: %d of %d KILLED" % (killed, len(MUTANTS)))
    return 0 if killed == len(MUTANTS) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="GEMMA-OWN-BAR (zero calls)")
    g = ap.add_mutually_exclusive_group(required=True)
    for f in ("--selftest", "--mutants", "--calibrate-plan", "--calibrate", "--write-config", "--check-config", "--launch-plan", "--run"):
        g.add_argument(f, action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--snapshot-db", default=None)
    ap.add_argument("--s1-data-root", default=None, help="--run: re-read M-AF-g / M-AF leaf counts from S1's run root (descriptive)")
    a = ap.parse_args(argv)
    if a.selftest:
        print(SELFTEST_DOC)
        return selftest()
    if a.mutants:
        return run_mutants()
    if a.calibrate_plan:
        return calibrate_plan()
    if a.launch_plan:
        return launch_plan()
    if a.calibrate:
        check_code_pins()
        calibrate(write=not a.dry_run)
        return 0
    if a.write_config:
        write_config(write=not a.dry_run)
        return 0
    if a.check_config:
        return check_config()
    run(snap_db=a.snapshot_db, write=not a.dry_run, s1_root=a.s1_data_root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
