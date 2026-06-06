import numpy as np
from PIL import Image
import io
import matplotlib.pyplot as plt

def generate_simulated_gradcam(image: Image.Image) -> Image.Image:
    """
    Generates a simulated Grad-CAM heatmap overlay restricted to typical lung regions.
    """
    img_rgb = image.convert("RGB")
    w, h = img_rgb.size
    
    heatmap = np.zeros((h, w), dtype=np.float32)
    
    # Define Typical Lung Bounding Box (Anatomical Approximation)
    # X-axis: 15% to 85% of width
    # Y-axis: 20% to 80% of height
    
    # Create Lung Regions (Left and Right Lobes)
    # We avoid the central part (mediastinum/heart)
    for side in [-1, 1]: # -1 for Left, 1 for Right (relative to center)
        # Center of the lobe
        cx = w // 2 + side * (w // 4)
        cy = h // 2
        
        # Spread
        sigma_x = w // 8
        sigma_y = h // 4
        
        y, x = np.ogrid[-cy:h-cy, -cx:w-cx]
        
        # Create an elliptical Gaussian blob for the lung
        lung_blob = np.exp(-( (x*x)/(2.*sigma_x**2) + (y*y)/(2.*sigma_y**2) ))
        
        # Add a "lesion" or "affected area" inside this lung
        # For simulation, we pick a random point within this lobe
        lx = cx + np.random.randint(-w//10, w//10)
        ly = cy + np.random.randint(-h//6, h//6)
        lsig = np.random.randint(min(h,w)//15, min(h,w)//8)
        
        yy, xx = np.ogrid[-ly:h-ly, -lx:w-lx]
        lesion_blob = np.exp(-(xx*xx + yy*yy) / (2. * lsig**2))
        
        # Restrict the lesion intensity by the lung shape
        heatmap = np.maximum(heatmap, lesion_blob * lung_blob)
        
    # Apply JET colormap
    cmap = plt.get_cmap('jet')
    heatmap_colored = cmap(heatmap)
    
    # Convert to RGB uint8
    heatmap_colored = (heatmap_colored[:, :, :3] * 255).astype(np.uint8)
    heatmap_img = Image.fromarray(heatmap_colored)
    
    # Overlay with slightly higher alpha for "well highlighted" look
    overlay = Image.blend(img_rgb, heatmap_img, alpha=0.5)
    
    return overlay

