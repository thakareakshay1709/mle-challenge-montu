import spacy
from spacy.util import minibatch, compounding
from spacy.training import Example
import random
import logging
import os
from typing import List, Dict, Any, Tuple
import re

class PIIModelTrainer:
    def __init__(self, model_path: str = "models/pii_ner"):
        self.model_path = model_path
        self.nlp = None
        self._initialize_model()
        
    def _initialize_model(self):
        """Initialize or load the model"""
        if os.path.exists(self.model_path):
            self.nlp = spacy.load(self.model_path)
        else:
            self.nlp = spacy.load("en_core_web_sm")
            # Disable all pipes except NER
            disabled_pipes = [pipe for pipe in self.nlp.pipe_names if pipe != "ner"]
            # Also disable lookups if it exists
            if "lookups" in self.nlp.pipe_names:
                disabled_pipes.append("lookups")
            self.nlp.disable_pipes(disabled_pipes)

    def prepare_training_data(self, training_data: List[Dict[str, str]]) -> List[Tuple[str, List[Tuple[int, int, str]]]]:
        """Convert training data to spaCy format"""
        formatted_data = []
        for item in training_data:
            text = item['text']
            redacted_text = item['redacted_text']
            
            # Extract entities from redacted text
            entities = []
            # Find category markers in the redacted text
            for match in re.finditer(r'\[(.*?)\]', redacted_text):
                start_idx = match.start()
                end_idx = match.end()
                category = match.group(1)
                entities.append((start_idx, end_idx, category))
            
            formatted_data.append((text, entities))
        return formatted_data

    def train(self, training_data: List[Dict[str, str]], iterations: int = 20) -> Dict[str, Any]:
        """Train the model with new data"""
        if not training_data:
            raise ValueError("Training data cannot be empty")

        # Prepare training data
        training_data_formatted = self.prepare_training_data(training_data)
        
        # Add new labels
        for _, entities in training_data_formatted:
            for _, _, label in entities:
                if label not in self.nlp.get_pipe("ner").labels:
                    self.nlp.get_pipe("ner").add_label(label)

        # Get other pipes to disable during training
        other_pipes = [pipe for pipe in self.nlp.pipe_names if pipe != "ner"]

        # Train the model
        with self.nlp.disable_pipes(*other_pipes):
            optimizer = self.nlp.create_optimizer()
            
            for iteration in range(iterations):
                random.shuffle(training_data_formatted)
                losses = {}
                
                # Batch up the examples using spaCy's minibatch
                batches = minibatch(training_data_formatted, size=compounding(4.0, 32.0, 1.001))
                
                for batch in batches:
                    for text, entities in batch:
                        doc = self.nlp.make_doc(text)
                        example = Example.from_dict(doc, {"entities": entities})
                        self.nlp.update([example], sgd=optimizer, losses=losses)
                
                logging.info(f"Iteration {iteration + 1} Losses: {losses}")

        # Save the model
        self.nlp.to_disk(self.model_path)
        return {"message": "Training completed successfully", "losses": losses}

    def evaluate(self, test_data: List[Dict[str, str]]) -> Dict[str, Any]:
        """Evaluate the model's performance"""
        if not test_data:
            raise ValueError("Test data cannot be empty")

        metrics = {
            "accuracy": 0,
            "precision": {},
            "recall": {},
            "f1": {}
        }

        total_entities = 0
        correct_entities = 0
        category_metrics = {}

        for item in test_data:
            text = item['text']
            doc = self.nlp(text)
            
            # Get true entities from redacted text
            true_entities = []
            for match in re.finditer(r'\[(.*?)\]', item['redacted_text']):
                category = match.group(1)
                true_entities.append(category)

            # Get predicted entities
            pred_entities = [ent.label_ for ent in doc.ents]

            # Update metrics
            for category in set(true_entities + pred_entities):
                if category not in category_metrics:
                    category_metrics[category] = {
                        "tp": 0, "fp": 0, "fn": 0
                    }

            # Calculate true positives, false positives, and false negatives
            for true_ent in true_entities:
                if true_ent in pred_entities:
                    category_metrics[true_ent]["tp"] += 1
                else:
                    category_metrics[true_ent]["fn"] += 1

            for pred_ent in pred_entities:
                if pred_ent not in true_entities:
                    category_metrics[pred_ent]["fp"] += 1

            total_entities += len(true_entities)
            correct_entities += len(set(true_entities).intersection(pred_entities))

        # Calculate overall accuracy
        metrics["accuracy"] = correct_entities / total_entities if total_entities > 0 else 0

        # Calculate per-category metrics
        for category, counts in category_metrics.items():
            tp = counts["tp"]
            fp = counts["fp"]
            fn = counts["fn"]
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            metrics["precision"][category] = precision
            metrics["recall"][category] = recall
            metrics["f1"][category] = f1

        return metrics
