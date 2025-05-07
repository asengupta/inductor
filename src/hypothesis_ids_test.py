"""
Test script to verify that subject, relation, and object nodes have different IDs,
and that the relation node uses the hypothesis ID.
"""

import os

from dotenv import load_dotenv

from hypothesis import Hypothesis
from hypothesis_operations import HypothesisOperations
from id_provider import UuidProvider
from neo4j_operations import Neo4jOperations

# Load environment variables from .env file
load_dotenv("./env/.env")

# Get Neo4j connection details from environment variables
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")


def main():
    """Run the test."""
    # Initialize the Neo4j operations with a custom ID provider
    id_provider = UuidProvider()
    neo4j_ops = Neo4jOperations(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, id_provider=id_provider)

    # Initialize the Hypothesis operations
    hypothesis_ops = HypothesisOperations(neo4j_ops)

    try:
        # Create a hypothesis
        print("Creating a hypothesis...")
        test_hypothesis = Hypothesis(
            subject="TestSubject",
            relation="TestRelation",
            object="TestObject",
            confidence=0.8
        )
        hypothesis_id = hypothesis_ops.create_hypothesis(test_hypothesis)
        print(f"Created hypothesis with ID: {hypothesis_id}")

        # Get the nodes directly from Neo4j to check their IDs
        print("\nVerifying node IDs...")

        # Get the relation node
        relation_node = neo4j_ops.read_node(hypothesis_id)
        print(f"Relation node ID: {relation_node['id']}")

        # Get the subject and object nodes through relationships
        subject_node, object_node = hypothesis_ops._get_connected_nodes(hypothesis_id)
        print(f"Subject node ID: {subject_node['id']}")
        print(f"Object node ID: {object_node['id']}")

        # Verify that the IDs are different
        print("\nVerifying that IDs are different...")
        ids = [relation_node['id'], subject_node['id'], object_node['id']]
        unique_ids = set(ids)
        print(f"Number of unique IDs: {len(unique_ids)} (should be 3)")
        print(f"All IDs are different: {len(unique_ids) == 3}")

        # Verify that the relation node ID matches the hypothesis ID
        print("\nVerifying that relation node ID matches hypothesis ID...")
        print(f"Relation node ID: {relation_node['id']}")
        print(f"Hypothesis ID: {hypothesis_id}")
        print(f"Match: {relation_node['id'] == hypothesis_id}")

        # Clean up
        print("\nCleaning up...")
        hypothesis_ops.delete_hypothesis(hypothesis_id)
        print("Hypothesis deleted.")

    finally:
        # Close the connection
        neo4j_ops.close()
        print("\nConnection closed.")


if __name__ == "__main__":
    main()
