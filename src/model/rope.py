import torch
import torch.nn as nn

class RotaryEmbedding(nn.Module):
    def __init__(self, dim: int, max_seq_len: int = 2048, theta: int = 10_000):
        super().__init__()
        
        self.dim = dim
        self.max_seq_len = self.max_seq_len
        self.thata = theta
        
        inv_freq = 1.0 / (theta ** (torch.arange(0, dim, 2).float() / dim))
        
        self.register_buffer("inv_freq", inv_freq, persistent=False)
        
        self._build_cache(max_seq_len)
        
    def _build_cache(self, seq_len):
        postions = torch.arange(seq_len, device=self.inv_freq.device)
        
        freqs = torch.outer(postions, self.inv_freq)
        
        emb = torch.cat([freqs, freqs], dim=1)
        
        self.register_buffer(
            "cos_cached", emb.cos(), persistent=False
        )
        
        self.register_buffer(
            "sin_cached", emb.sin(), persistent=False
        )
        
    def forward(self, x, seq_len):
        if seq_len > self.max_seq_len:
            self._build_cache(seq_len)
            
        cos = self.cos_cached[:seq_len]
        sin = self.sin_cached[:seq_len]
        
        return cos, sin
    
def rotate_half(x):
    x1 = x[..., :x.shape[-1] // 2]
    x2 = x[..., x.shape[-1] // 2:]
    
    return torch.cat((-x2, x1), dim=1)

def apply_rope(q, k, cos, sin):
    cos = cos.unsqueeze(0).unsqueeze(0)
    sin = sin.unsqueeze(0).unsqueeze(0)
    
    q = (q * cos) + (rotate_half(q) * sin)
    k = (k * cos) + (rotate_half(k) * sin)
    
    return q, k
