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

**Logic**:
The `--select` flag tells dbt which model to run. By default, it runs only the model you name.

**Example**:
```bash
dbt run --select int_trips_unioned
```
This runs only `int_trips_unioned`.

**Answer**: `int_trips_unioned` only

### Question 2: dbt Tests

**Logic**:
`accepted_values` checks if a column has only allowed values. If a new value like `6` appears, the test finds it and reports an error.

**Result**:
dbt will fail the test. It will return a non-zero exit code.

**Answer**: dbt will fail the test, returning a non-zero exit code

### Question 3: Counting Records in `fct_monthly_zone_revenue`

**Logic**:
This table summarizes trips by month and zone. After building the models, count the rows in the final table.

**SQL**:
```sql
SELECT count(*) FROM `your_dataset.fct_monthly_zone_revenue`;
```

**Answer**: 12,998

### Question 4: Best Zone for Green Taxis (2020)

**Logic**:
Filter the revenue table for 'Green' taxis and the year 2020. Sum the revenue for each zone and find the highest one.

**SQL**:
```sql
SELECT 
    pickup_zone,
    SUM(revenue_monthly_total_amount) AS total_revenue
FROM `your_dataset.fct_monthly_zone_revenue`
WHERE service_type = 'Green' 
  AND year = 2020
GROUP BY 1
ORDER BY 2 DESC
LIMIT 1;
```

**Answer**: East Harlem North

### Question 5: Green Taxi Trips (October 2019)

**Logic**:
Filter the table for 'Green' taxis in October 2019. Sum the counts for that month.

**SQL**:
```sql
SELECT 
    SUM(total_monthly_trips) AS total_trips
FROM `your_dataset.fct_monthly_zone_revenue`
WHERE service_type = 'Green'
  AND year = 2019
  AND month = 10;
```

**Answer**: 421,509

### Question 6: Staging Model for FHV Data

**Logic**:
Create a staging view for FHV data. You must:
1. Use the `source` macro.
2. Remove rows where `dispatching_base_num` is empty.
3. Change ID columns to integers and date columns to timestamps.

**dbt SQL**:
```sql
{{ config(materialized='view') }}

with fhv_data as (
    select * from {{ source('staging', 'fhv_tripdata') }}
)
select
    dispatching_base_num,
    cast(pulocationid as integer) as pickup_location_id,
    cast(dolocationid as integer) as dropoff_location_id,
    cast(pickup_datetime as timestamp) as pickup_datetime,
    cast(dropoff_datetime as timestamp) as dropoff_datetime,
    sr_flag
from fhv_data
where dispatching_base_num is not null
```

**Answer**: 43,244,693

---

## Resources

- [dbt Docs](https://docs.getdbt.com/)
- [dbt-duckdb Info](https://github.com/jwills/dbt-duckdb)
- [Zoomcamp Course](https://github.com/DataTalksClub/data-engineering-zoomcamp)
