import os
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/admin/login", methods=["GET", "POST"])
def login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        valid_username = os.environ.get("ADMIN_USERNAME", "admin").strip()
        valid_password = os.environ.get("ADMIN_PASSWORD", "admin123").strip()
        print(f"[login] submitted='{username}' expected='{valid_username}' | password_len={len(password)} expected_len={len(valid_password)} | match={'YES' if username == valid_username and password == valid_password else 'NO'}", flush=True)
        if username == valid_username and password == valid_password:
            session.permanent = False
            session["admin_logged_in"] = True
            session["admin_username"] = username
            session["login_at"] = datetime.now(timezone.utc).timestamp()
            return redirect(url_for("admin_dashboard"))
        flash("שם משתמש או סיסמה שגויים", "error")

    return render_template("admin/login.html")


@auth_bp.route("/admin/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
