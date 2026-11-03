# Checkpoint 01 — Foundation and baseline

## Scope and repository inspection

Inspected the existing project rather than rebuilding it. The accessible working copy
was on branch `main`, clean at the beginning of this checkpoint, with these real local
commits already present:

- `4b0b347` — project initialization and assumptions.
- `57d3d36` — catalog and policy tools.
- `fdeeadf` — original 15-test baseline.
- `cb1dae2` — Windows setup and English commands.
- `6acb528` — allowed tools and initial session-scoped order lookup.

The last two commits were made during the preceding session before the new manual
checkpoint workflow was supplied. They are preserved, not backdated or rewritten.
No new commit or push was made for Checkpoint 01. The ZIP deliberately excludes `.git`.
Your Windows checkout may have a different history; inspect it before committing.

## Actual changes

- Restore Portuguese CLI aliases while keeping English primary commands.
- Repair the Windows launcher that previously referenced an unimplemented web app.
- Remove unused web/provider runtime dependencies from the CLI baseline.
- Translate current technical documentation and docstrings into English; preserve
  explanatory Portuguese comments and original Portuguese source data.
- Clarify what is implemented, planned, or not yet verified.
- Add compatibility/path tests without changing the 15 original tests.

## Files created

- `CHECKPOINT.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `tests/test_cli.py`

## Files modified relative to the inspected working copy

- `README.md`, `docs/decisoes.md`
- `pyproject.toml`, `.env.example`
- `setup_windows.bat`, `start_windows.bat`
- `src/emporio/cli.py`, `src/emporio/config.py`
- `src/emporio/__init__.py`, `src/emporio/catalog.py`, `src/emporio/policies.py`,
  `src/emporio/tools.py`: docstrings translated; existing business behavior preserved.
- `scripts/build_policy_index.py`: docstring translated.

No source CSV, PDF, policy-index content, or original test was modified. No files
need deletion when applying this snapshot. Existing `.git`, `.env` and `.venv` are not
included or overwritten by the ZIP. The Python distribution remains version 0.2.0,
which already existed before this checkpoint's changes.

## Observed validation in the execution environment

Environment: Linux, Python 3.12. These results are actual tool executions, not a claim
that the candidate has executed the new snapshot on Windows.

| Command or check | Actual result |
|---|---|
| `python -m pip install -e .` | Successfully installed emporio-agent 0.2.0 |
| `python -m emporio.cli catalogo --categoria Violões --maximo 1000` | Returned 10 products (default result limit); all available and priced at or below BRL 1,000 |
| `python -m unittest discover -s tests -v` | Ran 19 tests; OK (revised checkpoint) |
| Compare `tests/test_core.py` with original baseline commit | Byte-identical; all 15 tests retained |
| Compare six CSVs and policy PDF with supplied files | Byte-identical |
| Parse Python source files | Successful |
| Archive structure and excluded paths | Verified when packaging; no enclosing directory, secrets or Git metadata |

The editable installer warned that the console-script directory is not on this
container's PATH. The documented `python -m emporio.cli` form avoids that issue.

## Requirements coverage

| Area | Status |
|---|---|
| Python package and reproducible deterministic tools | Implemented; baseline validated |
| Pricing, promotions, stock/status checks | Existing tests pass |
| Policy retrieval with page references and hash check | Implemented; baseline tested |
| Initial order tool | Exists; specific authorization/missing-field tests pending 02 |
| Full ingestion schema/date validation | Partial |
| Persona, chat, multi-turn context, scope handling | Missing; checkpoint 03 |
| Local LLM and provider failure handling | Missing; checkpoint 04 |
| Five conversation examples | Missing; checkpoint 05 |
| Final submission PDF and complete interview documentation | Missing; checkpoint 06 |
| Windows batch execution | Not verified in this environment |
| Public GitHub repository | Not created or verified; candidate supplies real URL |
| Live AI behavior | Not tested; no provider adapter/model exists yet |

## Apply and validate on Windows

1. Back up any uncommitted changes. Do not delete your `.git` directory.
2. Extract the contents of this ZIP into `C:\Artefact\artefact-emporio`, replacing
   matching project files. Do not extract into another nested `artefact-emporio` folder.
3. Confirm that `C:\Artefact\artefact-emporio\pyproject.toml` exists.
4. Run in CMD:

```bat
cd /d C:\Artefact\artefact-emporio
python -m pip install -e .
python -m emporio.cli catalogo --categoria Violões --maximo 1000
python -m unittest discover -s tests -v
git status
git branch --show-current
git diff --stat
```

A virtual environment is recommended; README includes its activation commands.
Expected local result: 19 passing tests. This expectation is not a report of your
Windows execution.

## Candidate-controlled Git workflow

Review the diff before staging. Keep checkpoint ZIPs outside the repository.
Do not initialize a nested repository or replace an existing Git history.

```bat
git add -A
git commit -m "chore: establish validated project baseline"
git remote -v
git branch --show-current
```

If `origin` is configured and the current branch is correct, this command pushes the
current branch without assuming its name:

```bat
git push -u origin HEAD
```

If there is no configured remote, configure your actual repository URL first; do not
use a guessed URL. If Git reports no changes, do not create an empty checkpoint commit.

## Stop condition and next step

Stop here. After local extraction, testing and commit, the candidate says
**NEXT CHECKPOINT**. Only then begin Checkpoint 02: complete and validate operational
services, especially order isolation and missing tracking/delivery fields.

## Revision 01 — Windows subprocess encoding fix

Candidate Windows execution confirmed package installation, catalog output and all
15 original tests. The three CLI tests failed with UnicodeDecodeError: their reader
used UTF-8 while the child Python process emitted a Windows legacy encoding.

`tests/test_cli.py` now explicitly sets `PYTHONIOENCODING=utf-8` in the child
process environment, matching the existing UTF-8 reader. It preserves other environment
variables. No business rule or original test was changed. One regression test inherits
cp1252 and checks exact accented source strings after the child override.

Validation: `python -m unittest discover -s tests -v` — 19 tests, OK.
Also run under inherited `PYTHONIOENCODING=cp1252`: 19 tests, OK.
These revised runs are Linux verification of the encoding contract; Windows rerun
remains pending. Revised archive: `01-foundation-and-baseline-fixed.zip`.
Extract directly into the existing project. No Git metadata, secrets or extra parent
folder is included. No commit or push performed. If the baseline is not committed yet,
use its original commit message. Otherwise use:
`fix: align CLI subprocess encoding across platforms`.
