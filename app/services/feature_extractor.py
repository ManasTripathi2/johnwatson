from app.fusion.confidence import ConfidenceState


class FeatureExtractor:
    """
    Converts a participant's evidence history into
    a feature vector for the ML model.
    """

    FEATURE_NAMES = [
        "evidence_count",
        "average_signal_score",
        "name_match",
        "speaking_pattern",
        "addressed_by_name",
        "join_time",
        "screen_share",
        "known_interviewer",
    ]

    def extract(
        self,
        state: ConfidenceState,
    ) -> list[float]:

        signal_scores = {
            evidence.signal.value: evidence.score
            for evidence in state.evidence_history
        }

        scores = [
            evidence.score
            for evidence in state.evidence_history
        ]

        average_score = (
            sum(scores) / len(scores)
            if scores
            else 0.0
        )

        return [
            float(len(state.evidence_history)),
            average_score,
            signal_scores.get("name_match", 0.0),
            signal_scores.get("speaking_pattern", 0.0),
            signal_scores.get("addressed_by_name", 0.0),
            signal_scores.get("join_time", 0.0),
            signal_scores.get("screen_share", 0.0),
            signal_scores.get("known_interviewer", 0.0),
        ]