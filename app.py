from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime

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
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            name TEXT NOT NULL,
            phone_code TEXT DEFAULT '+62',
            phone_number TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS shopping_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            quantity TEXT DEFAULT '1',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT DEFAULT '',
            priority TEXT DEFAULT 'normal',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS family_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS annual_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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


@app.route('/')
def index():
    return render_template('index.html')


# ===================== TASKS =====================
@app.route('/api/tasks', methods=['GET', 'POST'])
def tasks():
    if request.method == 'GET':
        return jsonify_list(get_db().execute(
            'SELECT * FROM tasks ORDER BY created_at DESC').fetchall())
    data = request.get_json(force=True)
    db = get_db()
    db.execute(
        'INSERT INTO tasks (title, location, assignee, due_date, progress, notes) VALUES (?,?,?,?,?,?)',
        [data['title'], data.get('location', ''), data.get('assignee', ''),
         data.get('due_date', ''), data.get('progress', 0), data.get('notes', '')])
    db.commit()
    new_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': new_id}), 201


@app.route('/api/tasks/<int:tid>', methods=['PUT', 'DELETE'])
def task(tid):
    db = get_db()
    if request.method == 'DELETE':
        db.execute('DELETE FROM tasks WHERE id=?', [tid])
        db.commit()
        db.close()
        return jsonify({'status': 'ok'})
    data = request.get_json(force=True)
    db.execute(
        'UPDATE tasks SET title=?, location=?, assignee=?, due_date=?, progress=?, notes=? WHERE id=?',
        [data['title'], data.get('location', ''), data.get('assignee', ''),
         data.get('due_date', ''), data.get('progress', 0), data.get('notes', ''), tid])
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


# ===================== STICKY NOTES =====================
@app.route('/api/sticky-notes', methods=['GET', 'POST'])
def sticky_notes():
    if request.method == 'GET':
        return jsonify_list(get_db().execute(
            'SELECT * FROM sticky_notes ORDER BY created_at DESC').fetchall())
    data = request.get_json(force=True)
    db = get_db()
    db.execute('INSERT INTO sticky_notes (content) VALUES (?)', [data['content']])
    db.commit()
    new_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': new_id}), 201


@app.route('/api/sticky-notes/<int:nid>', methods=['DELETE'])
def sticky_note(nid):
    db = get_db()
    db.execute('DELETE FROM sticky_notes WHERE id=?', [nid])
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


# ===================== TRANSACTIONS =====================
@app.route('/api/transactions', methods=['GET', 'POST'])
def transactions():
    if request.method == 'GET':
        return jsonify_list(get_db().execute(
            'SELECT * FROM transactions ORDER BY created_at DESC').fetchall())
    data = request.get_json(force=True)
    db = get_db()
    db.execute(
        'INSERT INTO transactions (amount, type, category, asset, notes, transaction_date) VALUES (?,?,?,?,?,?)',
        [data.get('amount', 0), data.get('type', 'Pengeluaran'),
         data.get('category', ''), data.get('asset', ''),
         data.get('notes', ''), data.get('transaction_date', '')])
    db.commit()
    new_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': new_id}), 201


@app.route('/api/transactions/<int:txn_id>', methods=['DELETE'])
def transaction(txn_id):
    db = get_db()
    db.execute('DELETE FROM transactions WHERE id=?', [txn_id])
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


# ===================== EMERGENCY CONTACTS =====================
@app.route('/api/emergency-contacts', methods=['GET', 'POST'])
def emergency_contacts():
    if request.method == 'GET':
        return jsonify_list(get_db().execute(
            'SELECT * FROM emergency_contacts ORDER BY created_at DESC').fetchall())
    data = request.get_json(force=True)
    db = get_db()
    db.execute(
        'INSERT INTO emergency_contacts (name, phone_code, phone_number) VALUES (?,?,?)',
        [data['name'], data.get('phone_code', '+62'), data['phone_number']])
    db.commit()
    new_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': new_id}), 201


@app.route('/api/emergency-contacts/<int:cid>', methods=['DELETE'])
def emergency_contact(cid):
    db = get_db()
    db.execute('DELETE FROM emergency_contacts WHERE id=?', [cid])
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


# ===================== SHOPPING ITEMS =====================
@app.route('/api/shopping-items', methods=['GET', 'POST'])
def shopping_items():
    if request.method == 'GET':
        return jsonify_list(get_db().execute(
            'SELECT * FROM shopping_items ORDER BY created_at DESC').fetchall())
    data = request.get_json(force=True)
    db = get_db()
    db.execute(
        'INSERT INTO shopping_items (item_name, quantity) VALUES (?,?)',
        [data['item_name'], data.get('quantity', '1')])
    db.commit()
    new_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': new_id}), 201


@app.route('/api/shopping-items/<int:sid>', methods=['DELETE'])
def shopping_item(sid):
    db = get_db()
    db.execute('DELETE FROM shopping_items WHERE id=?', [sid])
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


# ===================== ANNOUNCEMENTS =====================
@app.route('/api/announcements', methods=['GET', 'POST'])
def announcements():
    if request.method == 'GET':
        return jsonify_list(get_db().execute(
            'SELECT * FROM announcements ORDER BY created_at DESC').fetchall())
    data = request.get_json(force=True)
    db = get_db()
    db.execute(
        'INSERT INTO announcements (title, content, priority) VALUES (?,?,?)',
        [data['title'], data.get('content', ''), data.get('priority', 'normal')])
    db.commit()
    new_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': new_id}), 201


@app.route('/api/announcements/<int:aid>', methods=['DELETE'])
def announcement(aid):
    db = get_db()
    db.execute('DELETE FROM announcements WHERE id=?', [aid])
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


# ===================== FAMILY MEMBERS =====================
@app.route('/api/family-members', methods=['GET', 'POST'])
def family_members():
    if request.method == 'GET':
        return jsonify_list(get_db().execute(
            'SELECT * FROM family_members ORDER BY created_at DESC').fetchall())
    data = request.get_json(force=True)
    db = get_db()
    db.execute(
        'INSERT INTO family_members (name, role) VALUES (?,?)',
        [data['name'], data.get('role', '')])
    db.commit()
    new_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': new_id}), 201


@app.route('/api/family-members/<int:mid>', methods=['DELETE'])
def family_member(mid):
    db = get_db()
    db.execute('DELETE FROM family_members WHERE id=?', [mid])
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


# ===================== ANNUAL EVENTS =====================
@app.route('/api/annual-events', methods=['GET', 'POST'])
def annual_events():
    if request.method == 'GET':
        return jsonify_list(get_db().execute(
            'SELECT * FROM annual_events ORDER BY created_at DESC').fetchall())
    data = request.get_json(force=True)
    db = get_db()
    db.execute(
        'INSERT INTO annual_events (name, event_date, notes) VALUES (?,?,?)',
        [data['name'], data.get('event_date', ''), data.get('notes', '')])
    db.commit()
    new_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
    db.close()
    return jsonify({'status': 'ok', 'id': new_id}), 201


@app.route('/api/annual-events/<int:eid>', methods=['DELETE'])
def annual_event(eid):
    db = get_db()
    db.execute('DELETE FROM annual_events WHERE id=?', [eid])
    db.commit()
    db.close()
    return jsonify({'status': 'ok'})


# ===================== DASHBOARD SUMMARY =====================
@app.route('/api/dashboard')
def dashboard():
    db = get_db()
    data = {
        'tasks': len(db.execute('SELECT id FROM tasks').fetchall()),
        'tasks_completed': len(db.execute('SELECT id FROM tasks WHERE progress=100').fetchall()),
        'sticky_notes': len(db.execute('SELECT id FROM sticky_notes').fetchall()),
        'transactions': len(db.execute('SELECT id FROM transactions').fetchall()),
        'contacts': len(db.execute('SELECT id FROM emergency_contacts').fetchall()),
        'shopping_items': len(db.execute('SELECT id FROM shopping_items').fetchall()),
        'announcements': len(db.execute('SELECT id FROM announcements').fetchall()),
        'family_members': len(db.execute('SELECT id FROM family_members').fetchall()),
        'events': len(db.execute('SELECT id FROM annual_events').fetchall()),
        'recent_tasks': [dict(r) for r in db.execute(
            'SELECT title, progress FROM tasks ORDER BY created_at DESC LIMIT 5').fetchall()],
        'recent_announcements': [dict(r) for r in db.execute(
            'SELECT title, created_at FROM announcements ORDER BY created_at DESC LIMIT 3').fetchall()],
    }
    db.close()
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
