from flask import Flask, jsonify, render_template, Response, request, redirect, abort, url_for, send_file
from flask_cors import CORS
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from oauthlib.oauth2 import WebApplicationClient
import json
import os
import math
import requests
import re
from find_more_like_algorithm.constants import IMDB_ID, TITLE, IMDB_ID_REGEX_PATTERN, PLOT, OMDB_USER_KEY, USER_SEEN
from find_more_like_algorithm.utils import KEYS_CONFIG, PROJECT_CONFIG, WEBAPP_PATH, RAW_IMDB_DATA_PATH, \
    SIMILAR_LIST_SAVING_PATH, open_json, TITLE_TO_ID_JSON_PATH, AVAILABLE_TITLES_JSON_PATH, \
    get_imdb_id_prefix_folder_name, ROOT_PATH
from webapp.db_handler import DB, SeenTitles, MissingTitles
from webapp.poster_images_handling import delete_oldest_cached_image_if_cached_poster_images_limit_reached, \
    _get_cached_image_path, _save_image
from webapp.user import User, get_user_by_id

VERSION_NUMBER = "0.0.1"
ONE_PAGE_SUGGESTIONS_AMOUNT = 10

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", KEYS_CONFIG["google_client_id"])
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", KEYS_CONFIG["google_client_secret"])
GOOGLE_DISCOVERY_URL = ("https://accounts.google.com/.well-known/openid-configuration")

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# User session management setup - https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# create db and tables
DB().create_tables()

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

TITLE_TO_ID_MAPPING = open_json(TITLE_TO_ID_JSON_PATH)
AVAILABLE_TITLES = open_json(AVAILABLE_TITLES_JSON_PATH)


@app.route("/get_available_titles")
def get_titles():
    searched_term = request.args.get("term")
    if searched_term is None:
        return jsonify(None)

    titles_containing_term = []
    for title in AVAILABLE_TITLES:
        if _is_searched_term_contained_in_title(searched_term, title):
            titles_containing_term.append(title)

    amount_of_titles_containing_term = len(titles_containing_term)
    max_title_amount_to_return = 100
    if amount_of_titles_containing_term > max_title_amount_to_return:
        titles_containing_term = titles_containing_term[:max_title_amount_to_return]
        titles_containing_term.append(
            f"*** There are {amount_of_titles_containing_term - max_title_amount_to_return} more titles matching to the search, please refine your search ***")
    return jsonify(titles_containing_term)


def _is_searched_term_contained_in_title(searched_term, title):
    # TODO maybe remove non [A-Z\d], maybe remove stop words
    title_lowered = title.lower()
    searched_term_lowered = searched_term.lower()
    if searched_term_lowered in title_lowered:
        return True
    else:
        return False


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)


def get_google_provider_cfg():  # todo: add error handling
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in your db with the information provided by Google
    user = User(
        google_id=unique_id, name=users_name, email=users_email, profile_pic=picture
    )

    # Begin user session by logging the user in
    login_user(user, remember=True)

    # Send user back to homepage
    return redirect(url_for("main"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main"))


@app.route('/')
def main():
    return render_template('homepage.html', version_number=VERSION_NUMBER, current_user=current_user)


@app.route('/search')
def search_redirect():
    query = request.args.get('selected-title')
    hide_seen_titles = request.args.get('hide-seen-titles')
    page_index = request.args.get('page_index', default=0)
    app.logger.info(hide_seen_titles)
    return redirect(f'/search/{query}/{hide_seen_titles}/{page_index}')


@app.route('/search/<string:title>/<string:hide_seen_titles>/<int:page_index>')
def search(title, hide_seen_titles, page_index):
    # hide_seen_titles = hide_seen_titles.lower() == "on"  # TODO make this boolean
    imdb_id = TITLE_TO_ID_MAPPING[title]
    search_results_response = get_limited_search_results(imdb_id, hide_seen_titles, page_index)
    search_results = json.loads(search_results_response.data)
    return render_template('search_results.html',
                           **search_results,
                           version_number=VERSION_NUMBER)


@app.route('/get_limited_search_results/<string:imdb_id>/<string:hide_seen_titles>/<int:page_index>')
def get_limited_search_results(imdb_id, hide_seen_titles, page_index):  # TODO: move this logic to search
    similarity_list = _get_similarity_list(imdb_id)
    max_page_number = math.ceil(len(similarity_list) / ONE_PAGE_SUGGESTIONS_AMOUNT) - 1  # page number starts from 0
    if page_index > max_page_number:
        abort(404, description="Resource not found")

    user_seen_imdb_ids = get_user_seen_imdb_ids()
    results = get_movies_presentation_data(imdb_id,
                                           similarity_list,
                                           user_seen_imdb_ids)
    if hide_seen_titles.lower() == "on":
        results = [result for result in results if results[USER_SEEN]]

    start_index = ONE_PAGE_SUGGESTIONS_AMOUNT * page_index
    end_index = start_index + ONE_PAGE_SUGGESTIONS_AMOUNT
    results = results[start_index: end_index]

    requested_title_data = load_presentation_data(imdb_id)
    data = {
        "similarity_results": results,
        "requested_title_data": requested_title_data,
        "current_page_index": page_index,
        "max_page_number": max_page_number,
        "hide_seen_titles": hide_seen_titles,
    }
    return jsonify(data)


@app.route('/get_all_search_results/<string:imdb_id>')
def get_all_search_results(imdb_id):
    similarity_list = _get_similarity_list(imdb_id)
    user_seen_imdb_ids = get_user_seen_imdb_ids()
    results = get_movies_presentation_data(imdb_id, similarity_list, user_seen_imdb_ids)
    requested_title_data = load_presentation_data(imdb_id)
    data = {
        "similarity_results": results,
        "requested_title_data": requested_title_data,
    }
    return jsonify(data)


def _get_similarity_list(imdb_id):
    prefix = get_imdb_id_prefix_folder_name(imdb_id)
    similarity_list_file_path = SIMILAR_LIST_SAVING_PATH.joinpath(prefix, f'{imdb_id}.json')
    similarity_list = open_json(similarity_list_file_path)

    return similarity_list


def get_movies_presentation_data(requested_imdb_id, similarity_list, user_seen_imdb_ids):
    results = []
    for imdb_id, similarity_value in similarity_list:  # TODO use similarity_value
        if imdb_id == requested_imdb_id:
            continue

        imdb_id_presentation_data = load_presentation_data(imdb_id)
        imdb_id_presentation_data[USER_SEEN] = imdb_id_presentation_data[IMDB_ID] in user_seen_imdb_ids
        results.append(imdb_id_presentation_data)

    return results


def _load_imdb_data(imdb_id):
    imdb_id_folder_prefix = get_imdb_id_prefix_folder_name(imdb_id)
    file_path = os.path.join(RAW_IMDB_DATA_PATH, imdb_id_folder_prefix, f'{imdb_id}.json')
    if os.path.exists(file_path):
        imdb_data = open_json(file_path)
        return imdb_data
    else:
        raise FileNotFoundError(f'.... {file_path} ... ')  # todo: is this how you should do it ?


def load_presentation_data(imdb_id):
    imdb_data = _load_imdb_data(imdb_id)
    if imdb_data:
        return {
            **imdb_data,
            'IMDb_path': 'https://www.imdb.com/title/{}/'.format(imdb_id)
        }


def get_user_seen_imdb_ids():
    if current_user.is_authenticated:
        user_id = current_user.get_id()
        with DB() as db:
            rows = db.session.query(
                SeenTitles
            ).filter(
                SeenTitles.user_id == user_id
            ).all()

            seen_imdb_ids = [row.imdb_id for row in rows]

        return set(seen_imdb_ids)
    else:
        return set()


@app.route('/save_seen_checkbox', methods=["POST"])
def save_seen_checkbox():
    imdb_id, _ = request.form.get("id").split("_")
    checkbox_status = request.form.get("status")
    checkbox_status = checkbox_status.lower() == 'true'  # todo: this value return stings

    if current_user.is_authenticated:
        user_id = current_user.get_id()
        with DB() as db:
            if checkbox_status:
                seen_title = SeenTitles(user_id=user_id, imdb_id=imdb_id)
                db.session.add(seen_title)
            else:
                seen_titles = db.session.query(
                    SeenTitles
                ).filter(
                    SeenTitles.user_id == user_id,
                    SeenTitles.imdb_id == imdb_id
                ).all()

                for seen_title in seen_titles:
                    db.session.delete(seen_title)

            db.session.commit()

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


@app.route('/save_missing_titles', methods=["POST"])
def save_missing_titles():
    link_to_imdb = request.form.get("imdb_link")
    found_imdb_ids = re.findall(IMDB_ID_REGEX_PATTERN, str(link_to_imdb))
    if not found_imdb_ids:  # if no IMDb id was found
        raise ValueError("Bad")
    with DB() as db:
        for imdb_id in found_imdb_ids:
            missing_title = MissingTitles(imdb_link=link_to_imdb, imdb_id=imdb_id)
            db.session.add(missing_title)
            db.session.commit()

    return jsonify({"missing_link": link_to_imdb})  # todo: return warning if bad input / return success and failure


@app.route('/get_poster_image/<string:imdb_id>')
def get_poster_image(imdb_id):
    # TODO: make sure imdb_id_ is valid
    # TODO: resize images ?
    cached_image_path = _get_cached_image_path(imdb_id)
    if cached_image_path.exists():
        return send_file(cached_image_path, mimetype='image/PNG')

    delete_oldest_cached_image_if_cached_poster_images_limit_reached()
    api_key = KEYS_CONFIG[OMDB_USER_KEY]
    response = requests.get(f"http://img.omdbapi.com/?apikey={api_key}&i={imdb_id}", stream=True)
    if response.status_code == 200:
        _save_image(cached_image_path, response.content)
        return send_file(cached_image_path, mimetype='image/PNG')
    else:
        imdb_data = _load_imdb_data(imdb_id)
        imdb_poster_link = imdb_data["Poster"]
        if "http" in imdb_poster_link:  # TODO: make this better
            response = requests.get(imdb_poster_link, stream=True)
            _save_image(cached_image_path, response.content)
            return send_file(cached_image_path, mimetype='image/PNG')
        else:
            no_poster_image_found_image_path = ROOT_PATH.joinpath("webapp", "static", "no_poster_image_found.png")
            return send_file(no_poster_image_found_image_path, mimetype='image/PNG')


if __name__ == "__main__":
    app.run(ssl_context="adhoc")
