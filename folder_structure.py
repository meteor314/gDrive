import os
import sqlite3
import auth
import configparser
import googleapiclient
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import re


# load config file
config = configparser.ConfigParser()
config.read('config.ini')

# get the path of the folder to be backed up
folder_path = config['FOLDER']['LOCAL_FOLDER_PATH']
drive_folder_id = config['FOLDER']['DRIVE_FOLDER_ID']
is_share_drive = config['FOLDER']['IS_SHARE_DRIVE']


def connect_to_drive():
    drive = build('drive', 'v3', credentials=auth.Auth().gauth.credentials)
    return drive


drive = connect_to_drive()


def create_folders_table(conn):
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS folders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 abs_path TEXT UNIQUE,
                 rel_path TEXT UNIQUE,
                 g_drive_id TEXT
                    )''')
    conn.commit()


def insert_folder_info(conn, folder_info):
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO folders (abs_path, rel_path, g_drive_id) VALUES (?, ?, NULL)", folder_info)
        conn.commit()
    except sqlite3.IntegrityError:
        # Ignore duplicate values
        pass


def insert_folders_with_paths_recursively_to_db(folder_path, db_file_path):
    conn = sqlite3.connect(db_file_path)
    create_folders_table(conn)
    for root, dirs, files in os.walk(folder_path):
        for folder in dirs:
            folder_info = (os.path.join(root, folder),
                           os.path.relpath(os.path.join(root, folder), folder_path))
            insert_folder_info(conn, folder_info)
    conn.close()


def create_folder_structure_in_gdrive(db_file_path, drive_folder_id):
    conn = sqlite3.connect(db_file_path)
    c = conn.cursor()
    c.execute("SELECT * FROM folders WHERE g_drive_id IS NULL")
    rows = c.fetchall()
    if len(rows) == 0:
        print("All folders are already created in Google Drive")
        return

    creds = Credentials.from_authorized_user_file(
        'token.json', ['https://www.googleapis.com/auth/drive'])
    service = build('drive', 'v3', credentials=creds)

    # by default the root folder id is the drive_folder_id
    folder_ids = {folder_path: drive_folder_id}
    for row in rows:
        folder_name = os.path.basename(row[1])
        parent_folder_path = os.path.dirname(row[1])

        # Find the parent folder id
        try:
            parent_folder_id = folder_ids[parent_folder_path]
        except KeyError:
            # Get the parent folder id from the database
            c.execute(
                "SELECT g_drive_id FROM folders WHERE abs_path = ?", (parent_folder_path,))
            parent_folder_id = c.fetchone()[0]
            folder_ids[parent_folder_path] = parent_folder_id
            # Update the folder id in the database for this folder
            c.execute(
                "UPDATE folders SET g_drive_id = ? WHERE abs_path = ?", (parent_folder_id, row[1]))
            conn.commit()

        # Find the folder in google drive with the same name as local folder
        # escape the single quotes
        folder_name = re.sub(r'[^\w\s]', '', folder_name)
        folder_query = f"mimeType='application/vnd.google-apps.folder' and trashed=false and name='{folder_name}' and '{parent_folder_id}' in parents"
        folder_list = service.files().list(q=folder_query).execute().get('files', [])
        if len(folder_list) > 0:
            # Folder already exists in Google Drive
            drive_folder_id = folder_list[0]['id']

        else:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id]
            }
            if is_share_drive == 'True':
                folder_metadata['driveId'] = drive_folder_id
                folder_metadata['parents'] = [parent_folder_id]

            folder = service.files().create(body=folder_metadata, fields='id, name',
                                            supportsAllDrives=is_share_drive).execute()

            print('Created folder: %s' % folder.get('name'), folder.get('id'))
            drive_folder_id = folder.get('id')
            # Add the folder id to the dictionary
            folder_ids[row[1]] = drive_folder_id
            print(row[1])
        c.execute("UPDATE folders SET g_drive_id = ? WHERE abs_path = ?",
                  (drive_folder_id, row[1]))
        conn.commit()


folder_path
db_file_path = "folders.db"
insert_folders_with_paths_recursively_to_db(folder_path, db_file_path)
create_folder_structure_in_gdrive(db_file_path, drive_folder_id)
