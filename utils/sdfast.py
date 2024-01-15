import threading
import requests
import time
import os
import json
import subprocess
from utils.logging import logging
import signal
import asyncio
class SDFast:
    """
    A class to manage the interface with the SDFast model for generating images from text or images.
    """

    def __init__(self, instance, model_name: str = None, model_path: str = None, model_refiner: str = None, model_type: str = "t2i", host: str = "127.0.0.1", port: int = 9000, gpu_id=0, warm_up=True):
        instance.models[model_name] = self
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
            self.process = subprocess.Popen(command, shell=True, env=environment, preexec_fn=os.setsid, stdout=subprocess.PIPE)
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

    def i2i(self, image, prompt, height, width, strength, seed, batch_size):
        """
        Image-to-image transformation.

        :param image: Base image for transformation.
        :param prompt: Text prompt for image generation.
        :param height: Height of the output image.
        :param width: Width of the output image.
        :param num_inference_steps: Number of inference steps.
        :param seed: Random seed for generation.
        :param batch_size: Batch size for generation.
        :param refiner: Whether to use the refiner model.
        :return: The generated image or None if failed.
        """
        payload = {
            "image": image,
            "prompt": prompt,
            "height": height,
            "width": width,
            "strength": strength,
            "seed": seed,
            "batch_size": batch_size
        }
        data = json.dumps(payload)
        response = requests.post(f"http://{self.host}:{self.port}/image_to_image", data=data)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to get response: {response.status_code}")
            return None

    def t2i(self, prompt, height, width, num_inference_steps, seed, batch_size, refiner):
        """
        Text-to-image transformation.

        :param prompt: Text prompt for image generation.
        :param height: Height of the output image.
        :param width: Width of the output image.
        :param num_inference_steps: Number of inference steps.
        :param seed: Random seed for generation.
        :param batch_size: Batch size for generation.
        :param refiner: Whether to use the refiner model.
        :return: The generated image or None if failed.
        """
        payload = {
            "prompt": prompt,
            "height": height,
            "width": width,
            "num_inference_steps": num_inference_steps,
            "seed": seed,
            "batch_size": batch_size,
            "refiner": refiner
        }
        data = json.dumps(payload)
        response = requests.post(f"http://{self.host}:{self.port}/text_to_image", data=data)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Failed to get response: {response.status_code}")
            return None
        
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

