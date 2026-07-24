import sentencepiece as spm

from pathlib import Path

Path('./token').mkdir(parents=True, exist_ok=True)

spm.SentencePieceTrainer.train(
    input='./data/instruct.txt',
    model_prefix='./token/lanna',
    vocab_size=32000,
    model_type="unigram",
    input_sentence_size=5_000_000,
    shuffle_input_sentence=True,
    character_coverage=1.0,
    user_defined_symbols=[
        '<|user|>',
        '<|assistant|>',
        '<|system|>',
        '<|environment|>',
        '<|end|>'
    ],
    train_extremely_large_corpus=True,
    num_threads=12
)