import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch

from src.config import (
    VOCAB_SIZE,
    D_MODEL,
    N_LAYERS,
    N_HEADS,
    CONTEXT_LENGTH,
    FFN_DIM,
    ROPE_THETA,
    DROPOUT,
    BIAS,
    DEVICE,
    DTYPE,
    TEMPERATURE,
    TOP_K,
)
from src.model.transformer import Transformer
from server.inference import OnnxGenerator, TorchGenerator, BaseGenerator

app = FastAPI(title="LLM Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

generator: BaseGenerator | None = None
model_loaded = False

DEMO_RESPONSES = [
    "That's an interesting question. I'm still under active development.",
    "My current architecture contains approximately 50 million parameters.",
    "I don't always know the answer, but here's my best guess.",
    "As an experimental model, I'm learning every day.",
    "Let me think about that... Based on my training data, I'd suggest exploring further.",
    "Interesting! Could you tell me more about what you'd like to know?",
    "I'm an experimental 50M parameter language model built for learning purposes.",
    "While I can't provide a definitive answer, here's what I understand so far.",
]


def load_generator():
    import random

    global generator, model_loaded

    checkpoint_path = os.path.join(os.path.dirname(__file__), "model.pt")
    onnx_path = os.path.join(os.path.dirname(__file__), "model.onnx")

    if os.path.exists(onnx_path) and os.path.getsize(onnx_path) > 0:
        try:
            generator = OnnxGenerator(onnx_path)
            model_loaded = True
            print("ONNX model loaded successfully")
            return
        except Exception as e:
            print(f"ONNX load failed: {e}")

    if os.path.exists(checkpoint_path) and os.path.getsize(checkpoint_path) > 0:
        try:
            model = Transformer(
                vocab_size=VOCAB_SIZE,
                d_model=D_MODEL,
                n_layers=N_LAYERS,
                n_heads=N_HEADS,
                context_length=CONTEXT_LENGTH,
                ffn_dim=FFN_DIM,
                rope_theta=ROPE_THETA,
                dropout=DROPOUT,
                bias=BIAS,
            )
            checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
            state = checkpoint.get("model_state_dict", checkpoint)
            model.load_state_dict(state)
            model.to(DEVICE).to(DTYPE).eval()

            generator = TorchGenerator(model, DEVICE)
            model_loaded = True
            print(f"PyTorch model loaded on {DEVICE}")
            return
        except Exception as e:
            print(f"PyTorch load failed: {e}")

    print("No model found — running in demo mode")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@app.on_event("startup")
async def startup():
    load_generator()


@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": model_loaded}


@app.post("/chat")
async def chat(req: ChatRequest):
    import random

    if model_loaded and generator is not None:
        try:
            response = generator.generate(
                req.message,
                temperature=TEMPERATURE,
                top_k=TOP_K,
            )
            return ChatResponse(response=response)
        except Exception as e:
            print(f"Generation error: {e}")

    response = random.choice(DEMO_RESPONSES)
    return ChatResponse(response=response)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
