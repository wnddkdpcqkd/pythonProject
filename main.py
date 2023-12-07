import scrap
from service import DriveAndSheetService, get_different_spreadsheet_row, print_and_save
from datetime import datetime
import time


def convert_to_number(value):
    try:
        number_value = int(value)  # 또는 int(value)를 사용하여 정수로 변환할 수도 있습니다.
        return number_value
    except ValueError:
        return -1


if __name__ == '__main__':

    service = DriveAndSheetService()

    config_sheet = service.open_sheet_by_key('1Gp_3WvNpXJLqPnda-6lZSCwdbULm_1TpOTHLAkiS2hY')
    config_data = config_sheet.worksheet('설정').get_all_records()

    today_string = datetime.today().strftime("%Y-%m-%d")
    today_text_file = today_string + '.txt'
    today_sheet = service.add_spreadsheet(today_string)

    ws_outline = today_sheet.worksheet('개요')
    ws_outline.append_row(['이름', '총개수', '뽑힌개수'])
    ws_posts = today_sheet.worksheet('정보')
    ws_posts.append_row(['이름', '제목', '링크'])

    for site in config_data:

        name = site['이름']
        site_url = site['사이트주소']
        include_keywords = site['포함']
        exclude_keywords = site['불포함']
        depth1 = site['depth1']
        depth2 = site['depth2']
        href_index = convert_to_number(site['href_index'])

        if site_url != '' and depth1 != '':
            print_and_save(f'...추출중... [{name}]', today_text_file)
            posts = scrap.get_post_array(site_url, depth1, depth2, href_index)
            filtered_post = scrap.exclude_post_by_keywords(scrap.include_post_by_keywords(posts, include_keywords),
                                                           exclude_keywords)
            total_count = len(posts)
            filtered_count = len(filtered_post)

            try:
                append_row_res = ws_outline.append_row([name, total_count, filtered_count])
                appended_range = append_row_res.get('updates').get('updatedRange').split('!')[-1]
                if total_count == 0:
                    num_rows = ws_outline.row_count
                    cell_format = {
                        "backgroundColor": {
                            "red": 217/255,
                            "green": 234/255,
                            "blue": 211/255
                        }
                    }
                    ws_outline.format(appended_range, cell_format)
            except Exception as e:
                print_and_save('오류 발생', today_text_file)
                print_and_save(e, today_text_file)

            site_posts = []
            for post in filtered_post:
                site_posts.append([name, post['title'], post['link']])
            ws_posts.append_rows(site_posts)
            time.sleep(2)

    service.resize_spread_sheet(spreadsheet_id=today_sheet.id, worksheet_id=ws_posts.id)

    # -----------------------------------------오늘 자 데이터 추출 완료-------------------------------------------------#
    print_and_save('...추출 완료, 이전 데이터와 비교 시작...', today_text_file)
    # -----------------------------------------데이터 비교 시작-------------------------------------------------#
    old_spreadsheet = service.find_latest_sheet()

    if old_spreadsheet is not None:
        try:
            old_records = old_spreadsheet.worksheet('정보').get_all_records()
            today_records = today_sheet.worksheet('정보').get_all_records()
            different_link_arr = get_different_spreadsheet_row(old_records, today_records, '링크')
            different_title_arr = get_different_spreadsheet_row(old_records, today_records, '제목')
            print_and_save('링크 비교중...', today_text_file)
            for index, row in different_link_arr.iterrows():
                row_number = index + 2
                cell_format = {
                    "backgroundColor": {
                        "red": 217 / 255,
                        "green": 234 / 255,
                        "blue": 211 / 255
                    }
                }
                appended_range = f"C{row_number}"
                ws_posts.format(appended_range, cell_format)
                time.sleep(2)

            print_and_save('제목 비교중...', today_text_file)
            for index, row in different_link_arr.iterrows():
                row_number = index + 2
                cell_format = {
                    "backgroundColor": {
                        "red": 242 / 255,
                        "green": 213 / 255,
                        "blue": 123 / 255
                    }
                }
                appended_range = f"B{row_number}"
                ws_posts.format(appended_range, cell_format)
                time.sleep(2)

            print_and_save('모든 프로세스가 끝났습니다.', today_text_file)

        except Exception as e:
            print_and_save('이전 데이터와의 비교에 실패했습니다.', today_text_file)
            print_and_save(e, today_text_file)

    print_and_save('[파일명] : [' + datetime.today().strftime("%Y-%m-%d") + '.txt]', today_text_file)

