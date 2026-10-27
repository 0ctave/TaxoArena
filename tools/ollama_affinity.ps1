# THREAD-CAP (registered 2026-09-27, docs/judge_v2_program.md section "THREAD-CAP", plan R-F, RP07),
# Ollama route (ii) as ruled after READY_w0_rp07 M2: PROCESS AFFINITY of the Ollama server, a
# first-N-CPU mask. No engine code, no request option, no derived tag, no DB path.
#
# Windows child processes inherit the parent's affinity, so the runner (llama.cpp) processes the
# server spawns AFTER the mask is set run on the same N CPUs. A runner already loaded BEFORE the
# mask is set keeps its old mask: this script sets and prints the mask of every ollama* process
# it finds, server and runners, and prints each one's mask after setting (the B4 witness).
#
# Usage (PowerShell):
#   .\tools\ollama_affinity.ps1 -Threads 12            # dry run: prints the mask and the current masks, sets nothing
#   .\tools\ollama_affinity.ps1 -Threads 12 -Apply     # sets the mask on every ollama* process, prints each after
#   .\tools\ollama_affinity.ps1 -SelfTest              # mask arithmetic on known values, no process touched
# B4 witness procedure: start `ollama serve`, run this with -Apply BEFORE the first embedding
# request, run the 200-text scratch leg, then run this again (dry) and read the OS peak CPU
# (Get-Counter '\Processor(_Total)\% Processor Time' sampled during the leg). Fail-closed:
# -Threads outside 1..24 refuses; -Apply with no ollama process refuses.
param(
    [int]$Threads = 0,
    [switch]$Apply,
    [switch]$SelfTest
)
$ErrorActionPreference = 'Stop'

function Get-CapMask([int]$n) {
    if ($n -lt 1 -or $n -gt 24) { throw "[THREAD-CAP] -Threads $n is not in 1..24; refusing" }
    return [int64](([int64]1 -shl $n) - 1)
}

if ($SelfTest) {
    $cases = @(@(1, 1), @(8, 255), @(12, 4095), @(24, 16777215))
    $fail = 0
    foreach ($c in $cases) {
        $got = Get-CapMask $c[0]
        if ($got -ne $c[1]) { $fail++; Write-Output "FAIL mask($($c[0])) = $got, expected $($c[1])" }
        else { Write-Output ("ok   mask({0}) = 0x{1:X}" -f $c[0], $got) }
    }
    foreach ($bad in @(0, 25, -3)) {
        try { Get-CapMask $bad | Out-Null; $fail++; Write-Output "FAIL mask($bad) admitted" }
        catch { Write-Output "ok   mask($bad) refused" }
    }
    Write-Output "SELFTEST $(if ($fail -eq 0) {'PASS'} else {"FAIL ($fail)"})"
    if ($fail -ne 0) { exit 1 }
    exit 0
}

$mask = Get-CapMask $Threads
Write-Output ("[THREAD-CAP] ollama route (ii) requested={0} mask=0x{1:X} logicalProcessors={2}" -f $Threads, $mask, [Environment]::ProcessorCount)
$procs = @(Get-Process -Name 'ollama*' -ErrorAction SilentlyContinue)
if ($procs.Count -eq 0) {
    if ($Apply) { throw "[THREAD-CAP] no ollama* process found; start 'ollama serve' first; refusing" }
    Write-Output "[THREAD-CAP] no ollama* process running (dry run; nothing set)"
    exit 0
}
foreach ($p in $procs) {
    if ($Apply) { $p.ProcessorAffinity = [IntPtr]$mask; $p.Refresh() }
    Write-Output ("[THREAD-CAP] pid={0} name={1} affinity=0x{2:X} {3}" -f $p.Id, $p.ProcessName, [int64]$p.ProcessorAffinity, $(if ($Apply) {'(set)'} else {'(dry run, unchanged)'}))
}
