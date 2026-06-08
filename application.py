import os
import click
from dotenv import load_dotenv, find_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session

load_dotenv(find_dotenv())

_admin_user = os.environ.get("ADMIN_USERNAME", "admin")
_admin_pass = os.environ.get("ADMIN_PASSWORD", "admin123")
print(f"[startup] ADMIN_USERNAME={_admin_user!r}  ADMIN_PASSWORD={'*' * len(_admin_pass)} (len={len(_admin_pass)})")

from models import db, Admin, Product, Review, StoreSetting
from routes import login_required
from routes.auth import auth_bp
from routes.products import products_bp
from routes.reviews import reviews_bp
from routes.settings import settings_bp, get_setting

application = Flask(__name__)

# ── Configuration ──────────────────────────────────────────────────────────────
application.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-in-prod")
application.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///store.db"
)
application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
application.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB upload limit
application.config["SESSION_COOKIE_SAMESITE"] = "Lax"
application.config["SESSION_COOKIE_HTTPONLY"] = True

db.init_app(application)

# ── Blueprints ─────────────────────────────────────────────────────────────────
application.register_blueprint(auth_bp)
application.register_blueprint(products_bp)
application.register_blueprint(reviews_bp)
application.register_blueprint(settings_bp)


# ── Admin dashboard (lives in main app to avoid circular imports) ──────────────

@application.route("/admin/dashboard")
@login_required
def admin_dashboard():
    total_new = Product.query.filter_by(category="rental").count()
    total_refurb = Product.query.filter_by(category="refurbished").count()
    pending_reviews = Review.query.filter_by(status="pending").count()
    return render_template(
        "admin/dashboard.html",
        total_new=total_new,
        total_refurb=total_refurb,
        pending_reviews=pending_reviews,
    )


# ── Public pages ───────────────────────────────────────────────────────────────
@application.route("/")
def home():
    hero_image = get_setting("hero_image")
    opening_hours_raw = get_setting("opening_hours", "")
    opening_hours_lines = [line for line in opening_hours_raw.splitlines() if line.strip()]
    return render_template("home.html", hero_image=hero_image, opening_hours_lines=opening_hours_lines)


@application.route("/rental")
def rental():
    products = Product.query.filter_by(category="rental").order_by(Product.created_at.desc()).all()
    return render_template("rental.html", products=products)


@application.route("/refurbished-products")
def refurbished_products():
    products = Product.query.filter_by(category="refurbished").order_by(Product.created_at.desc()).all()
    return render_template("refurbished_products.html", products=products)


@application.route("/about")
def about():
    return render_template("about.html")


@application.route("/reviews")
def reviews():
    approved = Review.query.filter_by(status="approved").order_by(Review.created_at.desc()).all()
    return render_template("reviews.html", reviews=approved)


@application.route("/contact", methods=["GET", "POST"])
def contact():
    submitted = False
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        rating = request.form.get("rating", "5")
        text = request.form.get("text", "").strip()

        try:
            rating = max(1, min(5, int(rating)))
        except ValueError:
            rating = 5

        if name and text:
            review = Review(customer_name=name, rating=rating, text=text, status="pending")
            db.session.add(review)
            db.session.commit()
            submitted = True

    address = get_setting("address", "")
    email = get_setting("email", "")
    phone = get_setting("phone", "")
    return render_template("contact.html", submitted=submitted, address=address, email=email, phone=phone)


# ── CLI seed command ───────────────────────────────────────────────────────────
@application.cli.command("seed")
def seed():
    """Seed the database with initial data."""
    with application.app_context():
        db.create_all()

        # Admin user
        admin_username = os.environ.get("ADMIN_USERNAME", "admin")
        admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
        if not Admin.query.filter_by(username=admin_username).first():
            admin = Admin(username=admin_username)
            admin.set_password(admin_password)
            db.session.add(admin)
            click.echo(f"Admin user created: {admin_username}")

        # Store settings
        defaults = {
            "address": "ביתר עילית",
            "email": "info@mechashmechadash.co.il",
            "phone": "0527138797",
            "opening_hours": "ראשון-חמישי: 09:00 - 18:00\nשישי: 09:00 - 13:00\nשבת: סגור",
            "hero_image": "",
        }
        for key, value in defaults.items():
            if not StoreSetting.query.filter_by(key=key).first():
                db.session.add(StoreSetting(key=key, value=value))

        # Sample products
        if Product.query.count() == 0:
            sample_products = [
                Product(
                    name='מחשב נייד ASUS VivoBook 15',
                    description='מחשב נייד חדש עם מעבד Intel Core i5, 8GB RAM, SSD 512GB, מסך 15.6 אינץ\'',
                    price=2999.0,
                    category="rental",
                ),
                Product(
                    name='מחשב שולחני HP ProDesk',
                    description='מחשב שולחני חדש עם מעבד Intel Core i7, 16GB RAM, SSD 1TB',
                    price=3499.0,
                    category="rental",
                ),
                Product(
                    name='מחשב נייד Dell Latitude 5490 מחודש',
                    description='מחשב נייד מחודש במצב מצוין, מעבד Intel Core i5, 8GB RAM, SSD 256GB',
                    price=1299.0,
                    category="refurbished",
                ),
                Product(
                    name='מחשב שולחני Lenovo ThinkCentre מחודש',
                    description='מחשב שולחני מחודש ובדוק, מעבד Intel Core i5, 8GB RAM, HDD 500GB',
                    price=899.0,
                    category="refurbished",
                ),
            ]
            db.session.add_all(sample_products)

        # Sample reviews
        if Review.query.count() == 0:
            sample_reviews = [
                Review(
                    customer_name="ישראל ישראלי",
                    rating=5,
                    text="שירות מעולה! קיבלתי מחשב מחדש במצב מושלם במחיר מצוין. ממליץ בחום!",
                    status="approved",
                ),
                Review(
                    customer_name="שרה כהן",
                    rating=4,
                    text="מוצר טוב, משלוח מהיר. אשתמש שוב.",
                    status="pending",
                ),
            ]
            db.session.add_all(sample_reviews)

        db.session.commit()
        click.echo("Seed data inserted successfully.")


@application.cli.command("update-admin")
def update_admin():
    """Update the admin record in the DB from ADMIN_USERNAME / ADMIN_PASSWORD env vars."""
    with application.app_context():
        new_username = os.environ.get("ADMIN_USERNAME", "").strip()
        new_password = os.environ.get("ADMIN_PASSWORD", "").strip()

        if not new_username or not new_password:
            click.echo("ERROR: ADMIN_USERNAME and ADMIN_PASSWORD must both be set in the environment.", err=True)
            return

        admin = Admin.query.first()
        if not admin:
            click.echo("No admin record found. Run 'flask seed' first.", err=True)
            return

        old_username = admin.username
        admin.username = new_username
        admin.set_password(new_password)
        db.session.commit()
        click.echo(f"Admin updated: username '{old_username}' -> '{new_username}', password rehashed.")


# ── DB init on startup ─────────────────────────────────────────────────────────
with application.app_context():
    db.create_all()


if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1")
    application.run(debug=debug, host="0.0.0.0", port=5000)
