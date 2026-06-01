import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from models import db, Product
from routes import login_required

products_bp = Blueprint("products", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(file_field):
    """Save uploaded image to static/uploads and return filename. # TODO: S3"""
    f = request.files.get(file_field)
    if f and f.filename and allowed_file(f.filename):
        filename = secure_filename(f.filename)
        upload_dir = os.path.join(current_app.root_path, "static", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        f.save(os.path.join(upload_dir, filename))
        return filename
    return None


@products_bp.route("/admin/products")
@login_required
def admin_products():
    rental_products = Product.query.filter_by(category="rental").order_by(Product.created_at.desc()).all()
    refurb_products = Product.query.filter_by(category="refurbished").order_by(Product.created_at.desc()).all()
    return render_template("admin/products.html", rental_products=rental_products, refurb_products=refurb_products)


@products_bp.route("/admin/products/add", methods=["GET", "POST"])
@login_required
def add_product():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        price = request.form.get("price", "0")
        category = request.form.get("category", "rental")

        try:
            price = float(price)
        except ValueError:
            price = 0.0

        img1 = save_image("image_1")
        img2 = save_image("image_2")
        img3 = save_image("image_3")

        product = Product(
            name=name,
            description=description,
            price=price,
            category=category,
            image_1=img1,
            image_2=img2,
            image_3=img3,
        )
        db.session.add(product)
        db.session.commit()
        flash("המוצר נוסף בהצלחה", "success")
        return redirect(url_for("products.admin_products"))

    return render_template("admin/product_form.html", product=None, action="add")


@products_bp.route("/admin/products/edit/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == "POST":
        product.name = request.form.get("name", "").strip()
        product.description = request.form.get("description", "").strip()
        product.category = request.form.get("category", "rental")
        try:
            product.price = float(request.form.get("price", "0"))
        except ValueError:
            product.price = 0.0

        img1 = save_image("image_1")
        img2 = save_image("image_2")
        img3 = save_image("image_3")

        if img1:
            product.image_1 = img1
        if img2:
            product.image_2 = img2
        if img3:
            product.image_3 = img3

        # Allow clearing individual images
        if request.form.get("clear_image_1"):
            product.image_1 = None
        if request.form.get("clear_image_2"):
            product.image_2 = None
        if request.form.get("clear_image_3"):
            product.image_3 = None

        db.session.commit()
        flash("המוצר עודכן בהצלחה", "success")
        return redirect(url_for("products.admin_products"))

    return render_template("admin/product_form.html", product=product, action="edit")


@products_bp.route("/admin/products/delete/<int:product_id>", methods=["POST"])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("המוצר נמחק", "success")
    return redirect(url_for("products.admin_products"))
