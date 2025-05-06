"""
Hypothesis Operations Example

This script demonstrates how to use the HypothesisOperations class to perform CRUD operations
on Hypothesis nodes in Neo4J, where each hypothesis consists of three connected nodes:
subject, relation, and object.
"""

import os
from dotenv import load_dotenv
from neo4j_operations import Neo4jOperations
from hypothesis import Hypothesis, HypothesisSubject, HypothesisObject
from hypothesis_operations import HypothesisOperations

# Load environment variables from .env file
load_dotenv("./env/.env")

# Get Neo4j connection details from environment variables
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

def main():
    """Run the example."""
    # Initialize the Neo4j operations
    neo4j_ops = Neo4jOperations(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

    # Initialize the Hypothesis operations
    hypothesis_ops = HypothesisOperations(neo4j_ops)

    try:
        # Example 1: Create a hypothesis using HypothesisSubject and HypothesisObject
        print("Creating a hypothesis...")

        # Create a subject
        earth_subject = HypothesisSubject(
            name="Earth",
            additional_properties={
                "type": "Planet",
                "diameter_km": 12742
            }
        )
        print(f"Created subject with ID: {earth_subject.id}")

        # Create an object
        sun_object = HypothesisObject(
            name="Sun",
            additional_properties={
                "type": "Star",
                "diameter_km": 1392700
            }
        )
        print(f"Created object with ID: {sun_object.id}")

        # Create a hypothesis using the subject and object
        earth_hypothesis = Hypothesis(
            subject=earth_subject,
            relation="orbits",
            object=sun_object,
            confidence=0.99,
            additional_properties={
                "source": "Astronomical observation",
                "verified": True
            }
        )

        # Save the hypothesis to Neo4J
        hypothesis_id = hypothesis_ops.create_hypothesis(earth_hypothesis)
        print(f"Created hypothesis with ID: {hypothesis_id}")
        print(f"This created three nodes in Neo4J with relationships between them.")

        # Example 2: Read a hypothesis
        print("\nReading the hypothesis...")
        hypothesis = hypothesis_ops.read_hypothesis(hypothesis_id)
        print(f"Hypothesis data:")
        print(f"  Subject: {hypothesis.subject.name} (ID: {hypothesis.subject.id})")
        print(f"  Subject additional properties: {hypothesis.subject.additional_properties}")
        print(f"  Relation: {hypothesis.relation}")
        print(f"  Object: {hypothesis.object.name} (ID: {hypothesis.object.id})")
        print(f"  Object additional properties: {hypothesis.object.additional_properties}")
        print(f"  Confidence: {hypothesis.confidence}")
        print(f"  Additional properties: {hypothesis.additional_properties}")

        # Example 3: Update a hypothesis
        print("\nUpdating the hypothesis...")

        # Update the subject
        hypothesis.subject.name = "Earth (Updated)"
        hypothesis.subject.additional_properties["mass_kg"] = 5.97e24

        # Update the relation
        hypothesis.relation = "orbits_around"

        # Update the confidence
        hypothesis.confidence = 0.999

        # Update the hypothesis additional properties
        hypothesis.additional_properties["last_verified"] = "2023-06-15"

        # Save the updates
        updated = hypothesis_ops.update_hypothesis(hypothesis)
        print(f"Hypothesis updated: {updated}")

        # Example 4: Read the updated hypothesis
        print("\nReading the updated hypothesis...")
        updated_hypothesis = hypothesis_ops.read_hypothesis(hypothesis_id)
        print(f"Updated hypothesis data:")
        print(f"  Subject: {updated_hypothesis.subject.name} (ID: {updated_hypothesis.subject.id})")
        print(f"  Subject additional properties: {updated_hypothesis.subject.additional_properties}")
        print(f"  Relation: {updated_hypothesis.relation}")
        print(f"  Object: {updated_hypothesis.object.name} (ID: {updated_hypothesis.object.id})")
        print(f"  Object additional properties: {updated_hypothesis.object.additional_properties}")
        print(f"  Confidence: {updated_hypothesis.confidence}")
        print(f"  Additional properties: {updated_hypothesis.additional_properties}")

        # Example 5: Create another hypothesis with a shared subject
        print("\nCreating another hypothesis with a shared subject...")

        # Reuse the Earth subject from the first hypothesis
        earth_subject = updated_hypothesis.subject

        # Create an Earth object for when Earth is used as an object
        earth_object = HypothesisObject(
            name=earth_subject.name,
            additional_properties=earth_subject.additional_properties.copy()
        )

        # Create a new subject for the Moon
        moon_subject = HypothesisSubject(
            name="Moon",
            additional_properties={
                "type": "Natural Satellite",
                "diameter_km": 3474
            }
        )

        # Create a hypothesis where the Moon orbits the Earth
        moon_hypothesis = Hypothesis(
            subject=moon_subject,  # The Moon is the subject
            relation="orbits",
            object=earth_object,  # The Earth is the object
            confidence=0.999
        )

        moon_hypothesis_id = hypothesis_ops.create_hypothesis(moon_hypothesis)
        print(f"Created another hypothesis with ID: {moon_hypothesis_id}")
        print(f"This hypothesis reuses the Earth node from the first hypothesis.")

        # Example 6: Find hypotheses by relation
        print("\nFinding hypotheses by relation...")
        orbit_hypotheses = hypothesis_ops.find_hypotheses(relation="orbits")
        print(f"Found {len(orbit_hypotheses)} hypotheses with relation 'orbits':")
        for h in orbit_hypotheses:
            print(f"  {h.subject.name} {h.relation} {h.object.name} (confidence: {h.confidence})")

        # Example 7: Find hypotheses by subject name
        print("\nFinding hypotheses by subject name...")
        earth_hypotheses = hypothesis_ops.find_hypotheses(subject="Earth (Updated)")
        print(f"Found {len(earth_hypotheses)} hypotheses with subject 'Earth (Updated)':")
        for h in earth_hypotheses:
            print(f"  {h.subject.name} {h.relation} {h.object.name} (confidence: {h.confidence})")

        # Example 8: Find hypotheses by object name
        print("\nFinding hypotheses by object name...")
        earth_object_hypotheses = hypothesis_ops.find_hypotheses(object_="Earth (Updated)")
        print(f"Found {len(earth_object_hypotheses)} hypotheses with object 'Earth (Updated)':")
        for h in earth_object_hypotheses:
            print(f"  {h.subject.name} {h.relation} {h.object.name} (confidence: {h.confidence})")

        # Example 9: Find hypotheses by subject ID
        print("\nFinding hypotheses by subject ID...")
        subject_id = earth_subject.id
        subject_id_hypotheses = hypothesis_ops.find_hypotheses(subject_id=subject_id)
        print(f"Found {len(subject_id_hypotheses)} hypotheses with subject ID '{subject_id}':")
        for h in subject_id_hypotheses:
            print(f"  {h.subject.name} {h.relation} {h.object.name} (confidence: {h.confidence})")

        # Example 10: Find hypotheses by confidence range
        print("\nFinding hypotheses by confidence range...")
        high_confidence = hypothesis_ops.find_hypotheses(min_confidence=0.99)
        print(f"Found {len(high_confidence)} hypotheses with confidence >= 0.99:")
        for h in high_confidence:
            print(f"  {h.subject.name} {h.relation} {h.object.name} (confidence: {h.confidence})")

        # Example 11: Delete a hypothesis but keep subject and object nodes
        print("\nDeleting the first hypothesis but keeping subject and object nodes...")
        deleted_earth = hypothesis_ops.delete_hypothesis(hypothesis_id, keep_subject_object=True)
        print(f"Earth hypothesis deleted: {deleted_earth}")
        print(f"The subject and object nodes are still in the database and can be reused.")

        # Example 12: Verify that the hypothesis is deleted but subject and object still exist
        print("\nVerifying deletion...")
        deleted_earth_hypothesis = hypothesis_ops.read_hypothesis(hypothesis_id)
        print(f"Earth hypothesis after deletion: {deleted_earth_hypothesis}")

        # Example 13: Find nodes by ID to verify they still exist
        print("\nVerifying that subject and object nodes still exist...")
        subject_node = neo4j_ops.read_node(earth_subject.id)
        object_node = neo4j_ops.read_node(sun_object.id)
        print(f"Subject node still exists: {subject_node is not None}")
        print(f"Object node still exists: {object_node is not None}")

        # # Example 14: Delete the second hypothesis without keeping subject and object
        # print("\nDeleting the second hypothesis without keeping subject and object nodes...")
        # deleted_moon = hypothesis_ops.delete_hypothesis(moon_hypothesis_id, keep_subject_object=False)
        # print(f"Moon hypothesis deleted: {deleted_moon}")
        # print(f"The subject node will be deleted if not used by other hypotheses.")
        # print(f"The object node (Earth) will not be deleted because it's used by other hypotheses.")
        #
        # # Example 15: Verify deletion
        # print("\nVerifying deletion...")
        # deleted_moon_hypothesis = hypothesis_ops.read_hypothesis(moon_hypothesis_id)
        # print(f"Moon hypothesis after deletion: {deleted_moon_hypothesis}")
        #
        # # Check if the Moon node still exists
        # moon_node = neo4j_ops.read_node(moon_subject.id)
        # print(f"Moon node still exists: {moon_node is not None}")
        #
        # # The Earth nodes should still exist because they're used by other hypotheses
        # earth_subject_node = neo4j_ops.read_node(earth_subject.id)
        # earth_object_node = neo4j_ops.read_node(earth_object.id)
        # print(f"Earth subject node still exists: {earth_subject_node is not None}")
        # print(f"Earth object node still exists: {earth_object_node is not None}")

    finally:
        # Close the connection
        neo4j_ops.close()
        print("\nConnection closed.")

if __name__ == "__main__":
    main()
