# Manual checks on Windows

From the directory containing pyproject.toml, run `python -m pip install -e .`.

- [ ] Run `python -m unittest discover -s tests -v`. Expect 49 tests and OK.
- [ ] Start `python -m emporio.cli chat --mode offline`. Ask “Show available acoustic guitars under BRL 1000.” Expect five available models beginning with the Tagima Memphis at BRL 429.90.
- [ ] Ask “How much is the Takamine GD20?” and then “And with PIX?” Expect BRL 2199.00 and BRL 2089.05 respectively.
- [ ] Ask “What is your address and opening hours?” Confirm both answers cite page 2.
- [ ] Ask “order 1” as a guest. Expect a request for a customer session. Type exit.
- [ ] Start `python -m emporio.cli chat --mode offline --demo-customer-id 3`. Ask “Can I return order 1?” Expect the recorded order status and a question about the channel and receipt date.
- [ ] If Ollama is running with the configured model, start `python -m emporio.cli chat --mode local-llm`. Ask the same Takamine question. Compare the reported price and availability to the offline result. Record the model name and actual response separately.

The five checked-in examples use offline mode. Run `python scripts/record_examples.py` after installation to regenerate them from the current source data.
