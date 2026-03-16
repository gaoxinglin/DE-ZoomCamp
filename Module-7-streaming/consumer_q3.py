import json
from kafka import KafkaConsumer

TOPIC = "green-trips"
BOOTSTRAP_SERVERS = ["localhost:9092"]


def main() -> None:
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        group_id=None,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        consumer_timeout_ms=7000,
    )

    gt_5_count = 0
    total_messages = 0

    for message in consumer:
        payload = message.value
        total_messages += 1

        trip_distance = payload.get("trip_distance")
        try:
            if float(trip_distance) > 5.0:
                gt_5_count += 1
        except (TypeError, ValueError):
            continue

    consumer.close()

    print(f"Total messages consumed: {total_messages}")
    print(f"Trips with trip_distance > 5: {gt_5_count}")


if __name__ == "__main__":
    main()
