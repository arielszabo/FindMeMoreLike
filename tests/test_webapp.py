import os
import sys
import yaml

root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, root)

class TestWeb(object):
    def setup_class(self):
        create_config_files()
        import webapp.api
        self.app = webapp.api.app.test_client()

    def test_main(self):
        rv = self.app.get('/')
        assert rv.status == '200 OK'
        #print(rv.data)
        assert b'<title>FindMeMoreLike_HomePage</title>' in rv.data

def create_config_files():
    keys_config_file = os.path.join(root, 'keys_config.yaml')
    if not os.path.exists(keys_config_file):
        keys_config = {
            'google_client_id': 'blabla',
            'google_client_secret': 'secret blabla',
        }
        with open(keys_config_file, 'w') as outfile:
            yaml.dump(keys_config, outfile, default_flow_style=False)



