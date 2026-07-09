import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

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


@router.get("/stream")
def stream_replay() -> StreamingResponse:
    john.reset()

    def events():
        for event, states in john.replay_engine.iter_replay(
            "data/replay/sample_interview.json",
            sleep=True,
        ):
            payload = {
                "event_type": event.event_type.value,
                "participant_id": event.participant_id,
                "rankings": [
                    {
                        "participant_id": state.participant_id,
                        "confidence": round(state.confidence, 3),
                        "evidence_count": len(state.evidence_history),
                        "latest_reason": (
                            state.latest_evidence.reason
                            if state.latest_evidence
                            else None
                        ),
                    }
                    for state in states
                ],
            }

            yield f"data: {json.dumps(payload)}\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
    )
