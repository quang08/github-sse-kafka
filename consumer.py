import logging
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, LongType, TimestampType
from pyspark.sql.functions import from_json, col, to_json, struct

def write_to_psql(batch_df, batch_id):
    try:
        batch_df.write \
            .format("jdbc") \
            .option("url", "jdbc:postgresql://postgres:5432/github_events") \
            .option("dbtable", "github_events") \
            .option("user", "postgres") \
            .option("password", "postgres") \
            .option("driver", "org.postgresql.Driver") \
            .option("stringtype", "unspecified") \
            .option("customTableQuery", """
                INSERT INTO github_events (id, event_type, created_at, actor_id, actor_login, repo_id, repo_name, event_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (id) DO NOTHING
            """) \
            .mode("append") \
            .save()
    except Exception as e:
        logging.error(f'Error writing batch ${batch_id} to PostgreSQL: ${e}', exc_info=True)

def main():
    logging.info("START")

    # Init Spark session
    spark = SparkSession.builder \
        .appName("GithubEventsProcessor") \
        .config("spark.jars", "/app/jars/postgresql-42.7.3.jar") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2") \
        .getOrCreate()

    # Define schema
    schema = StructType([
        StructField("id", StringType(), True),
        StructField("type", StringType(), True),
        StructField("created_at", StringType(), True),
        StructField("actor", StructType([
            StructField("id", IntegerType(), True),
            StructField("login", StringType(), True)
        ]), True),
        StructField("repo", StructType([
            StructField("id", IntegerType(), True),
            StructField("name", StringType(), True)
        ]), True),
        StructField("payload", StructType([
            StructField("before", StringType(), True),
            StructField("commits", StringType(), True),
            StructField("distinct_size", IntegerType(), True),
            StructField("head", StringType(), True),
            StructField("push_id", LongType(), True),
            StructField("ref", StringType(), True),
            StructField("repository_id", IntegerType(), True),
            StructField("size", IntegerType(), True)
        ]), True)
    ])

    # Read from Kafka
    kafka_df = spark.readStream \
        .format('kafka') \
        .option('kafka.bootstrap.servers', 'kafka-broker:9092') \
        .option('subscribe', 'github_events') \
        .load()

    # Parse JSON 
    parsed_df = kafka_df.selectExpr("CAST(value AS STRING) as json") \
        .select(from_json(col('json'), schema).alias('data')) \
        .select('data.*')

    # Flatten nested fields
    flattened_df = parsed_df.select(
        col("id"),
        col("type").alias("event_type"),
        col("created_at").cast(TimestampType()),
        col("actor.id").alias('actor_id'),
        col("actor.login").alias('actor_login'),
        col("repo.id").alias('repo_id'),
        col("repo.name").alias('repo_name'),
        to_json(struct("payload")).alias("event_data")  # Convert payload struct to JSON string
    )

    # Stream query
    query = flattened_df.writeStream \
        .foreachBatch(write_to_psql) \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    try:
        logging.basicConfig(level=logging.DEBUG)
        main()
    except KeyboardInterrupt:
        pass