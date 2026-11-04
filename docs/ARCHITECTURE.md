# Architecture — Checkpoint 02

## Existing data flow

The CLI selects a deterministic operation. Catalog operations create a SQLite snapshot
from the six supplied CSVs, execute parameterized queries, apply business rules in
Python, serialize results and close the database. Policy operations validate the PDF
hash, search indexed pages and return text with source references.

| Module | Responsibility | Status |
|---|---|---|
| `catalog.py` | CSV loading, relations, search, availability, prices | Existing baseline tested |
| `policies.py` | Hash verification and bilingual lexical page retrieval | Baseline tested; broader recall not evaluated |
| `config.py` | Editable-install data path and environment override | CLI path regression tested |
| `cli.py` | English commands and legacy aliases | Tested |
| `tools.py` | Allowlist, parameter validation, session-scoped orders | Validated: ownership, missing data, input and privacy tests |
| `scripts/build_policy_index.py` | Rebuild text index from PDF | Existing script, optional PyMuPDF dependency |

## Intended completion path

Keep these modules. Add a bounded in-memory conversational session and deterministic
offline routing in Checkpoint 03. Add a small configurable LLM provider adapter in
Checkpoint 04, preferring local Ollama after checking model and hardware requirements.
Tool results remain authoritative for prices and availability. The LLM will receive
selected evidence to produce customer-friendly responses, not a database dump or an
unrestricted SQL interface. Offline output will be explicitly labeled as deterministic.

Checkpoint 03 implemented the deterministic offline router and bounded selection context.
No Streamlit application or production authentication is claimed.

## Why this is small

SQLite handles local relational data; the Python standard library handles money,
CLI parsing and tests. A short manual does not automatically justify embeddings or a
vector database. A CLI meets the interface requirement without a web deployment.

## Error boundaries

Invalid relationships fail ingestion. Missing products return `None`. Unknown policy
topics return no matching pages. A changed PDF invalidates its index. CLI exceptions
currently surface as developer errors; conversational recovery belongs to later stages.
The existing order tool filters ownership in SQL and closes its database per call.

## Checkpoint 03 implementation update

`chat.py` now implements the planned offline router and bounded selection context.
It calls ToolBox and renders exact price strings or reviewed policy templates after
retrieving the source page. The chat command supports exit, EOF and Ctrl+C.
The earlier intended-path section records the pre-chat design; offline routing is
implemented. Production authentication remains out of scope.

## Checkpoint 04 local LLM path

`llm_agent.py` runs the existing offline router and captures only the allowlisted tool
results from the current turn. It passes the customer message, up to three earlier
exchanges, and those results to `llm.py`. Retrieved policy page text is included only when
the policy search tool returns it. The model cannot execute tools, SQL, or mutations.
Its response is a presentation layer; prices, inventory, policies, and order ownership
remain controlled by Python tools. If no tool produced evidence, the deterministic
out-of-scope/greeting response is used without invoking the model.

`llm.py` calls Ollama's local `/api/chat` endpoint using `urllib`, JSON, and a bounded
timeout. There are no extra Python dependencies or API keys. Only localhost HTTP URLs are
accepted. `LLM_MODEL` defaults to `llama3.2:3b`, but must be downloaded separately. The
model/service was not available for a live run during this checkpoint; mocked tests cover
request construction, evidence injection, invalid/empty responses, and connection errors.
