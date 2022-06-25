from dataclasses import field
from uuid import uuid4


def default() -> str:
    return str(uuid4())


default_uuid = field(default_factory=default)
