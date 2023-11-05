from flask import Flask, url_for, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from chatbot import get_Chat_response
import sqlite3
# import bcrypt
import secrets
import pickle
import numpy as np


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.secret_key = secrets.token_hex(16)
db = SQLAlchemy(app)
model = pickle.load(open('model.pkl','rb'))
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, username, password):
        self.username = username
        self.password = password

# Create a model for the data
class FormDetails(db.Model):
    __tablename__ = 'form_details'
    id = db.Column(db.Integer, primary_key=True)
    Age = db.Column(db.Integer)
    Annual_Income = db.Column(db.Float)
    Num_Bank_Accounts = db.Column(db.Integer)
    Delay_from_due_date = db.Column(db.Integer)
    Num_Credit_Card = db.Column(db.Integer)
    Num_of_Loan = db.Column(db.Integer)
    Num_of_Delayed_Payment = db.Column(db.Integer)
    Interest_Rate = db.Column(db.Float)
    Changed_Credit_Limit = db.Column(db.Float)
    Outstanding_Debt = db.Column(db.Float)
    Credit_Utilization_Ratio = db.Column(db.Float)
    Credit_History_Age = db.Column(db.Integer)
    Total_EMI_per_month = db.Column(db.Float)
    Amount_invested_monthly = db.Column(db.Float)
    Monthly_Balance = db.Column(db.Float)
    Num_Credit_Inquiries = db.Column(db.Integer)

class UserFormId(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    form_id = db.Column(db.Integer)

def create_database():
    database_file = 'users.db'
    with app.app_context():
        conn = sqlite3.connect(database_file)
        conn.close()

# Function to create the database tables
def create_tables():
    with app.app_context():
        db.create_all()

@app.route('/', methods=['GET'])
def index():
    if session.get('logged_in'):
        return render_template('home.html')
       
    else:
        return render_template('index.html', message="Hello!")

@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    return get_Chat_response(input)

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            db.session.add(User(username=request.form['username'], password=request.form['password']))
            db.session.commit()
            return redirect(url_for('login'))
        except:
            return render_template('index.html', message="User Already Exists")
    else:
        return render_template('register.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        u = request.form['username']
        p = request.form['password']
        data = User.query.filter_by(username=u, password=p).first()
        if data is not None:
            session['logged_in'] = True
            return redirect(url_for('index'))
        return render_template('index.html', message="Incorrect Details")

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    return redirect(url_for('index'))

@app.route('/predict', methods=['GET', 'POST'])
def predictscore():
    if request.method == 'POST':
        try:
            age = (request.form['Age'])
            annual_income = (request.form.get('Annual_Income'))
            num_bank_accounts = (request.form.get('Num_Bank_Accounts'))
            delay_from_due_date = (request.form.get('Delay_from_due_date'))
            num_credit_card = (request.form.get('Num_Credit_Card'))
            num_of_loan = (request.form.get('Num_of_Loan'))
            num_of_delayed_payment = (request.form.get('Num_of_Delayed_Payment'))
            interest_rate = (request.form.get('Interest_Rate'))
            changed_credit_limit = (request.form.get('Changed_Credit_Limit'))
            outstanding_debt = (request.form.get('Outstanding_Debt'))
            credit_utilization_ratio = (request.form.get('Credit_Utilization_Ratio'))
            credit_history_age = (request.form.get('Credit_History_Age'))
            total_emi_per_month = (request.form.get('Total_EMI_per_month'))
            amount_invested_monthly = (request.form.get('Amount_invested_monthly'))
            monthly_balance = (request.form.get('Monthly_Balance'))
            num_credit_inquiries = (request.form.get('Num_Credit_Inquiries'))
            monthly_inhand_salary = (request.form.get('Monthly_Inhand_Salary'))
            credit_mix = request.form['Credit_Mix']
            payment_of_min_amount = request.form['Payment_of_Min_Amount']

            Credit_Mix_Good = 0
            Credit_Mix_Bad = 0
            Credit_Mix_Standard = 0

            if credit_mix == 'good':
                Credit_Mix_Good = 1
            elif credit_mix == 'bad':
                Credit_Mix_Bad = 1
            elif credit_mix == 'standard':
                Credit_Mix_Standard = 1
             
            Payment_of_Min_Amount_No = 0
            Payment_of_Min_Amount_Yes = 0
            Payment_of_Min_Amount_NM = 0

            if payment_of_min_amount == 'No':
                Payment_of_Min_Amount_No = 1
            elif payment_of_min_amount == 'Yes':
                Payment_of_Min_Amount_Yes = 1
   
            model_input_array = np.array([
            age, annual_income,monthly_inhand_salary, num_bank_accounts,num_credit_card, interest_rate,  num_of_loan,delay_from_due_date,
             num_of_delayed_payment, changed_credit_limit,num_credit_inquiries, outstanding_debt, credit_utilization_ratio,
            credit_history_age, total_emi_per_month, amount_invested_monthly,
            monthly_balance,Credit_Mix_Bad,Credit_Mix_Good,Credit_Mix_Standard,Payment_of_Min_Amount_NM,
            Payment_of_Min_Amount_No,Payment_of_Min_Amount_Yes])
            
            model_input_array = model_input_array.reshape(1, -1)
            prediction = model.predict(model_input_array)
            print(prediction)
            
            new_data = FormDetails(
                Age=age, Annual_Income=annual_income, Num_Bank_Accounts=num_bank_accounts,
                Delay_from_due_date=delay_from_due_date, Num_Credit_Card=num_credit_card,
                Num_of_Loan=num_of_loan, Num_of_Delayed_Payment=num_of_delayed_payment,
                Interest_Rate=interest_rate, Changed_Credit_Limit=changed_credit_limit,
                Outstanding_Debt=outstanding_debt, Credit_Utilization_Ratio=credit_utilization_ratio,
                Credit_History_Age=credit_history_age, Total_EMI_per_month=total_emi_per_month,
                Amount_invested_monthly=amount_invested_monthly, Monthly_Balance=monthly_balance,
                Num_Credit_Inquiries=num_credit_inquiries
            )
            
            db.session.add(new_data)
            db.session.commit()
            formId = new_data.id
            userId = session.get('user_id')
            db.session.add(UserFormId(user_id=userId,form_id=formId))
            db.session.commit()
        except Exception as e: 
            flash("An error occurred while storing data. Please try again.", e)
        return render_template('form.html', prediction=int(prediction))
    else:
        return render_template('form.html')

@app.route('/cibilchatbot', methods=['GET'])
def cibilchatbot():
    return render_template('chat.html')

if __name__ == '__main__':
    # Create the SQLite database
    create_database()
    
    # Create the database tables
    create_tables()

    app.run()
