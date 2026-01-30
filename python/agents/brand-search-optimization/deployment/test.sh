# Copyright 2025 Google LLC


set -x

run_unit_tests(){
    # Make sure you are inside brand-search-optimization directory
    # And ENABLE_UNIT_TEST_MODE=1 in .env
    export PYTHONPATH="$PYTHONPATH:."
    pytest tests/
}

run_unit_tests

exit 0