# Artefact Empório Agent

A Python customer-support prototype for **Empório da Música**, a fictional musical
instrument store in Campo Grande, Brazil. Developed for the Artefact AI Engineer
technical challenge.

## Current status: Checkpoint 02 — Operational services

The deterministic tools work without an API key. This checkpoint provides catalog
search, verified prices and availability, CSV-to-SQLite ingestion, and policy page
retrieval. **It is not yet a conversational or LLM-powered assistant.**

Session-scoped order tools are validated with dedicated ownership, missing-data,
privacy and input-validation tests. They are callable Python services, not a public
CLI command or production authentication mechanism.

Read [CHECKPOINT.md](CHECKPOINT.md) for actual validation evidence and changed files.

## Requirements and Windows setup

- Python 3.11 or later; development checks use Python 3.12.
- No runtime dependencies, model downloads or API keys for this checkpoint.
- Git is needed for your own commits and GitHub publication.

Extract the **contents** of `02-operational-services.zip` directly into
`C:\Artefact\artefact-emporio`. The archive has no enclosing folder and contains no
`.git` directory. Preserve your existing `.git`, virtual environment and local secrets.
Back up uncommitted local changes before overwriting matching project files.

In Windows CMD:

```bat
cd /d C:\Artefact\artefact-emporio
dir pyproject.toml
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -e .
python -m emporio.cli catalog --category "acoustic guitars" --max-price 1000
python -m unittest discover -s tests -v
```

Alternatively, run `setup_windows.bat` to create the virtual environment and install
the project. `start_windows.bat` displays available commands; it does not start a chat.

**If pip cannot find `pyproject.toml`, you are in the wrong folder.** The correct
folder contains `pyproject.toml`, `src`, `data` and `tests` together.

## Available commands

```bat
python -m emporio.cli --help
python -m emporio.cli catalog --category "acoustic guitars" --max-price 1000
python -m emporio.cli product 90 --payment pix
python -m emporio.cli policy "Can I return my purchase?"
```

The original Portuguese commands remain supported:

```bat
python -m emporio.cli catalogo --categoria Violões --maximo 1000
python -m emporio.cli produto 90 --pagamento pix
python -m emporio.cli politica "posso devolver uma compra?"
```

The CLI prints JSON for development inspection. Monetary fields ending in `_cents`
are integer cent values; `59990` means BRL 599.90. Original product names and policy
text remain in Portuguese, unchanged from the source. English customer-facing
conversation will be introduced in later checkpoints.

Data paths resolve relative to the editable installation, not the current terminal
folder. Override them with `--data PATH` before the subcommand or the operating-system
variable `EMPORIO_DATA_DIR`. This checkpoint does not read `.env` files.

## Architecture and decisions

1. `Catalog` loads the six CSVs into an in-memory SQLite database.
2. Primary keys, foreign keys, checks and a unique active-promotion index validate
   structural relationships. Loading fails rather than returning a partial snapshot.
3. Parameterized queries retrieve products. Python computes discounts with Decimal
   and integer cents. Availability requires active status and positive stock.
4. `Policies` searches a prebuilt, hash-checked PDF text index and returns page numbers.
5. The CLI presents these deterministic results. A future agent will call allowed
   tools instead of generating unrestricted SQL.

The data is a supplied **snapshot**, not a live store integration. The implementation
uses all six tables but does not send a customer list to a model.

See [architecture](docs/ARCHITECTURE.md), [decisions](docs/decisoes.md), and
[checkpoint roadmap](docs/ROADMAP.md).

## Testing

```bat
python -m unittest discover -s tests -v
```

The 15 original tests are preserved unchanged. Four additional tests protect English
and Portuguese CLI compatibility path resolution outside the project directory, and UTF-8 output capture when a legacy
Windows encoding is inherited.
Tests require no provider or network. Installation may need network access to obtain
setuptools if it is not already available.

To regenerate the policy index after intentionally changing the PDF, install the
optional development dependencies and run from the project root:

```bat
python -m pip install -e ".[dev]"
python scripts/build_policy_index.py
```

Review the regenerated index and rerun tests before committing it.

## Known limitations

- No chat loop, conversation memory, persona or out-of-scope conversational handling yet.
- No real LLM adapter or live model verification yet. Ollama is the preferred next
  integration target; no model or hardware availability is assumed.
- Order authorization filtering is tested; real identity authentication is not implemented.
- Ingestion validates key relationships and basic numeric constraints, but does not yet
  provide a comprehensive schema/date validation report.
- Retrieval is lexical and page-based, with a small bilingual vocabulary. There are no
  embeddings, relevance benchmarks, or guarantees that every phrasing will retrieve well.
- Policy ambiguities must not be turned into unsupported promises.
- Only editable source installation is supported; data is not bundled into a standalone wheel.
- Windows scripts are provided but have not been executed on Windows in this environment.

## AI coding assistant disclosure

OpenAI ChatGPT/Codex assisted with source inspection, implementation suggestions,
code drafting, debugging, documentation and automated tests. The development process
uses incremental checkpoints and actual test execution. Candidate review and Windows
validation are recorded only when confirmed by the candidate. AI-generated code is
not presented as entirely manually authored.

## Git and delivery

This checkpoint ZIP intentionally excludes Git metadata. It must not replace your
existing repository history. No commit or push is performed automatically for this
checkpoint. Review changes, test locally, and commit only the validated changes:

```bat
git status
git branch --show-current
git diff --stat
git add -A
git commit -m "chore: establish validated project baseline"
```

Push to your actual branch and configured remote; see CHECKPOINT.md. Do not upload
ZIPs, `.env`, or virtual environments. Do not change the repository after submission.

Checkpoint 02 adds 11 operational tests: the complete suite now has 30 passing tests.
