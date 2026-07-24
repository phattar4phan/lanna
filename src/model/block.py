import torch
import torch.nn as nn

from .rmsnorm import RMSNorm
from .attention import CasualSelfAttention
from .mlp import SwiGLU

class TransformerBlock(nn.Module):
    def __init__(self, d_model: int, n_heads: int, context_length: int, ffn_dim: int, rope_theta: int = 10_000, dropout: float = 0.0, bias: bool = False):
        super().__init__()
        
        self.attn_norm = RMSNorm(d_model)
        
        self.attention = CasualSelfAttention(
            d_model=d_model,
            n_heads=n_heads,
            context_length=context_length,
            rope_theta=rope_theta,
            dropout=dropout,
            bias=bias
        )
        
        self.mlp_norm = RMSNorm(d_model)
        
        self.mlp = SwiGLU(
            d_model=d_model,
            hidden_dim=ffn_dim,
            bias=bias
        )
        
    def forward(self, x):
        # prenormalized attenion
        x = x + self.attention(self.attn_norm(x))
        
        # prenormalized mlp
        x = x + self.mlp(self.mlp_norm(x))
        
        return x
