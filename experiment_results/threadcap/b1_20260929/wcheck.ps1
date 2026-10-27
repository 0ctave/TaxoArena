param([string]$tag)
"== W-CHECK $tag $(Get-Date -Format s)"
foreach($f in 'embeddings_cache.db','embeddings_cache.db-wal','embeddings_cache.db-shm','snapshots.db','snapshots.db-wal','snapshots.db-shm','snapshots_frozen.db'){
  if(Test-Path $f){ try{ $s=[IO.File]::Open((Resolve-Path $f),'Open','Read','None'); $s.Close(); "W1 $f FREE" } catch { "W1 $f BUSY" } } else { "W1 $f absent" } }
Get-CimInstance Win32_Process | ?{ $_.Name -match 'java|python|gradle' } | %{ $c=($_.CommandLine+'') -replace '\s+',' '; $k='other'; if($c -match 'GradleDaemon'){$k='gradle-daemon'} elseif($c -match 'Gradle Test Executor|GradleWorkerMain|worker.org.gradle'){$k='GRADLE-WORKER'} elseif($c -match 'kotlin-compiler|KotlinCompileDaemon'){$k='kotlin-daemon'} elseif($c -match '--selftest'){$k='selftest(admitted)'} elseif($c -match 'bootRun|TaxoArenaApplication|pool_guard|dry-run|tools[/\]analysis|tools[/\]chains'){$k='REFUSED'}; "W2 {0} {1} {2}" -f $_.ProcessId,$k,$c.Substring(0,[Math]::Min(140,$c.Length)) }
"W4 {0:N1} GB free" -f ((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB)
