from models import db, Employees, Customers, Generators, ServiceRecords, Service_Employee_Int, Password_Recovery, Projects, Tasks
from config import ApplicationConfig
from flask import Flask
import json
from datetime import datetime

app = Flask(__name__)
app.config.from_object(ApplicationConfig)
db.init_app(app)

def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)

def print_table_contents(model):
    print(f"\n=== {model.__tablename__} Table ===")
    records = model.query.all()
    for record in records:
        # Convert SQLAlchemy model to dictionary
        record_dict = {column.name: getattr(record, column.name) 
                      for column in record.__table__.columns}
        # Print each record as formatted JSON
        print(json.dumps(record_dict, indent=2, default=serialize_datetime))
    print(f"Total records: {len(records)}\n")

with app.app_context():
    # Print contents of each table
    tables = [Employees, Customers, Generators, ServiceRecords, 
             Service_Employee_Int, Password_Recovery, Projects, Tasks]
    
    for table in tables:
        print_table_contents(table)