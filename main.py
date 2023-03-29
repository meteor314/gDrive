# libraries
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import hashlib
import os

# Google Drive Authentication
gauth = GoogleAuth()
# try to load saved client credentials :https://stackoverflow.com/questions/24419188/automating-pydrive-verification-process/24542604#24542604
gauth.LoadCredentialsFile("token.json")
# gauth.LocalWebserverAuth("token.json")
if gauth.credentials is None:
    print('No credentials found')
    gauth.LocalWebserverAuth(port_numbers=[8080, 8090])
elif gauth.access_token_expired:
    print('Credentials have expired')
    gauth.Refresh()
else:
    gauth.Authorize()
drive = GoogleDrive(gauth)

#  save credentials
gauth.SaveCredentialsFile("token.json")

#  md5 hash function


def md5checksum(file_path):
    if not os.path.isfile(file_path):
        return None
    with open(file_path, 'rb') as f:
        md5 = hashlib.md5()
        while True:
            data = f.read(8192)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()

#  upload file to Google Drive


def upload_folder_to_drive(local_folder_path, drive_folder_id):
    # Find the folder in Google Drive with the same name as the local folder
    query = "trashed=false and mimeType='application/vnd.google-apps.folder' and title='{}'".format(
        os.path.basename(local_folder_path))
    folder_list = drive.ListFile({'q': query}).GetList()

    if len(folder_list) > 0:
        # If the folder already exists in Google Drive, use the first result
        drive_folder = folder_list[0]
    else:
        # If the folder does not exist, create it
        folder_metadata = {'title': os.path.basename(
            local_folder_path), 'mimeType': 'application/vnd.google-apps.folder', 'parents': [{'id': drive_folder_id}]}
        drive_folder = drive.CreateFile(folder_metadata)
        drive_folder.Upload()

    # Upload files to the existing or newly created folder
    for file_name in os.listdir(local_folder_path):
        file_path = os.path.join(local_folder_path, file_name)
        if os.path.isfile(file_path):
            # Check if the file already exists in the folder
            query = "trashed=false and mimeType!='application/vnd.google-apps.folder' and title='{}' and parents in '{}'".format(
                file_name, drive_folder['id'])
            file_list = drive.ListFile({'q': query}).GetList()
            file_exists = any(md5 == md5checksum(file_path)
                              for md5 in (f['md5Checksum'] for f in file_list))

            if not file_exists:
                # If the file does not exist, upload it to the folder
                file_metadata = {'title': file_name,
                                 'parents': [{'id': drive_folder['id']}]}

                drive_file = drive.CreateFile(file_metadata)
                drive_file.SetContentFile(file_path)
                drive_file.Upload()
                print("File '{}' has been uploaded to Google Drive.".format(file_name))

        elif os.path.isdir(file_path):
            # Recursively upload subfolders and their contents
            subfolder_id = create_or_get_folder(
                drive, file_name, drive_folder['id'])
            upload_folder_to_drive(file_path, subfolder_id)


def create_or_get_folder(drive, folder_name, parent_folder_id):
    # Check if the folder already exists
    query = "trashed=false and mimeType='application/vnd.google-apps.folder' and title='{}' and parents in '{}'".format(
        folder_name, parent_folder_id)
    folder_list = drive.ListFile({'q': query}).GetList()

    if len(folder_list) > 0:
        # If the folder already exists in Google Drive, use the first result
        drive_folder = folder_list[0]
    else:
        # If the folder does not exist, create it
        folder_metadata = {'title': folder_name,
                           'mimeType': 'application/vnd.google-apps.folder', 'parents': [{'id': parent_folder_id}]}
        drive_folder = drive.CreateFile(folder_metadata)
        drive_folder.Upload()

    return drive_folder['id']


__local_folder_path__ = r'<Path of  your  folder>'
__drive_folder_id__ = '<ID of the folder in Google Drive>'

upload_folder_to_drive(__local_folder_path__, __drive_folder_id__)
