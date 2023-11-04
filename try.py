from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

def create_database():
    database_file = 'users.db'
    with app.app_context():
        db.create_all()

def create_tables():
    with app.app_context():
        db.create_all()

db.session.add(User("Sujan","Rao"))
db.session.commit()

# Define your other routes and views here

if __name__ == '__main__':
    app.secret_key = "ThisIsNotASecret:p"
    create_database()
    create_tables()
    app.run(debug=True)
