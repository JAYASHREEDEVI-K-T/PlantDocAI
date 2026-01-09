import os
import io
import json
import logging
from typing import Optional, Union
import time
from dotenv import load_dotenv

import torch
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from torchvision import transforms
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from models.ImageClassificationModel import CNNModel
from recommendation_engine import RecommendationEngine, UserFeedback
from simple_gpt_engine import SimpleGPTEngine

# Load environment variables from .env file
load_dotenv()

# ----------------- Configuration -----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI(
    title="🌿 Plant Disease Detection API",
    version="3.0.0",
    description="Advanced plant disease detection with AI-powered recommendations"
)

# ----------------- CORS Middleware -----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Paths -----------------
LABELS_IMAGE_PATH = os.path.join("models", "plant_disease_classes.json")
LABELS_TEXT_PATH = os.path.join("models", "labels_text_model.json")
IMAGE_MODEL_WEIGHTS = os.path.join("models", "cnn_model_weights.pth")
TEXT_MODEL_PATH = "text_classification_model"
KNOWLEDGE_BASE_PATH = os.path.join("models", "disease_knowledge_base.json")

# ----------------- Helpers -----------------
def load_labels(path: str) -> Optional[Union[list, dict]]:
    """Load labels JSON and return as-is"""
    if not os.path.exists(path):
        logging.warning(f"Labels file not found: {path}")
        return None
    with open(path, "r", encoding="utf-8") as f:
        labels = json.load(f)
    
    try:
        length = len(labels)
    except Exception:
        length = None
    logging.info(f"Loaded labels from {path} (type={type(labels)}, len={length})")
    return labels

# ----------------- Load labels -----------------
image_class_labels = load_labels(LABELS_IMAGE_PATH)
text_class_labels = load_labels(LABELS_TEXT_PATH)

# ----------------- Initialize Recommendation Engine with YOUR MODEL PRIORITY -----------------
class HybridRecommendationEngine:
    """Hybrid engine: YOUR MODEL FIRST, GPT as fallback"""
    
    def __init__(self, 
                 knowledge_base_path: str,
                 openai_api_key: Optional[str] = None,
                 enable_cache: bool = True,
                 enable_analytics: bool = True,
                 max_retries: int = 3):
        
        self.max_retries = max_retries
        self.gpt_engine = None
        self.current_engine_type = "initializing"
        
        # Initialize YOUR recommendation engine (ALWAYS PRIORITY)
        try:
            self.primary_engine = RecommendationEngine(
                knowledge_base_path=knowledge_base_path,
                enable_cache=enable_cache,
                enable_analytics=enable_analytics,
                cache_size=1000
            )
            logger.info("✅ PRIMARY: Your recommendation engine initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize primary engine: {e}")
            raise RuntimeError("Could not initialize recommendation system")
        
        # Initialize GPT as BACKUP/ENHANCEMENT only
        if openai_api_key:
            try:
                self.gpt_engine = SimpleGPTEngine(
                    api_key=openai_api_key,
                    model="gpt-4o-mini"
                )
                
                if self.gpt_engine.use_gpt:
                    self.current_engine_type = "your_model_with_gpt_backup"
                    logger.info("✅ GPT available as backup/enhancement")
                else:
                    self.current_engine_type = "your_model_only"
                    logger.info("ℹ️ GPT not available, using your model only")
                    
            except Exception as e:
                logger.warning(f"⚠️ GPT initialization failed: {e}")
                self.gpt_engine = None
                self.current_engine_type = "your_model_only"
        else:
            self.current_engine_type = "your_model_only"
            logger.info("ℹ️ No API key, using your model only")
    
    def generate_recommendation(self, 
                               disease_class: str, 
                               confidence: float,
                               plant_type: Optional[str] = None,
                               language: str = "en",
                               user_location: Optional[str] = None) -> dict:
        """Generate recommendation: YOUR MODEL FIRST, GPT as enhancement/fallback"""
        
        # ALWAYS USE YOUR MODEL FIRST
        try:
            logger.info(f"🎯 Using YOUR MODEL for {disease_class}")
            result = self.primary_engine.generate_recommendation(
                disease_class=disease_class,
                confidence=confidence,
                plant_type=plant_type,
                language=language,
                user_location=user_location
            )
            result['engine_used'] = 'your_model'
            result['primary_source'] = 'knowledge_base'
            
            # Check if your model has good data
            has_complete_data = all([
                result.get('symptoms'),
                result.get('treatment'),
                result.get('prevention')
            ])
            
            # OPTIONAL: Use GPT to ENHANCE (not replace) if available and data is incomplete
            if not has_complete_data and self.gpt_engine and self.gpt_engine.use_gpt:
                try:
                    logger.info(f"   → Enhancing with GPT for incomplete data...")
                    
                    # Parse disease class
                    parts = disease_class.split("___")
                    if len(parts) == 2:
                        plant = parts[0].replace("_", " ")
                        disease = parts[1].replace("_", " ")
                    else:
                        plant = plant_type or "Unknown"
                        disease = disease_class.replace("_", " ")
                    
                    gpt_result = self.gpt_engine.generate_recommendation(plant, disease, confidence)
                    
                    # MERGE: Keep your model's data, fill gaps with GPT
                    for field in ['symptoms', 'treatment', 'prevention', 'organic_solutions', 
                                 'chemical_solutions', 'care_instructions']:
                        if not result.get(field) and gpt_result.get(field):
                            if isinstance(gpt_result[field], list):
                                result[field] = "\n".join([f"• {item}" for item in gpt_result[field]])
                            else:
                                result[field] = gpt_result[field]
                    
                    result['engine_used'] = 'your_model_enhanced_by_gpt'
                    result['enhancement'] = 'gpt_filled_gaps'
                    logger.info(f"   ✅ Enhanced with GPT")
                    
                except Exception as e:
                    logger.warning(f"   ⚠️ GPT enhancement failed: {e}, keeping your model data")
            
            logger.info(f"✅ Recommendation generated by YOUR MODEL")
            return result
            
        except Exception as e:
            logger.error(f"❌ Your model failed: {e}")
            
            # ONLY use GPT if YOUR MODEL completely fails
            if self.gpt_engine and self.gpt_engine.use_gpt:
                try:
                    logger.warning(f"⚠️ Falling back to GPT as last resort")
                    
                    parts = disease_class.split("___")
                    if len(parts) == 2:
                        plant = parts[0].replace("_", " ")
                        disease = parts[1].replace("_", " ")
                    else:
                        plant = plant_type or "Unknown"
                        disease = disease_class.replace("_", " ")
                    
                    result = self.gpt_engine.generate_recommendation(plant, disease, confidence)
                    
                    # Format lists
                    for field in ['symptoms', 'treatment', 'prevention', 'organic_solutions', 
                                 'chemical_solutions', 'care_instructions']:
                        if field in result and isinstance(result[field], list):
                            result[field] = "\n".join([f"• {item}" for item in result[field]])
                    
                    result['engine_used'] = 'gpt_emergency_fallback'
                    result['warning'] = 'primary_model_failed'
                    return result
                    
                except Exception as e2:
                    logger.error(f"❌ GPT fallback also failed: {e2}")
            
            # Last resort: generic response
            return {
                'disease': disease_class.replace('_', ' '),
                'severity': 'unknown',
                'description': 'Unable to generate detailed recommendations',
                'error': str(e),
                'engine_used': 'error_response'
            }
    
    # Delegate methods to YOUR engine
    def submit_feedback(self, feedback): 
        return self.primary_engine.submit_feedback(feedback)
    
    def get_popular_diseases(self, limit=10): 
        return self.primary_engine.get_popular_diseases(limit)
    
    def get_analytics_report(self): 
        return self.primary_engine.get_analytics_report()
    
    def save_knowledge_base(self, path): 
        return self.primary_engine.save_knowledge_base(path)
    
    def save_analytics(self): 
        if self.primary_engine.analytics:
            self.primary_engine.save_analytics()
    
    def clear_cache(self): 
        if self.primary_engine.cache:
            self.primary_engine.clear_cache()
    
    @property
    def cache(self): 
        return self.primary_engine.cache
    
    @property
    def analytics(self): 
        return self.primary_engine.analytics
    
    @property
    def knowledge_base(self): 
        return self.primary_engine.knowledge_base

# Initialize hybrid recommendation engine
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY:
    logger.info("🔑 OpenAI API key found, GPT available as backup")
else:
    logger.info("ℹ️ No OpenAI API key, using your model only")

recommendation_engine = HybridRecommendationEngine(
    knowledge_base_path=KNOWLEDGE_BASE_PATH,
    openai_api_key=OPENAI_API_KEY,
    enable_cache=True,
    enable_analytics=True,
    max_retries=3
)

logger.info(f"✅ Recommendation engine initialized: {recommendation_engine.current_engine_type}")
logger.info(f"🎯 PRIORITY: Your model always used first!")

# ----------------- Device -----------------
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
logger.info(f"Using device: {device}")

# ----------------- Image model load -----------------
image_model = None
try:
    if image_class_labels is None:
        num_image_classes = 15
    elif isinstance(image_class_labels, dict):
        num_image_classes = len(image_class_labels)
    elif isinstance(image_class_labels, list):
        num_image_classes = len(image_class_labels)
    else:
        num_image_classes = 15

    image_model = CNNModel(num_classes=num_image_classes)
    state = torch.load(IMAGE_MODEL_WEIGHTS, map_location=device)
    
    if isinstance(state, dict) and "state_dict" in state and isinstance(state["state_dict"], dict):
        image_model.load_state_dict(state["state_dict"])
    else:
        image_model.load_state_dict(state)
    
    image_model.to(device)
    image_model.eval()
    logger.info("✅ Image classification model loaded successfully")
except Exception as e:
    logger.exception(f"❌ Error loading image model: {e}")
    image_model = None

# ----------------- Image preprocessing -----------------
MEAN = [0.4760, 0.5004, 0.4266]
STD  = [0.1775, 0.1509, 0.1960]

image_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=MEAN, std=STD)
])

# ----------------- Text model load -----------------
text_model = None
tokenizer = None
try:
    tokenizer = AutoTokenizer.from_pretrained(TEXT_MODEL_PATH)
    text_model = AutoModelForSequenceClassification.from_pretrained(TEXT_MODEL_PATH)
    text_model.to(device)
    text_model.eval()
    logger.info("✅ Text classification model loaded successfully")
except Exception as e:
    logger.exception(f"❌ Error loading text model: {e}")
    text_model = None

# ----------------- Utility Functions -----------------
def labels_length(labels: Optional[Union[list, dict]]) -> Optional[int]:
    if labels is None:
        return None
    try:
        return len(labels)
    except Exception:
        return None

def get_label_by_index(labels: Optional[Union[list, dict]], idx: int) -> str:
    """Safely get label by index"""
    if labels is None:
        return str(idx)
    try:
        if isinstance(labels, list):
            return labels[idx]
        elif isinstance(labels, dict):
            if idx in labels:
                return labels[idx]
            sidx = str(idx)
            return labels.get(sidx, str(idx))
        else:
            return str(idx)
    except Exception:
        logger.exception("Error fetching label by index")
        return str(idx)

# ----------------- Endpoints -----------------
@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "🌿 Plant Disease Detection API",
        "version": "3.0.0",
        "features": [
            "Image Classification",
            "Text Classification", 
            "AI Recommendations - YOUR MODEL FIRST",
            "GPT as Enhancement/Fallback",
            "Analytics & Feedback System",
            "Multi-language Support"
        ],
        "recommendation_priority": "your_model_first_then_gpt",
        "recommendation_engine": recommendation_engine.current_engine_type,
        "endpoints": {
            "health_check": "/health-check",
            "predict_image": "/predict/image",
            "predict_text": "/predict/text",
            "get_recommendation": "/recommend/{disease_class}",
            "submit_feedback": "/feedback",
            "analytics": "/analytics",
            "popular_diseases": "/analytics/popular",
            "save_knowledge_base": "/recommend/save",
            "clear_cache": "/cache/clear"
        }
    }

@app.get("/health-check")
def health_check():
    """Health check endpoint"""
    cache_info = None
    if recommendation_engine.cache:
        cache_info = {
            "size": len(recommendation_engine.cache.cache),
            "hits": sum(recommendation_engine.cache.access_count.values())
        }
    
    return {
        "status": "ok", 
        "message": "API running successfully",
        "models": {
            "image_model": "loaded" if image_model is not None else "not loaded",
            "text_model": "loaded" if text_model is not None else "not loaded",
            "recommendation_engine": recommendation_engine.current_engine_type,
            "priority": "your_model_first"
        },
        "cache": cache_info,
        "analytics_enabled": recommendation_engine.analytics is not None,
        "gpt_available": recommendation_engine.gpt_engine is not None and recommendation_engine.gpt_engine.use_gpt,
        "your_model_available": recommendation_engine.primary_engine is not None
    }

@app.post("/predict/image")
async def predict_image(
    file: UploadFile = File(...), 
    include_recommendations: bool = True,
    language: str = "en",
    user_location: Optional[str] = None
):
    """Predict plant disease from image with YOUR MODEL recommendations first"""
    if image_model is None:
        raise HTTPException(status_code=500, detail="Image model not loaded")

    try:
        image = Image.open(io.BytesIO(await file.read())).convert("RGB")
    except Exception as e:
        logger.error(f"Invalid image file: {e}")
        raise HTTPException(status_code=400, detail="Invalid image file")

    # Preprocess and predict
    image_tensor = image_transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = image_model(image_tensor)
        probs = torch.softmax(outputs, dim=1)[0]
        top_idx = int(torch.argmax(probs).item())
        top_prob = float(probs[top_idx])

    top_label = get_label_by_index(image_class_labels, top_idx)

    response = {
        "prediction": top_label,
        "class_index": top_idx,
        "confidence": round(top_prob, 4),
        "model_type": "image_classification"
    }

    # Add recommendations from YOUR MODEL first
    if include_recommendations:
        try:
            recommendations = recommendation_engine.generate_recommendation(
                disease_class=top_label,
                confidence=top_prob,
                language=language,
                user_location=user_location
            )
            response["recommendations"] = recommendations
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            response["recommendations"] = {
                "error": "Could not generate recommendations",
                "details": str(e)
            }

    return JSONResponse(response)

@app.post("/predict/text")
async def predict_text(
    text: str = Form(...), 
    include_recommendations: bool = True,
    language: str = "en",
    user_location: Optional[str] = None
):
    """Predict plant disease from text with YOUR MODEL recommendations first"""
    if text_model is None or tokenizer is None:
        raise HTTPException(status_code=500, detail="Text model/tokenizer not loaded")
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text input required")

    # Tokenize and predict
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        logits = text_model(**inputs).logits
        probs = torch.softmax(logits, dim=1)[0]
        pred_idx = int(torch.argmax(probs).item())
        confidence = float(probs[pred_idx])

    pred_label = get_label_by_index(text_class_labels, pred_idx)

    response = {
        "prediction": pred_label,
        "class_index": pred_idx,
        "confidence": round(confidence, 4),
        "input_text": text,
        "model_type": "text_classification"
    }

    # Add recommendations from YOUR MODEL first
    if include_recommendations:
        try:
            recommendations = recommendation_engine.generate_recommendation(
                disease_class=pred_label,
                confidence=confidence,
                language=language,
                user_location=user_location
            )
            response["recommendations"] = recommendations
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            response["recommendations"] = {
                "error": "Could not generate recommendations",
                "details": str(e)
            }

    return JSONResponse(response)

@app.get("/recommend/{disease_class}")
async def get_recommendation(
    disease_class: str,
    confidence: float = 0.95,
    language: str = "en",
    user_location: Optional[str] = None
):
    """Get standalone recommendations for a disease"""
    try:
        recommendations = recommendation_engine.generate_recommendation(
            disease_class=disease_class,
            confidence=confidence,
            language=language,
            user_location=user_location
        )
        return JSONResponse(recommendations)
    except Exception as e:
        logger.exception(f"Error generating recommendations: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error generating recommendations: {str(e)}"
        )

@app.post("/feedback")
async def submit_feedback(
    disease_class: str = Form(...),
    recommendation_id: str = Form(...),
    rating: int = Form(...),
    was_helpful: bool = Form(...),
    user_comment: Optional[str] = Form(None)
):
    """Submit user feedback for recommendations"""
    if not (1 <= rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    try:
        feedback = UserFeedback(
            disease_class=disease_class,
            recommendation_id=recommendation_id,
            rating=rating,
            was_helpful=was_helpful,
            user_comment=user_comment
        )
        
        recommendation_engine.submit_feedback(feedback)
        
        return JSONResponse({
            "status": "success",
            "message": "Thank you for your feedback!",
            "feedback": {
                "disease_class": disease_class,
                "rating": rating,
                "was_helpful": was_helpful
            }
        })
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Error submitting feedback: {str(e)}")

@app.get("/analytics")
async def get_analytics():
    """Get comprehensive analytics report"""
    try:
        report = recommendation_engine.get_analytics_report()
        return JSONResponse(report)
    except Exception as e:
        logger.error(f"Error generating analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating analytics: {str(e)}")

@app.get("/analytics/popular")
async def get_popular_diseases(limit: int = 10):
    """Get most frequently detected diseases"""
    try:
        popular = recommendation_engine.get_popular_diseases(limit=limit)
        return JSONResponse({
            "popular_diseases": [
                {"disease": disease, "count": count}
                for disease, count in popular
            ]
        })
    except Exception as e:
        logger.error(f"Error fetching popular diseases: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recommend/save")
async def save_knowledge_base():
    """Save current knowledge base to file"""
    try:
        recommendation_engine.save_knowledge_base(KNOWLEDGE_BASE_PATH)
        recommendation_engine.save_analytics()
        
        return JSONResponse({
            "status": "success",
            "message": f"Knowledge base and analytics saved",
            "knowledge_base_path": KNOWLEDGE_BASE_PATH,
            "entries": len(recommendation_engine.knowledge_base)
        })
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving: {str(e)}")

@app.post("/cache/clear")
async def clear_cache():
    """Clear recommendation cache"""
    try:
        recommendation_engine.clear_cache()
        return JSONResponse({
            "status": "success",
            "message": "Cache cleared successfully"
        })
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ----------------- Shutdown Event -----------------
@app.on_event("shutdown")
async def shutdown_event():
    """Save analytics on shutdown"""
    try:
        recommendation_engine.save_analytics()
        logger.info("✅ Analytics saved on shutdown")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# ----------------- Run -----------------

# uvicorn main:app --reload --host localhost --port 8000
