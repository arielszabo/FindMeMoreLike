# FindMeMoreLike


Pre-Trained Doc2Vec model is saved in the 'enwiki_dbow' folder and it is from https://github.com/jhlau/doc2vec

# Need to Know:
- save your OMDb api key in the file: 'omdb_user_key.txt'

## Web - development
```
FLASK_APP=webapp.api FLASK_DEBUG=1 flask run --port 5000
```

# TODO:
* Tests ! expand what we already have
* Make a POC with the API
* make the WIKI extractor better
* Download more movies
* maybe use a db for the raw data
* clean the raw data jsons - add this as a method to the extractors
* get all the actors ?
