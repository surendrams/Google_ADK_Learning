

set -x

prepare(){
    touch __init__.py
    export PYTHONPATH=:.
}

remove_selenium(){
    rm -rf selenium
}

run_eval(){
    adk eval \
        brand_search_optimization \
        eval/data/eval_data1.evalset.json \
        --config_file_path eval/data/test_config.json
}

main(){
    echo "
    You must be inside brand-search-optimization dir and then
    # sh deployment/eval/eval.sh
    "
    prepare
    remove_selenium
    run_eval
}

main

exit 0
