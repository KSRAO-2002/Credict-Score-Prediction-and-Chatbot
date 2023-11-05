# from flask import Flask, render_template, request, redirect, session
# from flask_sqlalchemy import SQLAlchemy

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# db = SQLAlchemy(app)

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(100), unique=True)
#     password = db.Column(db.String(100))

# def create_database():
#     database_file = 'users.db'
#     with app.app_context():
#         db.create_all()

# def create_tables():
#     with app.app_context():
#         db.create_all()

# db.session.add(User("Sujan","Rao"))
# db.session.commit()

# # Define your other routes and views here

# if __name__ == '__main__':
#     app.secret_key = "ThisIsNotASecret:p"
#     create_database()
#     create_tables()
#     app.run(debug=True)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Use SQLite database
db = SQLAlchemy(app)

# class FormDetails(db.Model):
#     __tablename__ = 'form_details'
#     id = db.Column(db.Integer, primary_key=True)
#     Age = db.Column(db.Integer)
#     Annual_Income = db.Column(db.Float)
#     Num_Bank_Accounts = db.Column(db.Integer)
#     Delay_from_due_date = db.Column(db.Integer)
#     Num_Credit_Card = db.Column(db.Integer)
#     Num_of_Loan = db.Column(db.Integer)
#     Num_of_Delayed_Payment = db.Column(db.Integer)
#     Interest_Rate = db.Column(db.Float)
#     Changed_Credit_Limit = db.Column(db.Float)
#     Outstanding_Debt = db.Column(db.Float)
#     Credit_Utilization_Ratio = db.Column(db.Float)
#     Credit_History_Age = db.Column(db.Integer)
#     Total_EMI_per_month = db.Column(db.Float)
#     Amount_invested_monthly = db.Column(db.Float)
#     Monthly_Balance = db.Column(db.Float)
#     Num_Credit_Inquiries = db.Column(db.Integer)

class UserFormId(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    form_id = db.Column(db.Integer)
# Create the database and tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()
