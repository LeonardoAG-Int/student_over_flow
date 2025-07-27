from flask import Flask
from config import Config
from extensions import db, login_manager
from routes import configure_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()

    configure_routes(app)
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
