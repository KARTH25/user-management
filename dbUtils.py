from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Float

db = SQLAlchemy()

def create_db():
    db.create_all()
    print('Database created')

def seed_db():
    user1 = Users(first_name="Karthick", last_name="Raja", email="karthickraja@gmail.com", password="123")
    user2 = Users(first_name="Tom", last_name="Jerry", email="tomjerry@gmail.com", password="123")
    user3 = Users(first_name="Ninja", last_name="Hattori", email="ninjahattori@gmail.com", password="123")
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.commit()
    print("Database seeded")

def drop_db():
    db.drop_all()
    print("Database dropped")

class Users(db.Model):
    __tablename__ = 'userInfo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)




