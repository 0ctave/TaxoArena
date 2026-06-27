# HANDOVER

Top-level pointer doc for the next AI coding agent resuming work on TaxoArena.

## Owner

- Octave Boëlle (octave.boelle@gmail.com), Berlin DE

## Repo

- https://github.com/0ctave/TaxoArena (default branch: `main`)

## Build environment

Verbatim guidance:

> Build with `JAVA_HOME=~/.gradle/jdks/jdk-21.0.11+10 ./gradlew compileKotlin compileTestKotlin --no-daemon` under Temurin JDK 21 from `~/.gradle/jdks/`. System JDK on the workstation is 25 — DO NOT use it. The owner runs JDK 23 on Windows against this guidance; agents should still use JDK 21.

## Stack versions

- Kotlin 2.1.10
- Spring Boot 3.4.3
- Gradle 8.10
- Mosaic 0.18.0
- Temurin JDK 21.0.11+10

## Owner's working preferences

- Conservative on token use — short reports, no bloat.
- Coding work goes through coding subagent / Claude Code / Codex — never edit code directly from the parent agent.
- Subagents push branches but do NOT open PRs; the orchestrator opens & merges via `gh`.
- Use `gh` CLI for all GitHub operations (not browser, not connector).

## PR pipeline

PRs #46–#69 all merged as of this handover. The next planned task is a metrics-section refactor — see `docs/ROADMAP.md`.

## Pointers

- `docs/ARCHITECTURE.md` — core package map and key files with their roles.
- `docs/METRICS.md` — metric philosophy, quality vs characterization split, NMI specifics, run snapshots.
- `docs/PR_HISTORY.md` — tabular history of PRs #46–#69.
- `docs/ROADMAP.md` — prioritized forward-looking work for the next agent.
- `docs/CONVENTIONS.md` — build/test commands, branch/PR naming, merge policy.
