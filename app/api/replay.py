from fastapi import APIRouter

from app.services.johnwatson import JohnWatson

router = APIRouter(
    prefix="/replay",
    tags=["Replay"],
)

john = JohnWatson()


@router.post("/")
def replay_interview():

    john.reset()

    john.replay(
        "data/replay/sample_interview.json"
    )

    return {
        "status": "completed",
        "participants": len(john.rankings()),
        "rankings": [
            {
                "participant_id": state.participant_id,
                "confidence": round(
                    state.confidence,
                    3,
                ),
            }
            for state in john.rankings()
        ],
    }