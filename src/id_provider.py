"""
ID Provider Module

This module provides an interface for generating unique IDs.
"""

from typing import Protocol
import uuid

class IdProvider(Protocol):
    """
    Protocol defining the interface for ID providers.
    """

    def generate_id(self) -> str:
        """
        Generate a unique ID.

        Returns:
            A string representation of a unique ID
        """
        ...

class UuidProvider:
    """
    An implementation of IdProvider that generates UUIDs.
    """

    def generate_id(self) -> str:
        """
        Generate a unique UUID.

        Returns:
            A string representation of a UUID
        """
        return str(uuid.uuid4())
