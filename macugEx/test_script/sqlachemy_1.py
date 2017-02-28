# -*- coding: utf-8 -*-

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy import and_, or_, text, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Model = declarative_base()
Session = sessionmaker()


class User(Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), unique=True, nullable=False, default='')
    age = Column(Integer, index=True, nullable=True)
    password = Column(String(128), nullable=False)


if __name__ == '__main__':
    engine = create_engine('mysql://acp:acp123@127.0.0.1:3306/much', echo=True)
    # Model.metadata.create_all(engine)
    # Model.metadata.drop_all(engine)
    Session.configure(bind=engine)
    session = Session()
    session.commit()
