#!/usr/bin/env bash

trap 'exit' ERR
ROOT_DIR=$(pwd)

# Activate clean virtualenv.

VENV=venv-insta-web
if [ ! -d $VENV ]; then
virtualenv $VENV
fi
if [ -f $VENV/bin/activate ]; then
. $VENV/bin/activate
else
# On Windows, not bin for some reason.
 $VENV/Scripts/activate
fi

# Install python packages in virtualenv
pip install -r requirement.txt

# Run the python program
cd $ROOT_DIR

#<write the python command to execute>
python instagramScrap.py -u ''DESIRED_INSTAGRAM_USERNAME_TO_CRAWL_DATA''