from fastapi import APIRouter

from app.api.replay import john

router = APIRouter(
    prefix="/confidence",
    tags=["Confidence"],
)


@router.get("/")
def get_confidence():

    rankings = []

    for state in john.rankings():

        rankings.append(
            {
                "participant_id": state.participant_id,
                "confidence": round(
                    state.confidence,
                    3,
                ),
                "evidence_count": len(
                    state.evidence_history
                ),
                "latest_reason": (
                    state.latest_evidence.reason
                    if state.latest_evidence
                    else None
                ),
            }
        )

    return {
        "participants": rankings
    }