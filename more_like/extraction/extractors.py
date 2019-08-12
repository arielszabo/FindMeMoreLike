import os
import re
import json
import glob


class DataExtractor(object):
    def __init__(self, saving_path):
        self.saving_path = saving_path
        self.existing_ids = self._get_existing_ids()

    def _get_existing_ids(self):
        all_saved_files = glob.glob(os.path.join(self.saving_path, '*.json'))
        return list(map(lambda name: re.search(r'tt\d+', name).group(0), all_saved_files))

    def extract_data(self):
        pass  # This method needs to be implemented todo: add an assertion if not with the class name

    def save(self, data, movie_id):
        with open(os.path.join(self.saving_path, '{}.json'.format(movie_id)), 'w') as j_file:
            json.dump(data, j_file)


