# from flask import Flask, url_for, render_template, request, redirect, session
# from flask_sqlalchemy import SQLAlchemy
# from transformers import AutoModelForCausalLM, AutoTokenizer
# import sqlite3
# # import bcrypt
# import torch
# import secrets


# tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
# model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")


# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# db = SQLAlchemy(app)
# app.secret_key = secrets.token_hex(16)

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(100), unique=True)
#     password = db.Column(db.String(100))

#     def __init__(self, username, password):
#         self.username = username
#         self.password = password
# class CustomerDetails(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     Age = db.Column(db.Integer)
#     Annual_Income = db.Column(db.Integer)
#     Num_Bank_Accounts = db.Column(db.Integer)
    
#     def __init__(self, Age, Annual_income, Num_Bank_Accounts):
#         self.Age = Age
#         self.Annual_Income = Annual_income
#         self.Num_Bank_Accounts = Num_Bank_Accounts

# def create_database():
#     database_file = 'users.db'
#     with app.app_context():
#         conn = sqlite3.connect(database_file)
#         create_tables()
#         conn.close()

# # Function to create the database tables
# def create_tables():
#     with app.app_context():
#         db.create_all()

# @app.route('/', methods=['GET'])
# def index():
#     if session.get('logged_in'):
#         return render_template('home.html')
       
#     else:
#         return render_template('index.html', message="Hello!")


# @app.route('/register/', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         try:
#             db.session.add(User(username=request.form['username'], password=request.form['password']))
#             db.session.commit()
#             return redirect(url_for('login'))
#         except Exception as e:
#             # Print the exception to understand the specific issue
#             print(f"Error: {str(e)}")
#             return render_template('index.html', message="User Already Exists")
#     else:
#         return render_template('register.html')


# @app.route('/login/', methods=['GET', 'POST'])
# def login():
#     if request.method == 'GET':
#         return render_template('login.html')
#     else:
#         u = request.form['username']
#         p = request.form['password']
#         data = User.query.filter_by(username=u, password=p).first()
#         if data is not None:
#             session['logged_in'] = True
#             return redirect(url_for('index'))
#         return render_template('index.html', message="Incorrect Details")

# @app.route('/logout', methods=['GET', 'POST'])
# def logout():
#     session['logged_in'] = False
#     return redirect(url_for('index'))

# @app.route('/predictscore', methods=['GET', 'POST'])
# def predictscore():
#     if request.method == 'POST':
#         # Extract data from the form
#         Age = request.form['Age']
#         Annual_Income = request.form['Annual_Income']
#         Num_Bank_Accounts = request.form['Num_Bank_Accounts']
#         print(Age, Annual_Income, Num_Bank_Accounts)
#         # Add more fields as needed

#         # Create a new CustomerDetails record and add it to the database
#         customer = CustomerDetails(Age=Age, Annual_Income=Annual_Income, Num_Bank_Accounts=Num_Bank_Accounts)
#         db.session.add(customer)
#         db.session.commit()

# @app.route('/predict', methods=['GET', 'POST'])
# def predict():
#     # session['logged_in'] = False
#     return render_template('form.html')
#     return redirect(url_for('form'))

# @app.route("/get", methods=["GET", "POST"])
# def chat():
#     msg = request.form["msg"]
#     input = msg
#     return get_Chat_response(input)

# def get_Chat_response(text):
#     # Let's chat for 5 lines
#     for step in range(5):
#         # encode the new user input, add the eos_token and return a tensor in Pytorch
#         new_user_input_ids = tokenizer.encode(str(text) + tokenizer.eos_token, return_tensors='pt')

#         # append the new user input tokens to the chat history
#         bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if step > 0 else new_user_input_ids

#         # generated a response while limiting the total chat history to 1000 tokens, 
#         chat_history_ids = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

#         # pretty print last ouput tokens from bot
#         return tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
    
# @app.route('/cibilchatbot', methods=['GET'])
# def cibilchatbot():
#     return render_template('chat.html')

# if(__name__ == '__main__'):
#     # Correct indentation
#     create_database()
#     app.run()


from flask import Flask, url_for, render_template, request, redirect, session, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import bcrypt
import torch
import secrets

tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.secret_key = secrets.token_hex(16)
db = SQLAlchemy(app)
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

def get_Chat_response(text):

    # Let's chat for 5 lines
    for step in range(5):
        # encode the new user input, add the eos_token and return a tensor in Pytorch
        new_user_input_ids = tokenizer.encode(str(text) + tokenizer.eos_token, return_tensors='pt')

        # append the new user input tokens to the chat history
        bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if step > 0 else new_user_input_ids

        # generated a response while limiting the total chat history to 1000 tokens, 
        chat_history_ids = model.generate(bot_input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id)

        # pretty print last ouput tokens from bot
        return tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)

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
    from app import db
    if request.method == 'POST':
        print("hello")
        try:
            age = (request.form['Age'])
            print(age)
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
            return jsonify({'message': 'Data stored successfully'})
        except Exception as e: 
            print("Here is the exception: ",e)
            return render_template('home.html')
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
