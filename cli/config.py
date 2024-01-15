import json
import random
import string
import os
from pathlib import Path
# For colored text output
from termcolor import colored

class SubCliConfig:
    def __init__(self):
        init_json_path = os.path.join(str(Path.home()), '.sense', 'init.json')
        self._sense_dir = "/srv/sense"
        # Lire le fichier JSON et accéder à la clé 'folder'
        try:
            with open(init_json_path, 'r') as file:
                self._sense_dir = json.load(file)['path']
        except Exception as e:
            pass
        self._mode = 0
        self._config_data = {}
        self._api_tokens = []
        self._models = {
            "diffusions": [
                {
                    "gpu_id": "4,5,6,7",
                    "modelName": "dataautogpt3/OpenDalleV1.1",
                    "modelType": "Text2Image"
                },
                {
                    "modelName": "stabilityai/stable-diffusion-xl-refiner-1.0",
                    "modelType": "Image2Image"
                }
            ],
            "turbomind": [
                {
                    "gpu_id": "0,1,2,3",
                    "modelName": "CortexLM/qwen-72b-chat-w4",
                    "modelType": "qwen-14b"
                }
            ]
        }
    
    def init(self):
        file_config_exists = os.path.exists(os.path.join(self._sense_dir, 'config.json'))
        if file_config_exists:
            response = input(colored("The config.json file will be deleted during initialization. Do you agree? (y/n): ", "red"))
            if response.lower() == 'y':
                pass;
            else:
                return;
        
        self._set_mode()
        self._generate_api_key_if_required()
        self._set_gpu_ids()
        self._generate_config()

    def reset_api_key(self):
        self._load_config() 
        self._generate_api_key_if_required()
        self._edit_config()

    def _set_gpu_ids(self):
        for category in self._models:
            for model in self._models[category]:
                if "gpu_id" in model:
                    if category == "diffusions":
                        gpu_id = input(f"Enter the GPU IDs for the diffusion model {model['modelName']} (e.g., 4,5,6,7): ")
                        model["gpu_id"] = gpu_id
                    elif category == "turbomind":
                        valid = False
                        while not valid:
                            gpu_ids = input(f"Enter the GPU IDs for the turbomind model {model['modelName']} (e.g., 0,1 or 2,3,4,5): ").split(',')
                            if len(gpu_ids) in [1, 2, 4, 8, 16]:
                                model["gpu_id"] = ','.join(gpu_ids)
                                valid = True
                            else:
                                print("Invalid input. The number of GPUs must be 1, 2, 4, 8, 16, etc.")
    def _load_config(self):
        config_path = os.path.join(self._sense_dir, 'config.json')
        if os.path.exists(config_path):
            with open(config_path, 'r') as json_file:
                self._config_data = json.load(json_file)
            self._mode = self._config_data.get('mode', 0)
            self._api_tokens = self._config_data.get('api_tokens', [])
            self._models = self._config_data.get('models', [])
        else:
            self._mode = 0
            self._config_data = {}
            self._api_tokens = []

    def _edit_config(self):
        # Assurez-vous que la liste des jetons d'API contient la nouvelle clé générée
        self._config_data['mode'] = self._mode
        self._config_data['api_tokens'] = self._api_tokens

        # Enregistrez les modifications dans config.json
        with open(os.path.join(self._sense_dir, 'config.json'), 'w') as json_file:
            json.dump(self._config_data, json_file, indent=4)
        print(colored("API key has been updated in the configuration.", "green"))

    def _set_mode(self):
        response = input(colored("Select mode. (1=Diffusion/2=Turbomind): ", "blue"))
        if response.lower() == '1':
            self._mode = 1
        else:
            self._mode = 2
        print(colored(f"Mode: {self._mode}", "green"))
    
    def _generate_api_key_if_required(self):
        response = input(colored("Do you want to generate a random API key? (y/n): ", "blue"))
        if response.lower() == 'y':
            key = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
            self._api_tokens = [key]
            print(colored(f"API Key generated: {key}", "green"))

    def _generate_config(self):
        # Save to config.py

        # Save to config.json
        config_json = {
            "mode": self._mode,
            "api_tokens": self._api_tokens,
            "models": self._models
        }
        with open(os.path.join(self._sense_dir, 'config.json'), 'w') as json_file:
            json.dump(config_json, json_file, indent=4)

        print(colored("Configuration have been saved.", "green"))
