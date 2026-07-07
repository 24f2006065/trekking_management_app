from flask import Blueprint, render_template, redirect, url_for,request,flash
from flask_login import login_required, current_user
from app.models import User, Trek, Booking, StaffProfile
from datetime import datetime
from app import db

routes = Blueprint('routes', __name__)

# Home Page
@routes.route('/')
def home():
    return render_template('index.html')

# Staff Dashboard
@routes.route('/staff')
@login_required
def staff_dashboard():

    if current_user.role != "staff":
        return redirect(url_for('auth.login'))

    profile = StaffProfile.query.filter_by(
        user_id=current_user.id
    ).first()

    assigned_treks = Trek.query.filter_by(
        assigned_staff_id=profile.id
    ).all()

    total_participants = 0

    for trek in assigned_treks:
        total_participants += len(trek.bookings)

    return render_template(
        'staff_dashboard.html',
        assigned_treks=assigned_treks,
        total_participants=total_participants
    )


# User Dashboard
@routes.route('/user')
@login_required
def user_dashboard():

    if current_user.role != "user":
        return redirect(url_for('auth.login'))

    return render_template('user_dashboard.html')


@routes.route('/admin', methods= ["GET", "POST"])
@login_required
def admin_dashboard():

    if current_user.role != "admin":
        return redirect(url_for('auth.login'))

    total_users = User.query.filter_by(role='user').count()

    total_staff = User.query.filter_by(role='staff').count()

    total_treks = Trek.query.count()

    total_bookings = Booking.query.count()

    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        total_staff=total_staff,
        total_treks=total_treks,
        total_bookings=total_bookings
    )

@routes.route("/add_trek", methods=["GET", "POST"])
@login_required
def add_trek():

    if current_user.role != "admin":
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        trek = Trek(
            trek_name=request.form["trek_name"],
            location=request.form["location"],
            difficulty=request.form["difficulty"],
            duration=int(request.form["duration"]),
            available_slots=int(request.form["available_slots"]),
            start_date=datetime.strptime(
                request.form["start_date"],
                "%Y-%m-%d"
            ).date(),
            end_date=datetime.strptime(
                request.form["end_date"],
                "%Y-%m-%d"
            ).date(),
            status=request.form["status"]
        )

        db.session.add(trek)
        db.session.commit()

        flash("Trek Added Successfully")

        return redirect(url_for("routes.view_treks"))

    return render_template("add_trek.html")



@routes.route('/view_treks')
@login_required
def view_treks():

    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))

    treks = Trek.query.all()

    return render_template(
        'view_treks.html',
        treks=treks
    )

@routes.route("/edit_trek/<int:trek_id>", methods=["GET", "POST"])
@login_required
def edit_trek(trek_id):

    if current_user.role != "admin":
        return redirect(url_for("auth.login"))

    trek = Trek.query.get_or_404(trek_id)

    if request.method == "POST":

        trek.trek_name = request.form["trek_name"]
        trek.location = request.form["location"]
        trek.difficulty = request.form["difficulty"]
        trek.duration = request.form["duration"]
        trek.available_slots = request.form["available_slots"]
        trek.status = request.form["status"]

        db.session.commit()

        flash("Trek Updated Successfully")

        return redirect(url_for("routes.view_treks"))

    return render_template(
        "edit_trek.html",
        trek=trek
    )

@routes.route("/delete_trek/<int:trek_id>")
@login_required
def delete_trek(trek_id):

    if current_user.role != "admin":
        return redirect(url_for("auth.login"))

    trek = Trek.query.get_or_404(trek_id)

    db.session.delete(trek)
    db.session.commit()

    flash("Trek Deleted")

    return redirect(url_for("routes.view_treks"))

@routes.route("/staff_requests")
@login_required
def staff_requests():

    if current_user.role != "admin":
        return redirect(url_for("auth.login"))

    staff = StaffProfile.query.filter_by(status="Pending").all()

    return render_template(
        "staff_requests.html",
        staff=staff
    )
@routes.route("/approve_staff/<int:id>")
@login_required
def approve_staff(id):

    if current_user.role != "admin":
        return redirect(url_for("auth.login"))

    profile = StaffProfile.query.get_or_404(id)

    profile.status = "Approved"

    db.session.commit()

    flash("Staff Approved Successfully")

    return redirect(url_for("routes.staff_requests"))

@routes.route("/view_staff")
@login_required
def view_staff():

    if current_user.role != "admin":
        return redirect(url_for("auth.login"))

    staff = StaffProfile.query.all()

    return render_template(
        "view_staff.html",
        staff=staff
    )

@routes.route("/assign_staff/<int:trek_id>", methods=["GET", "POST"])
@login_required
def assign_staff(trek_id):

    if current_user.role != "admin":
        return redirect(url_for("auth.login"))

    trek = Trek.query.get_or_404(trek_id)

    staff = StaffProfile.query.filter_by(status="Approved").all()

    if request.method == "POST":

        trek.assigned_staff_id = request.form["staff_id"]

        db.session.commit()

        flash("Staff Assigned Successfully")

        return redirect(url_for("routes.view_treks"))

    return render_template(
        "assign_staff.html",
        trek=trek,
        staff=staff
    )

@routes.route("/view_users")
@login_required
def view_users():

    if current_user.role != "admin":
        return redirect(url_for("auth.login"))

    users = User.query.filter_by(role="user").all()

    return render_template(
        "view_users.html",
        users=users
    )
@routes.route("/blacklist_user/<int:id>")
@login_required
def blacklist_user(id):

    if current_user.role != "admin":
        return redirect(url_for("auth.login"))

    user = User.query.get_or_404(id)

    user.is_blacklisted = True

    db.session.commit()

    flash("User Blacklisted")

    return redirect(url_for("routes.view_users"))

@routes.route("/blacklist_staff/<int:id>")
@login_required
def blacklist_staff(id):

    if current_user.role != "admin":
        return redirect(url_for("auth.login"))

    profile = StaffProfile.query.get_or_404(id)

    profile.status = "Blacklisted"

    db.session.commit()

    flash("Staff Blacklisted")

    return redirect(url_for("routes.view_staff"))

@routes.route("/view_bookings")
@login_required
def view_bookings():

    if current_user.role != "admin":
        return redirect(url_for("auth.login"))

    bookings = Booking.query.all()

    return render_template(
        "view_bookings.html",
        bookings=bookings
    )
@routes.route("/update_trek/<int:trek_id>", methods=["GET","POST"])
@login_required
def update_trek(trek_id):

    if current_user.role != "staff":
        return redirect(url_for("auth.login"))

    profile = StaffProfile.query.filter_by(
        user_id=current_user.id
    ).first()

    trek = Trek.query.filter_by(
        id=trek_id,
        assigned_staff_id=profile.id
    ).first()

    if trek is None:
        flash("Unauthorized Access")
        return redirect(url_for("routes.staff_dashboard"))

    if request.method == "POST":

        trek.available_slots = request.form.get("available_slots")
        trek.status = request.form.get("status")

        db.session.commit()

        flash("Trek Updated Successfully")

        return redirect(url_for("routes.staff_dashboard"))

    return render_template(
        "update_trek.html",
        trek=trek
    )
@routes.route("/participants/<int:trek_id>")
@login_required
def participants(trek_id):

    if current_user.role != "staff":
        return redirect(url_for("auth.login"))

    profile = StaffProfile.query.filter_by(
        user_id=current_user.id
    ).first()

    trek = Trek.query.filter_by(
        id=trek_id,
        assigned_staff_id=profile.id
    ).first()

    if trek is None:
        flash("Unauthorized")
        return redirect(url_for("routes.staff_dashboard"))

    bookings = Booking.query.filter_by(
        trek_id=trek.id
    ).all()

    return render_template(
        "participants.html",
        trek=trek,
        bookings=bookings
    )