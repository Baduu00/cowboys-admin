import os
import sqlite3
from functools import wraps
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, g
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "cowboys-dev-secret-change-me")
CORS(app)  # allows the static site (different domain) to call the API

DB_PATH = os.environ.get("DB_PATH", "menu.db")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "cowboys2026")


# ---------- Database ----------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price_100g REAL,
            price_140g REAL,
            price_200g REAL,
            category TEXT DEFAULT 'burger',
            sort_order INTEGER DEFAULT 0
        )
        """
    )
    count = db.execute("SELECT COUNT(*) FROM menu_items").fetchone()[0]
    if count == 0:
        seed = [
            ("Hamburger", 395, 415, 465, "burger", 1),
            ("Sheriff Burger Menü", 465, 490, 520, "burger", 2),
            ("Mushroom Menü", 490, None, 570, "burger", 3),
            ("Ranch Burger Menü", 490, None, 570, "burger", 4),
            ("Cheese Burger Menü", 495, None, 575, "burger", 5),
            ("Hot Chilli Menü", 490, None, 570, "burger", 6),
            ("Chicken Burger Menü", 440, None, None, "burger", 7),
        ]
        db.executemany(
            "INSERT INTO menu_items (name, price_100g, price_140g, price_200g, category, sort_order) VALUES (?,?,?,?,?,?)",
            seed,
        )
        db.commit()
    db.close()


# ---------- Auth ----------

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("admin"))
        error = "Şifre yanlış."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------- Admin UI ----------

@app.route("/")
def index():
    return redirect(url_for("admin") if session.get("logged_in") else url_for("login"))


@app.route("/admin")
@login_required
def admin():
    db = get_db()
    items = db.execute("SELECT * FROM menu_items ORDER BY sort_order, id").fetchall()
    return render_template("admin.html", items=items)


@app.route("/admin/add", methods=["POST"])
@login_required
def admin_add():
    db = get_db()
    db.execute(
        "INSERT INTO menu_items (name, price_100g, price_140g, price_200g, category, sort_order) VALUES (?,?,?,?,?,?)",
        (
            request.form["name"],
            request.form.get("price_100g") or None,
            request.form.get("price_140g") or None,
            request.form.get("price_200g") or None,
            request.form.get("category", "burger"),
            request.form.get("sort_order", 0),
        ),
    )
    db.commit()
    return redirect(url_for("admin"))


@app.route("/admin/update/<int:item_id>", methods=["POST"])
@login_required
def admin_update(item_id):
    db = get_db()
    db.execute(
        "UPDATE menu_items SET name=?, price_100g=?, price_140g=?, price_200g=?, category=?, sort_order=? WHERE id=?",
        (
            request.form["name"],
            request.form.get("price_100g") or None,
            request.form.get("price_140g") or None,
            request.form.get("price_200g") or None,
            request.form.get("category", "burger"),
            request.form.get("sort_order", 0),
            item_id,
        ),
    )
    db.commit()
    return redirect(url_for("admin"))


@app.route("/admin/delete/<int:item_id>", methods=["POST"])
@login_required
def admin_delete(item_id):
    db = get_db()
    db.execute("DELETE FROM menu_items WHERE id=?", (item_id,))
    db.commit()
    return redirect(url_for("admin"))


# ---------- Public API (used by the static site) ----------

@app.route("/api/menu")
def api_menu():
    db = get_db()
    items = db.execute("SELECT * FROM menu_items ORDER BY sort_order, id").fetchall()
    return jsonify([dict(row) for row in items])


init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
