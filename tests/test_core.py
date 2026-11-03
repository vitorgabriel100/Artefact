import csv
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path
from emporio.catalog import Catalog, cents
from emporio.policies import Policies

DATA = Path(__file__).resolve().parents[1] / 'data'


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = Catalog(DATA)
        self.addCleanup(self.catalog.close)

    def test_import_relations(self):
        self.assertEqual(self.catalog.db.execute('SELECT count(*) FROM products').fetchone()[0],65)
        self.assertEqual(self.catalog.db.execute('PRAGMA foreign_key_check').fetchall(),[])

    def test_budget_and_stock(self):
        found = self.catalog.search(category='Violoes',max_price='1000')
        self.assertTrue(found)
        self.assertTrue(all(r['available'] and r['final_price_cents']<=100000 for r in found))
        self.assertTrue(all(r['category']=='Violões' for r in found))

    def test_no_promotion_pix_stacking(self):
        table = self.catalog.product(90)
        pix = self.catalog.product(90,'pix')
        self.assertEqual(pix['discount_percent'],18)
        self.assertEqual(pix['final_price_cents'],table['final_price_cents'])

    def test_pix_rounding(self):
        pix = self.catalog.product(81,'pix')
        self.assertEqual(pix['table_price_cents'],59990)
        self.assertEqual(pix['final_price_cents'],56991)

    def test_inactive_promotion_not_applied(self):
        self.assertEqual(self.catalog.product(102)['discount_percent'],0)

    def test_status_overrides_stock(self):
        for product_id,reason in [(136,'discontinued'),(130,'coming_soon'),(96,'out_of_stock')]:
            with self.subTest(product_id=product_id):
                p = self.catalog.product(product_id)
                self.assertFalse(p['available'])
                self.assertEqual(p['unavailable_reason'],reason)

    def test_unknown_product(self):
        self.assertIsNone(self.catalog.product(999999))

    def test_sql_input_is_literal(self):
        self.assertEqual(self.catalog.search("' OR 1=1 --"),[])

    def test_catalog_has_no_customer_details(self):
        self.assertFalse({'email','phone','customer_id'} & self.catalog.product(81).keys())

    def test_invalid_money(self):
        for value in ['-1','NaN','Infinity']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                cents(value)

    def test_orphan_promotion_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            shutil.copytree(DATA,folder,dirs_exist_ok=True)
            with (Path(folder)/'promotions.csv').open('a',encoding='utf-8',newline='') as f:
                csv.writer(f).writerow([999,999999,10,'Invalid',1])
            with self.assertRaises(sqlite3.IntegrityError):
                Catalog(folder)

    def test_ambiguous_active_promotions_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            shutil.copytree(DATA,folder,dirs_exist_ok=True)
            with (Path(folder)/'promotions.csv').open('a',encoding='utf-8',newline='') as f:
                csv.writer(f).writerow([999,90,10,'Duplicate',1])
            with self.assertRaises(sqlite3.IntegrityError):
                Catalog(folder)


class PolicyTests(unittest.TestCase):
    def test_return_policy_has_source(self):
        found = Policies(DATA).search('posso devolver uma compra?')
        self.assertIn(4,[p['page'] for p in found])
        self.assertTrue(all(p['source']=='politicas_da_loja.pdf' for p in found))

    def test_unknown_topic(self):
        self.assertEqual(Policies(DATA).search('astrofisica'),[])

    def test_document_change_detected(self):
        with tempfile.TemporaryDirectory() as folder:
            shutil.copytree(DATA,folder,dirs_exist_ok=True)
            with (Path(folder)/'politicas_da_loja.pdf').open('ab') as f:
                f.write(b'changed')
            with self.assertRaises(ValueError):
                Policies(folder)


if __name__ == '__main__':
    unittest.main()
