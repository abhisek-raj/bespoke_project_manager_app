from dotenv import load_dotenv
import os

load_dotenv()

class ApplicationConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    # Prefer DATABASE_URL if provided; otherwise use instance/db.sqlite at project root
    _db_url = os.environ.get("DATABASE_URL")
    if _db_url:
        SQLALCHEMY_DATABASE_URI = _db_url
    else:
        _project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        _instance_dir = os.path.join(_project_root, "instance")
        os.makedirs(_instance_dir, exist_ok=True)
        _db_path = os.path.join(_instance_dir, "db.sqlite")
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{_db_path}"