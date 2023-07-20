# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import scrap
from drive_service import DriveService
import pandas as pd
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
import gspread
import spreadsheet_service
import time


def convert_to_number(value):
    try:
        number_value = int(value)  # 또는 int(value)를 사용하여 정수로 변환할 수도 있습니다.
        return number_value
    except ValueError:
        return -1


if __name__ == '__main__':
    service_key_path = './serviceKey.json'
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = Credentials.from_service_account_file(service_key_path, scopes=scope)

    client = gspread.authorize(credentials)

    g_drive_service = DriveService(service_key_path)
    config_sheet = client.open_by_key('1Gp_3WvNpXJLqPnda-6lZSCwdbULm_1TpOTHLAkiS2hY')
    config_data = config_sheet.worksheet('설정').get_all_records()

    # initial setting
    today_sheet_id = g_drive_service.add_spreadsheet(datetime.today().strftime("%Y-%m-%d"))
    today_sheet = client.open_by_key(today_sheet_id)
    today_sheet.add_worksheet('개요', 300, 3)
    today_sheet.add_worksheet('정보', 3000, 3)
    Sheet_1 = today_sheet.worksheet('Sheet1')
    today_sheet.del_worksheet(Sheet_1)

    ws_outline = today_sheet.worksheet('개요')
    ws_outline.append_row(['이름', '총개수', '뽑힌개수'])
    ws_posts = today_sheet.worksheet('정보')
    ws_posts.append_row(['이름', '제목', '상세페이지 링크'])

    for site in config_data:

        name = site['이름']
        site_url = site['사이트주소']
        include_keywords = site['포함']
        exclude_keywords = site['불포함']
        depth1 = site['depth1']
        depth2 = site['depth2']
        href_index = convert_to_number(site['href_index'])

        if site_url != '' and depth1 != '':
            posts = scrap.get_post_array(site_url, depth1, depth2, href_index)
            filtered_post = scrap.exclude_post_by_keywords(scrap.include_post_by_keywords(posts, include_keywords),
                                                           exclude_keywords)
            total_count = len(posts)
            filtered_count = len(filtered_post)

            try:
                append_row_res = ws_outline.append_row([name, total_count, filtered_count])
                appended_range = append_row_res.get('updates').get('updatedRange').split('!')[-1]
                print(appended_range)
                if total_count > 10:
                    num_rows = ws_outline.row_count
                    cell_format = {
                        "backgroundColor": {
                            "red": 1.0,
                            "green": 0.0,
                            "blue": 0.0
                        }
                    }
                    ws_outline.format(appended_range, cell_format)
            except Exception as e:
                print('오류 발생:', e)

            site_posts = []
            for post in filtered_post:
                site_posts.append([name, post['title'], post['link']])
            ws_posts.append_rows(site_posts)
            time.sleep(2)

    spreadsheet_service.resize_spread_sheet(spreadsheet_id=today_sheet_id,
                                            worksheet_id=ws_posts.id, credentials=credentials)
