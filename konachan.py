import json
import os
import requests
from datetime import datetime, timedelta
import concurrent.futures
import urllib3
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# 文件保存路径，用双斜号
FILE_PATH = 'C:\\Users\\Sukap\\Desktop\\konachan\\'
# Konachan的链接，可改成konachan.com
base_url = 'https://konachan.net/post.json?tags=date:{}-{}-{}&page={}'

current_date = datetime.strptime('2024-01-05', '%Y-%m-%d')
current_page = 1

# 创建一个自定义的会话对象，用于添加重试逻辑
session = requests.Session()
retry_strategy = Retry(total=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount('https://', adapter)


# 错误日志的处理
def error_log(error_type, msg=None, status_code=None, url=None):
    json_path = FILE_PATH + 'error.json'
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            json_data = file.read()
            if json_data.strip():
                json_data = json.loads(json_data)
            else:
                json_data = []
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        json_data = []

    if status_code:
        json_data.append({'error_type': error_type, 'status_code': status_code, 'msg': msg, 'url': url})
    else:
        json_data.append({'error_type': error_type, 'msg': msg})

    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(json_data, file, ensure_ascii=False)


# 使用多线程下载图片
def download_image_in_thread(url, folder_path, image_id):
    print(f"ID: {image_id} 正在下载...")
    response = session.get(url)
    if response.status_code == 200:
        with open(os.path.join(folder_path, f"{image_id}.jpg"), 'wb') as file:
            file.write(response.content)
        print(f"ID: {image_id} 下载完成")
    else:
        # 理论编写，实际没遇到过...
        print(f"ID: {image_id} 下载失败，状态码：{response.status_code}")
        error_log('图片下载失败', f"ID: {image_id} 下载失败", response.status_code, url)


def main():
    global current_date, current_page
    try:
        while True:
            url = base_url.format(current_date.year, current_date.month, current_date.day, current_page)
            print(f"URL: {url}")
            response = session.get(url)
            print(f"Status Code: {response.status_code}")
            response.raise_for_status()
            data = response.json()

            # 解析获取到的JSON数据
            if not data:
                # 将某日的全部下载完成后增加一日
                current_date += timedelta(days=1)
                # 重置一下页数
                current_page = 1
            else:
                # 最大线程数，按需修改（不是越大越好）
                max_workers = 6
                # 如果需要限制线程数，则在下一行的括号中填入 max_workers
                with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
                    for item in data:
                        post_id = item.get('id')
                        file_url = item.get('file_url')
                        # 创建"年 + 月"文件夹
                        folder_name = f"{current_date.year}{current_date.month:02d}"
                        folder_path = os.path.join(FILE_PATH, folder_name)
                        if not os.path.exists(folder_path):
                            os.makedirs(folder_path)

                        # 提交图片下载任务给线程池
                        executor.submit(download_image_in_thread, file_url, folder_path, post_id)

                    # 检查日期是否等于当前日期，如果是则停止循环
                    if current_date.date() == datetime.now().date():
                        break

                current_page += 1

    except requests.exceptions.RequestException as e:
        print('RequestException' + str(e))
        error_log('请求异常', str(e))
    except ValueError as e:
        error_log('数据解析失败', str(e))


if __name__ == "__main__":
    main()
