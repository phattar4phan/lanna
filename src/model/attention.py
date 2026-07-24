import torch
import torch.nn as nn
import torch.nn.functional as F

from .rope import RotaryEmbedding, apply_rope

class CasualSelfAttention(nn.Module):
    def __init__(self, d_model: int, n_heads: int, context_length: int, rope_theta: int = 10_000, dropout: float = 0.0, bias: bool = False):
        super().__init__()
        
        assert d_model % n_heads == 0
        
        self.d_model = d_model
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads
        
        self.dropout = dropout
        
        # combined qkv projection
        self.qkv = nn.Linear(
            d_model, d_model * 3, bias=bias
        )
        
        # output projection
        self.out_proj = nn.Linear(
            d_model, d_model, bias=bias
        )
        
        self.rope = RotaryEmbedding(
            dim=self.head_dim, max_seq_len=context_length, theta=rope_theta
        )
        
        self.attn_dropout = nn.Dropout(dropout)
        self.resid_dropout = nn.Dropout(dropout)
        
    def forward(self, x):
        B, T, C = x.shape
        
        # qkv
        qkv = self.qkv(x)
        
        q, k, v = qkv.chunk(
            3, dim=-1
        )
        
        # shape: (B, heads, tokens, head_dim)
        q = q.view(
            B, T, self.n_heads, self.head_dim
        ).transpose(1, 2)
        
        k = k.view(
            B, T, self.n_heads, self.head_dim
        ).transpose(1, 2)
        
        v = v.view(
            B, T, self.n_heads, self.head_dim
        ).transpose(1, 2)
        
        # RoPE
        cos, sin = self.rope(
            x, T
        )
        
        q, k = apply_rope(q, k, cos, sin)
        
        # attention
        # sdpa automatically, optimized kernels, casual masking
        y = F.scaled_dot_product_attention(
            q, k, v, dropout_p=(
                self.dropout if self.training else 0.0
            ),
            is_causal=True
        )
        
        # merge heads
        y = y.transpose(1, 2).contiguous()
        
        y = y.view(B, T, C)
        
        # output projection
        y = self.out_proj(y)
        y = self.resid_dropout(y)
        
        return y