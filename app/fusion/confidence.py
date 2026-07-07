from dataclasses import dataclass, field
from datetime import datetime

from app.evidence.evidence import Evidence


@dataclass
class ConfidenceState:
    """
    Represents the current confidence state of a participant.
    """

    participant_id: str

    confidence: float = 0.5

    evidence_history: list[Evidence] = field(default_factory=list)

    updated_at: datetime = field(default_factory=datetime.utcnow)

    def update(
        self,
        confidence: float,
        evidence: Evidence
    ) -> None:
        self.confidence = confidence
        self.evidence_history.append(evidence)
        self.updated_at = datetime.utcnow()

    @property
    def latest_evidence(self) -> Evidence | None:
        if not self.evidence_history:
            return None

        return self.evidence_history[-1]

    @property
    def explanation(self) -> list[str]:
        return [
            evidence.reason
            for evidence in self.evidence_history
        ]