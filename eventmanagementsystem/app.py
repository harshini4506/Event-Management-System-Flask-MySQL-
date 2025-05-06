from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
from db import get_db, fetch_tables

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['email']
        pwd = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (user, pwd))
        account = cursor.fetchone()
        if account:
            session['email'] = user
            flash('Login successful!', 'success')
            return redirect('/dashboard')
        else:
            flash('Invalid login credentials.', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        pwd = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash('User already exists. Please login.', 'warning')
            return redirect('/login')
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, pwd))
        db.commit()
        flash('Signup successful! Please log in.', 'success')
        return redirect('/login')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    flash('Logged out successfully.', 'info')
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    db = get_db()
    tables = fetch_tables(db)
    return render_template('dashboard.html', tables=tables)

@app.route('/table/<table_name>')
def view_table(table_name):
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page

    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total_rows = cursor.fetchone()[0]

    cursor.execute(f"SELECT * FROM {table_name} LIMIT %s OFFSET %s", (per_page, offset))
    rows = cursor.fetchall()
    columns = [i[0] for i in cursor.description]
    total_pages = (total_rows + per_page - 1) // per_page

    return render_template('dashboard.html', tables=fetch_tables(db), data=rows, columns=columns,
                           selected_table=table_name, page=page, total_pages=total_pages)

@app.route('/add/<table_name>', methods=['POST'])
def add_entry(table_name):
    db = get_db()
    cursor = db.cursor()
    columns = request.form.keys()
    values = [request.form[col] for col in columns]
    placeholders = ', '.join(['%s'] * len(values))
    query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    cursor.execute(query, values)
    db.commit()
    flash('Entry added successfully!', 'success')
    return redirect(f'/table/{table_name}')

if __name__ == '__main__':
    app.run(debug=True)
