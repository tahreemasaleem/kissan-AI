import io
import os
import time
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from llm_service import ChatRequest, get_botanist_response
import csv
import math

# Try importing torch and PIL, gracefully fallback if not available
try:
    import torch
    import torch.nn as nn
    from torchvision import models, transforms
    from PIL import Image
    ML_AVAILABLE = True
except ImportError as e:
    ML_AVAILABLE = False
    print(f"Warning: ML libraries not installed ({e}). Running in mock mode.")

app = FastAPI(title="Kissan AI Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None
class_names = []
device = None
transform = None

@app.on_event("startup")
def load_model():
    global model, class_names, device, transform
    if not ML_AVAILABLE:
        return
        
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    try:
        # Load the saved model dictionary
        model_path = os.path.join(os.path.dirname(__file__), "kissan_disease_model.pth")
        checkpoint = torch.load(model_path, map_location=device)
        class_names = checkpoint['class_names']
        
        # Recreate the exact ResNet-18 architecture
        model = models.resnet18(weights=None)
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, len(class_names))
        
        # Load the trained weights
        model.load_state_dict(checkpoint['state_dict'])
        model = model.to(device)
        model.eval()
        print("[OK] ML Model loaded successfully!")
    except Exception as e:
        print(f"[ERROR] Error loading ML model: {e}")
        print("Make sure kissan_disease_model.pth is in the backend folder!")

# Load crop dataset
CROP_DATA = []
try:
    csv_path = os.path.join(os.path.dirname(__file__), "..", "crop fertilizers ds", "updated_dataset.csv")
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            CROP_DATA.append(row)
    print("[OK] Crop dataset loaded successfully!")
except Exception as e:
    print(f"[ERROR] Error loading crop dataset: {e}")

@app.get("/")
def read_root():
    return {"message": "Welcome to Kissan AI API"}

DISEASE_DB = {
    "healthy": {
        "description": "Your plant appears to be in excellent condition with no visible signs of disease.",
        "symptoms": ["Vibrant green leaves", "Sturdy stems", "No visible spots or discoloration"],
        "treatment_chemical": "None required.",
        "treatment_organic": "Continue regular maintenance.",
        "prevention": "Maintain consistent watering, ensure adequate sunlight, and provide regular balanced nutrients.",
        "recommendation_ur": "آپ کا پودا بالکل صحت مند نظر آ رہا ہے! اسے برقرار رکھیں۔"
    },
    "blight": {
        "description": "Blight is a rapid and complete chlorosis, browning, then death of plant tissues such as leaves, branches, twigs, or floral organs.",
        "symptoms": ["Brown or black spots on leaves", "White fungal growth in humid conditions", "Rapid wilting and death of plant parts"],
        "treatment_chemical": "Apply fungicides containing chlorothalonil, copper fungicide, or mancozeb as soon as symptoms appear.",
        "treatment_organic": "Prune and destroy infected leaves. Spray a mixture of baking soda and horticultural oil.",
        "prevention": "Ensure good air circulation, avoid overhead watering, and practice crop rotation.",
        "recommendation_ur": "متاثرہ پتوں کو فوراً ہٹا دیں۔ مناسب پھپھوند کُش دوا (فنجی سائیڈ) استعمال کریں۔ پانی دیتے وقت پتوں کو گیلا نہ کریں۔"
    },
    "rust": {
        "description": "Rust is a fungal disease that affects many types of plants. It gets its name from the rust-colored spores that form on the leaves.",
        "symptoms": ["Yellow, orange, red, rust, or brown powdery pustules on the undersides of leaves", "Yellow spots on the upper surface of leaves", "Leaf drop"],
        "treatment_chemical": "Use fungicides containing sulfur, myclobutanil, or copper.",
        "treatment_organic": "Remove and destroy affected leaves. Apply neem oil or sulfur powder.",
        "prevention": "Water at the base of the plant to keep leaves dry. Space plants properly for good airflow.",
        "recommendation_ur": "پودے کے اوپر سے پانی دینے سے گریز کریں۔ متاثرہ پتوں کو کاٹ دیں۔ سلفر یا کاپر پر مشتمل دوا استعمال کریں۔"
    },
    "scab": {
        "description": "Scab is a fungal disease that causes lesions on leaves, stems, and fruit, significantly reducing crop quality.",
        "symptoms": ["Dark, olive-green to black, scabby spots on leaves and fruit", "Twisting and distortion of leaves"],
        "treatment_chemical": "Apply fungicides like captan, myclobutanil, or sulfur early in the season.",
        "treatment_organic": "Apply liquid copper soap or neem oil early in the season.",
        "prevention": "Rake up and dispose of fallen leaves in autumn. Prune trees to open the canopy for better air circulation.",
        "recommendation_ur": "پھلوں اور پتوں پر کالے دھبے نظر آنے پر فوری طور پر کاپر صابن یا فنجی سائیڈ کا سپرے کریں۔"
    },
    "powdery mildew": {
        "description": "Powdery mildew is a fungal disease that affects a wide range of plants, easily identifiable by its white powdery spots.",
        "symptoms": ["White or gray powdery spots, often on the upper surfaces of leaves", "Curling or distortion of leaves"],
        "treatment_chemical": "Use fungicides containing potassium bicarbonate, myclobutanil, or sulfur.",
        "treatment_organic": "Spray a solution of baking soda, liquid soap, and water, or use neem oil.",
        "prevention": "Plant resistant varieties, improve air circulation, and avoid excessive nitrogen fertilizer.",
        "recommendation_ur": "پتوں پر سفید پاؤڈر نظر آئے تو بیکنگ سوڈا اور پانی کا مکسچر سپرے کریں، یا مناسب فنجی سائیڈ استعمال کریں۔"
    },
    "rot": {
        "description": "Rot refers to various bacterial or fungal diseases that cause the decay of plant tissues, particularly roots and fruits.",
        "symptoms": ["Soft, mushy areas on fruit or stems", "Foul odor", "Dark, sunken lesions"],
        "treatment_chemical": "Chemical treatments are often ineffective once rot sets in; copper fungicides can be used preventatively.",
        "treatment_organic": "Remove and destroy affected parts immediately to prevent spread.",
        "prevention": "Ensure well-draining soil, avoid overwatering, and harvest fruits promptly.",
        "recommendation_ur": "گلنے سڑنے والے حصوں کو فوراً ہٹا دیں۔ پانی کی زیادتی سے بچیں اور مٹی کی نکاسی کو بہتر بنائیں۔"
    }
}

@app.post("/predict-disease")
async def predict_disease(file: UploadFile = File(...)):
    # Fallback to mock if ML libraries aren't installed or model failed to load
    if not ML_AVAILABLE or model is None:
        time.sleep(2)
        return {
            "filename": file.filename,
            "prediction": "Mock Prediction (PyTorch not installed)",
            "confidence": 0.99,
            "disease_info": {
                "description": "This is a mock response because machine learning libraries are not installed.",
                "symptoms": ["N/A"],
                "treatment_chemical": "N/A",
                "treatment_organic": "N/A",
                "prevention": "Please install torch, torchvision, and Pillow to use real AI."
            },
            "recommendation_ur": "براہ کرم اصلی AI استعمال کرنے کے لیے torch اور torchvision انسٹال کریں۔"
        }

    try:
        # Read uploaded image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # Transform the image
        img_t = transform(image)
        batch_t = torch.unsqueeze(img_t, 0).to(device)
        
        # Run inference
        with torch.no_grad():
            outputs = model(batch_t)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)[0]
            confidence, predicted_idx = torch.max(probabilities, 0)
            
        predicted_class = class_names[predicted_idx.item()]
        
        # Clean up the class name (e.g. "Tomato___Early_blight" -> "Tomato Early blight")
        clean_name = predicted_class.replace("___", " - ").replace("_", " ")
        clean_lower = clean_name.lower()
        
        # Determine disease details based on keywords
        matched_disease = None
        for key in DISEASE_DB.keys():
            if key in clean_lower:
                matched_disease = DISEASE_DB[key]
                break
                
        # Default fallback if no keyword matches
        if not matched_disease:
            matched_disease = {
                "description": f"The model detected {clean_name}, but detailed information is not available in our database yet.",
                "symptoms": ["Observe the plant for unusual spots, wilting, or discoloration."],
                "treatment_chemical": "Consult a local agricultural expert for specific chemical treatments.",
                "treatment_organic": "Remove heavily affected parts. Apply broad-spectrum organic treatments like neem oil as a precaution.",
                "prevention": "Maintain optimal growing conditions, proper watering, and good airflow.",
                "recommendation_ur": "اس حالت کے لیے مقامی زرعی ماہر سے مشورہ کریں۔"
            }
            
        return {
            "filename": file.filename,
            "prediction": clean_name,
            "confidence": confidence.item(),
            "disease_info": matched_disease,
            "recommendation_ur": matched_disease.get("recommendation_ur", "اس حالت کے لیے مقامی زرعی ماہر سے مشورہ کریں۔")
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.post("/chat")
async def chat_with_botanist(request: ChatRequest):
    try:
        response_text = get_botanist_response(request)
        return {"response": response_text}
    except Exception as e:
        return {"error": str(e)}

@app.get("/crops")
def get_all_crops():
    return {"crops": [crop["Crop_Name"] for crop in CROP_DATA]}

@app.get("/crop/{crop_name}")
def get_crop_info(crop_name: str):
    for crop in CROP_DATA:
        if crop["Crop_Name"].lower() == crop_name.lower():
            return crop
    return {"error": "Crop not found"}

if __name__ == "__main__":
    import uvicorn
    print("\nStarting Kissan AI Backend Server...\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
