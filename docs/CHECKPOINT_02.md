# Checkpoint 02 — Operational services

## Changes

Hardened `src/emporio/tools.py`: reject invalid session identities, blank queries,
non-finite or negative budgets before querying. Existing allowed tools, pricing,
policy retrieval and session-scoped order implementation are preserved.
Added `tests/test_tools.py` with 11 operational tests. Previous 19 tests unchanged.
Updated README and architecture status. Archived previous report in docs/CHECKPOINT_01.md.
No files removed, new dependencies, commits or pushes. Existing local branch: main;
uncommitted checkpoint-01 changes were preserved.

## Actual verification

`python -m unittest discover -s tests -v`: 30 tests, OK on Linux/Python 3.12.
Tests cover owned orders, unknown orders, wrong ownership, missing identity,
identity injection, missing shipping values, invalid arguments, exact product prices,
availability, policy sources and related pages. All original tests remain passing.

## Privacy and demonstration boundary

Customer ID is supplied by the application session, never a tool argument.
Unknown and unauthorized orders produce identical results. No customer email, phone,
address or internal notes are returned. This is authorization filtering, not real
identity authentication. The later local demo may assign a clearly labeled fictional
session; public production deployment requires actual authentication.

## Limitations

No conversational interface or LLM yet. No actual receipt date or purchase channel
exists in the supplied orders. Missing tracking and delivery remain null. Data is a
local snapshot, not live inventory. General schema/date validation and broader lexical
retrieval evaluation remain improvements; no policy eligibility approval is implemented.

## Apply and validate

Extract the complete ZIP directly into C:\Artefact\artefact-emporio.
It has no enclosing directory or .git, .env, virtual environment or nested archives.
No cleanup is required. Preserve local modifications before replacing matching files.

```bat
cd /d C:\Artefact\artefact-emporio
python -m pip install -e .
python -m unittest discover -s tests -v
git status
git diff --stat
git add -A
git commit -m "feat: complete catalog order and policy services"
```

Expected Windows result: 30 tests, OK; the revised suite was not run on Windows here.
If origin is configured, inspect `git branch --show-current` and use
`git push -u origin HEAD` to push the current branch.

Stop after this checkpoint. After local validation and commit, say NEXT CHECKPOINT
for the offline conversational assistant (03).
