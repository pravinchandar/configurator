#!/bin/bash

set -e

# clean slate
rm -rf /tmp/configurator.pytest

# Install packages relevant for unit testing
apt-get install python-virtualenv -y
apt-get install python-pip -y

# setup virutalenv
virtualenv /tmp/configurator.pytest
source /tmp/configurator.pytest/bin/activate

cp -pr . /tmp/configurator.pytest/
export PYTHONPATH=/tmp/configurator.pytest/src/

pip install -U pytest
pip install -U mock
pip install -U pytest-mock

cd /tmp/configurator.pytest/test
pytest .
