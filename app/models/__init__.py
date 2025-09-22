from .. import db


class Obligacje(db.Model):
    __tablename__ = 'obligacje'
    id = db.Column(db.BigInteger, primary_key=True)
    csv_content = db.Column(db.Text, nullable=False)


