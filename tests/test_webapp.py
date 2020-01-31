import os
import sys
import yaml
import pytest

root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, root)
os.environ["FIND_MORE_LIKE_CONFIG"] = os.path.join(root, 'tests', 'testing_config.yaml')

class TestWeb(object):
    def setup_class(self):
        # create_config_files()
        import webapp.api
        self.app = webapp.api.app.test_client()

    def test_main(self):
        rv = self.app.get('/')
        assert rv.status == '200 OK'
        #print(rv.data)
        assert b'<title>FindMeMoreLike_HomePage</title>' in rv.data

    def test_login(self):
        rv = self.app.get('/login')
        assert rv.status == '302 FOUND'
        print(rv.data)
        print(rv.headers)
        assert rv.headers['Location'] == 'https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=blabla&redirect_uri=http%3A%2F%2Flocalhost%2Flogin%2Fcallback&scope=openid+email+profile'
        #assert b'<title>FindMeMoreLike_HomePage</title>' in rv.data

    def test_search(self):
        rv = self.app.get('/search')
        assert rv.status == '302 FOUND'
        print(rv.data)
        print(rv.headers)
        assert rv.headers['Location'] == 'http://localhost/search/None/None/0'
        # TODO are those None-s correct in the redirection?


    @pytest.mark.xfail(reason = "The site should be able to handle incorrect or missing data")
    def test_save_seen_checkbox_missing_status(self):
        rv = self.app.post('/save_seen_checkbox', data = {
            "id": "some_value",
        })
        assert rv.status == '200 OK' # TODO what should be really expected here?
        print(rv.headers)
        print(rv.data)

    def test_save_seen_checkbox(self):
        rv = self.app.post('/save_seen_checkbox', data = {
            "id": "some_value",
            "status": "OK"
        })
        assert rv.status == '200 OK'
        assert rv.headers['Content-Type'] == 'application/json'
        #print(rv.headers)
        assert rv.json == { "ok": 1}



