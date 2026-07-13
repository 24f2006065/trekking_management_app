from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import Booking, StaffProfile, Trek, User

routes = Blueprint('routes', __name__)


@routes.route('/')
def home():
    return render_template('index.html')


@routes.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('routes.admin_dashboard'))
    if current_user.role == 'staff':
        return redirect(url_for('routes.staff_dashboard'))
    return redirect(url_for('routes.user_dashboard'))


@routes.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return 'Unauthorized'

    total_users = User.query.filter_by(role='user').count()
    total_staff = User.query.filter_by(role='staff').count()
    total_treks = Trek.query.count()
    total_bookings = Booking.query.count()

    return render_template('admin_dashboard.html', total_users=total_users,  total_staff=total_staff, total_treks=total_treks,  total_bookings=total_bookings)


@routes.route('/admin/treks')
@login_required
def view_treks():
    if current_user.role != 'admin':
        return 'Unauthorized'

    search = request.args.get('q', '')
    treks = Trek.query.all()
    if search:
        treks = Trek.query.filter(Trek.trek_name.ilike(f'%{search}%')).all()

    return render_template('view_treks.html', treks=treks, query=search)


@routes.route('/admin/treks/add', methods=['GET', 'POST'])
@login_required
def add_trek():
    if current_user.role != 'admin':
        return 'Unauthorized'

    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()

        trek = Trek(
            trek_name=request.form['trek_name'],
            location=request.form['location'],
            difficulty=request.form['difficulty'],
            duration=int(request.form['duration']),
            available_slots=int(request.form['available_slots']),
            start_date=start_date,
            end_date=end_date,
            status=request.form['status']
        )
        db.session.add(trek)
        db.session.commit()
        flash('Trek added successfully')
        return redirect(url_for('routes.view_treks'))

    return render_template('add_trek.html')


@routes.route('/admin/treks/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_trek(id):
    if current_user.role != 'admin':
        return 'Unauthorized'

    trek = Trek.query.get(id)
    if not trek:
        return 'Trek not found'

    if request.method == 'POST':
        trek.trek_name = request.form['trek_name']
        trek.location = request.form['location']
        trek.difficulty = request.form['difficulty']
        trek.duration = int(request.form['duration'])
        trek.available_slots = int(request.form['available_slots'])
        trek.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        trek.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        trek.status = request.form['status']
        db.session.commit()
        flash('Trek updated successfully')
        return redirect(url_for('routes.view_treks'))

    return render_template('edit_trek.html', trek=trek)


@routes.route('/admin/treks/<int:id>/delete')
@login_required
def delete_trek(id):
    if current_user.role != 'admin':
        return 'Unauthorized'

    trek = Trek.query.get(id)
    if trek:
        Booking.query.filter_by(trek_id=id).delete()
        db.session.delete(trek)
        db.session.commit()
        flash('Trek deleted')
    return redirect(url_for('routes.view_treks'))


@routes.route('/admin/treks/<int:id>/assign', methods=['GET', 'POST'])
@login_required
def assign_staff(id):
    if current_user.role != 'admin':
        return 'Unauthorized'

    trek = Trek.query.get(id)
    staff = StaffProfile.query.filter_by(status='Approved').all()
    if not trek:
        return 'Trek not found'

    if request.method == 'POST':
        trek.assigned_staff_id = request.form.get('staff_id')
        db.session.commit()
        flash('Staff assigned successfully')
        return redirect(url_for('routes.view_treks'))

    return render_template('assign_staff.html', trek=trek, staff=staff)


@routes.route('/admin/staff')
@login_required
def view_staff():
    if current_user.role != 'admin':
        return 'Unauthorized'

    search = request.args.get('q', '')
    staff = StaffProfile.query.all()
    if search:
        staff = StaffProfile.query.join(User).filter(User.name.ilike(f'%{search}%')).all()
    return render_template('view_staff.html', staff=staff, query=search)


@routes.route('/admin/staff/requests')
@login_required
def staff_requests():
    if current_user.role != 'admin':
        return 'Unauthorized'
    staff = StaffProfile.query.filter_by(status='Pending').all()
    return render_template('staff_requests.html', staff=staff)


@routes.route('/admin/staff/<int:id>/approve')
@login_required
def approve_staff(id):
    if current_user.role != 'admin':
        return 'Unauthorized'
    profile = StaffProfile.query.get(id)
    if profile:
        profile.status = 'Approved'
        db.session.commit()
    return redirect(url_for('routes.staff_requests'))


@routes.route('/admin/users')
@login_required
def view_users():
    if current_user.role != 'admin':
        return 'Unauthorized'
    search = request.args.get('q', '')
    users = User.query.filter_by(role='user').all()
    if search:
        users = User.query.filter(User.role == 'user', User.name.ilike(f'%{search}%')).all()
    return render_template('view_users.html', users=users, query=search)


@routes.route('/admin/users/<int:id>/blacklist')
@login_required
def blacklist_user(id):
    if current_user.role != 'admin':
        return 'Unauthorized'
    user = User.query.get(id)
    if user:
        user.is_blacklisted = True
        db.session.commit()
    return redirect(url_for('routes.view_users'))


@routes.route('/admin/staff/<int:id>/blacklist')
@login_required
def blacklist_staff(id):
    if current_user.role != 'admin':
        return 'Unauthorized'
    profile = StaffProfile.query.get(id)
    if profile:
        profile.status = 'Blacklisted'
        profile.user.is_blacklisted = True
        db.session.commit()
    return redirect(url_for('routes.view_staff'))


@routes.route('/admin/bookings')
@login_required
def view_bookings():
    if current_user.role != 'admin':
        return 'Unauthorized'
    bookings = Booking.query.all()
    return render_template('view_bookings.html', bookings=bookings)


@routes.route('/staff')
@login_required
def staff_dashboard():
    if current_user.role != 'staff':
        return 'Unauthorized'
    profile = StaffProfile.query.filter_by(user_id=current_user.id).first()
    if not profile or profile.status != 'Approved':
        return 'Waiting for admin approval'
    assigned_treks = Trek.query.filter_by(assigned_staff_id=profile.id).all()
    total_participants = 0
    for trek in assigned_treks:
        total_participants = total_participants + len(trek.bookings)
    return render_template('staff_dashboard.html', assigned_treks=assigned_treks, total_participants=total_participants)


@routes.route('/staff/treks/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update_trek(id):
    if current_user.role != 'staff':
        return 'Unauthorized'
    profile = StaffProfile.query.filter_by(user_id=current_user.id).first()
    trek = Trek.query.get(id)
    if not trek or trek.assigned_staff_id != profile.id:
        return 'Unauthorized'
    if request.method == 'POST':
        trek.available_slots = int(request.form['available_slots'])
        trek.status = request.form['status']
        db.session.commit()
        return redirect(url_for('routes.staff_dashboard'))
    return render_template('update_trek.html', trek=trek)


@routes.route('/staff/treks/<int:id>/participants')
@login_required
def participants(id):
    if current_user.role != 'staff':
        return 'Unauthorized'
    profile = StaffProfile.query.filter_by(user_id=current_user.id).first()
    trek = Trek.query.get(id)
    if not trek or trek.assigned_staff_id != profile.id:
        return 'Unauthorized'
    bookings = Booking.query.filter_by(trek_id=id).all()
    return render_template('participants.html', trek=trek, bookings=bookings)


@routes.route('/staff/bookings/<int:id>/complete')
@login_required
def complete_booking(id):
    if current_user.role != 'staff':
        return 'Unauthorized'
    booking = Booking.query.get(id)
    profile = StaffProfile.query.filter_by(user_id=current_user.id).first()
    if not booking or booking.trek.assigned_staff_id != profile.id:
        return 'Unauthorized'
    booking.status = 'Completed'
    db.session.commit()
    return redirect(url_for('routes.participants', id=booking.trek_id))


@routes.route('/user')
@login_required
def user_dashboard():
    if current_user.role != 'user':
        return 'Unauthorized'
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    total_bookings = len(bookings)
    upcoming_treks = 0
    for booking in bookings:
        if booking.status == 'Booked':
            upcoming_treks = upcoming_treks + 1
    return render_template('user_dashboard.html', total_bookings=total_bookings,  upcoming_treks=upcoming_treks)


@routes.route('/treks')
@login_required
def available_treks():
    if current_user.role != 'user':
        return 'Unauthorized'
    location = request.args.get('location', '')
    difficulty = request.args.get('difficulty', '')
    treks = Trek.query.filter_by(status='Open').all()
    result = []
    for trek in treks:
        if trek.available_slots > 0:
            if location.lower() in trek.location.lower():
                if difficulty == '' or difficulty == trek.difficulty:
                    result.append(trek)
    return render_template('available_treks.html', treks=result, location=location, difficulty=difficulty)


@routes.route('/treks/<int:id>/book')
@login_required
def book_trek(id):
    if current_user.role != 'user':
        return 'Unauthorized'
    trek = Trek.query.get(id)
    if not trek or trek.status != 'Open' or trek.available_slots <= 0:
        flash('Trek is not available')
        return redirect(url_for('routes.available_treks'))
    existing = Booking.query.filter_by(user_id=current_user.id, trek_id=id).first()
    if existing:
        flash('You have already booked this trek')
        return redirect(url_for('routes.available_treks'))
    booking = Booking(user_id=current_user.id, trek_id=id, booking_date=datetime.now(), status='Booked')
    db.session.add(booking)
    trek.available_slots = trek.available_slots - 1
    db.session.commit()
    return redirect(url_for('routes.my_bookings'))


@routes.route('/my-bookings')
@login_required
def my_bookings():
    if current_user.role != 'user':
        return 'Unauthorized'
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('my_bookings.html', bookings=bookings)


@routes.route('/bookings/<int:id>/cancel')
@login_required
def cancel_booking(id):
    if current_user.role != 'user':
        return 'Unauthorized'
    booking = Booking.query.get(id)
    if not booking or booking.user_id != current_user.id:
        return 'Unauthorized'
    if booking.status == 'Booked':
        booking.status = 'Cancelled'
        booking.trek.available_slots = booking.trek.available_slots + 1
        db.session.commit()
    return redirect(url_for('routes.my_bookings'))


@routes.route('/profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    if current_user.role == 'admin':
        return 'Unauthorized'
    if request.method == 'POST':
        current_user.name = request.form['name']
        current_user.email = request.form['email']
        if current_user.role == 'staff':
            current_user.staff_profile.contact = request.form['contact']
        db.session.commit()
        return redirect(url_for('routes.dashboard'))
    return render_template('update_profile.html')
