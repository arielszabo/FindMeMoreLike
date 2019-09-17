from flask import Flask, jsonify, render_template, Response, request, redirect
import json
import os
import yaml

VERSION_NUMBER = "0.0.1"
ONE_PAGE_SUGGESTIONS_AMOUNT = 10

app = Flask(__name__)
root = os.path.dirname(os.path.dirname(__file__))


def _open_json(full_file_path):
    with open(full_file_path, 'r') as jfile:
        return json.load(jfile)


with open(os.path.join(root, 'project_config.yaml'), 'r') as yfile:
    project_config = yaml.load(yfile)



@app.route('/')
def main():
    return render_template('homepage.html', version_number=VERSION_NUMBER)

@app.route('/search')
def search_redirect():
    query = request.args.get('imdbid')
    title = request.args.get('title')
    return redirect('/search/' + query + '/' + title)

@app.route('/search/<string:imdb_id>/<string:title>')
def search(imdb_id, title):
    file_path = os.path.join(root, project_config["similar_list_saving_path"], '{}.json'.format(imdb_id))
    similarity_list = _open_json(file_path)[:ONE_PAGE_SUGGESTIONS_AMOUNT]
    results = [load_presentation_data(similar_movie['imdbID']) for similar_movie in similarity_list]

    return render_template('search_results.html',
                           similarity_results=results,
                           request_title=title,
                           search_request=imdb_id,
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
            'IMDb_path': 'https://www.imdb.com/title/{}/'.format(imdb_id)
        }

    else:
        raise FileNotFoundError(f'.... {file_path} ... ') #todo: is this how you should do it ?


@app.errorhandler(404)
def not_found():
    return render_template('404.html',
                       h1='404',
                       title='Four Oh Four',
                       ), 404



# todo: cookie-based authentication
# todo: deal with bad inputs (?)
# todo: connect to an actual server
# if __name__ == '__main__':
    # app.run(debug=True)
