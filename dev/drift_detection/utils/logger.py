import logging
import logstash
import sys

# Define logstash host
logstash_host = 'localhost'

# Define logger 
logger = logging.getLogger('drift_detection')
logger.setLevel(logging.INFO)

# Define formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Define handlers
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

logstash_handler = logstash.LogstashHandler(logstash_host, 5044, version=1)
logstash_handler.setLevel(logging.INFO)

# Add handlers
logger.addHandler(console_handler)
logger.addHandler(logstash_handler)