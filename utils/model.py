import asyncio
from utils.logging import logging
import json
import os
import aiofiles
from huggingface_hub import snapshot_download
from utils.turbomind import TurboMind
from utils.sdfast import SDFast
import random

class ModelManager:
    """
    A class to manage downloading, configuring, and running various machine learning models asynchronously.
    """

    def __init__(self, pulse=False, prevent_oom=False):
        self.models = {}
        self.prevent_oom = prevent_oom
        self.base_directory = os.getcwd()
        self.models_directory = os.path.join(self.base_directory, 'models')
        self.available_ports = [6000,6001,6002,6003,6004,6005,6006]
        self.used_ports = set()
        if not os.path.exists(self.models_directory):
            os.makedirs(self.models_directory)
        self.config = asyncio.run(self.load_config("config.json"))
        if not pulse:
            asyncio.run(self.load_models_from_config())

    def get_random_port(self):
        if not self.available_ports:
            raise Exception("All ports are in use.")
        
        port = random.choice(self.available_ports)
        self.available_ports.remove(port)
        self.used_ports.add(port)
        return port

    def release_port(self, port):
        if port in self.used_ports:
            self.used_ports.remove(port)
            self.available_ports.append(port)
        else:
            raise Exception(f"Port {port} is not in the list of used ports.")

    async def load_config(self, config_path):
        """
        Asynchronously load the configuration file.

        Parameters:
        config_path (str): Path to the configuration file.
        """
        try:
            async with aiofiles.open(config_path, 'r') as config_file:
                return json.loads(await config_file.read())
        except FileNotFoundError:
            logging.error(f"Configuration file {config_path} not found.")
            return {}
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from the config file {config_path}.")
            return {}

    async def fetch_model(self, model_name):
        """
        Asynchronously download a model snapshot from Hugging Face and save it to a specific directory.

        Parameters:
        model_name (str): Name of the model on Hugging Face.
        """
        model_name = model_name.replace('|', '/')
        model_folder = f"./models/{model_name.replace('/', '-')}/model"
        logging.debug(f'Fetching model {model_name} from huggingface..')
        snapshot_download(repo_id=model_name, local_dir=model_folder)

    async def allocate_wrapper(self, engine, model_name, n_gpus, tb_model_type=None):
        async for chunk in self.allocate(engine=engine, model_name=model_name, n_gpus=n_gpus, tb_model_type=tb_model_type):
            logging.debug(chunk)
    async def load_models_from_config(self):
        """
        Asynchronously load models as specified in the configuration.
        """
        models = self.config.get('models', {})
        logging.success("Pulse Load Balancer is disabled. Loading models via config.json")
        await self.load_diffusions(models.get('diffusions', [])),
        await self.load_turbomind(models.get('turbomind', []))
        gpu_ids = models["diffusions"][0]["gpu_id"].split(",")  # Split the GPU IDs string into a list
        logging.debug('Async loading models. Please wait')
        task1 = self.allocate_wrapper(engine="turbomind", model_name="CortexLM|qwen-72b-chat-w4", n_gpus=models["turbomind"][0]["gpu_id"], tb_model_type="qwen-14b")
        tasks2 = [self.allocate_wrapper(engine="sdfast", model_name="dataautogpt3|OpenDalleV1.1", n_gpus=gpu_id) for gpu_id in gpu_ids]

        # Executing all tasks simultaneously
        await asyncio.gather(task1, *tasks2)



    async def load_diffusions(self, diffusions):
        """
        Asynchronously load diffusion models from the config.

        Parameters:
        diffusions (list): List of diffusion models to load.
        """
        tasks = [self.fetch_model(model_info.get('modelName')) for model_info in diffusions if model_info.get('modelName')]
        await asyncio.gather(*tasks)

    async def load_turbomind(self, turbominds):
        """
        Asynchronously load turbomind models from the config.

        Parameters:
        turbominds (list): List of turbomind models to load.
        """
        tasks = [self.fetch_model(model_info.get('modelName')) for model_info in turbominds if model_info.get('modelName')]
        await asyncio.gather(*tasks)

    async def allocate(self, engine, model_name, n_gpus, tb_model_type=None):
        model_name_fn = model_name.replace("/", "-").replace("|", "-")
        if engine == "turbomind":
            model_path = f"/models/{model_name_fn}/"
            model_type = tb_model_type
            yield {"status": "allocating", "message": "Model allocated"}
            logging.info(f'Allocate {model_path} (type = {model_type}) with {n_gpus} GPUs..')
            yield {"status": "downloading", "message": "Download model"}
            await self.fetch_model(model_name=model_name)
            yield {"status": "downloaded", "message": "Model downloaded"}
            yield {"status": "start_process", "message": "Starting process"}
            tm = TurboMind(self, model_path=model_path, model_name=model_name, gpu_id=n_gpus, tb_model_type=model_type, port=self.get_random_port(), prevent_oom=self.prevent_oom)
            yield {"status": "wait_status", "message": "Wait for status"}
            if tm.wait_for_tb_model_status():
                tm.warm_up(gpu_id=n_gpus)
                yield {"status": "ready", "message": "Model is ready"}
                self.models[model_name].status = 1
                logging.info(f'Model {model_name} is ready')
            else:
                yield {"status": "error", "message": "Model is not ready"}
                logging.error(f'Error when allocating {model_path}.')
                del self.models[model_name]
                await tm.destroy()
        if engine == "sdfast":
            yield {"status": "allocating", "message": "Model allocated"}
            model_path = f"/models/{model_name_fn}/model"
            logging.info(f'Allocate {model_path} (type = sdfast) with {n_gpus} GPUs..')
            yield {"status": "downloading", "message": "Download model"}
            await self.fetch_model(model_name=model_name)
            yield {"status": "downloaded", "message": "Model downloaded"}
            yield {"status": "start_process", "message": "Starting process"}
            sd = SDFast(self, model_name=model_name, model_path=model_path, model_refiner="/models/stabilityai-stable-diffusion-xl-refiner-1.0/model", port=self.get_random_port(), model_type="t2i", gpu_id=n_gpus)
            yield {"status": "wait_status", "message": "Wait for status"}
            if await sd.wait_for_sd_model_status():
                yield {"status": "ready", "message": "Model is ready"}
                logging.info(f'Model {model_name} is ready')
            else:
                yield {"status": "error", "message": "Model is not ready"}
                logging.error(f'Error when allocating {model_path}.')
                del self.models[model_name]
                await sd.destroy()