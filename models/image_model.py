import torch
import torch.nn as nn
from torchvision import models

class ImageModel(nn.Module):
    def __init__(self, num_classes=5):
        super(ImageModel, self).__init__()
        # Use ResNet18 as per requirements
        self.resnet = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        # Replace final layer
        in_features = self.resnet.fc.in_features
        self.resnet.fc = nn.Linear(in_features, num_classes)

    def forward(self, x):
        return self.resnet(x)
