from flask import flash, redirect, request, render_template, Response, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from sqlalchemy.sql.expression import func
from sqlalchemy.exc import StatementError
import twilio.twiml
from twilio.rest import TwilioRestClient

import importlib

from hotline_app import create_app
from hotline_app import config
from hotline_app.models import Story
from hotline_app.database import db



application = create_app()
APP_URL = config.CONFIG_VARS['APP_URL']

@application.route("/")
def index():

    return render_template('index.html')


# this is for when a hotline is first launched and there aren't many stories yet
# here, people only have the option to leave messages and don't yet have the option to record
@application.route("/incoming-call-start", methods=['GET', 'POST'])
def incoming_call_start():
    resp = twilio.twiml.Response()
    # recording: introducing the project
    resp.play(APP_URL+'/static/audio/intro.mp3')

    resp.play(APP_URL+'/static/audio/prompt.mp3')
    resp.pause(length=1)
    resp.play(APP_URL+'/static/audio/prompt_extra_1.mp3')
    resp.play(APP_URL+'/static/audio/prompt_extra_2.mp3')
    resp.gather(numDigits=1, action="/handle-keypress/record", method="POST", timeout=60)

    return str(resp)


@application.route("/incoming-call", methods=['GET', 'POST'])
def incoming_call():
    resp = twilio.twiml.Response()
    # recording: introducing the project
    resp.play(APP_URL+'/static/audio/intro.mp3')
    resp.play(APP_URL+'/static/audio/decision_1a.mp3')
    resp.gather(numDigits=1, action="/handle-keypress/listen-share", method="POST", timeout=30)

    return str(resp)

@application.route("/handle-keypress/<decision>", methods=['GET', 'POST'])
def handle_keypress(decision):

    pressed = request.values.get('Digits', None)
    call_sid = request.values.get('CallSid', None)
    resp = twilio.twiml.Response()

    if decision=="listen-share":
        if pressed == '1': # listening to a story
            resp.play(APP_URL+'/static/audio/recording_intro.mp3')
            resp.pause(length=1)

            # grabbing a random story
            try:
                random_story = Story.query.filter_by(is_approved=True).order_by(func.rand()).first()
            except StatementError:
                db.session.rollback()
                random_story = Story.query.filter_by(is_approved=True).order_by(func.rand()).first()
            if random_story:
                resp.play(random_story.recording_url)

            resp.pause(length=1)
            resp.play(APP_URL+'/static/audio/decision_1b.mp3')
            resp.gather(numDigits=1, action="/handle-keypress/listen-share", method="POST", timeout=30)
        elif pressed == '2': # sharing a story
            resp.play(APP_URL+'/static/audio/prompt.mp3')
            resp.pause(length=1)
            resp.play(APP_URL+'/static/audio/prompt_extra_1.mp3')
            resp.play(APP_URL+'/static/audio/prompt_extra_2.mp3')
            resp.gather(numDigits=1, action="/handle-keypress/record", method="POST", timeout=60)
        else:
            resp.play(APP_URL+'/static/audio/decision_1a.mp3')
            resp.gather(numDigits=1, action="/handle-keypress/listen-share", method="POST", timeout=30)
    elif decision=="record":
        resp.play(APP_URL+'/static/audio/prompt_extra_3.mp3')
        resp.record(maxLength="60", action="/handle-recording")

    elif decision=="consent-contact":
        if pressed == '1': # ok to contact
            resp.play(APP_URL+'/static/audio/thanks_a.mp3')

            # update contact_ok flag
            try:
                story = Story.query.filter_by(call_sid=call_sid).first()
                story.contact_ok = True
                db.session.commit()
            except StatementError:
                db.session.rollback()
                story = Story.query.filter_by(call_sid=call_sid).first()
                story.contact_ok = True
                db.session.commit()

        elif pressed == '2': # not ok to contact
            resp.play(APP_URL+'/static/audio/thanks_b.mp3')


    return str(resp)


@application.route("/handle-recording", methods=['GET', 'POST'])
def handle_recording():
    recording_url = request.values.get('RecordingUrl', None)
    call_sid = request.values.get('CallSid', None)
    from_number = request.values.get('From', None)

    resp = twilio.twiml.Response()

    if recording_url:
        try:
            new_story = Story(call_sid, from_number, recording_url)
            db.session.add(new_story)
            db.session.commit()
        except StatementError:
            db.session.rollback()
            new_story = Story(call_sid, from_number, recording_url)
            db.session.add(new_story)
            db.session.commit()

    resp.play(APP_URL+'/static/audio/thanks_a.mp3')
    resp.play(APP_URL+'/static/audio/decision_2.mp3')
    resp.gather(numDigits=1, action="/handle-keypress/consent-contact", method="POST", timeout=30)

    return str(resp)


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    ADMIN_USER = config.CONFIG_VARS['ADMIN_USER']
    ADMIN_PASS = config.CONFIG_VARS['ADMIN_PASS']
    return username == ADMIN_USER and password == ADMIN_PASS

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your credentials for that url', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@application.route('/review')
@requires_auth
def review():

    try:
        review_queue = Story.query.filter_by(is_approved=None).all()
        approved = Story.query.filter_by(is_approved=True).all()
    except StatementError:
        db.session.rollback()
        review_queue = Story.query.filter_by(is_approved=None).all()
        approved = Story.query.filter_by(is_approved=True).all()

    return render_template('review.html', review_queue = review_queue, approved=approved)

@application.route('/reviewtrash')
@requires_auth
def reviewtrash():

    disapproved = Story.query.filter_by(is_approved=False).all()

    return render_template('reviewtrash.html', disapproved=disapproved)



@application.route('/approve/<story_id>')
@requires_auth
def approve(story_id):
    story = Story.query.get(story_id)
    story.is_approved = True
    db.session.commit()
    return redirect('/review')

@application.route('/disapprove/<story_id>')
@requires_auth
def disapprove(story_id):
    story = Story.query.get(story_id)
    story.is_approved = False
    db.session.commit()
    return redirect('/review')


@application.route('/settings', methods=['GET', 'POST'])
@requires_auth
def settings():

    if request.method == 'POST':

        new_config = {
            "TWILIO_ACCOUNT_SID": request.form['twilio-account-sid'],
            "TWILIO_AUTH_TOKEN": request.form['twilio-auth-token'],
            "TWILIO_PHONE_NO": request.form['twilio-phone-no'],
        }

        config.update_config(new_config)
        importlib.reload(config)

        flash("settings updated!")

    return render_template('settings.html', CONFIG_VARS=config.CONFIG_VARS)


@application.route('/initialize')
@requires_auth
def initialize():
    db.create_all()
    flash("db initialized!")
    return redirect('/')



if __name__ == "__main__":

    application.secret_key = config.CONFIG_VARS['SECRET_KEY']
    debug = True if config.CONFIG_VARS['DEBUG'] == 'True' else False
    application.run(debug=debug, host='0.0.0.0')
