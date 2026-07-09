from datetime import datetime

from app.fusion.bayesian import BayesianFusionEngine
from app.models.interview import Interview
from app.services.interview_engine import InterviewEngine
from app.services.replay_engine import ReplayEngine

from app.signals.addressed_by_name import AddressedByNameSignal
from app.signals.engine import SignalEngine
from app.signals.join_time import JoinTimeSignal
from app.signals.known_interviewer import KnownInterviewerSignal
from app.signals.name_match import NameMatchSignal
from app.signals.screen_share import ScreenShareSignal
from app.signals.speaking_pattern import SpeakingPatternSignal


class JohnWatson:
    """
    Central application service.
    """

    def __init__(
        self,
        interview_id: str = "INT-001",
        candidate_name: str = "Manas Tripathi",
        interviewer_names: list[str] | None = None,
    ) -> None:

        self.interview = Interview(
            interview_id=interview_id,
            candidate_name=candidate_name,
            interviewer_names=interviewer_names or ["Alice Johnson"],
        )

        signals = SignalEngine()

        signals.register(
            NameMatchSignal(
                self.interview.candidate_name
            )
        )

        signals.register(
            SpeakingPatternSignal()
        )

        signals.register(
            AddressedByNameSignal(
                self.interview.candidate_name
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

        self.engine = InterviewEngine(
            interview=self.interview,
            signal_engine=signals,
            fusion_engine=fusion,
        )

        self.replay_engine = ReplayEngine(
            self.engine
        )

    def replay(
        self,
        replay_file: str,
    ) -> None:

        self.replay_engine.replay(
            replay_file
        )

    def rankings(self):

        return self.engine.rankings()

    def reset(self) -> None:

        self.interview.started_at = datetime.utcnow()
        self.interview.ended_at = None
        self.engine.reset()
