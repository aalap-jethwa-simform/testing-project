from . import db


from sqlalchemy import Column, Integer, String

class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String(120), unique=True, nullable=False)
