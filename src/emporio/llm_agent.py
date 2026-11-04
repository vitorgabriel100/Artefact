"""Combine deterministic tools with a local model that only phrases their evidence."""

import json
from pathlib import Path

from .chat import OfflineAgent
from .llm import OllamaChatProvider, ProviderError, SYSTEM_INSTRUCTIONS


class GroundedLocalAgent:
    """Use the existing allowlisted router first; never let the model call tools."""

    def __init__(self, data_dir: Path, customer_id: int | None = None,
                 provider: OllamaChatProvider | None = None):
        self.offline = OfflineAgent(data_dir, customer_id)
        self.provider = provider or OllamaChatProvider.from_environment()
        self.history: list[dict[str, str]] = []

    def respond(self, message: str) -> str:
        """Retrieve verified facts, then ask Ollama to write a grounded answer."""
        deterministic_answer = self.offline.respond(message)
        trace = self.offline.trace

        # Sem evidência de uma consulta permitida, preservamos a resposta de escopo
        # determinística; não pedimos ao LLM para responder usando conhecimento geral.
        if not trace:
            self._remember(message, deterministic_answer)
            return deterministic_answer

        evidence = self._evidence(trace)
        # A resposta determinística de referência permite comparar o estilo sem dar
        # ao modelo acesso ao restante do banco ou a um histórico amplo.
        current = (
            f"Customer message:\n{message}\n\n"
            f"Verified tool results (JSON):\n{json.dumps(evidence, ensure_ascii=False, indent=2)}\n\n"
            f"Deterministic reference answer:\n{deterministic_answer}\n\n"
            "Write a natural customer-facing answer using only the verified results."
        )
        messages = [*self.history[-6:], {'role': 'user', 'content': current}]
        answer = self.provider.respond(SYSTEM_INSTRUCTIONS, messages)
        self._remember(message, answer)
        return answer

    @staticmethod
    def _evidence(trace: list[dict]) -> list[dict]:
        """Keep only results from the current allowlisted calls; no database dumps."""
        evidence = []
        for call in trace[:4]:
            result = call['result']
            if call['tool'] == 'search_policies':
                # O índice contém texto apenas das páginas recuperadas nesta consulta.
                evidence.append({'tool': call['tool'], 'pages': result.get('pages', [])})
            else:
                evidence.append({'tool': call['tool'], 'result': result})
        return evidence

    def _remember(self, user_message: str, answer: str) -> None:
        """Retain only the last three exchanges in this process's memory."""
        self.history.extend([
            {'role': 'user', 'content': user_message[:2000]},
            {'role': 'assistant', 'content': answer[:2000]},
        ])
        self.history = self.history[-6:]


def run_local_chat(data_dir: Path, customer_id: int | None = None) -> None:
    """Run the Ollama-backed mode without silently switching to offline mode."""
    agent = GroundedLocalAgent(data_dir, customer_id)
    print(f'Empório da Música | LOCAL LLM: Ollama model {agent.provider.model}.')
    print('Requires Ollama running locally and the selected model downloaded.')
    print('Answers with no retrieved evidence use the deterministic scope response.')
    if customer_id is not None:
        print(f'DEMO customer session #{customer_id}; simulated identity, not authentication.')
    print('Ask about instruments, orders or policies. Type exit or quit to leave.')
    while True:
        try:
            message = input('You: ')
            if message.strip().lower() in ('exit', 'quit', 'sair'):
                break
            try:
                answer = agent.respond(message)
            except ProviderError as error:
                # Não expõe traceback nem diz que a resposta offline veio do LLM.
                print(f'Assistant: Local model unavailable: {error}')
                continue
            print('Assistant: ' + answer)
        except (EOFError, KeyboardInterrupt):
            break
    print('\nThanks for visiting Empório da Música!')
