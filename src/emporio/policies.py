"""Baseline lexical de políticas com rastreabilidade ao PDF."""
import hashlib
import json
import re
from pathlib import Path
from .catalog import normalize

STOP = set('a o as os de da do das dos e em um uma para por que qual quais posso como minha meu'.split())
EXPANSIONS = {'devolver':['devolucao','arrependimento'], 'devolucao':['arrependimento'],
              'pagar':['pagamento'], 'parcelar':['parcelamento'], 'abre':['horario'],
              'aberto':['horario'], 'fechado':['horario'], 'endereco':['rua'],
              'defeito':['garantia','trocas'], 'entrega':['frete'], 'pix':['pagamento','cumulatividade']}


class Policies:
    def __init__(self, data_dir):
        data_dir = Path(data_dir)
        self.index = json.loads((data_dir / 'policies_index.json').read_text(encoding='utf-8'))
        current = hashlib.sha256((data_dir / 'politicas_da_loja.pdf').read_bytes()).hexdigest()
        if current != self.index['sha256']:
            raise ValueError('PDF alterado; regenere o índice de políticas')

    def search(self, query, limit=3):
        if not 1 <= limit <= 8:
            raise ValueError('limit deve estar entre 1 e 8')
        words = set(re.findall(r'\w+',normalize(query))) - STOP
        expanded = words | {v for word in words for v in EXPANSIONS.get(word,[])}
        ranked = []
        for page in self.index['pages']:
            tokens = set(re.findall(r'\w+',normalize(page['text'])))
            score = len(expanded & tokens)
            if score:
                ranked.append({'page':page['page'], 'text':page['text'], 'score':score,
                               'source':'politicas_da_loja.pdf'})
        return sorted(ranked,key=lambda r:(-r['score'],r['page']))[:limit]
