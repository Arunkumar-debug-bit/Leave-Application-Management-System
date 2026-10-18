from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from pathlib import Path
from functools import wraps

app = Flask(__name__)
app.secret_key = "change-this-demo-secret"
DB = Path(__file__).with_name("leave_app.db")

def connect():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS leaves (
        id INTEGER PRIMARY KEY AUTOINCREMENT, student_name TEXT NOT NULL,
        student_id TEXT NOT NULL, leave_type TEXT NOT NULL, start_date TEXT NOT NULL,
        end_date TEXT NOT NULL, reason TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Pending',
        submitted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, reviewed_by TEXT, review_note TEXT)""")

def required(role=None):
    def deco(fn):
        @wraps(fn)
        def wrapped(*a, **kw):
            if "role" not in session:
                return redirect(url_for("login"))
            if role and session["role"] != role:
                flash("You don't have permission to do that.", "error")
                return redirect(url_for("dashboard"))
            return fn(*a, **kw)
        return wrapped
    return deco

@app.route("/")
def home():
    return redirect(url_for("dashboard" if "role" in session else "login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        role = request.form.get("role", "student")
        sid = request.form.get("student_id", "").strip() or name.upper().replace(" ", "")
        if not name or role not in ("student", "faculty"):
            flash("Enter your name and choose a valid role.", "error")
            return render_template("login.html")
        session.clear()
        session.update(name=name, role=role, student_id=sid)
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@required()
def dashboard():
    with connect() as c:
        if session["role"] == "student":
            leaves = c.execute("SELECT * FROM leaves WHERE student_id=? ORDER BY id DESC", (session["student_id"],)).fetchall()
        else:
            leaves = c.execute("SELECT * FROM leaves ORDER BY id DESC").fetchall()
        stats = {k: c.execute("SELECT COUNT(*) FROM leaves" + (" WHERE status=?" if k != "total" else ""),
                              (() if k == "total" else (v,))).fetchone()[0]
                 for k, v in [("total", None), ("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")]}
    return render_template("dashboard.html", leaves=leaves, stats=stats)

@app.route("/apply", methods=["GET", "POST"])
@required("student")
def apply():
    if request.method == "POST":
        typ, start, end, reason = (request.form.get(x, "").strip() for x in ("leave_type", "start_date", "end_date", "reason"))
        if not all([typ, start, end, reason]):
            flash("Please complete every field.", "error")
        elif end < start:
            flash("End date cannot be before start date.", "error")
        else:
            with connect() as c:
                c.execute("INSERT INTO leaves(student_name,student_id,leave_type,start_date,end_date,reason) VALUES(?,?,?,?,?,?)",
                          (session["name"], session["student_id"], typ, start, end, reason))
            flash("Leave application submitted.", "success")
            return redirect(url_for("dashboard"))
    return render_template("apply.html")

@app.route("/review/<int:leave_id>", methods=["POST"])
@required("faculty")
def review(leave_id):
    status = request.form.get("status")
    if status not in ("Approved", "Rejected"):
        flash("Invalid status.", "error")
    else:
        with connect() as c:
            c.execute("UPDATE leaves SET status=?, reviewed_by=?, review_note=? WHERE id=? AND status='Pending'",
                      (status, session["name"], request.form.get("review_note", "").strip(), leave_id))
        flash("Review saved.", "success")
    return redirect(url_for("dashboard"))

@app.route("/withdraw/<int:leave_id>", methods=["POST"])
@required("student")
def withdraw(leave_id):
    with connect() as c:
        c.execute("DELETE FROM leaves WHERE id=? AND student_id=? AND status='Pending'", (leave_id, session["student_id"]))
    flash("Pending request withdrawn if it belonged to you.", "success")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
