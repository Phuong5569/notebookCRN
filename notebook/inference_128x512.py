#!/usr/bin/env python3
"""
Inference script for model trained with IMG_HEIGHT=128, IMG_WIDTH=512
"""
import torch
from torchvision import transforms
from PIL import Image
import argparse

# Import from training script
from handwriting_ocr_train import CRNN, NUM_CLASSES, IDX_TO_CHAR, BLANK_IDX, resize_with_padding

# CRITICAL: Match your training settings
IMG_HEIGHT = 128
IMG_WIDTH = 512
HIDDEN_SIZE = 256


def predict(model, image_path, device):
    """Predict text from image"""
    # Load and preprocess
    image = Image.open(image_path).convert('RGB')
    image = resize_with_padding(image, IMG_HEIGHT, IMG_WIDTH)
    
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    image = transform(image).unsqueeze(0).to(device)
    
    # Predict
    model.eval()
    with torch.no_grad():
        output = model(image)
        output = output.squeeze(1)
        
        # Decode
        _, max_indices = torch.max(output, dim=1)
        decoded = []
        prev_idx = -1
        for idx in max_indices.cpu().numpy():
            if idx != BLANK_IDX and idx != prev_idx:
                if idx in IDX_TO_CHAR:
                    decoded.append(IDX_TO_CHAR[idx])
            prev_idx = idx
        
        return ''.join(decoded)


def main():
    parser = argparse.ArgumentParser(description='Inference for 128×512 model')
    parser.add_argument('--image', type=str, required=True, help='Path to image')
    parser.add_argument('--model', type=str, default='best_model.pth', help='Model checkpoint')
    args = parser.parse_args()
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    print("="*60)
    print("Loading model trained with:")
    print(f"  IMG_HEIGHT = {IMG_HEIGHT}")
    print(f"  IMG_WIDTH = {IMG_WIDTH}")
    print(f"  HIDDEN_SIZE = {HIDDEN_SIZE}")
    print("="*60)
    
    # Load model with correct dimensions
    model = CRNN(img_height=IMG_HEIGHT, num_classes=NUM_CLASSES, hidden_size=HIDDEN_SIZE)
    
    checkpoint = torch.load(args.model, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(device)
    
    print(f"Model loaded from: {args.model}")
    print(f"Epoch: {checkpoint.get('epoch', 'N/A')}")
    print(f"Val loss: {checkpoint.get('val_loss', 'N/A')}")
    print()
    
    # Predict
    prediction = predict(model, args.image, device)
    
    print(f"Predicted text: {prediction}")
    print()


if __name__ == "__main__":
    main()
