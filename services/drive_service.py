import os
import re
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
SERVICE_ACCOUNT_FILE = 'service_account.json'

def get_drive_service():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(f"Missing {SERVICE_ACCOUNT_FILE} for Google Drive auth.")
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def extract_file_id(url: str) -> str:
    """
    Extracts the file ID from various Google Drive URL formats.
    """
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    match = re.search(r'id=([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    raise ValueError(f"Invalid Google Drive URL provided: {url}")

def download_resume(url: str) -> bytes:
    """
    Downloads a file from Google Drive into memory and returns the bytes.
    """
    try:
        file_id = extract_file_id(url)
        service = get_drive_service()
        
        request = service.files().get_media(fileId=file_id)
        file_bytes = io.BytesIO()
        downloader = MediaIoBaseDownload(file_bytes, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            
        return file_bytes.getvalue()
    except Exception as e:
        raise Exception(f"Failed to download resume from Google Drive: {str(e)}")
