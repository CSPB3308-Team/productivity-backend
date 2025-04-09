import unittest
import os
from app import create_app, db

# Class for user testings
class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        # Sets up testing db
        self.app = create_app()

        # Override database for testing, force in memory sqlite3
        self.app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['TESTING'] = True

        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all() # run the schema (migrations)

    # After each test, tear it down
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # Test creating a new user
    def test_user_creation(self):
        with self.app.app_context():
            from app.models import Users  #import inside the test context
            # User info we are trying to add
            user = Users(username="testuser", email="test@example.com")
            # Attempt to add
            db.session.add(user)
            db.session.commit()
            # Query
            retrieved_user = Users.query.filter_by(username="testuser").first()
            # Asserts
            self.assertIsNotNone(retrieved_user) # it exists
            self.assertEqual(retrieved_user.email, "test@example.com") #it matches the email

if __name__ == '__main__':
    unittest.main()
