import numpy as np
import sentencepiece as spm
from datasets import load_dataset

sp = spm.SentencePieceProcessor()
sp.load("./token/lanna.model")

ds = load_dataset("allenai/Dolci-Instruct-SFT")

print("Encoding...")

with open("./data/train.bin", "wb") as f:
    for i, row in enumerate(ds["train"]):
        text = ""

        for msg in row["messages"]:
            content = msg.get("content")
            if content is None:
                continue

            text += f"<|{msg['role']}|>\n"
            text += content.strip()
            text += "\n\n"

        text += "<|end|>\n"

        ids = sp.encode(text, out_type=int)
        np.array(ids, dtype=np.uint32).tofile(f)

        if i % 10000 == 0:
            print(f"processed {i} samples")

print("Done.")