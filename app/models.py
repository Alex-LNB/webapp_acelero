from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

USER_ADMIN = 128
USER_NORMAL = 8

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    encrypted_password = db.Column(db.String(102), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    name = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(10), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    admin = db.Column(db.Integer, default=USER_NORMAL)
    
    def verify_password(self, password):
        return check_password_hash(self.encrypted_password, password)
    
    @property
    def password(self):
        pass

    @password.setter
    def password(self, value):
        self.encrypted_password = generate_password_hash(value)
    
    @classmethod
    def create_element(cls, username, password, admin=False):
        user = User(username=username, password=password)
        if admin:
            user.admin=USER_ADMIN
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def get_by_id(cls, id):
        return User.query.filter_by(id=id).first()
    
    @classmethod
    def get_by_username(cls, username):
        return User.query.filter_by(username=username).first()

    @classmethod
    def set_admin(cls):
        if User.get_by_username('Administrator') == None:
            User.create_element('Administrator','password',True)
    
    @property
    def is_admin(self):
        if self.admin == USER_ADMIN:
            return True
        else:
            return False

    @classmethod
    def update_element(cls, id, name, phone, email):
        user = User.get_by_id(id)
        if user is None:
            return False
        else:
            user.name = name
            user.phone = phone
            user.email = email
            db.session.add(user)
            db.session.commit()
            return user
