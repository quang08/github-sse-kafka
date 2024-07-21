# ETL Pipeline for Github Firehose API
ETL (Extract, Transform, Load) pipeline using various technologies to extract data from the [GitHub Firehose API](https://github-firehose.libraries.io/), transform it, and load it into a PostgreSQL database.

## Design:
![design](https://github.com/user-attachments/assets/4f6eb644-afe4-4d38-870b-a371551f3512)

## Source:
- **[GitHub Firehose API](https://github-firehose.libraries.io/)**: Provides a real-time stream of public events from GitHub.

## Technologies Used:
- **PostgreSQL**: Stores the transformed data from the GitHub Firehose API.
- **Kafka**: Serves as the message queue.
- **Spark**: Used for processing and transforming the data in real-time.
- **Docker**: Orchestrates services.

## Libraries Used:
- **[Quix](https://quix.io/docs/quix-streams/api-reference/kafka.html#consumerconsumer_group_metadata)**: Quix is a library for building and managing streaming data pipelines. It simplifies the interaction with Kafka, providing a high-level API for producing and consuming messages.
- **requests-sse**: Python library for handling Server-Sent Events (SSE) with the Requests library.
- **PySpark**: Python API for Spark, used for building and running Spark applications.

## Tweaks: Configuration for Kafka Performance

The producer in this project is configured with external settings to optimize Kafka performance, especially when dealing with a high-traffic API like the GitHub Firehose API. The configurations include:

- **Statistics Interval**: statistics.interval.ms is set to collect performance statistics at regular intervals.
- **Batch Size**: batch.size is set to 1MB to allow efficient batching of messages, balancing between low latency and high throughput.
- **Linger Time**: linger.ms is set to 500ms to wait and collect messages before sending them in a batch, further optimizing throughput.
- **Compression**: compression.type is set to gzip to compress message data, saving storage and bandwidth at the cost of additional CPU usage for compression and decompression.

## Setup and Usage
### Prerequisites:
- Docker
- Docker Compose

### Steps:
1. Build and Run the Docker containers:
```sh
    docker-compose up --build
```

2.	Verify Data Ingestion:
```sh
    docker-compose exec postgres psql -U postgres -d github_events
```
```sh
    SELECT * FROM github_events;
```

## Scripts Description:
- main.py: Extracts data from the GitHub Firehose API, transforms it, and produces messages to Kafka.
- consumer.py: Consumes messages from Kafka, transforms them, and loads them into PostgreSQL.
- entrypoint.sh: Determines whether to run the producer or consumer based on the RUN_MODE environment variable.