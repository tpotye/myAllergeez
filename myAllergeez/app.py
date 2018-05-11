# coding: utf-8

from flask import Flask
from flaskext.mysql import MySQL
from flask import Flask,request
from flask import g, session, request, url_for, flash
from flask import redirect, render_template, json
from flask_oauthlib.client import OAuth
from werkzeug import generate_password_hash, check_password_hash
import requests
import oauth2
import os
import json
import urllib


app = Flask(__name__)
app.secret_key = os.urandom(24)
mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'myallergeez'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showLogin')
def showLogin():
    return render_template('login.html', message=request.args.get('message'))

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        if request.form['login'] == "Login":
            try:
                username = request.form['inputUsername']
                password = request.form['inputPassword']

                conn = mysql.connect
                cursor = conn.cursor()
                cursor.callproc('sp_validateUser', [username])
                data = cursor.fetchall()
                
                
                if len(data) > 0:

                    # check credentials in database and see if they match
                    if check_password_hash(str(data[0][2]), password):
                        session['user'] = username
                        twit_un = str(data[0][3])
                        
                    else: # credentials didn't match
                        return redirect(url_for('showLogin', message="Username/password is incorrect"))

                else: # username didn't match
                    return redirect(url_for('showLogin', message="Username/password is incorrect"))

            except Exception as e:
                return redirect(url_for('showLogin', message="An error has occurred"))

            finally:
                cursor.close()
                conn.close()


@app.route('/showSignup')
def showSignup():
    return render_template('signup.html', message=request.args.get('message'))

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['inputName']
    username = request.form['inputUsername']
    password = request.form['inputPassword']

    try:
        conn = mysql.connect
        cursor = conn.cursor()
        hashed_password = generate_password_hash(password)
        cursor.callproc('sp_createUser', [name, username, hashed_password])
        data = cursor.fetchall()

        if name and username and password and request.method == 'POST':
            if len(data) is 0:
                conn.commit()
                return redirect(url_for('showLogin', message="Successfully signed up!"))

            else:
                return redirect(url_for('showSignup', message="Username already exists! Enter a valid username"))

    except Exception as e:
        return redirect(url_for('showSignup'))

    finally:
        cursor.close()
        conn.close()

#https://ndb.nal.usda.gov/ndb/search/list to find the numbers
#https://ndb.nal.usda.gov/ndb/doc/apilist/API-FOOD-REPORTV2.md
#api key for ndb: YKQXoSOyvWFcan8H0FPsRIxBAMtsKtPomkGemRTE

@app.route('/showSearch')
def showSearch():
    return render_template('search.html', message=request.args.get('message'))

@app.route('/food', methods=['GET', 'POST'])
def food():

   #ndb api
    num= request.form['upc']
    a1= request.form['allergy1']
    a2= request.form['allergy2']
    a3= request.form['allergy3']
    a4= request.form['allergy4']
    a5= request.form['allergy5']
    
    url='https://api.nal.usda.gov/ndb/V2/reports?ndbno='+ num +'&type=f&format=json&api_key=YKQXoSOyvWFcan8H0FPsRIxBAMtsKtPomkGemRTE'
    response = requests.get(url)
    results= json.loads(response.content.decode('utf-8'))
    ingredients = results['foods']
    
    if a1 in str(ingredients) or a2 in str(ingredients) or a3 in str(ingredients) or a4 in str(ingredients) or a5 in str(ingredients):
        message = "DO NOT EAT THIS" 
    else:
        message = "THIS IS SAFE TO EAT"
    
    if a1 in str(ingredients):
        ing = a1
        url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSkey72Qkh2n1Gi3FBBpKvfLGzT307cIgrSIFHIwd12eTxT93oO"
    elif a2 in str(ingredients):
        ing = a2
        url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSkey72Qkh2n1Gi3FBBpKvfLGzT307cIgrSIFHIwd12eTxT93oO"
    elif a3 in str(ingredients):
        ing = a3
        url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSkey72Qkh2n1Gi3FBBpKvfLGzT307cIgrSIFHIwd12eTxT93oO"
    elif a4 in str(ingredients):
        ing = a4
        url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSkey72Qkh2n1Gi3FBBpKvfLGzT307cIgrSIFHIwd12eTxT93oO"
    elif a5 in str(ingredients):
        ing = a5
        url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSkey72Qkh2n1Gi3FBBpKvfLGzT307cIgrSIFHIwd12eTxT93oO"
    else:
        ing = "No allergies found"
        url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTcfOwXuUL3U6VVwHGSNZhmZelFpcIb3mLYy5BayUgl1Vubsz_l"
    return render_template('food.html', result=ingredients, answer= message, why= ing, img= url)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
