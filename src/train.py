import time
import math
import numpy as np

import torch
from torch.utils.data import Dataset, DataLoader

from tqdm import tqdm
from colorama import Fore, init

from config import *
from model.transformer import Transformer

init(autoreset=True)

PERCENT = Fore.LIGHTBLUE_EX
BATCH = Fore.LIGHTYELLOW_EX
TIME_GREEN = Fore.LIGHTGREEN_EX
TIME_CYAN = Fore.LIGHTCYAN_EX
LOSS = Fore.LIGHTMAGENTA_EX
ACC = Fore.LIGHTRED_EX
VAL = Fore.LIGHTWHITE_EX

def format_time(seconds):

    seconds = int(seconds)

    minutes = seconds // 60
    seconds %= 60

    return f"{minutes:02d}:{seconds:02d}"

def accuracy(logits, targets):

    pred = logits.argmax(dim=-1)

    correct = (
        pred == targets
    ).sum()

    total = targets.numel()

    return correct.item(), total

class TokenDataset(Dataset):
    def __init__(self, path, block_size):
        self.data = np.memmap(path, dtype=np.uint32, mode='r')
        self.block_size = block_size
        
    def __len__(self):
        return len(self.data) // self.block_size
    
    def __getitem__(self, idx):
        start = idx * self.block_size
        
        x = torch.from_numpy(self.data[start:start+self.block_size].astype(np.int64))
        y = torch.from_numpy(self.data[start+1:start+self.block_size+1].astype(np.int64))
        
        return x, y

def create_loader(path):
    dataset = TokenDataset(
        path,
        CONTEXT_LENGTH
    )

    return DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS,
        pin_memory=PIN_MEMORY
    )

@torch.no_grad()
def evaluate(loader):
    model.eval()

    total_loss = 0
    total_correct = 0
    total_tokens = 0

    bar = tqdm(
        loader,
        desc="Validation",
        unit="batch",
        dynamic_ncols=True
    )


    for x, y in bar:

        x = x.to(
            DEVICE,
            non_blocking=True
        )

        y = y.to(
            DEVICE,
            non_blocking=True
        )


        logits, loss = model(
            x,
            y
        )


        total_loss += loss.item()


        c, t = accuracy(
            logits,
            y
        )


        total_correct += c
        total_tokens += t


        acc = (
            total_correct /
            total_tokens *
            100
        )


        bar.set_postfix_str(
            f"{LOSS}loss "
            f"{VAL}{loss.item():.4f} "
            f"{ACC}accuracy "
            f"{VAL}{acc:.2f}%"
        )


    return (
        total_loss / len(loader),
        total_correct /
        total_tokens *
        100
    )

model = Transformer(
    vocab_size=VOCAB_SIZE,
    d_model=D_MODEL,
    n_layers=N_LAYERS,
    n_heads=N_HEADS,
    context_length=CONTEXT_LENGTH,
    ffn_dim=FFN_DIM,
    rope_theta=ROPE_THETA,
    dropout=DROPOUT,
    bias=BIAS
)

model.to(DEVICE)

params = sum(
    p.numel()
    for p in model.parameters()
)

print(f"{Fore.LIGHTBLUE_EX}Parameters{Fore.RESET}: {params}")
print(f'{Fore.LIGHTBLUE_EX}Shards{Fore.RESET}: {len(SHARDS)}')

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=LEARNING_RATE,
    betas=(BETA1, BETA2),
    weight_decay=WEIGHT_DECAY,
    eps=EPS
)

print(f'{Fore.LIGHTBLUE_EX}Optimizer{Fore.RESET}: {optimizer}')

scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer,
    mode="min",
    factor=0.5,
    patience=2,
    min_lr=MIN_LR
)

print(f'{Fore.LIGHTBLUE_EX}Scheduler{Fore.RESET}: {scheduler}')

scaler = torch.amp.GradScaler("cuda", enabled=DEVICE == "cuda")

def train(paths, stage_name, epochs, val_path):
    for epoch in range(epochs):
        model.train()

        total_loss = 0
        total_batches = 0
        total_correct = 0
        total_tokens = 0

        start = time.perf_counter()

        for path in paths:
            print(f"\n{stage_name}: {path}")

            loader = create_loader(path)

            bar = tqdm(
                loader,
                desc=f"{stage_name} Epoch {epoch+1}/{epochs}",
                unit="batch",
                dynamic_ncols=True
            )

            for step, (x, y) in enumerate(bar):
                x = x.to(DEVICE, non_blocking=True)
                y = y.to(DEVICE, non_blocking=True)

                with torch.autocast(device_type="cuda", dtype=DTYPE, enabled=DEVICE=="cuda"):
                    logits, loss = model(x, y)
                    loss_scaled = loss / GRAD_ACCUM

                scaler.scale(loss_scaled).backward()

                if (step + 1) % GRAD_ACCUM == 0:
                    scaler.unscale_(optimizer)

                    torch.nn.utils.clip_grad_norm_(
                        model.parameters(),
                        MAX_GRAD_NORM
                    )

                    scaler.step(optimizer)
                    scaler.update()

                    optimizer.zero_grad(set_to_none=True)

                total_loss += loss.item()
                total_batches += 1

                c, t = accuracy(logits,y)

                total_correct += c
                total_tokens += t

                elapsed = time.perf_counter() - start
                speed = (step + 1) / elapsed
                remaining = (len(loader) - step - 1) / speed

                acc = total_correct / total_tokens * 100

                bar.set_postfix_str(
                    f"{PERCENT}{bar.n / bar.total * 100:.2f}% "
                    f"{BATCH}{speed:.1f} batch/s "
                    f"{TIME_GREEN}{format_time(elapsed)}"
                    f"{TIME_CYAN}/{format_time(remaining)} "
                    f"{LOSS}loss {VAL}{loss.item():.4f} "
                    f"{ACC}acc {VAL}{acc:.2f}%"
                )

            print(
                f"{stage_name} shard finished"
            )

        if (step + 1) % GRAD_ACCUM != 0:
            scaler.unscale_(optimizer)

            torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                MAX_GRAD_NORM
            )

            scaler.step(optimizer)
            scaler.update()

            optimizer.zero_grad(
                set_to_none=True
            )

        train_loss = total_loss / total_batches
        train_acc = total_correct / total_tokens * 100

        val_loader = create_loader(val_path)

        val_loss, val_acc = evaluate(val_loader)

        scheduler.step(val_loss)

        print(
            f"\n"
            f"{LOSS}loss {VAL}{train_loss:.4f} "
            f"{ACC}acc {VAL}{train_acc:.2f}% "
            f"{VAL}val_loss {val_loss:.4f} "
            f"{VAL}val_acc {val_acc:.2f}%\n"
        )

    torch.save(model.state_dict(),CHECKPOINT_DIR / f"{stage_name}.pt")

    print(f"Saved {stage_name} checkpoint")

train(
    [GENERAL_PATH],
    "BASE",
    3,
    GENERAL_VAL_PATH
)

train(
    SHARDS,
    "SFT",
    EPOCHS,
    INSTRUCT_VAL_PATH
)

torch.save(model.state_dict(), CHECKPOINT_DIR / "llm.pt")

print("Saved checkpoint")

model.eval()

dummy = torch.randint(
    0,
    VOCAB_SIZE,
    (1, CONTEXT_LENGTH),
    device=DEVICE
)

torch.onnx.export(
    model,
    dummy,
    SRC_DIR / "llm.onnx",
    input_names= [
        "input_ids"
    ],
    output_names= [
        "logits"
    ],
    dynamic_axes= {
        "input_ids": {
            0:"batch",
            1:"sequence"
        },

        "logits": {
            0:"batch",
            1:"sequence"
        }
    },
    opset_version=18
)

print(f"ONNX {Fore.LIGHTGREEN_EX}export{Fore.RESET} completed.")