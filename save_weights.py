import torch
import os
from models.fusion_model import MultimodalFusion

os.makedirs("weights", exist_ok=True)
model = MultimodalFusion()

# Save random initialized weights as "dummy" weights
torch.save(model.state_dict(), "weights/multimodal_fusion_demo.pt")
print("Saved dummy weights to weights/multimodal_fusion_demo.pt")
