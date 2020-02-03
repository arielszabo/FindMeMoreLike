#!/bin/bash


zip_folder_containing_folders_and_save () {
    mkdir ${1}_zip
    cd $1
    for i in */; do tar -zcvf "../${1}_zip/${i%/}.tar.gz" "$i"; done
    cd ..

    # save results in bucket
    gsutil -m cp -r "${1}_zip" gs://ariel-szabo/find-me-more-like/raw_data_zip_files/
}


# save logs in bucket
gsutil -m cp -r find_me_more_like_logs gs://ariel-szabo/find-me-more-like/



zip_folder_containing_folders_and_save similar_list_data
#zip_folder_containing_folders_and_save raw_imdb_data
#zip_folder_containing_folders_and_save raw_wiki_data