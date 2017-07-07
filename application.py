from flask import flash, redirect, request, render_template, Response, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from hotline_app import create_app
from hotline_app import config
from hotline_app.models import Story
from hotline_app.database import db
import twilio.twiml
from twilio.rest import TwilioRestClient
import importlib



application = create_app()

@application.route("/")
def index():

    return render_template('index.html')


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
