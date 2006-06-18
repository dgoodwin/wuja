import logging
import logging.config
from os.path import expanduser, exists, abspath

def setupLogging(confFileLocations):
    actualLoggingConfLocation = None
    for location in confFileLocations:
        if exists(expanduser(location)):
            actualLoggingConfLocation = location
            break

    if actualLoggingConfLocation != None:
        logging.config.fileConfig(expanduser(location))
    else:
        print("Unable to locate logging configuration in the following locations:")
        for location in confFileLocations:
            print("   " + abspath(expanduser(location)))

