from pydantic import BaseModel, Field
from typing import Dict, Literal, Optional, List, Union


class GenerateRequest(BaseModel):
    """Generate request."""
    prompt: Union[str, List[Dict[str, str]]]
    session_id: int = -1
    interactive_mode: bool = False
    stream: bool = False
    stop: Optional[Union[str, List[str]]] = Field(default=None,
                                                  examples=[None])
    request_output_len: int = 512
    top_p: float = 0.8
    top_k: int = 40
    temperature: float = 0.8
    repetition_penalty: float = 1.0
    ignore_eos: bool = False
    skip_special_tokens: Optional[bool] = True
    cancel: Optional[bool] = False


class GenerateRequestQos(BaseModel):
    """Generate request."""
    prompt: Union[str, List[Dict[str, str]]]
    session_id: int = -1
    interactive_mode: bool = False
    stream: bool = False
    stop: bool = False
    request_output_len: int = 512
    top_p: float = 0.8
    top_k: int = 40
    temperature: float = 0.8
    repetition_penalty: float = 1.0
    ignore_eos: bool = False
    user_id: Optional[str] = None


class GenerateResponse(BaseModel):
    """Generate response."""
    text: str
    tokens: int
    finish_reason: Optional[Literal['stop', 'length']] = None