import logging
import json
from pprint import pformat
from requests_sse import EventSource
from quixstreams import Application

def handle_stats(msg):
    stats = json.loads(msg)
    logging.info("STATS: %s", pformat(stats))

def main():
    logging.info("START")

    app = Application(
            broker_address='kafka-broker:9092',
            loglevel="DEBUG",
            producer_extra_config={
                # measure  
                "statistics.interval.ms": 3 * 100, # collect stats such as messages sent
                "stats_cb": handle_stats, # processes and logs stats
                "debug": "msg", # log message related information
                # tuning
                "linger.ms": 500, # amount of time to wait and collect message in a batch before sending the batch (balance between low latency and high throughput)
                "batch.size": 1024 * 1024, # in bytes: 1 MB
                "compression.type": "gzip", # readable string type like json can compress well and would help save storage cost, bandwdith: trade off CPU time to compress, for better network usage
            }
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