import sqlite3
import os
import csv
import auth
import configparser
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import datetime
import hashlib

# load config file
config = configparser.ConfigParser()
config.read('config.ini')
# get the path of the folder to be backed up
folder_path = config['FOLDER']['LOCAL_FOLDER_PATH']
drive_folder_id = config['FOLDER']['DRIVE_FOLDER_ID']

# Authenticate with Google Drive


def connect_to_drive():
    drive = build('drive', 'v3', credentials=auth.Auth().gauth.credentials)
    return drive


drive = connect_to_drive()


def create_files_table(conn):
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS files
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                abs_path TEXT UNIQUE,
                rel_path TEXT UNIQUE,
                created_time TEXT,
                updated_time TEXT,
                size INTEGER,
                file_id TEXT,
                is_uploaded INTEGER DEFAULT 0)''')

    conn.commit()


def list_files():
    conn = sqlite3.connect('folders.db')
    create_files_table(conn)
    files = []
    for root, dirs, files_list in os.walk(folder_path):
        for file in files_list:
            # abs_path, title, rel_path, size, created_time, update_time
            file_info = (os.path.join(root, file), file, os.path.relpath(os.path.join(root, file), folder_path), os.path.getsize(
                os.path.join(root, file)), os.path.getctime(os.path.join(root, file)), os.path.getmtime(os.path.join(root, file)))
            files.append(file_info)

    c = conn.cursor()
    c.executemany(
        "INSERT OR IGNORE INTO files (abs_path, title, rel_path, size, created_time, updated_time) VALUES (?, ?, ?, ?, ?, ?)", files)
    conn.commit()
    conn.close()


def delete_files_table(conn):
    conn = sqlite3.connect(conn)
    c = conn.cursor()
    c.execute('''DROP TABLE files''')
    conn.commit()


# Get files parent folder g_drive_id from the database folders.db
def get_parent_folder_id(conn, abs_path):
    conn = sqlite3.connect(conn)
    c = conn.cursor()
    parent_folder_path = os.path.dirname(abs_path)
    print(parent_folder_path)
    c.execute(
        "SELECT g_drive_id FROM folders WHERE abs_path = ?", (parent_folder_path,))

    result = c.fetchone()
    if result is None:
        print("result is None")
        parent_folder_id = drive_folder_id
    else:
        print("result", result)
        parent_folder_id = result[0]
    conn.close()
    return parent_folder_id


def upload_files():
    conn = sqlite3.connect('folders.db')
    c = conn.cursor()
    c.execute(
        "SELECT * FROM files WHERE is_uploaded = 0")

    # Get all files that are not uploaded and update_time is less than 1 day
    """
    one_day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
    c.execute(
        "SELECT * FROM files WHERE is_uploaded = 0 AND updated_time > ?", (one_day_ago,))
    files = c.fetchall()
    """
    files = c.fetchall()
    for file in files:
        parent_folder_id = get_parent_folder_id('folders.db', file[2])
        print("parent_folder_id", parent_folder_id)
        # Upload the file
        file_metadata = {
            'name': file[1],
            'parents': [parent_folder_id]
        }
        media = MediaFileUpload(file[2], resumable=True)
        uploaded_file = drive.files().create(
            body=file_metadata, media_body=media, fields='id').execute()
        print('File ID: %s' % uploaded_file.get('id'))
        # Update the database
        c.execute("UPDATE files SET is_uploaded = 1, file_id = ? WHERE id = ?",
                  (uploaded_file.get('id'), file[0]))
        conn.commit()

    conn.close()


# Export the database to a csv file
def export_to_csv():
    conn = sqlite3.connect('folders.db')
    c = conn.cursor()
    c.execute("SELECT * FROM files")
    files = c.fetchall()
    with open('logs\\files.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        # Write the header row
        writer.writerow([description[0] for description in c.description])
        # Write the data rows
        writer.writerows(files)
    conn.close()

# Create table from csv file


def import_table_from_csv(conn, csv_file):
    conn = sqlite3.connect(conn)
    c = conn.cursor()
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        # Get the header row
        header = next(reader)
        # Check if the table already exists if not create it
        c.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='test'")
        table_exists = c.fetchone() is not None
        if not table_exists:
            c.execute('''CREATE TABLE test
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT,
                        abs_path TEXT UNIQUE,
                        rel_path TEXT UNIQUE,
                        created_time TEXT,
                        updated_time TEXT,
                        size INTEGER,
                        file_id TEXT,
                        is_uploaded INTEGER DEFAULT 0)''')
        c.executemany("INSERT OR IGNORE INTO test VALUES (?,?,?,?,?,?,?,?,?)",
                      reader)
        conn.commit()

# Check the integrity of the local folder and the Google Drive folder to make sure they are in sync


def check_integrity():
    local_folder_md5 = get_md5(folder_path)
    print(local_folder_md5)

    # Get the md5 checksum of the Google Drive folder
    query = "trashed = false and parents = '{0}' and mimeType != 'application/vnd.google-apps.folder'".format(
        drive_folder_id)
    files = drive.files().list(q=query, fields='files(md5Checksum)').execute()
    g_drive_folder_md5 = hashlib.md5()
    for file in files.get('files', []):
        g_drive_folder_md5.update(file.get('md5Checksum').encode('utf-8'))
    g_drive_folder_md5 = g_drive_folder_md5.hexdigest()
    print(g_drive_folder_md5)

    if local_folder_md5 == g_drive_folder_md5:
        print('Integrity check passed :)')
    else:
        print('Integrity check failed :(')


def get_md5(path):
    md5 = hashlib.md5()
    for root, dirs, files in os.walk(path):
        for file in files:
            with open(os.path.join(root, file), 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5.update(chunk)
    return md5.hexdigest()


# check_integrity()
if __name__ == "__main__":
    list_files()
    upload_files()
    # export_to_csv()
    # import_table_from_csv('folders.db', 'logs\\files.csv')
    # delete_files_table('folders.db')
