from typing import Optional, Any

from neo4j import GraphDatabase, Driver, Session

from id_provider import IdProvider


class Neo4jOperations:
    def __init__(self, uri: str, username: str, password: str, id_provider: IdProvider):
        self.driver: Driver = GraphDatabase.driver(uri, auth=(username, password))
        self.id_provider = id_provider

    def close(self):
        self.driver.close()

    def _get_session(self) -> Session:
        return self.driver.session()

    def create_node(self, node_type: str, properties: dict[str, Any] = {}, labels: list[str] = []) -> str:
        # Ensure node_type is included in properties
        properties['nodeType'] = node_type

        # Generate a unique ID if not provided
        if 'id' not in properties:
            properties['id'] = self.id_provider.id()

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

    def read_node(self, node_id: str) -> Optional[dict[str, Any]]:
        query = "MATCH (n {id: $id}) RETURN n"

        with self._get_session() as session:
            result = session.run(query, id=node_id)
            record = result.single()
            if record:
                node = record["n"]
                return dict(node.items())
            return None

    def update_node(self, node_id: str, properties: dict[str, Any]) -> bool:
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
        query = "MATCH (n {id: $id}) DELETE n RETURN count(n) as count"

        with self._get_session() as session:
            result = session.run(query, id=node_id)
            record = result.single()
            return record and record["count"] > 0

    def find_nodes(self, node_type: Optional[str] = None, properties: dict[str, Any] = {},
                  labels: list[str] = []) -> list[dict[str, Any]]:
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
