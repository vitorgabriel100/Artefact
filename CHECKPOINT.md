# Checkpoint 03 — Offline conversational assistant

## Implemented

Added `src/emporio/chat.py`: deterministic intent routing, readable product prices,
policy translations with retrieved page references, session product selection and
last accessible order. Added chat CLI mode and an explicitly simulated customer flag.
Updated `start_windows.bat` to launch chat. Added `tests/test_chat.py` (10 tests).
Updated README and architecture. Archived checkpoint 02 in docs/CHECKPOINT_02.md.
Existing source records and previous 30 tests remain unchanged. No new dependencies.

## Actual validation

`python -m unittest discover -s tests -v`: 40 tests, OK, Linux/Python 3.12.
Tests cover budget search, ambiguous references, first-product selection, PIX follow-up,
specific/missing models, discontinued stock, policy topics and page references,
combined order/return requests, order isolation, unsupported requests, input limits,
and a real CLI subprocess greeting/exit. An initial missing accessories routing term
was found by the suite and fixed before delivery. Windows execution remains pending.

## Usage

```bat
cd /d C:\Artefact\artefact-emporio
python -m pip install -e .
python -m unittest discover -s tests -v
python -m emporio.cli chat --mode offline
```

Try: `Show acoustic guitars under BRL 1000`, `the first one`, `and with PIX?`,
`What is your address and opening hours?`, then `exit`.

For an explicitly simulated identity using fictional supplied data:

```bat
python -m emporio.cli chat --mode offline --demo-customer-id 3
```

Try `Can I return order 1?`. The assistant queries order and policy, asks for purchase
channel and actual receipt date, and does not approve eligibility.

## Limits

This is rules/templates, not LLM inference. English output, limited Portuguese input
aliases. It does not understand arbitrary paraphrases. Follow-ups retain product IDs
and the last accessible order only, not a full dialogue history. Return eligibility
is not evaluated from subsequent free-text dates. Model-code and category search are
supported; brand-only search, general specifications and alternate-product suggestions
need further work. Simple numeric budget formats only. Policy translations are static
reviewed templates, checked for page availability against the hash-validated index;
manual changes require reviewing templates as well as rebuilding the index.
The demo customer flag is not authentication. No remote service or write action exists.

## Delivery and Git

Extract the complete archive directly into C:\Artefact\artefact-emporio.
No enclosing folder, Git metadata, credentials, environments or other ZIPs included.
No deletions required; preserve your local edits before replacing matching files.
No commit/push was performed here. Existing uncommitted work was preserved.

```bat
git status
git diff --stat
git add -A
git commit -m "feat: implement offline conversational assistant"
```

If origin is configured, `git push -u origin HEAD` pushes the current branch.
Stop here. After local validation and commit, say NEXT CHECKPOINT to start 04.
