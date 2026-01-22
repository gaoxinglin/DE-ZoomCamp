#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import click
from sqlalchemy import create_engine
from tqdm.auto import tqdm



dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]

@click.command()
@click.option('--pg_user', default='root', help='Postgres username')
@click.option('--pg_password', default='root', help='Postgres password')
@click.option('--pg_host', default='127.0.0.1', help='Postgres host')
@click.option('--pg_port', default=5432, type=int, help='Postgres port')
@click.option('--pg_db', default='ny_taxi', help='Postgres database name')
@click.option('--year', default=2025, type=int, help='Year of the data')
@click.option('--month', default=11, type=int, help='Month of the data')
@click.option('--target_table', default='green_taxi_data', help='Name of the target table')
@click.option('--chunksize', default=100000, type=int, help='Chunk size for ingestion')

def run(pg_user, pg_password, pg_host, pg_port, pg_db, year, month, target_table, chunksize):
    prefix = 'https://d37ci6vzurychx.cloudfront.net/trip-data' 
    url = f'{prefix}/green_tripdata_{year}-{month:02d}.parquet'

    print(f"Connecting to database...")
    engine = create_engine(f'postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}')

    print(f"Reading CSV data from {url}...")
    df = pd.read_parquet(url, engine='pyarrow')

    print("Data read successfully. Starting ingestion...")
    
    # 将 DataFrame 分块并使用 tqdm 显示进度
    total_chunks = (len(df) + chunksize - 1) // chunksize
    for i in tqdm(range(total_chunks), desc="Ingesting data"):
        start = i * chunksize
        end = min((i + 1) * chunksize, len(df))
        df_chunk = df.iloc[start:end]
        
        # 第一块使用 'replace' 清空表，后续使用 'append'
        if_exists = 'replace' if i == 0 else 'append'
        df_chunk.to_sql(name=target_table, con=engine, if_exists=if_exists, index=False)
    
    print("Done.")

if __name__ == '__main__':
    run()




