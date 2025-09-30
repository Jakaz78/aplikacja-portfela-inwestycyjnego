from .. import db

class SettingsOption(db.Model):
    __tablename__ = 'settings_options'

    id = db.Column(db.SmallInteger, primary_key=True)
    theme = db.Column(db.String(10), nullable=False)      # np. 'Dark' lub 'Light'
    language = db.Column(db.String(16), nullable=False)   # np. 'Polski', 'Deutsch', 'English'

    def __repr__(self):
        return f"<SettingsOption id={self.id} theme={self.theme} language={self.language}>"
