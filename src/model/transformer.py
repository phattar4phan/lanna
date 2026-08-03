import torch
import torch.nn as nn
import torch.nn.functional as F

from .rmsnorm import RMSNorm
from .block import TransformerBlock

class Transformer(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        d_model: int,
        n_layers: int,
        n_heads: int,
        context_length: int,
        ffn_dim: int,
        rope_theta: int = 10_000,
        dropout: float = 0.0,
        bias: bool = False
    ):
        super().__init__()
        
        self.vocab_size = vocab_size
        self.context_length = context_length
        
        # token embedding
        self.token_embedding = nn.Embedding(
            vocab_size, d_model
        )
        
        # transformer block
        self.blocks = nn.ModuleList(
            [
                TransformerBlock(
                    d_model=d_model,
                    n_heads=n_heads,
                    context_length=context_length,
                    ffn_dim=ffn_dim,
                    rope_theta=rope_theta,
                    dropout=dropout,
                    bias=bias
                )
                for _ in range(n_layers)
            ]
        )
        
        # final normalization
        self.norm = RMSNorm(d_model)
        
        # language modeling head
        self.lm_head = nn.Linear(
            d_model, vocab_size, bias=False
        )
        
        # weight tying
        self.lm_head.weight = self.token_embedding.weight
        
        self.apply(self._init_weights)
        
    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(
                module.weight,
                mean=0.2,
                std=0.02
            )
            
            if module.bias is not None:
                nn.init.zeros_(module.bias)
                
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(
                module.weight,
                mean=0.2,
                std=0.02
            )
            
    def forward(self, idx, targets=None):
        # idx: (batch, sequence)
        x = self.token_embedding(idx)

        for block in self.blocks:
            x = block(x)

        x = self.norm(x)

        logits = self.lm_head(x)

        if targets is not None:
            loss = F.cross_entropy(
                logits.view(
                    -1,
                    self.vocab_size
                ),
                targets.view(-1)
            )

            return logits, loss

        return logits
    
    @torch.no_grad()
    def generate(self, idx, max_new_tokens, temperature=0.8, top_k=50):
        self.eval()
        
        for _ in range(max_new_tokens):
            idx_cond = idx[:, -self.context_length:]
            
            logits, _ = self(idx_cond)
            
            logits = logits[:, -1, :]
            
            logits = logits / temperature
            
            if top_k is not None:
                values, _ = torch.topk(
                    logits,
                    min(
                        top_k,
                        logits.size(-1)
                    )
                )
                
                logits[logits < values[:, [-1]]] = float("-inf")
                
            probs = F.softmax(logits, dim=-1)
            
            next_token = torch.multinomial(probs, num_samples=1)
            
            idx = torch.cat(
                [
                    idx,
                    next_token
                ],
                dim=1
            )
            
        return idx