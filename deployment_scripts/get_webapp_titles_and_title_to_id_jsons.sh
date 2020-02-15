#!/usr/bin/env bash


gsutil -m cp -r gs://ariel-szabo/find-me-more-like/raw_data_zip_files/title_to_id.json webapp/title_to_id.json
gsutil -m cp -r gs://ariel-szabo/find-me-more-like/raw_data_zip_files/only_titles.json webapp/static/only_titles.json