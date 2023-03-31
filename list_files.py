import glob
import os
import sqlite3
# use glop to list all files and update local_path query with title
# https://stackoverflow.com/questions/2186525/use-a-glob-to-find-files-recursively-in-python

# conn:<The returned Connection object con represents the connection to the on-disk database.>, drive:<pydrive>


def list_file_recursively(conn, drive):
    # In order to execute SQL statements and fetch results from SQL queries, we will need to use a database cursor. Call con.cursor() to create the Cursor:
    c = conn.cursor()
    file_name = "test.pdf"
    ext = file_name.split('.')[1].lower()
    for f in glob.glob('C:\\Users\\admin\\Desktop\\**\\*.{}', recursive=True).format(ext):
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
