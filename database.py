import sqlite3
import os
from datetime import datetime, date, timedelta


class Database:
    def __init__(self, db_path=None):
        if db_path is None:
            home = os.path.expanduser("~")
            app_dir = os.path.join(home, ".pomodoro-timer")
            os.makedirs(app_dir, exist_ok=True)
            db_path = os.path.join(app_dir, "pomodoro.db")

        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                estimated_pomodoros INTEGER DEFAULT 1,
                completed_pomodoros INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                completed_at TEXT,
                is_completed INTEGER DEFAULT 0
            )
        """)

        # Pomodoro records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pomodoro_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                duration_minutes INTEGER NOT NULL,
                completed_at TEXT NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
        """)

        conn.commit()
        conn.close()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    # Task operations
    def create_task(self, name, estimated_pomodoros=1):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (name, estimated_pomodoros, created_at) VALUES (?, ?, ?)",
            (name, estimated_pomodoros, datetime.now().isoformat())
        )
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id

    def get_tasks(self, include_completed=False):
        conn = self._get_conn()
        cursor = conn.cursor()
        if include_completed:
            cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        else:
            cursor.execute("SELECT * FROM tasks WHERE is_completed = 0 ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_today_tasks(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        today = date.today().isoformat()
        cursor.execute(
            "SELECT * FROM tasks WHERE date(created_at) = ? ORDER BY created_at DESC",
            (today,)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows

    def update_task_progress(self, task_id):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET completed_pomodoros = completed_pomodoros + 1 WHERE id = ?",
            (task_id,)
        )
        conn.commit()
        conn.close()

    def complete_task(self, task_id):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET is_completed = 1, completed_at = ? WHERE id = ?",
            (datetime.now().isoformat(), task_id)
        )
        conn.commit()
        conn.close()

    def delete_task(self, task_id):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()

    # Pomodoro record operations
    def add_pomodoro_record(self, task_id, duration_minutes):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO pomodoro_records (task_id, duration_minutes, completed_at) VALUES (?, ?, ?)",
            (task_id, duration_minutes, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

    def get_today_pomodoro_count(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        today = date.today().isoformat()
        cursor.execute(
            "SELECT COUNT(*) FROM pomodoro_records WHERE date(completed_at) = ?",
            (today,)
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_week_pomodoro_count(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        week_ago = (date.today() - timedelta(days=7)).isoformat()
        cursor.execute(
            "SELECT COUNT(*) FROM pomodoro_records WHERE date(completed_at) >= ?",
            (week_ago,)
        )
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_pomodoro_history(self, limit=50):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT pr.*, t.name FROM pomodoro_records pr "
            "LEFT JOIN tasks t ON pr.task_id = t.id "
            "ORDER BY pr.completed_at DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows