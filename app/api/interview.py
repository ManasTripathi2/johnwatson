from fastapi import APIRouter

from app.models.interview import Interview

router = APIRouter(
    prefix="/interview",
    tags=["Interview"],
)

interview = Interview(
    interview_id="INT-001",
    candidate_name="Manas Tripathi",
    interviewer_names=[
        "Alice Johnson",
    ],
)


@router.get("/")
def get_interview():

    return {
        "interview_id": interview.interview_id,
        "candidate_name": interview.candidate_name,
        "interviewer_names": interview.interviewer_names,
        "participant_count": len(interview.participants),
    }