FROM apache/flink:1.20.0-scala_2.12-java17

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip wget ca-certificates && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    pip3 install --no-cache-dir apache-flink==1.20.0 && \
    wget -q -O /opt/flink/lib/flink-sql-connector-kafka-3.3.0-1.20.jar https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/3.3.0-1.20/flink-sql-connector-kafka-3.3.0-1.20.jar && \
    wget -q -O /opt/flink/lib/flink-connector-jdbc-3.3.0-1.20.jar https://repo1.maven.org/maven2/org/apache/flink/flink-connector-jdbc/3.3.0-1.20/flink-connector-jdbc-3.3.0-1.20.jar && \
    wget -q -O /opt/flink/lib/postgresql-42.7.4.jar https://repo1.maven.org/maven2/org/postgresql/postgresql/42.7.4/postgresql-42.7.4.jar && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

USER flink
