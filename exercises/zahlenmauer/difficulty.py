from enum import Enum


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

    @classmethod
    def from_string(cls, value: str) -> "Difficulty":
        for diff in cls:
            if diff.value.lower() == value.lower():
                return diff
        raise ValueError(f"Unknown difficulty: {value}. Expected one of: {[d.value for d in cls]}")
