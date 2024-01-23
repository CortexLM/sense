import atexit
import utils.system as system
import signal
import os
path = os.path.dirname(os.path.realpath(__file__))
def main():
    from utils.logging import logging
    with open(f"{path}/VERSION", "r") as f:
        local_version = f.read().strip()
    print(f"""
░▄▀▀▒██▀░█▄░█░▄▀▀▒██▀░░░▄▀▀▒██▀▒█▀▄░█▒█▒██▀▒█▀▄
▒▄██░█▄▄░█▒▀█▒▄██░█▄▄▒░▒▄██░█▄▄░█▀▄░▀▄▀░█▄▄░█▀▄
                                                v{local_version}
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
    parser.add_argument("--pulse", default=False, help="Activate Pulse Load Balancer")
    parser.add_argument("--prevent_oom", default=False, action=argparse.BooleanOptionalAction, help="Reduce cache for Turbomind (Only for validators)")
    parser.add_argument('--instance_num', type=int, default=8, help='Instance num for LMDeploy')
    args = parser.parse_args()

    logging.warning("Sense server must not be on the same server as the miner/validator.")
    
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
    model = ModelManager(pulse=args.pulse, prevent_oom=args.prevent_oom, instance_num=args.instance_num)
    api = DaemonAPI(model=model, api_tokens=config['api_tokens'])
    api.run(host=args.host, port=args.port)
if __name__ == "__main__":
    atexit.register(system.terminate_all_process)

    main()