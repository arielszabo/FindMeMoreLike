from flask_login import UserMixin

from webapp.db_handler import DB, Users

class User(UserMixin):
    def __init__(self, google_id, name, email, profile_pic):
        self.google_id = google_id
        self.name = name
        self.email = email
        self.profile_pic = profile_pic

        self.id = self.get_id()

    def get_id(self):
        with DB() as db:
            query = db.session.query(Users).filter(Users.email == self.email)
            rows = query.all()  # id is unique so maximum one row will be returned

        if rows:  # if it's not an empty list
            return rows[0].id
        else:
            create_id = self.create_me()
            return create_id


    def create_me(self):
        with DB() as db:
            new_user = Users(google_id=self.google_id, name=self.name, email=self.email, profile_pic=self.profile_pic)
            db.session.add(new_user)
            db.session.flush()

            create_id = new_user.id

        return create_id


def get_user_by_id(user_id):
    with DB() as db:
        query = db.session.query(Users).filter(Users.id == user_id)
        rows = query.all()  # id is unique so maximum one row will be returned

    if rows:  # if it's not an empty list

        user_data = rows[0]
        user = User(
            google_id=user_data.google_id,
            name=user_data.name,
            email=user_data.email,
            profile_pic=user_data.profile_pic
        )

        return user

    else:
        return