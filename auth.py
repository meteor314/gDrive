from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
# Authenticate with Google Drive API :  https://stackoverflow.com/questions/24419188/automating-pydrive-verification-process/24542604#24542604
# For service account : https://stackoverflow.com/questions/60736955/how-to-connect-pydrive-with-an-service-account


class Auth:
    def __init__(self):
        self.gauth = GoogleAuth()
        if os.path.exists('token.json') is False:
            with open('token.json', 'w') as f:
                f.write('')
                print('token.json created')
        self.gauth.LoadCredentialsFile("token.json")
        if self.gauth.credentials is None:
            # Authenticate if they're not there
            print('No credentials found, please authenticate')
            self.gauth.LocalWebserverAuth(
                port_numbers=[8080, 8090])
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

    def refresh_token(self):
        self.gauth.LoadCredentialsFile("token.json")
        try:
            self.gauth.Refresh()
        except Exception as e:
            print("Refresh token has been revoked. Please re-authenticate.", e)
            self.gauth.LocalWebserverAuth(port_numbers=[8080, 8090])
        self.gauth.SaveCredentialsFile("token.json")
        self.drive = GoogleDrive(self.gauth)
