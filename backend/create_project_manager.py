from flask_bcrypt import Bcrypt
from models import db, Employees
from base import api

# Create project manager user
with api.app_context():
    # Check if project manager exists
    if not Employees.query.filter_by(Email="pm@qualityelectric.com").first():
        bcrypt = Bcrypt()
        hashed_password = bcrypt.generate_password_hash("manager123")
        project_manager = Employees(
            Employeeid=2001,
            Email="pm@qualityelectric.com",
            Password=hashed_password,
            FirstName="Project",
            LastName="Manager",
            PhoneNumber=1234567891,
            Admin=False,
            Role="project_manager",
            DateHired="2025-10-27"
        )
        db.session.add(project_manager)
        db.session.commit()
        print("Project Manager user created successfully!")
        print("\nYou can now log in with:")
        print("Email: pm@qualityelectric.com")
        print("Password: manager123")
    else:
        print("Project Manager user already exists!")