# app.py
import os
import sys
from pathlib import Path
from flask import Flask, render_template
from auth.routes import auth_bp
from tickets.routes import tickets_bp
from db import init_engine, connect
from sqlalchemy import text

def create_app():
    app = Flask(__name__, template_folder='.')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'change-me')

    project_dir = Path(__file__).resolve().parent
    local_db_path = (project_dir / "mydatabase.db").resolve()  # Windows/local dev
    server_db_path = Path("/home/vicki888blue/mydatabase.db")  # PythonAnywhere

    # Decide which DB to use based on OS
    if os.name == "nt":  # Windows
        # Windows SQLite URL: three slashes, with a drive letter in the path
        db_url = f"sqlite:///{local_db_path.as_posix()}"  # e.g., sqlite:///C:/.../mydatabase.db
    else:  # Linux (PythonAnywhere)
        db_url = f"sqlite:////{server_db_path.as_posix()}"  # e.g., sqlite:////home/vicki888blue/mydatabase.db

    # If you REALLY want to allow env var on Linux production only, uncomment next line:
    # if os.name != "nt": db_url = os.getenv("DATABASE_URL", db_url)

    app.config['DATABASE_URL'] = db_url
    print(">>> Platform:", sys.platform, "| Using DATABASE_URL =", db_url)

    init_engine(db_url)

    # Diagnostics: prints on startup/reload
    try:
        with connect() as conn:
            dblist = conn.execute(text("PRAGMA database_list;")).fetchall()
            print(">>> SQLite database_list:", dblist)
            cols = conn.execute(text("PRAGMA table_info(Tickets);")).fetchall()
            print(">>> Tickets columns:", [c[1] for c in cols])
    except Exception as e:
        print(">>> DB check failed:", repr(e))

    app.register_blueprint(auth_bp)
    app.register_blueprint(tickets_bp, url_prefix="/tickets")

    @app.get("/")
    def home():
        return render_template("home.html")

    return app

application = create_app()

if __name__ == "__main__":
    application.run(debug=True)
