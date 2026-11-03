"""Exercise operational tools with real supplied records and adversarial arguments."""
import csv
import unittest
from pathlib import Path
from emporio.tools import ToolBox

DATA = Path(__file__).resolve().parents[1] / 'data'

class OperationalTests(unittest.TestCase):
    def setUp(self):
        self.tools = ToolBox(DATA, customer_id=3)

    def test_owned_order(self):
        order = self.tools.execute('get_order', {'order_id': 1})
        self.assertTrue(order['found'])
        self.assertEqual(order['status'], 'delivered')
        self.assertEqual(order['total_brl'], '11499.00')
        self.assertTrue(order['items'])
        self.assertFalse({'email', 'phone', 'customer_id', 'notes'} & order.keys())
        self.assertIsNone(order['received_date'])
        self.assertIsNone(order['purchase_channel'])

    def test_wrong_owner_and_unknown_order_are_indistinguishable(self):
        self.assertEqual(self.tools.execute('get_order', {'order_id': 2}),
                         self.tools.execute('get_order', {'order_id': 9999}))

    def test_guest_cannot_read_orders(self):
        self.assertIn('error', ToolBox(DATA).execute('get_order', {'order_id': 1}))

    def test_identity_cannot_be_injected_in_arguments(self):
        self.assertIn('error', self.tools.execute('get_order', {'order_id': 2, 'customer_id': 7}))

    def test_missing_shipping_is_preserved(self):
        with (DATA / 'orders.csv').open(encoding='utf-8-sig', newline='') as stream:
            rows = [r for r in csv.DictReader(stream) if not r['tracking_code']]
        self.assertTrue(rows)
        for row in rows:
            with self.subTest(order_id=row['order_id']):
                result = ToolBox(DATA, int(row['customer_id'])).execute('get_order', {'order_id': int(row['order_id'])})
                self.assertTrue(result['found'])
                self.assertIsNone(result['tracking'])
                self.assertEqual(result['estimated_delivery'], row['estimated_delivery'] or None)

    def test_invalid_tool_arguments(self):
        cases = [('unknown', {}), ('get_order', {}), ('get_order', {'order_id': True}),
                 ('get_order', {'order_id': -1}), ('get_order', {'order_id': '1 OR 1=1'}),
                 ('search_products', {'limit': 11}), ('search_policies', {'query': '  '}),
                 ('search_products', {'max_price': float('nan')}),
                 ('search_products', {'max_price': float('inf')}),
                 ('search_products', {'max_price': -1})]
        for name, args in cases:
            with self.subTest(name=name, args=args):
                self.assertIn('error', self.tools.execute(name, args))

    def test_invalid_session_identity(self):
        for value in [True, 0, -1, '3']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                ToolBox(DATA, value)

    def test_product_missing_and_unavailable(self):
        self.assertEqual(self.tools.execute('get_product', {'product_id': 9999}), {'found': False})
        for product_id in [96, 130, 136]:
            self.assertFalse(self.tools.execute('get_product', {'product_id': product_id})['available'])

    def test_price_and_budget_contract(self):
        regular = self.tools.execute('get_product', {'product_id': 90})
        pix = self.tools.execute('get_product', {'product_id': 90, 'payment': 'pix'})
        self.assertEqual(regular['final_price_brl'], pix['final_price_brl'])
        result = self.tools.execute('search_products', {'category': 'acoustic guitars', 'max_price': 1000})
        self.assertTrue(result['products'])
        from decimal import Decimal
        self.assertTrue(all(p['available'] and Decimal(p['final_price_brl']) <= 1000 for p in result['products']))

    def test_policy_sources_and_missing_topic(self):
        result = self.tools.execute('search_policies', {'query': 'return purchase'})
        self.assertIn(4, [p['page'] for p in result['pages']])
        self.assertFalse(self.tools.execute('search_policies', {'query': 'astrophysics'})['found'])

    def test_related_policy_pages(self):
        for query, required in [('payment pix', {3, 6}), ('shipping', {4, 5}), ('phone', {2, 6})]:
            with self.subTest(query=query):
                result = self.tools.execute('search_policies', {'query': query})
                self.assertTrue(required <= {p['page'] for p in result['pages']})
