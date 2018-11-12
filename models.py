import os

from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ShortURL(db.Model):
    __tablename__ = "shorturl"
    id = db.Column(db.Integer, primary_key=True)
    longurl = db.Column(db.String, nullable=False, index=True, unique=True)
    urltitle = db.Column(db.String, nullable=False, index=True)
    creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expiry_time_minutes = db.Column(db.Integer, nullable=False, default=0)
    clicks = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<ShortURL({self.id}): {self.urltitle}>"
