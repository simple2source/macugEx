#!/bin/bash

# 1. update requriements.txt
pip freeze | grep -v pgoapi > requirements.txt

# 2. deploy
eb deploy

