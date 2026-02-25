"""dlt pipeline to ingest NYC taxi data from the DLT Hub analytics REST API."""

import dlt
from dlt.sources.rest_api import rest_api_resources
from dlt.sources.rest_api.typing import RESTAPIConfig


@dlt.source
def nyc_taxi_source() -> dlt.sources.DltSource:
    """NYC taxi rides from the DLT Hub analytics REST API."""
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api",
        },
        "resources": [
            {
                "name": "rides",
                "endpoint": {
                    # Response is a root-level JSON array
                    "data_selector": "$",
                    "params": {
                        "page": 1,
                    },
                    "paginator": {
                        "type": "page_number",
                        "base_page": 1,
                        "page_param": "page",
                        # No total_path — stop when the API returns an empty page
                        "total_path": None,
                        "stop_after_empty_page": True,
                    },
                },
            }
        ],
    }

    yield from rest_api_resources(config)


pipeline = dlt.pipeline(
    pipeline_name="taxi_pipeline",
    destination="duckdb",
    dataset_name="nyc_taxi_data",
    dev_mode=True,
    progress="log",
)


if __name__ == "__main__":
    load_info = pipeline.run(nyc_taxi_source())
    print(load_info)  # noqa: T201
