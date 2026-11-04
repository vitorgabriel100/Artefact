"""Exercise the local provider boundary without requiring Ollama or network access."""

import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from emporio.llm import OllamaChatProvider, ProviderError, SYSTEM_INSTRUCTIONS
from emporio.llm_agent import GroundedLocalAgent

DATA = Path(__file__).resolve().parents[1] / 'data'


class FakeProvider:
    def __init__(self, answer='The verified answer.'):
        self.answer = answer
        self.system = None
        self.messages = None

    def respond(self, system, messages):
        self.system, self.messages = system, messages
        return self.answer


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def read(self):
        return json.dumps(self.payload).encode('utf-8')


class OllamaProviderTests(unittest.TestCase):
    def test_request_uses_chat_endpoint_json_and_timeout(self):
        provider = OllamaChatProvider('test:latest', timeout=17)
        with patch('emporio.llm.urlopen', return_value=FakeResponse(
                {'message': {'content': 'Hello'}})) as request:
            self.assertEqual(provider.respond('system', [{'role': 'user', 'content': 'hi'}]), 'Hello')
        req = request.call_args.args[0]
        body = json.loads(req.data.decode('utf-8'))
        self.assertEqual(req.full_url, 'http://localhost:11434/api/chat')
        self.assertEqual(body['model'], 'test:latest')
        self.assertEqual(body['messages'][0]['content'], 'system')
        self.assertFalse(body['stream'])
        self.assertEqual(request.call_args.kwargs['timeout'], 17)

    def test_provider_environment_defaults_are_local_and_configurable(self):
        with patch.dict(os.environ, {'LLM_PROVIDER': 'ollama', 'LLM_MODEL': 'custom:1b',
                                     'LLM_BASE_URL': 'http://127.0.0.1:1234', 'LLM_TIMEOUT': '9'}):
            provider = OllamaChatProvider.from_environment()
        self.assertEqual(provider.model, 'custom:1b')
        self.assertEqual(provider.endpoint, 'http://127.0.0.1:1234/api/chat')
        self.assertEqual(provider.timeout, 9)

    def test_rejects_remote_provider_url(self):
        with self.assertRaises(ValueError):
            OllamaChatProvider('model', 'https://example.com')

    def test_network_failure_is_actionable(self):
        with patch('emporio.llm.urlopen', side_effect=OSError('offline')):
            with self.assertRaisesRegex(ProviderError, 'Start Ollama'):
                OllamaChatProvider('model').respond('system', [])

    def test_invalid_and_empty_provider_responses_are_rejected(self):
        for payload in ({'message': {'content': '  '}}, {'other': 'value'}):
            with self.subTest(payload=payload), patch(
                    'emporio.llm.urlopen', return_value=FakeResponse(payload)):
                with self.assertRaises(ProviderError):
                    OllamaChatProvider('model').respond('system', [])


class GroundedAgentTests(unittest.TestCase):
    def test_provider_receives_only_retrieved_catalog_evidence(self):
        provider = FakeProvider()
        agent = GroundedLocalAgent(DATA, provider=provider)
        answer = agent.respond('How much is the Takamine GD20?')
        self.assertEqual(answer, 'The verified answer.')
        prompt = provider.messages[-1]['content']
        self.assertIn('Takamine GD20', prompt)
        self.assertIn('final_price_brl', prompt)
        self.assertIn('Never invent product names, prices, stock', provider.system)
        self.assertNotIn('customers.csv', prompt)

    def test_policy_result_includes_retrieved_page_text(self):
        provider = FakeProvider()
        agent = GroundedLocalAgent(DATA, provider=provider)
        agent.respond('What is your address?')
        prompt = provider.messages[-1]['content']
        self.assertIn('Rua 14 de Maio', prompt)
        self.assertIn('page', prompt.lower())

    def test_no_verified_result_does_not_call_model(self):
        provider = FakeProvider()
        agent = GroundedLocalAgent(DATA, provider=provider)
        answer = agent.respond('What is the weather tomorrow?')
        self.assertIn('instruments', answer)
        self.assertIsNone(provider.messages)


if __name__ == '__main__':
    unittest.main()
