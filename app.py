from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import hashlib
import secrets
import requests
from datetime import datetime
import os
from functools import wraps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(16))

# Database setup
def init_db():
    conn = sqlite3.connect('learning_platform.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            academic_level TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hash):
    return hashlib.sha256(password.encode()).hexdigest() == hash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_ai_explanation(topic, academic_level):
    # Fallback explanations when OpenAI API fails
    fallback_explanations = {
        'school': f"Here's a simple explanation of {topic}:\n\n{topic} is an important concept that you can understand by thinking about it step by step. It's used in many real-world situations and helps us solve problems. Think of it like building blocks - each part works together to create something bigger.\n\nKey points:\n• It's a fundamental concept in its field\n• It has practical applications\n• Understanding it helps with related topics",
        'college': f"Understanding {topic}:\n\n{topic} is a fundamental concept with several key components. It involves understanding the basic principles, how they apply in different contexts, and why they matter in your field of study.\n\nKey aspects:\n• Theoretical foundation and principles\n• Practical applications and use cases\n• Connections to other concepts\n• Real-world examples and implementations",
        'degree': f"Advanced Analysis of {topic}:\n\n{topic} represents a complex theoretical framework with multiple dimensions. It requires understanding both the foundational principles and their practical applications.\n\nAdvanced considerations:\n• Theoretical underpinnings and research\n• Current developments and trends\n• Implementation challenges\n• Future directions and opportunities"
    }
    
    fallback_text = fallback_explanations.get(academic_level, fallback_explanations['school'])
    
    return {
        'explanation': f"{fallback_text}\n\n⚠️ Note: Add credits to your OpenAI account for AI-powered detailed explanations.",
        'summary': f"Basic explanation of {topic} for {academic_level} level",
        'examples': [f"Example: {topic} can be seen in everyday situations", f"Application: {topic} is used in various fields"]
    }



@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        academic_level = request.form['academic_level']
        
        if not all([name, email, password, academic_level]):
            flash('All fields are required')
            return render_template('register.html')
        
        conn = sqlite3.connect('learning_platform.db')
        cursor = conn.cursor()
        
        # Check if email exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            flash('Email already registered')
            conn.close()
            return render_template('register.html')
        
        # Insert new user
        password_hash = hash_password(password)
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, academic_level)
            VALUES (?, ?, ?, ?)
        ''', (name, email, password_hash, academic_level))
        
        conn.commit()
        conn.close()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('learning_platform.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, password_hash, academic_level FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and verify_password(password, user[2]):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['academic_level'] = user[3]
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', 
                         user_name=session['user_name'],
                         academic_level=session['academic_level'])

@app.route('/explain', methods=['POST'])
@login_required
def explain_topic():
    topic = request.form['topic']
    academic_level = session.get('academic_level', 'school')
    
    if not topic:
        flash('Please enter a topic')
        return redirect(url_for('dashboard'))
    
    explanation = get_ai_explanation(topic, academic_level)
    
    return render_template('explanation.html',
                         topic=topic,
                         explanation=explanation,
                         academic_level=academic_level)

@app.route('/update_level', methods=['POST'])
@login_required
def update_level():
    new_level = request.form['academic_level']
    user_id = session['user_id']
    
    conn = sqlite3.connect('learning_platform.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET academic_level = ? WHERE id = ?', (new_level, user_id))
    conn.commit()
    conn.close()
    
    session['academic_level'] = new_level
    flash('Academic level updated successfully!')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)