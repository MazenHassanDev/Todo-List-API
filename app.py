from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from database import Config

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    from routes.auth_routes import auth_bp
    from routes.todo_routes import todos_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(todos_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)