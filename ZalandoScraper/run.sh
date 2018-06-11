#!/usr/bin/env bash

trap 'exit' ERR
ROOT_DIR=$(pwd)

# Activate clean virtualenv.

VENV=venv-zalando
if [ ! -d $VENV ]; then
virtualenv $VENV
fi
if [ -f $VENV/bin/activate ]; then
. $VENV/bin/activate
else
# On Windows, not bin for some reason.
. $VENV/Scripts/activate
fi

# Install python packages in virtualenv
pip install -r requirements.txt

# Run the python program
cd $ROOT_DIR

#<write the python command to execute>

python zalandoScraper_v3_download_all.py
