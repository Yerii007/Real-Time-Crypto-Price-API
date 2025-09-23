from extensions_file import db
from models.user import User
from flask_jwt_extended import create_access_token

class AuthService:

    @staticmethod
    def register_user(name, password):
        if not name or not password:
            return None, None

        if User.query.filter_by(name=name).first():
            return None, None

        user = User(name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        token = create_access_token(identity=str(user.id))
        return user, token

    @staticmethod
    def authenticate_user(name, password):
        if not name or not password:
            return None, None

        user = User.query.filter_by(name=name).first()
        if user and user.check_password(password):
            token = create_access_token(identity=str(user.id))
            return user, token
        return None, None
