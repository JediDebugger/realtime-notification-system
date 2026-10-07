"""Shape checks shared by events and the preference store (DEC-19).

Each raises ValueError, because a malformed value is the caller's bug.
"""


def _is_positive_int(value: object) -> bool:
    # bool is a subclass of int, so True would otherwise pass as 1.
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def check_id(field: str, value: object) -> None:
    if not _is_positive_int(value):
        raise ValueError(f"{field} must be a positive integer, got {value!r}")


def check_level(field: str, value: object) -> None:
    if not _is_positive_int(value):
        raise ValueError(f"{field} must be an integer of 1 or more, got {value!r}")


def check_text(field: str, value: object) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-blank string, got {value!r}")
