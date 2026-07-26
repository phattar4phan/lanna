import torch

from pathlib import Path

# paths
SRC_DIR = Path(__file__).resolve().parent

DATA_DIR = SRC_DIR.parent / "data"
TOKEN_DIR = SRC_DIR.parent / "token"

CHECKPOINT_DIR = SRC_DIR / "checkpoints"
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

# tokenizers
TOKENIZER_PATH = TOKEN_DIR / "lanna.model"
VOCAB_SIZE = 32_000

# models
CONTEXT_LENGTH = 512

N_LAYERS, N_HEADS = 8, 8

D_MODEL = 512
HEAD_DIM = D_MODEL // N_HEADS

FFN_DIM = D_MODEL * 4

DROPOUT = 0.0
BIAS = False

ROPE_THETA = 10_000

# training
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

DTYPE = (
    torch.bfloat16 if DEVICE == "cuda" and torch.cuda.is_bf16_supported() else torch.float16 if DEVICE == "cuda" else torch.float32
)

EPOCHS = 3

BATCH_SIZE = 3
GRAD_ACCUM = 16

LEARNING_RATE = 3e-4
MIN_LR = 3e-5

WEIGHT_DECAY = 0.1

BETA1 = 0.9
BETA2 = 0.95

EPS = 1e-8

MAX_GRAD_NORM = 1.0

WARMUP_STEPS = 2_000

# data
NUM_WORKERS = 6
PIN_MEMORY = True

SHARDS_DIR = DATA_DIR / "shards"
SHARDS = sorted(SHARDS_DIR.glob("train_*.bin"))

VAL_PATH = DATA_DIR / "val.bin"

# checkpoints
SAVE_EVERY = 1
CHECKPOINT_NAME = CHECKPOINT_DIR / "lanna.pt"

# generatino
TEMPERATURE = 0.8
TOP_K = 50
MAX_NEW_TOKENS = 256

# reproducibility
SEED = 42