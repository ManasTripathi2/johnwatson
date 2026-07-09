from fastapi import APIRouter

from app.api.replay import john
from app.services.ml_inference import ModelInferenceService

router = APIRouter(
    prefix="/ml",
    tags=["ML"],
)

ml_service = ModelInferenceService()

@router.get("/predict")
def predict_candidates() -> dict[str, list[dict[str, object]]]:
    predictions = []

    for state in john.rankings():
        probability = ml_service.predict(state)
        participant = john.interview.get_participant(state.participant_id)

        predictions.append(
            {
                "participant_id": state.participant_id,
                "display_name": (
                    participant.display_name
                    if participant
                    else state.participant_id
                ),
                "confidence": round(state.confidence, 3),
                "model_probability": round(probability, 3),
                "evidence_count": len(state.evidence_history),
                "latest_reason": (
                    state.latest_evidence.reason
                    if state.latest_evidence
                    else None
                ),
                "evidence_reasons": state.explanation,
            }
        )

    return {
        "predictions": predictions,
    }
