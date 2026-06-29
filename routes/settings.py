from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from models import db, StoreSetting
from routes import login_required
from utils.s3 import upload_to_s3

settings_bp = Blueprint("settings", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_setting(key, default=""):
    s = StoreSetting.query.filter_by(key=key).first()
    return s.value if s else default


def set_setting(key, value):
    s = StoreSetting.query.filter_by(key=key).first()
    if s:
        s.value = value
    else:
        s = StoreSetting(key=key, value=value)
        db.session.add(s)
    db.session.commit()


@settings_bp.route("/admin/home-settings", methods=["GET", "POST"])
@login_required
def home_settings():
    if request.method == "POST":
        hero_file = request.files.get("hero_image")
        if hero_file and hero_file.filename and allowed_file(hero_file.filename):
            filename = secure_filename(hero_file.filename)
            url = upload_to_s3(hero_file, filename)
            set_setting("hero_image", url)

        # Opening hours (stored as plain text / newline-separated)
        opening_hours = request.form.get("opening_hours", "")
        set_setting("opening_hours", opening_hours)

        set_setting("address", request.form.get("address", "").strip())
        set_setting("phone", request.form.get("phone", "").strip())
        set_setting("email", request.form.get("email", "").strip())

        flash("ההגדרות עודכנו בהצלחה", "success")
        return redirect(url_for("settings.home_settings"))

    current_hero = get_setting("hero_image")
    current_hours = get_setting("opening_hours")
    return render_template(
        "admin/home_settings.html",
        current_hero=current_hero,
        current_hours=current_hours,
        current_address=get_setting("address"),
        current_phone=get_setting("phone"),
        current_email=get_setting("email"),
    )
