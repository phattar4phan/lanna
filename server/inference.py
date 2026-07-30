import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from abc import ABC, abstractmethod

import torch
import sentencepiece as spm

from src.config import CONTEXT_LENGTH, MAX_NEW_TOKENS

SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
TOKENIZER_PATH = os.path.join(SERVER_DIR, "token", "llm.model")

SYSTEM_PROMPT = "You are LLM, a helpful 50M parameter language model. Answer concisely and honestly."


def format_chat(user_message: str) -> str:
    return f"<|user|>\n{user_message}\n<|assistant|>\n"


class BaseGenerator(ABC):
    @abstractmethod
    def generate(self, prompt: str, temperature: float = 0.8, top_k: int = 50) -> str:
        ...


class TorchGenerator(BaseGenerator):
    def __init__(self, model: torch.nn.Module, device: str):
        self.model = model
        self.device = device
        self.tokenizer = spm.SentencePieceProcessor()
        self.tokenizer.Load(TOKENIZER_PATH)

    @torch.no_grad()
    def generate(self, prompt: str, temperature: float = 0.8, top_k: int = 50) -> str:
        self.model.eval()

        chat_prompt = format_chat(prompt)
        token_ids = self.tokenizer.EncodeAsIds(chat_prompt)
        input_tensor = torch.tensor([token_ids], dtype=torch.long, device=self.device)

        output = self.model.generate(
            input_tensor,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=temperature,
            top_k=top_k,
        )

        output_ids = output[0].tolist()
        new_tokens = output_ids[len(token_ids):]

        end_token = self.tokenizer.PieceToId("<|end|>")
        if end_token in new_tokens:
            new_tokens = new_tokens[: new_tokens.index(end_token)]

        response = self.tokenizer.DecodeIds(new_tokens)
        return response.strip()


class OnnxGenerator(BaseGenerator):
    def __init__(self, onnx_path: str):
        import onnxruntime as ort

        self.session = ort.InferenceSession(onnx_path)
        self.tokenizer = spm.SentencePieceProcessor()
        self.tokenizer.Load(TOKENIZER_PATH)

    def generate(self, prompt: str, temperature: float = 0.8, top_k: int = 50) -> str:
        chat_prompt = format_chat(prompt)
        token_ids = self.tokenizer.EncodeAsIds(chat_prompt)

        input_ids = [token_ids]
        generated = []

        for _ in range(MAX_NEW_TOKENS):
            seq = input_ids[0][-CONTEXT_LENGTH:]
            input_feed = {
                "input_ids": [[seq]],
            }

            outputs = self.session.run(None, input_feed)
            logits = torch.tensor(outputs[0][0, -1, :])

            logits = logits / temperature

            if top_k is not None:
                values, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < values[-1]] = float("-inf")

            probs = torch.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1).item()

            end_id = self.tokenizer.PieceToId("<|end|>")
            if next_token == end_id:
                break

            generated.append(next_token)
            input_ids[0].append(next_token)

        return self.tokenizer.DecodeIds(generated).strip()
