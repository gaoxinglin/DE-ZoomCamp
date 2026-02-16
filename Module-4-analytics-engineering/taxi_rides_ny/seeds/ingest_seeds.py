import os
import requests
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def download_csv(url, target_dir, filename):
    # 1. 确保目录存在
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        logging.info(f"创建目录: {target_dir}")

    target_path = os.path.join(target_dir, filename)

    # 2. 下载文件
    try:
        logging.info(f"正在从 {url} 下载数据...")
        response = requests.get(url, timeout=30)
        response.raise_for_status() # 检查请求是否成功

        # 3. 写入文件
        with open(target_path, 'wb') as f:
            f.write(response.content)
        
        logging.info(f"文件已成功保存至: {target_path}")
    
    except requests.exceptions.RequestException as e:
        logging.error(f"下载失败: {e}")

if __name__ == "__main__":
    URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
    TARGET_DIR = os.path.dirname(os.path.abspath(__file__))
    FILENAME = "taxi_zone_lookup.csv"
    
    download_csv(URL, TARGET_DIR, FILENAME)