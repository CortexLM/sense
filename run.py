import argparse
from utils.logging import logging
from utils.model import ModelManager
import utils.system as system
import time
from utils.fastapi import DaemonAPI

def main():
    parser = argparse.ArgumentParser(description="Run the Daemon API with specified host and port")
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host for the API server')
    parser.add_argument('--port', type=int, default=8000, help='Port for the API server')
    args = parser.parse_args()

    logging.warning("Sense server must not be on the same server as the miner/validator.")
    time.sleep(2)
    logging.info("[⚡️] Initializing Sense...")
    system.display_system_info()
    model = ModelManager()
    api = DaemonAPI(model=model)
    api.run(host=args.host, port=args.port)

if __name__ == "__main__":
    main()