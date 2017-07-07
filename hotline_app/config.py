import json
import os

DEFAULT_SETTINGS = {
    "ADMIN_USER" : "admin",
    "ADMIN_PASS" : "something-secret",
    "DB_USER" : "root",
    "DB_PW" : "",
    "DB_HOST" : "localhost",
    "DB_NAME" : "story_hotline",
    "TWILIO_ACCOUNT_SID" : "",
    "TWILIO_AUTH_TOKEN" : "",
    "TWILIO_PHONE_NO" : "", # "+12223456789"
    "SECRET_KEY" : "another-secret-thing",
    "DEBUG": "False"
}


config_filepath = os.path.dirname(__file__)+'/config_vars_secret.json'


# make a config file if it doesnt exist, based on default values & env vars
if not os.path.isfile(config_filepath):
    # TODO: a more elegant way of doing this?

    config_settings = {}
    for k, default_v in DEFAULT_SETTINGS.items():
        # if env var exists, use env var value - otherwise use default value
        config_settings[k] = os.getenv(k, default_v)

    with open(config_filepath, 'w') as f:
        json.dump(config_settings, f, indent=4)


# TODO: handle when config file exists but env vars have been updated



def update_config(updates):

    # start with old config
    if os.path.isfile(config_filepath):
        with open(config_filepath) as f:
            config = json.load(f)
    else:
        config = {}

    # update config accordingly
    for k, v in updates.items():
        config[k] = v

    # write config file
    with open(config_filepath, 'w') as f:
        json.dump(config, f, indent=4)



# read settings from config file
with open(config_filepath) as f:
    json_config = json.load(f)

    CONFIG_VARS = {}
    for k, default_v in DEFAULT_SETTINGS.items():
        CONFIG_VARS[k] = json_config.get(k, default_v)
