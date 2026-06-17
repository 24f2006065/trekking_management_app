from app import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False
    )

    is_blacklisted = db.Column(
        db.Boolean,
        default=False
    )

    bookings = db.relationship(
        'Booking',
        backref='user',
        lazy=True
    )

    staff_profile = db.relationship(
        'StaffProfile',
        backref='user',
        uselist=False
    )


class StaffProfile(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )

    contact = db.Column(
        db.String(20)
    )

    status = db.Column(
        db.String(20),
        default='Pending'
    )

    assigned_treks = db.relationship(
        'Trek',
        backref='staff',
        lazy=True
    )


class Trek(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    trek_name = db.Column(
        db.String(100),
        nullable=False
    )

    location = db.Column(
        db.String(100),
        nullable=False
    )

    difficulty = db.Column(
        db.String(20),
        nullable=False
    )

    duration = db.Column(
        db.Integer,
        nullable=False
    )

    available_slots = db.Column(
        db.Integer,
        nullable=False
    )

    start_date = db.Column(
        db.Date
    )

    end_date = db.Column(
        db.Date
    )

    status = db.Column(
        db.String(20),
        default='Pending'
    )

    assigned_staff_id = db.Column(
        db.Integer,
        db.ForeignKey('staff_profile.id')
    )

    bookings = db.relationship(
        'Booking',
        backref='trek',
        lazy=True
    )


class Booking(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )

    trek_id = db.Column(
        db.Integer,
        db.ForeignKey('trek.id')
    )

    booking_date = db.Column(
        db.DateTime
    )

    status = db.Column(
        db.String(20),
        default='Booked'
    )


    