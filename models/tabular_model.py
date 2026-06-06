import torch
import torch.nn as nn

class TabularModel(nn.Module):
    def __init__(self, input_dim=4, output_dim=8):
        super(TabularModel, self).__init__()
        self.mlp = nn.Sequential(
            nn.Linear(input_dim, 16),
            nn.ReLU(),
            nn.Linear(16, output_dim)
        )

    def forward(self, x):
        return self.mlp(x)
