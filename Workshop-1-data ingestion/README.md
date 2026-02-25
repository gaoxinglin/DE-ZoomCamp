# Workshop 1: Data Ingestion with dlt

This workshop covers building an AI-assisted data pipeline using [dlt (data load tool)](https://dlthub.com/), loading NYC Yellow Taxi data from a custom paginated REST API into DuckDB, and querying the results.

## Overview

In this workshop, we learned how to:
- Build a REST API source pipeline with dlt from scratch (no scaffold)
- Configure pagination for an API that stops on empty pages
- Use the **dlt MCP Server** with an AI assistant (GitHub Copilot / Cursor / Claude) to build and debug pipelines
- Load paginated JSON data into DuckDB as a local data warehouse
- Inspect and query loaded data using the dlt Dashboard, DuckDB, and marimo notebooks

## Files & Scripts

| File | Description |
|------|-------------|
| [taxi-pipeline/taxi_pipeline.py](taxi-pipeline/taxi_pipeline.py) | Main dlt pipeline: REST API source → DuckDB |
| [taxi-pipeline/taxi_pipeline.duckdb](taxi-pipeline/taxi_pipeline.duckdb) | Local DuckDB database with loaded taxi data |
| [dlt_Pipeline_Overview.ipynb](dlt_Pipeline_Overview.ipynb) | Workshop overview notebook |
| [github_pipeline.py](github_pipeline.py) | Demo pipeline for GitHub API data |
| [open_library_pipeline.py](open_library_pipeline.py) | Demo pipeline for Open Library API |

## Data Source

| | |
|---|---|
| **Base URL** | `https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api` |
| **Format** | Paginated JSON |
| **Page Size** | 1,000 records per page |
| **Pagination** | Stop when an empty page is returned |

## Pipeline Design

The pipeline uses dlt's `rest_api_resources` with a `page_number` paginator configured to stop on empty pages:

```python
@dlt.source
def nyc_taxi_source() -> dlt.sources.DltSource:
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api",
        },
        "resources": [
            {
                "name": "rides",
                "endpoint": {
                    "data_selector": "$",
                    "params": {"page": 1},
                    "paginator": {
                        "type": "page_number",
                        "base_page": 1,
                        "page_param": "page",
                        "total_path": None,
                        "stop_after_empty_page": True,
                    },
                },
            }
        ],
    }
    yield from rest_api_resources(config)
```

## Setup

### 1. Install dlt
```bash
pip install "dlt[duckdb]"
```

### 2. Set up dlt MCP Server (VS Code Copilot)
Create `.vscode/mcp.json`:
```json
{
  "servers": {
    "dlt": {
      "command": "uv",
      "args": [
        "run", "--with", "dlt[duckdb]", "--with", "dlt-mcp[search]",
        "python", "-m", "dlt_mcp"
      ]
    }
  }
}
```

### 3. Run the pipeline
```bash
cd taxi-pipeline
python taxi_pipeline.py
```

### 4. Inspect with dlt Dashboard
```bash
dlt pipeline taxi_pipeline show
```

---

## Homework Solutions

### Question 1: What is the start date and end date of the dataset?

**Answer**: `2009-06-01 to 2009-07-01`

Query the `MIN` and `MAX` of `trip_pickup_date_time` in the `rides` table using dlt MCP.

```sql
SELECT 
    MIN(trip_pickup_date_time)::DATE AS start_date, 
    MAX(trip_pickup_date_time)::DATE AS end_date
FROM nyc_taxi_data.rides;
```

| start_date | end_date |
|---|---|
| 2009-06-01 | 2009-07-01 |

---

### Question 2: What proportion of trips are paid with credit card?

**Answer**: `26.66%`

Group by `payment_type` and calculate each type's percentage of total trips. Credit card records are stored as `"Credit"` (case-sensitive).

```sql
SELECT 
    payment_type,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM nyc_taxi_data.rides
GROUP BY payment_type
ORDER BY count DESC;
```

| payment_type | count | percentage |
|---|---|---|
| CASH | 7235 | 72.35% |
| **Credit** | **2666** | **26.66%** |
| Cash | 97 | 0.97% |
| No Charge | 1 | 0.01% |
| Dispute | 1 | 0.01% |

> Note: `CASH` and `Cash` are the same payment type with inconsistent casing. Combined, cash payments account for 73.32%.

---

### Question 3: What is the total amount of money generated in tips?

**Answer**: `$6,063.41`

Sum the `tip_amt` column. Note that this dataset uses `tip_amt` instead of `tip_amount`.

```sql
SELECT ROUND(SUM(tip_amt), 2) AS total_tips
FROM nyc_taxi_data.rides;
```

| total_tips |
|---|
| 6063.41 |

---

## Key Takeaways

- **dlt MCP Server** gives the AI assistant direct access to pipeline metadata and docs, making debugging much faster
- For custom APIs without an official scaffold, just include the API details in your prompt and the AI can build the full pipeline
- `stop_after_empty_page` is the correct pagination setting for APIs that signal the end of data with an empty response
- DuckDB works great as a lightweight local data warehouse; use `dlt pipeline show` to inspect your data visually

## Resources

| | |
|---|---|
| dlt Documentation | [dlthub.com/docs](https://dlthub.com/docs) |
| dlt Dashboard Docs | [dlthub.com/docs/general-usage/dashboard](https://dlthub.com/docs/general-usage/dashboard) |
| marimo + dlt Guide | [dlthub.com/docs/general-usage/dataset-access/marimo](https://dlthub.com/docs/general-usage/dataset-access/marimo) |
| Homework Link | [dlt_homework.md](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/workshops/dlt/dlt_homework.md) |
