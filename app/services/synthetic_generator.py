import json
import random
from datetime import timedelta
from pathlib import Path

from app.core.enums import EventType
from app.events.event import Event
from app.services.feature_extractor import FeatureExtractor
from app.services.johnwatson import JohnWatson


class SyntheticInterviewGenerator:
    """
    Generates training samples by running synthetic event streams
    through the same signal engine used at inference time.
    """

    CANDIDATE_NAME = "Manas Tripathi"
    INTERVIEWER_NAME = "Alice Johnson"

    def __init__(
        self,
        seed: int = 42,
    ) -> None:
        self.random = random.Random(seed)
        self.feature_extractor = FeatureExtractor()

    def generate(
        self,
        output_path: str | Path,
        interviews: int = 100,
    ) -> None:
        dataset = []

        for interview_id in range(interviews):
            dataset.extend(self._generate_interview(interview_id))

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(dataset, file, indent=4)

    def _generate_interview(
        self,
        interview_id: int,
    ) -> list[dict]:
        service = JohnWatson(
            interview_id=f"SYN-{interview_id:04d}",
            candidate_name=self.CANDIDATE_NAME,
            interviewer_names=[self.INTERVIEWER_NAME],
        )

        candidate_id = "P001"
        participants = self._participants(candidate_id)

        for event in self._events(
            participants,
            candidate_id,
            service.interview.started_at,
        ):
            service.engine.process(event)

        samples = []

        for state in service.rankings():
            samples.append(
                {
                    "interview_id": interview_id,
                    "participant_id": state.participant_id,
                    "features": dict(
                        zip(
                            FeatureExtractor.FEATURE_NAMES,
                            self.feature_extractor.extract(state),
                        )
                    ),
                    "label": int(state.participant_id == candidate_id),
                }
            )

        return samples

    def _participants(
        self,
        candidate_id: str,
    ) -> list[tuple[str, str]]:
        candidate_names = [
            self.CANDIDATE_NAME,
            "Manas T.",
            "M Tripathi",
            "Candidate",
        ]

        participants = [
            (
                candidate_id,
                self.random.choices(
                    candidate_names,
                    weights=[7, 2, 1, 1],
                )[0],
            ),
            ("P002", self.INTERVIEWER_NAME),
            ("P003", self.random.choice(["Guest", "Observer", "Rahul Sharma"])),
        ]

        if self.random.random() < 0.35:
            participants.append(
                ("P004", self.random.choice(["Manas", "M. Tripathi", "Unknown"]))
            )

        if self.random.random() < 0.20:
            participants.append(
                ("P005", self.random.choice(["Panelist", "Bob Smith"]))
            )

        return participants

    def _events(
        self,
        participants: list[tuple[str, str]],
        candidate_id: str,
        start,
    ) -> list[Event]:
        events = []

        for index, (participant_id, display_name) in enumerate(participants):
            events.append(
                self._event(
                    EventType.PARTICIPANT_JOINED,
                    participant_id,
                    start,
                    offset=float(index * self.random.randint(1, 8)),
                    display_name=display_name,
                )
            )

        if self.random.random() < 0.25:
            events.append(
                self._event(
                    EventType.DISPLAY_NAME_CHANGED,
                    candidate_id,
                    start,
                    offset=10.0,
                    display_name=self.CANDIDATE_NAME,
                )
            )

        events.append(
            self._event(
                EventType.TRANSCRIPT_RECEIVED,
                "P002",
                start,
                offset=12.0,
                text=self.random.choice(
                    [
                        "Manas Tripathi, could you introduce yourself?",
                        "Manas, please walk us through your last project.",
                        "Could the candidate start with an introduction?",
                    ]
                ),
            )
        )

        candidate_turns = self.random.randint(1, 4)

        for turn in range(candidate_turns):
            events.append(
                self._event(
                    EventType.SPEECH_ENDED,
                    candidate_id,
                    start,
                    offset=18.0 + (turn * 18.0),
                    duration=self.random.uniform(25.0, 75.0),
                )
            )

        if self.random.random() < 0.55:
            events.append(
                self._event(
                    EventType.SCREEN_SHARE_STARTED,
                    candidate_id,
                    start,
                    offset=80.0,
                )
            )

        if self.random.random() < 0.20:
            events.append(
                self._event(
                    EventType.SCREEN_SHARE_STARTED,
                    "P002",
                    start,
                    offset=82.0,
                )
            )

        if self.random.random() < 0.45:
            events.append(
                self._event(
                    EventType.SPEECH_ENDED,
                    "P002",
                    start,
                    offset=90.0,
                    duration=self.random.uniform(8.0, 35.0),
                )
            )

        return sorted(events, key=lambda event: event.timestamp)

    def _event(
        self,
        event_type: EventType,
        participant_id: str,
        start,
        offset: float,
        **data: object,
    ) -> Event:
        return Event(
            event_type=event_type,
            participant_id=participant_id,
            timestamp=start + timedelta(seconds=offset),
            data=data,
        )
