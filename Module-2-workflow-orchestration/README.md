# Module 2: Workflow Orchestration with Kestra

This module covers workflow orchestration using [Kestra](https://kestra.io/), an open-source orchestration platform.

## Overview

In this module, we learned how to:
- Build ETL pipelines with Kestra flows
- Use variables and expressions for dynamic workflows
- Load data into PostgreSQL and BigQuery
- Schedule workflows with triggers
- Use backfill for historical data processing

## Flows

| Flow | Description |
|------|-------------|
| `01_hello_world.yaml` | Basic hello world flow |
| `02_python.yaml` | Python script execution |
| `03_getting_started_data_pipeline.yaml` | Simple data pipeline |
| `04_postgres_taxi.yaml` | Load taxi data to PostgreSQL |
| `05_postgres_taxi_scheduled.yaml` | Scheduled PostgreSQL loading |
| `06_gcp_kv.yaml` | GCP key-value configuration |
| `07_gcp_setup.yaml` | GCP setup flow |
| `08_gcp_taxi.yaml` | Load taxi data to BigQuery |
| `09_gcp_taxi_scheduled.yaml` | Scheduled BigQuery loading |
| `10_chat_without_rag.yaml` | Chat without RAG |
| `11_chat_with_rag.yaml` | Chat with RAG |

## How to Run

1. Start Kestra with Docker Compose:
```bash
docker compose up -d
```

2. Open Kestra UI at http://localhost:8080

3. Import flows from the `flows/` directory

---

## Homework Solutions

### Assignment

The task is to extend existing flows to include data for the year 2021.

**How to do it:**
- Use the backfill feature in scheduled flow (`09_gcp_taxi_scheduled.yaml`)
- Set time period: `2021-01-01` to `2021-07-31`
- Run for both `yellow` and `green` taxi data

---

### Question 1: Uncompressed File Size

**Question:** Within the execution for Yellow Taxi data for year 2020 and month 12, what is the uncompressed file size of `yellow_tripdata_2020-12.csv`?

**How to solve:**
1. Run `04_postgres_taxi.yaml` or `08_gcp_taxi.yaml`
2. Set inputs: `taxi=yellow`, `year=2020`, `month=12`
3. After execution, check the `extract` task output
4. Look at the file size in the Outputs tab

**Answer:** `128.3 MiB`

---

### Question 2: Rendered Variable Value

**Question:** What is the rendered value of the variable `file` when `taxi=green`, `year=2020`, `month=04`?

**How to solve:**

Look at the variable definition in the flow:
```yaml
variables:
  file: "{{inputs.taxi}}_tripdata_{{inputs.year}}-{{inputs.month}}.csv"
```

Replace the inputs:
- `{{inputs.taxi}}` → `green`
- `{{inputs.year}}` → `2020`
- `{{inputs.month}}` → `04`

**Answer:** `green_tripdata_2020-04.csv`

---

### Question 3: Yellow Taxi Rows for 2020

**Question:** How many rows are there for Yellow Taxi data for all CSV files in year 2020?

**How to solve:**
1. Run the flow for all 12 months of 2020 with `taxi=yellow`
2. Use backfill or run manually for each month
3. Query the database:
```sql
SELECT COUNT(*) FROM yellow_tripdata 
WHERE filename LIKE '%2020%';
```

**Answer:** `24,648,499`

---

### Question 4: Green Taxi Rows for 2020

**Question:** How many rows are there for Green Taxi data for all CSV files in year 2020?

**How to solve:**
1. Run the flow for all 12 months of 2020 with `taxi=green`
2. Query the database:
```sql
SELECT COUNT(*) FROM green_tripdata 
WHERE filename LIKE '%2020%';
```

**Answer:** `1,734,051`

---

### Question 5: Yellow Taxi Rows for March 2021

**Question:** How many rows are there for Yellow Taxi data for March 2021?

**How to solve:**
1. Run the flow with `taxi=yellow`, `year=2021`, `month=03`
2. Query the database:
```sql
SELECT COUNT(*) FROM yellow_tripdata 
WHERE filename LIKE '%2021-03%';
```

**Answer:** `1,925,152`

---

### Question 6: Timezone Configuration

**Question:** How would you configure the timezone to New York in a Schedule trigger?

**How to solve:**

Look at the Kestra documentation for Schedule triggers. The correct way is:

```yaml
triggers:
  - id: schedule
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 9 1 * *"
    timezone: "America/New_York"
```

**Answer:** Add a `timezone` property set to `America/New_York` in the Schedule trigger configuration

---

## Useful Commands

```bash
# Start Kestra
docker compose up -d

# Stop Kestra
docker compose down

# View logs
docker compose logs -f
```

## Resources

- [Kestra Documentation](https://kestra.io/docs)
- [NYC TLC Data](https://github.com/DataTalksClub/nyc-tlc-data/releases)
- [Data Engineering Zoomcamp](https://github.com/DataTalksClub/data-engineering-zoomcamp)
