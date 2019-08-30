from flask import Flask, jsonify, render_template, Response
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


@app.route('/hello')
def hello():
    return jsonify({'about': 'Hello World!'})


@app.route('/find/<string:imdb_id>')
def find_most_similar(imdb_id):

    file_path = os.path.join('similar_list_data', '{}.json'.format(imdb_id)) # todo: load path from config
    if os.path.exists(file_path):
        return jsonify(_open_json(file_path))
    else:
        raise FileNotFoundError('.... ? ... ') #todo: is this how you should do it ?


@app.route('/show/<string:imdb_id>')
def load_showing_data(imdb_id):
    file_path = os.path.join('raw_imdb_data', '{}.json'.format(imdb_id)) # todo: load path from config
    if os.path.exists(file_path):
        imdb_data = _open_json(file_path)
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

### TODO: static page for the time of transition
@app.route("/<path:filename>")
def static_file(filename = None):
    #index.html  redirect

    mime = 'text/html'
    try:
        content = open(root + '/html/' + filename, 'rb').read()
    except Exception:
        return not_found()

    if filename[-4:] == '.css':
        mime = 'text/css'
    elif filename[-5:] == '.json':
        mime = 'application/javascript'
    elif filename[-3:] == '.js':
        mime = 'application/javascript'
    elif filename[-4:] == '.xml':
        mime = 'text/xml'
    elif filename[-4:] == '.jpg':
        mime = 'image/jpg'
    elif filename[-4:] == '.ico':
        mime = 'image/x-icon'
    return Response(content, mimetype=mime)

@app.errorhandler(404)
def not_found(e = None):
    return render_template('404.html',
                       h1='404',
                       title='Four Oh Four',
                       ), 404



# todo: cookie-based authentication
# todo: deal with bad inputs (?)
# todo: connect to an actual server
# if __name__ == '__main__':
    # app.run(debug=True)
