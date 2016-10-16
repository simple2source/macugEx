# -*- coding: utf-8 -*-
"""sqlalchemy use test v4 """
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import func, exists
from sqlalchemy.orm import sessionmaker, relationship, aliased
from sqlalchemy.ext.declarative import declarative_base


Model = declarative_base()
Session = sessionmaker()


class User(Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(45), unique=True, nullable=False)
    fullname = Column(String(128), index=True, nullable=True)
    password = Column(String(128), nullable=False)

    addresses = relationship('Address', back_populates='user', foreign_keys='[Address.user_id]')
    managed_addresses = relationship('Address', back_populates='admin', foreign_keys='[Address.admin_id]')

    def __repr__(self):
        return 'User<id={},name={},fullname={}>'.format(self.id, self.name, self.fullname)


class Address(Model):
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String(128), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    admin_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship('User', back_populates='addresses', foreign_keys=[user_id])
    admin = relationship('User', back_populates='managed_addresses', foreign_keys=[admin_id])

    def __repr__(self):
        return 'Address<id={},address={}>'.format(self.id, self.address)


if __name__ == '__main__':
    engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/demo', echo=True)
    Session.configure(bind=engine)
    session = Session()

    # Model.metadata.drop_all(engine)
    # Model.metadata.create_all(engine)

    # select users.*, c.count from users left join (
    #     select user_id, count(*) as count from addresses group by user_id
    # ) as counter on users.id = counter.user_id

    # stmt = session.query(Address.user_id, func.count('*').label('count')).group_by(Address.user_id).subquery()
    # result = session.query(User, stmt.c.count).outerjoin(stmt, User.id == stmt.c.user_id).all()

    # select users.* from users where exist (select * from addresses where user_id != users.id)
    stmt = exists().where(Address.user_id != User.id)
    result = session.query(User).filter(stmt).all()
    print(result)