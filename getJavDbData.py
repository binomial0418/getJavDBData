import sys
import requests
from bs4 import BeautifulSoup
import json
import os

#----------------------------------------------------------------------------------------------------------
# 將資料寫入json
#----------------------------------------------------------------------------------------------------------
def download_image(img_url, save_path):
    img_response = requests.get(img_url, stream=True)
    if img_response.status_code == 200:
        with open(save_path, 'wb') as file:
            for chunk in img_response.iter_content(1024):
                file.write(chunk)
        return True
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
    # 设置请求头以模仿浏览器
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # 发送HTTP GET请求获取网页内容
    response = requests.get(url, headers=headers)
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
    else:
        print("No <strong> element with text '番號:' found")

    #資料寫入json
    title = av_no + ' ' + title
    data = {
        "title": title,
        "actress": "",
        "sid":av_no
    }
    #file_nam = '/volume1/DS220/BT/income/' + av_no + '/'  +  title + '.json'
    file_nam = '/volume1/DS220/BT/income/' + av_no + '/'  +  av_no + '.json'
    write_to_json(data,file_nam)    
    #下載圖檔 
    #file_nam = '/volume1/DS220/BT/income/' + av_no + '/' + title + '_B.png'
    file_nam = '/volume1/DS220/BT/income/' + av_no + '/' + 'cover.png'
    download_image(img_src,file_nam)
    #更換資料夾名
    old_name = '/volume1/DS220/BT/income/' + av_no + '/' 
    new_name = '/volume1/DS220/BT/income/' + '/' + title + '/'
    #print(old_name)
    #print(new_name)
    #os.rename(old_name, new_name)
#------------------------------------------------------------------------------------
# 取得網址
#------------------------------------------------------------------------------------
def get_url(key):    
    search_keyword = key
    first_result_link = ''
    # 目标URL
    search_url = f"https://javdb.com/search?q={search_keyword}"

    # 发送HTTP GET请求获取搜索结果页面内容
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(search_url, headers=headers)

    # 检查请求是否成功
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
