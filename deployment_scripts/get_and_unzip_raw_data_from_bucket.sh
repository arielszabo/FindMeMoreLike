#!/bin/bash

embedding_file=enwiki_dbow

gsutil -m cp "gs://ariel-szabo/find-me-more-like/${embedding_file}.tar.gz" .
gunzip "${embedding_file}.tar.gz"
tar -xf "${embedding_file}.tar"

zip_folder=raw_data_zip_files

# get raw data from bucket
gsutil -m cp -r gs://ariel-szabo/find-me-more-like/$zip_folder .


# unzip
for folder_name in raw_imdb_data raw_wiki_data
do
    mkdir $folder_name
    for zipped_file in "$zip_folder/$folder_name"_zip/*
    do
        zipped_file_with_tar_suffix="${zipped_file%.*}"
        gunzip "$zipped_file_with_tar_suffix.gz"
        tar -xf "$zipped_file_with_tar_suffix" -C "$folder_name/"
    done
done
