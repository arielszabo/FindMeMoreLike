#!/bin/bash


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

# run python code
python main_algorithm_run.py



zip_folder=similar_list_data_zip

mkdir $zip_folder

cd similar_list_data2/
for i in */; do tar -zcvf "../$zip_folder/${i%/}.tar.gz" "$i"; done
cd ..

# save results in bucket
gsutil -m cp -r $zip_folder gs://ariel-szabo/find-me-more-like/

# save logs in bucket
gsutil -m cp -r find_me_more_like_logs gs://ariel-szabo/find-me-more-like/