# EVAL-METRIC-DETERMINISM rule-7 guard (W1 + processes + RAM), derived from the D9 operator's w1.ps1 (untouched).
# usage: powershell -NoProfile -File emd_w1.ps1 [-Admit "pid,pid"]      exit 0 = GO; 4 = WAIT (never kill); 2 = bad args
# W1: main's embeddings_cache.db and ag_news_smoke_cache_v1.db must open EXCLUSIVELY (FREE). Processes: every java.exe /
# python.exe is printed; a python whose command line contains --selftest, or a PID listed in -Admit (the harness's own
# Gradle / Kotlin daemons, recorded after leg P1), is ADMITTED and printed; any other is FOREIGN -> WAIT. RAM >= 12 GB.
param([string]$Admit = "", [string]$Main = "Z:\FAC\TUBerlin\THESIS\TaxoArena")
$go = $true
$adm = @()
if ($Admit -ne "") { $adm = $Admit.Split(",") | ForEach-Object { [int]$_ } }
foreach ($n in @("embeddings_cache.db", "ag_news_smoke_cache_v1.db")) {
  $p = Join-Path $Main $n
  try { $f = [IO.File]::Open($p, 'Open', 'Read', 'None'); $f.Close(); "[W1] FREE $p" }
  catch { "[W1] BUSY $p : $($_.Exception.Message)"; $go = $false }
}
Get-CimInstance Win32_Process -Filter "Name='java.exe' or Name='python.exe' or Name='pythonw.exe'" | ForEach-Object {
  $cl = [string]$_.CommandLine
  if ($adm -contains [int]$_.ProcessId) { "[PROC] ADMITTED (listed) $($_.ProcessId) $($_.Name) $($_.CreationDate) $cl" }
  elseif ($_.Name -like "python*" -and $cl -like "*--selftest*") { "[PROC] ADMITTED (--selftest) $($_.ProcessId) $($_.Name) $cl" }
  else { "[PROC] FOREIGN $($_.ProcessId) $($_.Name) $($_.CreationDate) $cl"; $go = $false }
}
$gb = [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB, 2)
"[RAM] free GB $gb (bar 12)"
if ($gb -lt 12) { $go = $false }
"[TIME] " + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
if ($go) { "[W] GO"; exit 0 } else { "[W] WAIT (never kill; re-run until GO)"; exit 4 }
