from flask import Flask, jsonify, render_template, Response, request, redirect, abort
import json
import os
import yaml
import math

VERSION_NUMBER = "0.0.1"
ONE_PAGE_SUGGESTIONS_AMOUNT = 10

app = Flask(__name__)

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _open_json(full_file_path):
    with open(full_file_path, 'r') as jfile:
        return json.load(jfile)


with open(os.path.join(root, 'project_config.yaml'), 'r') as yfile:
    project_config = yaml.load(yfile, Loader=yaml.FullLoader)



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


# todo: cookie-based authentication
# todo: deal with bad inputs (?)
# todo: connect to an actual server
# if __name__ == '__main__':
    # app.run(debug=True)
