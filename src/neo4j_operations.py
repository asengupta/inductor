"""
Neo4J Operations Module

This module provides CRUD operations for Neo4J nodes.
Each node will have an ID and a nodeType property.
"""

from typing import Dict, List, Optional, Any

from neo4j import GraphDatabase, Driver, Session

from id_provider import IdProvider, UuidProvider


class Neo4jOperations:
    """
    A class to handle CRUD operations for Neo4J nodes.

    Each node will have an ID and a nodeType property.
    """

    def __init__(self, uri: str, username: str, password: str, id_provider: IdProvider):
        """
        Initialize the Neo4jOperations with connection details.

        Args:
            uri: The URI for the Neo4j instance
            username: The username for authentication
            password: The password for authentication
            id_provider: Provider for generating unique IDs (defaults to UuidProvider)
        """
        self.driver: Driver = GraphDatabase.driver(uri, auth=(username, password))
        self.id_provider = id_provider

    def close(self):
        """Close the driver connection."""
        self.driver.close()

    def _get_session(self) -> Session:
        """Get a new session from the driver."""
        return self.driver.session()

    def create_node(self, node_type: str, properties: Dict[str, Any] = None, labels: List[str] = None) -> str:
        """
        Create a new node in Neo4j.

        Args:
            node_type: The type of the node (required)
            properties: Additional properties for the node
            labels: Additional labels for the node

        Returns:
            The ID of the created node
        """
        if properties is None:
            properties = {}
        if labels is None:
            labels = []

        # Ensure node_type is included in properties
        properties['nodeType'] = node_type

        # Generate a unique ID if not provided
        if 'id' not in properties:
            properties['id'] = self.id_provider.generate_id()

        # Prepare labels string for Cypher query
        all_labels = [node_type] + labels
        labels_str = ':'.join(all_labels)

        # Prepare properties string for Cypher query
        props_str = ', '.join([f"{k}: ${k}" for k in properties.keys()])

        query = f"CREATE (n:{labels_str} {{{props_str}}}) RETURN n.id as id"

        with self._get_session() as session:
            result = session.run(query, **properties)
            record = result.single()
            return record["id"]

    def read_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Read a node from Neo4j by its ID.

        Args:
            node_id: The ID of the node to read

        Returns:
            A dictionary containing the node properties or None if not found
        """
        query = "MATCH (n {id: $id}) RETURN n"

        with self._get_session() as session:
            result = session.run(query, id=node_id)
            record = result.single()
            if record:
                node = record["n"]
                return dict(node.items())
            return None

    def update_node(self, node_id: str, properties: Dict[str, Any]) -> bool:
        """
        Update a node in Neo4j.

        Args:
            node_id: The ID of the node to update
            properties: The properties to update

        Returns:
            True if the node was updated, False otherwise
        """
        # Don't allow updating the ID
        if 'id' in properties:
            del properties['id']

        # Prepare properties string for Cypher query
        props_list = [f"n.{k} = ${k}" for k in properties.keys()]
        props_str = ', '.join(props_list)

        query = f"MATCH (n {{id: $id}}) SET {props_str} RETURN n.id as id"

        with self._get_session() as session:
            result = session.run(query, id=node_id, **properties)
            record = result.single()
            return record is not None

    def delete_node(self, node_id: str) -> bool:
        """
        Delete a node from Neo4j.

        Args:
            node_id: The ID of the node to delete

        Returns:
            True if the node was deleted, False otherwise
        """
        query = "MATCH (n {id: $id}) DELETE n RETURN count(n) as count"

        with self._get_session() as session:
            result = session.run(query, id=node_id)
            record = result.single()
            return record and record["count"] > 0

    def find_nodes(self, node_type: Optional[str] = None, properties: Dict[str, Any] = None,
                  labels: List[str] = None) -> List[Dict[str, Any]]:
        """
        Find nodes matching the given criteria.

        Args:
            node_type: The type of nodes to find
            properties: Properties to match
            labels: Labels to match

        Returns:
            A list of dictionaries containing the node properties
        """
        if properties is None:
            properties = {}
        if labels is None:
            labels = []

        # Build the match clause
        match_parts = []
        if node_type:
            match_parts.append(f":{node_type}")
        if labels:
            match_parts.extend([f":{label}" for label in labels])

        match_str = ''.join(match_parts)

        # Build the where clause
        where_parts = []
        for k, v in properties.items():
            where_parts.append(f"n.{k} = ${k}")

        where_str = " AND ".join(where_parts)

        # Build the query
        query = f"MATCH (n{match_str})"
        if where_str:
            query += f" WHERE {where_str}"
        query += " RETURN n"

        with self._get_session() as session:
            result = session.run(query, **properties)
            return [dict(record["n"].items()) for record in result]
