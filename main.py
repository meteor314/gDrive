import sqlite3
import os
import auth
from auth import Auth
from list_files import list_files
import googleapiclient
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
import datetime
import asyncio

# Connect to Google Drive API
auth.Auth()

list_files("C:\\Users\\admin\\Desktop\\test")


async def upload_file(service, folder_id, file_path, max_retries=3):
    # Get the file title relative to the folder path
    title = os.path.basename(file_path)

    # Create the file metadata
    metadata = {
        'name': title,
        'parents': [folder_id]
    }

    # Upload the file
    media = googleapiclient.http.MediaFileUpload(file_path)

    # Try to upload the file with retries
    for i in range(max_retries):
        try:
            service.files().create(
                body=metadata, media_body=media, fields='id').execute()
            return
        except HttpError as error:
            print(f"Error uploading {file_path}: {error}")
            print(f"Retrying ({i+1}/{max_retries})...")
            await asyncio.sleep(1)  # Wait for 1 second before retrying

    print(f"Failed to upload {file_path} after {max_retries} retries.")


async def upload_files_to_drive(folder_path, folder_id, batch_size=10):
    print('Uploading files to Google Drive...')
    creds = Credentials.from_authorized_user_file(
        'token.json', scopes=['https://www.googleapis.com/auth/drive'])

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
            # Refresh the token with auth.py refresh_token()
            print('Token expired')
            auth.Auth().refresh_token()
            creds = Credentials.from_authorized_user_file(
                'token.json', scopes=['https://www.googleapis.com/auth/drive'])
            service = build('drive', 'v3', credentials=creds)

        tasks = []
        for j in range(i, i + batch_size):
            if j >= len(file_paths):
                break

            file_path = file_paths[j]
            tasks.append(upload_file(service, folder_id, file_path))

        await asyncio.gather(*tasks)

        # Update the database
        c.executemany(
            "UPDATE uploaded_files SET is_uploaded=1 WHERE local_path=?", [(file_path,) for file_path in file_paths[i:i+batch_size]])
        conn.commit()

    conn.close()
    print('Done')


if __name__ == '__main__':
    folder_id = "14pwrQ42PpsqUbsBT0deJrTDsZaFk3VT8"  # Replace with your folder ID
    local_path = "C:\\Users\\admin\\Desktop\\test"
    loop = asyncio.get_event_loop()
    loop.run_until_complete(upload_files_to_drive(local_path, folder_id))
