from models import db, Employees, Customers, Generators, ServiceRecords, Service_Employee_Int, Password_Recovery, Tasks, Projects
from flask_bcrypt import Bcrypt
from config import ApplicationConfig
from flask_cors import CORS
from flask_jwt_extended import JWTManager

def create_app():
    from flask import Flask
    app = Flask(__name__)
    
    # Configure CORS for production
    CORS(app, 
         origins=[
             "http://localhost:5173",  # Development
             "https://your-production-domain.com"  # Add your production frontend URL
         ],
         allow_credentials=True,
         supports_credentials=True,
         expose_headers=["Content-Type", "X-CSRFToken"],
         allow_headers=["Content-Type", "Authorization"])

    @app.after_request
    def after_request(response):
        # Allow requests from both development and production domains
        origin = request.headers.get('Origin')
        if origin in ["http://localhost:5173", "https://your-production-domain.com"]:
            response.headers.add('Access-Control-Allow-Origin', origin)
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    app.config.from_object(ApplicationConfig)
    
    # Initialize extensions
    db.init_app(app)
    bcrypt = Bcrypt(app)
    jwt = JWTManager(app)
    
    # Import routes
    from routes import register_routes
    register_routes(app)
    
    return app

app = create_app()