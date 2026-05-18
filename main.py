import io
import torch
from fastapi import FastAPI, File, UploadFile
from torchvision import models, transforms
from PIL import Image

app = FastAPI(
    title="MLOPS ResNet API",
    description="A simple API for classifying images using ResNet",
    version="1.0",
)

print("Loading model...")
try:
    model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    model.eval()
    print("Model loaded.")

except Exception as e:
    print(f"Error loading model: {e}")
    exit(1)

preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

@app.get("/")
def read_root():
    return {"message": "Welcome to the MLOPS ResNet API! Send an image to endpoint /predict"}

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        input_tensor = preprocess(image)
        input_batch = input_tensor.unsqueeze(0)

        with torch.no_grad():
            output = model(input_batch)
            _, predicted_idx = torch.max(output.data, 1)
        return {
            "filename": file.filename,
            "predicted_class_id": predicted_idx.item()
        }
    except Exception as e:
        return {"error": str(e)}
