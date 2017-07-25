# story-hotline
playing &amp; collecting audio stories over phone calls

## About
This is a web app built with Python (a programming language) and Flask (a python web framework). It allows you to collect audio messages via a phone hotline, & is designed to work with Twilio.

Features:
- callers can leave messages, which are recorded
- callers can choose to listen to random messages from other callers (my goal here was to engineer serendipity)
- callers can opt in to being contacted by a reporter
- admin users can moderate the messages that come in, to decide which ones can be public on the hotline

This documentation is a draft & is thus far from complete. Please reach out (cathy.deng at buzzfeed.com) with any questions!

## How to use this project to create a functioning hotline

1. get a Twilio account & buy a phone number. Twilio is a service for routing phone activity so that you can handle it programmatically.
2. deploy this Python Flask app (i.e. publish it so that it lives on the internet somewhere)
    - (MORE DOCUMENTATION TO COME)
3. configure your Twilio phone number
    - set incoming calls to hit `wherever-your-app-is-deployed.com/incoming-call` (if you want callers to be able to record & listen) OR `wherever-your-app-is-deployed.com/incoming-call-start` (if you want callers to only be able to record)
    
NOTE: if you do this, you will end up with a hotline that has our hard-coded BuzzFeed audio recordings. To have your own audio recordings, you will need to fork this project (i.e. copy and have your own version) and update the mp3s (MORE DOCUMENTATION TO COME)

## Running this app locally (for development)
**1. Install OS level dependencies**
  - Python 3
  - MySQL

**2. Clone this repo**
  ```bash
  git clone https://github.com/buzzfeed-openlab/story-hotline.git
  cd story-hotline
  ```

**3. Install required python libraries**  

Optional but recommended: make a virtual environment using [virtualenv](https://virtualenv.readthedocs.io/en/latest/) and [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/install.html).

Notes:
- Instructions for setting up virtualenv [here](http://docs.python-guide.org/en/latest/dev/virtualenvs/).
- `mkvirtualenv` will automatically activate the `speakeasy` environment; to activate it in the future, just use `workon speakeasy`
- if the virtualenv you make isn't python 3 (check w/ `python --version`), use `mkvirtualenv speakeasy -p /path/to/your/python3` (find your python3 path with `which python3`)

```bash
mkvirtualenv speakeasy
```

Install requirements:
```bash
pip install -r requirements.txt
```


**4. Create a MySQL database**

```bash
mysql -u root
```
& then
```bash
create database story_hotline;
```

If you're working locally, you're good to go. But if you're going to host this on a shared server you probably want to create a new user for this database so it isn't all `root`.

**5. Configure the app**

Two ways of doing this: (a) making a config file or (b) setting environment variables

*Option A*:  
Make the secret json config file, `hotline_app/config_vars_secret.json`
Then, edit the config file (MORE DOCUMENTATION DETAILS TO COME)

*Option B*:  
see the keys in `DEFAULT_SETTINGS` in `hotline_app/config.py` for the names of environment variables to set (MORE DOCUMENTATION DETAILS TO COME)

**6. Run the app**

  ```bash
  python application.py
  ```

**7. Initialize the database**

  Visit the `/initialize` route (e.g. `localhost:5000/intialize`) & enter admin credentials (`ADMIN_USER` & `ADMIN_PASS`). This will create the `story` table for storing responses.
