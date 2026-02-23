"""@bruin

name: ingestion.trips
connection: duckdb-default

materialization:
  type: table
  strategy: append
image: python:3.12.8

columns:
  - name: VendorID
    type: integer
    description: "A code indicating the TPEP provider that provided the record."
  - name: tpep_pickup_datetime
    type: timestamp
    description: "The date and time when the meter was engaged."
  - name: tpep_dropoff_datetime
    type: timestamp
    description: "The date and time when the meter was disengaged."
  - name: passenger_count
    type: double
    description: "The number of passengers in the vehicle."
  - name: trip_distance
    type: double
    description: "The elapsed trip distance in miles reported by the taximeter."
  - name: RatecodeID
    type: double
    description: "The final rate code in effect at the end of the trip."
  - name: store_and_fwd_flag
    type: varchar
    description: "This flag indicates whether the trip record was held in vehicle memory before sending to the vendor."
  - name: PULocationID
    type: integer
    description: "TLC Taxi Zone in which the taximeter was engaged."
  - name: DOLocationID
    type: integer
    description: "TLC Taxi Zone in which the taximeter was disengaged."
  - name: payment_type
    type: integer
    description: "A numeric code signifying how the passenger paid for the trip."
  - name: fare_amount
    type: double
    description: "The time-and-distance fare calculated by the meter."
  - name: extra
    type: double
    description: "Miscellaneous extras and surcharges."
  - name: mta_tax
    type: double
    description: "$0.50 MTA tax that is automatically triggered based on the metered rate in use."
  - name: tip_amount
    type: double
    description: "Tip amount – This field is automatically populated for credit card tips. Cash tips are not included."
  - name: tolls_amount
    type: double
    description: "Total amount of all tolls paid in trip."
  - name: improvement_surcharge
    type: double
    description: "$0.30 improvement surcharge assessed trips at the flag drop."
  - name: total_amount
    type: double
    description: "The total amount charged to passengers. Does not include cash tips."
  - name: congestion_surcharge
    type: double
    description: "Total amount collected in trip for NYS congestion surcharge."
  - name: Airport_fee
    type: double
    description: "$1.25 for pick up only at LaGuardia and John F. Kennedy Airports."
  - name: taxi_type
    type: varchar
    description: "The type of taxi (e.g., yellow, green)."
  - name: extracted_at
    type: timestamp
    description: "The timestamp when the data was extracted."

@bruin"""

import os
import json
import pandas as pd
from datetime import datetime

def materialize():
    start_date_str = os.environ.get("BRUIN_START_DATE")
    end_date_str = os.environ.get("BRUIN_END_DATE")
    
    bruin_vars_str = os.environ.get("BRUIN_VARS", "{}")
    bruin_vars = json.loads(bruin_vars_str)
    taxi_types = bruin_vars.get("taxi_types", ["yellow"])
    
    start_date = pd.to_datetime(start_date_str)
    end_date = pd.to_datetime(end_date_str)
    
    # Generate a list of months between start_date and end_date
    months = pd.date_range(start_date.replace(day=1), end_date, freq='MS')
    if len(months) == 0:
        months = [start_date.replace(day=1)]
        
    dfs = []
    for taxi_type in taxi_types:
        for month in months:
            year_str = month.strftime("%Y")
            month_str = month.strftime("%m")
            url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi_type}_tripdata_{year_str}-{month_str}.parquet"
            try:
                df = pd.read_parquet(url)
                
                # Filter data for the specific date window
                pickup_col = None
                if 'tpep_pickup_datetime' in df.columns:
                    pickup_col = 'tpep_pickup_datetime'
                elif 'lpep_pickup_datetime' in df.columns:
                    pickup_col = 'lpep_pickup_datetime'
                elif 'pickup_datetime' in df.columns:
                    pickup_col = 'pickup_datetime'
                
                if pickup_col:
                    mask = (df[pickup_col] >= pd.to_datetime(start_date_str)) & (df[pickup_col] < pd.to_datetime(end_date_str) + pd.Timedelta(days=1))
                    df = df[mask]
                
                df['taxi_type'] = taxi_type
                df['extracted_at'] = datetime.now()
                dfs.append(df)
            except Exception as e:
                print(f"Failed to fetch {url}: {e}")
                
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    else:
        return pd.DataFrame()
