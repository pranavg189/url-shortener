import math
import sys
from flask import render_template

""" base62 mapping """
base_map="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def base62_encode(number):
    """Encode a base10 number to base62 string"""
    result = ''

    while number > 0:
        result = base_map[number % 62] + result
        number = number // 62

    return result


def base62_decode(string):
    """Decode a base62 string to base10 number"""
    result = 0

    index = len(string)

    for c in string:
        result = result + base_map.index(c) * pow(62, index-1)
        index = index-1

    return result

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code
