"""Protect legacy commands and editable-install path resolution."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class CliCompatibilityTests(unittest.TestCase):
    def run_cli(self, *arguments, cwd=ROOT):
        # encoding no leitor não configura o processo filho. Ambos precisam concordar.
        child_environment = dict(os.environ, PYTHONIOENCODING='utf-8')
        completed = subprocess.run(
            [sys.executable, '-m', 'emporio.cli', *arguments],
            cwd=cwd, capture_output=True, text=True, encoding='utf-8', check=True,
            env=child_environment,
        )
        return json.loads(completed.stdout)

    def test_legacy_and_english_catalog_commands_match(self):
        legacy = self.run_cli('catalogo', '--categoria', 'Violões', '--maximo', '1000')
        english = self.run_cli('catalog', '--category', 'Violões', '--max-price', '1000')
        self.assertTrue(legacy)
        self.assertEqual(legacy, english)

    def test_legacy_product_and_policy_commands_match(self):
        self.assertEqual(self.run_cli('produto', '90', '--pagamento', 'pix'),
                         self.run_cli('product', '90', '--payment', 'pix'))
        self.assertEqual(self.run_cli('politica', 'return'), self.run_cli('policy', 'return'))

    def test_data_resolution_outside_project_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            product = self.run_cli('product', '81', cwd=directory)
        self.assertEqual(product['product_id'], 81)
        self.assertEqual(product['table_price_cents'], 59990)

    def test_accented_output_with_inherited_windows_encoding(self):
        # Reproduz uma configuração legada herdada; o helper deve fixar UTF-8 no filho.
        with patch.dict(os.environ, {'PYTHONIOENCODING': 'cp1252'}):
            product = self.run_cli('product', '81')
        self.assertEqual(product['category'], 'Violões')
        self.assertIn('Violão', product['description'])
