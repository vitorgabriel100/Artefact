"""Provide a bounded, explicitly deterministic conversational fallback."""

import re
from decimal import Decimal
from pathlib import Path

from .catalog import Catalog, normalize
from .tools import ToolBox

# Traduções revisadas das seções do manual; só são usadas após recuperar a página.
POLICY_ANSWERS = {
    'hours': (2, 'Normal opening hours: Monday-Friday 9 AM-6 PM; Saturday 9 AM-1 PM. '
              'Closed on Sundays and holidays. Special opening hours must be confirmed with staff.'),
    'address': (2, 'The store is at Rua 14 de Maio, 3200, Centro, Campo Grande, MS, CEP 79202-333.'),
    'payment': (3, 'The manual lists PIX, debit card, credit card and bank slips. PIX gives 5% off '
                'regular prices and cannot be combined with promotions. Bank slips may take up to '
                '3 business days to clear. Combined payment is allowed above BRL 2,000. '
                'Installment terms differ between the summary and section 3.1; confirm the '
                'applicable minimum with staff before committing to an installment plan.'),
    'return': (4, 'For online purchases, the manual allows withdrawal within 7 calendar days '
               'after receipt. It specifies original packaging, no signs of use, and all included '
               'accessories/manuals. Return shipping is paid by the store; reimbursement uses the '
               'original payment method within 10 business days. Was the purchase online, and '
               'when did you actually receive it? Approval requires reviewing the conditions.'),
    'exchange': (4, 'The manual allows preference exchanges within 7 days, subject to stock, '
                 'with the product in perfect condition and original packaging. Price differences '
                 'are charged or refunded. Customized and explicitly final-sale items have '
                 'restrictions. Staff must review eligibility.'),
    'warranty': (7, 'The manual distinguishes a 90-day legal warranty from receipt and a '
                 'manufacturer warranty whose terms depend on the product certificate. It also '
                 'describes manufacturing-defect exchanges within 30 days of purchase and '
                 'manufacturer support after that. Staff should review your specific case.'),
    'shipping': (4, 'In metropolitan Campo Grande, the manual states free delivery above BRL 500 '
                 'and BRL 35 below BRL 500, usually in 1-3 business days. Exactly BRL 500 is '
                 'not defined. Other cities require a shipping quote based on destination and '
                 'package details; large instruments may need a special quote. These are policy '
                 'estimates, not a promised delivery date.'),
    'accessories': (2, 'We specialize in musical instruments and do not sell cables, picks, '
                    'replacement strings, cases, pedals or amplifiers. I can help you find an instrument.'),
}
TOPICS = {
    'hours': ('hours', 'open', 'horario', 'abre'),
    'address': ('address', 'located', 'endereco'),
    'payment': ('payment', 'installment', 'boleto', 'parcel', 'pagamento'),
    'return': ('return', 'refund', 'changed my mind', 'devolver', 'arrepend'),
    'exchange': ('exchange', 'troca'),
    'warranty': ('warranty', 'defect', 'garantia', 'defeito'),
    'shipping': ('shipping', 'delivery cost', 'frete'),
    'accessories': ('accessories', 'cable', 'pick', 'replacement strings', 'case', 'pedal', 'amplifier', 'acessorio'),
}
CATEGORIES = {
    'acoustic guitar': 'Violões', 'violao': 'Violões', 'violoes': 'Violões',
    'electric guitar': 'Guitarras', 'guitar': 'Guitarras', 'guitarra': 'Guitarras',
    'bass': 'Baixos', 'baixo': 'Baixos', 'drum': 'Baterias', 'bateria': 'Baterias',
    'keyboard': 'Teclados', 'piano': 'Pianos', 'teclado': 'Teclados', 'ukulele': 'Ukuleles',
}


def has_phrase(text: str, phrase: str) -> bool:
    """Match whole words or phrase prefixes at word boundaries."""
    return bool(re.search(r'\b' + re.escape(phrase) + r'\w*\b', text))


class OfflineAgent:
    """Route supported requests to verified tools, retaining only recent selections."""

    def __init__(self, data_dir: Path, customer_id: int | None = None):
        self.tools = ToolBox(data_dir, customer_id)
        catalog = Catalog(data_dir)
        try:
            # Índice apenas de nomes/IDs; registros de clientes não entram no roteamento.
            self.names = [(r['id'], r['name']) for r in catalog.db.execute('SELECT id,name FROM products')]
        finally:
            catalog.close()
        self.product_ids: list[int] = []
        self.last_order_id: int | None = None
        self.trace: list[dict] = []

    def call(self, name: str, arguments: dict) -> dict:
        """Record the current turn's evidence for tests and later demonstrations."""
        result = self.tools.execute(name, arguments)
        self.trace.append({'tool': name, 'arguments': arguments, 'result': result})
        return result

    def policy(self, topic: str) -> str:
        """Render a reviewed translation only when its source page is available."""
        page, answer = POLICY_ANSWERS[topic]
        query = {'accessories': 'accessories', 'return': 'return purchase'}.get(topic, topic)
        evidence = self.call('search_policies', {'query': query})
        pages = {p['page'] for p in evidence.get('pages', [])}
        if page not in pages:
            return 'I could not verify the relevant policy. Please ask store staff.'
        return answer + f' [Store policy, page {page}]'

    def respond(self, message: str) -> str:
        """Handle one message without model inference, code execution or arbitrary SQL."""
        self.trace = []
        text = normalize(message.strip())
        if not text:
            return 'Please enter a question about instruments, orders or store policies.'
        if len(text) > 2000:
            return 'Please shorten your message to 2,000 characters.'
        if text in ('hi', 'hello', 'hey', 'oi', 'ola'):
            return 'Hi! Welcome to Empório da Música. What instrument or store information can I help with?'
        if text in ('thanks', 'thank you', 'obrigado'):
            return 'You are welcome! Let me know if you need anything else.'
        if any(x in text for x in ('ignore previous', 'system prompt', 'all customers', 'execute code', 'drop table')):
            return 'I can help with instruments, your accessible orders and store policies. Please ask a store-related question.'

        topics = [topic for topic, phrases in TOPICS.items() if any(has_phrase(text, p) for p in phrases)]
        order_match = re.search(r'\b(?:order|pedido)\s*#?\s*(\d+)\b', text)
        order_request = order_match or has_phrase(text, 'order') or has_phrase(text, 'pedido') or has_phrase(text, 'tracking')
        parts = []
        if order_request:
            order_id = int(order_match.group(1)) if order_match else self.last_order_id
            if order_id is None:
                parts.append('What is your order number? Order access also requires a customer session.')
            else:
                result = self.call('get_order', {'order_id': order_id})
                if result.get('found'):
                    self.last_order_id = order_id
                    parts.append(f"Order #{order_id}: {result['status']}. Tracking: {result['tracking'] or 'not provided'}. "
                                 f"Recorded estimated delivery: {result['estimated_delivery'] or 'not provided'}. "
                                 'This is the supplied snapshot, not a live delivery update. Actual receipt date is unknown.')
                else:
                    parts.append(result.get('error', result.get('message', 'Order information is unavailable.')))
        if topics:
            parts.extend(self.policy(topic) for topic in topics[:3])
            return '\n\n'.join(parts)
        if parts:
            return '\n\n'.join(parts)

        # Um código de modelo (ex.: GD20) é mais específico que palavras de cortesia.
        tokens = re.findall(r'[a-z0-9]+', text)
        model_tokens = [t for t in tokens if re.search('[a-z]', t) and re.search('[0-9]', t)]
        matches = [(pid, name) for pid, name in self.names if model_tokens and
                   all(t in re.findall(r'[a-z0-9]+', normalize(name)) for t in model_tokens)]
        if model_tokens and not matches:
            self.product_ids = []
            return 'I could not find that model in the supplied catalog. Please check the model name.'
        if not matches:
            matches = [(pid, name) for pid, name in self.names if normalize(name) in text]
        payment = 'pix' if has_phrase(text, 'pix') else 'table'
        if matches:
            ids = [pid for pid, _ in matches][:5]
        elif any(has_phrase(text, p) for p in ('that one', 'this one', 'first one', 'in stock', 'pix', 'available')) and self.product_ids:
            if 'first one' in text:
                ids = self.product_ids[:1]
            elif len(self.product_ids) == 1:
                ids = self.product_ids
            else:
                return 'Which model do you mean? Please give its name or say "the first one".'
        else:
            category = next((value for key, value in CATEGORIES.items() if has_phrase(text, key)), None)
            if category:
                arguments = {'category': category, 'limit': 5, 'payment': payment}
                budget = re.search(r'(?:under|below|up to|ate|budget(?: of)?)\s*(?:r\$|brl|\$)?\s*(\d+(?:[.,]\d+)?)', text)
                if budget:
                    raw = budget.group(1)
                    # Milhar em inglês e decimal em português são tratados explicitamente.
                    amount = raw.replace(',', '') if re.fullmatch(r'\d+,\d{3}', raw) else raw.replace(',', '.')
                    maximum = Decimal(amount)
                    if has_phrase(text, 'under') or has_phrase(text, 'below'):
                        maximum -= Decimal('0.01')
                    arguments['max_price'] = float(maximum)
                result = self.call('search_products', arguments)
                products = result.get('products', [])
                self.product_ids = [p['product_id'] for p in products]
                return self.format_products(products)
            if payment == 'pix':
                return self.policy('payment')
            return 'I can help with musical instruments, orders and store policies. Try "acoustic guitars under BRL 1000" or a specific model name.'
        self.product_ids = ids
        products = [self.call('get_product', {'product_id': pid, 'payment': payment}) for pid in ids]
        return self.format_products(products)

    @staticmethod
    def format_products(products: list[dict]) -> str:
        """Display exact tool-provided prices without recomputing discounts."""
        if not products:
            return 'No matching available instruments were found. Try another category or budget.'
        lines = []
        for product in products:
            availability = 'available' if product['available'] else product['unavailable_reason'].replace('_', ' ')
            line = f"- {product['name']}: BRL {product['final_price_brl']} — {availability}"
            if product['discount_percent']:
                line += f" (regular BRL {product['table_price_brl']}; {product['discount_percent']}% {product['discount_source']} discount)"
            lines.append(line)
        return '\n'.join(lines) + '\nSource: supplied product snapshot. Prices do not reserve stock.'


def run_chat(data_dir: Path, customer_id: int | None = None) -> None:
    """Run an interactive terminal session and exit cleanly on EOF or interruption."""
    agent = OfflineAgent(data_dir, customer_id)
    print('Empório da Música | OFFLINE: deterministic rules and templates; no LLM inference.')
    if customer_id is not None:
        print(f'DEMO customer session #{customer_id}; simulated identity, not authentication.')
    print('Ask about instruments, orders or policies. Type exit or quit to leave.')
    while True:
        try:
            message = input('You: ')
            if message.strip().lower() in ('exit', 'quit', 'sair'):
                break
            print('Assistant: ' + agent.respond(message))
        except (EOFError, KeyboardInterrupt):
            break
    print('\nThanks for visiting Empório da Música!')
