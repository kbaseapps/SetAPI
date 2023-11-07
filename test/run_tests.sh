#!/bin/sh
echo "Removing temp files..."
rm -rf /kb/module/work/tmp/* || true
echo "...done removing temp files."

current_dir=$(dirname "$(readlink -f "$0")")
base_dir=$(dirname "$current_dir")
export KB_DEPLOYMENT_CONFIG="$base_dir"/deploy.cfg
export KB_AUTH_TOKEN=$(cat /kb/module/work/token)
export PYTHONPATH="$base_dir"/lib:"$base_dir"/test:"$PYTHONPATH"

echo "Using deployment config $KB_DEPLOYMENT_CONFIG"

cd "$base_dir"

# collect coverage data
pytest \
    --cov=lib/SetAPI \
    --cov-config=.coveragerc \
    --cov-report=html \
    --cov-report=xml \
    -vv \
    test/AssemblySet_basic_test.py test/DifferentialExpressionMatrixSet_basic_test.py test/ReadsAlignmentSet_basic_test.py test/ReadsSet_basic_test.py test/SampleSet_basic_test.py test/SampleSetSearch_test.py test/ExpressionSet_basic_test.py test/FeatureSetSet_test.py test/GenomeSet_basic_test.py