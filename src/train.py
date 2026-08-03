import os

# Reduces VRAM fragmentation / slow reallocation stalls on small (4GB) GPUs.
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

# On NixOS, /nix/store is read-only so `ldconfig -p` can never build a cache
# there, which breaks Triton's default way of locating libcuda.so. Point it
# straight at the driver instead so it skips ldconfig entirely.
if "TRITON_LIBCUDA_PATH" not in os.environ:
    for _candidate in ("/run/opengl-driver/lib", "/run/opengl-driver-32/lib"):
        if os.path.exists(os.path.join(_candidate, "libcuda.so.1")) or \
           os.path.exists(os.path.join(_candidate, "libcuda.so")):
            os.environ["TRITON_LIBCUDA_PATH"] = _candidate
            break

import time
import math
import multiprocessing as mp
import sys
import numpy as np

import torch
from torch.utils.data import Dataset, DataLoader

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
RESET = Fore.RESET

# Run one concurrent validation batch every N training steps -- keeps val
# signal live without spending GPU cycles on it every single iteration.
VAL_INTERVAL = 25

# --- GPU throughput tuning (Ampere: RTX 3050 supports TF32 + fast fp16/bf16 tensor cores) ---
torch.backends.cudnn.benchmark = True
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
torch.set_float32_matmul_precision("high")


def format_time(seconds):

    seconds = int(seconds)

    minutes = seconds // 60
    seconds %= 60

    return f"{minutes:02d}:{seconds:02d}"


def fused_loss_correct(loss_tensor, logits, targets):
    """
    Compute loss + correct-count and pull them back to Python in a
    single GPU sync (torch.stack + one .tolist()) instead of two
    separate .item() calls, which each force a blocking sync.
    """
    pred = logits.argmax(dim=-1)
    correct = (pred == targets).sum()
    total = targets.numel()

    loss_val, correct_val = torch.stack(
        [loss_tensor.detach(), correct.float()]
    ).tolist()

    return loss_val, int(correct_val), total


class TokenDataset(Dataset):
    def __init__(self, path, block_size):
        self.data = np.memmap(path, dtype=np.uint32, mode='r')
        self.block_size = block_size

    def __len__(self):
        return (len(self.data) - 1) // self.block_size

    def __getitem__(self, idx):
        start = idx * self.block_size

        x = torch.from_numpy(self.data[start:start+self.block_size].astype(np.int64))
        y = torch.from_numpy(self.data[start+1:start+self.block_size+1].astype(np.int64))

        return x, y


def create_loader_from(path):
    dataset = TokenDataset(
        path,
        CONTEXT_LENGTH
    )

    return DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS,
        pin_memory=PIN_MEMORY,
        persistent_workers=NUM_WORKERS > 0,
        prefetch_factor=4 if NUM_WORKERS > 0 else None,
        # Drop the ragged final batch so shapes stay constant -- avoids
        # cudnn.benchmark re-tuning and torch.compile recompiling on it.
        drop_last=True
    )


if __name__ == "__main__":
    raw_model = Transformer(
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

    raw_model.to(DEVICE)

    params = sum(
        p.numel()
        for p in raw_model.parameters()
    )

    print(f"{Fore.LIGHTBLUE_EX}Parameters{Fore.RESET}: {params}")
    print(f'{Fore.LIGHTBLUE_EX}Shards{Fore.RESET}: {len(SHARDS)}')

    # torch.compile fuses kernels and cuts Python/launch overhead -- meaningful
    # win when the GPU is busy with many small kernel launches per step.
    # Always keep `raw_model` as the reference used for saving/export, since
    # compiled wrappers can alter state_dict() key names across torch versions.
    model = raw_model
    if DEVICE == "cuda":
        try:
            compiled_model = torch.compile(raw_model)

            # torch.compile is lazy -- it only actually compiles on the first
            # real forward call, and forward/backward are compiled separately
            # (backward is only triggered by an actual .backward() call), and
            # per input shape. Warm up with the *real* batch shape and a real
            # forward+backward pass here, in a controlled spot, so a
            # backend/toolchain failure (e.g. Triton/ldconfig on NixOS) falls
            # back cleanly instead of crashing mid-training later.
            warmup_x = torch.randint(0, VOCAB_SIZE, (BATCH_SIZE, CONTEXT_LENGTH), device=DEVICE)
            warmup_y = torch.randint(0, VOCAB_SIZE, (BATCH_SIZE, CONTEXT_LENGTH), device=DEVICE)

            with torch.autocast(device_type="cuda", dtype=DTYPE, enabled=True):
                _, warmup_loss = compiled_model(warmup_x, warmup_y)

            warmup_loss.backward()
            raw_model.zero_grad(set_to_none=True)

            model = compiled_model
            print(f"{Fore.LIGHTBLUE_EX}torch.compile{Fore.RESET}: enabled")
        except Exception as e:
            print(f"{Fore.LIGHTBLUE_EX}torch.compile{Fore.RESET}: unavailable, continuing without it ({e})")

    # Fused AdamW launches the whole optimizer step as a single CUDA kernel
    # instead of one kernel per parameter -- falls back gracefully if the
    # installed torch/CUDA combo doesn't support it.
    try:
        optimizer = torch.optim.AdamW(
            raw_model.parameters(),
            lr=LEARNING_RATE,
            betas=(BETA1, BETA2),
            weight_decay=WEIGHT_DECAY,
            eps=EPS,
            fused=DEVICE == "cuda"
        )
    except (TypeError, RuntimeError):
        optimizer = torch.optim.AdamW(
            raw_model.parameters(),
            lr=LEARNING_RATE,
            betas=(BETA1, BETA2),
            weight_decay=WEIGHT_DECAY,
            eps=EPS,
            foreach=True
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

    # GradScaler is only needed for fp16 (prevents underflow); it's a no-op
    # overhead if you're training in bf16, so only enable it when it matters.
    scaler_enabled = DEVICE == "cuda" and DTYPE == torch.float16
    scaler = torch.amp.GradScaler("cuda", enabled=scaler_enabled)



class ValidationWorker:
    """
    Runs validation in a separate process so it overlaps with training
    instead of stealing GPU time between steps. The training thread ships
    a weight snapshot over a queue; the worker loads it, evaluates one
    batch, and posts (loss, correct, total) back. `poll()` never blocks
    the training loop -- it reads whatever result is ready.
    """
    def __init__(self, val_path):
        # `uv run script.py` breaks spawn's main-module re-import in the
        # child (pickle data truncated). fork is inherited-safe here since
        # the worker builds its own model after forking.
        method = "fork" if sys.platform != "win32" else "spawn"
        self.ctx = mp.get_context(method)
        print(f"{Fore.LIGHTBLUE_EX}Validation{Fore.RESET}: {method} worker")
        self.state_q = self.ctx.Queue(maxsize=4)
        self.result_q = self.ctx.Queue(maxsize=4)
        self.proc = self.ctx.Process(
            target=_val_worker_loop,
            args=(val_path, self.state_q, self.result_q),
            daemon=False
        )
        self.proc.start()

    def submit(self, state_dict):
        if not self.proc.is_alive():
            raise BrokenPipeError("validation worker died")
        # Snapshot weights on CPU so the worker can copy them without
        # racing the optimizer on GPU tensors.
        snapshot = {k: v.detach().cpu().clone() for k, v in state_dict.items()}
        self.state_q.put(snapshot, timeout=10)

    def poll(self):
        if self.proc.is_alive() and not self.result_q.empty():
            return self.result_q.get_nowait()
        return None

    def close(self):
        if self.proc.is_alive():
            self.proc.terminate()
            self.proc.join(timeout=5)


def _val_worker_loop(val_path, state_q, result_q):
    """Runs inside the spawned validation process (own CUDA context)."""
    import torch

    worker_model = Transformer(
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
    worker_model.to(DEVICE).eval()

    loader = create_loader_from(val_path)
    iterator = iter(loader)

    while True:
        state_dict = state_q.get()
        worker_model.load_state_dict(state_dict)

        try:
            vx, vy = next(iterator)
        except StopIteration:
            iterator = iter(loader)
            vx, vy = next(iterator)

        vx = vx.to(DEVICE, non_blocking=True)
        vy = vy.to(DEVICE, non_blocking=True)

        with torch.no_grad():
            with torch.autocast(device_type="cuda", dtype=DTYPE, enabled=DEVICE == "cuda"):
                vlogits, vloss = worker_model(vx, vy)

        vloss_val, vc, vt = fused_loss_correct(vloss, vlogits, vy)
        result_q.put((vloss_val, vc, vt))


def run_val_step(val_iter, val_loader):
    """
    Pull a single validation batch and evaluate it. Used as the inline
    fallback when the concurrent validation process cannot start.
    """
    try:
        vx, vy = next(val_iter)
    except StopIteration:
        val_iter = iter(val_loader)
        vx, vy = next(val_iter)

    vx = vx.to(DEVICE, non_blocking=True)
    vy = vy.to(DEVICE, non_blocking=True)

    was_training = model.training
    model.eval()

    with torch.no_grad():
        with torch.autocast(device_type="cuda", dtype=DTYPE, enabled=DEVICE == "cuda"):
            vlogits, vloss = model(vx, vy)

    if was_training:
        model.train()

    vloss_val, vc, vt = fused_loss_correct(vloss, vlogits, vy)

    return val_iter, vloss_val, vc, vt


def train(paths, stage_name, epochs, val_path):
    val_loader = create_loader_from(val_path)
    val_iter = iter(val_loader)

    # Concurrent validation in a background process; falls back to the
    # inline path if the worker can't start (e.g. spawn unavailable).
    worker = None
    try:
        worker = ValidationWorker(val_path)
        print(f"{Fore.LIGHTBLUE_EX}Validation{Fore.RESET}: concurrent process")
    except Exception as e:
        print(f"{Fore.LIGHTBLUE_EX}Validation{Fore.RESET}: inline fallback ({e})")

    try:
        for epoch in range(epochs):
            model.train()

            total_loss = 0
            total_batches = 0
            total_correct = 0
            total_tokens = 0

            val_total_loss = 0
            val_total_correct = 0
            val_total_tokens = 0
            val_steps = 0

            # last computed val stats, carried forward between VAL_INTERVAL runs
            last_val_loss_avg = 0.0
            last_val_acc = 0.0

            start = time.perf_counter()

            for path in paths:
                print(f"\n{stage_name}: {path}")

                loader = create_loader_from(path)
                total_batches_shard = len(loader)

                for step, (x, y) in enumerate(loader):
                    x = x.to(DEVICE, non_blocking=True)
                    y = y.to(DEVICE, non_blocking=True)

                    with torch.autocast(device_type="cuda", dtype=DTYPE, enabled=DEVICE == "cuda"):
                        logits, loss = model(x, y)
                        loss_scaled = loss / GRAD_ACCUM

                    scaler.scale(loss_scaled).backward()

                    if (step + 1) % GRAD_ACCUM == 0:
                        scaler.unscale_(optimizer)

                        torch.nn.utils.clip_grad_norm_(
                            raw_model.parameters(),
                            MAX_GRAD_NORM
                        )

                        scaler.step(optimizer)
                        scaler.update()

                        optimizer.zero_grad(set_to_none=True)

                    loss_val, c, t = fused_loss_correct(loss, logits, y)

                    total_loss += loss_val
                    total_batches += 1
                    total_correct += c
                    total_tokens += t

                    # concurrent validation, throttled to every VAL_INTERVAL steps:
                    # ship a weight snapshot to the background process, then pick up
                    # whatever result is ready without blocking the training loop.
                    if (step + 1) % VAL_INTERVAL == 0:
                        vloss_val = None
                        if worker is not None:
                            try:
                                worker.submit(raw_model.state_dict())
                                res = worker.poll()
                            except Exception:
                                worker.close()
                                worker = None
                                res = None
                            if res is not None:
                                vloss_val, vc, vt = res

                        if vloss_val is None:
                            # worker unavailable or result not ready yet -- fall
                            # back to the inline path when the worker is gone.
                            if worker is None:
                                val_iter, vloss_val, vc, vt = run_val_step(val_iter, val_loader)
                            else:
                                continue

                        val_total_loss += vloss_val
                        val_total_correct += vc
                        val_total_tokens += vt
                        val_steps += 1

                        last_val_loss_avg = val_total_loss / val_steps
                        last_val_acc = val_total_correct / val_total_tokens * 100

                    elapsed = time.perf_counter() - start
                    speed = (step + 1) / elapsed
                    remaining = (total_batches_shard - step - 1) / speed

                    percent = (step + 1) / total_batches_shard * 100
                    acc = total_correct / total_tokens * 100

                    print(
                        f"\r{PERCENT}{epoch + 1}/{epochs}{RESET}: "
                        f"{BATCH}{step + 1}/{total_batches_shard}{RESET}, "
                        f"{PERCENT}{percent:.2f}%{RESET}, "
                        f"{BATCH}{speed:.1f}{RESET} batch/s, "
                        f"{LOSS}loss{RESET}: {loss_val:.4f}, "
                        f"{ACC}acc{RESET}: {acc:.2f}%, "
                        f"{VAL}vloss{RESET}: {Fore.LIGHTWHITE_EX}{last_val_loss_avg:.4f}{Fore.RESET}, "
                        f"{VAL}vacc{RESET}: {Fore.LIGHTWHITE_EX}{last_val_acc:.2f}%{Fore.RESET}, "
                        f"{TIME_GREEN}{format_time(elapsed)}{RESET}/"
                        f"{TIME_CYAN}{format_time(remaining)}{RESET}",
                        end="",
                        flush=True
                    )

                print()
                print(f"{stage_name} shard finished")

            if (step + 1) % GRAD_ACCUM != 0:
                scaler.unscale_(optimizer)

                torch.nn.utils.clip_grad_norm_(
                    raw_model.parameters(),
                    MAX_GRAD_NORM
                )

                scaler.step(optimizer)
                scaler.update()

                optimizer.zero_grad(
                    set_to_none=True
                )

            train_loss = total_loss / total_batches
            train_acc = total_correct / total_tokens * 100
            val_loss = val_total_loss / max(val_steps, 1)
            val_acc = val_total_correct / max(val_total_tokens, 1) * 100

            scheduler.step(val_loss)

            print(
                f"\n"
                f"{LOSS}loss {VAL}{train_loss:.4f} "
                f"{ACC}acc {VAL}{train_acc:.2f}% "
                f"{VAL}val_loss {val_loss:.4f} "
                f"{VAL}val_acc {val_acc:.2f}%\n"
            )

    finally:
        if worker is not None:
            worker.close()

    torch.save(raw_model.state_dict(), CHECKPOINT_DIR / f"{stage_name}.pt")

    print(f"Saved {stage_name} checkpoint")


if __name__ == "__main__":
    train(
        [GENERAL_PATH],
        "BASE",
        3,
        GENERAL_VAL_PATH
    )

    train(
        SHARDS,
        "SFT",
        3,
        INSTRUCT_VAL_PATH
    )

    torch.save(raw_model.state_dict(), CHECKPOINT_DIR / "llm.pt")

    print("Saved checkpoint")

    raw_model.eval()

    dummy = torch.randint(
        0,
        VOCAB_SIZE,
        (1, CONTEXT_LENGTH),
        device=DEVICE
    )

    torch.onnx.export(
        raw_model,
        dummy,
        SRC_DIR / "llm.onnx",
        input_names=[
            "input_ids"
        ],
        output_names=[
            "logits"
        ],
        dynamic_axes={
            "input_ids": {
                0: "batch",
                1: "sequence"
            },

            "logits": {
                0: "batch",
                1: "sequence"
            }
        },
        opset_version=18
    )

    print(f"ONNX {Fore.LIGHTGREEN_EX}export{Fore.RESET} completed.")
