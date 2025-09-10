# GitHub username: M-Ismail-x2
# Edx username: m-ismail-x2

# pip install -r requirements.txt
# python app.py

import sys
import requests
from flask import Flask, render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medicloud.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

class MedicalHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    condition = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    dosage = db.Column(db.String(150), nullable=False)
    frequency = db.Column(db.String(150), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        Name = request.form['Name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        new_user = User(Name=Name, email=email, password=password)
        if User.query.filter_by(email=email).first():
            flash('Email address already in use. Please choose a different one.', 'danger')
            return render_template('register.html')

        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'user_id' in session:
        id = session['user_id']
    else:
        id = 3 # use example profile
    user = User.query.get(id)
    medical_history = MedicalHistory.query.filter_by(user_id=user.id).all()
    medications = Medication.query.filter_by(user_id=user.id).all()
    return render_template('profile.html', user=user, medical_history=medical_history, medications=medications)

@app.route('/add_history', methods=['GET', 'POST'])
def add_history():
    if not 'user_id' in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        condition = request.form['condition']
        description = request.form['description']
        new_history = MedicalHistory(user_id=session['user_id'], condition=condition, description=description)
        db.session.add(new_history)
        db.session.commit()
        flash('Medical history added!', 'success')
        return redirect(url_for('profile'))
    return render_template('add_history.html')

@app.route('/health_news')
def health_news():
    if not 'user_id' in session:
        return redirect(url_for('login'))
    api_key = 'd258a72b3fc2472bac429e09f6516a03'
    url = f'https://newsapi.org/v2/everything?q=health&language=en&apiKey={api_key}'
    response = requests.get(url)
    data = response.json()

    articles = []
    if data.get('status') == 'ok':
        for article in data.get('articles', []):
            # Filter out articles without necessary details
            if article['title'] and article['description'] and article['url'] and article['title'].lower() != '[removed]':
                articles.append({
                    'title': article['title'],
                    'description': article['description'],
                    'url': article['url'],
                    'urlToImage': article['urlToImage']
                })

    return render_template('news.html', articles=articles)

@app.route('/meals')
def meals():
    if not 'user_id' in session:
        return redirect(url_for('login'))
    try:
        url = 'https://api.spoonacular.com/recipes/complexSearch'
        params = {
            'apiKey': 'd67aeacce2eb4382b2006e6a57cd761b',
            'query': 'health',
            'number': 10
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        meal_data = response.json()
        meals = [
            {
                "id": meal["id"],  # Ensure ID is included
                "name": meal["title"],
                "image": meal["image"]
            }
            for meal in meal_data["results"]
        ]
    except Exception as e:
        flash(f'Could not retrieve meal suggestions: {e}', 'danger')
        meals = []

    return render_template('meals.html', meals=meals)

@app.route('/recipe/<int:recipe_id>')
def recipe(recipe_id):
    api_key = 'd67aeacce2eb4382b2006e6a57cd761b'
    url = f'https://api.spoonacular.com/recipes/{recipe_id}/information'
    params = {'apiKey': api_key}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        recipe_data = response.json()
        return render_template('recipe.html', recipe=recipe_data)
    except Exception as e:
        flash(f'Error fetching recipe information: {e}', 'danger')
        return redirect(url_for('meals'))

@app.route('/nutrition/<int:recipe_id>')
def nutrition(recipe_id):
    api_key = 'd67aeacce2eb4382b2006e6a57cd761b'
    url = f'https://api.spoonacular.com/recipes/{recipe_id}/nutritionWidget.json'
    params = {'apiKey': api_key}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        nutrition_data = response.json()
        return render_template('nutrition.html', nutrition=nutrition_data)
    except Exception as e:
        flash(f'Error fetching nutrition information: {e}', 'danger')
        return redirect(url_for('meals'))

@app.route('/add_medication', methods=['GET', 'POST'])
def add_medication():
    if not 'user_id' in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        dosage = request.form['dosage']
        frequency = request.form['frequency']
        new_medication = Medication(user_id=session['user_id'], name=name, dosage=dosage, frequency=frequency)
        db.session.add(new_medication)
        db.session.commit()
        flash('Medication added!', 'success')
        return redirect(url_for('profile'))
    return render_template('add_medication.html')

@app.route('/symptom_diagnoser', methods=['GET', 'POST'])
def symptom_diagnoser():
    advice = disease_info = treatment_recommendations = None
    flash_messages = []
    if request.method == 'POST':
        symptoms = request.form.get('symptoms', '')
        gender = request.form.get('gender', '')
        age = request.form.get('age', '')
        temp = request.form.get('temp', '')
        bmi = request.form.get('BMI', '')
        sbp = request.form.get('SBP', '')
        dbp = request.form.get('DBP', '')
        # Use Infermedica API (public demo)
        try:
            headers = {
                'App-Id': 'demo',
                'App-Key': 'demo',
                'Content-Type': 'application/json'
            }
            evidence = []
            for s in [x.strip() for x in symptoms.replace(' and ', ',').split(',') if x.strip()]:
                evidence.append({"id": s.lower().replace(' ', '_'), "choice_id": "present"})
            payload = {
                "sex": "male" if gender == "2" else ("female" if gender == "3" else "male"),
                "age": int(age) if age else 30,
                "evidence": evidence
            }
            resp = requests.post('https://api.infermedica.com/v3/diagnoser', headers=headers, data=json.dumps(payload), timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('conditions'):
                    disease_info = ', '.join([c['name'] for c in data['conditions'][:3]])
                    advice = data['conditions'][0]['explanation'] if 'explanation' in data['conditions'][0] else None
                    treatment_recommendations = data['conditions'][0]['common_name'] if 'common_name' in data['conditions'][0] else None
                else:
                    flash_messages.append('No likely condition found. Try different symptoms.')
            else:
                flash_messages.append('Symptom diagnoser service unavailable.')
        except Exception:
            flash_messages.append('Error processing your request. Please try again.')
    return render_template('symptom_diagnoser.html', advice=advice, disease_info=disease_info, treatment_recommendations=treatment_recommendations, flash_messages=flash_messages)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
    host, port = None, None
    if len(sys.argv) > 1 and sys.argv[1] != "debug":
        host = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[1] != "debug":
        port = sys.argv[2]
    
    app.run(host=host, port=port, debug=bool("debug" in sys.argv))
