from flask_login import UserMixin

from webapp.db import DB, Users

class User(UserMixin):
    def __init__(self, id_, name, email, profile_pic):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic

        self.create_if_not_exist()

    def create_if_not_exist(self):
        with DB() as db:
            query = db.session.query(Users).filter(Users.id == self.id)
            rows = query.all()  # id is unique so maximum one row will be returned

        if not rows:  # if it's not an empty list
            self.create_me()


    def create_me(self):
        with DB() as db:
            new_user = Users(id=self.id, name=self.name, email=self.email, profile_pic=self.profile_pic)
            db.session.add(new_user)
            db.session.commit()


def get_user_by_id(user_id):
    with DB() as db:
        query = db.session.query(Users).filter(Users.id == user_id)
        rows = query.all()  # id is unique so maximum one row will be returned

    if rows:  # if it's not an empty list

        user_data = rows[0]
        user = User(
            id_=user_data.id,
            name=user_data.name,
            email=user_data.email,
            profile_pic=user_data.profile_pic
        )

        return user

    else:
        return