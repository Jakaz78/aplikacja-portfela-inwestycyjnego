from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from . import bp
from ... import db
from ...models.user import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # 1. Jeśli to tylko wyświetlenie strony (GET), zwróć szablon
    if request.method == 'GET':
        return render_template('login.html')

    # 2. Logika logowania (POST)
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        login_user(user)
        flash('Zalogowano!', 'success')
        # Przekieruj tam gdzie użytkownik chciał iść, lub na główną
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.index'))

    flash('Nieprawidłowy email lub hasło.', 'danger')
    return render_template('login.html')


@bp.route("/register", methods=["GET", "POST"])
def register():
    # 1. Wyświetlenie formularza
    if request.method == 'GET':
        return render_template("register.html")

    # 2. Logika rejestracji (POST)
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password")

    # Szybkie sprawdzenia błędów (Guard clauses)
    if not email or not password:
        flash("Email i hasło są wymagane.", "warning")
        return render_template("register.html")  # Lepiej renderować niż robić redirect (zachowuje dane w formularzu)

    if User.query.filter_by(email=email).first():
        flash("Taki e-mail już istnieje.", "danger")
        return render_template("register.html")

    # Tworzenie użytkownika
    new_user = User(
        email=email,
        first_name=request.form.get("first_name"),
        last_name=request.form.get("last_name")
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)  # Auto-logowanie
    flash("Konto utworzone! Witaj w aplikacji.", "success")

    return redirect(url_for("main.index"))


@bp.route('/logout')  # Domyślnie to jest GET
@login_required
def logout():
    logout_user()
    flash('Wylogowano.', 'info')
    return redirect(url_for('auth.login'))