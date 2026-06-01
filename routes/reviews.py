from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Review
from routes import login_required

reviews_bp = Blueprint("reviews", __name__)


@reviews_bp.route("/admin/reviews")
@login_required
def admin_reviews():
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template("admin/reviews.html", reviews=reviews)


@reviews_bp.route("/admin/reviews/approve/<int:review_id>", methods=["POST"])
@login_required
def approve_review(review_id):
    review = Review.query.get_or_404(review_id)
    review.status = "approved"
    db.session.commit()
    flash("הביקורת אושרה", "success")
    return redirect(url_for("reviews.admin_reviews"))


@reviews_bp.route("/admin/reviews/reject/<int:review_id>", methods=["POST"])
@login_required
def reject_review(review_id):
    review = Review.query.get_or_404(review_id)
    review.status = "rejected"
    db.session.commit()
    flash("הביקורת נדחתה", "success")
    return redirect(url_for("reviews.admin_reviews"))


@reviews_bp.route("/admin/reviews/delete/<int:review_id>", methods=["POST"])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    flash("הביקורת נמחקה", "success")
    return redirect(url_for("reviews.admin_reviews"))
