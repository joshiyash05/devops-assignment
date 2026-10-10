import sqlite3
from datetime import date

from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            height_cm REAL NOT NULL,
            weight_kg REAL NOT NULL,
            program TEXT NOT NULL,
            membership_end TEXT
        );

        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            workout_type TEXT NOT NULL,
            duration_min INTEGER NOT NULL,
            notes TEXT,
            FOREIGN KEY (client_id) REFERENCES clients (id)
        );
        """
    )
    db.commit()


def row_to_dict(row):
    return dict(row) if row is not None else None


def list_clients():
    rows = get_db().execute("SELECT * FROM clients ORDER BY id").fetchall()
    return [row_to_dict(row) for row in rows]


def get_client(client_id):
    row = get_db().execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
    return row_to_dict(row)


def create_client(payload):
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO clients (name, age, height_cm, weight_kg, program, membership_end)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            payload["name"].strip(),
            int(payload["age"]),
            float(payload["height_cm"]),
            float(payload["weight_kg"]),
            payload.get("program", "Beginner"),
            payload.get("membership_end"),
        ),
    )
    db.commit()
    return get_client(cursor.lastrowid)


def list_workouts(client_id):
    rows = (
        get_db()
        .execute(
            "SELECT * FROM workouts WHERE client_id = ? ORDER BY date DESC, id DESC",
            (client_id,),
        )
        .fetchall()
    )
    return [row_to_dict(row) for row in rows]


def create_workout(client_id, payload):
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO workouts (client_id, date, workout_type, duration_min, notes)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            client_id,
            payload.get("date") or date.today().isoformat(),
            payload["workout_type"].strip(),
            int(payload["duration_min"]),
            payload.get("notes", ""),
        ),
    )
    db.commit()
    row = db.execute("SELECT * FROM workouts WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return row_to_dict(row)
