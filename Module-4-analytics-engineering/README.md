# Module 4: Analytics Engineering with dbt

This module is about Analytics Engineering using [dbt](https://www.getdbt.com/). We learn how to turn raw data into clean tables for analysis.

## Overview

In this module, we learned how to:
- Make SQL models with dbt.
- Use the Medallion Architecture (Staging, Intermediate, and Fact tables).
- Use Jinja to make SQL dynamic.
- Write tests to check data quality.
- See how tables connect (lineage).

## Setup

This project uses [DuckDB](https://duckdb.org/) and `dbt-duckdb`. You can see the settings in [pyproject.toml](pyproject.toml).

How to start:
1. Put your taxi data in the [data/](data/) folder.
2. Start dbt:
   ```bash
   dbt init taxi_rides_ny
   ```
3. Set up your `profiles.yml` to use DuckDB.

---

## Homework Solutions

Check [homework-module4.md](homework-module4.md) for the questions.

### Question 1: dbt Lineage and Execution

**Question**: When running `dbt run --select int_trips_unioned`, what happens?

**Logic**:
The `--select` flag tells dbt which model to run. By default, it runs only the model you name, without upstream or downstream dependencies unless explicitly specified with `+` modifiers.

**Example**:
```bash
dbt run --select int_trips_unioned
```
This runs only `int_trips_unioned`.

**Answer**: `int_trips_unioned` only

---

### Question 2: dbt Tests

**Question**: What happens when a new payment type appears that wasn't in the `accepted_values` test?

**Logic**:
`accepted_values` checks if a column has only allowed values. If a new value like `6` appears, the test finds it and reports an error.

**Result**:
dbt will fail the test. It will return a non-zero exit code.

**Answer**: dbt will fail the test, returning a non-zero exit code

---

### Question 3: Counting Records in `fct_monthly_zone_revenue`

**Question**: What is the count of records in the `fct_monthly_zone_revenue` model?

**Solution Steps**:
1. Make sure all upstream models are built
2. Build the model:
   ```bash
   dbt build --select fct_monthly_zone_revenue
   ```
3. Query the total count in the database

**SQL**:
```sql
-- For DuckDB
SELECT count(*) FROM fct_monthly_zone_revenue;

-- For BigQuery
SELECT count(*) FROM `your_dataset.fct_monthly_zone_revenue`;
```

**Common Issues**:
- Make sure you use the right target (dev or prod)
- DuckDB and BigQuery have different query syntax

**Answer**: 12,184

---

### Question 4: Best Zone for Green Taxis (2020)

**Question**: Which zone had the highest revenue for Green taxis in 2020?

**Solution Steps**:
1. Query the `fct_monthly_zone_revenue` table
2. Filter: `service_type = 'Green'` and year = 2020
3. Group by `pickup_zone` and sum the total revenue
4. Order by revenue DESC and take the top result

**SQL (DuckDB)**:
```sql
SELECT 
    pickup_zone,
    SUM(revenue_monthly_total_amount) AS total_revenue
FROM fct_monthly_zone_revenue
WHERE service_type = 'Green' 
  AND revenue_month >= '2020-01-01' 
  AND revenue_month < '2021-01-01'
GROUP BY pickup_zone
ORDER BY total_revenue DESC
LIMIT 1;
```

**SQL (BigQuery)**:
```sql
SELECT 
    pickup_zone,
    SUM(revenue_monthly_total_amount) AS total_revenue
FROM `your_dataset.fct_monthly_zone_revenue`
WHERE service_type = 'Green' 
  AND EXTRACT(YEAR FROM revenue_month) = 2020
GROUP BY 1
ORDER BY 2 DESC
LIMIT 1;
```

**Common Issues**:
- Need to handle date filtering correctly
- DuckDB and BigQuery use different date functions

**Answer**: East Harlem North

---

### Question 5: Green Taxi Trips (October 2019)

**Question**: What is the total number of trips for Green taxis in October 2019?

**Solution Steps**:
1. Query the `total_monthly_trips` field from `fct_monthly_zone_revenue`
2. Filter for Green taxis in October 2019
3. Sum up trips across all zones

**SQL (DuckDB)**:
```sql
SELECT 
    SUM(total_monthly_trips) AS total_trips
FROM fct_monthly_zone_revenue
WHERE service_type = 'Green'
  AND revenue_month = '2019-10-01';
```

**SQL (BigQuery)**:
```sql
SELECT 
    SUM(total_monthly_trips) AS total_trips
FROM `your_dataset.fct_monthly_zone_revenue`
WHERE service_type = 'Green'
  AND revenue_month = '2019-10-01';
```

**Answer**: 384,624

---

### Question 6: Staging Model for FHV Data

**Question**: Count of records in `stg_fhv_tripdata` where `dispatching_base_num` is NOT NULL for 2019?

**Solution Steps**:

#### Step 1: Download FHV Data
Found that the project didn't have FHV (For-Hire Vehicle) data. Need to update `ingest.py` to download it:

```python
# Update ingest.py to add FHV data download
for taxi_type in ["yellow", "green", "fhv"]:
    download_and_convert_files(taxi_type)
```

Then run:
```bash
uv run python taxi_rides_ny/ingest.py
```

#### Step 2: Fix YAML Configuration
Got a syntax error in `schem.yml`:
```
Runtime Error Syntax error near line 96
```

**Root Cause**: Added `sources` format under the `models` list by mistake, which broke YAML parsing.

**Solution**: Remove the wrong `- name: staging` block and add proper `stg_fhv_tripdata` model definition.

#### Step 3: Configure Data Source
Add FHV data source in `sources.yml`:
```yaml
sources:
  - name: raw
    tables:
      - name: fhv_tripdata
        description: Raw for-hire vehicle (FHV) trip records
        loaded_at_field: pickup_datetime
```

#### Step 4: Create Staging Model
Create `stg_fhv_tripdata.sql`:
```sql
{{
    config(
        materialized='view'
    )
}}

with tripdata as 
(
  select *
  from {{ source('raw','fhv_tripdata') }}
)
select
    -- identifiers
    cast(dispatching_base_num as string) as dispatching_base_num,
    cast(pulocationid as integer) as pickup_location_id,
    cast(dolocationid as integer) as dropoff_location_id,

    -- timestamps
    cast(pickup_datetime as timestamp) as pickup_datetime,
    cast(dropoff_datetime as timestamp) as dropoff_datetime,
    
    -- trip info
    sr_flag,
    affiliated_base_number
from tripdata
```

#### Step 5: Load Data into DuckDB
Got an error:
```
Catalog Error: Table with name fhv_tripdata does not exist!
```

**Root Cause**: The DuckDB database doesn't have the `fhv_tripdata` table yet.

**Solution**: Update `ingest.py` to automatically load downloaded Parquet files into DuckDB's `prod` schema:
```python
for taxi_type in ["yellow", "green", "fhv"]:
    con.execute(f"""
        CREATE OR REPLACE TABLE prod.{taxi_type}_tripdata AS
        SELECT * FROM read_parquet('data/{taxi_type}/*.parquet', union_by_name=true)
    """)
```

#### Step 6: Run dbt Build
```bash
dbt build --select stg_fhv_tripdata
```

Got a test failure:
```
FAIL 3 not_null_stg_fhv_tripdata_dispatching_base_num
Got 3 results, configured to fail if != 0
```

This error shows that 3 records have NULL `dispatching_base_num`. This is what the question asks us to filter out.

#### Step 7: Count Final Results

**Common Issues**:
- First query returned **58,206,741** records - way too high!
- **Reason**: `ingest.py` downloaded both 2019 and 2020 data, but the question only asks for 2019
- After filtering for 2019: got **43,244,696** records
- Question asks to filter out `dispatching_base_num IS NULL` records (3 total)
- Final result: 43,244,696 - 3 = **43,244,693**

**Final Verification SQL**:
```sql
-- Count 2019 records where dispatching_base_num IS NOT NULL
SELECT count(*) 
FROM stg_fhv_tripdata 
WHERE pickup_datetime >= '2019-01-01' 
  AND pickup_datetime < '2020-01-01'
  AND dispatching_base_num IS NOT NULL;
```

**Key Issues Summary**:
1. 📦 **Missing Data**: Project only has Yellow and Green by default - need to download FHV manually
2. 📝 **YAML Syntax Errors**: Easy to mix up `schem.yml` and `sources.yml` formats
3. 🗄️ **Table Not Found**: dbt only transforms data - raw data must be loaded into database first
4. 📅 **Year Range**: Script downloads multiple years by default, but questions usually ask for one year
5. 🚫 **NULL Handling**: Raw data has some NULL records that need filtering
6. 🔄 **dev vs prod**: Watch out for dbt target config - make sure you query the right schema

**Answer**: 43,244,693

---

## Resources

- [dbt Docs](https://docs.getdbt.com/)
- [dbt-duckdb Info](https://github.com/jwills/dbt-duckdb)
- [Zoomcamp Course](https://github.com/DataTalksClub/data-engineering-zoomcamp)
