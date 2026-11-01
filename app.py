from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_wtf.csrf import CSRFProtect
import sqlite3
import os
import secrets

app = Flask(__name__)
# La clé de session vient de l'environnement ou est générée aléatoirement :
# aucun secret n'est écrit en dur dans le code
_session_key = os.environ.get("APP_KEY") or secrets.token_hex(32)
app.config.update(SECRET_KEY=_session_key)
csrf = CSRFProtect(app)

DB_PATH = os.path.join(os.path.dirname(__file__), "tasks.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


init_db()


@app.route("/", methods=["GET"])
def index():
    conn = get_db()
    tasks = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()
    if title:
        conn = get_db()
        conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        conn.commit()
        conn.close()
    return redirect(url_for("index"))


@app.route("/complete/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    conn = get_db()
    conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


@app.route("/api/tasks", methods=["GET"])
def api_tasks():
    conn = get_db()
    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return jsonify([dict(row) for row in tasks])


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)