@echo off
rem One-shot tuning pipeline launcher.
rem   tune              -> full pipeline: L9 screen (seed 42) -> collect -> Pareto select -> validate finalists (seeds 137, 2048)
rem   tune screen       -> screening stage only
rem   tune validate     -> finalist validation only (needs tuning/finalists.csv from a previous select)
rem   tune screen --clean  -> wipe previous outputs first
cd /d "%~dp0"
set STAGE=%1
if "%STAGE%"=="" set STAGE=full
python tools\tuning\tuning_harness.py pipeline --spec tools\tuning\sweep_spec.toml --stage %STAGE% %2 %3
