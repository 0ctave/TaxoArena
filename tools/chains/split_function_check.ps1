# The 3/3 criterion of FRAMEWORK item 18 (SPLIT-FUNCTION-IMPL): three passes of
#   python tools/analysis/pool_guard.py --pool p2dca21ab5f4ef3ae     (the MMLU-Pro pool reproduces as a list)
#   python tools/analysis/pool_guard.py --pool paeec37aa28063c75     (the union pool reproduces as a list)
#   python tools/analysis/split_side.py --selftest                   (the function reproduces every vector)
#   gradlew test --tests taxonomy.dataset.SplitSide* --tests taxonomy.dataset.PinnedPoolsReproduceTest
#                                                                    (the Kotlin replication of both)
# Each pass concatenates the deterministic outputs (the gradle step contributes its per-class
# test/failure counts, not its timings), prints the pass's sha256, and PASS is printed iff the
# three digests are identical and every step exited 0. Read-only on every DB, 0 LLM calls, no
# construction. Set TAXOARENA_DATA_ROOT when the caches live outside this checkout.
#
#   powershell -File tools/chains/split_function_check.ps1
$ErrorActionPreference = "Continue"
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $root
$digests = @()
$allOk = $true
for ($pass = 1; $pass -le 3; $pass++) {
    $out = New-Object System.Text.StringBuilder
    $ok = $true
    foreach ($cmd in @(
        @("python", "tools/analysis/pool_guard.py", "--pool", "p2dca21ab5f4ef3ae"),
        @("python", "tools/analysis/pool_guard.py", "--pool", "paeec37aa28063c75"),
        @("python", "tools/analysis/split_side.py", "--selftest"))) {
        $text = & $cmd[0] $cmd[1..($cmd.Length - 1)] 2>&1 | Out-String
        if ($LASTEXITCODE -ne 0) { $ok = $false; Write-Host "[pass $pass] FAILED: $($cmd -join ' ')" }
        [void]$out.AppendLine("## " + ($cmd -join " "))
        [void]$out.Append($text)
    }
    $gradle = & .\gradlew.bat test --offline -q --rerun-tasks --tests "taxonomy.dataset.SplitSide*" --tests "taxonomy.dataset.PinnedPoolsReproduceTest" 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) { $ok = $false; Write-Host "[pass $pass] FAILED: gradle"; Write-Host $gradle }
    [void]$out.AppendLine("## gradle test SplitSide* PinnedPoolsReproduceTest")
    Get-ChildItem "build/test-results/test" -Filter "*.xml" | Where-Object { $_.Name -match "SplitSide|PinnedPoolsReproduce" } | Sort-Object Name | ForEach-Object {
        $x = [xml](Get-Content $_.FullName)
        [void]$out.AppendLine("$($x.testsuite.name) tests=$($x.testsuite.tests) failures=$($x.testsuite.failures) errors=$($x.testsuite.errors) skipped=$($x.testsuite.skipped)")
    }
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($out.ToString())
    $sha = [System.BitConverter]::ToString([System.Security.Cryptography.SHA256]::Create().ComputeHash($bytes)).Replace("-", "").ToLower()
    $digests += $sha
    if (-not $ok) { $allOk = $false }
    Write-Host "[pass $pass] exit=$(if ($ok) { 0 } else { 1 }) sha256=$sha"
    if ($pass -eq 1) { Write-Host $out.ToString() }
}
$identical = ($digests | Select-Object -Unique).Count -eq 1
if ($allOk -and $identical) { Write-Host "PASS: 3/3 passes reproduce the pinned pools as lists and the function for new items (digest $($digests[0]))"; exit 0 }
else { Write-Host "FAIL: allOk=$allOk identical=$identical digests=$($digests -join ', ')"; exit 1 }
