# Empório da Música | Customer support assistant

A customer can ask about instruments, prices, orders and store policies in an English terminal chat. The Artefact challenge supplies a fictional store's CSV records and a Portuguese policy manual. The prototype helps staff answer repeated questions while keeping each answer tied to a product record, an accessible order or a page in the manual.

## Run on Windows

Use Python 3.11 or later. From a clone, open Command Prompt in the folder containing `pyproject.toml`. If using the checkpoint ZIP, extract into `C:\Artefact` and open `C:\Artefact\artefact-emporio`. Keep the data directory alongside the source for the editable installation.

```bat
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -e .
python -m emporio.cli chat --mode offline
```

Ask `Show acoustic guitars under BRL 1000`, then `the first one` and `and with PIX?`. Type `exit` to leave. The default mode uses reviewed English templates and runs locally without a key. The batch files setup_windows.bat and start_windows.bat provide the same offline entry point.

## Run with a local model

Install and start Ollama separately. Run these commands in the activated environment. A first-time model download requires internet access.

```bat
ollama pull llama3.2:3b
python -m emporio.cli chat --mode local-llm
```

Ask `How much is the Takamine GD20?` to exercise retrieval and generation. Compare the answer with [the recorded price example](examples/02-product-price-and-stock.md). Greetings and unsupported requests use the deterministic response. If generation fails, chat displays the provider error. To continue with templates, exit and start offline mode.

| OS variable | Default | Purpose |
|---|---|---|
| LLM_PROVIDER | ollama | Supported provider |
| LLM_MODEL | llama3.2:3b | An installed local model tag |
| LLM_BASE_URL | http://localhost:11434 | Local Ollama server address |
| LLM_TIMEOUT | 60 | Request timeout in seconds, from 1 to 180 |
| EMPORIO_DATA_DIR | Project data directory | Override the supplied snapshot location |

Use `set "LLM_MODEL=your-installed-tag"` in Windows CMD to choose a model. The application reads the process environment. The commented .env.example documents the settings.

## Where answers come from

Python routes supported questions to four allowlisted operations. Catalog and order queries use SQLite. Policy questions retrieve numbered PDF pages. The offline chat presents tool results directly. Local LLM mode passes the question, recent context, selected results and an English reference answer to Ollama for wording. Its system instructions require exact prices, source pages and acknowledgement of missing evidence.

| Operation | Evidence and business rule |
|---|---|
| search_products | Filters category and budget. An available product must be active and have positive stock. |
| get_product | Returns model details and computed prices. An active promotion takes priority over the 5% PIX discount. Decimal arithmetic rounds to whole cents. |
| get_order | Filters the order by both order ID and session customer ID in a parameterized query. |
| search_policies | Matches normalized words and bilingual aliases against the page index. Some topics also retrieve related pages. A source hash detects changes to the PDF. |

Six CSV files populate an in-memory relational database with integrity checks. Each data tool opens and closes its own snapshot. This keeps the setup small and makes repeated database loading an explicit cost. Policy templates are reviewed English translations. Updating the PDF requires rebuilding its index and reviewing those templates.

Start a fictional customer session with `python -m emporio.cli chat --mode offline --demo-customer-id 3`. Ask `Can I return order 1?`. The session supplies the owner ID. Guests cannot inspect orders. A production service would need authenticated identities and access controls around the source files themselves.

## Verification and demonstrations

Run `python -m unittest discover -s tests -v` from the installed checkout. The final Linux validation covers 49 tests including CLI replay of every published conversation. Provider tests use mocked HTTP responses. Windows validation of the final package and live generation with a downloaded model require a local run.

1. [Find available guitars under BRL 1,000](examples/01-product-search.md)
2. [Check the Takamine GD20 and its PIX price](examples/02-product-price-and-stock.md)
3. [Find the address and opening hours](examples/03-store-information.md)
4. [Combine a customer order with the return policy](examples/04-return-and-order-policy.md)
5. [Resolve a follow-up and handle an accessory request](examples/05-out-of-scope-and-followup.md)

All five conversations were recorded in offline mode. Each includes the tool calls and sources. See the [manual checks](docs/MANUAL_QA.md) for a repeatable local run.

## Design limits and next steps

The CLI, standard-library runtime and lexical search fit a small static dataset and an eight-page manual. Category and model routing supports selected phrases. The session remembers product selections and the last accessible order until exit. In LLM mode, up to three earlier exchanges are available for wording. A model can still introduce unsupported claims. A production version should evaluate paraphrase recall and factual accuracy, authenticate customers, connect live inventory, and escalate exceptions to staff. The prototype cannot reserve stock, approve returns or determine actual delivery dates.

[Architecture](docs/ARCHITECTURE.md) · [Decisions and source ambiguities](docs/DECISIONS.md) · [Interview guide](docs/INTERVIEW_GUIDE.md)

## Use of AI coding assistants

OpenAI Codex assisted with architecture suggestions, Python drafts, refactoring, debugging installation and CLI behavior, test development and English documentation. Work was split into reviewable checkpoints. Tool contracts, source records and replayed conversations provide checks on generated changes. Automated results are reported separately from candidate-side verification and live model evaluation.
