# Module 7 Homework Answers

This file summarizes the final answers for all 6 questions in
[homework.md](homework.md).

## Final Answers

1. Q1. Redpanda version
	- `v25.3.9`

2. Q2. Time to send data to `green-trips`
	- Measured runtime on this machine: about `3s`
	- Homework option to submit: `10 seconds`

3. Q3. Trips with `trip_distance > 5`
	- `8506`

4. Q4. 5-minute tumbling window (max `PULocationID`)
	- `74`

5. Q5. 5-minute session window (longest session size)
	- `81`

6. Q6. 1-hour tumbling window (largest total tip hour)
	- `2025-10-16 18:00:00`

## Notes

- Q3 was computed from the Kafka topic with `auto_offset_reset='earliest'`.
- Q4-Q6 were computed with PyFlink jobs and PostgreSQL sink tables.
