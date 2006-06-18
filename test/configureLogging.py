from wuja.log import setupLogging

import logging

# Configure logging: (needs to be done before importing our modules)
confFileLocations = ["./logging.conf"]
setupLogging(confFileLocations)

logger = logging.getLogger()
logger.debug("Configured logging.")

