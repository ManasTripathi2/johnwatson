from app.fusion.confidence import ConfidenceState


class FeatureExtractor:
    """
    Converts a participant's evidence history into
    the feature vector expected by the trained model.
    """

    FEATURE_NAMES = [
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

        return [
            signal_scores.get("name_match", 0.0),
            signal_scores.get("speaking_pattern", 0.0),
            signal_scores.get("addressed_by_name", 0.0),
            signal_scores.get("join_time", 0.0),
            signal_scores.get("screen_share", 0.0),
            signal_scores.get("known_interviewer", 0.0),
        ]