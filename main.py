# Libraries
import glob
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import sqlite3
from auth import *

drive = auth('token.json')


# Database Connection
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Create table if not exists
sql_query = "CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY AUTOINCREMENT, file_id TEXT, file_name TEXT, file_path TEXT, file_size TEXT, file_type TEXT, file_date TEXT, is_uploaded TEXT DEFAULT 'false', local_path TEXT DEFAULT 'null')"
c.execute(sql_query)
conn.commit()

# Upload files to Google Drive


def upload_folder_to_drive(local_folder_path, drive_folder_id):
    #  Find the folder in Google Drive with the same name as the local folder
    query = "trashed=false and mimeType='application/vnd.google-apps.folder' and title='{}'".format(
        os.path.basename(local_folder_path))
    folder_list = drive.ListFile({'q': query}).GetList()
    if len(folder_list) > 0:
        drive_folder = folder_list[0]
    else:
        # Folder already exists
        folder_metadata = {'title': os.path.basename(
            local_folder_path), 'mimeType': 'application/vnd.google-apps.folder', 'parents': [{'id': drive_folder_id}]}
        drive_folder = drive.CreateFile(folder_metadata)
        drive_folder.Upload()

    # Upload files to Google Drive
    for file_name in os.listdir(local_folder_path):
        file_path = os.path.join(local_folder_path, file_name)
        if os.path.isfile(file_path):
            # Check if file is_uploaded is true in database
            sql_query = "SELECT * FROM files WHERE file_path = '{}'".format(
                file_path)
            c.execute(sql_query)
            result = c.fetchone()
            if result is None:
                # Upload file to Google Drive
                file_metadata = {'title': file_name,
                                 'parents': [{'id': drive_folder['id']}]}
                file = drive.CreateFile(file_metadata)
                file.SetContentFile(file_path)
                file.Upload()
                # Insert file info to database
                sql_query = "INSERT INTO files (file_id, file_name, file_path, file_size, file_type, file_date) VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(
                    file['id'], file_name, file_path, file['fileSize'], file['mimeType'], file['createdDate'])
                c.execute(sql_query)
                conn.commit()
                print('File {} uploaded to Google Drive in {} folder'.format(
                    file_name, drive_folder['title']))
            else:
                print('File {} already uploaded to Google Drive'.format(file_name))


# Upload folder to Google Drive
upload_folder_to_drive('C:\\Users\\admin\\Desktop\\test',
                       '1LpHr3p00TF9HczZ51g4ASFpu-zOqAjnY')
"""

# use glop to list all files and update local_path query with title
# https://stackoverflow.com/questions/2186525/use-a-glob-to-find-files-recursively-in-python
for f in glob.glob('C:\\Users\\admin\\Desktop\\osu\\**.pdf', recursive=True):
    if os.path.isfile(f):
        # Check if file is_uploaded is true in database
        sql_query = "SELECT * FROM files WHERE file_path = '{}'".format(
            f)
        c.execute(sql_query)
        result = c.fetchone()
        if result is None:
            # Upload file to Google Drive
            file_metadata = {'title': os.path.basename(f),
                             'parents': [{'id': '1gwNCNGlpUf2DyufVAmTCrWRa-vAsltkd'}]}
            file = drive.CreateFile(file_metadata)
            file.SetContentFile(f)
            file.Upload()
            # Insert file info to database
            sql_query = "INSERT INTO files (file_id, file_name, file_path, file_size, file_type, file_date, local_path) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
                file['id'], os.path.basename(f), f, file['fileSize'], file['mimeType'], file['createdDate'], f)
            c.execute(sql_query)
            conn.commit()
            print('File {} uploaded to Google Drive in {} folder'.format(
                os.path.basename(f), 'osu'))
        else:
            print('File {} already uploaded to Google Drive'.format(
                os.path.basename(f)))
"""
