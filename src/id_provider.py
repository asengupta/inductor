"""
ID Provider Module

This module provides an interface for generating unique IDs.
"""

import uuid
from typing import Protocol


class IdProvider(Protocol):
    """
    Protocol defining the interface for ID providers.
    """

    def id(self) -> str:
        """
        Generate a unique ID.

        Returns:
            A string representation of a unique ID
        """
        ...


class UuidProvider(IdProvider):
    """
    An implementation of IdProvider that generates UUIDs.
    """

    def id(self) -> str:
        """
        Generate a unique UUID.

        Returns:
            A string representation of a UUID
        """
        return str(uuid.uuid4())
