from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ShoppingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    quantity = db.Column(db.Integer, default=1)
