from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.models import StaffProfile, User

auth = Blueprint('auth', __name__)


@auth.route('/register')
def register_choice():
    return render_template('register_choice.html')


@auth.route('/user/register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        existing = User.query.filter_by(email=email).first()

        if existing:
            flash('Email already exists')
            return redirect(url_for('auth.user_register'))

        user = User(name=name, email=email, password=generate_password_hash(password), role='user')
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please login.')
        return redirect(url_for('auth.login'))

    return render_template('user_register.html')


@auth.route('/staff/register', methods=['GET', 'POST'])
def staff_register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        contact = request.form['contact']
        existing = User.query.filter_by(email=email).first()

        if existing:
            flash('Email already exists')
            return redirect(url_for('auth.staff_register'))

        user = User(name=name, email=email, password=generate_password_hash(password), role='staff')
        db.session.add(user)
        db.session.commit()

        profile = StaffProfile(user_id=user.id, contact=contact, status='Pending')
        db.session.add(profile)
        db.session.commit()
        flash('Registration submitted. Wait for admin approval.')
        return redirect(url_for('auth.login'))

    return render_template('staff_register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid email or password')
            return redirect(url_for('auth.login'))

        if user.is_blacklisted:
            flash('Your account has been blacklisted')
            return redirect(url_for('auth.login'))

        if user.role == 'staff':
            profile = StaffProfile.query.filter_by(user_id=user.id).first()
            if not profile or profile.status != 'Approved':
                flash('Waiting for admin approval')
                return redirect(url_for('auth.login'))

        login_user(user)
        return redirect(url_for('routes.dashboard'))

    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.home'))
