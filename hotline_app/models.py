import datetime

from .database import db


class Story(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    call_sid = db.Column(db.String(255))
    from_number = db.Column(db.String(255))
    recording_url = db.Column(db.String(255), unique=True)

    contact_ok = db.Column(db.Boolean)
    is_approved = db.Column(db.Boolean)

    dt = db.Column(db.DateTime, default=datetime.datetime.now)


    def __init__(self, call_sid, from_number, recording_url, contact_ok=False, is_approved=False):
        self.call_sid = call_sid
        self.from_number = from_number
        self.recording_url = recording_url
        self.contact_ok = contact_ok
        self.is_approved = is_approved

    def __repr__(self):
        return '<Story %r>' % self.recording_url
