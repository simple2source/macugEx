# -*- coding: utf-8 -*-
"""sqlalchemy use test v2"""
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
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

    # addresses = [Address(address='me@xueming.li'), Address(address='li.xm87@gmail.com')]
    # admin = User(name='mage', fullname='Ma ge', password='123456', managed_addresses=addresses)
    # user = User(name='comyn', fullname='Comyn Li', password='123456', addresses=addresses)
    # session.add(user) # User is master table  1:n
    # session.add(admin)

    # address = Address(address='xueming.li@magedu.com')
    # user = session.query(User).filter(User.id == 1).first()
    #
    # address.user = user
    #
    # session.add(address)  # Address is master  n:1
    #
    # try:
    #     session.commit()
    # except Exception as e:
    #     session.rollback()
    #     raise e

    # find user address is xueming.li@magedu.com
    # select * from users join addresses on users.id = addresses.user_id where addresses.address = 'xueming.li@magedu.com'

    # result = session.query(User).join(Address).filter(Address.address == 'li.xm87@gmail.com').all()
    # result = session.query(User).outerjoin(Address).filter(Address.address == 'xueming.li@magedu.com').all()
    # result = session.query(User).join(Address, Address.user_id == User.id).filter(Address.address == 'li.xm87@gmail.com').all()
    result = session.query(User).join(Address, User.addresses).filter(Address.address == 'li.xm87@gmail.com').all()
    # select users.* from users
    #   join addresses as a1 on users.id = a1.user_id
    #   join addresses as a2 on users.id = a2.user_id
    # where a1.address = 'xueming.li@magedu.com' and a2.address = 'me@xueming.li'
    # admin = session.query(User).filter(User.id == 2).first()
    # a1 = aliased(Address)
    # a2 = aliased(Address)
    # result = session.query(User)\
    #     .join(a1, User.addresses)\
    #     .join(a2, User.addresses)\
    #     .filter(a1.address == 'li.xm87@gmail.com')\
    #     .filter(a2.admin == admin).all()
    print(result)