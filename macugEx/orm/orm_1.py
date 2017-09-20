# -*- coding:utf-8 -*-

import sqlalchemy
import flask_sqlalchemy
from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import func
from sqlalchemy.orm import relationship
import pymysql

engine = create_engine()
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class User(Base):
    __tablename__ = 'user'
