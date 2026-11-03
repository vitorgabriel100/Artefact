"""Carga atômica de snapshots e ferramentas de catálogo, sem SQL gerado por LLM."""
import csv
import json
import sqlite3
import unicodedata
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


def normalize(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', str(value).lower())
                   if not unicodedata.combining(c))


def cents(value):
    amount = Decimal(str(value))
    if not amount.is_finite() or amount < 0:
        raise ValueError('Valor monetário deve ser finito e não negativo')
    return int((amount * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def discount(value, percent):
    return int((Decimal(value) * (100 - Decimal(percent)) / 100)
               .quantize(Decimal('1'), rounding=ROUND_HALF_UP))


class Catalog:
    def __init__(self, data_dir):
        self.db = sqlite3.connect(':memory:')
        self.db.row_factory = sqlite3.Row
        self.db.create_function('norm', 1, normalize)
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('''
        CREATE TABLE categories(id INTEGER PRIMARY KEY, name TEXT NOT NULL);
        CREATE TABLE customers(id INTEGER PRIMARY KEY, name TEXT, phone TEXT, email TEXT, city TEXT);
        CREATE TABLE products(id INTEGER PRIMARY KEY, name TEXT NOT NULL,
          category_id INTEGER REFERENCES categories(id), price INTEGER CHECK(price>=0),
          stock INTEGER CHECK(stock>=0), status TEXT CHECK(status IN ('active','discontinued','coming_soon')),
          description TEXT, specs TEXT);
        CREATE TABLE promotions(id INTEGER PRIMARY KEY, product_id INTEGER REFERENCES products(id),
          percent INTEGER CHECK(percent>0 AND percent<=100), description TEXT,
          active INTEGER CHECK(active IN (0,1)));
        CREATE UNIQUE INDEX one_active_promotion ON promotions(product_id) WHERE active=1;
        CREATE TABLE orders(id INTEGER PRIMARY KEY, customer_id INTEGER REFERENCES customers(id),
          order_date TEXT, status TEXT, total INTEGER CHECK(total>=0), payment TEXT,
          tracking TEXT, estimated_delivery TEXT, notes TEXT);
        CREATE TABLE order_items(order_id INTEGER REFERENCES orders(id),
          product_id INTEGER REFERENCES products(id), quantity INTEGER CHECK(quantity>0),
          PRIMARY KEY(order_id,product_id));
        ''')
        def rows(name):
            with (Path(data_dir) / (name + '.csv')).open(encoding='utf-8-sig', newline='') as f:
                return list(csv.DictReader(f))
        try:
            with self.db:
                for r in rows('categories'):
                    self.db.execute('INSERT INTO categories VALUES (?,?)', (int(r['category_id']),r['name']))
                for r in rows('customers'):
                    self.db.execute('INSERT INTO customers VALUES (?,?,?,?,?)',
                                    (int(r['customer_id']),r['name'],r['phone'],r['email'],r['city']))
                for r in rows('products'):
                    specs = json.loads(r['specs'])
                    if not isinstance(specs, dict):
                        raise ValueError('specs deve ser um objeto JSON')
                    self.db.execute('INSERT INTO products VALUES (?,?,?,?,?,?,?,?)',
                        (int(r['product_id']),r['name'],int(r['category_id']),cents(r['price_brl']),
                         int(r['stock_quantity']),r['status'],r['description'],json.dumps(specs)))
                for r in rows('promotions'):
                    self.db.execute('INSERT INTO promotions VALUES (?,?,?,?,?)',
                        (int(r['promotion_id']),int(r['product_id']),int(r['discount_percent']),
                         r['description'],int(r['is_active'])))
                for r in rows('orders'):
                    self.db.execute('INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?)',
                        (int(r['order_id']),int(r['customer_id']),r['order_date'],r['status'],
                         cents(r['total_brl']),r['payment_method'],r['tracking_code'] or None,
                         r['estimated_delivery'] or None,r['notes'] or None))
                for r in rows('order_items'):
                    self.db.execute('INSERT INTO order_items VALUES (?,?,?)',
                        (int(r['order_id']),int(r['product_id']),int(r['quantity'])))
        except Exception:
            self.db.close()
            raise

    def close(self):
        self.db.close()

    def product(self, product_id, payment='table'):
        if payment not in ('table', 'pix'):
            raise ValueError('Pagamento deve ser table ou pix')
        row = self.db.execute('''SELECT p.*, c.name category, pr.percent, pr.description promotion
           FROM products p JOIN categories c ON c.id=p.category_id
           LEFT JOIN promotions pr ON pr.product_id=p.id AND pr.active=1
           WHERE p.id=?''', (product_id,)).fetchone()
        if row is None:
            return None
        r = dict(row)
        pct = r['percent'] if r['percent'] is not None else (5 if payment == 'pix' else 0)
        available = r['status'] == 'active' and r['stock'] > 0
        return {'product_id':r['id'], 'name':r['name'], 'category':r['category'],
                'description':r['description'], 'specs':json.loads(r['specs']),
                'status':r['status'], 'stock_quantity':r['stock'], 'available':available,
                'unavailable_reason':None if available else (r['status'] if r['status'] != 'active' else 'out_of_stock'),
                'table_price_cents':r['price'], 'final_price_cents':discount(r['price'],pct),
                'discount_percent':pct, 'discount_source':'promotion' if r['percent'] is not None else ('pix' if pct else None),
                'promotion':r['promotion'], 'source':'CSV snapshot / SQLite'}

    def search(self, query='', category='', max_price=None, available_only=True, payment='table', limit=10):
        if not 1 <= limit <= 50:
            raise ValueError('limit deve estar entre 1 e 50')
        maximum = cents(max_price) if max_price is not None else None
        ids = self.db.execute('''SELECT p.id FROM products p JOIN categories c ON c.id=p.category_id
            WHERE instr(norm(p.name || ' ' || p.description), ?) > 0
              AND instr(norm(c.name), ?) > 0 ORDER BY p.id''',
            (normalize(query),normalize(category))).fetchall()
        results = [self.product(r['id'],payment) for r in ids]
        results = [r for r in results if (not available_only or r['available'])
                   and (maximum is None or r['final_price_cents'] <= maximum)]
        return sorted(results,key=lambda r:(r['final_price_cents'],r['product_id']))[:limit]
