@echo off
rem EVAL-METRIC-DETERMINISM leg runner (registration docs/judge_v2_program.md L20311-L20389, 55a6ce1): the REGISTERED bootRun
rem command, unchanged, captured by cmd redirection (no PowerShell ErrorRecord wrapping, no UTF-16). Derived from
rem experiment_results/lcb_stage0/d9/helpers/d9_legrun.cmd (blob:8a67bcbf), which is untouched; changes: leg names
rem P1 R1 R2 P2 R3, ratings_emd_<leg>.db, no probe branch; -PjvmThreads=12 in every leg (re-cut 2026-09-30, B-EM-1 (3);
rem the registrar's L22178: the same -PjvmThreads in all five legs).
rem usage: emd_legrun.cmd <P1|R1|R2|P2|R3> <leg root> <stage dir>      writes leg<L>_bootrun.log, leg<L>_exit.txt in the stage
setlocal
if "%~3"=="" (echo usage: emd_legrun.cmd P1^|R1^|R2^|P2^|R3 leg-root stage-dir & exit /b 2)
if not "%~4"=="" (echo [RUN] refusing: exactly three arguments & exit /b 2)
set "L=%~1"
set "R=%~2"
set "ST=%~3"
set "OK="
for %%x in (P1 R1 R2 P2 R3) do if "%L%"=="%%x" set "OK=1"
if not defined OK (echo [RUN] refusing: leg must be P1, R1, R2, P2 or R3 & exit /b 2)
if not exist "%ST%\" (echo [RUN] refusing: stage dir %ST% does not exist & exit /b 2)
set "LOG=%ST%\leg%L%_bootrun.log"
set "EXF=%ST%\leg%L%_exit.txt"
if exist "%LOG%" (echo [RUN] refusing: %LOG% exists & exit /b 2)
if exist "%EXF%" (echo [RUN] refusing: %EXF% exists & exit /b 2)
cd /d "%R%" || (echo [RUN] refusing: cannot cd to %R% & exit /b 2)
>>"%EXF%" echo START %DATE% %TIME%
call .\gradlew.bat bootRun --console=plain --offline --no-build-cache -PjvmThreads=12 "-Dranking.db.path=ratings_emd_%L%.db" --args="--config experiment_configs/topic_partition/ag_news_smoke_s42.toml" > "%LOG%" 2>&1
set "RC=%ERRORLEVEL%"
>>"%EXF%" echo EXIT %RC%
>>"%EXF%" echo END %DATE% %TIME%
echo [RUN] %LOG% EXIT %RC%
exit /b %RC%
