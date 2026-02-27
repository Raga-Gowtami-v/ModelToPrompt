from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

# Map spaCy entity labels to PII types
ENTITY_PII_MAP = {
    "PERSON": "PERSON_NAME",
    "ORG": "ORGANIZATION",
    "GPE": "LOCATION",
    "LOC": "LOCATION",
    "DATE": "DATE",
    "MONEY": "FINANCIAL",
    "CARDINAL": "NUMBER",
}


class NERDetector:
    def __init__(self, model_name: str = "en_core_web_sm"):
        self.nlp = None
        try:
            import spacy
            self.nlp = spacy.load(model_name)
        except ModuleNotFoundError:
            logger.warning("spaCy is not installed. NER detection is disabled.")
        except OSError:
            try:
                from spacy.cli import download
                download(model_name)
                import spacy
                self.nlp = spacy.load(model_name)
            except Exception as exc:
                logger.warning("Failed to load/download spaCy model '%s'. NER detection is disabled. %s", model_name, exc)

    def detect(self, text: str) -> List[Dict]:
        """Detect PII entities using spaCy NER."""
        if self.nlp is None:
            return []

        doc = self.nlp(text)
        detections = []
        for ent in doc.ents:
            pii_type = ENTITY_PII_MAP.get(ent.label_)
            if pii_type:
                detections.append({
                    "type": pii_type,
                    "value": ent.text,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "confidence": 0.80,
                    "detector": "ner",
                })
        return detections
