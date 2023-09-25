# Delete MONA distribution if it exists
folder_to_delete1="./mona/dist"
folder_to_delete2="./mona/mona.egg-info"

# Function to delete a folder if it exists
delete_folder() {
    if [ -d "$1" ]; then
        rm -r "$1"
        echo "Folder '$1' has been deleted."
    else
        echo "Folder '$1' does not exist."
    fi
}

# Call the function to delete the first folder
delete_folder "$folder_to_delete1"
delete_folder "$folder_to_delete2"

# Build MONA interpreter
cd mona
python -m build
cd ..
pip install mona/dist/mona-0.0.1.tar.gz
