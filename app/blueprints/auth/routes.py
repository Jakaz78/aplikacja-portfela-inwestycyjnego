from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import bp
from ... import db
from ...models.user import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Nieprawidłowy email lub hasło.', 'danger')
            return render_template('login.html')
        login_user(user)
        flash('Zalogowano!', 'success')
        return redirect(url_for('main.index'))

    # Opcjonalne logowanie przez GET na potrzeby testów: /auth/login?email=...&password=...
    email = request.args.get('email')
    password = request.args.get('password')
    if email and password:
        email = email.strip().lower()
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Zalogowano (GET).', 'success')
            return redirect(url_for('main.index'))
        flash('Nieprawidłowy email lub hasło (GET).', 'danger')

    return render_template('login.html')


@bp.get('/logout')
@login_required
def logout():
    logout_user()
    flash('Wylogowano.', 'info')
    return redirect(url_for('auth.login'))


