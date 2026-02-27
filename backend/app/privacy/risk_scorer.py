from typing import List, Dict

# Risk weights by PII type (0.0 - 1.0)
RISK_WEIGHTS = {
    "SSN": 1.0,
    "CREDIT_CARD": 1.0,
    "AADHAAR": 1.0,
    "PAN": 0.9,
    "EMAIL": 0.6,
    "PHONE": 0.6,
    "PERSON_NAME": 0.5,
    "DATE_OF_BIRTH": 0.7,
    "IP_ADDRESS": 0.4,
    "LOCATION": 0.3,
    "ORGANIZATION": 0.2,
    "DATE": 0.2,
    "FINANCIAL": 0.7,
    "NUMBER": 0.1,
}


class RiskScorer:
    """Calculate overall PII risk score for a document."""

    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or RISK_WEIGHTS

    def score(self, detections: List[Dict]) -> Dict:
        """Compute risk score from a list of PII detections.

        Returns a dict with overall score, risk level, and per-type breakdown.
        """
        if not detections:
            return {"score": 0.0, "level": "LOW", "breakdown": {}}

        type_counts = {}
        for det in detections:
            pii_type = det["type"]
            type_counts[pii_type] = type_counts.get(pii_type, 0) + 1

        # Weighted score: sum of (weight * count) normalized
        weighted_sum = sum(
            self.weights.get(t, 0.5) * count for t, count in type_counts.items()
        )
        max_possible = sum(
            self.weights.get(t, 0.5) * count for t, count in type_counts.items()
        )
        overall_score = min(weighted_sum / max(len(detections), 1), 1.0)

        # Determine risk level
        if overall_score >= 0.7:
            level = "HIGH"
        elif overall_score >= 0.4:
            level = "MEDIUM"
        else:
            level = "LOW"

        breakdown = {
            pii_type: {"count": count, "weight": self.weights.get(pii_type, 0.5)}
            for pii_type, count in type_counts.items()
        }

        return {
            "score": round(overall_score, 3),
            "level": level,
            "breakdown": breakdown,
            "total_detections": len(detections),
        }
