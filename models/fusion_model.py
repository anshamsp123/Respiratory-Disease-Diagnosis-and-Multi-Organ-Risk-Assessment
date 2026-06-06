import torch
import torch.nn as nn
from models.image_model import ImageModel
from models.tabular_model import TabularModel

class MultimodalFusion(nn.Module):
    def __init__(self, num_classes=5, num_tabular_features=4):
        super(MultimodalFusion, self).__init__()
        self.image_model = ImageModel(num_classes=num_classes)
        self.tabular_model = TabularModel(input_dim=num_tabular_features, output_dim=8)
        
        # Fusion layer
        self.fusion = nn.Sequential(
            nn.Linear(num_classes + 8, 16),
            nn.ReLU(),
            nn.Linear(16, num_classes) # Final disease class
        )
        
    def forward(self, img, tab):
        img_out = self.image_model(img)
        tab_out = self.tabular_model(tab)
        fused = torch.cat((img_out, tab_out), dim=1)
        return self.fusion(fused)
