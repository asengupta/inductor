"""
Neo4J Operations Example

This script demonstrates how to use the Neo4jOperations class to perform CRUD operations on Neo4J nodes.
"""

import os
from dotenv import load_dotenv
from neo4j_operations import Neo4jOperations
from id_provider import UuidProvider

# Load environment variables from .env file
load_dotenv("./env/.env")

# Get Neo4j connection details from environment variables
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

def main():
    """Run the example."""
    # Initialize the Neo4j operations with a custom ID provider
    id_provider = UuidProvider()  # You can use your own implementation of IdProvider here
    neo4j_ops = Neo4jOperations(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, id_provider=id_provider)

    # Alternatively, you can use the default ID provider (UuidProvider)
    # neo4j_ops = Neo4jOperations(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

    try:
        # Example 1: Create a node
        print("Creating a node...")
        person_id = neo4j_ops.create_node(node_type="Person", properties={
            "name": "John Doe",
            "age": 30,
            "email": "john.doe@example.com"
        }, labels=["Employee", "Developer"])
        print(f"Created node with ID: {person_id}")

        # Example 2: Read a node
        print("\nReading the node...")
        person = neo4j_ops.read_node(person_id)
        print(f"Node data: {person}")

        # Example 3: Update a node
        print("\nUpdating the node...")
        updated = neo4j_ops.update_node(
            node_id=person_id,
            properties={
                "age": 31,
                "position": "Senior Developer"
            }
        )
        print(f"Node updated: {updated}")

        # Example 4: Read the updated node
        print("\nReading the updated node...")
        updated_person = neo4j_ops.read_node(person_id)
        print(f"Updated node data: {updated_person}")

        # Example 5: Find nodes by type and properties
        print("\nFinding nodes by type and properties...")
        people = neo4j_ops.find_nodes(
            node_type="Person",
            properties={"age": 31}
        )
        print(f"Found {len(people)} nodes:")
        for person in people:
            print(f"  - {person}")

        # # Example 6: Delete the node
        # print("\nDeleting the node...")
        # deleted = neo4j_ops.delete_node(person_id)
        # print(f"Node deleted: {deleted}")
        #
        # # Example 7: Verify deletion
        # print("\nVerifying deletion...")
        # deleted_person = neo4j_ops.read_node(person_id)
        # print(f"Node after deletion: {deleted_person}")

    finally:
        # Close the connection
        neo4j_ops.close()
        print("\nConnection closed.")

if __name__ == "__main__":
    main()
