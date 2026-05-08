import sys
from curl_cffi import requests
from bs4 import BeautifulSoup
import json
import os
import time

# 全域設定請求標頭
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://javdb.com/',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# 初始化 Session (模擬 Chrome 瀏覽器指紋)
session = requests.Session(impersonate="chrome")
session.headers.update(HEADERS)

# 設定基礎存檔路徑
BASE_PATH = '/Volumes/DS220/BT/income/'
if not os.path.exists(BASE_PATH):
    # 如果是在 Synology 環境執行
    if os.path.exists('/volume1/DS220/BT/income/'):
        BASE_PATH = '/volume1/DS220/BT/income/'


#----------------------------------------------------------------------------------------------------------
# 將資料寫入json
#----------------------------------------------------------------------------------------------------------
def download_image(img_url, save_path):
    try:
        img_response = session.get(img_url, stream=True, timeout=10)
        if img_response.status_code == 200:
            with open(save_path, 'wb') as file:
                for chunk in img_response.iter_content(1024):
                    file.write(chunk)
            return True
        else:
            print(f"Failed to download image. Status code: {img_response.status_code}")
    except Exception as e:
        print(f"Error downloading image: {e}")
    return False
#----------------------------------------------------------------------------------------------------------
# 將資料寫入json
#----------------------------------------------------------------------------------------------------------
def write_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
#----------------------------------------------------------------------------------------------------------
# 取得詳細資料
#----------------------------------------------------------------------------------------------------------
def get_data(url):  
    # 發送HTTP GET請求獲取網頁內容
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching detail page: {e}")
        return

    web_content = response.content


    # 使用BeautifulSoup解析HTML内容
    soup = BeautifulSoup(web_content, 'html.parser')
    #print(soup)
    # 查找并提取所需的信息
    # 查找并提取所需的信息
    title_element = soup.find('strong', class_='current-title')
    title = title_element.text.strip() if title_element else "No title found"
    print("title:", title)
    # 查找并提取img标签中class为video-cover的内容
    img_element = soup.find('img', class_='video-cover')
    if img_element:
        img_src = img_element.get('src')
        print(f"Image source: {img_src}")
    else:
        print("No img element with class 'video-cover' found")


    # 查找并提取包含 <strong>番號:</strong> 的内容
    strong_element = soup.find('strong', string='番號:')
    if strong_element:
        span_element = strong_element.find_next('span', class_='value')
        if span_element:
            av_no = span_element.text.strip()
            print(f"番號: {av_no}")
        else:
            print("No <span> element with class 'value' found next to <strong>番號:</strong>")
            av_no = "unknown"
    else:
        print("No <strong> element with text '番號:' found")
        av_no = "unknown"

    # 確保資料夾存在
    save_dir = os.path.join(BASE_PATH, av_no)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)

    # 資料寫入json
    title = av_no + ' ' + title
    data = {
        "title": title,
        "actress": "",
        "sid": av_no
    }
    file_nam = os.path.join(save_dir, f"{av_no}.json")
    write_to_json(data, file_nam)    
    # 下載圖檔 
    file_nam = os.path.join(save_dir, "cover.png")
    download_image(img_src, file_nam)

    #更換資料夾名
    old_name = save_dir
    new_name = os.path.join(BASE_PATH, title)
    #print(old_name)
    #print(new_name)
    #if old_name != new_name:
    #    os.rename(old_name, new_name)

#------------------------------------------------------------------------------------
# 取得網址
#------------------------------------------------------------------------------------
def get_url(key):    
    search_keyword = key
    first_result_link = ''
    # 目标URL
    search_url = f"https://javdb.com/search?q={search_keyword}"
    print(f"Searching: {search_url}")
    
    # 發送HTTP GET請求獲取搜尋結果頁面內容
    try:
        response = session.get(search_url, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return ''

    # 檢查請求是否成功
    if response.status_code == 200:

        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 查找并提取第一个结果的链接
        first_result = soup.find('a', class_='box')
        if first_result:
            first_result_link = "https://javdb.com" + first_result['href']
            
            #print(f"第一個連結網址: {first_result_link}")
        else:
            print("No result found for the search.")
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
    
    return first_result_link         
#-------------------------------------------------------------------------------
# Main function :Get state
#-------------------------------------------------------------------------------
if __name__ == '__main__':
   if len(sys.argv) != 2:
       print("Usage: python3 script.py <search_keyword>")
   else:
       search_keyword = sys.argv[1]
       link = get_url(search_keyword)
       #print(f"第一個連結網址: {link}")
       if len(link) != 0:
          get_data(link)
