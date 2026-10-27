# R2 supervisor — SINGLE-PASS, run by Windows Task Scheduler every 15 min.
# Independent of any Claude Code session: survives session death, terminal close,
# and credit exhaustion on the assistant side. Requires only: machine on, user
# logged in, Azure credit for the judge calls.
#
# Each pass: if the R2 JVM is running -> exit. If all 20 strata converged ->
# delete this scheduled task and exit. Otherwise relaunch bootRun (lossless
# resume from match_history; INVALID verdicts are never persisted). The task's
# default IgnoreNew instance policy prevents overlapping passes while a
# relaunched bootRun is still running inside one instance.
$ErrorActionPreference = 'Continue'
$TASKNAME = 'TaxoArenaR2Supervisor'
Set-Location 'Z:\FAC\TUBerlin\THESIS\TaxoArena'
$log = 'experiment_results\x12_profile\supervisor.log'
$runlog = 'experiment_results\x12_profile\run.log'
$countFile = 'experiment_results\x12_profile\supervisor_relaunches.txt'

$running = Get-CimInstance Win32_Process -Filter "Name='java.exe'" -ErrorAction SilentlyContinue |
           Where-Object { $_.CommandLine -match 'x12_profile' }
if ($running) { exit 0 }

# Converged? The all-converged [PROFILE] line has 20 stratum stars + 1 legend star.
$last = ''
try {
    $m = Select-String -Path $runlog -Pattern '\[PROFILE\] round' -ErrorAction Stop
    if ($m) { $last = $m[-1].Line }
} catch {}
$stars = ($last.ToCharArray() | Where-Object { $_ -eq '*' }).Count
if ($stars -ge 21) {
    Add-Content $log "$(Get-Date -Format s) [task] all strata converged - removing scheduled task"
    schtasks /delete /tn $TASKNAME /f | Out-Null
    exit 0
}

$count = 0
if (Test-Path $countFile) { $count = [int](Get-Content $countFile -ErrorAction SilentlyContinue | Select-Object -First 1) }
if ($count -ge 8) {
    Add-Content $log "$(Get-Date -Format s) [task] relaunch cap (8) reached, stars=$stars - removing task, manual attention needed"
    schtasks /delete /tn $TASKNAME /f | Out-Null
    exit 0
}
Set-Content $countFile ($count + 1)

Get-Content .env | ForEach-Object {
    $line = ($_ -replace "`r", '').Trim()
    if ($line -match '^([A-Za-z_][A-Za-z0-9_]*)=(.*)$') {
        [System.Environment]::SetEnvironmentVariable($Matches[1], $Matches[2], 'Process')
    }
}
Add-Content $log "$(Get-Date -Format s) [task] JVM down, unconverged (stars=$stars) - relaunch #$($count + 1)"
cmd /c 'gradlew.bat bootRun --rerun-tasks "-Dranking.db.path=experiment_results/x12_profile/ratings_x12p.db" "--args=--config experiment_configs/x12_profile.toml" >> experiment_results\x12_profile\run.log 2>&1'
Add-Content $log "$(Get-Date -Format s) [task] bootRun exited with code $LASTEXITCODE"
