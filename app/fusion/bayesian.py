from math import exp, log

from app.evidence.evidence import Evidence


class BayesianFusionEngine:
    """
    Maintains the candidate probability for each participant
    by continuously updating beliefs using incoming evidence.
    """

    def __init__(self, prior: float = 0.5):
        self._beliefs: dict[str, float] = {}
        self._prior = prior

    def update(self, evidence: Evidence) -> float:
        """
        Update the probability of a participant being the candidate.
        """

        probability = self._beliefs.get(
            evidence.participant_id,
            self._prior
        )

        probability = min(max(probability, 1e-6), 1 - 1e-6)

        log_odds = log(probability / (1 - probability))

        log_odds += evidence.score

        probability = 1 / (1 + exp(-log_odds))

        self._beliefs[evidence.participant_id] = probability

        return probability

    def get_probability(self, participant_id: str) -> float:
        return self._beliefs.get(
            participant_id,
            self._prior
        )

    def rankings(self) -> list[tuple[str, float]]:
        return sorted(
            self._beliefs.items(),
            key=lambda item: item[1],
            reverse=True
        )

    def reset(self) -> None:
        self._beliefs.clear()