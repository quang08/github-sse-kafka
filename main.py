import logging
import json
from pprint import pformat
from requests_sse import EventSource
from quixstreams import Application

def main():
    logging.info("START")

    app = Application(
            broker_address='localhost:19092',
            loglevel="DEBUG"
        )

    with (
            app.get_producer() as producer,
            EventSource(
              "http://github-firehose.libraries.io/events", timeout=30
            ) as event_src, 
         ):
            for event in event_src:
                value = json.loads(event.data) 
                key = value['id'] # key for kafka
                logging.debug("Got: %s", pformat(value))

                # send to kafka
                producer.produce(
                     topic='github_events', 
                     key=key,
                     value=json.dumps(value), #serialize for kafka
                )

    
if __name__ == "__main__":
    try:
        logging.basicConfig(level="INFO")
        main()
    except KeyboardInterrupt:
        pass