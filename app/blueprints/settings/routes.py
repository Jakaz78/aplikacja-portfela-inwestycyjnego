from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from . import bp
from ... import db
from ...models.user_settings import UserSettings


def ensure_user_settings_exist():
    """Upewnia się, że użytkownik ma przypisany obiekt UserSettings."""
    if not current_user.settings:
        # Jeśli z jakiegoś powodu ustawienia nie istnieją, stwórz domyślne
        defaults = current_app.config['DEFAULT_SETTINGS']
        new_settings = UserSettings(
            user_id=current_user.id,
            theme=defaults.get('theme', 'Dark'),
            language=defaults.get('language', 'Polski')
        )
        db.session.add(new_settings)
        db.session.commit()
        # Odśwież użytkownika, żeby widział relację
        db.session.refresh(current_user)


@bp.route("/", methods=["GET", "POST"])
@login_required
def settings():
    # 1. Zabezpieczenie: upewnij się, że rekord w bazie istnieje
    ensure_user_settings_exist()

    # Teraz możemy bezpiecznie odwoływać się do current_user.settings
    user_settings = current_user.settings

    if request.method == "POST":
        action = request.form.get("action")

        if action == "save":
            theme = request.form.get("theme")
            language = request.form.get("language")

            # Walidacja i zapis
            if theme in current_app.config['THEMES']:
                user_settings.theme = theme

            if language in current_app.config['LANGUAGES']:
                user_settings.language = language

            try:
                db.session.commit()
                flash("Ustawienia zostały zapisane!", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Błąd zapisu: {str(e)}", "danger")

        elif action == "reset":
            # Przywróć wartości domyślne z konfigu
            defaults = current_app.config['DEFAULT_SETTINGS']
            user_settings.theme = defaults['theme']
            user_settings.language = defaults['language']

            try:
                db.session.commit()
                flash("Przywrócono ustawienia domyślne.", "info")
            except Exception:
                db.session.rollback()
                flash("Błąd podczas resetowania.", "danger")

        else:
            flash("Nieznana akcja.", "warning")

        return redirect(url_for("settings.settings"))

    # GET: Wyświetl formularz
    return render_template(
        "settings.html",
        settings=user_settings,  # Przekazujemy obiekt prosto z bazy
        themes=current_app.config['THEMES'],
        languages=current_app.config['LANGUAGES'],
    )