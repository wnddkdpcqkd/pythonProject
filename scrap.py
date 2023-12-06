import gspread
import requests
import urllib3
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib3.exceptions import InsecureRequestWarning


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_link_from_arr(x, index=-1):
    links = x.find_all('a')
    if len(links) > 1:
        if index == -1:
            return '두개 이상의 하이퍼 링크가 있습니다. href_index 값을 입력 해주세요.'
        elif index > len(links):
            return 'href_index 값이 하이퍼링크 개수보다 큽니다.'
        else:
            for idx, link in enumerate(links):
                if idx+1 == index:
                    return link.get('href')
    elif len(links) == 0:
        return '연결된 하이퍼 링크가 없습니다. depth1 을 hyperlink가 포함되도록 설정해주세요.'
    else:
        for elem in links:
            return elem.get('href')


def convert_link_format(site_url: str, post_url: str):
    for char in post_url:
        if '\uac00' <= char <= '\ud7a3':  # 한글 음절의 범위
            return post_url.replace('¤t', '&current')

    return urljoin(site_url, post_url).replace('¤t', '&current')


def get_post_array(site_url, depth1, depth2, href_index):
    # post_array : return 값
    post_array = []
    try:
        response = requests.get(site_url, verify=False)
    except requests.exceptions.SSLError as e:
        print('SSL Error [보안접근 불가]')
        return post_array
    except requests.exceptions.ConnectionError as e:
        print('Connection Error [연결 오류]')
        return post_array

    depth1_arr = list(filter(None, depth1.split(',')))
    depth2_arr = list(filter(None, depth2.split(',')))
    if response.status_code == 200:
        html_content = response.content
        soup = BeautifulSoup(html_content, 'html.parser')

        if len(depth1_arr) == 2:
            tag, attr = map(str.strip, depth1_arr)
            depth1_data = soup.find_all(tag, attr)
        else:
            tag = depth1_arr[0].strip()
            depth1_data = soup.find_all(tag)

        for data in depth1_data:
            post = None

            if len(depth2_arr) != 0:
                # depth2 까지 있을 때
                if len(depth2_arr) == 2:
                    tag, attr = map(str.strip, depth2_arr)
                    depth2_data = data.find_all(tag, attr)
                else:
                    tag = depth1_arr[0].strip()
                    depth2_data = data.find_all(tag)

                for data2 in depth2_data:
                    post = data2

            else:
                # depth1 까지만 있을 때
                post = data

            if post is not None:
                title = post.get_text(strip=True)
                link = convert_link_format(site_url, get_link_from_arr(data, href_index))
                post_array.append({'title': title, 'link': link})

    return post_array


def include_post_by_keywords(array: list, keywords: str):
    keyword_arr = keywords.split(',')
    new_arr = []
    for post in array:
        for keyword in keyword_arr:
            if keyword in post['title']:
                new_arr.append(post)
                break

    return new_arr


def exclude_post_by_keywords(array: list, keywords: str):
    keyword_arr = keywords.split(',')
    new_arr = []
    for post in array:
        new_arr.append(post)
        for keyword in keyword_arr:
            if keyword != '' and keyword in post['title']:
                new_arr.pop()
                break

    return new_arr

