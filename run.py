import argparse
import time
from utils.autoupdater import AutoUpdater
from subprocess import Popen, PIPE, run
import sys
import subprocess

def check_and_install_pm2():
    try:
        # Check if pm2 is already installed
        run(["pm2", "--version"], stdout=PIPE, stderr=PIPE, check=True)
        print("pm2 is already installed.")
    except:
        try:
            # Check if npm is installed
            run(["npm", "--version"], stdout=PIPE, stderr=PIPE, check=True)
            print("npm is already installed.")
        except subprocess.CalledProcessError:
            # If neither pm2 nor npm is installed, install nvm, npm, and pm2
            print("Neither pm2 nor npm is installed. Installing nvm, npm, and pm2...")

            # Install nvm
            run(["curl", "-o-", "https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh", "|", "bash"])
            run(['export', 'NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"'])
            run(['[', '-s', '$NVM_DIR/nvm.sh', ']', '&&', '.', '$NVM_DIR/nvm.sh'])
            run(["nvm", "install", "--lts"])

            # Install npm and pm2
            run(["npm", "install", "pm2", "-g"])

            print("Installation completed.")
        else:
            # If npm is installed, simply install pm2
            run(["npm", "install", "pm2", "-g"])
            print("pm2 has been successfully installed via npm.")

def update_and_start(process_name, interval=60):
    updater = AutoUpdater()
    updater.check_update()

    # Get all arguments passed to your script
    sys.argv[1:] = ['--process_name', 'sense', '--host', '127.0.0.1', '--port', '6666']

    # Initialize an empty list to store the arguments
    arguments = []

    # Flag to indicate whether we should skip the next argument (the value after "--process_name")
    skip_next = False

    for arg in sys.argv[1:]:
        if skip_next:
            # Skip the current argument if the flag is set
            skip_next = False
        elif arg == "--process_name":
            # If we encounter "--process_name", set the flag to skip the next argument
            skip_next = True
        else:
            # Otherwise, add the argument to the list of arguments
            arguments.append(arg)
    pm2_command = f"pm2 start --interpreter python3 sense.py --name {process_name}"
    if arguments:
        pm2_command += f" -- {' '.join(arguments)}"
    run(pm2_command, shell=True, check=True)

def check_for_updates(process_name, interval=60):
    updater = AutoUpdater()

    while True:
        if updater.check_update():
            pm2_command_stop = f"pm2 stop {process_name}"
            process = Popen(pm2_command_stop, shell=True, stdout=PIPE, stderr=PIPE)
            process.communicate()
            pm2_command_start = f"pm2 start {process_name}"
            process = Popen(pm2_command_start, shell=True, stdout=PIPE, stderr=PIPE)
            process.communicate()

            print("PM2 process successfully restarted.")

        time.sleep(interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automatic Update Script with AutoUpdater and PM2.")
    parser.add_argument("--process_name", required=True, help="Name of the PM2 process to start.")
    args, unknown = parser.parse_known_args()
    check_and_install_pm2()
    update_and_start(args.process_name)
    check_for_updates(args.process_name)