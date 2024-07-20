import logging
import json
import psycopg2
from quixstreams import Application

def transform_data(data):
    return {
        'id': data['id'],
        'event_type': data['type'],
        'event_data': json.dumps(data)
    }

def push_to_postgres(data, conn):
    logging.debug("Pushing to Postgres: %s", data)
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO github_events (id, event_type, event_data) 
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """, (data['id'], data['event_type'], data['event_data'])
        )

    conn.commit()

def main():
    logging.info("START")
    # establish connection with postgres
    conn = psycopg2.connect(
        dbname = "github_events",
        user = 'postgres',
        password = 'postgres',
        host = 'postgres' #?
    )

    # connect to kafka
    app = Application(
        broker_address='kafka-broker:9092',
        loglevel="DEBUG",
        consumer_group="github_events_group", #?
        auto_offset_reset="latest",
    )
    
    # create kafka consumer and sub to topic
    with app.get_consumer() as consumer:
        consumer.subscribe(["github_events"])

        while True:
            msg = consumer.poll(1)

            if msg is None:
                logging.debug("Waiting for messages...")
            elif msg.error() is not None:
                raise Exception(msg.error())
            else:
                key = msg.key().decode('utf8')
                value = json.loads(msg.value())
                offset = msg.offset()

                logging.debug(f'Consumed: {offset} {key} {value}')

                transformed_data = transform_data(value)
                push_to_postgres(transformed_data, conn)
                consumer.store_offsets(msg)    

if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.DEBUG)
        main()
    except KeyboardInterrupt:
        pass