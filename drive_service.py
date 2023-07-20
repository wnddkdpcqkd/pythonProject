from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials


class DriveService:
    def __init__(self, service_key_dir):
        scope = ['https://www.googleapis.com/auth/drive']
        credentials = Credentials.from_service_account_file(service_key_dir, scopes=scope)
        self.drive_service = build('drive', 'v3', credentials=credentials)

    def add_spreadsheet(self, spreadsheet_name):
        folder_id = '1qvkNTx1dRvQHs8LPFYHZ94QVuxO6AzJF'  # 공유 문서함의 ID를 입력합니다.
        spreadsheet_metadata = {
            'name': spreadsheet_name,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': [folder_id],
            'allowFileDiscovery': True,
        }

        spreadsheet = self.drive_service.files().create(body=spreadsheet_metadata, fields='id').execute()
        spreadsheet_id = spreadsheet.get('id')
        return spreadsheet_id

