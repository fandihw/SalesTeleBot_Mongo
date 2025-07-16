import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import SERVICE_ACCOUNT_PATH



FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")  # Path ke file .json

def upload_photo(file_path):
    credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_PATH, scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials)

    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [FOLDER_ID]
    }

    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    file_id = file.get('id')
    return f"https://drive.google.com/file/d/{file_id}/view"
