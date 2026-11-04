# Checkpoint 04 — Grounded local LLM

## Implemented

Added `src/emporio/llm.py` as a small standard-library client for Ollama's local chat
API. Added `src/emporio/llm_agent.py` to feed it the customer's current message, a short
session context, and only verified results from the existing allowlisted tools. Retrieved
policy excerpts are passed only when returned by the policy search. The model only writes
customer-facing text; it cannot execute tools, SQL, prices, orders, or store actions.

Added the `local-llm` CLI mode and configuration through `LLM_PROVIDER`, `LLM_MODEL`,
`LLM_BASE_URL`, and `LLM_TIMEOUT`. Offline mode remains the default. Remote endpoints are
rejected to keep this no-key demo local. No new Python dependency or API key is required.
Added `tests/test_llm.py` with eight provider and grounding boundary tests. Checkpoint 03
is preserved in `docs/CHECKPOINT_03.md`.

## Validation status

`python -m unittest discover -s tests -v`: 48 tests passed on Linux/Python 3.12. The eight
new provider tests cover
request construction and timeout, environment configuration, rejection of remote URLs,
connection errors, invalid/empty responses, verified product/policy context, and no model
call when the deterministic router retrieves no evidence. A real Ollama installation and
model were not available for live verification here; Windows execution remains pending.

## Run locally on Windows

Install Ollama and let its local service start. Download the selected model, then run in
`C:\Artefact\artefact-emporio`:

```bat
ollama pull llama3.2:3b
set "LLM_PROVIDER=ollama"
set "LLM_MODEL=llama3.2:3b"
set "LLM_BASE_URL=http://localhost:11434"
set "LLM_TIMEOUT=60"
python -m emporio.cli chat --mode local-llm
```

The default model is configurable and is not assumed to be installed. Ollama's local
HTTP API requires no provider key. The CLI displays an explicit local-model error if the
service or model is unavailable; it does not silently label offline text as an LLM answer.
Use `--mode offline` when Ollama is not installed. Run the suite with:

```bat
python -m unittest discover -s tests -v
```

## Delivery and Git

Extract the complete archive directly into `C:\Artefact\artefact-emporio`, preserving the
existing `.git` directory and local history. This archive contains no Git metadata,
credentials, model weights or Python environment. Review the diff, run the tests, then
commit and push this checkpoint yourself:

```bat
git status
git diff --stat
git add -A
git commit -m "feat: integrate grounded llm response generation"
git push
```

This is an integration, not live-model validation. Record a live test only after running
one question through an installed local model.
