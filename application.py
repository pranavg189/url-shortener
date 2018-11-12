import os
from flask import Flask, flash, render_template, redirect, request, jsonify
from models import *
from helpers import *
from bs4 import BeautifulSoup
import urllib.request
from sqlalchemy import or_
from datetime import datetime, timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

# Configure application
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(basedir, 'urlinfo.db')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.secret_key = "super secret key"

db.init_app(app)

@app.route('/')
def index():
    """Display form to create a short url"""
    return render_template("shorten.html")

@app.route('/create', methods=["POST"])
def create():
    """Create short URL"""
    longurl = request.form.get("longurl")
    expiry_time = request.form.get("expiry")

    if longurl == '':
        flash("An error occured. Please scroll below....")
        return apology("Empty URL ! Please enter a valid URL")

    # check whether the longurl already exists
    shorturl = ShortURL.query.filter_by(longurl=longurl).first()

    if shorturl != None:
        base62_string = base62_encode(shorturl.id)
        return render_template("exists.html", base62_string=base62_string)
    else:

        # validate whether url is a valid url or not
        try:
            soup = BeautifulSoup(urllib.request.urlopen(longurl), features="html.parser")
        except urllib.error.HTTPError:
            flash("An error occured. Please scroll below....")
            return apology("Unreachable URL ! Please enter a valid URL")
        except ValueError:
            flash("An error occured. Please scroll below....")
            return apology("Invalid URL string ! Please enter a valid URL")

        if soup.title == None:
            urltitle = "Not Applicable"
        else:
            # strip leading and trailing whitespaces
            urltitle = (soup.title.string).strip()

        # if valid url and reachable, proceed to save it into the database
        if expiry_time == None:
            new_shorturl = ShortURL(longurl=longurl, urltitle=urltitle)
        else:
            new_shorturl = ShortURL(longurl=longurl, urltitle=urltitle, expiry_time_minutes=expiry_time)

        db.session.add(new_shorturl)
        db.session.commit()

        flash("The short URL creation was successful !")

        base62_string = base62_encode(new_shorturl.id)

        return render_template("created.html", base62_string=base62_string, expiry_time=expiry_time)

@app.route('/shorturl/<string:base62_string>')
def open_short_url(base62_string):
    """Redirect to long url"""
    base10_number = base62_decode(base62_string)
    shorturl = ShortURL.query.get(base10_number)

    if shorturl == None:
        flash("An error occured. Please scroll below....")
        return apology("No such short URL exists ! Please enter a valid short URL")
    else:

        # check if the url has expired
        current_time = datetime.utcnow()
        short_url_time = shorturl.creation_date + timedelta(minutes=shorturl.expiry_time_minutes)

        if current_time > short_url_time and shorturl.expiry_time_minutes != 0:
            db.session.delete(shorturl)
            db.session.commit()
            flash("An error occured. Please scroll below....")
            return apology("This short URL has expired and hence was deleted ! Please create a new one.")
        else:
            shorturl.clicks = shorturl.clicks + 1
            db.session.commit()
            return redirect(shorturl.longurl)

# API to return longurl or url-titles matching the given query
@app.route('/search', methods=["GET"])
def search():
    json_result = []
    query = '%' + request.args.get("query") + '%'

    rows = ShortURL.query.filter(or_(ShortURL.longurl.ilike(query), ShortURL.urltitle.ilike(query))).all()

    result_id = 1
    for row in rows:
        shorturl = {}
        shorturl["result id"] = result_id
        shorturl["url"] = row.longurl
        shorturl["title"] = row.urltitle

        json_result.append(shorturl)
        result_id = result_id + 1

    if len(json_result) == 0:
        json_result.append("Sorry, no results found !")

    return jsonify(json_result)


@app.route('/info/<string:base62_string>')
def get_short_url_info(base62_string):
    """Present readable information about the short url"""
    shorturl_json = {}

    base10_number = base62_decode(base62_string)
    shorturl = ShortURL.query.get(base10_number)

    if shorturl == None:
        flash("An error occured. Please scroll below....")
        return apology("No such short URL exists ! Please enter a valid short URL")
    else:

        shorturl_json["url"] = shorturl.longurl
        shorturl_json["title"] = shorturl.urltitle
        shorturl_json["creation_date"] = shorturl.creation_date

        if shorturl.expiry_time_minutes != 0:
            shorturl_json["expiry_time"] = shorturl.expiry_time_minutes
        else:
            shorturl_json["expiry_time"] = "Unlimited"

        # check if the url has expired as of now
        current_time = datetime.utcnow()
        short_url_time = shorturl.creation_date + timedelta(minutes=shorturl.expiry_time_minutes)

        if current_time > short_url_time and shorturl.expiry_time_minutes != 0:
            shorturl_json["status"] = "expired"
        else:
            shorturl_json["status"] = "active"

        shorturl_json["clicks"] = shorturl.clicks

        return jsonify(shorturl_json)

@app.route('/url')
def url():
    """Test Redirection"""
    return redirect("https://docs.google.com/document/d/1EmDo9WJJSuKch89Bdr6uEtbT5GAyMlaV_NEBQEA5yQE/edit")


"""Run this block of code to create the initial tables for the model"""
def main():
    db.create_all()

if __name__ == "__main__":
    with app.app_context():
        main()
