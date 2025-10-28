from models import db, Employees
from base import api, bcrypt

"""
One-time script to FORCE RESET admin passwords in production DB.
Run this against your Render Postgres to fix invalid bcrypt hashes.
"""

with api.app_context():
    print("Resetting admin passwords...")
    
    # Reset admin@qualityelectric.com
    user1 = Employees.query.filter_by(Email="admin@qualityelectric.com").first()
    if user1:
        user1.Password = bcrypt.generate_password_hash("admin123").decode("utf-8")
        db.session.commit()
        print("[OK] Reset password for admin@qualityelectric.com")
    else:
        print("[FAIL] admin@qualityelectric.com not found")
    
    # Reset admin@gmail.com
    user2 = Employees.query.filter_by(Email="admin@gmail.com").first()
    if user2:
        user2.Password = bcrypt.generate_password_hash("admin123").decode("utf-8")
        db.session.commit()
        print("[OK] Reset password for admin@gmail.com")
    else:
        print("[FAIL] admin@gmail.com not found")
    
    print("\nDone! You can now log in with:")
    print("Email: admin@gmail.com")
    print("Password: admin123")
