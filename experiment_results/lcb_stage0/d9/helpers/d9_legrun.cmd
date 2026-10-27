@echo off
rem LCB-D9-BYTE-INERTNESS leg runner (delta READY docs/reviews/READY_lcb_d9_delta1.md): the REGISTERED bootRun commands,
rem unchanged, captured by cmd redirection (no PowerShell ErrorRecord wrapping, no UTF-16).
rem usage: d9_legrun.cmd <A|B> <leg root> <stage dir>                      the leg (S3/S4): leg<L>_bootrun.log, leg<L>_exit.txt
rem        d9_legrun.cmd <A|B> <leg root> <stage dir> probe <probe toml>   the R3 probe (S6/S7): probe<L>.log, probe<L>_exit.txt
setlocal
if "%~3"=="" (echo usage: d9_legrun.cmd A^|B leg-root stage-dir [probe probe-toml] & exit /b 2)
set "L=%~1"
set "R=%~2"
set "ST=%~3"
if not "%L%"=="A" if not "%L%"=="B" (echo [RUN] refusing: leg must be A or B & exit /b 2)
if not exist "%ST%\" (echo [RUN] refusing: stage dir %ST% does not exist & exit /b 2)
if "%~4"=="" goto leg
if not "%~4"=="probe" (echo [RUN] refusing: 4th argument must be probe & exit /b 2)
if "%~5"=="" (echo [RUN] refusing: probe needs the probe toml & exit /b 2)
set "LOG=%ST%\probe%L%.log"
set "EXF=%ST%\probe%L%_exit.txt"
goto run
:leg
set "LOG=%ST%\leg%L%_bootrun.log"
set "EXF=%ST%\leg%L%_exit.txt"
:run
if exist "%LOG%" (echo [RUN] refusing: %LOG% exists & exit /b 2)
if exist "%EXF%" (echo [RUN] refusing: %EXF% exists & exit /b 2)
cd /d "%R%" || (echo [RUN] refusing: cannot cd to %R% & exit /b 2)
>>"%EXF%" echo START %DATE% %TIME%
if "%~4"=="probe" (
  call .\gradlew.bat bootRun --console=plain --offline "-Dranking.db.path=ratings_d9_probe%L%.db" --args="--config %~5" > "%LOG%" 2>&1
) else (
  call .\gradlew.bat bootRun --console=plain --offline --no-build-cache "-Dranking.db.path=ratings_d9_%L%.db" --args="--config experiment_configs/topic_partition/ag_news_smoke_s42.toml" > "%LOG%" 2>&1
)
set "RC=%ERRORLEVEL%"
>>"%EXF%" echo EXIT %RC%
>>"%EXF%" echo END %DATE% %TIME%
echo [RUN] %LOG% EXIT %RC%
exit /b %RC%
