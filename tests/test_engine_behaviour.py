from datetime import timedelta
import unittest

from app.core.enums import EventType, SignalType
from app.events.event import Event
from app.services.johnwatson import JohnWatson


class EngineBehaviourTest(unittest.TestCase):
    def setUp(self) -> None:
        self.service = JohnWatson()
        self.start = self.service.interview.started_at

    def event(
        self,
        event_type: EventType,
        participant_id: str,
        offset: float,
        **data: object,
    ) -> Event:
        return Event(
            event_type=event_type,
            participant_id=participant_id,
            timestamp=self.start + timedelta(seconds=offset),
            data=data,
        )

    def test_addressed_by_name_credits_next_speaker(self) -> None:
        self.service.engine.process(
            self.event(
                EventType.PARTICIPANT_JOINED,
                "P001",
                0.0,
                display_name="Manas Tripathi",
            )
        )
        self.service.engine.process(
            self.event(
                EventType.PARTICIPANT_JOINED,
                "P002",
                1.0,
                display_name="Alice Johnson",
            )
        )
        self.service.engine.process(
            self.event(
                EventType.TRANSCRIPT_RECEIVED,
                "P002",
                5.0,
                text="Manas Tripathi, please introduce yourself.",
            )
        )
        self.service.engine.process(
            self.event(
                EventType.SPEECH_ENDED,
                "P001",
                10.0,
                duration=30,
            )
        )

        candidate = self.service.engine.get_state("P001")
        interviewer = self.service.engine.get_state("P002")

        assert candidate is not None
        assert interviewer is not None
        self.assertTrue(
            any(
                evidence.signal == SignalType.ADDRESSED_BY_NAME
                for evidence in candidate.evidence_history
            )
        )
        self.assertFalse(
            any(
                evidence.signal == SignalType.ADDRESSED_BY_NAME
                for evidence in interviewer.evidence_history
            )
        )

    def test_speaking_pattern_emits_incremental_scores(self) -> None:
        self.service.engine.process(
            self.event(
                EventType.PARTICIPANT_JOINED,
                "P001",
                0.0,
                display_name="Manas Tripathi",
            )
        )

        self.service.engine.process(
            self.event(EventType.SPEECH_ENDED, "P001", 10.0, duration=60)
        )
        self.service.engine.process(
            self.event(EventType.SPEECH_ENDED, "P001", 20.0, duration=60)
        )

        state = self.service.engine.get_state("P001")

        assert state is not None
        speaking_scores = [
            evidence.score
            for evidence in state.evidence_history
            if evidence.signal == SignalType.SPEAKING_PATTERN
        ]

        self.assertEqual(len(speaking_scores), 2)
        self.assertLess(sum(speaking_scores), 0.35)

    def test_silent_participant_remains_ranked(self) -> None:
        self.service.engine.process(
            self.event(
                EventType.PARTICIPANT_JOINED,
                "P003",
                15.0,
                display_name="Observer",
            )
        )

        state = self.service.engine.get_state("P003")

        assert state is not None
        self.assertIn(state, self.service.rankings())


if __name__ == "__main__":
    unittest.main()
