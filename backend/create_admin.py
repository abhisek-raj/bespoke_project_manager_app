from flask_bcrypt import Bcrypt
from models import db, Employees
from base import api

# Create admin user
with api.app_context():
    # Check if admin exists
    if not Employees.query.filter_by(Email="admin@qualityelectric.com").first():
        bcrypt = Bcrypt()
        hashed_password = bcrypt.generate_password_hash("admin123")
        admin = Employees(
            Employeeid=1001,
            Email="admin@qualityelectric.com",
            Password=hashed_password,
            FirstName="Admin",
            LastName="User",
            PhoneNumber=1234567890,
            Admin=True,
            DateHired="2025-10-27"
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
        print("\nYou can now log in with:")
        print("Email: admin@qualityelectric.com")
        print("Password: admin123")
    else:
        print("Admin user already exists!")