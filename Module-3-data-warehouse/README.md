# Module 3: Data Warehousing with BigQuery

This module covers Data Warehousing concepts using [Google BigQuery](https://cloud.google.com/bigquery), including table types, optimization through partitioning and clustering, and Machine Learning integrated into the data warehouse.

## Overview

In this module, we learned how to:
- Create and manage External and Native tables in BigQuery
- Optimize query performance using Partitioning and Clustering
- Understand BigQuery's columnar storage architecture
- Implement Machine Learning models directly in SQL using BigQuery ML
- Use [DLT (Data Load Tool)](https://dlthub.com/) to ingest data into Google Cloud Storage (GCS) and BigQuery

## Files & Scripts

| File | Description |
|------|-------------|
| [big_query.sql](big_query.sql) | Core SQL for creating external/partitioned tables and performance testing |
| [big_query_ml.sql](big_query_ml.sql) | Workflow for building and evaluating Machine Learning models in BigQuery |
| [big_query_hw.sql](big_query_hw.sql) | SQL solutions for the module homework |
| [load_yellow_taxi_data.py](load_yellow_taxi_data.py) | Python script to upload Parquet files to GCS |
| [DLT_upload_to_GCP.ipynb](DLT_upload_to_GCP.ipynb) | Jupyter notebook demonstrating data ingestion with DLT |

## Setup and Data Ingestion

1. **Upload Data to GCS**:
   Use the Python script or DLT notebook to upload the 2024 Yellow Taxi data (January to June) to your GCS bucket.
   ```bash
   # Make sure to set your bucket name in the script
   python load_yellow_taxi_data.py
   ```

2. **Create Tables**: 
   Use [big_query.sql](big_query.sql) to create external tables pointing to GCS and native tables inside BigQuery.

---

## Key Optimization Concepts

### Partitioning vs Clustering
- **Partitioning**: Divides a table into segments based on a date or integer column. It helps reduce the amount of data scanned when filtering.
  - *Example*: Partitioning by `DATE(tpep_pickup_datetime)`.
- **Clustering**: Sorts data based on specific columns within each partition. It improves performance for filter or aggregation queries on those columns.
  - *Example*: Clustering by `VendorID`.

---

## Homework Solutions

### Data for 2024 Yellow Taxi (Jan - June)

#### Question 1: Counting records
**Answer**: `20,332,093`
- Query: `SELECT count(*) FROM de-zoomcamp-12.homework3.yellow_tripdata_non_partitioned;`

#### Question 2: Data read estimation (Distinct PULocationIDs)
**Answer**: `0 MB for the External Table and 155.12 MB for the Materialized Table`
- Native tables store data in a way that allows BigQuery to estimate bytes before running, while external tables often show 0MB estimate (though they still scan data).

#### Question 3: Why are estimated bytes different?
**Answer**: `BigQuery is a columnar database, and it only scans the specific columns requested.`

#### Question 4: Counting zero fare trips
**Answer**: `8,333`
- Query: `SELECT count(*) FROM de-zoomcamp-12.homework3.yellow_tripdata_non_partitioned WHERE fare_amount = 0;`

#### Question 5: Best strategy for optimization
**Answer**: `Partition by tpep_dropoff_datetime and Cluster on VendorID`
- Since the query filters by date and orders by VendorID.

#### Question 6: Partition benefits (2024-03-01 to 2024-03-15)
**Answer**: `310.24 MB for non-partitioned vs 26.84 MB for partitioned`
- Partitioning significantly reduces the volume of data scanned by skipping irrelevant partitions.

#### Question 7: External table storage
**Answer**: `GCP Bucket`
- External tables do not store data in BigQuery storage; they point to files in GCS.

#### Question 8: Clustering best practices
**Answer**: `False`
- It's not always best practice. Clustering is most effective on tables larger than 1GB.

#### Question 9: Understanding table scans
**Answer**: `0 bytes`
- BigQuery uses metadata to return the total row count for native tables without scanning the data.

---

## BigQuery ML Example

Basic linear regression for predicting tip amount:
```sql
CREATE OR REPLACE MODEL `de-zoomcamp-12.homework3.tip_model`
OPTIONS (model_type='linear_reg', input_label_cols=['tip_amount']) AS
SELECT * FROM `de-zoomcamp-12.homework3.yellow_tripdata_partitioned`
WHERE fare_amount != 0 AND tip_amount IS NOT NULL;
```

## Resources

- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [BigQuery ML Introduction](https://cloud.google.com/bigquery/docs/bqml-introduction)
- [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp)
