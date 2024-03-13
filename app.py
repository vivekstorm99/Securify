from flask import Flask, render_template, request, redirect, url_for, session

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import urllib
import mysql.connector

app = Flask(__name__)
app.secret_key = 'mysecretkey'

mydb = mysql.connector.connect(
  host='localhost',
  user='root',
  password='Mcqueen_9599',
  database='citizen_safety'
)

mycursor = mydb.cursor()

@app.route("/login")
def loginpage():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get user input from form
        email = request.form['email']
        password = request.form['password']

        # Retrieve user information from database
        query = 'SELECT * FROM users WHERE email = %s'
        values = (email,)
        mycursor.execute(query, values)
        user = mycursor.fetchone()

        if user:
            # Check if password is correct
            if password == user[2]:
                # Save user ID in session
                session['user_id'] = user[0]
                return render_template('loggedin.html')
            else:
                return render_template('login.html', msg='Invalid email or password')
        else:
            return render_template('login.html', msg='Invalid email or password')
    else:
        return render_template('login.html')

@app.route('/')
def index():
    query = "SELECT * FROM report"
    df = pd.read_sql(query, mydb)

    # Count Report Types
    report_counts = df['report_type'].value_counts()

    # Visualize Data
    # Visualize Data
    plt.figure(figsize=(9, 6))
    sns.set_theme()
    sns.barplot(x=report_counts.index, y=report_counts.values, alpha=0.8)
    plt.title('Count of Each Report Type')
    plt.ylabel('Count', fontsize=12)
    plt.xlabel('Report Type', fontsize=12)

    # Convert Plot to PNG Image
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = urllib.parse.quote(base64.b64encode(img.read()).decode())

    return render_template('index.html', plot_url=plot_url)
    

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get user input from form
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']


        # Store user information in database
        query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        values = (username, email, password)
        mycursor.execute(query, values)
        mydb.commit()

        # Redirect user to login page
        return redirect(url_for('login'))
    else:
        return render_template('register.html')
    

    
@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/reportsuccess', methods=['post','get'])
def reportsuccess():
    if request.method == 'POST' or request.method == 'post':
        crime_type = request.form.get('report_type')
        crime_desc = request.form.get('report_description')
        query = "INSERT INTO report (report_type, report_description) VALUES (%s, %s)"
        values = (crime_type, crime_desc)   
        mycursor.execute(query,values)
        mydb.commit()
        return render_template('reportsuccess.html')
    else:
        return render_template('index.html')
        
@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/cybertips')
def cybertips():
    return render_template('cybertips.html')

@app.route('/emergency')
def emr():
    return render_template('emergency_contacts.html')

@app.route('/emergency', methods=['GET','POST'])
def emergencycontacts():
    if request.method == 'POST':
        # Get user input from form
        emergency_type = request.form['emergency_type']
        phone_number = request.form['phone_number']


        # Store user information in database
        query = "INSERT INTO emergency (emergency_type, phone_number) VALUES (%s, %s)"
        values = (emergency_type, phone_number)
        mycursor.execute(query, values)
        mydb.commit()

        # Redirect user to login page
        return render_template('reportsuccessem.html')
    else:
        return render_template('index.html')
    


@app.route('/logout')
def logout():
    # Clear user ID from session
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
