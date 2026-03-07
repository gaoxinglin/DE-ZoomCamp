# Module 6 - Batch Processing with PySpark

This module covers batch data processing using Apache Spark and PySpark, applied to the NYC Yellow Taxi dataset for November 2025.

---

## Q1: Install Spark and PySpark

Install PySpark and start a local Spark session:

```python
import pyspark
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .master("local[*]") \
    .appName('yellow_taxi_processing') \
    .getOrCreate()

print(spark.version)
```

**Answer: `4.1.1`**

---

## Q2: Yellow November 2025 — Average Parquet File Size

Read the November 2025 Yellow Taxi data, repartition to 4 partitions, and save as parquet:

```python
input_path = 'data/yellow_tripdata_2025-11.parquet'
df = spark.read.parquet(input_path)

df = df.repartition(4)
df.write.parquet('data/pq/yellow/2025/11/', mode='overwrite')
```

This creates 4 `.parquet` files. Each file is approximately **25 MB**.

**Answer: `25MB`**

---

## Q3: Count Records on November 15th

Filter trips that started on November 15, 2025:

```python
from pyspark.sql import functions as F

df_15th = df \
    .withColumn('pickup_date', F.to_date('tpep_pickup_datetime')) \
    .filter(F.col('pickup_date') == '2025-11-15')

print(df_15th.count())
```

**Answer: `162,604`**

---

## Q4: Longest Trip in Hours

Calculate the duration of each trip and find the maximum:

```python
df_duration = df \
    .withColumn('duration_hours',
        (F.unix_timestamp('tpep_dropoff_datetime') - F.unix_timestamp('tpep_pickup_datetime')) / 3600)

longest = df_duration.select(F.max('duration_hours')).collect()[0][0]
print(f"{longest:.1f}")
```

**Answer: `90.6` hours**

---

## Q5: Spark User Interface Port

Spark's built-in web UI shows job progress, DAGs, executors, and more.

**Answer: `4040`**

Access it at [http://localhost:4040](http://localhost:4040) while a Spark session is running.

---

## Q6: Least Frequent Pickup Location Zone

Load the zone lookup CSV and join with the taxi data using Spark SQL:

```python
df_zones = spark.read.option("header", "true").csv('data/taxi_zone_lookup.csv')

df.createOrReplaceTempView('yellow_taxi_data')
df_zones.createOrReplaceTempView('zones')

spark.sql("""
    SELECT z.Zone, COUNT(1) as trip_count
    FROM yellow_taxi_data t
    JOIN zones z ON t.PULocationID = z.LocationID
    GROUP BY z.Zone
    ORDER BY trip_count ASC
    LIMIT 1
""").show()
```

**Answer: `Arden Heights`** (1 trip)
