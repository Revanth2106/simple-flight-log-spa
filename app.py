from flask import Flask, render_template, request, jsonify, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "simple_secret_key"

DATABASE = "flight_logs.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def setup_database():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS flight_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tailNumber TEXT NOT NULL,
            flightID TEXT NOT NULL,
            takeoff TEXT NOT NULL,
            landing TEXT NOT NULL,
            duration TEXT NOT NULL
        )
    """)

    admin = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        ("admin",)
    ).fetchone()

    if admin is None:
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", generate_password_hash("admin123"))
        )

    conn.commit()
    conn.close()


def login_required():
    return "username" in session


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data["username"]
    password = data["password"]

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        session["username"] = username
        return jsonify({"success": True})

    return jsonify({"success": False, "message": "Invalid username or password"})


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})


@app.route("/flightlogs", methods=["GET"])
def get_flight_logs():
    if not login_required():
        return jsonify({"error": "Not logged in"}), 401

    flightID = request.args.get("flightID", "")

    conn = get_db()

    if flightID:
        logs = conn.execute(
            "SELECT * FROM flight_logs WHERE flightID LIKE ? ORDER BY id DESC",
            ("%" + flightID + "%",)
        ).fetchall()
    else:
        logs = conn.execute(
            "SELECT * FROM flight_logs ORDER BY id DESC"
        ).fetchall()

    conn.close()

    return jsonify([dict(log) for log in logs])


@app.route("/flightlogs", methods=["POST"])
def create_flight_log():
    if not login_required():
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()

    conn = get_db()
    conn.execute("""
        INSERT INTO flight_logs 
        (tailNumber, flightID, takeoff, landing, duration)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data["tailNumber"],
        data["flightID"],
        data["takeoff"],
        data["landing"],
        data["duration"]
    ))

    conn.commit()
    conn.close()

    return jsonify({"success": True})


@app.route("/flightlogs/<int:id>", methods=["PUT"])
def update_flight_log(id):
    if not login_required():
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()

    conn = get_db()
    conn.execute("""
        UPDATE flight_logs
        SET tailNumber = ?, flightID = ?, takeoff = ?, landing = ?, duration = ?
        WHERE id = ?
    """, (
        data["tailNumber"],
        data["flightID"],
        data["takeoff"],
        data["landing"],
        data["duration"],
        id
    ))

    conn.commit()
    conn.close()

    return jsonify({"success": True})


@app.route("/flightlogs/<int:id>", methods=["DELETE"])
def delete_flight_log(id):
    if not login_required():
        return jsonify({"error": "Not logged in"}), 401

    conn = get_db()
    conn.execute("DELETE FROM flight_logs WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"success": True})


@app.route("/users", methods=["POST"])
def create_user():
    if not login_required():
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()

    conn = get_db()

    try:
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (data["username"], generate_password_hash(data["password"]))
        )
        conn.commit()
        result = {"success": True}
    except sqlite3.IntegrityError:
        result = {"success": False, "message": "Username already exists"}

    conn.close()
    return jsonify(result)


@app.route("/users/<int:id>", methods=["DELETE"])
def delete_user(id):
    if not login_required():
        return jsonify({"error": "Not logged in"}), 401

    conn = get_db()
    conn.execute("DELETE FROM users WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"success": True})


if __name__ == "__main__":
    setup_database()
    app.run(debug=True)
