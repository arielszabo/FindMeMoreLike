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
    for zipped_file in "$zip_folder/$folder_name/"*
    do
        zipped_file_with_tar_suffix="${zipped_file%.*}"
        gunzip "$zipped_file_with_tar_suffix.gz"
        tar -xf "$zipped_file_with_tar_suffix" -C "$folder_name/"
    done
done


# activate venv
source ~/venv3/bin/activate


pip install -r requirements.txt

## run python code
#python main_algorithm_run.py
## > find_me_more_like_logs/stdout.txt 2> find_me_more_like_logs/stderror.txt
#
#
## save logs in bucket
#gsutil -m cp -r find_me_more_like_logs gs://ariel-szabo/find-me-more-like/
#
#
#
#for folder_name in raw_imdb_data raw_wiki_data similar_list_data
#do
#    mkdir ${folder_name}_zip
#    cd $folder_name
#    for i in */; do tar -zcvf "../${folder_name}_zip/${i%/}.tar.gz" "$i"; done
#    cd ..
#
#    # save results in bucket
#    gsutil -m cp -r "${folder_name}_zip" gs://ariel-szabo/find-me-more-like/$zip_folder/
#done
#


# stop instance
VM_NAME=main-algo-instance
gcloud compute instances stop $VM_NAME --zone us-central1-a -q
