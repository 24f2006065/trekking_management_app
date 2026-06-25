from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
routes = Blueprint('routes', __name__)

@routes.route('/admin')
@login_required
def admin_dashboard():

    if current_user.role != "admin":
        return redirect(url_for('auth.login'))

    return render_template('admin_dashboard.html')

@routes.route('/staff')
@login_required
def staff_dashboard():

    if current_user.role != "staff":
        return redirect(url_for('auth.login'))

    return render_template('staff_dashboard.html')

@routes.route('/user')
@login_required
def user_dashboard():

    if current_user.role != "user":
        return redirect(url_for('auth.login'))

    return render_template('user_dashboard.html')