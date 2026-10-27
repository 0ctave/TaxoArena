"""Mutation check for tools/ops/wal_checkpoint.py (re-runnable; temp dirs only, no DB of record opened).

    python tools/ops/wal_checkpoint_mutants.py

Each mutant is one (or two) exact text replacements in a scratch copy of the sibling wal_checkpoint.py
(every anchor must occur exactly once, else NOT-APPLIED); the copy's `--selftest` is run and the mutant
is KILLED iff it exits non-zero. Exit 0 iff every mutant applied and was killed.
M* = builder's set, R* = review docs/reviews/READY_wal_checkpoint.md (R1-R8), N* = added with C1/C2.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

TARGET = Path(__file__).resolve().with_name("wal_checkpoint.py")

MUTANTS = [
    ("M1 allow-list bypass", "if not (name in ALLOWED_FIXED or ALLOWED_PATTERN.fullmatch(name)):", "if False:"),
    ("M2 match instead of fullmatch", "ALLOWED_PATTERN.fullmatch(name)", "ALLOWED_PATTERN.match(name)"),
    ("M3 bare-name check dropped",
     'if not name or name != os.path.basename(name) or "/" in name or "\\\\" in name or name in (".", ".."):',
     "if not name:"),
    ("M4 java.exe not forbidden", 'FORBIDDEN_PROCS = ("java.exe", "javaw.exe")', 'FORBIDDEN_PROCS = ("javaw.exe",)'),
    ("M5 gradle not forbidden", 'or n.lower().startswith("gradle")', ""),
    ("M6 empty process list accepted", "if not names:\n        raise Refused", "if False:\n        raise Refused"),
    ("M7 probe share mode RW", "0x80000000 | 0x40000000, 0, None, 3", "0x80000000 | 0x40000000, 3, None, 3"),
    ("M8 first probe skipped", '        probe(db)\n        stage = "disk"', '        stage = "disk"'),
    ("M9 busy flag ignored", "res[0] == 0 and res[1] == res[2]", "res[1] == res[2]"),
    ("M10 log==ckpt ignored", "res[0] == 0 and res[1] == res[2]", "res[0] == 0"),
    ("M11 copy compare dropped", "if not (src_sha == dst_sha == src_sha2):", "if False:"),
    ("M12 AFTER diff ignored", "        if changed:\n", "        if False:\n"),
    ("M13 AFTER = BEFORE", "after = hashes_immutable(db)", "after = dict(before)"),
    ("M14 WAL not applied in BEFORE", "bwal if bwal.exists() else None, bdir", "None, bdir"),
    ("M15 no-op checkpoint", 'res = tuple(con.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone())',
     "res = (0, 0, 0)"),
    ("M16 dry-run checkpoints", "        if dry_run:\n", "        if False:\n"),
    ("M17 existing backup dir accepted", "if target.exists():\n            raise", "if False:\n            raise"),
    ("M18 post-close -wal check dropped", "if wal_after not in (None, 0):", "if False:"),
    ("M19 WITHOUT ROWID pk ordered by cid", "key=lambda r: r[5])", "key=lambda r: r[0])"),
    ("M20 hash first row only", "            n += 1\n", "            n += 1\n            break\n"),
    ("M21 non-wal accepted", 'if str(mode).lower() != "wal":', "if False:"),
    ("M22 -wal not backed up", "for f in (db, wal, shm):", "for f in (db, shm):"),
    ("M23 in-connection -wal check dropped", "if wal_open not in (None, 0):", "if False:"),
    ("M23b in-conn check dropped + no-op ckpt", [("if wal_open not in (None, 0):", "if False:"),
     ('res = tuple(con.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone())', "res = (0, 0, 0)")], None),
    ("M24 PASSIVE instead of TRUNCATE", 'wal_checkpoint(TRUNCATE)").fetchone())', 'wal_checkpoint(PASSIVE)").fetchone())'),
    ("M25 schema not hashed", '    out = {"__schema__": {"rows": len(master), "sha256": sh.hexdigest()}}',
     "    out = {}"),
    ("R1 symlink refusal dropped", "if p.is_symlink():", "if False:"),
    ("R2 outside-root refusal dropped", "if pr.parent != root_r:", "if False:"),
    ("R3 second probe dropped", '        check_processes(procs())\n        probe(db)\n        stage = "checkpoint"',
     '        check_processes(procs())\n        stage = "checkpoint"'),
    ("R4 second process check dropped", '        stage = "recheck"\n        check_processes(procs())\n',
     '        stage = "recheck"\n'),
    ("R5 source re-hash dropped", "src_sha == dst_sha == src_sha2", "src_sha == dst_sha"),
    ("R6 disk check dropped", "if free < need:", "if False:"),
    ("R7 tasklist rc ignored", 'if out.returncode != 0:\n            raise Refused(f"tasklist',
     'if False:\n            raise Refused(f"tasklist'),
    ("R8 javaw.exe not forbidden", 'FORBIDDEN_PROCS = ("java.exe", "javaw.exe")', 'FORBIDDEN_PROCS = ("java.exe",)'),
    ("N1 hard-link check dropped", "if f.exists() and os.stat(f).st_nlink > 1:", "if False:"),
    ("N2 only Refused caught (tracebacks)", "    except Exception as e:  # noqa", "    except Refused as e:  # noqa"),
    ("N3 checkpoint-attempted flag never set", "            checkpointed = True\n", ""),
    ("N4 backup state always 'none'", 'kept = f"backup kept at {bdir}" if bdir is not None else "no backup written"',
     'kept = "no backup written"'),
    ("N5 stage label not advanced", '        stage = "before-hash"\n', ""),
    ("N6 rowid tables ordered by nothing", '            order = "_rowid_"\n        except', '            order = "1"\n        except'),
]


def main() -> int:
    src = TARGET.read_text(encoding="utf-8")
    rows, bad = [], 0
    with tempfile.TemporaryDirectory(prefix="walckpt_mut_") as td:
        m = Path(td) / "wal_checkpoint.py"
        for label, old, new in MUTANTS:
            pairs = old if isinstance(old, list) else [(old, new)]
            if any(src.count(o) != 1 for o, _ in pairs):
                rows.append((label, "NOT-APPLIED")); bad += 1
                continue
            t = src
            for o, n in pairs:
                t = t.replace(o, n, 1)
            m.write_text(t, encoding="utf-8", newline="\n")
            p = subprocess.run([sys.executable, str(m), "--selftest"], capture_output=True, text=True)
            fl = [l.strip()[5:60] for l in p.stdout.splitlines() if l.strip().startswith("FAIL")]
            if p.returncode == 0:
                rows.append((label, "SURVIVED")); bad += 1
            else:
                rows.append((label, "killed by " + (fl[0] if fl else f"rc {p.returncode} (crash)")))
    for label, verdict in rows:
        print(f"{label:42s} {verdict}")
    print(f"[wal-ckpt-mutants] {len(rows) - bad}/{len(rows)} killed")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
