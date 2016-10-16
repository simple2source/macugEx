# -*- coding: utf-8 -*-
"""sqlalchemy use test v5 多对多关系"""
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, joinedload
from sqlalchemy.ext.declarative import declarative_base

Model = declarative_base()
Session = sessionmaker()


post_keywords = Table('post_keywords', Model.metadata,
                      Column('post_id', ForeignKey('posts.id'), primary_key=True),
                      Column('keyword_id', ForeignKey('keywords.id'), primary_key=True))


class Post(Model):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), unique=True, nullable=False)
    body = Column(Text, nullable=True)

    keywords = relationship('Keyword', back_populates='posts', secondary=post_keywords)

    def __repr__(self):
        return 'Post<id={},title={}>'.format(self.id, self.title)


class Keyword(Model):
    __tablename__ = 'keywords'

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String(64), nullable=False, unique=True)

    posts = relationship('Post', back_populates='keywords', secondary=post_keywords)

    def __repr__(self):
        return 'Keyword<id={},keyword={}>'.format(self.id, self.keyword)


if __name__ == '__main__':
    engine = create_engine('mysql+pymysql://root:123456@127.0.0.1:3306/demo', echo=True)
    Session.configure(bind=engine)
    session = Session()

    # Model.metadata.drop_all(engine)
    # Model.metadata.create_all(engine)

    # keyword1 = Keyword(keyword='abc')
    # keyword2 = Keyword(keyword='xyz')
    # keyword3 = Keyword(keyword='haha')
    #
    # post1 = Post(title='post1', keywords=[keyword1, keyword2])
    # port2 = Post(title='post2', keywords=[keyword2, keyword3])
    #
    # session.add(post1)
    # session.add(port2) # Post is master

    # post3 = Post(title='post3')
    # post4 = Post(title='post4')
    # post5 = Post(title='post5')
    #
    # keyword4 = Keyword(keyword='k4', posts=[post3, post4])
    # keyword5 = Keyword(keyword='k5', posts=[post4, post5])
    #
    # session.add(keyword4)
    # session.add(keyword5)  # Keyword is master
    #
    # try:
    #     session.commit()
    # except Exception as e:
    #     session.rollback()
    #     raise e

    # post = session.query(Post).options(joinedload(Post.keywords)).filter(Post.id == 1).first()
    # print(post)
    # print("=========")
    # print(post.keywords)

    # keyword = session.query(Keyword).filter(Keyword.id == 1).first()
    # print(keyword)
    # print(keyword.posts)

    # post = session.query(Post).filter(Post.keywords.any(keyword='abc')).first()
    # print(post)
    for kw in session.query(Keyword).filter(Keyword.keyword == 'abc').all():
        print(kw.posts)

    # keywords = session.query(Keyword).filter(Keyword.posts.any(title='post1')).all()
    # print(keywords)