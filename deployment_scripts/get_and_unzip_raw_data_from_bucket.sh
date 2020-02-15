#!/bin/bash

embedding_file=enwiki_dbow

#gsutil -m cp "gs://ariel-szabo/find-me-more-like/${embedding_file}.tar.gz" .
#gunzip "${embedding_file}.tar.gz"
#tar -xf "${embedding_file}.tar"

zip_folder=raw_data_zip_files


get_and_unzip () {
    gsutil -m cp -r "gs://ariel-szabo/find-me-more-like/$zip_folder/${1}"_zip .
    mkdir $1
    for zipped_file in "$zip_folder/${1}"_zip/*
    do
        zipped_file_with_tar_suffix="${zipped_file%.*}"
        gunzip "$zipped_file_with_tar_suffix.gz"
        tar -xf "$zipped_file_with_tar_suffix" -C "${1}/"
    done

}

# unzip
get_and_unzip raw_imdb_data
get_and_unzip raw_wiki_data
get_and_unzip similar_list_data_zip