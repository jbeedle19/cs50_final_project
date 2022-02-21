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

# Search for where the show is streaming
# "https://api.watchmode.com/v1/title/{titleID}/sources/?apiKey={API_KEY}"

# Search for show/movie
# "https://api.watchmode.com/v1/search/?apiKey={API_KEY}&search_field=name&search_value={title}&types={type}"