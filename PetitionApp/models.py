from database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean


class Users(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_activate = Column(Boolean, default=True)
    role = Column(String)


class Petition(Base):
    __tablename__ = 'petition'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    petition_name = Column(String)
    petition_text = Column(String)
    images = Column(String)


class Signature(Base):
    __tablename__ = 'signature'

    id = Column(Integer, primary_key=True, index=True)
    petition_id = Column(Integer, ForeignKey('petition.id'))
    name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(20))
    city = Column(String(100))
    state = Column(String(50))
    show_signature = Column(Boolean)
    user_id = Column(Integer, ForeignKey('users.id'))


