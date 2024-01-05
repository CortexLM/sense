from .config import SubCliConfig
import fire
import os
import json
from pathlib import Path
class CLI(object):
    def init(self):
        # Get the current working directory where the user executed the command
        current_dir = os.getcwd()

        # Path to the VERSION file in the current directory
        version_file_path = os.path.join(current_dir, 'VERSION')

        # Determine the user's home directory
        user_dir = str(Path.home())

        # Path to the .sense directory in the user's home directory
        sense_dir = os.path.join(user_dir, '.sense')

        # Path to the init.json file within the .sense directory
        init_json_path = os.path.join(sense_dir, 'init.json')
        os.makedirs(sense_dir, exist_ok=True)
        with open(init_json_path, 'a') as file:
            pass
        if os.path.isfile(version_file_path):
            # If the VERSION file exists in the current directory, create the init.json file
            global_path = current_dir
            data = {'path': global_path}
            with open(init_json_path, 'w') as file:
                json.dump(data, file)
                print("\033[94mSense has been initialized to :", global_path, "\033[0m")
        else:
            print("\033[91mYou are not on the Sense folder. It's usually /srv/sense folder.\033[0m")

def run():
    cli = CLI()
    cli.config = SubCliConfig()
    fire.Fire(cli, name='sense')