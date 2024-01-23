from loguru import logger
import sys
import os
import re

# Check if the file logs/latest.log exists
path = os.path.dirname(os.path.realpath(__file__))
if os.path.isfile('{path}/../logs/latest.log'):
    # Open the file in read mode
    with open('logs/latest.log', 'r') as file:
        # Read the first line
        first_line = file.readline()
        
        # Use a regular expression to extract the date
        match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})', first_line)
        
        # If a match is found
        if match:
            # Extract the date
            date_string = match.group(1)
            
            # Transform the filename using the date
            new_filename = f'logs/{date_string.replace(" ", "_").replace(":", "").replace(".", "")}.log'
            
            # Rename the file
            os.rename('logs/latest.log', new_filename)

logger.add("logs/latest.log", level="DEBUG", format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS zz}</green> | <level>{level: <8}</level> | <yellow>Line {line: >4} ({file}):</yellow> <b>{message}</b>", colorize=False, backtrace=True, diagnose=True)

logging = logger
