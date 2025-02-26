from app import db, app # imports our sqlalchemy and our app instance
from app.models import Users

# Initialize db with a sample user, this file will definitely change!
with app.app_context():
    if not Users.query.filter_by(username="testuser").first():
        new_user = Users(username="testuser", email="testuser@example.com")
        db.session.add(new_user)
        db.session.commit()
        print("User 'testuser' created!")
    else:
        print("User 'testuser' already exists.")