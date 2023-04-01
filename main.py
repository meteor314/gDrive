# Libraries
import sqlite3
import os
import auth
import auth as a
from list_files import list_files
import googleapiclient
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
import datetime


token_expiry = None

# Authenticate with Google Drive API
auth = a.Auth()
token_expiry = auth.gauth.credentials.token_expiry

# Start time
start_time = datetime.datetime.now()

# Define the folder path
folder_path = "C:\\Users\\admin\\Desktop\\test"
list_files(folder_path)


# load the client secrets file
client_secrets_file = os.path.join(
    os.path.dirname(__file__), 'client_secrets.json')


creds_file = os.path.join(os.path.dirname(__file__), 'token.json')


def upload_files_to_drive(folder_path, folder_id, batch_size=10):
    print('Uploading files to Google Drive...')
    creds = Credentials.from_authorized_user_file(
        creds_file, scopes=['https://www.googleapis.com/auth/drive'])

    # Create the Drive API client
    service = build('drive', 'v3', credentials=creds)

    # Connect to SQLite database
    conn = sqlite3.connect('uploaded_files.db')
    c = conn.cursor()

    # Select all files from the database where is_uploaded is 0
    file_paths = c.execute(
        "SELECT local_path FROM uploaded_files WHERE is_uploaded=0").fetchall()

    file_paths = [f[0] for f in file_paths]

    # Upload files in batches
    for i in range(0, len(file_paths), batch_size):

        # Refresh the token if it has expired
        if creds.expired:
            auth.gauth.Refresh()
            creds = Credentials.from_authorized_user_file(
                creds_file, scopes=['https://www.googleapis.com/auth/drive'])
            service = build('drive', 'v3', credentials=creds)

        for j in range(i, i + batch_size):
            if j >= len(file_paths):
                break

            file_path = file_paths[j]
            # Get the file title relative to the folder path
            title = os.path.relpath(file_path, folder_path)

            # Create the file metadata
            metadata = {
                'name': title,
                'parents': [folder_id]
            }

            # Upload the file
            media = googleapiclient.http.MediaFileUpload(file_path)
            service.files().create(
                body=metadata, media_body=media, fields='id').execute()

            # Update the database
            c.execute(
                "UPDATE uploaded_files SET is_uploaded=1 WHERE local_path=?", (file_path,))
            conn.commit()

    conn.close()
    print('Done')


if __name__ == '__main__':
    local_path = "C:\\Users\\admin\\Desktop\\test"  # Replace with your local path
    folder_id = "14pwrQ42PpsqUbsBT0deJrTDsZaFk3VT8"  # Replace with your folder ID
    upload_files_to_drive(local_path, folder_id)
