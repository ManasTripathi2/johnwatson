from enum import Enum


class EventType(str, Enum):
    PARTICIPANT_JOINED = "participant_joined"
    PARTICIPANT_LEFT = "participant_left"

    DISPLAY_NAME_CHANGED = "display_name_changed"

    SPEECH_STARTED = "speech_started"
    SPEECH_ENDED = "speech_ended"

    TRANSCRIPT_RECEIVED = "transcript_received"

    SCREEN_SHARE_STARTED = "screen_share_started"
    SCREEN_SHARE_ENDED = "screen_share_ended"

    CAMERA_ON = "camera_on"
    CAMERA_OFF = "camera_off"

    MICROPHONE_ON = "microphone_on"
    MICROPHONE_OFF = "microphone_off"


class SignalType(str, Enum):
    NAME_MATCH = "name_match"
    SPEAKING_PATTERN = "speaking_pattern"
    ADDRESSED_BY_NAME = "addressed_by_name"
    SCREEN_SHARE = "screen_share"
    JOIN_TIME = "join_time"
    KNOWN_INTERVIEWER = "known_interviewer"


class EvidenceSource(str, Enum):
    RULE = "rule"
    ML = "ml"
    LLM = "llm"


class InterviewStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    FINISHED = "finished"