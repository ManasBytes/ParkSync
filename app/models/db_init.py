from app import create_app
from app.extensions import db
from app.models import User

def seed_database():
    app = create_app()
    

    with app.app_context():
        print("Re-initializing database...")

        # Reset DB
        db.drop_all()
        db.create_all()

        # Create Admin User Only
        print("Creating admin user...")
        admin = User(
            username='admin',
            email='admin@parksync.com',
            is_admin=True
        )
        first_user = User(
            username = 'manass',
            email ='manasarmo.1819r@gmail.com'
        )
        admin.set_password('admin123')
        first_user.set_password("manas123")
        db.session.add(admin)
        db.session.add(first_user)
        db.session.commit()

        print("\n" + "="*60)
        print("DATABASE INITIALIZED WITH ONLY ADMIN ACCOUNT")
        print("="*60)
        print("Admin Login:")
        print("  Email: admin@parksync.com")
        print("  Password: admin123")
        print("="*60 + "\n")

if __name__ == '__main__':
    seed_database()
        