from googleapiclient.discovery import build


def resize_spread_sheet(spreadsheet_id, worksheet_id, credentials):
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
    sheets_api = build('sheets', 'v4', credentials=credentials)
    res = sheets_api.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": requests}).execute()
    return res

