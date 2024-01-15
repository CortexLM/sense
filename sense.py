import atexit
import utils.system as system
import signal
def main():
    from utils.logging import logging
    print("""
░▄▀▀▒██▀░█▄░█░▄▀▀▒██▀░░░▄▀▀▒██▀▒█▀▄░█▒█▒██▀▒█▀▄
▒▄██░█▄▄░█▒▀█▒▄██░█▄▄▒░▒▄██░█▄▄░█▀▄░▀▄▀░█▄▄░█▀▄
                                                v0.0.1
""")
    logging.debug("Loading modules..")
    import argparse
    from utils.model import ModelManager
    import json
    import time
    from utils.fastapi import DaemonAPI
    parser = argparse.ArgumentParser(description="Run the Daemon API with specified host and port")
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host for the API server')
    parser.add_argument('--port', type=int, default=8080, help='Port for the API server')
    args = parser.parse_args()

    
    logging.warning("Sense server must not be on the same server as the miner/validator.")
    time.sleep(2)
    logging.info("Initializing Sense..")
    try:
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        logging.error("The 'config.json' file has not been found. Make sense config init to initialize the default configuration")
        return;
    except json.JSONDecodeError as e:
        logging.error(f"Error when loading the config.json file: {e}")
        return;
    system.display_system_info()
    model = ModelManager()
    api = DaemonAPI(model=model, api_tokens=config['api_tokens'])
    api.run(host=args.host, port=args.port)
if __name__ == "__main__":
    atexit.register(system.terminate_all_process)

    main()