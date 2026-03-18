from flask import Flask
from config import Config
from database import Base, engine
from utils.extensions import bcrypt, limiter

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    bcrypt.init_app(app)
    limiter.init_app(app)

    from models.user_model import User
    from models.todo_model import Todo
    from models.refresh_token_model import RefreshToken

    Base.metadata.create_all(engine)

    from routes.auth_routes import auth_bp
    from routes.todo_routes import todos_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(todos_bp)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)