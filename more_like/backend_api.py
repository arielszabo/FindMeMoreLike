from flask import Flask, jsonify
import utils
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({'about': 'Hello World!'})


@app.route('/find/<string:imdb_id>')
def find_most_similar(imdb_id):

    file_path = os.path.join('similar_list_data', '{}.json'.format(imdb_id))
    if os.path.exists(file_path):
        return jsonify(utils.open_json(file_path))
    else:
        raise FileNotFoundError('.... ? ... ') #todo: is this how you should do it ?

if __name__ == '__main__':
    app.run(debug=True)
