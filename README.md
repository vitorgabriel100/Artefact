# Artefact Empório Agent

A Python customer-support prototype for the fictional Empório da Música store.
**Checkpoint 03:** deterministic offline chat and independently tested operational tools.
No API key, network call or model is required to run the assistant.

## Windows setup

Extract this archive directly into `C:\Artefact\artefact-emporio`.
The directory must contain `pyproject.toml`, `src`, `data` and `tests`.
Preserve your existing Git history and local changes. Python 3.11+ is required.

```bat
cd /d C:\Artefact\artefact-emporio
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -e .
python -m unittest discover -s tests -v
python -m emporio.cli chat --mode offline
```

Alternatively run setup_windows.bat, then start_windows.bat. The batch scripts have
not been executed on Windows in the development environment.

## Conversation

Try these in one session:

- Show acoustic guitars under BRL 1000
- Is that one available? (asks for clarification when multiple products were listed)
- The first one
- And with PIX?
- What is your address and opening hours?
- Do you sell cables?
- exit

A local fictional customer demonstration can use:

```bat
python -m emporio.cli chat --mode offline --demo-customer-id 3
```

Ask `Can I return order 1?`. The startup banner labels the identity as simulated.
Guests cannot retrieve orders. The ID is assigned by CLI configuration, never by chat.
This is not production authentication. Do not expose this demo as a public service.

## Existing developer commands

```bat
python -m emporio.cli catalog --category "acoustic guitars" --max-price 1000
python -m emporio.cli product 90 --payment pix
python -m emporio.cli policy "return purchase"
python -m emporio.cli catalogo --categoria Violões --maximo 1000
```

Legacy Portuguese aliases remain supported. Developer commands print JSON; fields
ending in `_cents` contain integer cents. Chat formats the tools' exact BRL strings.
Source names and documents remain in Portuguese; responses use English templates.
Data resolves relative to the editable installation. Use `--data PATH` before a
subcommand, or set the OS variable EMPORIO_DATA_DIR. No .env loader exists yet.

## Architecture and rationale

CLI → deterministic router → allowed tools → SQLite / policy pages → readable answer.
SQLite validates local relationships and parameterized queries isolate orders.
Decimal and integer cents calculate discounts. The model will not calculate prices.
The short policy manual uses lexical retrieval with bilingual aliases and page references,
without embeddings or a vector database. Chat keeps selected product IDs and the last
accessible order in memory. Exiting discards that context.

Policy responses are reviewed English templates accompanied by retrieved source pages.
They are not generated translations. Updating the manual requires reviewing those
translations as well as regenerating its hash-checked index.

See docs/ARCHITECTURE.md, docs/decisoes.md and CHECKPOINT.md for details.

## Testing and limitations

The complete suite has 40 passing tests in Linux/Python 3.12. Previous 30 tests remain
unchanged; 10 new tests cover conversation and terminal operation. No live LLM has
been implemented or tested. Windows validation of this checkpoint is still pending.
Offline rules support selected phrasing, not general language understanding. Brand-only
search and arbitrary specification queries are limited. Return follow-ups do not calculate
eligibility. Unknown facts are not invented. Data is a CSV snapshot, not live inventory.
No return approval, payment, reservation or complaint submission is performed.

Ollama integration is planned for checkpoint 04, after verifying its setup and hardware
requirements. Five demonstrations and final submission material follow in 05 and 06.

## AI assistant disclosure

OpenAI ChatGPT/Codex assisted with analysis, code drafting, debugging, documentation
and tests. Actual executions and candidate validation are tracked separately. Code is
not represented as entirely manually authored. The candidate reviews and commits each
checkpoint. No GitHub publication or submission has been performed by this checkpoint.

## Development and Git

Optional developer tools: `python -m pip install -e ".[dev]"`.
Rebuild the policy index from the project root with `python scripts/build_policy_index.py`.
Review templates and rerun tests after source changes. Runtime has no external dependencies.
Keep ZIPs, .env and environments out of Git. Use the commands in CHECKPOINT.md to commit
this actual stage. Preserve existing history and do not change the repository after submission.
