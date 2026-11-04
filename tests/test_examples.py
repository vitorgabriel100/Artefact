"""Replay the published examples so the documented conversations stay reproducible."""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ExampleTests(unittest.TestCase):
    def test_cli_reproduces_each_published_answer(self):
        examples = sorted((ROOT / 'examples').glob('*.md'))
        self.assertEqual(len(examples), 5)
        for example in examples:
            with self.subTest(scenario=example.stem):
                # Lemos as perguntas publicadas e comparamos cada resposta completa no terminal.
                turns = example.read_text(encoding='utf-8').split('**Customer**\n\n')[1:]
                questions, answers = [], []
                for turn in turns:
                    question, reply = turn.split('\n\n**Assistant**\n\n', 1)
                    questions.append(question)
                    answers.append(reply.split('\n\n**Tools called during this turn**', 1)[0])
                command = [sys.executable, '-X', 'utf8', '-m', 'emporio.cli', 'chat', '--mode', 'offline']
                if example.stem.startswith('04-'):
                    command.extend(['--demo-customer-id', '3'])
                result = subprocess.run(command, cwd=ROOT, input='\n'.join([*questions, 'exit', '']),
                                        text=True, encoding='utf-8', capture_output=True, check=True)
                actual = [turn.split('\nYou: ', 1)[0] for turn in result.stdout.split('You: Assistant: ')[1:]]
                # O próximo prompt também delimita respostas compostas por múltiplos parágrafos.
                self.assertEqual([reply.rstrip('\n') for reply in actual], answers)
