import threading
import requests
import time
import os
import json
import subprocess
from utils.logging import logging
import signal
import asyncio
import shlex
import aiohttp
class SDFast:
    """
    A class to manage the interface with the SDFast model for generating images from text or images.
    """

    def __init__(self, instance, model_name: str = None, model_path: str = None, model_refiner: str = None, model_type: str = "t2i", host: str = "127.0.0.1", port: int = 9000, gpu_id=0, warm_up=True):
        if instance.models.get(model_name) is None:
            instance.models[model_name] = {}
            instance.models[model_name]['workers'] = {}
        n = 0
        while n in instance.models[model_name]['workers']:
                n += 1
        instance.models[model_name]['workers'][n] = self
        """
        Initialize the SDFast model instance.

        :param instance: The main model instance.
        :param model_path: Path to the SDFast model.
        :param model_refiner: Path to the model refiner.
        :param model_type: Type of the model (e.g., 't2i' for text-to-image).
        :param host: Host address for the model server.
        :param port: Port number for the model server.
        :param gpu_id: GPU ID to use for the model.
        :param warm_up: Flag to warm up the model on initialization.
        """
        self.model_type = "turbomind"
        self.model_name = model_name

        self.instance = instance
        self.model_path = model_path
        self.host = host
        self.port = port
        self.gpu_id = gpu_id
        self.model_type = model_type
        self.model_refiner = model_refiner
        self.base_directory = instance.base_directory
        self.run_subprocess()
    def run_subprocess(self):
        """
        Run the SDFast model subprocess.
        """
        environment = os.environ.copy()
        environment["CUDA_VISIBLE_DEVICES"] = str(self.gpu_id)
        command = f"python3 api/sdfast.py --host {self.host} --port {self.port} --model_name {self.base_directory}{self.model_path} --model_refiner {self.base_directory}{self.model_refiner} --model_type {self.model_type}"
        logging.info(f'Spawning 1 process for {self.model_path}')

        try:
            self.process = subprocess.Popen(shlex.split(command), shell=False, env=environment, preexec_fn=os.setsid, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            logging.error(f"Error when executing the command: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")

    async def wait_for_sd_model_status(self, timeout=720):
        """
        Wait for the SDFast model to be ready.

        :param timeout: Maximum time to wait for the model to be ready.
        """
        start_time = time.time()
        url = f"http://{self.host}:{self.port}/ping"
        while True:
            if time.time() - start_time > timeout:
                logging.error(f"Error: Timeout of {timeout} seconds exceeded for model {self.model_path} ({self.host}:{self.port})")
                return False

            try:
                response = requests.get(url)
                if response.status_code == 200:
                    logging.info(f'Model {self.model_path} is ready')
                    return True
            except requests.exceptions.RequestException:
                pass
            await asyncio.sleep(1)  # Wait for a second before retrying

    async def make_request(self, endpoint, payload):
        async with aiohttp.ClientSession() as session:
            url = f"http://{self.host}:{self.port}{endpoint}"
            headers = {"Content-Type": "application/json"}
            try:
                async with session.post(url, json=payload, headers=headers) as response:
                    response_data = await response.json()
                    if response.status == 200:
                        return response_data
                    else:
                        logging.error(f"Failed to get response: {response.status}")
                        return None
            except Exception as e:
                logging.error(f"Failed to make request: {str(e)}")
                return None

    async def i2i(self, image, prompt, height, width, strength, seed, batch_size):
        payload = {
            "image": image,
            "prompt": prompt,
            "height": height,
            "width": width,
            "strength": strength,
            "seed": seed,
            "batch_size": batch_size
        }
        response = await self.make_request("/image_to_image", payload)
        return response

    async def t2i(self, prompt, height, width, num_inference_steps, seed, batch_size, refiner):
        payload = {
            "prompt": prompt,
            "height": height,
            "width": width,
            "num_inference_steps": num_inference_steps,
            "seed": seed,
            "batch_size": batch_size,
            "refiner": refiner
        }
        response = await self.make_request("/text_to_image", payload)
        return response
        
    def destroy(self):
        if self.process:
            try:
                logging.info(f"Stop {self.model_path} model..")
                model = self.instance.models.get(self.model_name)
                if model:
                    del model
                os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                time.sleep(2)
                logging.info(f"{self.model_path} model stopped.")
            except Exception as e:
                logging.error(f"Error when stopping {self.model_path} model: {e}")
        else:
            logging.info(f"{self.model_path} model is not running.")