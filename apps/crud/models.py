from datetime import datetime
from flask_login import UserMixin
from apps.app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin) :
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), index=True)
    email = db.Column(db.String(255), unique=True, index=True)
    password_hash = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    user_images = db.relationship("UserImage", backref="user", order_by="desc(UserImage.id)")

    @property
    def password(self):
        raise AttributeError("읽어 들일 수 없음")
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_duplicate_email(self):
        return User.query.filter_by(email=self.email).first() is not None

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)