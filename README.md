# FindMeMoreLike
=============

[![Build Status](https://travis-ci.org/arielszabo/FindMeMoreLike.png)](https://travis-ci.org/arielszabo/FindMeMoreLike)



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
* make the WIKI extractor better
* Download more movies

* clean the raw data jsons - add this as a method to the extractors
* get all the actors ?


* after Flask restart User must login again


## Deployment hints

As user ariel:

```
git clone https://github.com/arielszabo/FindMeMoreLike.git
cd FindMeMoreLike
mkdir db
chmod a+w db

ln -s /home/ariel/findmemorelike/config/nginx.conf /etc/nginx/sites-enabled/find-me-more-like.conf
ln -s /home/ariel/findmemorelike/config/uwsgi.ini /etc/uwsgi/apps-enabled/find-me-more-like.ini

mkdir ~/letsencrypt
```

As root:

```
certbot certonly --webroot -w /home/ariel/letsencrypt/ -d find-alike.szabgab.com
certbot renew
```
Your cert will expire on 2020-05-15.



### restart your webapp
`sudo systemctl restart uwsgi`

## logs are at:
`sudo less /var/log/uwsgi/app/find-me-more-like.log`