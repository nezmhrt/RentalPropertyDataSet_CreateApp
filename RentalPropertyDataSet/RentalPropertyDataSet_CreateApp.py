# スーモ賃貸物件のデータセットを作成するソフト
# 参考code:http://www.analyze-world.com/entry/2017/10/09/062445


import requests
from bs4 import BeautifulSoup
import time
import re
import pandas as pd
from pandas import Series, DataFrame

# url for suumo.jp named of place :chiyoda p.1
url = 'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=030&bs=040&ta=13&sc=13101&cb=0.0&ct=9999999&mb=0&mt=9999999&et=9999999&cn=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&sngz=&po1=09'
r = requests.get(url)


soup = BeautifulSoup(r.content, "html.parser")

# 物件リスト取得
summary = soup.find("div", {'id': 'js-bukkenList'})

# ページ数取得
body = soup.find('body')
pages = body.find('div', class_='pagination pagination_set-nav')
pages_text = str(pages)
pages_split = int(pages_text.split('</a></li>\n</ol>')
                  [0][-3:].replace('>', ''))

# url
urls = []
urls.append(url)

# 2ページ目以降のurlを格納※１ページ目はurlが特殊
for i in range(pages_split - 1):
    pg = str(i + 2)
    url_page = url + '&page=' + pg
    urls.append(url_page)

names = []  # 住宅名
addresses = []  # 住所
locations = []  # 場所
ages = []  # 築年数
heights = []  # 建物高さ
floors = []  # 階
rent = []  # 賃料
areas = []  # 面積
detail_urls = []  # 詳細url

for url in urls:
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    summary = soup.find("div", {'id': 'js-bukkenList'})
    apartments = summary.find_all('div', class_='cassetteitem')

    for apartment in apartments:

        # 住宅名取得
        name = apartment.find('div', class_='cassetteitem_content-title').text
        # 住所取得
        address = apartment.find('li', class_='cassetteitem_detail-col1').text
        # 場所取得
        location = apartment.find(
            'li', class_='cassetteitem_detail-col2')('div')[0].text
        # 築年数、階数取得
        age_and_height = apartment.find(
            'li', class_='cassetteitem_detail-col3')
        age = age_and_height('div')[0].text
        height = age_and_height('div')[1].text

        for i in apartment.find_all('tbody'):
            names.append(name)
            addresses.append(address)
            locations.append(location)
            ages.append(age)
            heights.append(height)

        table = apartment.find('table')
        rows = []
        rows.append(table.find_all('tr'))

        data = []
        for row in rows:
            for tr in row:
                cols = tr.find_all('td')
                if len(cols) != 0:
                    _floor = cols[2].text
                    _floor = re.sub('[\r\n\t]', '', _floor)
                    _rent_cell = cols[3].find('ul').find_all('li')
                    _rent = _rent_cell[0].find('span').text
                    _floor_cell = cols[5].find('ul').find_all('li')
                    _area = _floor_cell[1].find('span').text
                    _detail_url = cols[8].find('a')['href']
                    _detail_url = 'https://suumo.jp' + _detail_url

                    text = [_floor, _rent, _area, _detail_url]
                    data.append(text)
        for row in data:
            floors.append(row[0])
            rent.append(row[1])
            areas.append(row[2])
            detail_urls.append(row[3])

        time.sleep(5)


names = Series(names)
addresses = Series(addresses)
locations = Series(locations)
ages = Series(ages)
heights = Series(heights)
floors = Series(floors)
rent = Series(rent)
areas = Series(areas)
detail_urls = Series(detail_urls)

suumo_df = pd.concat([names, addresses, locations, ages, heights, floors, rent,
                      areas, detail_urls], axis=1)
suumo_df.columns = ['Name', 'Address', 'Location', 'Age', 'Height', 'Floor', 'Rent',
                    'Area', 'Detail_url']

suumo_df.to_csv('suumo.csv', encoding='utf-8', header=True, index=False)
