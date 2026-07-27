import numpy as np
import sentencepiece as spm

sp = spm.SentencePieceProcessor(model_file="./token/llm.model")

def tokenizeIDs(input_path: str, output_path: str):
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
    
tokenizeIDs('./data/general.txt', './data/general.bin')
tokenizeIDs('./data/instruct.txt', './data/instruct.bin')