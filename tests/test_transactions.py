import unittest
from sqlalchemy import text
from app import create_app, db
from app.models import Users, CustomizationItems, Transactions

class TestTransactionsModel(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        db.create_all()
        db.session.execute(text('PRAGMA foreign_keys = ON'))

        self.user = Users(
            username='testuser',
            first_name='Test',
            last_name='User',
            email='testuser@example.com'
        )
        self.user.set_password('password')
        db.session.add(self.user)

        self.item = CustomizationItems(
            item_type='skin',
            name='CoolSkin',
            item_cost=100,
            model_key='skin_cool_001'
        )
        db.session.add(self.item)

        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_transaction(self):
        txn = Transactions(user_id=self.user.id, item_id=self.item.id)
        db.session.add(txn)
        db.session.commit()

        saved = Transactions.query.first()
        self.assertIsNotNone(saved)
        self.assertEqual(saved.user_id, self.user.id)
        self.assertEqual(saved.item_id, self.item.id)

    def test_transaction_relationships(self):
        txn = Transactions(user_id=self.user.id, item_id=self.item.id)
        db.session.add(txn)
        db.session.commit()

        self.assertEqual(self.user.transactions[0].item.name, 'CoolSkin')
        self.assertEqual(self.item.transactions[0].user.email, 'testuser@example.com')

    def test_unique_transaction_constraint(self):
        txn1 = Transactions(user_id=self.user.id, item_id=self.item.id)
        txn2 = Transactions(user_id=self.user.id, item_id=self.item.id)
        db.session.add(txn1)
        db.session.add(txn2)
        with self.assertRaises(Exception):
            db.session.commit()

    def test_transaction_with_missing_user(self):
        txn = Transactions(user_id=9999, item_id=self.item.id)
        db.session.add(txn)
        with self.assertRaises(Exception):
            db.session.commit()

    def test_transaction_with_missing_item(self):
        txn = Transactions(user_id=self.user.id, item_id=9999)
        db.session.add(txn)
        with self.assertRaises(Exception):
            db.session.commit()

if __name__ == '__main__':
    unittest.main()

