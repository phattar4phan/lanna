from pathlib import Path
from datasets import load_dataset

ds = load_dataset("allenai/Dolci-Instruct-SFT")

def serialize(messages):
    text = ''
    
    for msg in messages:
        content = msg.get("content")
        if content is None:
            continue
        
        text += f"<|{msg['role']}|>\n"
        text += msg["content"].strip()
        text += "\n\n"
        
    return text

with open(Path("./data/instruct.txt"), 'w', encoding='utf-8') as f:
    for row in ds['train']:
        f.write(serialize(row["messages"]))
        f.write("<|end|>\n\n") # seperator between conversations