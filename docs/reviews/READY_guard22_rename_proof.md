# READY-WITH-CONDITIONS: GUARD-22-RENAME-PROOF (adversarial-reviewer, 2026-09-23, zero calls)

Registration: `docs/judge_v2_program.md` L12599-L12708 (commit 8b4075b); record `docs/agents/results/GUARD-22-RENAME-PROOF.json`.
Change under proof: branch `guard22-rename` at 46d2f0f986d4412b09a47a18aaf109bb190f25b8, one file,
`src/test/kotlin/taxonomy/SeparationNullBySizeTest.kt` (called F below), blob c0d891213e777b0b8746f3f60f7375becb548fa2 -> 0b6e176fb9e6c45f8a5f655e4c85bcad44ef274b.
The reviewer ran NO Gradle, NO JVM and NO leg, and did not touch the main checkout's copy of F. At review time, `git hash-object F` returned c0d89121 and `git status --porcelain F | wc -l` returned 0.

VERDICT: **READY-WITH-CONDITIONS** for the two legs. Use the procedure, command lines and refusal conditions below exactly as written, and satisfy go conditions G1-G6.
A run that departs from them is not the registered proof.

## 1. Per-claim table

| # | claim | status | command / evidence | got vs claimed |
|---|---|---|---|---|
| 1 | branch = 46d2f0f and it changes one file | CONFIRMED | `git rev-parse guard22-rename`; `git diff --name-only 46d2f0f^ 46d2f0f` | 46d2f0f986d4...; 1 file (F) |
| 2 | 36 insertions / 36 deletions | CONFIRMED | `git diff -U0 HEAD guard22-rename -- F` gives 72 +/- lines; line-by-line comparison of the two blobs | 36 changed lines at the same positions (L1390-L1942); both blobs have 1989 lines when split on LF |
| 3 | blob c0d89121 at HEAD -> 0b6e176f on the branch | CONFIRMED | `git rev-parse HEAD:F guard22-rename:F`; `git hash-object F` | c0d891213e77... / 0b6e176fb9e6...; working tree c0d89121 |
| 4 | LF sha16 6322154dda0ef4c7 -> a87a6b37319c5ca5; CRLF 35054ef65ef7b221 -> fd5fbaa1abccd4b4 | CONFIRMED | sha256 of `git cat-file blob` (LF) and of its LF->CRLF rendering; the working-tree F (autocrlf=true, 1988 CR in 1988 lines) has sha16 35054ef65ef7b221 | all four match to the digit |
| 5 | the inverse substitution reproduces HEAD byte for byte | CONFIRMED (re-derived) | python on the branch blob: replace `\b(anchor|site)(Reps|Mcs|Config|Splitter|Capture)\b` with `r` / `mcs` / `config` / `splitter` / `capture` respectively, then compare bytes with the HEAD blob | `inverse == HEAD: True`; both 111889 bytes. NOTE: the old reps local is `r`, not `reps`. An inverse that maps to `reps` returns False (111928 vs 111889 bytes) |
| 6 | the substitution is a bijection (no new name exists at HEAD, so nothing is captured or shadowed) | CONFIRMED | count `\b<new>\b` in the HEAD blob | 0 for all ten new names. Branch counts: anchorReps 6, anchorMcs 4, anchorConfig 6, anchorSplitter 2, anchorCapture 7, siteReps 7, siteMcs 5, siteConfig 9, siteSplitter 2, siteCapture 7 |
| 7 | neither arm still uses an old name (a missed rename would still compile) | CONFIRMED | `grep -nE '\b(r|mcs|config|splitter|capture)\b'` over branch L1378-L1575 and L1668-L1988 | 1 hit, in a comment ("mcs=30 exports"); 0 in code |
| 8 | the branch file compiles | UNDETERMINED (never executed) | `ls .claude/worktrees/guard22-rename/build/...`: no such file. Main `build/classes/kotlin/test/taxonomy/SeparationNullBySizeTest*.class`: `siteReps` occurs 0 times | nobody has compiled the change in either checkout -> D2, G2 |
| 9 | nothing between the branch base and HEAD changes the code the legs run | CONFIRMED | `git merge-base HEAD guard22-rename` = 3c2f4be; `git rev-parse 3c2f4be:F` = c0d89121; `git diff 3c2f4be HEAD --name-only -- build.gradle.kts src/ \| wc -l` = 0 | leg B = HEAD's tree plus the one branch file, so only one thing varies |
| 10 | arm flags: snapshot, sliceDim 512, dropTop 0, whiten false, no sepBar | CONFIRMED | `tools/chains/anchor_free_cert.sh` L43; `anchor_free_cert_arm4.sh` L15 (`sitenull bareq512 512 0 ""`); `grep -o "Snapshot ID: [^ ]*" experiment_results/anchorfree/af_bareq512.build.out` | 20260917_161817_Headless_Run_Auto_ge. The CSV of record carries that id on 87/87 rows. The snapshot row is in `snapshots.db` (1 row, table snapshots), not in snapshots_frozen.db |
| 11 | `-PnullReps` is a Gradle property and `-DnullReps` is ignored | CONFIRMED | `build.gradle.kts` L213 `systemProperty("nullReps", providers.gradleProperty("nullReps").getOrElse("300"))`; test L383 `reps(default) = System.getProperty("nullReps")?.toIntOrNull() ?: default` | a `-DnullReps` run would silently use 300 reps |
| 12 | the default 6g heap is used and the guard admits the arm | CONFIRMED (arithmetic) | L202: `siteNullHeap` absent -> "6g". Guard peak = live * n * (55*dim/10 + 384) * 8, with live = min(24, nproc 24) = 24 and n_max = 8133 (CSV of record) | 4.997 GB, printed as 5.00 GB, against a budget of about 5.80 GB. The same at reps 24 and 300, because live is capped by the core count |
| 13 | "97 sites" (registration P3 "(point 7)"; JSON C1 denominator) | REFUTED | `wc -l experiment_results/anchorfree/site_null_af_bareq512_s42.csv` = 88 (87 rows) | the arm has 87 sites. 97 belongs to TOPIC-PARTITION-20NG T1b (20NG, snapshot 20260923_043423, n_max 11845), a different object whose name also contains "af_bareq512_s42" -> D1 |
| 14 | the P3 band of [4, 12] min is plausible | CONFIRMED (estimate) | arm-4 run: .out created 16:18:46, CSV written 17:27:03, so 68.3 min at 300 reps; scaled by 24/300 | about 5.5 min plus Gradle and JVM start-up |
| 15 | the engine-coder's switch `git checkout guard22-rename -- F` is safe | REFUTED | git semantics: `checkout <tree> -- <path>` writes the INDEX as well as the working tree | it can collide with other agents in the shared index -> the corrected switch is in section 3 |
| 16 | the coordinator's between-legs check "`git diff --cached --name-only` still empty" | PARTLY | a whole-index check blocks whenever another agent has legitimately staged something, and it does not show F's own index entry | narrowed to F: its index blob plus a per-path cached diff (section 3) |
| 17 | the withinNull arm cannot run under `:siteNull` | CONFIRMED | build.gradle.kts L222 `filter { includeTestsMatching("*SeparationNullBySizeTest*siteNull*") }` | the task filter excludes it. Never invoke `test` or `withinNull` |
| 18 | the CSV bytes depend only on the code: no timestamp, no wall time, fixed row order | CONFIRMED (reading) | writer L1925-L1943: a header, then fields taken from the rows. Sites sorted by (depth, -n). Per-replicate seed = seedBase + siteId.hashCode()*2654435761 + rep*104729, which does not depend on reps. `awaitAll` preserves order | the record contains no A/A run -> D8 |

## 2. Defects

- D1 LOW (registration): P3 "(point 7) ... 97 sites" and the JSON C1 denominator "97 sites" describe the wrong object. The pinned snapshot has 87 sites (claim 13). Fix: a registrar bracket inserted into the record, so that P3 and C1 are read against 87. The criterion itself (a byte comparison) is unchanged.
- D2 MEDIUM (change): the branch file has never been compiled (claim 8). If leg B failed to compile, the falsifier would fire and the registered reading would be "the two arms are not independent", which would be false. Fix: G2, a compile-only pre-flight in the worktree that needs no DB.
- D3 HIGH (vacuity): identical bytes alone cannot distinguish "leg B ran the renamed code" from "leg B ran HEAD's classes". The second can happen through a stale compile, a build-cache hit, a missed file-system change, or another agent reverting F before the compile. C2 asks for the "blob sha actually compiled" but gives no way to establish it. Fix: the class-file discriminator in section 3. The renamed locals appear in the LocalVariableTable, and today HEAD's classes contain `siteReps` 0 times and `guardDim` once. The count must be 0 after leg A and greater than 0 after leg B. Refusal condition R9.
- D4 MEDIUM (procedure): `anchor_free_cert.sh` runs Gradle with `-q`, and the arm-4 log `experiment_results/anchorfree/sitenull_bareq512.out` is 0 bytes. Under `-q`, neither `[SITENULL-HEAP]`, `[SEPBAR]` nor the task outcome line is printed, so C2 cannot be HELD. Fix: drop `-q`, as `tools/chains/topic_partition.sh` L556 does.
- D5 MEDIUM (procedure): if Git Bash passes a POSIX path (`/tmp/...` or `/c/...`) as `-DoutCsv`, the Windows JVM resolves it on the current drive (Z:), not in the scratchpad. Fix: convert it with `cygpath -w`.
- D6 LOW (procedure): `gradle.properties` sets `org.gradle.caching=true`, and this review does not rely on `outputs.upToDateWhen { false }` to prevent a FROM-CACHE result. Fix: `--no-build-cache` on both legs, fresh CSV paths, and R3.
- D7 LOW (procedure): the engine-coder's `git checkout guard22-rename -- F` stages F in the shared index (claim 15), and the coordinator's whole-index check is too broad (claim 16). Both are fixed in section 3.
- D8 MEDIUM (interpretation, not blocking): there is no A/A control, and all 24 concurrent coroutines share one `siteSplitter` and one `siteCapture`. A C1 failure is still recorded as FAILED: UNDETERMINED is not admissible, and this review does not reopen that. But the outcome must not describe a FAIL as "the rename changed the numbers" until an A/A pair (two leg-A runs) has been registered and run. The registration's own consequence ("the difference becomes the next registered object") is the path to that.
- D9 LOW (record): `GUARD-22-RENAME-PROOF.json` has `"ready": null`. The registrar fills it in with this file and its commit.

## 3. The switch-and-restore procedure and the two command lines

Run everything in Git Bash, in the MAIN checkout, by the run-operator, inside the rule-7 window of section 4.
`SCR` = the run-operator's scratchpad in POSIX form, with no spaces. Nothing below writes to `docs/`, `experiment_results/` or any DB.

### The two command lines (they differ only in `-DoutCsv` and the log name)

LEG A (F at HEAD, blob c0d89121):
```
./gradlew.bat siteNull --console=plain --offline --no-build-cache "-PnullReps=24" "-DsnapshotId=20260917_161817_Headless_Run_Auto_ge" "-DsliceDim=512" "-DdropTop=0" "-Dwhiten=false" "-DoutCsv=$(cygpath -w "$SCR/g22_legA.csv")" > "$SCR/g22_legA.out" 2>&1
```
LEG B (F at 46d2f0f, blob 0b6e176f, working tree only):
```
./gradlew.bat siteNull --console=plain --offline --no-build-cache "-PnullReps=24" "-DsnapshotId=20260917_161817_Headless_Run_Auto_ge" "-DsliceDim=512" "-DdropTop=0" "-Dwhiten=false" "-DoutCsv=$(cygpath -w "$SCR/g22_legB.csv")" > "$SCR/g22_legB.out" 2>&1
```
Deliberately absent: `-q`, `-DsepBar`, `-DsiteNullHeap`, `-DnullReps`, and any task other than `siteNull`.

### Switch and restore
- Leg A runs with F at HEAD. Before it, P0 checks: HEAD:F, the working-tree F and F's index entry are all c0d89121; F is not modified; the branch is at 46d2f0f and its F is 0b6e176f; `src/` and the build files are clean.
- Switch (working tree only): `git restore --source=guard22-rename --worktree -- src/test/kotlin/taxonomy/SeparationNullBySizeTest.kt`. Then verify: `git hash-object F` == 0b6e176fb9e6c45f8a5f655e4c85bcad44ef274b; CRLF sha16 == fd5fbaa1abccd4b4; `git ls-files -s -- F` still shows c0d89121; `git diff --cached --name-only -- F | wc -l` == 0. The whole-index check is replaced by these per-path checks, because another agent may legitimately stage its own paths.
- Leg B.
- Restore: `git restore --source=HEAD --worktree -- src/test/kotlin/taxonomy/SeparationNullBySizeTest.kt`. Then verify: `git hash-object F` == c0d891213e777b0b8746f3f60f7375becb548fa2; `git status --porcelain -- F` is empty; the index blob is c0d89121. Print `git status --short`. The restore runs EVEN IF leg B fails or is interrupted: it is on an EXIT trap that is set before the switch.
- Never use `git checkout <branch> -- F`, `git add`, `git stash` or `git reset` on F.

### The sequence as a script (reviewer-authored; `bash -n` passes; its check and compare path was run on fabricated logs, where it passed a sound pair and flagged a broken leg B (exit 1, discriminator 0, 89 lines, cmp differs))
Save the script below as `$SCR/g22_proof.sh`: 111 lines, git blob 1d8083ccd26546ba2067dce5af8e993f589299ca, sha16 e42f3e75a7e0a18c as saved by the reviewer. Run it in three phases, with the section-4 probe between phases:
`SCR=<scratchpad> bash "$SCR/g22_proof.sh" A` -> probe -> `... B` -> probe -> `... compare`.

```bash
#!/usr/bin/env bash
# GUARD-22-RENAME-PROOF, two :siteNull legs. Zero calls. Registration docs/judge_v2_program.md L12599-L12708 (8b4075b).
# Usage (Git Bash, main checkout, inside the rule-7 window):
#   SCR=<run-operator scratchpad, POSIX form, no spaces> bash g22_proof.sh A        # leg A, file at HEAD
#   (W1/W2/W4 probe)
#   SCR=... bash g22_proof.sh B        # switch (worktree only) -> leg B -> restore (always, EXIT trap)
#   (W1/W2 probe, W5)
#   SCR=... bash g22_proof.sh compare  # per-leg checks again, sha256, cmp
set -u
REPO=/z/FAC/TUBerlin/THESIS/TaxoArena
F=src/test/kotlin/taxonomy/SeparationNullBySizeTest.kt
BLOB_A=c0d891213e777b0b8746f3f60f7375becb548fa2
BLOB_B=0b6e176fb9e6c45f8a5f655e4c85bcad44ef274b
COMMIT_B=46d2f0f986d4412b09a47a18aaf109bb190f25b8
CLS=build/classes/kotlin/test/taxonomy
XML=build/test-results/siteNull/TEST-taxonomy.SeparationNullBySizeTest.xml
: "${SCR:?set SCR to the run-operator scratchpad (POSIX form, no spaces)}"
cd "$REPO" || exit 90
die()    { echo "REFUSED: $*"; exit 91; }
sha16()  { sha256sum "$1" | cut -c1-16; }
disc()   { cat $CLS/SeparationNullBySizeTest*.class | grep -a -o -E 'siteReps|anchorReps|siteCapture|anchorCapture' | wc -l; }
sanity() { cat $CLS/SeparationNullBySizeTest*.class | grep -a -o 'guardDim' | wc -l; }

p0() {
  [ "$(git rev-parse HEAD:$F)" = "$BLOB_A" ]                    || die "HEAD:F != c0d89121"
  [ "$(git hash-object "$F")" = "$BLOB_A" ]                     || die "working-tree F != c0d89121"
  [ "$(git status --porcelain -- "$F" | wc -l)" = 0 ]           || die "F modified in the working tree"
  [ "$(git ls-files -s -- "$F" | cut -d' ' -f2)" = "$BLOB_A" ]  || die "F index entry != c0d89121"
  [ "$(git rev-parse guard22-rename)" = "$COMMIT_B" ]           || die "branch moved off 46d2f0f"
  [ "$(git rev-parse guard22-rename:$F)" = "$BLOB_B" ]          || die "branch blob != 0b6e176f"
  [ "$(git status --porcelain -- src build.gradle.kts gradle.properties settings.gradle.kts | wc -l)" = 0 ] || die "src/ or build files dirty"
  echo "P0 OK HEAD=$(git rev-parse HEAD) HEAD:src=$(git rev-parse HEAD:src) yml16=$(sha16 config/application.yml) nproc=$(nproc)"
  git status --short
}

restore() {
  git restore --source=HEAD --worktree -- "$F"
  echo "RESTORE blob=$(git hash-object "$F") crlf16=$(sha16 "$F") porcelain=$(git status --porcelain -- "$F" | wc -l) index=$(git ls-files -s -- "$F" | cut -d' ' -f2) HEAD:F=$(git rev-parse HEAD:$F)"
  [ "$(git hash-object "$F")" = "$BLOB_A" ]           || echo "RESTORE FAILED: blob != c0d89121 (R13)"
  [ "$(git status --porcelain -- "$F" | wc -l)" = 0 ] || echo "RESTORE FAILED: porcelain non-empty (R13)"
  git status --short
}

# check <A|B>: count checks R2-R9 on one leg; exit status 0 iff all hold
check() {
  local L=$1 O="$SCR/g22_leg$1.out" C="$SCR/g22_leg$1.csv" X="$SCR/g22_leg$1.xml" bad=0 v
  t() { echo "  $3=$1 (must be $2)"; [ "$1" = "$2" ] || bad=1; }
  echo "== LEG $L checks"
  t "$(cat "$SCR/g22_leg$L.rc" 2>/dev/null)" 0 exit_code
  t "$(grep -c -x '> Task :siteNull' "$O")" 1 task_executed
  t "$(grep -c -F '[SITENULL-HEAP] REFUSING' "$O")" 0 heap_refusing
  t "$(grep -c -F '[SITENULL-HEAP] sliceDim=512 largest site n=8133 live=24 -> peak live 5.00 GB' "$O")" 1 heap_line
  grep -F '[SITENULL-HEAP] sliceDim=' "$O"
  t "$(grep -c -F '[SEPBAR] proposalSeparationBar=0.025 (-DsepBar absent -> default 0.025); sliceDim=512 dropTop=0 whiten=false reps=24' "$O")" 1 sepbar_line
  t "$(grep -c -F '87 accepted split sites, reps=24 per site per arm.' "$O")" 1 sites_line
  t "$(grep -c -F 'tests="1" skipped="0" failures="0" errors="0"' "$X" 2>/dev/null)" 1 xml_not_skipped
  if [ -f "$C" ]; then
    t "$(wc -l < "$C" | tr -d ' ')" 88 csv_lines
    t "$(awk -F, 'NR>1 && $NF=="24"' "$C" | wc -l | tr -d ' ')" 87 csv_rows_reps24
    echo "  csv=$(cygpath -w "$C") sha256=$(sha256sum "$C" | cut -d' ' -f1)"
  else echo "  csv=ABSENT"; bad=1; fi
  v=$(cat "$SCR/g22_leg$L.disc" 2>/dev/null)
  if [ "$L" = A ]; then t "$v" 0 discriminator_after_A; else [ "${v:-0}" -gt 0 ] && echo "  discriminator_after_B=$v (must be > 0)" || { echo "  discriminator_after_B=$v (must be > 0) FAIL"; bad=1; }; fi
  echo "  guardDim_sanity=$(cat "$SCR/g22_leg$L.sanity" 2>/dev/null) (must be >= 1)"
  echo "  wall_s=$(cat "$SCR/g22_leg$L.wall" 2>/dev/null)"
  return $bad
}

case "${1:-}" in
A)
  p0
  [ ! -e "$SCR/g22_legA.csv" ] && [ ! -e "$SCR/g22_legB.csv" ] || die "a leg CSV already exists"
  git rev-parse HEAD:src > "$SCR/g22_src_tree"; sha16 config/application.yml > "$SCR/g22_yml16"
  echo "LEG A blob=$(git hash-object "$F") lf16=$(git cat-file blob $BLOB_A | sha256sum | cut -c1-16) crlf16=$(sha16 "$F") commit=$(git rev-parse HEAD) nproc=$(nproc) heap=default(6g) reps=24 start=$(date -Iseconds)"
  T0=$(date +%s)
  ./gradlew.bat siteNull --console=plain --offline --no-build-cache "-PnullReps=24" "-DsnapshotId=20260917_161817_Headless_Run_Auto_ge" "-DsliceDim=512" "-DdropTop=0" "-Dwhiten=false" "-DoutCsv=$(cygpath -w "$SCR/g22_legA.csv")" > "$SCR/g22_legA.out" 2>&1; echo $? > "$SCR/g22_legA.rc"
  echo $(( $(date +%s) - T0 )) > "$SCR/g22_legA.wall"
  cp "$XML" "$SCR/g22_legA.xml" 2>/dev/null
  disc > "$SCR/g22_legA.disc"; sanity > "$SCR/g22_legA.sanity"
  check A && echo "LEG A SOUND: proceed to probe, then B" || echo "LEG A INSTRUMENT FAILURE (R0): do NOT run B; nothing is compared"
  ;;
B)
  p0
  check A > /dev/null || die "leg A not sound (R0)"
  [ ! -e "$SCR/g22_legB.csv" ] || die "leg B CSV already exists"
  trap restore EXIT
  git restore --source=guard22-rename --worktree -- "$F"
  [ "$(git hash-object "$F")" = "$BLOB_B" ]                     || die "switch: working-tree blob != 0b6e176f"
  [ "$(sha16 "$F")" = "fd5fbaa1abccd4b4" ]                      || die "switch: CRLF sha16 != fd5fbaa1abccd4b4"
  [ "$(git ls-files -s -- "$F" | cut -d' ' -f2)" = "$BLOB_A" ]  || die "switch: index entry moved"
  [ "$(git diff --cached --name-only -- "$F" | wc -l)" = 0 ]    || die "switch: F staged"
  echo "LEG B blob=$(git hash-object "$F") lf16=$(git cat-file blob $BLOB_B | sha256sum | cut -c1-16) crlf16=$(sha16 "$F") commit=$COMMIT_B(file) nproc=$(nproc) heap=default(6g) reps=24 start=$(date -Iseconds)"
  T0=$(date +%s)
  ./gradlew.bat siteNull --console=plain --offline --no-build-cache "-PnullReps=24" "-DsnapshotId=20260917_161817_Headless_Run_Auto_ge" "-DsliceDim=512" "-DdropTop=0" "-Dwhiten=false" "-DoutCsv=$(cygpath -w "$SCR/g22_legB.csv")" > "$SCR/g22_legB.out" 2>&1; echo $? > "$SCR/g22_legB.rc"
  echo $(( $(date +%s) - T0 )) > "$SCR/g22_legB.wall"
  cp "$XML" "$SCR/g22_legB.xml" 2>/dev/null
  disc > "$SCR/g22_legB.disc"; sanity > "$SCR/g22_legB.sanity"
  trap - EXIT
  restore
  [ "$(git rev-parse HEAD:src)" = "$(cat "$SCR/g22_src_tree")" ] || echo "WINDOW VIOLATION: HEAD:src moved during the window"
  [ "$(sha16 config/application.yml)" = "$(cat "$SCR/g22_yml16")" ] || echo "WINDOW VIOLATION: config/application.yml changed during the window"
  check B; echo "leg B check status=$?"
  ;;
compare)
  check A; echo "A status=$?"; check B; echo "B status=$?"
  echo "RESTORE-STATE blob=$(git hash-object "$F") porcelain=$(git status --porcelain -- "$F" | wc -l)"
  sha256sum "$SCR/g22_legA.csv" "$SCR/g22_legB.csv"
  cmp "$SCR/g22_legA.csv" "$SCR/g22_legB.csv" && echo "C1 BYTE-IDENTICAL" || echo "C1 DIFFER (falsifier R1)"
  ;;
*) echo "usage: SCR=... bash g22_proof.sh A|B|compare"; exit 2 ;;
esac
```

## 4. The rule-7 window: ruling on the precondition, and how to check it

RULING on "0 `tools/analysis/*.py` processes". The precondition is the RULE-7 NO-READERS guard of hygiene clause (2), which says "nothing else may read the pool or the caches while either leg runs, and a `python tools/analysis/...` invocation is a reader", together with clause (6). It is NOT a quiet-machine requirement. The one criterion, C1, is a byte comparison whose per-replicate seeds do not depend on timing. P3's wall-time symmetry is registered as "a NUISANCE readout with no bar". The phrase "a `python tools/analysis/...` invocation is a reader" is a conservative way of classifying scripts that open caches. A process that holds no handle on any DB the legs read does not violate what the rule is for. So the deciding test is the exclusive-open probe, not the process name.

The operator runs the following checks at three points: before leg A, before phase B (the switch), and after the restore, before `compare`.

W1. Exclusive-open probe in PowerShell. Every file must print FREE. Any HELD means refuse, and do not compare:
```
$repo='Z:\FAC\TUBerlin\THESIS\TaxoArena'
foreach($d in 'embeddings_cache.db','embeddings_cache.db-wal','embeddings_cache.db-shm','snapshots.db','snapshots.db-wal','snapshots.db-shm','snapshots_frozen.db'){ $p=Join-Path $repo $d; if(Test-Path $p){ try{ $s=[IO.File]::Open($p,'Open','Read','None'); $s.Close(); "FREE $d" } catch { "HELD $d" } } }
```
Never run the probe while a leg's JVM is running: an exclusive open at that moment would make the leg's own open fail.

W2. Process list with PIDs, printed at each of the three points:
```
Get-CimInstance Win32_Process | ? { $_.CommandLine -match 'tools[\\/](analysis|chains)|bootRun|TaxoArenaApplication|GradleWorkerMain|pool_guard' } | select ProcessId,Name,CommandLine | ft -auto | Out-String -Width 400
```
- ADMITTED: a `tools/analysis/*.py` process whose command line carries `--selftest`, provided W1 prints FREE for every file while it is running.
- REFUSED:
  - any other `tools/analysis/*.py` or `tools/chains/*` process;
  - any construction (`bootRun` / `TaxoArenaApplication`);
  - any Gradle test worker (`GradleWorkerMain`) that does not belong to the leg;
  - any `pool_guard.py`.
- A `--dry-run` is NOT admitted, because dry-runs open caches.

W3. Print the set of admitted PIDs at the start and end of each leg, next to that leg's wall time, and read P3 with it. If a CPU-heavy selftest ran during one leg and not the other, say so; do not argue it away.

W4. At least 12 GB of free physical memory before each leg: `(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB`. At review time: 63.1 GB total, 37.6 GB free. A leg uses a 6g JVM plus the 4g Gradle daemon.

W5. The orchestrator announces the window. No agent runs a git write that touches `src/` inside it (checkout, restore, stash, reset, add -A, commit -a). After the fact, phase B's `HEAD:src` and `config/application.yml` checks detect a breach.

If W1, W2 or W5 finds a breach at the post-restore point, do NOT make the comparison. Repeat the window from P0, with the old CSVs moved aside. This is a failed precondition, not a C1 outcome, so it never produces UNDETERMINED.

## 5. Refusal conditions

C1 is FAILED on any of R1, R10, R11 or R12. UNDETERMINED is NOT admissible.

Instrument refusals. These are count checks against each leg's own log, XML and CSV, and are done before the comparison (`check` in the script):
- R2: either leg's exit code is not 0.
- R3: the exact line `> Task :siteNull` does not occur exactly once in a log. This catches FROM-CACHE, UP-TO-DATE and FAILED.
- R4: any of the following:
  - either log has a `[SITENULL-HEAP] REFUSING` line;
  - the line `[SITENULL-HEAP] sliceDim=512 largest site n=8133 live=24 -> peak live 5.00 GB` does not occur exactly once;
  - the two legs' full `[SITENULL-HEAP]` lines differ, meaning the core count or heap was not the same.
- R5: the line `[SEPBAR] proposalSeparationBar=0.025 (-DsepBar absent -> default 0.025); sliceDim=512 dropTop=0 whiten=false reps=24` does not occur exactly once in a log. This catches `-DnullReps`, a stray `-DsepBar` and a wrong geometry.
- R6: `87 accepted split sites, reps=24 per site per arm.` does not occur exactly once in a log.
- R7, the arm was SKIPPED: the XML's `tests="1" skipped="0" failures="0" errors="0"` does not occur exactly once. Gradle exits 0 when the test is skipped by `assumeTrue` or when a worker dies, so the exit code alone does not show a skip.
- R8: the CSV does not have exactly 88 lines, or does not have exactly 87 rows whose trailing reps column is 24, or it existed before the leg ran.
- R9, VACUITY: the class-file discriminator (`siteReps|anchorReps|siteCapture|anchorCapture` in `build/classes/kotlin/test/taxonomy/SeparationNullBySizeTest*.class`) is not 0 after leg A, or is 0 after leg B, or the `guardDim` sanity count is 0.
- R13: after the restore, any of the following holds, which falsifies P4:
  - the blob is not c0d891213e777b0b8746f3f60f7375becb548fa2;
  - `git status --porcelain -- F` is not empty;
  - the index blob is not c0d89121.
  Report it, and restore by hand before doing anything else.

The registered falsifier (C1 FAILED):
- R1: ANY byte difference between `g22_legA.csv` and `g22_legB.csv`, tested with `cmp` on the bytes, with the sha256 of both printed. That covers a changed observed_sep, site_null_p50/p95, q_site, q_deflated, reach or accept %, cert_* flag or trunk_member, and also a changed row order, feasibility string or trailing reps column.
- R10: leg B wrote no CSV while leg A did.
- R11: either leg shows the arm SKIPPED (R7) or prints `[SITENULL-HEAP] REFUSING` (R4).
- R12: either leg exits non-zero (R2).

How to read the outcomes:
- R0 is the leg-A rule. If R2, R4 or R7 fires on LEG A, that is an instrument failure of the baseline:
  - phase B refuses (the script's `check A` gate), nothing is compared, and the window is repeated once the cause is fixed;
  - the falsifier's "leg B wrote no CSV while leg A did" presupposes a sound leg A.
- If R2, R4 or R7 fires on LEG B, the registered falsifier has fired (R11/R12). Record FAILED and print the cause, subject to D8.
- If R3, R5, R6, R8 or R9 fires on either leg, that leg was not the registered leg. The pair is void and is repeated from P0. These are procedure failures that the registration's falsifier does not name, so they cannot decide C1 either way.
- C2 is HELD iff all of the following are printed for both legs: every line the script prints, plus the P0 line and the RESTORE line.

## 6. Go conditions

- G1: Run exactly section 3, either with the script or with the same steps by hand. Use both command lines exactly as written, in the MAIN checkout, with `SCR` set.
- G2: Before the window, compile the branch file in the worktree, which needs no DB: `cd .claude/worktrees/guard22-rename && ./gradlew.bat compileTestKotlin --console=plain --offline` must end BUILD SUCCESSFUL (D2). If it fails, stop the proof and send it back to the engine-coder; that is not a C1 outcome. Do not copy any DB into the worktree.
- G3: Run section 4 at all three points. Make the comparison only after the post-restore probe is clean.
- G4: Use only `git restore --worktree` on F. Never `git checkout <branch> -- F`, `git add`, `git stash` or `git reset`.
- G5: Before the registrar writes the outcome, the reviewer recomputes C1 independently from the two scratchpad CSVs (sha256 plus a byte comparison). The three on-pass brackets are written only after that.
- G6: The registrar records D1 (87 sites, not 97) by insertion, and fills in `"ready"` in the JSON with this file and its commit.

## 7. Commands the reviewer ran (all read-only)

- git checks:
  - `git rev-parse guard22-rename 46d2f0f^{commit} HEAD:F guard22-rename:F`;
  - `git hash-object F`;
  - `git status --porcelain F | wc -l` (0);
  - `git diff --cached --name-only | wc -l` (0);
  - `git merge-base HEAD guard22-rename`;
  - `git diff 3c2f4be HEAD --name-only -- build.gradle.kts src/ | wc -l` (0).
- The two blobs: `git cat-file blob` of both, python sha16 (LF and CRLF), the inverse substitution (`inverse == HEAD: True`), and a regex scan of both arms for leftover old names.
- Build and chain files: `sed -n 184,224p build.gradle.kts`; greps of `tools/chains/anchor_free_cert*.sh` and `topic_partition.sh` L556; `gradle.properties` (caching=true).
- Data: the CSV of record (88 lines, 87 rows at reps 300, max n 8133); `snapshots.db` opened with `mode=ro` (the snapshot row is present).
- Build outputs and machine: class-file token counts in `build/classes` (guardDim 1, siteReps 0); the worktree `build/` does not exist; `nproc` = 24; RAM 63.1 GB total / 37.6 GB free.
- The script: `bash -n g22_proof.sh`, and `compare` run on fabricated logs in a scratch directory.
