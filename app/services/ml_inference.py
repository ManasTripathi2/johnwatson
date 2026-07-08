from pathlib import Path

import joblib

from app.services.feature_extractor import FeatureExtractor
from app.fusion.confidence import ConfidenceState

MODEL_PATH = Path(__file__).resolve().parents[2] / "data" / "processed" / "xgboost_model.joblib"


class ModelInferenceService:
    """Loads the trained model and predicts candidate probability."""

    def __init__(self, model_path: Path | str = MODEL_PATH) -> None:
        self.model_path = Path(model_path)
        self._model = None
        self._feature_extractor = FeatureExtractor()

    def _load_model(self) -> None:
        if self._model is None:
            self._model = joblib.load(self.model_path)

    def predict(self, state: ConfidenceState) -> float:
        self._load_model()

        features = self._feature_extractor.extract(state)
        probabilities = self._model.predict_proba([features])
        return float(probabilities[0][1])
