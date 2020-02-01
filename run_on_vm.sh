#!/bin/bash

zip_folder_containing_folders_and_save () {
    mkdir ${1}_zip
    cd $1
    for i in */; do tar -zcvf "../${1}_zip/${i%/}.tar.gz" "$i"; done
    cd ..

    # save results in bucket
    gsutil -m cp -r "${1}_zip" gs://ariel-szabo/find-me-more-like/$zip_folder/
}

#embedding_file=enwiki_dbow
#
#gsutil -m cp "gs://ariel-szabo/find-me-more-like/${embedding_file}.tar.gz" .
#gunzip "${embedding_file}.tar.gz"
#tar -xf "${embedding_file}.tar"

zip_folder=raw_data_zip_files

## get raw data from bucket
#gsutil -m cp -r gs://ariel-szabo/find-me-more-like/$zip_folder .


## unzip
#for folder_name in raw_imdb_data raw_wiki_data
#do
#    mkdir $folder_name
#    for zipped_file in "$zip_folder/$folder_name"_zip/*
#    do
#        zipped_file_with_tar_suffix="${zipped_file%.*}"
#        gunzip "$zipped_file_with_tar_suffix.gz"
#        tar -xf "$zipped_file_with_tar_suffix" -C "$folder_name/"
#    done
#done

#raw_imdb_data_folder_size=$(du -s raw_imdb_data)
#raw_wiki_data_folder_size=$(du -s raw_wiki_data)


# activate venv
source ~/venv3/bin/activate


pip install -r requirements.txt

# run python code
python main_algorithm_run.py
# > find_me_more_like_logs/stdout.txt 2> find_me_more_like_logs/stderror.txt


# save logs in bucket
gsutil -m cp -r find_me_more_like_logs gs://ariel-szabo/find-me-more-like/



zip_folder_containing_folders_and_save similar_list_data
#zip_folder_containing_folders_and_save raw_imdb_data
#zip_folder_containing_folders_and_save raw_wiki_data



# stop instance
VM_NAME=instance-2
gcloud compute instances stop $VM_NAME -q
