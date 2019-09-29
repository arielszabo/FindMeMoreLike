# FindMeMoreLike


* Pre-Trained Doc2Vec model is saved in the 'enwiki_dbow' folder and it is from https://github.com/jhlau/doc2vec
* Google Login methods are from here: https://realpython.com/flask-google-login/

# Need to Know:
- save your OMDb api key in the file: 'keys_config.yaml'
- save your GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET keys in the file: 'keys_config.yaml'

## Web - development
```
FLASK_APP=webapp.api FLASK_DEBUG=1 flask run --port 5000 --cert=adhoc
```

# TODO:
* Tests ! expand what we already have
* Make a POC with the API
* make the WIKI extractor better
* Download more movies
* maybe use a db for the raw data
* clean the raw data jsons - add this as a method to the extractors
* get all the actors ?


* add /google routes
* after Flask restart User must login again