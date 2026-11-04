"""Record five reproducible demonstrations through the same agent used by the CLI."""

import json
from pathlib import Path

from emporio.chat import OfflineAgent

ROOT = Path(__file__).resolve().parents[1]

# Cada cenário começa com uma sessão nova. Dentro dele, as perguntas compartilham contexto.
SCENARIOS = [
    ('01-product-search', 'Find available acoustic guitars below BRL 1,000.',
     ['Show available acoustic guitars under BRL 1000.'],
     'products.csv, categories.csv and promotions.csv',
     'The search excludes unavailable products and applies a strict upper price bound. The chat displays up to five matches.'),
    ('02-product-price-and-stock', 'Check a named instrument and its price when paying by PIX.',
     ['How much is the Takamine GD20?', 'And with PIX?'],
     'products.csv and promotions.csv',
     'The second turn reuses the selected product ID. The pricing tool computes the discount and returns the exact amount in BRL.'),
    ('03-store-information', 'Find the address and normal opening hours.',
     ['What is your address and opening hours?'],
     'politicas_da_loja.pdf, page 2',
     'The assistant retrieves policy pages before showing the reviewed English text. Special opening hours require staff confirmation.'),
    ('04-return-and-order-policy', 'Assess what the store can tell a customer about returning an order.',
     ['I changed my mind. Can I return order 1?'],
     'orders.csv, order_items.csv, products.csv and politicas_da_loja.pdf, page 4',
     'The order lookup is scoped to simulated customer 3. The estimated delivery date cannot establish the withdrawal deadline. The agent requests the purchase channel and actual receipt date.'),
    ('05-out-of-scope-and-followup', 'Resolve a product reference and handle an unsupported accessory.',
     ['How much is the Takamine GD20?', 'Is that one available?', 'Do you sell cables?'],
     'products.csv, promotions.csv and politicas_da_loja.pdf, page 2',
     'The follow-up uses the selected model. The accessory question switches to the store policy on which items it sells.'),
]


def record_examples(destination: Path) -> None:
    """Capture actual answers and tool arguments without copying raw customer records."""
    destination.mkdir(parents=True, exist_ok=True)
    for slug, objective, questions, sources, explanation in SCENARIOS:
        customer = 3 if slug.startswith('04-') else None
        agent = OfflineAgent(ROOT / 'data', customer)
        lines = [f'# {objective}', '', 'Mode: offline (deterministic).',
                 f'Session: {"simulated customer 3" if customer else "guest"}.', '']
        for question in questions:
            answer = agent.respond(question)
            lines.extend(['**Customer**', '', question, '', '**Assistant**', '', answer, '',
                          '**Tools called during this turn**', ''])
            for call in agent.trace:
                arguments = json.dumps(call['arguments'], ensure_ascii=False, sort_keys=True)
                lines.append(f"- `{call['tool']}({arguments})`")
            lines.append('')
        lines.extend(['## Evidence', '', sources, '', explanation, ''])
        (destination / f'{slug}.md').write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    record_examples(ROOT / 'examples')
