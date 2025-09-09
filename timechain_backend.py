from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, time

app = Flask(__name__)
CORS(app)  # allow frontend to talk to backend

DB = "timechain.db"

# --- Helpers ---
def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        # reports table
        c.execute('''CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            reporter TEXT,
            description TEXT,
            category TEXT,
            location TEXT,
            status TEXT,
            acceptedBy TEXT,
            createdAt INTEGER
        )''')
        # points table
        c.execute('''CREATE TABLE IF NOT EXISTS points (
            name TEXT,
            type TEXT, -- reporter or ngo
            score INTEGER,
            PRIMARY KEY(name, type)
        )''')
        conn.commit()


def add_points(name, type_, pts):
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT score FROM points WHERE name=? AND type=?", (name, type_))
        row = c.fetchone()
        if row:
            new_score = row[0] + pts
            c.execute("UPDATE points SET score=? WHERE name=? AND type=?", (new_score, name, type_))
        else:
            c.execute("INSERT INTO points (name, type, score) VALUES (?,?,?)", (name, type_, pts))
        conn.commit()


# --- API Routes ---
@app.route("/reports", methods=["GET"])
def get_reports():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM reports")
        rows = c.fetchall()
    reports = [dict(id=r[0], reporter=r[1], description=r[2], category=r[3],
                    location=r[4], status=r[5], acceptedBy=r[6], createdAt=r[7]) for r in rows]
    return jsonify(reports)


@app.route("/reports", methods=["POST"])
def submit_report():
    data = request.json
    rid = f"r_{int(time.time()*1000)}"
    reporter, desc, cat, loc = data.get("reporter"), data.get("description"), data.get("category"), data.get("location")
    if not reporter or not desc:
        return jsonify({"error":"Missing name/description"}), 400

    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO reports VALUES (?,?,?,?,?,?,?,?)",
                  (rid, reporter, desc, cat, loc, "pending", None, int(time.time())))
        conn.commit()

    # scoring
    pts = 10
    if cat == "health": pts = 30
    elif cat == "sanitation": pts = 20
    add_points(reporter, "reporter", pts)

    return jsonify({"success": True, "points": pts, "id": rid})


@app.route("/reports/<rid>/accept", methods=["POST"])
def accept_report(rid):
    data = request.json
    ngo = data.get("ngo")
    if not ngo: return jsonify({"error":"Missing NGO name"}), 400

    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("UPDATE reports SET status=?, acceptedBy=? WHERE id=?", ("in_progress", ngo, rid))
        conn.commit()

    add_points(ngo, "ngo", 5)
    return jsonify({"success": True, "points": 5})


@app.route("/reports/<rid>/solve", methods=["POST"])
def solve_report(rid):
    data = request.json
    ngo = data.get("ngo")
    if not ngo: return jsonify({"error":"Missing NGO name"}), 400

    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("UPDATE reports SET status=? WHERE id=?", ("solved", rid))
        conn.commit()

    add_points(ngo, "ngo", 20)
    return jsonify({"success": True, "points": 20})


@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT name, score FROM points WHERE type='reporter' ORDER BY score DESC")
        reporters = c.fetchall()
        c.execute("SELECT name, score FROM points WHERE type='ngo' ORDER BY score DESC")
        ngos = c.fetchall()
    return jsonify({
        "reporters": [{"name":n,"score":s} for n,s in reporters],
        "ngos": [{"name":n,"score":s} for n,s in ngos]
    })


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
