from app import db
from sqlalchemy import Column, Integer, String, PickleType
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    spotify_id = Column(String, nullable=False, unique=True)
    token_object = Column(PickleType)  # tekore.Token
