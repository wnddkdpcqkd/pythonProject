from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import gspread
from datetime import datetime, timedelta
import pandas as pd
import os


def print_and_save(text, filename="output.txt"):
    print(text)  # 콘솔에 출력
    with open(filename, "a") as file:  # 파일에 추가
        file.write(text + "\n")


def get_different_spreadsheet_row(list1, list2, column):
    old_df = pd.DataFrame(list1)
    new_df = pd.DataFrame(list2)

    print(old_df, new_df)
    new_entries = new_df[~new_df.set_index(column).index.isin(old_df.set_index(column).index)]

    return new_entries


class DriveAndSheetService:
    def __init__(self):
        path = os.path.abspath(__file__)
        directory = os.path.dirname(path)
        service_key_path = os.path.join(directory, 'serviceKey.json')
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        self.credentials = Credentials.from_service_account_file(service_key_path, scopes=scope)
        self.client = gspread.authorize(self.credentials)
        self.drive_service = build('drive', 'v3', credentials=self.credentials)
        self.drive_folder_id = '1qvkNTx1dRvQHs8LPFYHZ94QVuxO6AzJF'  # 공유 문서함의 ID를 입력합니다.

    def make_spreadsheet(self,spreadsheet_name):
        spreadsheet_metadata = {
            'name': spreadsheet_name,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': [self.drive_folder_id],
            'allowFileDiscovery': True,
        }
        spreadsheet = self.drive_service.files().create(body=spreadsheet_metadata, fields='id').execute()
        spreadsheet_id = spreadsheet.get('id')
        spreadsheet = self.client.open_by_key(spreadsheet_id)
        spreadsheet.add_worksheet('정보', 3000, 3)
        spreadsheet.add_worksheet('개요', 300, 3)
        sheet_1 = spreadsheet.worksheet('Sheet1')
        spreadsheet.del_worksheet(sheet_1)
        return spreadsheet

    def add_spreadsheet(self, spreadsheet_name):
        try:
            spreadsheet = self.client.open(spreadsheet_name, self.drive_folder_id)
            self.client.del_spreadsheet(spreadsheet.id)
            print(f"[{spreadsheet_name}]가 이미 존재합니다. 파일을 삭제하고 새로 생성합니다.")
            spreadsheet = self.make_spreadsheet(spreadsheet_name)
            return spreadsheet

        except gspread.SpreadsheetNotFound:
            print(f"[{spreadsheet_name}]를 생성합니다.")
            spreadsheet = self.make_spreadsheet(spreadsheet_name)
            return spreadsheet

    def resize_spread_sheet(self, spreadsheet_id, worksheet_id):

        sheets_api = build('sheets', 'v4', credentials=self.credentials)
        requests = [
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": worksheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": 1
                    },
                    "properties": {
                        "pixelSize": 200
                    },
                    "fields": "pixelSize"
                }
            }, {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": worksheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 1,
                        "endIndex": 2
                    },
                    "properties": {
                        "pixelSize": 600
                    },
                    "fields": "pixelSize"
                }
            }, {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": worksheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 2,
                        "endIndex": 3
                    },
                    "properties": {
                        "pixelSize": 600
                    },
                    "fields": "pixelSize"
                }
            }
        ]

        res = sheets_api.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": requests}).execute()
        return res

    def open_sheet_by_key(self, sheet_id):
        return self.client.open_by_key(sheet_id)

    def find_latest_sheet(self):
        delta = 1
        while delta < 7:
            date = (datetime.today() - timedelta(delta)).strftime("%Y-%m-%d")
            try:
                old_spreadsheet = self.client.open(date, self.drive_folder_id)
                print(f"Spreadsheet [{date}]와 비교 시작.")
                return old_spreadsheet
            except gspread.SpreadsheetNotFound:
                print(f"Spreadsheet [{date}]이 없습니다.")
                delta = delta + 1
        return None
