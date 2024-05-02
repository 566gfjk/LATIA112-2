import time
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service

# 設置 Chrome 驅動程式的路徑和啟動 WebDriver
service = Service('chromedriver')
driver = webdriver.Chrome(service=service)

# 發送 HTTP GET 請求並獲取網頁原始碼
print("正在發送 HTTP GET 請求...")
driver.get('https://news.ltn.com.tw/list/breakingnews')

# 等待網頁加載完成
time.sleep(3)

# 獲取網頁原始碼
html = driver.page_source

# 關閉瀏覽器
driver.quit()

# 使用 BeautifulSoup 解析網頁原始碼
soup = BeautifulSoup(html, 'html.parser')

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
filename = 'selenium_ltn_news_with_images.csv'
df.to_csv(filename, index=False, encoding='utf-8-sig')
