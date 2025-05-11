from typing import Optional, Any

from beta_bernoulli_belief import BetaBernoulliBelief
from hypothesis import Hypothesis
from hypothesis_subject import HypothesisSubject
from hypothesis_object import HypothesisObject
from neo4j_operations import Neo4jOperations


class HypothesisOperations:
    def __init__(self, neo4j_ops: Neo4jOperations):
        self.neo4j_ops = neo4j_ops

    def create_hypothesis(self, hypothesis: Hypothesis) -> str:
        # Check if subject node already exists
        existing_subject = self.neo4j_ops.read_node(hypothesis.subject.id)
        if existing_subject:
            # Use existing subject node
            subject_id = hypothesis.subject.id
        else:
            # Create subject node with the provided ID
            subject_id = self.neo4j_ops.create_node(node_type="Subject", properties={
                "name": hypothesis.subject.name,
                "id": hypothesis.subject.id
            })

        # Check if object node already exists
        existing_object = self.neo4j_ops.read_node(hypothesis.object.id)
        if existing_object:
            # Use existing object node
            object_id = hypothesis.object.id
        else:
            # Create object node with the provided ID
            object_id = self.neo4j_ops.create_node(node_type="Object", properties={
                "name": hypothesis.object.name,
                "id": hypothesis.object.id
            })

        # Create relation node with belief
        belief_dict = hypothesis.belief.to_dict()
        relation_id = self.neo4j_ops.create_node(node_type="Relation", properties={
            "name": hypothesis.relation,
            "belief_alpha": belief_dict.get("alpha", 1),
            "belief_beta": belief_dict.get("beta", 1),
            "id": hypothesis.id,  # Use the hypothesis ID for the relation node
            "hypothesisId": hypothesis.id,  # Store the hypothesis ID for reference
            "subject_id": subject_id,  # Store the subject ID for reference
            "object_id": object_id  # Store the object ID for reference
        })

        # Create relationships between nodes
        self._create_relationship(subject_id, relation_id, "FLOWS_TO")
        self._create_relationship(relation_id, object_id, "FLOWS_TO")

        return hypothesis.id

    def read_hypothesis(self, hypothesis_id: str) -> Optional[Hypothesis]:
        # Get the relation node
        relation_node = self.neo4j_ops.read_node(hypothesis_id)
        if not relation_node:
            return None

        # Get the subject and object nodes through relationships
        subject_node, object_node = self._get_connected_nodes(hypothesis_id)
        if not subject_node or not object_node:
            return None

        # Create HypothesisSubject
        subject = HypothesisSubject(
            name=subject_node.get("name", ""),
            id=subject_node.get("id", "")
        )

        # Create HypothesisObject
        object_ = HypothesisObject(
            name=object_node.get("name", ""),
            id=object_node.get("id", "")
        )

        # Create a Hypothesis object
        alpha = relation_node.get("belief_alpha", 1)
        beta = relation_node.get("belief_beta", 1)
        belief = BetaBernoulliBelief(alpha=alpha, beta=beta)

        return Hypothesis(
            subject=subject,
            relation=relation_node.get("name", ""),
            object=object_,
            belief=belief,
            id=hypothesis_id
        )

    def update_hypothesis(self, hypothesis: Hypothesis) -> bool:
        # Get the existing relation node
        relation_node = self.neo4j_ops.read_node(hypothesis.id)
        if not relation_node:
            return False

        # Get the existing subject and object nodes
        subject_node, object_node = self._get_connected_nodes(hypothesis.id)

        # Handle subject node
        if subject_node and subject_node["id"] == hypothesis.subject.id:
            # Update existing subject node
            subject_updated = self.neo4j_ops.update_node(
                node_id=subject_node["id"],
                properties={
                    "name": hypothesis.subject.name
                }
            )
        else:
            # Check if the new subject node exists
            existing_subject = self.neo4j_ops.read_node(hypothesis.subject.id)
            if existing_subject:
                # Use existing subject node
                subject_id = hypothesis.subject.id
                subject_updated = True
            else:
                # Create new subject node
                subject_id = self.neo4j_ops.create_node(node_type="Subject", properties={
                    "name": hypothesis.subject.name,
                    "id": hypothesis.subject.id
                })
                subject_updated = subject_id is not None

            # Update the relationship
            if subject_node:
                # Delete old relationship
                self._delete_relationship(subject_node["id"], hypothesis.id)

            # Create new relationship
            self._create_relationship(subject_id, hypothesis.id, "FLOWS_TO")

        # Handle object node
        if object_node and object_node["id"] == hypothesis.object.id:
            # Update existing object node
            object_updated = self.neo4j_ops.update_node(
                node_id=object_node["id"],
                properties={
                    "name": hypothesis.object.name
                }
            )
        else:
            # Check if the new object node exists
            existing_object = self.neo4j_ops.read_node(hypothesis.object.id)
            if existing_object:
                # Use existing object node
                object_id = hypothesis.object.id
                object_updated = True
            else:
                # Create new object node
                object_id = self.neo4j_ops.create_node(node_type="Object", properties={
                    "name": hypothesis.object.name,
                    "id": hypothesis.object.id
                })
                object_updated = object_id is not None

            # Update the relationship
            if object_node:
                # Delete old relationship
                self._delete_relationship(hypothesis.id, object_node["id"])

            # Create new relationship
            self._create_relationship(hypothesis.id, object_id, "FLOWS_TO")

        # Update relation node
        belief_dict = hypothesis.belief.to_dict()
        relation_properties = {
            "name": hypothesis.relation,
            "belief_alpha": belief_dict.get("alpha", 1),
            "belief_beta": belief_dict.get("beta", 1),
            "subject_id": hypothesis.subject.id,
            "object_id": hypothesis.object.id
        }


        relation_updated = self.neo4j_ops.update_node(
            node_id=hypothesis.id,
            properties=relation_properties
        )

        return subject_updated and object_updated and relation_updated

    def delete_hypothesis(self, hypothesis_id: str, keep_subject_object: bool = False) -> bool:
        # Get the nodes
        relation_node = self.neo4j_ops.read_node(hypothesis_id)
        if not relation_node:
            return False

        subject_node, object_node = self._get_connected_nodes(hypothesis_id)

        # Delete the relationships first (using Cypher query)
        self._delete_relationships(hypothesis_id)

        # Delete the relation node
        deleted_relation = self.neo4j_ops.delete_node(hypothesis_id)

        # Delete subject and object nodes if not keeping them
        if not keep_subject_object:
            if subject_node:
                # Check if the subject node is used by other hypotheses
                subject_used = self._is_node_used_elsewhere(subject_node["id"])
                if not subject_used:
                    self.neo4j_ops.delete_node(subject_node["id"])

            if object_node:
                # Check if the object node is used by other hypotheses
                object_used = self._is_node_used_elsewhere(object_node["id"])
                if not object_used:
                    self.neo4j_ops.delete_node(object_node["id"])

        return deleted_relation

    def _is_node_used_elsewhere(self, node_id: str) -> bool:
        query = """
        MATCH (n {id: $node_id})-[r:FLOWS_TO]->()
        RETURN count(r) as relationship_count
        UNION
        MATCH ()-[r:FLOWS_TO]->(n {id: $node_id})
        RETURN count(r) as relationship_count
        """

        with self.neo4j_ops._get_session() as session:
            result = session.run(query, node_id=node_id)
            total_count = 0
            for record in result:
                total_count += record["relationship_count"]
            return total_count > 0

    def find_hypotheses(self, subject: str = None, relation: str = None,
                        object_: str = None, min_alpha: int = None,
                        max_alpha: int = None, min_beta: int = None,
                        max_beta: int = None, subject_id: str = None,
                        object_id: str = None) -> list[Hypothesis]:
        query = """
        MATCH (s:Subject)-[:FLOWS_TO]->(r:Relation)-[:FLOWS_TO]->(o:Object)
        WHERE 1=1
        """

        params = {}

        if subject:
            query += " AND s.name = $subject"
            params["subject"] = subject

        if subject_id:
            query += " AND s.id = $subject_id"
            params["subject_id"] = subject_id

        if relation:
            query += " AND r.name = $relation"
            params["relation"] = relation

        if object_:
            query += " AND o.name = $object"
            params["object"] = object_

        if object_id:
            query += " AND o.id = $object_id"
            params["object_id"] = object_id

        if min_alpha is not None:
            query += " AND r.belief_alpha >= $min_alpha"
            params["min_alpha"] = min_alpha

        if max_alpha is not None:
            query += " AND r.belief_alpha <= $max_alpha"
            params["max_alpha"] = max_alpha

        if min_beta is not None:
            query += " AND r.belief_beta >= $min_beta"
            params["min_beta"] = min_beta

        if max_beta is not None:
            query += " AND r.belief_beta <= $max_beta"
            params["max_beta"] = max_beta

        query += " RETURN r.id as id, s, r, o"

        # Execute the query
        with self.neo4j_ops._get_session() as session:
            result = session.run(query, **params)
            hypotheses = []

            for record in result:
                # Create HypothesisSubject
                subject_node = dict(record["s"].items())
                subject = HypothesisSubject(
                    name=subject_node.get("name", ""),
                    id=subject_node.get("id", "")
                )

                # Create HypothesisObject
                object_node = dict(record["o"].items())
                object_ = HypothesisObject(
                    name=object_node.get("name", ""),
                    id=object_node.get("id", "")
                )

                # Create Hypothesis
                relation_node = dict(record["r"].items())
                alpha = relation_node.get("belief_alpha", 1)
                beta = relation_node.get("belief_beta", 1)
                belief = BetaBernoulliBelief(alpha=alpha, beta=beta)

                hypothesis = Hypothesis(
                    subject=subject,
                    relation=relation_node.get("name", ""),
                    object=object_,
                    belief=belief,
                    id=relation_node.get("id", "")
                )

                hypotheses.append(hypothesis)

        return hypotheses

    def _create_relationship(self, from_node_id: str, to_node_id: str, relationship_type: str) -> bool:
        query = f"""
        MATCH (a), (b)
        WHERE a.id = $from_id AND b.id = $to_id
        CREATE (a)-[r:{relationship_type}]->(b)
        RETURN type(r) as type
        """

        with self.neo4j_ops._get_session() as session:
            result = session.run(query, from_id=from_node_id, to_id=to_node_id)
            record = result.single()
            return record is not None

    def _get_connected_nodes(self, relation_id: str) -> tuple[Optional[dict[str, Any]], Optional[dict[str, Any]]]:
        query = """
        MATCH (s:Subject)-[:FLOWS_TO]->(r:Relation)-[:FLOWS_TO]->(o:Object)
        WHERE r.id = $relation_id
        RETURN s, o
        """

        with self.neo4j_ops._get_session() as session:
            result = session.run(query, relation_id=relation_id)
            record = result.single()

            if record:
                subject_node = dict(record["s"].items())
                object_node = dict(record["o"].items())
                return subject_node, object_node

            return None, None

    def _delete_relationships(self, relation_id: str) -> bool:
        query = """
        MATCH (s)-[r1:FLOWS_TO]->(rel:Relation)-[r2:FLOWS_TO]->(o)
        WHERE rel.id = $relation_id
        DELETE r1, r2
        RETURN count(r1) + count(r2) as deleted_count
        """

        with self.neo4j_ops._get_session() as session:
            result = session.run(query, relation_id=relation_id)
            record = result.single()
            return record and record["deleted_count"] > 0

    def _delete_relationship(self, from_node_id: str, to_node_id: str) -> bool:
        query = """
        MATCH (a {id: $from_id})-[r:FLOWS_TO]->(b {id: $to_id})
        DELETE r
        RETURN count(r) as deleted_count
        """

        with self.neo4j_ops._get_session() as session:
            result = session.run(query, from_id=from_node_id, to_id=to_node_id)
            record = result.single()
            return record and record["deleted_count"] > 0
