from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Главная страница
@app.route('/')
def index():
    if 'user' in session:
        conn = get_db_connection()
        # Получаем сообщения для отображения
        messages = conn.execute("SELECT * FROM messages").fetchall()
        conn.close()
        return render_template('home.html', user=session['user'], messages=messages)
    return redirect(url_for('login'))

# Авторизация пользователя
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        # Уязвимость SQL Injection
        user = conn.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'").fetchone()
        conn.close()
        if user:
            session['user'] = username
            return redirect(url_for('index'))
        return 'Invalid credentials'
    return render_template('login.html')

# Выход
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Поиск пользователя
@app.route('/search', methods=['POST'])
def search():
    if 'user' not in session or session['user'] != 'admin':
        return 'Access denied'
    search_query = request.form['query']
    conn = get_db_connection()
    # Уязвимость SQL Injection
    results = conn.execute(f"SELECT * FROM users WHERE username LIKE '%{search_query}%'").fetchall()
    conn.close()
    return render_template('home.html', results=results, user=session['user'])

# Регистрация нового пользователя (только для администратора)
@app.route('/register', methods=['POST'])
def register():
    if 'user' not in session or session['user'] != 'admin':
        return 'Access denied'
    username = request.form['username']
    password = request.form['password']
    conn = get_db_connection()
    # Уязвимость SQL Injection
    conn.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')")
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Удаление пользователя (только для администратора)
@app.route('/delete', methods=['POST'])
def delete():
    if 'user' not in session or session['user'] != 'admin':
        return 'Access denied'
    user_id = request.form['user_id']
    conn = get_db_connection()
    # Уязвимость SQL Injection
    conn.execute(f"DELETE FROM users WHERE id={user_id}")
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Добавление нового сообщения в чат
@app.route('/post_message', methods=['POST'])
def post_message():
    if 'user' not in session:
        return redirect(url_for('login'))
    username = session['user']
    message = request.form['message']
    conn = get_db_connection()
    # Уязвимость Stored XSS
    conn.execute("INSERT INTO messages (username, message) VALUES (?, ?)", (username, message))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Удаление сообщения из чата (доступно только администратору)
@app.route('/delete_message', methods=['POST'])
def delete_message():
    if 'user' not in session or session['user'] != 'admin':
        return 'Access denied'
    message_id = request.form['message_id']
    conn = get_db_connection()
    conn.execute("DELETE FROM messages WHERE id=?", (message_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
