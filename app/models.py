from . import db
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey


class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String(120), unique=True, nullable=False)


class Project(db.Model):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    owner = relationship('User', back_populates='projects')


User.projects = relationship('Project', back_populates='owner', cascade='all, delete-orphan')
