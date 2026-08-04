"""
Placeholder prediction service.

IMPORTANT: This module returns deterministic, rule-based mock scores so the rest
of the application (API contract, DB writes, reports, UI) can be built and tested
end-to-end. It is NOT a validated clinical model. Replace `run_inference()` with a
call to a real trained model (see Phase 3 - ML pipeline) before using this for
anything beyond development/demo purposes.
"""

import hashlib
import time
from typing import Optional

MOCK_DISEASE_MAP = {
    "BRCA1": "Hereditary Breast/Ovarian Cancer Syndrome",
    "BRCA2": "Hereditary Breast/Ovarian Cancer Syndrome",
    "CFTR": "Cystic Fibrosis",
    "APOE": "Late-Onset Alzheimer's Disease",
    "HTT": "Huntington's Disease",
    "TP53": "Li-Fraumeni Syndrome",
}

MOCK_DRUG_MAP = {
    "Hereditary Breast/Ovarian Cancer Syndrome": [
        {"drug_name": "Olaparib", "effectiveness": 0.78, "risk_level": "moderate"},
        {"drug_name": "Talazoparib", "effectiveness": 0.72, "risk_level": "moderate"},
    ],
    "Cystic Fibrosis": [
        {"drug_name": "Elexacaftor/Tezacaftor/Ivacaftor", "effectiveness": 0.85, "risk_level": "low"},
    ],
    "Late-Onset Alzheimer's Disease": [
        {"drug_name": "Lecanemab", "effectiveness": 0.55, "risk_level": "moderate"},
    ],
    "Huntington's Disease": [
        {"drug_name": "Tetrabenazine", "effectiveness": 0.60, "risk_level": "moderate"},
    ],
    "Li-Fraumeni Syndrome": [
        {"drug_name": "No disease-modifying drug — surveillance protocol recommended", "effectiveness": 0.0, "risk_level": "high"},
    ],
}


def _pseudo_random_from_string(value: str) -> float:
    """Deterministic pseudo-random float in [0, 1] derived from a string, for demo consistency."""
    digest = hashlib.sha256(value.encode()).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF


def run_inference(gene_name: str, mutation_type: Optional[str], chromosome: Optional[str]) -> dict:
    """Mock inference pipeline: preprocessing -> classification -> disease/drug prediction."""
    start = time.perf_counter()

    gene_key = gene_name.strip().upper()
    disease = MOCK_DISEASE_MAP.get(gene_key, "No significant association found")
    confidence = 0.55 + 0.4 * _pseudo_random_from_string(gene_key + str(mutation_type))
    probability = min(confidence + 0.03, 0.99)

    if confidence >= 0.85:
        risk_level = "high"
    elif confidence >= 0.65:
        risk_level = "moderate"
    else:
        risk_level = "low"

    drugs = MOCK_DRUG_MAP.get(disease, [])
    recommended_drug = drugs[0]["drug_name"] if drugs else None

    elapsed_ms = (time.perf_counter() - start) * 1000

    return {
        "disease": disease,
        "confidence": round(confidence, 4),
        "probability": round(probability, 4),
        "risk_level": risk_level,
        "recommended_drug": recommended_drug,
        "drug_recommendations": drugs,
        "model_version": "mock-v0.1-placeholder",
        "inference_time_ms": round(elapsed_ms, 3),
    }
