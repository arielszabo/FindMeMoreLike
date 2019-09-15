from flask import Flask, jsonify, render_template, Response, request
import json
import os

app = Flask(__name__)
root = os.path.dirname(os.path.dirname(__file__))


def _open_json(full_file_path):
    with open(full_file_path, 'r') as jfile:
        return json.load(jfile)



@app.route('/')
def main():
    return render_template('homepage.html')


@app.route('/search/<string:imdb_id>')
def search(imdb_id):
    file_path = os.path.join('similar_list_data', '{}.json'.format(imdb_id))  # todo: load path from config
    similarity_list = _open_json(file_path)[:5]
    results = [load_presentation_data(similar_movie['imdbID']) for similar_movie in similarity_list]

    return render_template('search_results.html', similarity_results=results)


def load_presentation_data(imdb_id):
    file_path = os.path.join('raw_imdb_data', '{}.json'.format(imdb_id)) # todo: load path from config
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
