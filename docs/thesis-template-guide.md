# Thesis LaTeX Template — Reference Guide

Practical reference for working in `report/`, the TU Berlin
(Fachgebiet dbta) LaTeX thesis template this thesis is built on. Written
from what has actually been verified about *this* repository across two
cleanup/authoring passes — not generic LaTeX advice.

## Build process

Root document: `report/main.tex`. It cannot be split-compiled from any
other file.

The compile pipeline is declared as `arara` magic comments at the very top
of `main.tex`:

```
% arara: pdflatex: { shell: yes }
% arara: biber
% arara: makeindex: { options: "-s nomentbl.ist -o main.nls main.nlo" }
% arara: pdflatex: { shell: yes }
% arara: pdflatex: { shell: yes }
```

To build: from the `report/` directory, run

```
arara main.tex
```

This runs pdflatex → biber → makeindex → pdflatex → pdflatex (two final
passes so cross-references, the bibliography, and the nomenclature/index
all settle). `shell: yes` is required because `\begin{filecontents*}` and
the PDF/A metadata handling in `main.tex`/`b_Meta.tex` need shell-escape.

**Prerequisites verified working in this repo:** a MiKTeX (or equivalent
TeX Live) install with `pdflatex`, `biber`, `makeindex`, and `arara` all on
`PATH`. No other setup is needed — `arara main.tex` alone reproduces a full
build.

`00_Arara_and_Latexindent/localSettings.yaml` is **not** part of the
compile pipeline — it configures `latexindent` (automatic `.tex`
reindenting/formatting), a separate, optional tool invoked on demand, not
during `arara main.tex`.

Build artifacts (`main.pdf`, `main.aux`, `main.bbl`, `main.log`, etc.) are
written to `report/` itself. `main.pdf` is the output; `main.log` is the
first place to check for warnings (undefined references, missing
citations — see below).

**Known build quirk:** `01_Document_administration/c_Commands.tex` points
`makeindex` at `05_Literature_and_Index/myindexstyle.ist` for the Index,
but that file does not currently exist in the repo. This does not break
the build (the Index is currently empty since nothing calls `\index{}`
anymore), but if `\index{}` calls are reintroduced and Index formatting
starts to matter, that style file will need to be created or the option
removed.

## Directory structure

| Folder | Purpose |
|---|---|
| `00_Arara_and_Latexindent/` | Build/formatting tool config. `localSettings.yaml` is `latexindent` settings only (see above); the actual compile recipe lives in `main.tex`'s arara comments. |
| `01_Document_administration/` | Preamble/config `\input` by `main.tex`, in order: `a_Packages.tex` (all `\usepackage`s), `b_Meta.tex` (title/author/metadata + document-type booleans), `c_Commands.tex` (custom commands, environments, caption/autoref/bibliography formatting), `d_NomenclatureCommands.tex` (List-of-Symbols group layout), `e_AbbreviationDefinitions.tex` (`\DeclareAcronym` entries), `f_CodeLanguageSpecifications.tex` (`lstlisting` language defs for AMPL/Matlab/LaTeX code blocks). |
| `02_Prematter/` | Front matter, each `\input`/`\include`d directly from `main.tex`: `a_Cover.tex`, `b_Declaration.tex` (affidavit), `c_Dedication.tex` (dissertation-only) + `c_Task.pdf` (thesis-mode task sheet, included instead when `isDiss=false`), `d_Acknowledgements.tex`, `e_Abstract.tex`, `f_Publications.tex` (dissertation-only), `g_Nomenclature.tex` (symbol entries), `h_Abbreviations.tex` (renders the acronym list). |
| `03_Content/` | Thesis chapters. `0_Text.tex` is the master include list read by `main.tex`; it `\input`s the numbered chapter files in build order. Add/reorder chapters by editing `0_Text.tex`. |
| `04_Appendix/` | Appendix chapters, same pattern: `0_Appendix.tex` is the master include list, `\input`ed from `main.tex` inside `\appendix`. |
| `05_Literature_and_Index/` | `Bibliography.bib` (the only `.bib` file) and (nominally) the index style file — see the build quirk above. `UNRESOLVED_CITATIONS.md` (added in this pass) tracks citation keys used in the text but missing from the `.bib` file. |
| `Figures/` | Image assets, on the `graphicspath` (set in `c_Commands.tex`), so figures can be `\includegraphics`d by filename without a path prefix. |

## Editing metadata (title page, author, etc.)

All in `01_Document_administration/b_Meta.tex`. As of this pass these are
still **template placeholders that need real values** before the thesis is
submission-ready:

- `\mytitle` — thesis title (currently placeholder text)
- `\autor` — author name (currently placeholder text)
- `\orcid` — ORCID (currently `XXXX-XXXX-XXXX-XXXX`)
- `\courseofstudy` — degree programme (currently `Mein Studiengang`)
- `\mymatriculationnumber` — currently `XXXXXX`
- `\myadvisor` — advisor name (currently placeholder text)
- `\germankeywords` / `\englishkeywords` — currently placeholder keyword lists

Document-type booleans, same file:

- `isDiss` — `true` = dissertation, `false` = Bachelor/Master thesis. Currently `false`. Governs: cover-page layout (`a_Cover.tex`), whether the Dedication (`c_Dedication.tex`) or the Task PDF (`c_Task.pdf`) is included, and whether the Publications chapter (`f_Publications.tex`) renders at all.
- `isMT` — `true` = Master's, `false` = Bachelor's (only meaningful when `isDiss=false`). Currently `true`. Governs the cover subtitle wording.
- `containsEN` — confidentiality/embargo notice toggle; when `true`, prints a `Sperrvermerk` naming `\firmenname` (also set in this file). Currently `false`.
- `isSG` — "styleguide-authoring mode" for the template's own documentation; not relevant to this thesis (leave `false`).

## Adding a new appendix

Pattern used for all appendices so far (A/B added by the original author,
C/D added in this pass):

1. Create `04_Appendix/N_Appendix_Name.tex` starting with
   `\chapter{Title}\label{app:some-label}`.
2. Add a line `\input{04_Appendix/N_Appendix_Name}` to
   `04_Appendix/0_Appendix.tex`.

Appendix lettering (Appendix A, B, C, …) is automatic — `documentclass[...,
appendixprefix=true, ...]` plus `\appendix` in `main.tex` — and follows the
**order of the `\input` lines** in `0_Appendix.tex`, not the filename
number. Keep the two in sync by convention, but the number in the filename
is not itself meaningful to the build.

Current appendices: A = Taxonomy Tuning Protocol
(`7_Appendix_TuningProtocol.tex`), B = Reference-Informed Judge Generation
(`8_Appendix_JudgeGeneration.tex`), C = Formal Metric Definitions
(`9_Appendix_MetricDefinitions.tex`), D = Evaluated Model Roster
(`10_Appendix_ModelRoster.tex`). `04_Appendix/0_Appendix.tex` is the single
source of truth for what's actually wired in — appendix files can exist on
disk without being included (check there before assuming a file is live).

Several `\ref{app:...}` calls in the main chapters still point at
appendices that don't exist yet (`app:numerics`, `app:graphnode-schema`,
`app:infra`) — these render as `??` in the PDF and are proposed-but-not-yet-drafted; see the citation/appendix proposal notes from the most recent session for what belongs in them and why they weren't drafted yet (source material exists but needs careful reconciliation with the current Methodology chapter before it's copied in).

## Citations

- Single bibliography database: `report/05_Literature_and_Index/Bibliography.bib`, loaded via `\addbibresource` in `main.tex`. Backend is `biblatex` + `biber` (not bibtex), `citestyle=authoryear`, `style=authoryear-comp` (see `a_Packages.tex`).
- In-text convention used throughout the chapters: `\parencite{key}` for parenthetical citations, `\textcite{key}` for narrative ("Author (Year) showed..."). Multiple keys: `\parencite{key1, key2}`.
- To check for missing/undefined citations: build with `arara main.tex`, then `grep -A2 "could not be found" report/main.log` — biblatex lists every `\cite`-family key it couldn't resolve against `Bibliography.bib`.
- **`report/05_Literature_and_Index/UNRESOLVED_CITATIONS.md`** (added in this pass) is the current list: 42 citation keys used in the chapter text with no matching `.bib` entry, each with file/line and the sentence it's supporting, so real bibliographic data can be sourced and added. None of the 42 are typos of existing entries (checked). Regenerate this list the same way if more citations are added before it's resolved.

## The `\todo{}` mechanism

- Package: `todonotes`, loaded in `01_Document_administration/a_Packages.tex` with `[colorinlistoftodos, \languagename, textsize=footnotesize]`.
- Usage: `\todo{note text}` inserts a margin note at that point; `\todo[inline]{note text}` renders inline instead (used for chapter-level "this is a skeleton" notes in this pass, since a bare `\todo{}` with no surrounding paragraph text can trip LaTeX into "no line here to end" errors if immediately followed by something needing horizontal mode — pair it with at least a short following sentence, or use `[inline]`, if that happens).
- `main.tex` calls `\listoftodos` and `\todototoc` (in the front-matter "Lists of..." block) to generate an automatic **List of ToDos** (titled "List of ToDos" in English / "ToDo-Verzeichnis" in German, per the language-dependent rename in `c_Commands.tex`) with page-linked entries for every `\todo{}` in the document. It regenerates automatically on a normal `arara main.tex` build — no separate step needed.
- Convention adopted in this pass: `\todo{...}` is used for placeholder/pending content (unwritten abstract, unwritten acknowledgements, structural skeleton sections in Results/Discussion) rather than lorem-ipsum filler or instructional prose, so pending work is both visibly marked in the PDF and centrally listed.

## Nomenclature and abbreviations

Two independent, currently-empty lists (cleared of the template's original
chemistry/process-engineering demo content in an earlier cleanup pass —
both need real thesis-specific entries added over time):

- **List of Symbols** (`nomencl` package): declare entries in `02_Prematter/g_Nomenclature.tex` with `\nomenclature[category]{symbol}{description}{}{unit/definition}`. Category letters (`L`/`G`/`X`/`Z`/`C`/`D`/`O`/`I` → Latin/Greek/Superscripts/Subscripts/Constants/Dimensionless numbers/Operators/Indices) and their printed group headings are wired in `01_Document_administration/d_NomenclatureCommands.tex`.
- **List of Abbreviations** (`acro` package): declare each abbreviation in `01_Document_administration/e_AbbreviationDefinitions.tex` with `\DeclareAcronym{key}{short=..., long=..., tag=...}`, then use `\ac{key}` in body text (auto-expands on first use, abbreviates thereafter). `02_Prematter/h_Abbreviations.tex` renders the list via `\printacronyms[...]`; it currently prints a single unclassified list (`heading=none`) — switch to per-`tag` sections (see the `include={TagName}, heading=section*` pattern) once there are enough abbreviations to warrant grouping.

## Other structural conventions observed

- **Label namespacing**: `ch:` for chapters, `sec:`/`subsec:` for sections/subsections (prefixed by a chapter abbreviation, e.g. `meth-`, `exp-`, `arch-`, `res-`, `disc-`), `app:` for appendix chapters, `tab:`/`fig:`/`eq:` for floats/equations. Follow this when adding new labels — it's what makes `\ref{}` targets guessable across chapters.
- **`\appendixprefix=true`** documentclass option: appendix chapters are automatically numbered "Appendix A", "Appendix B", … — don't hand-letter them.
- **Language machinery**: `babel` loads `english` then `ngerman` (English is default here, since it's listed first). Bilingual front-matter blocks (Declaration, Abstract, Publications) use `\iflanguage{english}{...}{\iflanguage{ngerman}{...}{}}` to switch heading text; don't assume a chapter is single-language just because most content chapters are English-only prose.
- **`\include` vs `\input`**: mostly `\input` throughout (allows arbitrary nesting); `02_Prematter/g_Nomenclature.tex` is the one file pulled in with `\include` (needed for the nomenclature/makeindex mechanism specifically).
- **`\printindex`** (imakeidx) is still wired in `main.tex`, but nothing currently calls `\index{}` (the template's own instructional chapter, which was full of `\index{}` calls, was removed as boilerplate). The Index chapter will render essentially empty unless `\index{}` calls are added back.
- Two appendix chapters (`7_Appendix_TuningProtocol.tex`, `8_Appendix_JudgeGeneration.tex`) existed on disk with real content but were **not** wired into `0_Appendix.tex` until this pass — always check `0_Appendix.tex` (and `0_Text.tex` for chapters) rather than assuming a file's presence in the folder means it's part of the build.
