

set -x
set -e

# Determine the directory where this script resides
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# Assume the project root directory is one level up from the script's directory
ROOT_DIR=$(dirname "$SCRIPT_DIR")

install_prereqs(){
    echo "--- Changing to root directory ($ROOT_DIR) to install prerequisites ---"
    # Execute poetry install within a subshell, changing directory first
    (cd "$ROOT_DIR" && poetry install)
    echo "--- Prerequisites installation finished ---"
}

populate_bq_data(){
    echo "--- Changing to root directory ($ROOT_DIR) to populate BigQuery data ---"
    # Execute the python script from the root directory within a subshell
    (cd "$ROOT_DIR" && python -m deployment.bq_populate_data)
    echo "--- BigQuery population finished ---"
}

main(){
    install_prereqs
    populate_bq_data
}

main

exit 0
