#!/bin/sh
echo "Removing temp files..."
rm -rf /kb/module/work/tmp/* || true
echo "...done removing temp files."

current_dir=$(dirname "$(readlink -f "$0")")
export KB_DEPLOYMENT_CONFIG="$current_dir"/deploy.cfg
export KB_AUTH_TOKEN=`cat /kb/module/work/token`
export PYTHONPATH="$current_dir"/../lib:"$current_dir"/../test:"$PYTHONPATH"

cd "$current_dir"/../test

# collect coverage data
pytest \
    --cov=lib/SetAPI \
    --cov-config=.coveragerc \
    --cov-report=html \
    --cov-report=xml \
    -vv \
    .
