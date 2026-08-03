import numpy as np
import sentencepiece as spm

sp = spm.SentencePieceProcessor(model_file="./token/llm.model")

def tokenize_docs(lines, output_path):
    """Encode each whole document + '<|end|>' as one training sequence.

    Instruct examples span many lines (<|user|> question <|assistant|>
    answer <|end|>); tokenizing per line would teach the model that
    '<|assistant|>' is a standalone document followed by '<|end|>'.
    """
    with open(output_path, 'wb') as fout:
        total_tokens = 0
        i = 0

        for line in lines:
            line = line.strip()

            if not line:
                continue

            ids = sp.encode(line + "\n<|end|>\n", out_type=int)

            np.array(ids, dtype=np.uint32).tofile(fout)

            total_tokens += len(ids)

            if i % 10000 == 0:
                print(f'\rProcessed: {i:,} lines | {total_tokens:,} tokens', end='', flush=True)

            i += 1

    print(f'\nDone! total: {total_tokens:,} tokens')


def tokenize_instruct(input_path, output_path):
    """Group instruct.txt lines into examples, one sequence per example."""
    with open(input_path, 'r', encoding='utf-8') as fin, open(output_path, 'wb') as fout:
        total_tokens = 0
        example = []
        count = 0

        def flush():
            nonlocal example, count
            if not example:
                return

            doc = "\n".join(example).strip()

            if doc:
                ids = sp.encode(doc + "\n<|end|>\n", out_type=int)
                np.array(ids, dtype=np.uint32).tofile(fout)
                nonlocal total_tokens
                total_tokens += len(ids)

            example = []
            count += 1

            if count % 10000 == 0:
                print(f'\rProcessed: {count:,} examples | {total_tokens:,} tokens', end='', flush=True)

        for line in fin:
            line = line.strip()

            if not line:
                continue

            example.append(line)

            if line == "<|end|>":
                flush()

        flush()

    print(f'\nDone! total: {total_tokens:,} tokens | {count:,} examples')


def tokenizeIDs(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as fin, open(output_path, 'wb') as fout:
        total_tokens = 0

        for i, line in enumerate(fin):
            line = line.strip()

            if not line:
                continue

            ids = sp.encode(line + "\n<|end|>\n", out_type=int)

            np.array(ids, dtype=np.uint32).tofile(fout)

            total_tokens += len(ids)

            if i % 10000 == 0:
                print(f'\rProcessed: {i:,} lines | {total_tokens:,} tokens', end='', flush=True)

    print(f'\nDone! total: {total_tokens:,} tokens')


def make_val_bin(src_path, dst_path, frac=0.05, floor=1_000_000):
    """Derive a validation set from the tail of a token .bin file."""
    data = np.memmap(src_path, dtype=np.uint32, mode="r")

    n = max(floor, int(len(data) * frac))
    n = min(n, len(data))

    np.asarray(data[-n:], dtype=np.uint32).tofile(dst_path)

    print(f'{dst_path}: {n:,} tokens')


if __name__ == "__main__":
    tokenizeIDs('./data/general.txt', './data/general.bin')
    tokenize_instruct('./data/instruct.txt', './data/instruct.bin')

    make_val_bin('./data/general.bin', './data/genval.bin')
    make_val_bin('./data/instruct.bin', './data/sftval.bin')
