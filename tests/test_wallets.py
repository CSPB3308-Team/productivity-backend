import unittest
from app import create_app, db
from app.models import Users, Wallets
from flask_testing import TestCase

class TestWalletsModel(TestCase):
    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        return app

    def setUp(self):
        db.create_all()
        self.user = Users(
            username='testuser',
            first_name='Test',
            last_name='User',
            email='testuser@example.com'
        )
        self.user.set_password('securepassword')
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_wallet_creation(self):
        wallet = Wallets(user_id=self.user.id, balance=100)
        db.session.add(wallet)
        db.session.commit()

        fetched_wallet = Wallets.query.filter_by(user_id=self.user.id).first()
        self.assertIsNotNone(fetched_wallet)
        self.assertEqual(fetched_wallet.balance, 100)

    def test_wallet_balance_default(self):
        wallet = Wallets(user_id=self.user.id)
        db.session.add(wallet)
        db.session.commit()

        fetched_wallet = Wallets.query.get(wallet.id)
        self.assertEqual(fetched_wallet.balance, 0)

    def test_wallet_balance_cannot_be_negative(self):
        wallet = Wallets(user_id=self.user.id, balance=-10)
        db.session.add(wallet)
        with self.assertRaises(Exception):
            db.session.commit()

    def test_user_wallet_relationship(self):
        wallet = Wallets(user_id=self.user.id, balance=50)
        db.session.add(wallet)
        db.session.commit()

        self.assertEqual(self.user.wallet.balance, 50)

    def test_user_wallet_uniqueness(self):
        wallet1 = Wallets(user_id=self.user.id, balance=100)
        wallet2 = Wallets(user_id=self.user.id, balance=200)
        db.session.add(wallet1)
        db.session.add(wallet2)
        with self.assertRaises(Exception):
            db.session.commit()

if __name__ == '__main__':
    unittest.main()
