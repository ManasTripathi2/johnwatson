from app.models.interview import Interview

from app.fusion.bayesian import BayesianFusionEngine

from app.services.interview_engine import InterviewEngine
from app.services.replay_engine import ReplayEngine

from app.signals.engine import SignalEngine

from app.signals.name_match import NameMatchSignal
from app.signals.speaking_pattern import SpeakingPatternSignal
from app.signals.addressed_by_name import AddressedByNameSignal
from app.signals.join_time import JoinTimeSignal
from app.signals.screen_share import ScreenShareSignal
from app.signals.known_interviewer import KnownInterviewerSignal


def main():

    interview = Interview(
        interview_id="INT-001",
        candidate_name="Manas Tripathi",
        interviewer_names=[
            "Alice Johnson",
        ],
    )

    signals = SignalEngine()

    signals.register(
        NameMatchSignal(
            interview.candidate_name
        )
    )

    signals.register(
        SpeakingPatternSignal()
    )

    signals.register(
        AddressedByNameSignal(
            interview.candidate_name
        )
    )

    signals.register(
        JoinTimeSignal()
    )

    signals.register(
        ScreenShareSignal()
    )

    signals.register(
        KnownInterviewerSignal()
    )

    fusion = BayesianFusionEngine()

    engine = InterviewEngine(
        interview=interview,
        signal_engine=signals,
        fusion_engine=fusion,
    )

    replay = ReplayEngine(engine)

    replay.replay(
        "data/replay/sample_interview.json"
    )


if __name__ == "__main__":
    main()