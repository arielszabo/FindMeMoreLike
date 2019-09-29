from sqlalchemy import Column, create_engine
from sqlalchemy.dialects.sqlite import TIMESTAMP, TEXT, BOOLEAN, INTEGER
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DB_NAME = "sqlite_db"
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

    id = Column(TEXT, primary_key=True)
    name = Column(TEXT, nullable=False)
    email = Column(TEXT, unique=True, nullable=False)
    profile_pic = Column(TEXT, nullable=False)


class SeenTitles(Base):
    __tablename__ = 'seen_titles'

    id = Column(INTEGER, primary_key=True)
    user_email = Column(TEXT, nullable=False)
    imdbID = Column(TEXT, nullable=False)
    seen = Column(BOOLEAN, nullable=False)





