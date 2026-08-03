import numpy as np
from pathlib import Path

instruct_input = "./data/instruct.bin"

output_dir = Path("./data/shards")
output_dir.mkdir(exist_ok=True)

NUM_SHARDS = 5
DTYPE = np.uint32

data = np.memmap(instruct_input, dtype=DTYPE, mode="r")

total_tokens = len(data)
tokens_per_shard = total_tokens // NUM_SHARDS

print(f"Total tokens: {total_tokens:,}")
print(f"Tokens/shard: {tokens_per_shard:,}")

for i in range(NUM_SHARDS):
    start = i * tokens_per_shard
    end = (i + 1) * tokens_per_shard if i < NUM_SHARDS - 1 else total_tokens

    out = output_dir / f"train_{i:02d}.bin"

    print(f"Writing {out.name}: {end - start:,} tokens")

    data[start:end].tofile(out)