# Artefact Empório Agent

A Python customer-support prototype for the fictional Empório da Música store.
**Checkpoint 04:** deterministic offline chat plus an optional Ollama local LLM that
phrases verified tool results. No paid provider key is required. Offline mode remains
available without Ollama.

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

## Optional local LLM

Install Ollama for Windows, start its local service, and download the documented default
model. The model is configurable; the application does not assume it is installed.

```bat
ollama pull llama3.2:3b
set "LLM_PROVIDER=ollama"
set "LLM_MODEL=llama3.2:3b"
set "LLM_BASE_URL=http://localhost:11434"
set "LLM_TIMEOUT=60"
python -m emporio.cli chat --mode local-llm
```

The LLM mode contacts only a local HTTP Ollama endpoint. The Python client uses the
standard library, sends one non-streaming `/api/chat` request per turn with verified tool
evidence, and does not enable model tool execution. Product/order/policy retrieval still
runs through the existing deterministic router and allowlisted tools. If that router
finds no evidence, the assistant returns its deterministic scope response without asking
the model. A model/service failure is reported explicitly; it is not silently relabelled
as an LLM answer. Order lookups still require the simulated CLI customer ID.

Set variables in the same Windows terminal before running the command. The project does
not load `.env` files. `LLM_TIMEOUT` defaults to 60 seconds and can be set from 1 to 180.
`LLM_BASE_URL` is restricted to localhost so customer messages and demo orders are not
sent to a remote host. No `LLM_API_KEY` is used or needed for local Ollama.

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

The complete suite has 48 passing tests on Linux/Python 3.12, including 8 provider
boundary tests. A real Ollama service/model was not available for live verification in
the development environment, and Windows validation remains pending. Prompt instructions
reduce unsupported claims but cannot guarantee model output; review generated answers
before any production use.
Offline rules support selected phrasing, not general language understanding. Brand-only
search and arbitrary specification queries are limited. Return follow-ups do not calculate
eligibility. Unknown facts are not invented. Data is a CSV snapshot, not live inventory.
No return approval, payment, reservation or complaint submission is performed.

The default `llama3.2:3b` tag is available in Ollama's model library. Choose a different
model if your machine needs a smaller one; performance depends on the available hardware.
Five demonstrations and final submission material follow in checkpoints 05 and 06.

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
