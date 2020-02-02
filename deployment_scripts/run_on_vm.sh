#!/bin/bash

# activate venv
source ~/venv3/bin/activate

pip install -r requirements.txt

logging_file=find_me_more_like_logs/main_algorithm_run.log

rm $logging_file
# run python code
python main_algorithm_run.py
# >> $logging_file 2>> $logging_file


# stop instance
VM_NAME=instance-2
gcloud compute instances stop $VM_NAME --zone us-east1-b -q
