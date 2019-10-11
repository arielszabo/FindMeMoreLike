from sqlalchemy import Column, create_engine
from sqlalchemy.dialects.sqlite import TIMESTAMP, TEXT, BOOLEAN, INTEGER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = os.path.join(root, "db", "webapp_db.db")
os.makedirs(os.path.dirname(DB_NAME), exist_ok=True)
Base = declarative_base()


class DB(object):
    def __init__(self):
        self.connection_string = f'sqlite:///{DB_NAME}'
        self.engine = create_engine(self.connection_string)
        self.session = None


    def __enter__(self):
        session = sessionmaker(expire_on_commit=False)
        self.session = session(bind=self.engine)

        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type:
            self.session.commit()

        self.session.close()


    def create_tables(self):
        Base.metadata.create_all(self.engine)


class Users(Base):
    __tablename__ = 'users'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    google_id = Column(TEXT)
    name = Column(TEXT, nullable=False)
    email = Column(TEXT, unique=True, nullable=False)
    profile_pic = Column(TEXT, nullable=False)


class SeenTitles(Base):
    __tablename__ = 'seen_titles'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    user_id = Column(INTEGER, nullable=False)
    imdb_id = Column(TEXT, nullable=False)
    # todo: make this uniuqe and fk to Users table



class MissingTitles(Base):
    __tablename__ = 'missing_titles'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    imdb_link = Column(TEXT, nullable=False)
    # todo: change this

