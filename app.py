
from engine import training
import csv
import pickle
import pandas as pd
# from gridfs import GridFS
from flask import Flask, render_template, url_for, request, session, redirect
import os
from flask_pymongo import PyMongo
# import bcrypt
# from bson import ObjectId
import re
import nltk
import create_db

app = Flask(__name__)
app.secret_key = "testing"
app.config["SECRET_KEY"]
app.config['MONGO_URI'] = 'mongodb://shanna_mongodb:27017/shanna_db'
#app.config['FILE_UPLOADS'] = "C:\\Users\\Osama\\Downloads\\Sandeep Project\\App\\static\\files"
mongo = PyMongo(app)
reg_users = mongo.db['register_users']
sentiment_model = training()

#create_db.createDB()

@app.route('/')
def index():   
    return render_template('main.html')

@app.route('/user_login', methods=['POST'])
def login_user():
    user_collection = reg_users
    print('user collection', user_collection)
    if request.method=='POST':
        print('yesssss')
        username = request.form['email']
        password = request.form['password']
        login_user = user_collection.find_one({'email' : username})


        if login_user:
            if login_user['password'] == password:
                session['email'] = username
                return redirect(url_for('dashboard'))               
            else:
                return ("please enter valid password")

        return 'Invalid username/password combination || OR || click on GET Started For Free to Signup'

@app.route('/user_signup', methods=['POST'])
def signup_user():
    user_collection = mongo.db.register_users
    if request.method == 'POST':
        user = request.form["email"]
        pwd = request.form["password"]
        existing_user = user_collection.find_one({'email' : user})
        if existing_user is None:
            user_collection.insert_one({'email' : user, 'password' : pwd})
            session['email'] = request.form['email']
            return "user registered"
        else:
            return "user already exists"


@app.route('/login')
def login():    
    return render_template('login.html')

@app.route('/signup')
def signup():    
    return render_template('signup.html')


@app.route('/results', methods=['POST', 'GET'])
def model_result():
    return render_template('download.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():   
    return render_template('dashboard.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/download')
def download():
    return render_template('download.html')

@app.route('/datafile', methods=['GET','POST'])
def uploadfile():
    
    if request.method == 'POST':
        if request.files:
            uploaded_file = request.files['csvfile'] 
            #model_name = request.form['modelname']
            # print('file name is:', str(uploaded_file).split('.')[-1])
            # print('file name is:::', uploaded_file)
            if 'csv' in str(uploaded_file):
                df = pd.read_csv(uploaded_file)
            elif 'xlsx' in str(uploaded_file):
                df = pd.read_excel(uploaded_file)
            else:
                return "Please upload file with .csv or .xslx extension"
            coloms = df.columns
            print('coloms are:', coloms)
            df['text'] = df[coloms[1]]
            print('text is::::', df['text'])
            

            #df = df.iloc[:500,:]
            #df.dropna(inplace=True)
            
            
            df['clean_text'] = df['text'].apply(sentiment_model.clean_text)
            #df.dropna(inplace=True)
            print('clean text:', df['clean_text'])
            df['sentiment'] = df['clean_text'].apply(sentiment_model.sentiment_scores)
            #print(df['sentiment'])
            
            df.to_csv('static/file/results2.csv')
            tmp = df['sentiment'].value_counts()
            x = list(tmp.index)
            y = list(tmp.values)

            df['text_len'] = df['text'].apply(lambda x: len(str(x).split()))
            tmp2 = df['text_len'].value_counts()
            x2 = list(tmp2.index)
            y2 = list(tmp2.values)

            
            return render_template('charts.html', x=x, y=y, x2=x2, y2=y2)




if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(host='0.0.0.0', port=5000)
