import requests
import pandas as pd
from bs4 import BeautifulSoup

# 發送 HTTP GET 請求並獲取網頁原始碼
print("正在發送 HTTP GET 請求...")
res = requests.get('https://news.ltn.com.tw/list/breakingnews')

# 檢查請求是否成功
if res.status_code == 200:
    print("HTTP 請求成功！")
else:
    print("HTTP 請求失敗！")
    exit()

soup = BeautifulSoup(res.text, 'lxml')

# 創建一個空列表來存儲新聞資訊的字典
news_list = []

# 選取每則新聞的標題、連結、發佈時間和圖片連結
for li in soup.select('ul.list li'):
    title = li.select_one('.title').text.strip()
    link = li.select_one('a').get('href')
    dt = li.select_one('.time').text.strip()
    img_url = li.select_one('img')['data-src']

    # 將新聞資訊存儲為字典
    news_info = {
        'Title': title,
        'Link': link,
        'Publish Time': dt,
        'Image URL': img_url
    }

    # 將字典添加到列表中
    news_list.append(news_info)

    # 在終端機中顯示新聞資訊
    print(f"標題：{title}")
    print(f"連結：{link}")
    print(f"發佈時間：{dt}")
    print(f"圖片連結：{img_url}")
    print()

# 將列表轉換為 DataFrame
df = pd.DataFrame(news_list)

# 將 DataFrame 寫入 CSV 檔案
filename = 'ltn_news_with_images.csv'
df.to_csv(filename, index=False, encoding='utf-8-sig')

print(f'新聞資訊已儲存至 {filename} 檔案中。')
