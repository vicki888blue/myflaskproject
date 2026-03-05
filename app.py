# app.py
from flask import Flask, render_template
from auth.routes import auth_bp
from tickets.routes import tickets_bp          
from db import init_engine                     

def create_app():
    app = Flask(__name__)
    app.secret_key = "change-me"

    
    app.config["DATABASE_URL"] = "sqlite:///mydatabase.db"
    init_engine(app.config["DATABASE_URL"])

   
    app.register_blueprint(auth_bp)                          # /login, /register, etc.
    app.register_blueprint(tickets_bp, url_prefix="/tickets")# /tickets, /tickets/new, ...

    @app.get("/")
    def home():
        return render_template("home.html")

    return app

if __name__ == "__main__":
    app = create_app()
    print("Starting development server at http://127.0.0.1:5000 …")
    app.run(debug=True)