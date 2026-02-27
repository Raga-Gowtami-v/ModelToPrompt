from typing import Dict, List

from app.privacy.regex_detector import RegexDetector
from app.privacy.ner_detector import NERDetector
from app.privacy.risk_scorer import RiskScorer


class PrivacyService:
    """Orchestrates PII detection, masking, and risk scoring."""

    def __init__(self):
        self.regex_detector = RegexDetector()
        self.ner_detector = NERDetector()
        self.risk_scorer = RiskScorer()

    def scan_and_mask(self, text: str, source: str = "unknown") -> Dict:
        """Run all detectors, merge results, mask PII, and compute risk score."""
        # Run both detectors
        regex_hits = self.regex_detector.detect(text)
        ner_hits = self.ner_detector.detect(text)

        # Merge and deduplicate detections
        all_detections = self._merge_detections(regex_hits, ner_hits)

        # Mask the text
        masked_text = self.regex_detector.mask(text, all_detections)

        # Score the risk
        risk = self.risk_scorer.score(all_detections)

        return {
            "source": source,
            "original_length": len(text),
            "masked_text": masked_text,
            "detections": all_detections,
            "risk": risk,
        }

    def _merge_detections(self, *detection_lists: List[Dict]) -> List[Dict]:
        """Merge detections from multiple detectors, removing overlaps."""
        all_dets = []
        for dets in detection_lists:
            all_dets.extend(dets)

        # Sort by start position
        all_dets.sort(key=lambda d: (d["start"], -d["end"]))

        # Remove overlapping detections, keeping higher confidence
        merged = []
        for det in all_dets:
            if merged and det["start"] < merged[-1]["end"]:
                # Overlap: keep the one with higher confidence
                if det["confidence"] > merged[-1]["confidence"]:
                    merged[-1] = det
            else:
                merged.append(det)
        return merged
