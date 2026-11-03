"""Define allowed tools and validate arguments before accessing source data."""

from pathlib import Path
from typing import Any

from .catalog import Catalog
from .policies import Policies


def declaration(name: str, description: str, properties: dict, required=()) -> dict:
    """Build a tool declaration next to its implementation for easier review."""
    return {'name': name, 'description': description,
            'parameters': {'type': 'OBJECT', 'properties': properties, 'required': list(required)}}


TOOL_DECLARATIONS = [
    declaration('search_products',
        'Search the supplied product snapshot. Use short model/brand names in query; use category '
        'for instrument types. Returns prices in BRL, availability and promotions. '
        'For a specific product that may be unavailable, set available_only=false.', {
            'query': {'type': 'STRING', 'description': 'Short brand/model text; omit for broad searches.'},
            'category': {'type': 'STRING', 'description': 'Examples: acoustic guitars, guitars, basses, drums, keyboards, ukuleles.'},
            'max_price': {'type': 'NUMBER', 'description': 'Maximum final unit price in BRL.'},
            'available_only': {'type': 'BOOLEAN'},
            'payment': {'type': 'STRING', 'enum': ['table', 'pix']},
            'limit': {'type': 'INTEGER', 'description': 'Between 1 and 10.'},
        }),
    declaration('get_product', 'Get verified details and prices for a known product ID.', {
        'product_id': {'type': 'INTEGER'},
        'payment': {'type': 'STRING', 'enum': ['table', 'pix']},
    }, ['product_id']),
    declaration('search_policies',
        'Retrieve original policy pages for opening hours, address, payments, shipping, '
        'returns, warranty, promotions, privacy and scope. Query can be English or Portuguese. '
        'Cite returned page numbers and explain the policy in English.', {
            'query': {'type': 'STRING'},
        }, ['query']),
    declaration('get_order',
        'Look up one order belonging to the session customer. Identity is assigned by the '
        'application, never by chat text. An unavailable order must not reveal whether it exists.', {
            'order_id': {'type': 'INTEGER'},
        }, ['order_id']),
]


def public_product(product: dict | None) -> dict:
    """Convert cents to exact decimal strings so the model need not calculate prices."""
    if product is None:
        return {'found': False}
    result = dict(product)
    for field in ('table_price', 'final_price'):
        value = result.pop(field + '_cents')
        result[field + '_brl'] = f'{value // 100}.{value % 100:02d}'
    return {'found': True, **result}


class ToolBox:
    """Open SQLite per call to avoid sharing connections between sessions."""

    def __init__(self, data_dir: Path, customer_id: int | None = None):
        self.data_dir = Path(data_dir)
        # O identificador vem da configuração da sessão; não faz parte do schema do LLM.
        self.customer_id = customer_id
        self.policies = Policies(self.data_dir)

    def execute(self, name: str, arguments: dict[str, Any]) -> dict:
        """Validate an untrusted tool call before accessing the database."""
        try:
            self._validate(name, arguments)
            if name == 'search_policies':
                pages = self.policies.search(arguments['query'])
                return {'pages': pages, 'found': bool(pages)}
            catalog = Catalog(self.data_dir)
            try:
                if name == 'search_products':
                    products = catalog.search(**arguments)
                    return {'products': [public_product(p) for p in products],
                            'source': 'Supplied CSV snapshot; not a live inventory integration'}
                if name == 'get_product':
                    return public_product(catalog.product(**arguments))
                return self._order(catalog, arguments['order_id'])
            finally:
                catalog.close()
        except (ValueError, TypeError) as error:
            # Mensagens de validação são nossas; erros internos de banco não vão ao modelo.
            return {'error': str(error), 'recoverable': True}

    @staticmethod
    def _validate(name: str, arguments: dict) -> None:
        schema = next((tool['parameters'] for tool in TOOL_DECLARATIONS if tool['name'] == name), None)
        if schema is None:
            raise ValueError('Unknown tool. Use only the declared tools.')
        if not isinstance(arguments, dict):
            raise ValueError('Tool arguments must be a JSON object.')
        if set(arguments) - set(schema['properties']):
            raise ValueError('Unexpected tool arguments.')
        if set(schema['required']) - set(arguments):
            raise ValueError('Missing required tool arguments.')
        expected_types = {'STRING': str, 'INTEGER': int, 'BOOLEAN': bool, 'NUMBER': (int, float)}
        for key, value in arguments.items():
            rule = schema['properties'][key]
            if not isinstance(value, expected_types[rule['type']]):
                raise ValueError(f'Invalid type for {key}.')
            if rule['type'] in ('INTEGER', 'NUMBER') and isinstance(value, bool):
                raise ValueError(f'Invalid type for {key}.')
            if 'enum' in rule and value not in rule['enum']:
                raise ValueError(f'Invalid value for {key}.')
            if isinstance(value, str) and len(value) > 300:
                raise ValueError(f'{key} is too long.')
        if 'limit' in arguments and not 1 <= arguments['limit'] <= 10:
            raise ValueError('limit must be between 1 and 10.')
        for key in ('order_id', 'product_id'):
            if key in arguments and arguments[key] <= 0:
                raise ValueError(f'{key} must be positive.')

    def _order(self, catalog: Catalog, order_id: int) -> dict:
        """Filter the owner in SQL before constructing the order response."""
        if self.customer_id is None:
            return {'error': 'Order details require a customer session. Contact store staff for access.'}
        row = catalog.db.execute('''
            SELECT id, order_date, status, total, payment, tracking, estimated_delivery
            FROM orders WHERE id=? AND customer_id=?
        ''', (order_id, self.customer_id)).fetchone()
        if row is None:
            # Mesma resposta para ID inexistente e pedido de outro cliente.
            return {'found': False, 'message': 'This order is not available in this customer session.'}
        result = dict(row)
        amount = result.pop('total')
        result['total_brl'] = f'{amount // 100}.{amount % 100:02d}'
        result['items'] = [dict(item) for item in catalog.db.execute('''
            SELECT p.name, i.quantity FROM order_items i
            JOIN products p ON p.id=i.product_id WHERE i.order_id=?
        ''', (order_id,))]
        # Não há data real de recebimento nem canal da compra no material fornecido.
        result.update({'found': True, 'received_date': None, 'purchase_channel': None,
                       'source': 'Supplied CSV snapshot; delivery estimates may be historical'})
        return result
