"""Retrieve policy pages with bilingual aliases and preserved source text."""

import hashlib
import json
import re
from pathlib import Path

from .catalog import normalize

STOP_WORDS = set(
    'a o as os de da do das dos e em um uma para por que qual quais posso como minha meu '
    'i a an the is are can my your me what how where when do does to of for and please'.split()
)
# O manual é português; aliases permitem consultas curtas em inglês sem embeddings.
# Trata-se de vocabulário de busca, não de uma cópia paralela das regras comerciais.
QUERY_ALIASES = {
    'devolver': ['devolucao', 'arrependimento'],
    'devolucao': ['arrependimento'],
    'return': ['devolucao', 'arrependimento', 'trocas'],
    'returns': ['devolucao', 'arrependimento'],
    'refund': ['reembolso', 'arrependimento'],
    'exchange': ['trocas', 'preferencia'],
    'pagar': ['pagamento'], 'payment': ['pagamento'],
    'installments': ['parcelamento', 'parcela'], 'parcelar': ['parcelamento'],
    'hours': ['horario', 'funcionamento'], 'open': ['horario', 'funcionamento'],
    'abre': ['horario'], 'aberto': ['horario'], 'fechado': ['horario'],
    'address': ['endereco', 'rua'], 'endereco': ['rua'],
    'contact': ['telefone', 'whatsapp', 'email'], 'phone': ['telefone', 'whatsapp'],
    'defeito': ['garantia', 'trocas'], 'defect': ['defeito', 'garantia'],
    'warranty': ['garantia'], 'shipping': ['frete', 'entregas'],
    'delivery': ['entregas', 'prazo'], 'entrega': ['frete'],
    'tracking': ['rastreamento'], 'pix': ['pagamento', 'cumulatividade'],
    'discount': ['desconto', 'promocoes'], 'accessories': ['acessorios'],
    'privacy': ['privacidade', 'dados'], 'complaint': ['reclamacao'],
}


class Policies:
    """Verify the source hash and return evidence with page numbers."""

    def __init__(self, data_dir: Path):
        data_dir = Path(data_dir)
        self.index = json.loads((data_dir / 'policies_index.json').read_text(encoding='utf-8'))
        current = hashlib.sha256((data_dir / 'politicas_da_loja.pdf').read_bytes()).hexdigest()
        if current != self.index['sha256']:
            raise ValueError('The policy PDF changed. Rebuild the policy index before continuing.')

    def search(self, query: str, limit: int = 3) -> list[dict]:
        """Return matching pages and related pages needed to interpret the rules."""
        if not 1 <= limit <= 8:
            raise ValueError('limit must be between 1 and 8')
        words = set(re.findall(r'\w+', normalize(query))) - STOP_WORDS
        expanded = words | {alias for word in words for alias in QUERY_ALIASES.get(word, [])}
        ranked = []
        for page in self.index['pages']:
            tokens = set(re.findall(r'\w+', normalize(page['text'])))
            score = len(expanded & tokens)
            if score:
                ranked.append({**page, 'score': score, 'source': 'politicas_da_loja.pdf'})
        selected = sorted(ranked, key=lambda row: (-row['score'], row['page']))[:limit]
        # Regras atravessam páginas. Acrescentamos o par necessário explicitamente:
        # pagamentos/promoções, entrega local/outras cidades, garantia/trocas e contatos.
        related = set()
        if expanded & {'telefone', 'whatsapp', 'email'}:
            related.update({2, 6})
        if expanded & {'pix', 'pagamento', 'parcelamento', 'promocoes', 'desconto'}:
            related.update({3, 6})
        if expanded & {'frete', 'entregas', 'rastreamento'}:
            related.update({4, 5})
        if expanded & {'garantia', 'defeito'}:
            related.update({4, 7})
        existing = {page['page'] for page in selected}
        for page in self.index['pages']:
            if page['page'] in related - existing:
                selected.append({**page, 'score': 0, 'source': 'politicas_da_loja.pdf',
                                 'reason': 'Related policy context'})
        return selected
