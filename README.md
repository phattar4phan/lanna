<p alight="center">
    <img src="./lanna.png", alt="lanna">
</p>

## Lanna
Minimal SLM for English (**~15M parameters**)

## Dataset
Changed to use [***allenai/Dolci-Instruct-SFT***](https://huggingface.co/datasets/allenai/Dolci-Instruct-SFT), gained 1.5 billion tokens to train. Reducing extra time to prepare and preprocess dataset from scratch.

Also with FineWeb Edu with around 300M tokens (stream downloading)

Download via huggingface using datasets:
```bash
# python

from datasets import load_dataset

ds = load_dataset("allenai/Dolci_Instruct-SFT")
```

## Tokenizer
Using trained (from scratch) **sentencepiece**, configurations here below (sentencepiece CLI, on my version I train it using python)
```bash
spm_train \
  --input=./data/instruct.txt \
  --model_prefix=./token/llm \
  --vocab_size=32000 \
  --model_type=unigram \
  --input_sentence_size=5000000 \
  --shuffle_input_sentence=true \
  --character_coverage=1.0 \
  --user_defined_symbols='<|user|>,<|assistant|>,<|system|>,<|environment|>,<|end|>' \
  --train_extremely_large_corpus=true \
  --num_threads=12
```

If you want to train this with the same corous, please be aware about limitations of your owned hardwares, as for me 16GB almost hit **`OOM (out of memory)`** error.

## Model
Input token IDs $\to$ Token Embedding $\to$ Transformer block * `N_LAYERS` $\to$ Final RMSNorm $\to$ Language Model (LM Head, Linear) $\to$ Vocabulary logits $\to$ Next token prediction

1. Token Embedding

input: ```[154, 82, 9324, 23, ...]``` | each integer represents a token from sentencepiece then embedding layer converts token into vectors
- Example:
    ```Token 154``` $\to$ ```[0.24, -0.12, 0.53, ...]```

2. Transformer block

Each block:
```text
Input x
   |
   |
   +-----------------------------+
   |                             |
   v                             |
RMSNorm                          |
   |                             |
   v                             |
Causal Self-Attention            |
   |                             |
   +------------- + -------------+
                  |
                  v
                  |
   +-----------------------------+
   |                             |
   v                             |
RMSNorm                          |
   |                             |
   v                             |
SwiGLU MLP                       |
   |                             |
   +------------- + -------------+
                  |
                  v

              Output
```
The `+` opeartions are residual connections, that allow information to flow through many layers without vanishing

3. RMSNorm

Instead of using BatchNorm or LayerNorm, I want this to be like LLaMA-style models which use RMSNorm to stabilize activations, make training easier and reduce computations

- Formula
$$RMS(x) = \sqrt{\frac{1}{d}\sum_{i=1}^{d}x_i^2}$$

4. Casual Self Attention

Each token looks at previous tokens, example:
Input: ```The cat sat on```.
When predicting: `the`. 
The model can see: ```The cat sat on```. 
but can't see: ```the mat```

Because it's future information, so the mask:
```text
       T h e  c a t

T      ✓
h      ✓ ✓
e      ✓ ✓ ✓
c      ✓ ✓ ✓ ✓
a      ✓ ✓ ✓ ✓ ✓
t      ✓ ✓ ✓ ✓ ✓ ✓
```
5. RoPE (Rotary Position Embedding)

Transformer have no built-in order, without position information: ```dog bites man``` and ```man bites dog``` look similar

RoPE injects postions by rotating Q/K vectors, instead of adding position embeddings: ```token + position```, it modifies attention vectors

Q $\to$ rotate(position)
K $\to$ rotate(position)

6. SwiGLU MLP

After attention, each token goes through a feed-forward network, it give better performance than ReLU/GELU MLPs

7. LM Head

At the end: hidden vector $\to$ Linear 512 $\to$ 32000 $\to$ probability of every token, the highest probability token is selected

## Tutorials
If you want to try this on your owned hardwares, run this in order:
- Copy git repository
```bash
git clone https://github.com/phattar4phan/lanna
```

- Go to cloned directory (in this case it must be ./lanna/)
```bash
cd ./lanna
```

- Install required dependecy (from pyproject.toml)
    - uv:
        ```bash
        uv sync
        ```
    - pip:
        ```bash
        pip3 install .
        ```

- Train tokenizer
    
    once you're done installing required dependecies, it's time to train the tokenizer
> [!NOTE]
> Be aware of your owned hardware limitations

    - Run as a python file (from `./lanna/`)
    ```bash
    uv run ./src/tspm.py
    ```
    - Run using sentencepiece command
    ```bash
    spm_train \
        --input=./data/instruct.txt,./data/general.txt \
        --model_prefix=./token/lanna \
        --vocab_size=32000 \
        --model_type=unigram \
        --input_sentence_size=5000000 \
        --shuffle_input_sentence=true \
        --character_coverage=1.0 \
        --user_defined_symbols='<|user|>,<|assistant|>,<|system|>,<|environment|>,<|end|>' \
        --train_extremely_large_corpus=true \
        --num_threads=12
    ```

- Train the model
```bash
uv run src/train.py
python -m train.py
```

Do it wait caution, for my own hardwards it took ~18 hours.

That's it, ONNX exported, ready for deployment.

## License
Apache 2.0