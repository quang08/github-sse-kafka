import logging
import json
from pprint import pformat
from requests_sse import EventSource

def main():
    logging.info("START")

    with EventSource("http://github-firehose.libraries.io/events", timeout=30) as event_src:
        for event in event_src:
            value = json.loads(event.data)
            key = value['id'] # key for kafka
            logging.info("Got: %s", pformat(value))

    
if __name__ == "__main__":
    try:
        logging.basicConfig(level="DEBUG")
        main()
    except KeyboardInterrupt:
        pass