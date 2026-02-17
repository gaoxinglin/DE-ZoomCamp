import os
import requests
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def download_file(url, target_dir, filename):
    # 1. 确保目录存在
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        logging.info(f"创建目录: {target_dir}")

    target_path = os.path.join(target_dir, filename)

    # 如果文件已存在则跳过
    if os.path.exists(target_path):
        logging.info(f"文件已存在，跳过下载: {filename}")
        return

    # 2. 下载文件
    try:
        logging.info(f"正在从 {url} 下载数据...")
        response = requests.get(url, timeout=60)
        response.raise_for_status() # 检查请求是否成功

        # 3. 写入文件
        with open(target_path, 'wb') as f:
            f.write(response.content)
        
        logging.info(f"文件已成功保存至: {target_path}")
    
    except requests.exceptions.RequestException as e:
        logging.error(f"下载失败 {filename}: {e}")

if __name__ == "__main__":
    # 1. 下载 Taxi Zone Lookup (CSV) - 存放在 seeds 目录
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    ZONE_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
    download_file(ZONE_URL, BASE_DIR, "taxi_zone_lookup.csv")

    # 2. 下载 FHV 数据 (Parquet) - 存放在 data/fhv 目录
    PROJECT_ROOT = os.path.dirname(BASE_DIR)
    FHV_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "fhv")
    
    years = [2019, 2020]
    for year in years:
        for month in range(1, 13):
            filename = f"fhv_tripdata_{year}-{month:02d}.parquet"
            url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{filename}"
            download_file(url, FHV_DATA_DIR, filename)
