import re
from black import out
from flask import Flask, render_template, request
import pickle
import pandas as pd
from collections import Counter
from assets import twitter_scrape
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

import sqlite3

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
app.config['TESTING'] = True
app.jinja_env.auto_reload = True

@app.route("/", methods=['GET', 'POST'])
def login():
    try:
        # Called when user call the url / on his browser without sending any data
        if request.method == 'GET':
            return render_template('login.html')
        # Called when user call the url / on his browser and send data
        else:
            # Get the data from the form
            username = request.form['username']
            password = request.form['password']
            # Check if the username and password are correct
            db = get_db_connection()
            user = db.execute('SELECT * FROM user WHERE username = ? AND password = ?', (username, password)).fetchone()
            db.close()
            # If the username and password are correct, redirect the user to the home page
            if user:
                return render_template('index.html')
            # If the username or password are incorrect, show an error message
            else:
                return render_template('login.html', error='Invalid email or password')
    except Exception as e:
        return render_template('login.html', error=str(e))

@app.route("/register", methods=['GET', 'POST'])
def register():
    # The try catch block is used to handle errors
    try:
        # Called when user call the url / on his browser without sending any data
        if request.method == 'GET':
            return render_template('register.html')
        # Called when user call the url / on his browser and send data to register new user
        else:
            username = request.form['username']
            password = request.form['password']
            db = get_db_connection()
            # check if the username is already in the database
            user = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
            db.close()
            # If the username is already in the database, show an error message
            if user:
                return render_template('register.html', error='Username already exists')
            # If the username is not in the database, register the user
            else:
                db = get_db_connection()
                # insert the new user to the database
                db.execute('INSERT INTO user (username, password) VALUES (?, ?)', (username, password))
                db.commit()
                db.close()
                return render_template('login.html')
    # The except block is used to handle errors
    except Exception as e:
        return render_template('register.html', error=str(e))


@app.route("/index", methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route("/arabicModel", methods=['POST'])
def arabic_model():
    search_word = request.form['search_word']
    # استخراج التويتات من تويتر بكلمة بحث معينة
    tweets = twitter_scrape.scrape("ar", str(search_word))
    tweetsContent = [tweet.content for tweet in tweets]
    tweetsLikeCount = [tweet.likeCount for tweet in tweets]
    tweetsUser = [tweet.user.username for tweet in tweets]
    tweetsDate = [tweet.date for tweet in tweets]
    print(tweetsDate[0])

    deserialized_model = pickle.load(open("assets/ARmodel.sav", 'rb'))
    output = deserialized_model.predict(tweetsContent)
    # تحويل النتائج إلى كلمات بحثية
   
    db = get_db_connection()
    
    # تحميل النموذج من ملف

        # db.execute("INSERT INTO datacollector (text) VALUES (?)",
        #     (tweetsContent[i])
        #     )
    converted = list(map(convert_to_int, output))
    
    data = []
    for i in range(len(output)):
        row = dict(tweetUser=tweetsUser[i], tweetContent=tweetsContent[i],
                   tweetLikeCount=tweetsLikeCount[i], tweetDate=tweetsDate[i], tweetProcessed=converted[i])
        data.append(row)
    # تحويل النتائج إلى كلمات بحثية
    count = Counter(converted)
    pos_count = count.get(4)
    neg_count = count.get(0)
    neut_count = count.get(2)
    db.execute("INSERT INTO sentimentanalysis (positive,negative) VALUES (?,?)",
            (int(pos_count), int(neg_count))
            )
    db.commit()
    db.close()
    return render_template('index.html', data=data, pos_count=pos_count, neg_count=neg_count, neut_count=neut_count)

@app.route("/faqs")
def faqs():
    return render_template('faqs.html')


@app.route("/aboutUs")
def aboutUs():
    return render_template('aboutUs.html')

@app.route("/feedback")
def feedback():
    return render_template('feedback.html')

def int_to_string(sentiment):
    if sentiment == 0:
        return "Negative"
    elif sentiment == 2:
        return "Neutral"
    else:
        return "Positive"

def convert_to_int(s):
    if s == "neg":
        return 0
    else:
        return 4
    

@app.route("/sentimentanalysis")
def sentiment():
    db = get_db_connection()
    data = db.execute("SELECT * FROM sentimentanalysis").fetchall()
    db.close()
    results = []
    for row in data:
        results.append({"positive": row["positive"], "negative": row["negative"], "time": row["time"]})
    return str(results)

@app.route("/users")
def users():
    db = get_db_connection()
    data = db.execute("SELECT * FROM user").fetchall()
    db.close()
    results = []
    for row in data:
        results.append({"id": row["id"], "username": row["username"], "created": row["created"]})
    return str(results)
    

if __name__ == '__main__':
    app.run(debug=True)