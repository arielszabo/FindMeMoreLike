from sqlalchemy import Column, create_engine
from sqlalchemy.dialects.sqlite import TIMESTAMP, TEXT, BOOLEAN, INTEGER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DB_NAME = "webapp_db"
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





