"""
Test script to demonstrate creating multiple relationships between the same subject and object.

This script creates a subject node and an object node, then creates multiple hypotheses
with different relations between them. It verifies that all relationships are correctly
stored in Neo4J.
"""

import os
from dotenv import load_dotenv
from neo4j_operations import Neo4jOperations
from hypothesis import Hypothesis, HypothesisSubject, HypothesisObject
from hypothesis_operations import HypothesisOperations
from id_provider import UuidProvider

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
        # Create a subject
        print("Creating a subject...")
        earth_subject = HypothesisSubject(
            name="Earth",
            additional_properties={
                "type": "Planet",
                "diameter_km": 12742
            }
        )
        print(f"Created subject with ID: {earth_subject.id}")

        # Create an object
        print("Creating an object...")
        mars_object = HypothesisObject(
            name="Mars",
            additional_properties={
                "type": "Planet",
                "diameter_km": 6779
            }
        )
        print(f"Created object with ID: {mars_object.id}")

        # Create multiple hypotheses with different relations between the same subject and object
        relations = [
            ("is_larger_than", 0.99),
            ("has_stronger_gravity_than", 0.95),
            ("has_more_water_than", 0.90),
            ("is_more_habitable_than", 0.75)
        ]

        hypothesis_ids = []

        print("\nCreating multiple hypotheses with different relations...")
        for relation, confidence in relations:
            # Create a hypothesis using the same subject and object but a different relation
            hypothesis = Hypothesis(
                subject=earth_subject,
                relation=relation,
                object=mars_object,
                confidence=confidence,
                additional_properties={
                    "source": "Scientific comparison",
                    "relation_type": "comparative"
                }
            )

            # Save the hypothesis to Neo4J
            hypothesis_id = hypothesis_ops.create_hypothesis(hypothesis)
            hypothesis_ids.append(hypothesis_id)
            print(f"Created hypothesis with relation '{relation}' and ID: {hypothesis_id}")

        print(f"\nCreated {len(hypothesis_ids)} different relationships between Earth and Mars.")

        # Verify that all hypotheses are stored correctly
        print("\nVerifying all hypotheses...")
        for hypothesis_id in hypothesis_ids:
            hypothesis = hypothesis_ops.read_hypothesis(hypothesis_id)
            print(f"  {hypothesis.subject.name} {hypothesis.relation} {hypothesis.object.name} (confidence: {hypothesis.confidence})")

        # Find all hypotheses with Earth as subject and Mars as object
        print("\nFinding all hypotheses with Earth as subject and Mars as object...")
        earth_mars_hypotheses = hypothesis_ops.find_hypotheses(
            subject="Earth",
            object_="Mars"
        )
        print(f"Found {len(earth_mars_hypotheses)} hypotheses:")
        for h in earth_mars_hypotheses:
            print(f"  {h.subject.name} {h.relation} {h.object.name} (confidence: {h.confidence})")

        # Verify that we found all the hypotheses we created
        print(f"\nVerified that all {len(relations)} relationships were found.")

        # Clean up
        print("\nCleaning up...")
        # for hypothesis_id in hypothesis_ids:
        #     hypothesis_ops.delete_hypothesis(hypothesis_id, keep_subject_object=True)
        # print("All hypotheses deleted, but subject and object nodes are preserved.")
        #
        # # Delete the subject and object nodes
        # neo4j_ops.delete_node(earth_subject.id)
        # neo4j_ops.delete_node(mars_object.id)
        # print("Subject and object nodes deleted.")

    finally:
        # Close the connection
        neo4j_ops.close()
        print("\nConnection closed.")

if __name__ == "__main__":
    main()
