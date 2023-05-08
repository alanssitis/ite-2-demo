#!/bin/bash

# Check if rstuf cli connected to rstuf instance (check if user set up rstuf)
if ! rstuf admin login; then
    echo "rstuf CLI not connected to RSTUF instance"
    exit 1
fi

# Install demo dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Add environment variables
echo "export ADD_TARGET_TOKEN=$( \
    rstuf admin token generate -s write:targets \
    | jq '.access_token' \
    | tr -d '"')" >> venv/bin/activate
echo "export DEL_TARGET_TOKEN=$( \
    rstuf admin token generate -s delete:targets \
    | jq '.access_token' \
    | tr -d '"')" >> venv/bin/activate

# Install in-toto-layout-generator
git submodule update --init
cd in-toto-layout-generator
pip install .
cd ..

echo "Make sure to run 'source venv/bin/activate' before starting the demo!"
