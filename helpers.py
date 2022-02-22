import os
import requests
import urllib.request
import json

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """ Render message as an apology to user """
    def escape(s):
        """
        Escape special characters

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                        ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# Search IMDB API for matching titles
def lookupTitle(title, type):
    """ Look up show or movie """

    # Contact API
    try:
        api_key = os.environ.get("IMDB_API_KEY")
        url = f"https://imdb-api.com/en/API/{type}/{api_key}/{title}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        data = response.json()
        return data
    except (KeyError, TypeError, ValueError):
        return None


# Search Watchmode API
def getTitleId(imdbID):
    """ Search Watchmode in order to get the movie/show id to then find its streaming sites """

    # Contact API
    try:
        watch_api_key = os.environ.get("WATCHMODE_API_KEY")
        url = f"https://api.watchmode.com/v1/search/?apiKey={watch_api_key}&search_field=imdb_id&search_value={imdbID}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        data = response.json()
        return data
    except (KeyError, TypeError, ValueError):
        return None


# Search Watchmode API
def getDetails(titleId):
    """ Search Watchmode for sources """

    # Contact API
    try:
        watch_api_key = os.environ.get("WATCHMODE_API_KEY")
        url = f"https://api.watchmode.com/v1/title/{titleId}/details/?apiKey={watch_api_key}&append_to_response=sources&regions=US"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        data = response.json()
        return data
    except (KeyError, TypeError, ValueError):
        return None


# Search Watchmode API for source details
def getSourceDetails():
    """ Search Watchmode for source details to store in list of dicts """

    # Contact API
    try:
        watch_api_key = os.environ.get("WATCHMODE_API_KEY")
        url = f"https://api.watchmode.com/v1/sources/?apiKey={watch_api_key}&regions=US"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        data = response.json()
    except (KeyError, TypeError, ValueError):
        return None

    # Remove unneccessary data and change key/value to be id/name
    try:
        for d in data:
            d[d["id"]] = d.pop("name", None)
            d.pop("id", None)
            d.pop("type", None)
            d.pop("logo_100px", None)
            d.pop("ios_appstore_url", None)
            d.pop("android_playstore_url", None)
            d.pop("android_scheme", None)
            d.pop("ios_scheme", None)
            d.pop("regions", None)
        return data
    except (KeyError, TypeError, ValueError):
        return None