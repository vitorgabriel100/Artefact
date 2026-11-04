# Interview rehearsal

**Give a thirty-second overview.** I built a Python assistant for a music store. When a customer asks for a guitar under a budget, Python checks availability and computes the price. When they ask about a return, it retrieves the store policy. Both modes use that evidence. The optional local model turns it into a conversational answer.

**Why Python and SQLite?** Python was required and its standard library includes the CLI, HTTP client, decimal arithmetic and SQL database. SQLite lets me validate relationships and combine records locally. Rebuilding it for each call limits throughput.

**What is RAG here?** Retrieval-augmented generation supplies relevant source text with a model request. For a policy question, the app retrieves pages from the manual and includes them in the local model prompt. Offline mode uses the same retrieval with reviewed templates.

**Why skip embeddings?** Eight pages and a small set of common topics made keyword lookup and bilingual aliases easy to inspect. I would evaluate missed paraphrases on labeled questions before changing retrieval.

**How does the model access data?** Python selects and validates the operation, runs it and passes selected results to Ollama. The model receives evidence and conversation context. It has no SQL or tool execution interface.

**Why deterministic tools?** A price should be reproducible. Active promotions take priority. Otherwise PIX gives 5% off the regular price. The tool rounds to cents. For the GD20 this changes BRL 2199.00 to BRL 2089.05.

**How do you reduce hallucinations?** The prompt supplies exact amounts, policy pages and a reference answer. Requests without a tool trace use the deterministic response. Generated wording can still contain errors. I would evaluate factual claims against tool outputs before deployment.

**How does order access work?** The query binds both order and session customer IDs. The demo flag simulates identity. In production, a trusted authentication layer must set that ID.

**How do you handle missing data?** Order 1 is marked delivered, but its record lacks the actual receipt date and purchase channel. I ask the customer for both because the seven-day online withdrawal period starts at receipt.

**What happens if the model is unavailable?** A request timeout or connection error is reported in the terminal. The user can restart with offline mode. The automated provider tests exercise mock responses. The recorded examples exercise offline chat.

**What would you improve?** First measure accuracy on realistic paraphrases and verify real model output on target hardware. For deployment, authenticate customers, integrate live stock and give unresolved cases a handoff to staff.

**How did you use Codex?** Codex helped draft and refactor code, debug setup, write tests and document decisions. Each checkpoint has a distinct scope. The test suite and recorded tool results let a reviewer check the behavior against supplied data.
