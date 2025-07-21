import sqlite3
DB_NAME = 'tasks.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            owner TEXT,
            status TEXT,
            due_date TEXT,
            notes TEXT,
            completed INTEGER DEFAULT 0,
            project TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_task(task):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO tasks (title, owner, status, due_date, notes, completed, project) VALUES (?, ?, ?, ?, ?, ?, ?)',
              (task['task'], task['owner'], task['status'], task['due'], task['notes'], 0, task.get('project', 'learning')))
    conn.commit()
    conn.close()

def get_tasks(project=None):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    if project:
        c.execute('SELECT id, title, owner, status, due_date, notes, completed, project FROM tasks WHERE project=?', (project,))
    else:
        c.execute('SELECT id, title, owner, status, due_date, notes, completed, project FROM tasks')
    rows = c.fetchall()
    conn.close()
    return [
        {
            'id': row[0], 'task': row[1], 'owner': row[2], 'status': row[3],
            'due': row[4], 'notes': row[5], 'completed': row[6], 'project': row[7]
        } for row in rows
    ]

def update_task(task_id, **kwargs):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    for k, v in kwargs.items():
        c.execute(f'UPDATE tasks SET {k}=? WHERE id=?', (v, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE id=?', (task_id,))
    conn.commit()
    conn.close() 