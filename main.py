import configparser
import folder_structure as fs
import upload_files as uf


# Config file
config = configparser.ConfigParser()
config.read('config.ini')
isRunning = config['RUN']['IS_RUNNING']


def main():
    # Create a folder structure in Google Drive
    fs.insert_folders_with_paths_recursively_to_db(
        fs.folder_path, 'folders.db')
    fs.create_folder_structure_in_gdrive('folders.db', fs.drive_folder_id)

    # List all files in the folder structure
    uf.list_files()
    # Upload files to Google Drive
    uf.upload_files()
    # Export the database to a csv file
    uf.export_to_csv()


if __name__ == "__main__":
    # If an error occurs, make sure to set isRunning to 1 in config.ini
    try:
        main()
    except Exception as e:
        print(e)
        config['RUN']['IS_RUNNING'] = '1'
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
    else:
        config['RUN']['IS_RUNNING'] = '0'
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
