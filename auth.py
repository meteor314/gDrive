from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
# Authenticate with Google Drive API :  https://stackoverflow.com/questions/24419188/automating-pydrive-verification-process/24542604#24542604


class Auth:
    def __init__(self):
        self.gauth = GoogleAuth()
        if os.path.exists('token.json') is False:
            with open('token.json', 'w') as f:
                f.write('')
        self.gauth.LoadCredentialsFile("token.json")
        if self.gauth.credentials is None:
            # Authenticate if they're not there
            print('No credentials found, please authenticate')
            self.gauth.LocalWebserverAuth(port_numbers=[8080, 8090])
        elif self.gauth.access_token_expired:
            # Refresh them if expired
            print('Credentials have expired, refreshing')
            self.gauth.Refresh()
        else:
            # Initialize the saved creds
            self.gauth.Authorize()
        # Save credentials
        self.gauth.SaveCredentialsFile("token.json")
        self.drive = GoogleDrive(self.gauth)
