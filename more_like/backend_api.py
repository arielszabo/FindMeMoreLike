from flask import Flask, jsonify
import utils
import os

app = Flask(__name__)
root = os.path.dirname(os.path.dirname(__file__))

def _send(filename):
    with open(filename, 'r') as f:
        return f.read()

@app.route('/')
def main():
    return _send(os.path.join(root, 'html', 'homepage.html'))


@app.route('/hello')
def hello():
    return jsonify({'about': 'Hello World!'})


@app.route('/find/<string:imdb_id>')
def find_most_similar(imdb_id):

    file_path = os.path.join('similar_list_data', '{}.json'.format(imdb_id)) # todo: load path from config
    if os.path.exists(file_path):
        return jsonify(utils.open_json(file_path))
    else:
        raise FileNotFoundError('.... ? ... ') #todo: is this how you should do it ?

@app.route('/show/<string:imdb_id>')
def load_showing_data(imdb_id):
    file_path = os.path.join('raw_imdb_data', '{}.json'.format(imdb_id)) # todo: load path from config
    if os.path.exists(file_path):
        imdb_data = utils.open_json(file_path)
        return jsonify({
            'Title': imdb_data['Title'],
            'Director': imdb_data['Director'],
            'Plot': imdb_data['Plot'],
            'Year': imdb_data['Year'],
            'Poster': imdb_data['Poster'],
            'IMDb_path': 'https://www.imdb.com/title/{}/'.format(imdb_id)
        })
    else:
        raise FileNotFoundError('.... ? ... ') #todo: is this how you should do it ?

# todo: cookie-based authentication
# todo: deal with bad inputs (?)
# todo: connect to an actual server
# if __name__ == '__main__':
    # app.run(debug=True)
