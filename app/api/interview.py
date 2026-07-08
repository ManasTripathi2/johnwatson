from fastapi import APIRouter

from app.api.replay import john

router = APIRouter(
    prefix="/interview",
    tags=["Interview"],
)


@router.get("/")
def get_interview():

    interview = john.interview

    return {
        "interview_id": interview.interview_id,
        "candidate_name": interview.candidate_name,
        "interviewer_names": interview.interviewer_names,
        "participant_count": len(interview.participants),
    }