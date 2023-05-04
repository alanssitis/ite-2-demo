#!/bin/bash

# Install demo dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install monkey-patched in-toto
git submodule update --init
cd in-toto-layout-generator
pip install .
cd ..

echo "\nMake sure to run 'source venv/bin/activate' before starting the demo!"
