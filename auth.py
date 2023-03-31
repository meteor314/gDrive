from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


def auth(file_path):

    # Google Drive Authentication
    gauth = GoogleAuth()
    # Try to load saved client credentials :  https://stackoverflow.com/questions/24419188/automating-pydrive-verification-process/24542604#24542604
    gauth.LoadCredentialsFile("token.json")
    if gauth.credentials is None:
        # Authenticate if they're not there
        print('No credentials found, please authenticate')
        gauth.LocalWebserverAuth(port_numbers=[8080, 8090])
    elif gauth.access_token_expired:
        # Refresh them if expired
        print('Credentials have expired, refreshing')
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()
    # Save credentials
    gauth.SaveCredentialsFile("token.json")
    return GoogleDrive(gauth)
