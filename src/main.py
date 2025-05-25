from fastapi import FastAPI, HTTPException, Depends
from typing import Dict, Any, List
import spacy
import os
from pydantic import BaseModel
from training_pipeline import PIIModelTrainer
from training_data import load_data

redact_app = FastAPI(title="PII Redaction Service")

# Initialize the model trainer
trainer = PIIModelTrainer()

# Load the trained model or pre-trained model
trained_model_path = "models/pii_ner"
if os.path.exists(trained_model_path):
    nlp = spacy.load(trained_model_path)
else:
    nlp = spacy.load("en_core_web_sm")

class PIIRequest(BaseModel):
    text: str

class TrainingData(BaseModel):
    training_data: List[Dict[str, str]] = []
    iterations: int = 20

class EvaluationData(BaseModel):
    test_data: List[Dict[str, str]]

def get_trainer():
    return trainer


def redact_pii(text: str) -> str:
    """
    Redact PII from the input text using spaCy NER.
    """
    # Process the text with spaCy
    doc = nlp(text)
    
    # Create a mapping of entity spans to their categories
    entities = []
    for ent in doc.ents:
        entities.append((ent.start_char, ent.end_char, ent.label_))
    
    # Sort entities by start position in reverse order to avoid index shifting
    entities.sort(key=lambda x: x[0], reverse=True)
    
    # Replace entities with their categories
    for start, end, category in entities:
        text = text[:start] + f"[{category}]" + text[end:]
    
    return text

@redact_app.post("/redact", response_model=Dict[str, Any])
async def redact_pii_endpoint(request: PIIRequest):
    """
    Endpoint to redact PII from text.
    """
    try:
        redacted_text = redact_pii(request.text)
        return {"redacted_text": redacted_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@redact_app.post("/train", response_model=Dict[str, Any])
async def train_endpoint(request: TrainingData, trainer: PIIModelTrainer = Depends(get_trainer)):
    """
    Endpoint to train the model with new data.
    """
    try:
        # Use provided training data or default data if none provided
        default_training_data = load_data()
        training_data = request.training_data if request.training_data else default_training_data['training_data']
        result = trainer.train(training_data, request.iterations)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@redact_app.post("/evaluate", response_model=Dict[str, Any])
async def evaluate_endpoint(request: EvaluationData, trainer: PIIModelTrainer = Depends(get_trainer)):
    """
    Endpoint to evaluate the model's performance.
    """
    try:
        metrics = trainer.evaluate(request.test_data)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(redact_app, host="0.0.0.0", port=8000)
