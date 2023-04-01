# Libraries
import os
import glob
import datetime
import sqlite3


#  List all files in a directory and subdirectories recursively and and create a db with title, local_path, is_uploaded, updated_date, size of file
def list_files(folder_path):
    # Connect to SQLite database
    conn = sqlite3.connect('uploaded_files.db')
    c = conn.cursor()

    # Create table if not exists
    c.execute(
        "CREATE TABLE IF NOT EXISTS uploaded_files (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, local_path TEXT, is_uploaded INTEGER DEFAULT 0, updated_date TEXT, size INTEGER)")

    # Recursively get all file paths in the folder and its subfolders
    file_paths = glob.glob(os.path.join(folder_path, '**'), recursive=True)
    file_paths = [f for f in file_paths if os.path.isfile(f)]

    # Upload files in batches
    for i in range(0, len(file_paths)):
        file_path = file_paths[i]
        # Get the file title relative to the folder path
        title = os.path.relpath(file_path, folder_path)
        local_path = file_path
        size = 0  # os.path.getsize(file_path)
        updated_date = datetime.datetime.fromtimestamp(
            os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')

        # Check if the file has already been uploaded
        c.execute("SELECT id FROM uploaded_files WHERE title=?", (title,))
        result = c.fetchone()

        if result is None:
            # Upload the file to Google Drive
            try:
                c.execute("INSERT INTO uploaded_files (title, local_path, updated_date, size) VALUES (?, ?, ?, ?)",
                          (title, local_path, updated_date, size))
                conn.commit()
            except Exception as e:
                print(e)
        else:
            c.execute(
                "SELECT updated_date FROM uploaded_files WHERE title=?", (title,))
            result = c.fetchone()
            if result[0] != updated_date:
                c.execute(
                    "UPDATE uploaded_files SET updated_date = ? WHERE title = ?", (updated_date, title))
                conn.commit()
            else:
                print("File is up to date")

    conn.close()
