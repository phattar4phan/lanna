import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

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
)
from src.model.transformer import Transformer


def export_to_onnx(checkpoint_path: str, output_path: str):
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

    dummy_input = torch.randint(0, VOCAB_SIZE, (1, 16), device=DEVICE)

    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        input_names=["input_ids"],
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch", 1: "sequence"},
            "logits": {0: "batch", 1: "sequence"},
        },
        opset_version=17,
    )

    print(f"Model exported to {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default=os.path.join(os.path.dirname(__file__), "model.pt"))
    parser.add_argument("--output", default=os.path.join(os.path.dirname(__file__), "model.onnx"))
    args = parser.parse_args()

    export_to_onnx(args.checkpoint, args.output)
