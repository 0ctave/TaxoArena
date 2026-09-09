# Structure-only sweep chain with OVERLAPPED site-nulls (docs/perf_review_2026-09-09.md, item #3).
#
#   pwsh -File tools/chains/sweep_chain.ps1 -Sweep experiment_results/dimsweep5 -ConfigDir experiment_configs/dimsweep5 `
#        -Arms bareq512_s7,bareq512_s11 -Dim 512 [-DropTop 0] [-Whiten false] [-NoOverlap]
#
# Per arm: BUILD (gradlew bootRun on <ConfigDir>/<arm>.toml; label-free, structural evidence only),
# then the arm's site-level null (`gradlew siteNull`) is launched DETACHED and the next arm's build
# starts immediately. The null reads only snapshots.db + embeddings_cache.db (never the pool file or
# the dataset DB), and build phase 4 is ~1 core while the null saturates all cores, so the two
# overlap with ~5% mutual slowdown. Builds stay strictly sequential (one construction per repo
# root: the reserved-pool activation and reserved_test_queries.json are process-global).
# Results are bit-identical to the sequential chain: both processes are deterministic and
# timing-independent (per-replicate seeded RNG in the null; no randomness in the splitter).
#
# Invariants: never pass --rerun-tasks (it recompiles build/classes under the running null JVM and
# costs a full Kotlin recompile per build for nothing); the frozen pool of record is re-pinned at
# the end (every build activates its own split); the frozen triples JSON is restored from HEAD.
param(
    [Parameter(Mandatory)] [string] $Sweep,
    [Parameter(Mandatory)] [string] $ConfigDir,
    [Parameter(Mandatory)] [string[]] $Arms,
    [Parameter(Mandatory)] [int] $Dim,
    [int] $DropTop = 0,
    [string] $Whiten = "false",
    [switch] $NoOverlap
)
$ErrorActionPreference = "Continue"
Set-Location (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
New-Item -ItemType Directory -Force $Sweep | Out-Null
$log = Join-Path $Sweep "chain.log"
function L($m) { $t = Get-Date -Format "HH:mm:ss"; "$t $m" | Tee-Object -FilePath $log -Append }

L "SWEEP CHAIN start: arms=$($Arms -join ',') dim=$Dim dropTop=$DropTop whiten=$Whiten overlap=$(-not $NoOverlap) HEAD=$(git rev-parse --short HEAD)"
$nulls = @()
foreach ($tag in $Arms) {
    $cfg = Join-Path $ConfigDir "$tag.toml"
    if (-not (Test-Path $cfg)) { L "${tag}: config $cfg missing, skipping"; continue }
    $seed = (Select-String -Path $cfg -Pattern '^\s*seed\s*=\s*(\d+)' | Select-Object -First 1).Matches[0].Groups[1].Value
    $runDir = Join-Path $Sweep "$tag\seed_$seed"
    if (Test-Path (Join-Path $runDir "dag_snapshots.jsonl")) { L "$tag build present, skipping build" }
    else {
        L "$tag BUILD start"
        $sw = [Diagnostics.Stopwatch]::StartNew()
        .\gradlew.bat bootRun --console=plain -q --args="--config $cfg" *> (Join-Path $Sweep "$tag.build.out")
        L "$tag BUILD exit=$LASTEXITCODE wall=$([int]$sw.Elapsed.TotalSeconds)s"
    }
    $csv = Join-Path $Sweep "site_null_$tag.csv"
    if (Test-Path $csv) { L "$tag site-null present, skipping"; continue }
    $logFile = Join-Path $runDir "headless_run.log"
    if (-not (Test-Path $logFile)) { L "$tag no run log; skipping site-null"; continue }
    $snap = (Select-String -Path $logFile -Pattern "Snapshot ID: (\S+)" | Select-Object -Last 1).Matches[0].Groups[1].Value
    if (-not $snap) { L "$tag no snapshot id; skipping site-null"; continue }
    $nullArgs = @("siteNull", "--console=plain", "-q", "-DsnapshotId=$snap", "-DsliceDim=$Dim", "-DdropTop=$DropTop", "-Dwhiten=$Whiten", "-DoutCsv=$csv")
    $outFile = Join-Path $Sweep "$tag.sitenull.out"
    if ($NoOverlap) {
        L "$tag SITENULL start (sequential) snapshot=$snap"
        $sw = [Diagnostics.Stopwatch]::StartNew()
        & .\gradlew.bat @nullArgs *> $outFile
        L "$tag SITENULL exit=$LASTEXITCODE wall=$([int]$sw.Elapsed.TotalSeconds)s"
    } else {
        # Site-nulls are serialised among themselves: two concurrent `gradlew siteNull` invocations
        # share the Test task's output directory (build/test-results/siteNull) and the second one
        # fails at start-up with "Unable to delete directory ... output.bin" (observed 2026-09-09
        # 22:46, D4 Law arm). Builds are shorter than nulls, so waiting here still lets every null
        # overlap the NEXT build.
        if ($nulls.Count -gt 0) {
            $prev = $nulls[-1]
            if (-not $prev.proc.HasExited) { L "$tag waiting for $($prev.tag) SITENULL to finish before launching its own"; $prev.proc.WaitForExit() }
        }
        L "$tag SITENULL launched DETACHED (overlaps the next build) snapshot=$snap"
        $p = Start-Process -FilePath (Resolve-Path .\gradlew.bat) -ArgumentList $nullArgs -RedirectStandardOutput $outFile -RedirectStandardError "$outFile.err" -WindowStyle Hidden -PassThru
        $nulls += @{ tag = $tag; proc = $p; started = Get-Date }
    }
}
foreach ($n in $nulls) {
    $n.proc.WaitForExit()
    L "$($n.tag) SITENULL exit=$($n.proc.ExitCode) wall=$([int]((Get-Date) - $n.started).TotalSeconds)s"
}
L "RE-PIN frozen pool of record"
python tools\analysis\pool_guard.py --activate *>> $log
git checkout -- frozen_triples_20260727_042523_Headless_Run_Auto_ge_MAIN.json 2>$null
L "SWEEP CHAIN done"
