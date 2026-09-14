import os

from flask import Flask, jsonify, request, send_from_directory
import psycopg
from psycopg.rows import dict_row


app = Flask(__name__, static_folder="static")
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "task_tracker",
    "user": "postgres",
    "password": "NewPassword123",
}


def get_connection():
    return psycopg.connect(**DATABASE_CONFIG, row_factory=dict_row)


@app.get("/")
def index():
    return send_from_directory("static", "index.html")


@app.get("/api/tasks")
def list_tasks():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT id, title, completed, created_at "
            "FROM tasks ORDER BY completed, created_at DESC"
        )
        return jsonify(cur.fetchall())


@app.post("/api/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()

    if not title:
        return jsonify(error="A task title is required."), 400
    if len(title) > 120:
        return jsonify(error="Keep task titles under 120 characters."), 400

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO tasks (title) VALUES (%s) "
            "RETURNING id, title, completed, created_at",
            (title,),
        )
        task = cur.fetchone()

    return jsonify(task), 201


@app.patch("/api/tasks/<int:task_id>")
def update_task(task_id):
    data = request.get_json(silent=True) or {}

    if "completed" not in data or not isinstance(data["completed"], bool):
        return jsonify(error="completed must be true or false."), 400

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            "UPDATE tasks SET completed = %s WHERE id = %s "
            "RETURNING id, title, completed, created_at",
            (data["completed"], task_id),
        )
        task = cur.fetchone()

    if task is None:
        return jsonify(error="Task not found."), 404

    return jsonify(task)


@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("DELETE FROM tasks WHERE id = %s RETURNING id", (task_id,))
        deleted = cur.fetchone()

    if deleted is None:
        return jsonify(error="Task not found."), 404

    return "", 204


if __name__ == "__main__":
    app.run(debug=True)