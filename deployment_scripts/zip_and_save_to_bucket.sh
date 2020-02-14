#!/bin/bash

zipping_log_file_path=find_me_more_like_logs/zipping_log_file.txt
rm ${zipping_log_file_path}

zip_folder_containing_folders_and_save () {
    $1 >> zipping_log_file_path
    mkdir ${1}_zip
    cd $1
    for i in */; do tar -zcvf "../${1}_zip/${i%/}.tar.gz" "$i"; done
    cd ..

    # save results in bucket
    gsutil -m cp -r "${1}_zip" gs://ariel-szabo/find-me-more-like/raw_data_zip_files/ >>zipping_log_file_path 2>>zipping_log_file_path
}


zip_folder_containing_folders_and_save similar_list_data
#zip_folder_containing_folders_and_save raw_imdb_data
#zip_folder_containing_folders_and_save raw_wiki_data
zip_folder_containing_folders_and_save vectors_cache


gsutil -m cp -r find_me_more_like_logs gs://ariel-szabo/find-me-more-like/
gsutil -m cp webapp/static/title_and_id_mapping.json gs://ariel-szabo/find-me-more-like/

sleep 60
# stop instance
VM_NAME=instance-2
gcloud compute instances stop $VM_NAME --zone us-east1-b -q