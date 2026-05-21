from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())
DATABASE = 'database.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 0,
            title TEXT NOT NULL,
            location TEXT DEFAULT '',
            assignee TEXT DEFAULT '',
            due_date TEXT DEFAULT '',
            progress INTEGER DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS sticky_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 0,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 0,
            amount REAL NOT NULL DEFAULT 0,
            type TEXT NOT NULL DEFAULT 'Pengeluaran',
            category TEXT DEFAULT '',
            asset TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            transaction_date TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS emergency_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 0,
            name TEXT NOT NULL,
            phone_code TEXT DEFAULT '+62',
            phone_number TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS shopping_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 0,
            item_name TEXT NOT NULL,
            quantity TEXT DEFAULT '1',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 0,
            title TEXT NOT NULL,
            content TEXT DEFAULT '',
            priority TEXT DEFAULT 'normal',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS family_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 0,
            name TEXT NOT NULL,
            role TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS annual_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 0,
            name TEXT NOT NULL,
            event_date TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()


with app.app_context():
    init_db()


def jsonify_list(rows):
    return jsonify([dict(r) for r in rows])


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'login_required'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def owner_filter(db, user_id):
    return user_id


# ===================== AUTH =====================

@app.route('/')
def landing():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html', user_name=session.get('user_name'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if not email or not password:
            error = 'Email dan password harus diisi.'
        else:
            db = get_db()
            user = db.execute('SELECT * FROM users WHERE email = ?', [email]).fetchone()
            db.close()
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_email'] = user['email']
                return redirect(url_for('dashboard'))
            error = 'Email atau password salah.'
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    error = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        if not name or not email or not password:
            error = 'Semua field harus diisi.'
        elif password != confirm:
            error = 'Konfirmasi password tidak cocok.'
        elif len(password) < 6:
            error = 'Password minimal 6 karakter.'
        else:
            db = get_db()
            existing = db.execute('SELECT id FROM users WHERE email = ?', [email]).fetchone()
            if existing:
                error = 'Email sudah terdaftar.'
            else:
                hashed = generate_password_hash(password)
                db.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)',
                           [name, email, hashed])
                db.commit()
                user = db.execute('SELECT * FROM users WHERE email = ?', [email]).fetchone()
                db.close()
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_email'] = user['email']
                return redirect(url_for('dashboard'))
            db.close()
    return render_template('register.html', error=error)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))


@app.route('/api/me')
@login_required
def api_me():
    return jsonify({'id': session['user_id'], 'name': session['user_name'], 'email': session['user_email']})


# ===================== TASKS =====================

@app.route('/api/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    uid = session['user_id']
    if request.method == 'GET':
        return jsonify_list(get_db().execute(
            'SELECT * FROM tasks WHERE user_id=? ORDER BY created_at DESC', [uid]).fetchall())
    data = request.get_json(force=True)
    db = get_db()
    db.execute(
        'INSERT INTO tasks (user_id, title, location, assignee, due_date, progress, notes) VALUES (?,?,?,?,?,?,?)',
        [uid, data['title'], data.get('location', ''), data.get('assignee', ''),
         data.get('due_date', ''), data.get('progress', 0), data.get('notes', '')])
    db.commit()
    new_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': new_id}), 201


@app.route('/api/tasks/<int:tid>', methods=['PUT', 'DELETE'])
@login_required
def task(tid):
    uid = session['user_id']
    db = get_db()
    if request.method == 'DELETE':
        db.execute('DELETE FROM tasks WHERE id=? AND user_id=?', [tid, uid])
        db.commit()
        db.close()
        return jsonify({'status': 'ok'})
    data = request.get_json(force=True)
    db.execute(
        'UPDATE tasks SET title=?, location=?, assignee=?, due_date=?, progress=?, notes=? WHERE id=? AND user_id=?',
        [data['title'], data.get('location', ''), data.get('assignee', ''),
         data.get('due_date', ''), data.get('progress', 0), data.get('notes', ''), tid, uid])
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


# ===================== STICKY NOTES =====================

@app.route('/api/sticky-notes', methods=['GET', 'POST'])
@login_required
def sticky_notes():
    uid = session['user_id']
    if request.method == 'GET':
        return jsonify_list(get_db().execute(
            'SELECT * FROM sticky_notes WHERE user_id=? ORDER BY created_at DESC', [uid]).fetchall())
    data = request.get_json(force=True)
    db = get_db()
    db.execute('INSERT INTO sticky_notes (user_id, content) VALUES (?,?)', [uid, data['content']])
    db.commit()
    new_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': new_id}), 201


@app.route('/api/sticky-notes/<int:nid>', methods=['DELETE'])
@login_required
def sticky_note(nid):
    db = get_db()
    db.execute('DELETE FROM sticky_notes WHERE id=? AND user_id=?', [nid, session['user_id']])
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


# ===================== TRANSACTIONS =====================

@app.route('/api/transactions', methods=['GET', 'POST'])
@login_required
def transactions():
    uid = session['user_id']
    if request.method == 'GET':
        return jsonify_list(get_db().execute(
            'SELECT * FROM transactions WHERE user_id=? ORDER BY created_at DESC', [uid]).fetchall())
    data = request.get_json(force=True)
    db = get_db()
    db.execute(
        'INSERT INTO transactions (user_id, amount, type, category, asset, notes, transaction_date) VALUES (?,?,?,?,?,?,?)',
        [uid, data.get('amount', 0), data.get('type', 'Pengeluaran'),
         data.get('category', ''), data.get('asset', ''),
         data.get('notes', ''), data.get('transaction_date', '')])
    db.commit()
    new_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': new_id}), 201


@app.route('/api/transactions/<int:txn_id>', methods=['DELETE'])
@login_required
def transaction(txn_id):
    db = get_db()
    db.execute('DELETE FROM transactions WHERE id=? AND user_id=?', [txn_id, session['user_id']])
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


# ===================== EMERGENCY CONTACTS =====================

@app.route('/api/emergency-contacts', methods=['GET', 'POST'])
@login_required
def emergency_contacts():
    uid = session['user_id']
    if request.method == 'GET':
        return jsonify_list(get_db().execute(
            'SELECT * FROM emergency_contacts WHERE user_id=? ORDER BY created_at DESC', [uid]).fetchall())
    data = request.get_json(force=True)
    db = get_db()
    db.execute(
        'INSERT INTO emergency_contacts (user_id, name, phone_code, phone_number) VALUES (?,?,?,?)',
        [uid, data['name'], data.get('phone_code', '+62'), data['phone_number']])
    db.commit()
    new_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': new_id}), 201


@app.route('/api/emergency-contacts/<int:cid>', methods=['DELETE'])
@login_required
def emergency_contact(cid):
    db = get_db()
    db.execute('DELETE FROM emergency_contacts WHERE id=? AND user_id=?', [cid, session['user_id']])
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


# ===================== SHOPPING ITEMS =====================

@app.route('/api/shopping-items', methods=['GET', 'POST'])
@login_required
def shopping_items():
    uid = session['user_id']
    if request.method == 'GET':
        return jsonify_list(get_db().execute(
            'SELECT * FROM shopping_items WHERE user_id=? ORDER BY created_at DESC', [uid]).fetchall())
    data = request.get_json(force=True)
    db = get_db()
    db.execute(
        'INSERT INTO shopping_items (user_id, item_name, quantity) VALUES (?,?,?)',
        [uid, data['item_name'], data.get('quantity', '1')])
    db.commit()
    new_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': new_id}), 201


@app.route('/api/shopping-items/<int:sid>', methods=['DELETE'])
@login_required
def shopping_item(sid):
    db = get_db()
    db.execute('DELETE FROM shopping_items WHERE id=? AND user_id=?', [sid, session['user_id']])
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


# ===================== ANNOUNCEMENTS =====================

@app.route('/api/announcements', methods=['GET', 'POST'])
@login_required
def announcements():
    uid = session['user_id']
    if request.method == 'GET':
        return jsonify_list(get_db().execute(
            'SELECT * FROM announcements WHERE user_id=? ORDER BY created_at DESC', [uid]).fetchall())
    data = request.get_json(force=True)
    db = get_db()
    db.execute(
        'INSERT INTO announcements (user_id, title, content, priority) VALUES (?,?,?,?)',
        [uid, data['title'], data.get('content', ''), data.get('priority', 'normal')])
    db.commit()
    new_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': new_id}), 201


@app.route('/api/announcements/<int:aid>', methods=['DELETE'])
@login_required
def announcement(aid):
    db = get_db()
    db.execute('DELETE FROM announcements WHERE id=? AND user_id=?', [aid, session['user_id']])
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


# ===================== FAMILY MEMBERS =====================

@app.route('/api/family-members', methods=['GET', 'POST'])
@login_required
def family_members():
    uid = session['user_id']
    if request.method == 'GET':
        return jsonify_list(get_db().execute(
            'SELECT * FROM family_members WHERE user_id=? ORDER BY created_at DESC', [uid]).fetchall())
    data = request.get_json(force=True)
    db = get_db()
    db.execute(
        'INSERT INTO family_members (user_id, name, role) VALUES (?,?,?)',
        [uid, data['name'], data.get('role', '')])
    db.commit()
    new_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': new_id}), 201


@app.route('/api/family-members/<int:mid>', methods=['DELETE'])
@login_required
def family_member(mid):
    db = get_db()
    db.execute('DELETE FROM family_members WHERE id=? AND user_id=?', [mid, session['user_id']])
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


# ===================== ANNUAL EVENTS =====================

@app.route('/api/annual-events', methods=['GET', 'POST'])
@login_required
def annual_events():
    uid = session['user_id']
    if request.method == 'GET':
        return jsonify_list(get_db().execute(
            'SELECT * FROM annual_events WHERE user_id=? ORDER BY created_at DESC', [uid]).fetchall())
    data = request.get_json(force=True)
    db = get_db()
    db.execute(
        'INSERT INTO annual_events (user_id, name, event_date, notes) VALUES (?,?,?,?)',
        [uid, data['name'], data.get('event_date', ''), data.get('notes', '')])
    db.commit()
    new_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': new_id}), 201


@app.route('/api/annual-events/<int:eid>', methods=['DELETE'])
@login_required
def annual_event(eid):
    db = get_db()
    db.execute('DELETE FROM annual_events WHERE id=? AND user_id=?', [eid, session['user_id']])
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


# ===================== DASHBOARD =====================

@app.route('/api/dashboard')
@login_required
def dashboard_api():
    uid = session['user_id']
    db = get_db()
    data = {
        'tasks': len(db.execute('SELECT id FROM tasks WHERE user_id=?', [uid]).fetchall()),
        'tasks_completed': len(db.execute('SELECT id FROM tasks WHERE user_id=? AND progress=100', [uid]).fetchall()),
        'sticky_notes': len(db.execute('SELECT id FROM sticky_notes WHERE user_id=?', [uid]).fetchall()),
        'transactions': len(db.execute('SELECT id FROM transactions WHERE user_id=?', [uid]).fetchall()),
        'contacts': len(db.execute('SELECT id FROM emergency_contacts WHERE user_id=?', [uid]).fetchall()),
        'shopping_items': len(db.execute('SELECT id FROM shopping_items WHERE user_id=?', [uid]).fetchall()),
        'announcements': len(db.execute('SELECT id FROM announcements WHERE user_id=?', [uid]).fetchall()),
        'family_members': len(db.execute('SELECT id FROM family_members WHERE user_id=?', [uid]).fetchall()),
        'events': len(db.execute('SELECT id FROM annual_events WHERE user_id=?', [uid]).fetchall()),
        'recent_tasks': [dict(r) for r in db.execute(
            'SELECT title, progress FROM tasks WHERE user_id=? ORDER BY created_at DESC LIMIT 5', [uid]).fetchall()],
        'recent_announcements': [dict(r) for r in db.execute(
            'SELECT title, created_at FROM announcements WHERE user_id=? ORDER BY created_at DESC LIMIT 3', [uid]).fetchall()],
    }
    db.close()
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
