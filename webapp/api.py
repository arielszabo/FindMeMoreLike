from flask import Flask, jsonify, render_template, Response, request, redirect, abort, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from oauthlib.oauth2 import WebApplicationClient
import json
import os
import yaml
import math
import sqlite3


# Internal imports todo: change
from db import init_db_command
from user import User


def _open_json(full_file_path):
    with open(full_file_path, 'r') as jfile:
        return json.load(jfile)


VERSION_NUMBER = "0.0.1"
ONE_PAGE_SUGGESTIONS_AMOUNT = 10

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(root, 'project_config.yaml'), 'r') as yfile:
    project_config = yaml.load(yfile, Loader=yaml.FullLoader)


with open(os.path.join(root, project_config["keys_config_path"]), 'r') as yfile:
    keys_config = yaml.load(yfile, Loader=yaml.FullLoader)



GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", keys_config["google_client_id"])
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", keys_config["google_client_secret"])
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)


# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)


# todo: create db and tables
# Naive database setup
try:
    init_db_command()
except sqlite3.OperationalError:
    # Assume it's already been created
    pass


# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)  # todo: query the user data here


@app.route('/')
def main():
    return render_template('homepage.html', version_number=VERSION_NUMBER)

@app.route('/search')
def search_redirect():
    query = request.args.get('imdbid')
    title = request.args.get('movie-name')
    page_index = request.args.get('page_index', default=0)
    return redirect(f'/search/{query}/{title}/{page_index}')

@app.route('/search/<string:imdb_id>/<string:title>/<int:page_index>')
def search(imdb_id, title, page_index):
    file_path = os.path.join(root, project_config["similar_list_saving_path"], '{}.json'.format(imdb_id))
    similarity_list = _open_json(file_path)
    max_page_number = math.ceil(len(similarity_list) / ONE_PAGE_SUGGESTIONS_AMOUNT) - 1  # page number starts from 0
    if page_index > max_page_number:
        abort(404, description="Resource not found")

    start_index = ONE_PAGE_SUGGESTIONS_AMOUNT*page_index
    end_index = ONE_PAGE_SUGGESTIONS_AMOUNT*(page_index+1)
    sliced_similarity_list = similarity_list[start_index:end_index]

    results = [load_presentation_data(similar_movie['imdbID']) for similar_movie in sliced_similarity_list]

    return render_template('search_results.html',
                           similarity_results=results,
                           request_title=title,
                           search_request=imdb_id,  #todo: rename
                           current_page_index=page_index,
                           max_page_number=max_page_number,
                           version_number=VERSION_NUMBER)


def load_presentation_data(imdb_id):
    file_path = os.path.join(root, project_config["api_data_saving_path"]["imdb"], '{}.json'.format(imdb_id))
    if os.path.exists(file_path):
        imdb_data = _open_json(file_path)
        return {
            'Title': imdb_data['Title'],
            'Director': imdb_data['Director'],
            'Plot': imdb_data['Plot'],
            'Year': imdb_data['Year'],
            'Poster': imdb_data['Poster'],
            'imdbID': imdb_data['imdbID'],
            'IMDb_path': 'https://www.imdb.com/title/{}/'.format(imdb_id)
        }

    else:
        raise FileNotFoundError(f'.... {file_path} ... ') #todo: is this how you should do it ?

@app.route('/save_seen_checkbox', methods=["POST"])
def save_seen_checkbox():
    imdbID = request.form.get("id")
    checkbox_status = request.form.get("status")

    return jsonify({"ok": 1})


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html',
                       h1='404',
                       title='Four Oh Four',
                       ), 404


@app.route('/privacy')
def privacy():
    return render_template('privacy.html', version_number=VERSION_NUMBER)