# docker-workshop
Workshop Codespaces

Homework: Process and Code

Q1:  docker run -it --entrypoint
=bash --rm python:3.13.11-slim
root@f58cecabecaa:/# python -V
Python 3.13.11

Q2: The hostname is db (the service name) and the port is 5432 (the internal container port).
Within a Docker network, services communicate using their service names and internal ports, regardless of the port mapping to the host machine.

Q3: SELECT count(1) 
    FROM
        green_tripdata
    WHERE
        lpep_pickup_datetime >= '2025-11-01' 
        AND lpep_pickup_datetime < '2025-12-01'
        AND trip_distance <= 1;

Q4: SELECT
        CAST(lpep_pickup_datetime AS DATE) AS pickup_day,
        MAX(trip_distance) AS max_distance
    FROM
        green_tripdata
    WHERE
        trip_distance < 100
    GROUP BY
        1
    ORDER BY
        max_distance DESC
    LIMIT 1;

Q5: SELECT
        z."Zone",
        SUM(t.total_amount) AS total_sum
    FROM
        green_tripdata t
    JOIN
        taxi_zone_lookup z ON t."PULocationID" = z."LocationID"
    WHERE
        CAST(t.lpep_pickup_datetime AS DATE) = '2025-11-18'
    GROUP BY
        1
    ORDER BY
        total_sum DESC
    LIMIT 1;

Q6: SELECT
        zdo."Zone" AS dropoff_zone,
        MAX(t.tip_amount) AS max_tip
    FROM
        green_tripdata t
    JOIN
        taxi_zone_lookup zpu ON t."PULocationID" = zpu."LocationID"
    JOIN
        taxi_zone_lookup zdo ON t."DOLocationID" = zdo."LocationID"
    WHERE
        zpu."Zone" = 'East Harlem North'
        AND t.lpep_pickup_datetime >= '2025-11-01' 
        AND t.lpep_pickup_datetime < '2025-12-01'
    GROUP BY
        1
    ORDER BY
        max_tip DESC
    LIMIT 1;

Q7: terraform init, terraform apply -auto-approve, terraform destroy (terraform plan is preview only)