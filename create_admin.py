from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():

    db.create_all()

    admin = User.query.filter_by(
        email="admin@trek.com"
    ).first()

    if not admin:

        admin = User(
            name="Admin",
            email="admin@trek.com",
            password=generate_password_hash(
                "admin123"
            ),
            role="admin"
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin created")

    else:
        print("Admin already exists")