from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from utils.logging import logging
import typing as t
import json
from starlette import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer
import signal
import utils.system as system
class TextInteractive(BaseModel):
    prompt: str
    temperature: Optional[float] = 0.8
    repetition_penalty: Optional[float] = 1.1
    top_p: Optional[float] = 0.9
    top_k: Optional[int] = 40
    max_tokens: Optional[int] = 512
    refiner: Optional[bool] = False

class TextCompletion(BaseModel):
    messages: List
    temperature: Optional[float] = 0.8
    repetition_penalty: Optional[float] = 1.1
    top_p: Optional[float] = 0.9
    max_tokens: Optional[int] = 512
    refiner: Optional[bool] = False

class TextToImage(BaseModel):
    prompt: str
    height: Optional[int] = 1024
    width: Optional[int] = 1024
    num_inference_steps: Optional[int] = 30
    seed: Optional[int] = -1 
    batch_size: Optional[int] = 1
    refiner: Optional[bool] = False

class ImageToImage(BaseModel):
    image: str
    prompt: str
    height: Optional[int] = 1024
    width: Optional[int] = 1024
    strength: Optional[int] = 1
    seed: Optional[int] = -1 
    batch_size: Optional[int] = 1

class UnauthorizedMessage(BaseModel):
    detail: str = "Bearer token missing or unknown"
    
class DaemonAPI:

    def __init__(self, model, api_tokens):
        self.app = FastAPI(docs_url="/")
        self.models = model.models
        self.known_tokens = set(api_tokens)
        get_bearer_token = HTTPBearer(auto_error=False)
        async def get_token(
            auth: t.Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),
        ) -> str:
            # Simulate a database query to find a known token
            if auth is None or (token := auth.credentials) not in self.known_tokens:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=UnauthorizedMessage().detail,
                )
            return token
        

        @self.app.get("/models", responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)})
        async def get_active_models(token: str = Depends(get_token)):
            models_list = jsonable_encoder(list(self.models.keys()))

            return JSONResponse(content=models_list)
        
        @self.app.get("/model/{model_name}/stop", responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)})
        async def stop_model(model_name: str, token: str = Depends(get_token)):
            model = self.models.get(model_name)
            if not model:
                raise HTTPException(status_code=404, detail="Model not found or stopped")
            
            try:
                model.__del__()
                return {"status": "success", "message": "Model stopped"}
            except:
                return {"status": "error", "message": "Model not stopped"}



        @self.app.post("/diffusion/{model_name}/text_to_image", responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)})
        async def diffusion_text_to_image(model_name: str, interact: TextToImage, token: str = Depends(get_token)):
            model = self.models.get(model_name)
            if not model:
                raise HTTPException(status_code=404, detail="Model not found or stopped")

            response = model.t2i(
                prompt=interact.prompt,
                height=interact.height,
                width=interact.width,
                num_inference_steps=interact.num_inference_steps,
                seed=interact.seed,
                batch_size=interact.batch_size,
                refiner=interact.refiner
            )
            return response
        
        @self.app.post("/diffusion/{model_name}/image_to_image", responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)})
        async def diffusion_image_to_image(model_name: str, interact: ImageToImage, token: str = Depends(get_token)):
            model = self.models.get(model_name)
            if not model:
                raise HTTPException(status_code=404, detail="Model not found or stopped")

            response = model.i2i(
                image=interact.image,
                prompt=interact.prompt,
                height=interact.height,
                width=interact.width,
                strength=interact.strength,
                seed=interact.seed,
                batch_size=interact.batch_size
            )
            return response
    
        @self.app.post("/text_generation/{model_name}/chat/interactive", responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)})
        async def text_generation_interactive(model_name: str, interact: TextInteractive, token: str = Depends(get_token)):
            model = self.models.get(model_name)
            if not model:
                raise HTTPException(status_code=404, detail="Model not found or stopped")

            response = model.interactive(
                prompt=interact.prompt,
                temperature=interact.temperature,
                repetition_penalty=interact.repetition_penalty,
                top_p=interact.top_p,
                top_k=interact.top_k,
                max_tokens=interact.max_tokens,
            )
            return StreamingResponse(response)

        @self.app.post("/text_generation/{model_name}/chat/completions", responses={status.HTTP_401_UNAUTHORIZED: dict(model=UnauthorizedMessage)})
        async def text_generation_completions(model_name: str, interact: TextCompletion, token: str = Depends(get_token)):
            model = self.models.get(model_name)
            if not model:
                raise HTTPException(status_code=404, detail="Model not found or stopped")

            response = model.completion(
                messages=interact.messages,
                temperature=interact.temperature,
                repetition_penalty=interact.repetition_penalty,
                top_p=interact.top_p,
                max_tokens=interact.max_tokens,
            )
            return StreamingResponse(response)

    def run(self, host="127.0.0.1", port=8000):
        import uvicorn
        logging.success(f"Sense started at address {host} on port {port}")
        uvicorn.run(self.app, host=host, port=port, log_level="error")