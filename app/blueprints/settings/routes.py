from flask import render_template, request, session, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from . import bp

def ensure_user_settings():
    # Preferencje trzymamy w DB; sesja jest cachem na czas requestu
    if not current_user.is_authenticated:
        if 'user_settings' not in session:
            session['user_settings'] = current_app.config['DEFAULT_SETTINGS'].copy()
        return session['user_settings']

    # Zaladowanie z DB albo ustawienie domyślnych
    db_settings = current_user.settings or current_app.config['DEFAULT_SETTINGS'].copy()
    session['user_settings'] = db_settings
    return db_settings

@bp.route("/", methods=["GET", "POST"])
@login_required
def settings():
    ensure_user_settings()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "save":
            theme = request.form.get("theme")
            language = request.form.get("language")

            # Pracujemy na kopii i przypisujemy z powrotem – bez mutowania zagnieżdżonych struktur
            settings = session.get('user_settings', {}).copy()

            if theme in current_app.config['THEMES']:
                settings['theme'] = theme
            if language in current_app.config['LANGUAGES']:
                settings['language'] = language

            session['user_settings'] = settings  # <- ważne przypisanie
            # Zapis do DB per-user
            current_user.settings = settings
            try:
                from ... import db
                db.session.add(current_user)
                db.session.commit()
            except Exception:
                from ... import db
                db.session.rollback()
            flash("Ustawienia zostały zapisane!", "success")

        elif action == "reset":
            session['user_settings'] = current_app.config['DEFAULT_SETTINGS'].copy()
            current_user.settings = session['user_settings']
            try:
                from ... import db
                db.session.add(current_user)
                db.session.commit()
            except Exception:
                from ... import db
                db.session.rollback()
            flash("Ustawienia zostały zresetowane!", "info")

        else:
            flash("Nieznana akcja.", "warning")

        return redirect(url_for("settings.settings"))

    # GET
    return render_template(
        "settings.html",
        settings=session['user_settings'],
        themes=current_app.config['THEMES'],
        languages=current_app.config['LANGUAGES'],
    )