import requests
import subprocess
import sys
import os
from utils.logging import logging

class AutoUpdater:
    def __init__(self):
        self.version_url = "https://raw.githubusercontent.com/CortexLM/sense/master/VERSION"
        self.local_version_file = "VERSION"
        self.local_version = None
        with open(self.local_version_file, "r") as f:
            self.local_version = f.read().strip()
        logging.success('Auto Updater ON')
        self.check_update()

    def restart(self):
        logging.debug('The Sense server is being restarted. It will be unavailable for a few minutes.')
        os.execv(sys.executable, ['python'] + sys.argv)

    def check_update(self):
        logging.debug('Checking for updates..')

        # Get the remote version from GitHub
        response = requests.get(self.version_url)
        remote_version = response.text.strip()

        if self.local_version != remote_version:
            # Versions are different, perform git pull
            subprocess.run(["git", "pull", "--force"], check=True)
            subprocess.run(["pip3", "install", "-r", "requirements.txt"], check=True)
            subprocess.run(["pip3", "install", "-e", "."], check=True)

            # Restart the Python script
            self.restart()
        else:
            logging.info(f"Current version {self.local_version} | Repo version {remote_version} -> No update needed.")