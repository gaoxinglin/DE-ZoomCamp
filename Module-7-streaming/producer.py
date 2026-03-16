import json
import pandas as pd
from kafka import KafkaProducer
from time import time

# 读取 parquet 文件
df = pd.read_parquet('green_tripdata_2025-10.parquet')

# 只保留题目要求的列
columns = [
    'lpep_pickup_datetime',
    'lpep_dropoff_datetime',
    'PULocationID',
    'DOLocationID',
    'passenger_count',
    'trip_distance',
    'tip_amount',
    'total_amount'
]
df = df[columns]

# 连接 Redpanda
def json_serializer(data):
    return json.dumps(data).encode('utf-8')

server = 'localhost:9092'
producer = KafkaProducer(
    bootstrap_servers=[server],
    value_serializer=json_serializer
)

topic_name = 'green-trips'

t0 = time()

for _, row in df.iterrows():
    message = row.to_dict()
    # Timestamp 需转为字符串
    for key, val in message.items():
        if hasattr(val, 'isoformat'):
            message[key] = val.isoformat()
    producer.send(topic_name, value=message)

producer.flush()

t1 = time()
took = t1 - t0
print(f"Took {took:.2f} seconds")