from torch import nn, Tensor
from typing import Tuple

class StackedLinearLayers(nn.Module):
    def __init__(self, n_input: int, n_output: int) -> None:
        super().__init__()
        self.seq_layers = nn.Sequential(
            nn.Linear(n_input, 512),
            nn.ReLU(),
            nn.Linear(512, 1024),
            nn.ReLU(),
            nn.Linear(1024, 2048),
            nn.ReLU(),
            nn.Linear(2048, 2048),
            nn.ReLU(),
            nn.Linear(2048, 2048),
            nn.ReLU(),
            nn.Linear(2048, 1024),
            nn.ReLU(),
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Linear(512, n_output)
        )

    def forward(self, x) -> Tensor:
        return self.seq_layers(x)

class Encoder(nn.Module):
    def __init__(self, n_input: int, n_embedding: int) -> None:
        super().__init__()
        self.linear_layers = StackedLinearLayers(n_input, n_embedding)

    def forward(self, x) -> Tensor:
        return self.linear_layers(x)


class Decoder(nn.Module):
    def __init__(self, n_embedding: int, n_codes: int, n_anchors: int) -> None:
        super().__init__()
        self.linear_layers = StackedLinearLayers(n_embedding, 512)

        self.out_code_head = nn.Sequential(
            nn.Linear(512, n_codes),
            nn.Softmax()
        )

        self.out_anchor_head = nn.Sequential(
            nn.Linear(512, n_anchors),
            nn.Softmax()
        )
    
    def forward(self, x) -> Tuple[Tensor, Tensor]:
        x = self.linear_layers(x)
        out_code = self.out_code_head(x)
        out_anchor = self.out_anchor_head(x)
        return out_code, out_anchor

class EncoderDecoder(nn.Module):
    def __init__(self, n_input: int, n_embedding: int, n_codes: int, n_anchors: int, ) -> None:
        super().__init__()
        self.encoder = Encoder(n_input, n_embedding)
        self.decoder = Decoder(n_embedding, n_codes, n_anchors)

    def forward(self, x) -> Tuple[Tensor, Tensor]:
        x = self.encoder(x)
        x = self.decoder(x)
        return x