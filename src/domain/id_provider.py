import uuid
from typing import Protocol


class IdProvider(Protocol):
    def id(self) -> str:
        ...


class UuidProvider(IdProvider):

    def id(self) -> str:
        return str(uuid.uuid4())
