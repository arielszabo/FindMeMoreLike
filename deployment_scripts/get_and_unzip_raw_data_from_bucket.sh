#!/bin/bash

embedding_file=enwiki_dbow

#gsutil -m cp "gs://ariel-szabo/find-me-more-like/${embedding_file}.tar.gz" .
#gunzip "${embedding_file}.tar.gz"
#tar -xf "${embedding_file}.tar"


get_and_unzip () {
    mkdir $1
    zip_folder="${1}"_zip
    gsutil -m cp -r gs://ariel-szabo/find-me-more-like/raw_data_zip_files/${zip_folder} .
    for zipped_file in ${zip_folder}/*
    do
        zipped_file_with_tar_suffix="${zipped_file%.*}"
        gunzip "$zipped_file_with_tar_suffix.gz"
        tar -xf "$zipped_file_with_tar_suffix" -C "${1}/"
    done
    rm -r ${zip_folder}
}

# unzip
#get_and_unzip raw_imdb_data
#get_and_unzip raw_wiki_data
get_and_unzip similar_list_data