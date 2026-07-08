import json
import random
from pathlib import Path


class SyntheticInterviewGenerator:
    """
    Generates synthetic interview samples for training
    the candidate identification model.
    """

    def generate(
        self,
        output_path: str | Path,
        interviews: int = 100,
    ) -> None:

        dataset = []

        for interview_id in range(interviews):
            dataset.extend(
                self._generate_interview(interview_id)
            )

        with open(
            output_path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                dataset,
                file,
                indent=4,
            )

    def _generate_interview(
        self,
        interview_id: int,
    ) -> list[dict]:

        participants = [
            ("P001", 1),
            ("P002", 0),
            ("P003", 0),
        ]

        samples = []

        for participant_id, label in participants:

            if label == 1:

                name_match = round(
                    random.uniform(0.90, 1.00),
                    3,
                )

                speaking_pattern = round(
                    random.uniform(0.65, 1.00),
                    3,
                )

                addressed_by_name = round(
                    random.uniform(0.60, 1.00),
                    3,
                )

                join_time = round(
                    random.uniform(0.85, 1.00),
                    3,
                )

                screen_share = random.choice([0, 1])

                known_interviewer = 0

            else:

                name_match = round(
                    random.uniform(0.00, 0.60),
                    3,
                )

                speaking_pattern = round(
                    random.uniform(0.00, 0.40),
                    3,
                )

                addressed_by_name = round(
                    random.uniform(0.00, 0.30),
                    3,
                )

                join_time = round(
                    random.uniform(0.20, 0.80),
                    3,
                )

                screen_share = random.choice([0, 0, 1])

                known_interviewer = random.choice([0, 1])

            samples.append(
                {
                    "interview_id": interview_id,
                    "participant_id": participant_id,
                    "features": {
                        "name_match": name_match,
                        "speaking_pattern": speaking_pattern,
                        "addressed_by_name": addressed_by_name,
                        "join_time": join_time,
                        "screen_share": screen_share,
                        "known_interviewer": known_interviewer,
                    },
                    "label": label,
                }
            )

        return samples