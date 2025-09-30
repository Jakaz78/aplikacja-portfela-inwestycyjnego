from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import bp
from ... import db
from ...models.user import User

def authenticate_user(email, password):
    """Pomocnicza funkcja do sprawdzenia hasła i użytkownika"""
    user = User.query.filter_by(email=email.strip().lower()).first()
    if user and user.check_password(password):
        return user
    return None

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = authenticate_user(request.form.get('email', ''), request.form.get('password', ''))
        if not user:
            flash('Nieprawidłowy email lub hasło.', 'danger')
            return render_template('login.html')
        login_user(user)
        flash('Zalogowano!', 'success')
        return redirect(url_for('main.index'))

    # Opcjonalne logowanie GET dla testów
    email = request.args.get('email')
    password = request.args.get('password')
    if email and password:
        user = authenticate_user(email, password)
        if user:
            login_user(user)
            flash('Zalogowano (GET).', 'success')
            return redirect(url_for('main.index'))
        flash('Nieprawidłowy email lub hasło (GET).', 'danger')

    return render_template('login.html')

@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")

        if not email or not password:
            flash("Email i hasło są wymagane.", "warning")
            return redirect(url_for("auth.register"))
        if User.query.filter_by(email=email).first():
            flash("Taki e-mail już istnieje.", "danger")
            return redirect(url_for("auth.register"))

        user = User(email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)  # automatyczne logowanie po rejestracji
        flash("Konto utworzone! Możesz się zalogować.", "success")
        return redirect(url_for("main.index"))

    return render_template("register.html")

@bp.get('/logout')
@login_required
def logout():
    logout_user()
    flash('Wylogowano.', 'info')
    return redirect(url_for('auth.login'))
