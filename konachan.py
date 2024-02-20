import json
import os
import requests
from datetime import datetime, timedelta

download_folder = "C:\\Users\\Sukap\\Desktop\\konachan"

# 设置初始日期
current_date = datetime(2024, 1, 1)
# 获取初始月份
current_month = current_date.strftime('%Y%m')

while True:
    # 创建当月文件夹
    month_folder = os.path.join(download_folder, current_month)
    if not os.path.exists(month_folder):
        os.makedirs(month_folder)

    # 格式化日期使其符合tags要求
    formatted_date = current_date.strftime('%Y-%m-%d')
    # 传递参数
    url = f'https://konachan.net/post.json?tags=date:{formatted_date}&page=1'
    response = requests.get(url)
    # 打印状态码
    print(f"Status Code: {response.status_code}")
    # 打印链接
    print(f"URL: {url}")

    # 检查是否成功获取响应
    if response.status_code == 200:
        try:
            data = response.json()
        # 处理JSON解析错误
        except json.decoder.JSONDecodeError:
            data = None
    else:
        data = None

    # 判断如果JSON数据不为空
    if data is not None and data:
        for item in data:
            image_id = str(item["id"])
            file_url = item["file_url"]
            file_extension = file_url.split('.')[-1]
            file_path = os.path.join(month_folder, f"{image_id}.{file_extension}")

            print(f"ID: {image_id} 正在下载...")
            # 将下载图片的响应命名为response_image
            response_image = requests.get(file_url)
            with open(file_path, 'wb') as f:
                f.write(response_image.content)
            print(f"ID: {image_id} 下载完成")

    # 下载完成日期加一天
    next_date = current_date + timedelta(days=1)
    # 判断月份是否改变
    if next_date.strftime('%Y%m') != current_month:
        # 更新当前月份
        current_month = next_date.strftime('%Y%m')
        # 更新文件夹路径
        month_folder = os.path.join(download_folder, current_month)
        if not os.path.exists(month_folder):
            # 在指定目录下创建新的月份文件夹
            os.makedirs(month_folder)

    # 更新当前日期
    current_date = next_date
