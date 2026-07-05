from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required

from app import db
from app.models import User, StaffProfile

auth = Blueprint("auth", __name__)


@auth.route("/register")
def register_choice():
    return render_template("register_choice.html")


@auth.route("/user/register", methods=["GET", "POST"])
def user_register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        existing = User.query.filter_by(email=email).first()

        if existing:
            flash("Email already exists")
            return redirect(url_for("auth.user_register"))

        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role="user"
        )

        db.session.add(user)
        db.session.commit()

        flash("Registration Successful")

        return redirect(url_for("auth.login"))

    return render_template("user_register.html")



@auth.route("/staff/register", methods=["GET", "POST"])
def staff_register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        contact = request.form.get("contact")

        existing = User.query.filter_by(email=email).first()

        if existing:
            flash("Email already exists")
            return redirect(url_for("auth.staff_register"))

        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role="staff"
        )

        db.session.add(user)
        db.session.commit()

        profile = StaffProfile(
            user_id=user.id,
            contact=contact,
            status="Pending"
        )

        db.session.add(profile)
        db.session.commit()

        flash("Registration Submitted. Wait for Admin Approval.")

        return redirect(url_for("auth.login"))

    return render_template("staff_register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Invalid Email or Password")
            return redirect(url_for("auth.login"))

        if not check_password_hash(user.password, password):
            flash("Invalid Email or Password")
            return redirect(url_for("auth.login"))

        if user.is_blacklisted:
            flash("Your account has been blocked.")
            return redirect(url_for("auth.login"))

        if user.role == "staff":

            profile = StaffProfile.query.filter_by(user_id=user.id).first()

            if profile is None or profile.status != "Approved":
                flash("Waiting for Admin Approval")
                return redirect(url_for("auth.login"))

        login_user(user)

        if user.role == "admin":
            return redirect(url_for("routes.admin_dashboard"))

        elif user.role == "staff":
            return redirect(url_for("routes.staff_dashboard"))

        return redirect(url_for("routes.user_dashboard"))

    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("auth.login"))

