# #!/bin/bash
# script_dir=$(dirname "$(readlink -f "$0")")
# export KB_DEPLOYMENT_CONFIG=$script_dir/../deploy.cfg
# export KB_AUTH_TOKEN=`cat /kb/module/work/token`
# export PYTHONPATH=$script_dir/../lib:$PATH:$PYTHONPATH
# cd $script_dir/../test
# python -m nose --with-coverage --cover-package=SetAPI --cover-html --cover-html-dir=/kb/module/work/test_coverage --nocapture  --nologcapture .


#!/bin/sh
echo "Removing temp files..."
rm -rf /kb/module/work/tmp/* || true
echo "...done removing temp files."

current_dir=$(dirname "$(readlink -f "$0")")
export KB_DEPLOYMENT_CONFIG="$current_dir"/deploy.cfg
export KB_AUTH_TOKEN=`cat /kb/module/work/token`
# export PYTHONPATH=$current_dir/../lib:$PATH:$PYTHONPATH
export PYTHONPATH="$current_dir"/../lib:"$current_dir"/../test:"$PYTHONPATH"

cd "$current_dir"/../test

# python -m nose --with-coverage --cover-package=SetAPI --cover-html --cover-html-dir=/kb/module/work/test_coverage .

# cd ..
# run without collecting coverage data
# python -m unittest discover -p "*_test.py"

# collect coverage data
pytest \
    --cov=lib/SetAPI \
    --cov-config=.coveragerc \
    --cov-report=html \
    --cov-report=xml \
    -vv \
    .
#    test/AssemblySet_basic_test.py
