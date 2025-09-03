from flask import render_template, request, session, redirect, url_for, flash, current_app
from . import bp

def ensure_user_settings():
    if 'user_settings' not in session:
        session['user_settings'] = current_app.config['DEFAULT_SETTINGS'].copy()
    return session['user_settings']

@bp.route("/", methods=["GET", "POST"])
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
            flash("Ustawienia zostały zapisane!", "success")

        elif action == "reset":
            session['user_settings'] = current_app.config['DEFAULT_SETTINGS'].copy()
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