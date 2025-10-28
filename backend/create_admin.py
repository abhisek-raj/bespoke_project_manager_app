from models import db, Employees
from base import api, bcrypt

# Create admin user
with api.app_context():
    # Check if admin exists
    if not Employees.query.filter_by(Email="admin@qualityelectric.com").first():
        hashed_password = bcrypt.generate_password_hash("admin123").decode("utf-8")
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

    # Ensure admin@gmail.com also exists
    if not Employees.query.filter_by(Email="admin@gmail.com").first():
        hashed_password = bcrypt.generate_password_hash("admin123").decode("utf-8")
        admin2 = Employees(
            Employeeid=1002,
            Email="admin@gmail.com",
            Password=hashed_password,
            FirstName="Admin",
            LastName="Gmail",
            PhoneNumber=1234567890,
            Admin=True,
            DateHired="2025-10-27"
        )
        db.session.add(admin2)
        db.session.commit()
        print("Admin Gmail user created successfully!")
        print("\nYou can now log in with:")
        print("Email: admin@gmail.com")
        print("Password: admin123")
    else:
        print("Admin Gmail user already exists!")