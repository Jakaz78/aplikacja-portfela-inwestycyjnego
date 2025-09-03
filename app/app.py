
import os
from flask import Flask, render_template, flash, redirect, request, session, url_for
import pandas as pd
from dotenv import load_dotenv


load_dotenv()



def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY") or os.urandom(24)
    # Katalog na dane
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'data')
    # API w UTF-8
    app.config['JSON_AS_ASCII'] = False
    return app



app = create_app()




THEMES = ['Dark', 'Light']
LANGUAGES = ['Polski', 'English', 'Deutsch']

default_settings = {
    'theme': 'Dark',
    'language': 'Polski'
}
def ensure_user_settings():
    """Gwarantuje, że ustawienia użytkownika istnieją w sesji."""
    if 'user_settings' not in session:
        session['user_settings'] = default_settings.copy()
    return session['user_settings']


@app.route('/')
def index():
    return render_template('index.html')
@app.route('/statistics')
def statistics():
    return render_template('statistics.html')

@app.route('/portfolio')
def portfolio():
    previous_path = os.path.join('data', 'previous.csv')
    if os.path.exists(previous_path):
        df = pd.read_csv(previous_path)
        data = df.to_dict(orient='records')
    else:
        data = []

    return render_template('portfolio.html', data=data)



@app.route('/settings', methods=['GET', 'POST'])
def settings():
    ensure_user_settings()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'save':
            theme = request.form.get('theme')
            language = request.form.get('language')

            # Prosta walidacja po stronie serwera
            if theme in THEMES:
                session['user_settings']['theme'] = theme
            if language in LANGUAGES:
                session['user_settings']['language'] = language

            flash("Ustawienia zostały zapisane!", "success")

        elif action == 'reset':
            session['user_settings'] = default_settings.copy()
            flash("Ustawienia zostały zresetowane!", "info")

        else:
            flash("Nieznana akcja.", "warning")

        return redirect(url_for('settings'))

    # GET
    return render_template(
        'settings.html',
        settings=session['user_settings'],
        themes=THEMES,
        languages=LANGUAGES,
    )



@app.route('/import_csv', methods=['POST'])
def import_csv():
    try:
        file = request.files['csv_file']
        if not file:
            flash("Nie wybrano pliku.", "warning")
            return redirect('/portfolio')

        try:
            df = pd.read_csv(file, header=0)
        except UnicodeDecodeError:
            file.seek(0)
            df = pd.read_csv(file, encoding="cp1250")

        if df.empty:
            flash("Plik CSV jest pusty.", "warning")
            return redirect('/portfolio')

        # Dopisz dane do previous.csv
        previous_path = os.path.join('data', 'previous.csv')
        if os.path.exists(previous_path):
            previous_df = pd.read_csv(previous_path)
            combined_df = pd.concat([previous_df, df], ignore_index=True)
        else:
            combined_df = df

        combined_df.to_csv(previous_path, index=False)

        flash(f"Zaimportowano {len(df)} nowych wierszy. Łącznie: {len(combined_df)}", "success")
        return redirect('/portfolio')

    except Exception as e:
        flash(f"Błąd podczas importu: {e}", "danger")
        return redirect('/portfolio')


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
