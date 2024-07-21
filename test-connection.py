import logging
from pyspark.sql import SparkSession

def test_db_connection():
    logging.info("START")

    # Init Spark session
    spark = SparkSession.builder \
        .appName("PostgresConnectionTest") \
        .config("spark.jars", "/app/jars/postgresql-42.7.3.jar") \
        .getOrCreate()

    # Test DB connection
    jdbc_url = "jdbc:postgresql://postgres:5432/github_events"
    connection_properties = {
        "user": "postgres",
        "password": "postgres",
        "driver": "org.postgresql.Driver"
    }

    try:
        df = spark.read.jdbc(url=jdbc_url, table="(SELECT 1) AS test", properties=connection_properties)
        df.show()
        logging.info("Database connection test successful")
    except Exception as e:
        logging.error(f"Database connection test failed: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_db_connection()