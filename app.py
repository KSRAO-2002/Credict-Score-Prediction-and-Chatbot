from flask import Flask, url_for, render_template, request, redirect, session, flash, jsonify
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet
from chatbot import get_Chat_response
import numpy as np
import pandas as pd
import sqlite3
import os
import secrets
import pickle
import joblib
import json

StSc = StandardScaler()

key = os.environ.get("MY_APP_ENCRYPTION_KEY")

if key is None:
    key = Fernet.generate_key()
    os.environ["MY_APP_ENCRYPTION_KEY"] = key.hex()
    print(os.environ["MY_APP_ENCRYPTION_KEY"])
else:
    key = bytes.fromhex(key)

cipher_suite = Fernet(key)

def encrypt_data(data):
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data

def decrypt_data(encrypted_data):
    decrypted_data = cipher_suite.decrypt(encrypted_data)
    return decrypted_data.decode()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.secret_key = secrets.token_hex(16)
db = SQLAlchemy(app)
model = pickle.load(open('model.pkl', 'rb'))
modelloan = joblib.load('modelloan.pkl')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


cleaned_suggestions = []
introduction_questions = [
    "Hello! I'm your friendly chatbot Cibi. What can I help you with today?",
    "Would you like to know something specific or just have a casual chat?",
]

# Load the user data and suggestions data
file_path = 'train.csv'  # Update with your file path
user_data = pd.read_csv(file_path)

# Relevant columns for collaborative filtering
selected_columns = [
    "Num_Credit_Card", "Interest_Rate" ,
    "Num_of_Loan",
    "Delay_from_due_date",
    "Num_of_Delayed_Payment", "Changed_Credit_Limit", "Num_Credit_Inquiries",
    "Outstanding_Debt"
]

sample_size =32000

if len(user_data) > sample_size:
    sample_indices = np.random.choice(len(user_data), size=sample_size, replace=False)
    user_data_sample = user_data.iloc[sample_indices]
else:
    user_data_sample = user_data

# Calculate cosine similarity between users
user_similarity = cosine_similarity(user_data_sample[selected_columns])

with open("suggestions.json", "r") as json_file:
    suggestions_data = json.load(json_file)

suggestions = {item["name"]: item["feature_indices"] for item in suggestions_data["suggestions"] if "Credit_Score" not in item["feature_indices"]}


# Define a function to check if a suggestion is relevant for the customer
def is_relevant_suggestion(user_average, similar_users_average, threshold):
    return np.abs(user_average - np.mean(similar_users_average)) > threshold

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
    Monthly_Inhand_Salary = db.Column(db.Float)
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
    Credit_Mix = db.Column(db.String(10)) 
    Payment_of_Min_Amount = db.Column(db.String(3))  


class UserFormId(db.Model):
    __tablename__ = 'user_from_id'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    form_id = db.Column(db.Integer)
    credit_score = db.Column(db.Integer)


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


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            db.session.add(
                User(username=request.form['username'], password=request.form['password']))
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
                age, annual_income, monthly_inhand_salary, num_bank_accounts, num_credit_card, interest_rate, num_of_loan, delay_from_due_date,
                num_of_delayed_payment, changed_credit_limit, num_credit_inquiries, outstanding_debt, credit_utilization_ratio,
                credit_history_age, total_emi_per_month, amount_invested_monthly,
                monthly_balance, Credit_Mix_Bad, Credit_Mix_Good, Credit_Mix_Standard, Payment_of_Min_Amount_NM,
                Payment_of_Min_Amount_No, Payment_of_Min_Amount_Yes])

            model_input_array = model_input_array.reshape(1, -1)
            prediction = model.predict(model_input_array)

            new_data = FormDetails(
                Age=age, Annual_Income=annual_income, Monthly_Inhand_Salary=monthly_inhand_salary, Num_Bank_Accounts=num_bank_accounts,
                Delay_from_due_date=delay_from_due_date, Num_Credit_Card=num_credit_card,
                Num_of_Loan=num_of_loan, Num_of_Delayed_Payment=num_of_delayed_payment,
                Interest_Rate=interest_rate, Changed_Credit_Limit=changed_credit_limit,
                Outstanding_Debt=outstanding_debt, Credit_Utilization_Ratio=credit_utilization_ratio,
                Credit_History_Age=credit_history_age, Total_EMI_per_month=total_emi_per_month,
                Amount_invested_monthly=amount_invested_monthly, Monthly_Balance=monthly_balance,
                Num_Credit_Inquiries=num_credit_inquiries, Credit_Mix = credit_mix, Payment_of_Min_Amount = payment_of_min_amount
            )
            db.session.add(new_data)
            db.session.commit()
            formId = new_data.id
            userId = session.get('user_id')
            db.session.add(UserFormId(user_id=userId,form_id=formId,credit_score=int(prediction)))
            db.session.commit()
        except Exception as e:
            flash("An error occurred while storing data. Please try again.", e)
        return render_template('form.html', prediction=int(prediction))
    else:
        return render_template('form.html')


@app.route('/loan', methods=['GET', 'POST'])
def loanapproval():
    if request.method == 'POST':
        user_input_value = {
            'Gender': 1,
            'Married': 1,
            'Dependents': 1,
            'Education': 0,
            'Self_Employed': 0,
            'ApplicantIncome': 8.43,
            'CoapplicantIncome': 7.31,
            'LoanAmount': 4.85,
            'Loan_Amount_Term': 360,
            'Credit_History': 1,
            'Property_Area': 0
        }

        user_input_array = np.array(list(user_input_value.values())).reshape(1, -1)
        
        scaled_user_input = StSc.fit_transform(user_input_array)
        prediction_value = modelloan.predict(scaled_user_input)
        print(prediction_value)
        result = {'status': 'approved', 'message': 'Your loan is approved.'}
        return jsonify(result) 
    else:
        user_input_value = {
            'Gender': 1,
            'Married': 1,
            'Dependents': 1,
            'Education': 0,
            'Self_Employed': 0,
            'ApplicantIncome': 8.43,
            'CoapplicantIncome': 7.31,
            'LoanAmount': 4.85,
            'Loan_Amount_Term': 360,
            'Credit_History': 1,
            'Property_Area': 0
        }
        user_input_array = np.array(list(user_input_value.values())).reshape(1, -1)
        scaled_user_input = StSc.transform(user_input_array)
        prediction_value = modelloan.predict(scaled_user_input)
        return render_template('loanform.html')

@app.route('/cibilchatbot', methods=['GET'])
def cibilchatbot():
    return render_template('chat.html')

@app.route("/get", methods=["POST"])
def chat():
    user_params = request.form.get("userParams")
    print("hello")
    print(user_params)
    if not user_params:
        return jsonify(["Please enter more parameters to get suggestions."])

    user_params = [float(param) for param in user_params.split(',')]
    
    # Convert user input to a NumPy array
    target_user_data = np.array(user_params)

    # Find most similar users
    target_user_similarity = cosine_similarity([target_user_data], user_data_sample[selected_columns])
    target_user_index = np.argmax(target_user_similarity)
    similar_users = np.argsort(user_similarity[target_user_index])[::-1]
    similar_users = similar_users[similar_users != target_user_index]  # Exclude the target user

    # Print credit score improvement suggestions for the user
    relevant_suggestions = []
    for suggestion, feature_indices in suggestions.items():
        user_average = np.mean(target_user_data[feature_indices])
        similar_users_average = np.mean(user_data_sample.iloc[similar_users, feature_indices], axis=1)

        # Define a threshold for each suggestion (customize as needed)
        if is_relevant_suggestion(user_average, similar_users_average, threshold= 3.5):
            relevant_suggestions.append(suggestion)
            relevant_suggestions = relevant_suggestions[:6]

        # json_responses = []
        formatted_suggestions = []

# # Convert each relevant suggestion to JSON and add it to the list
        for suggestion in relevant_suggestions:
            formatted_suggestions.append(str(suggestion))

# # Return the JSON responses as a list
    return jsonify(formatted_suggestions)

if __name__ == '__main__':
    # Create the SQLite database
    create_database()

    # Create the database tables
    create_tables()

    app.run()
