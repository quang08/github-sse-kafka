import logging
from requests_sse import EventSource

def main():
    logging.info("START")

    with EventSource("http://github-firehose.libraries.io/events", timeout=30) as event_src:
        for event in event_src:
            logging.info("Got: %s", event)

    
if __name__ == "__main__":
    logging.basicConfig(level="DEBUG")
    main()