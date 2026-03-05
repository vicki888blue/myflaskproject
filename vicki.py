# app.py
from flask import Flask, render_template
from config import Config
from db import init_engine
from auth.routes import auth_bp
from tickets.routes import tickets_bp
from auth.service import get_current_user


def create_app() -> Flask:
    """
    Flask application factory.
    - Loads configuration
    - Initialises DB engine (SQLAlchemy Core)
    - Registers feature blueprints
    - Declares lightweight 'home' route
    """
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    # --- Infrastructure ---
    init_engine(app.config["DATABASE_URL"])

    # --- Blueprints (feature modules) ---
    app.register_blueprint(auth_bp)                 # /login, /register, /logout
    app.register_blueprint(tickets_bp, url_prefix="/tickets")  # /tickets/...

    # --- Home ---
    @app.get("/")
    def home():
        return render_template("home.html", user=get_current_user())

    return app


if __name__ == "__main__":
    # In development you can keep debug=True; set False in prod
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)