# Checkpoint 05 — Tests and demonstration conversations

The five English conversations in [examples](examples/) record actual offline answers, tool arguments and evidence. The return example combines a session-scoped order lookup with page 4 of the store manual. Each scenario starts a new session.

The new regression test opens the CLI for each scenario, sends the published customer messages and compares every full answer. The 48 earlier tests remain in the suite.

Validation in Linux with Python 3.12 from the project root:

```sh
PYTHONPATH="$PWD/src" python -m unittest discover -s tests -v
```

Result: 49 tests passed. Live Ollama inference and Windows execution were not verified in this run. See the [manual checklist](docs/MANUAL_QA.md) for local verification.

Extract the archive into the parent of the existing artefact-emporio folder. Review the changes and commit this checkpoint separately. Suggested message: `test: expand coverage and add agent demonstrations`.
