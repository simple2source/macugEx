# -*- coding: utf-8 -*-
"""sqlalchemy use test v1"""
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy import and_, or_, not_, text, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Model = declarative_base()
Session = sessionmaker()


class User(Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), unique=True, nullable=False)
    fullname = Column(String(128), index=True, nullable=True)
    password = Column(String(128), nullable=False)

    def __repr__(self):
        return 'User<id={},name={},fullname={}>'.format(self.id, self.name, self.fullname)


if __name__ == '__main__':
    engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/demo', echo=True)

    # Model.metadata.drop_all(engine)
    # Model.metadata.create_all(engine)

    Session.configure(bind=engine)
    session = Session()

    # user = User(name='comyn', fullname='comyn li', password='5678')
    # user = session.query(User).filter(User.id == 2).one()
    # new_user = User(**{k: v for k, v in user.__dict__.items() if not k.startswith('_')})
    # new_user.name = 'comyn'
    # new_user.id = None
    # session.add(new_user)
    # try:
    #     session.commit()
    # except Exception as e:
    #     session.rollback()
    #     raise e

    # ret = session.query(User).filter(User.name == 'comyn').filter(User.id == 4).first()
    # ret = session.query(User).filter(and_(User.name == 'magedu', or_(User.name == 'comyn', User.id == 2))).all()
    # ret = session.query(User).filter(text('id < :id and name like :name')).params(id=4, name='comyn').all()
    # ret = session.query(User).order_by(User.id.desc()).order_by(User.name).all()
    # ret = session.query(func.count(User.id)).group_by(User.fullname).all()
    ret = session.query(User.name, User.password).all()
    print(ret)