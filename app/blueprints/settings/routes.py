from flask import render_template, request, session, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from . import bp
from ... import db
from ...models.settings_options import SettingsOption

def ensure_user_settings():
    if not current_user.is_authenticated:
        if 'user_settings' not in session:
            session['user_settings'] = current_app.config['DEFAULT_SETTINGS'].copy()
        return session['user_settings']

    if not current_user.settings:
        current_user.settings = 1  # domyślnie ID 1 (Dark + Polski)
        try:
            db.session.add(current_user)
            db.session.commit()
        except Exception:
            db.session.rollback()

    option = SettingsOption.query.get(current_user.settings)
    if option:
        settings = {'theme': option.theme, 'language': option.language}
    else:
        settings = current_app.config['DEFAULT_SETTINGS'].copy()
    session['user_settings'] = settings
    return settings

@bp.route("/", methods=["GET", "POST"])
@login_required
def settings():
    settings = ensure_user_settings()

    if request.method == "POST":
        action = request.form.get("action")
        if action == "save":
            theme = request.form.get("theme")
            language = request.form.get("language")

            updated_settings = settings.copy()

            if theme in current_app.config['THEMES']:
                updated_settings['theme'] = theme
            if language in current_app.config['LANGUAGES']:
                updated_settings['language'] = language

            session['user_settings'] = updated_settings

            # Znajdź ID ustawienia w tabeli po theme i language
            option = SettingsOption.query.filter_by(theme=updated_settings['theme'], language=updated_settings['language']).first()
            if option:
                current_user.settings = option.id
            else:
                current_user.settings = 1  # fallback default

            try:
                db.session.add(current_user)
                db.session.commit()
                flash("Ustawienia zostały zapisane!", "success")
            except Exception:
                db.session.rollback()
                flash("Wystąpił błąd podczas zapisu ustawień.", "danger")

        elif action == "reset":
            option = SettingsOption.query.get(1)
            if option:
                session['user_settings'] = {'theme': option.theme, 'language': option.language}
            else:
                session['user_settings'] = current_app.config['DEFAULT_SETTINGS'].copy()
            current_user.settings = 1
            try:
                db.session.add(current_user)
                db.session.commit()
                flash("Ustawienia zostały zresetowane!", "info")
            except Exception:
                db.session.rollback()
                flash("Wystąpił błąd podczas resetu ustawień.", "danger")

        else:
            flash("Nieznana akcja.", "warning")

        return redirect(url_for("settings.settings"))

    return render_template(
        "settings.html",
        settings=session.get('user_settings', current_app.config['DEFAULT_SETTINGS']),
        themes=current_app.config['THEMES'],
        languages=current_app.config['LANGUAGES'],
    )
