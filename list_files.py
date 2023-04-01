import os
import datetime
import sqlite3


# List all files in a directory and subdirectories recursively and create a database with title, local_path, is_uploaded, updated_date, size of file
def list_files(folder_path):
    # Connect to SQLite database
    with sqlite3.connect('uploaded_files.db') as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS uploaded_files (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, local_path TEXT, is_uploaded INTEGER DEFAULT 0, updated_date TEXT, size INTEGER)")

        # Recursively get all file paths in the folder and its subfolders
        file_paths = [os.path.join(dirpath, filename) for dirpath, _, filenames in os.walk(
            folder_path) for filename in filenames]

        # Upload files in batches
        file_data = []
        for file_path in file_paths:
            # Get the file title relative to the folder path
            title = os.path.relpath(file_path, folder_path)
            file_info = {
                'title': title,
                'local_path': file_path,
                'size': os.path.getsize(file_path),
                'updated_date': datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
            }

            # Add file data to list
            file_data.append(file_info)

        # Insert or update file data in database
        with conn:
            conn.executemany(
                "INSERT OR REPLACE INTO uploaded_files (title, local_path, size, updated_date) VALUES (:title, :local_path, :size, :updated_date)", file_data)
