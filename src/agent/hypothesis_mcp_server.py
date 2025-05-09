"""
Hypothesis MCP Server

This module provides an MCP server with tools for creating Hypothesis objects,
and updating and deleting HypothesisSubject and HypothesisObject in Neo4J.
"""

import os
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from mcp.server import FastMCP

from evidence import Evidence
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

# Initialize the Neo4j operations with a custom ID provider
id_provider = UuidProvider()
neo4j_ops = Neo4jOperations(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, id_provider=id_provider)

# Initialize the Hypothesis operations
hypothesis_ops = HypothesisOperations(neo4j_ops)

# Create the MCP server
mcp = FastMCP("Hypothesis Operations")


@mcp.tool()
async def create_evidence_strategy(evidence_components: list[Evidence]) -> list[Evidence]:
    return evidence_components


@mcp.tool()
async def create_hypothesis(subject: str, relation: str, object_: str, confidence: float) -> Dict[str, Any]:
    """
    Create a new Hypothesis in Neo4j.

    Args:
        subject: The name of the subject
        relation: The relation between subject and object
        object_: The name of the object
        confidence: The confidence level (between 0 and 1)

    Returns:
        A dictionary containing the ID of the created hypothesis
    """
    try:
        # Create a hypothesis using the create_from_strings method
        hypothesis = Hypothesis.create_from_strings(
            subject=subject,
            relation=relation,
            object_=object_,
            confidence=confidence
        )

        # Save the hypothesis to Neo4J
        hypothesis_id = hypothesis_ops.create_hypothesis(hypothesis)

        return {
            "success": True,
            "hypothesis_id": hypothesis_id,
            "message": f"Created hypothesis: {subject} {relation} {object_} (confidence: {confidence})"
        }
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }


@mcp.tool()
async def create_hypothesis_with_objects(subject_name: str, relation: str, object_name: str,
                                         confidence: float) -> Dict[str, Any]:
    """
    Create a new Hypothesis in Neo4j with detailed subject and object properties.

    Args:
        subject_name: The name of the subject
        relation: The relation between subject and object
        object_name: The name of the object
        confidence: The confidence level (between 0 and 1)

    Returns:
        A dictionary containing the ID of the created hypothesis
    """
    try:
        # Create subject
        subject = HypothesisSubject(
            name=subject_name
        )

        # Create object
        object_ = HypothesisObject(
            name=object_name
        )

        # Create hypothesis
        hypothesis = Hypothesis(
            subject=subject,
            relation=relation,
            object=object_,
            confidence=confidence
        )

        # Save the hypothesis to Neo4J
        hypothesis_id = hypothesis_ops.create_hypothesis(hypothesis)

        return {
            "success": True,
            "hypothesis_id": hypothesis_id,
            "subject_id": subject.id,
            "object_id": object_.id,
            "message": f"Created hypothesis: {subject_name} {relation} {object_name} (confidence: {confidence})"
        }
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }


@mcp.tool()
async def get_hypothesis(hypothesis_id: str) -> Dict[str, Any]:
    """
    Get a hypothesis by its ID.

    Args:
        hypothesis_id: The ID of the hypothesis to retrieve

    Returns:
        A dictionary containing the hypothesis data
    """
    try:
        hypothesis = hypothesis_ops.read_hypothesis(hypothesis_id)

        if hypothesis:
            return {
                "success": True,
                "hypothesis": {
                    "id": hypothesis.id,
                    "subject": {
                        "id": hypothesis.subject.id,
                        "name": hypothesis.subject.name
                    },
                    "relation": hypothesis.relation,
                    "object": {
                        "id": hypothesis.object.id,
                        "name": hypothesis.object.name
                    },
                    "confidence": hypothesis.confidence
                }
            }
        else:
            return {
                "success": False,
                "error": f"Hypothesis with ID {hypothesis_id} not found"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }


@mcp.tool()
async def update_hypothesis(hypothesis_id: str, relation: Optional[str] = None,
                            confidence: Optional[float] = None) -> Dict[str, Any]:
    """
    Update a hypothesis by its ID.

    Args:
        hypothesis_id: The ID of the hypothesis to update
        relation: The new relation (optional)
        confidence: The new confidence level (optional)

    Returns:
        A dictionary indicating success or failure
    """
    try:
        # Get the existing hypothesis
        hypothesis = hypothesis_ops.read_hypothesis(hypothesis_id)

        if not hypothesis:
            return {
                "success": False,
                "error": f"Hypothesis with ID {hypothesis_id} not found"
            }

        # Update the fields if provided
        if relation is not None:
            hypothesis.relation = relation

        if confidence is not None:
            hypothesis.confidence = confidence

        # Save the updates
        updated = hypothesis_ops.update_hypothesis(hypothesis)

        if updated:
            return {
                "success": True,
                "message": f"Updated hypothesis with ID {hypothesis_id}"
            }
        else:
            return {
                "success": False,
                "error": f"Failed to update hypothesis with ID {hypothesis_id}"
            }
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }


@mcp.tool()
async def delete_hypothesis(hypothesis_id: str, keep_subject_object: bool = False) -> Dict[str, Any]:
    """
    Delete a hypothesis by its ID.

    Args:
        hypothesis_id: The ID of the hypothesis to delete
        keep_subject_object: If True, keep the subject and object nodes

    Returns:
        A dictionary indicating success or failure
    """
    try:
        deleted = hypothesis_ops.delete_hypothesis(hypothesis_id, keep_subject_object=keep_subject_object)

        if deleted:
            return {
                "success": True,
                "message": f"Deleted hypothesis with ID {hypothesis_id}"
            }
        else:
            return {
                "success": False,
                "error": f"Hypothesis with ID {hypothesis_id} not found or could not be deleted"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }


@mcp.tool()
async def find_hypotheses(subject: Optional[str] = None, relation: Optional[str] = None,
                          object_: Optional[str] = None, min_confidence: Optional[float] = None,
                          max_confidence: Optional[float] = None, subject_id: Optional[str] = None,
                          object_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Find hypotheses matching the given criteria.

    Args:
        subject: Subject name to match (optional)
        relation: Relation to match (optional)
        object_: Object name to match (optional)
        min_confidence: Minimum confidence value (optional)
        max_confidence: Maximum confidence value (optional)
        subject_id: Subject ID to match (optional)
        object_id: Object ID to match (optional)

    Returns:
        A dictionary containing the matching hypotheses
    """
    try:
        hypotheses = hypothesis_ops.find_hypotheses(
            subject=subject,
            relation=relation,
            object_=object_,
            min_confidence=min_confidence,
            max_confidence=max_confidence,
            subject_id=subject_id,
            object_id=object_id
        )

        result = []
        for h in hypotheses:
            result.append({
                "id": h.id,
                "subject": {
                    "id": h.subject.id,
                    "name": h.subject.name
                },
                "relation": h.relation,
                "object": {
                    "id": h.object.id,
                    "name": h.object.name
                },
                "confidence": h.confidence
            })

        return {
            "success": True,
            "count": len(result),
            "hypotheses": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }


@mcp.tool()
async def update_subject(subject_id: str, name: Optional[str] = None) -> Dict[str, Any]:
    """
    Update a HypothesisSubject by its ID.

    Args:
        subject_id: The ID of the subject to update
        name: The new name (optional)

    Returns:
        A dictionary indicating success or failure
    """
    try:
        # Get the subject node
        subject_node = neo4j_ops.read_node(subject_id)

        if not subject_node or subject_node.get("nodeType") != "Subject":
            return {
                "success": False,
                "error": f"Subject with ID {subject_id} not found"
            }

        # Create a properties dictionary for the update
        properties = {}

        if name is not None:
            properties["name"] = name

        if not properties:
            return {
                "success": False,
                "error": "No properties provided for update"
            }

        # Update the subject node
        updated = neo4j_ops.update_node(subject_id, properties)

        if updated:
            return {
                "success": True,
                "message": f"Updated subject with ID {subject_id}"
            }
        else:
            return {
                "success": False,
                "error": f"Failed to update subject with ID {subject_id}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }


@mcp.tool()
async def delete_subject(subject_id: str) -> Dict[str, Any]:
    """
    Delete a HypothesisSubject by its ID.

    Args:
        subject_id: The ID of the subject to delete

    Returns:
        A dictionary indicating success or failure
    """
    try:
        # Check if the subject is used in any hypotheses
        subject_used = hypothesis_ops._is_node_used_elsewhere(subject_id)

        if subject_used:
            return {
                "success": False,
                "error": f"Subject with ID {subject_id} is used in one or more hypotheses and cannot be deleted"
            }

        # Delete the subject node
        deleted = neo4j_ops.delete_node(subject_id)

        if deleted:
            return {
                "success": True,
                "message": f"Deleted subject with ID {subject_id}"
            }
        else:
            return {
                "success": False,
                "error": f"Subject with ID {subject_id} not found or could not be deleted"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }


@mcp.tool()
async def update_object(object_id: str, name: Optional[str] = None) -> Dict[str, Any]:
    """
    Update a HypothesisObject by its ID.

    Args:
        object_id: The ID of the object to update
        name: The new name (optional)

    Returns:
        A dictionary indicating success or failure
    """
    try:
        # Get the object node
        object_node = neo4j_ops.read_node(object_id)

        if not object_node or object_node.get("nodeType") != "Object":
            return {
                "success": False,
                "error": f"Object with ID {object_id} not found"
            }

        # Create a properties dictionary for the update
        properties = {}

        if name is not None:
            properties["name"] = name

        if not properties:
            return {
                "success": False,
                "error": "No properties provided for update"
            }

        # Update the object node
        updated = neo4j_ops.update_node(object_id, properties)

        if updated:
            return {
                "success": True,
                "message": f"Updated object with ID {object_id}"
            }
        else:
            return {
                "success": False,
                "error": f"Failed to update object with ID {object_id}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }


@mcp.tool()
async def delete_object(object_id: str) -> Dict[str, Any]:
    """
    Delete a HypothesisObject by its ID.

    Args:
        object_id: The ID of the object to delete

    Returns:
        A dictionary indicating success or failure
    """
    try:
        # Check if the object is used in any hypotheses
        object_used = hypothesis_ops._is_node_used_elsewhere(object_id)

        if object_used:
            return {
                "success": False,
                "error": f"Object with ID {object_id} is used in one or more hypotheses and cannot be deleted"
            }

        # Delete the object node
        deleted = neo4j_ops.delete_node(object_id)

        if deleted:
            return {
                "success": True,
                "message": f"Deleted object with ID {object_id}"
            }
        else:
            return {
                "success": False,
                "error": f"Object with ID {object_id} not found or could not be deleted"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }


@mcp.tool()
async def create_subject(name: str) -> Dict[str, Any]:
    """
    Create a new HypothesisSubject in Neo4j.

    Args:
        name: The name of the subject

    Returns:
        A dictionary containing the ID of the created subject
    """
    try:
        # Create a subject
        subject = HypothesisSubject(
            name=name
        )

        # Create the subject node in Neo4j
        subject_id = neo4j_ops.create_node(node_type="Subject", properties={
            "name": subject.name,
            "id": subject.id,
            **subject.additional_properties
        })

        return {
            "success": True,
            "subject_id": subject_id,
            "message": f"Created subject: {name}"
        }
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }


@mcp.tool()
async def create_object(name: str) -> Dict[str, Any]:
    """
    Create a new HypothesisObject in Neo4j.

    Args:
        name: The name of the object

    Returns:
        A dictionary containing the ID of the created object
    """
    try:
        # Create an object
        object_ = HypothesisObject(
            name=name
        )

        # Create the object node in Neo4j
        object_id = neo4j_ops.create_node(node_type="Object", properties={
            "name": object_.name,
            "id": object_.id,
            **object_.additional_properties
        })

        return {
            "success": True,
            "object_id": object_id,
            "message": f"Created object: {name}"
        }
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }


@mcp.tool()
async def get_subject(subject_id: str) -> Dict[str, Any]:
    """
    Get a subject by its ID.

    Args:
        subject_id: The ID of the subject to retrieve

    Returns:
        A dictionary containing the subject data
    """
    try:
        subject_node = neo4j_ops.read_node(subject_id)

        if subject_node and subject_node.get("nodeType") == "Subject":
            # Convert to HypothesisSubject format
            subject = HypothesisSubject.from_dict(subject_node)

            return {
                "success": True,
                "subject": {
                    "id": subject.id,
                    "name": subject.name
                }
            }
        else:
            return {
                "success": False,
                "error": f"Subject with ID {subject_id} not found"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }


@mcp.tool()
async def get_object(object_id: str) -> Dict[str, Any]:
    """
    Get an object by its ID.

    Args:
        object_id: The ID of the object to retrieve

    Returns:
        A dictionary containing the object data
    """
    try:
        object_node = neo4j_ops.read_node(object_id)

        if object_node and object_node.get("nodeType") == "Object":
            # Convert to HypothesisObject format
            object_ = HypothesisObject.from_dict(object_node)

            return {
                "success": True,
                "object": {
                    "id": object_.id,
                    "name": object_.name
                }
            }
        else:
            return {
                "success": False,
                "error": f"Object with ID {object_id} not found"
            }
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }


@mcp.tool()
async def find_subjects(name: Optional[str] = None,
                        properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Find subjects matching the given criteria.

    Args:
        name: Name to match (optional)
        properties: Properties to match (optional)

    Returns:
        A dictionary containing the matching subjects
    """
    try:
        search_properties = {}
        if name is not None:
            search_properties["name"] = name

        if properties is not None:
            search_properties.update(properties)

        subjects = neo4j_ops.find_nodes(
            node_type="Subject",
            properties=search_properties
        )

        result = []
        for s in subjects:
            # Convert to HypothesisSubject format
            subject = HypothesisSubject.from_dict(s)

            result.append({
                "id": subject.id,
                "name": subject.name
            })

        return {
            "success": True,
            "count": len(result),
            "subjects": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }


@mcp.tool()
async def find_objects(name: Optional[str] = None,
                       properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Find objects matching the given criteria.

    Args:
        name: Name to match (optional)
        properties: Properties to match (optional)

    Returns:
        A dictionary containing the matching objects
    """
    try:
        search_properties = {}
        if name is not None:
            search_properties["name"] = name

        if properties is not None:
            search_properties.update(properties)

        objects = neo4j_ops.find_nodes(
            node_type="Object",
            properties=search_properties
        )

        result = []
        for o in objects:
            # Convert to HypothesisObject format
            object_ = HypothesisObject.from_dict(o)

            result.append({
                "id": object_.id,
                "name": object_.name
            })

        return {
            "success": True,
            "count": len(result),
            "objects": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }


@mcp.tool()
async def create_multiple_hypotheses(hypotheses_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create multiple Hypothesis objects at once.

    Args:
        hypotheses_data: A list of dictionaries, each containing data for a hypothesis:
            - subject: The name of the subject
            - relation: The relation between subject and object
            - object: The name of the object
            - confidence: The confidence level (between 0 and 1)
            - additional_properties: Additional properties for the hypothesis (optional)

    Returns:
        A dictionary containing the IDs of the created hypotheses
    """
    try:
        created_hypotheses = []
        failed_hypotheses = []

        for idx, hypo_data in enumerate(hypotheses_data):
            try:
                # Extract required fields
                subject = hypo_data.get("subject")
                relation = hypo_data.get("relation")
                object_ = hypo_data.get("object")
                confidence = hypo_data.get("confidence")

                # Validate required fields
                if not subject or not relation or not object_ or confidence is None:
                    failed_hypotheses.append({
                        "index": idx,
                        "error": "Missing required fields (subject, relation, object, confidence)"
                    })
                    continue

                # Create a hypothesis using the create_from_strings method
                hypothesis = Hypothesis.create_from_strings(
                    subject=subject,
                    relation=relation,
                    object_=object_,
                    confidence=confidence
                )

                # Save the hypothesis to Neo4J
                hypothesis_id = hypothesis_ops.create_hypothesis(hypothesis)

                created_hypotheses.append({
                    "index": idx,
                    "hypothesis_id": hypothesis_id,
                    "subject": subject,
                    "relation": relation,
                    "object": object_,
                    "confidence": confidence
                })

            except Exception as e:
                failed_hypotheses.append({
                    "index": idx,
                    "error": str(e)
                })

        return {
            "success": True,
            "created_count": len(created_hypotheses),
            "failed_count": len(failed_hypotheses),
            "created_hypotheses": created_hypotheses,
            "failed_hypotheses": failed_hypotheses
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }


@mcp.tool()
async def create_multiple_hypotheses_with_objects(hypotheses_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create multiple Hypothesis objects at once with detailed subject and object properties.

    Args:
        hypotheses_data: A list of dictionaries, each containing data for a hypothesis:
            - subject_name: The name of the subject
            - relation: The relation between subject and object
            - object_name: The name of the object
            - confidence: The confidence level (between 0 and 1)
            - subject_properties: Additional properties for the subject (optional)
            - object_properties: Additional properties for the object (optional)
            - hypothesis_properties: Additional properties for the hypothesis (optional)

    Returns:
        A dictionary containing the IDs of the created hypotheses
    """
    try:
        created_hypotheses = []
        failed_hypotheses = []

        for idx, hypo_data in enumerate(hypotheses_data):
            try:
                # Extract required fields
                subject_name = hypo_data.get("subject_name")
                relation = hypo_data.get("relation")
                object_name = hypo_data.get("object_name")
                confidence = hypo_data.get("confidence")

                # Validate required fields
                if not subject_name or not relation or not object_name or confidence is None:
                    failed_hypotheses.append({
                        "index": idx,
                        "error": "Missing required fields (subject_name, relation, object_name, confidence)"
                    })
                    continue

                # Create subject
                subject = HypothesisSubject(
                    name=subject_name
                )

                # Create object
                object_ = HypothesisObject(
                    name=object_name
                )

                # Create hypothesis
                hypothesis = Hypothesis(
                    subject=subject,
                    relation=relation,
                    object=object_,
                    confidence=confidence
                )

                # Save the hypothesis to Neo4J
                hypothesis_id = hypothesis_ops.create_hypothesis(hypothesis)

                created_hypotheses.append({
                    "index": idx,
                    "hypothesis_id": hypothesis_id,
                    "subject_id": subject.id,
                    "object_id": object_.id,
                    "subject_name": subject_name,
                    "relation": relation,
                    "object_name": object_name,
                    "confidence": confidence
                })

            except Exception as e:
                failed_hypotheses.append({
                    "index": idx,
                    "error": str(e)
                })

        return {
            "success": True,
            "created_count": len(created_hypotheses),
            "failed_count": len(failed_hypotheses),
            "created_hypotheses": created_hypotheses,
            "failed_hypotheses": failed_hypotheses
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }


@mcp.tool()
async def get_all_hypotheses() -> Dict[str, Any]:
    """
    Retrieve all available Hypothesis instances from the database.

    Returns:
        A dictionary containing all hypotheses
    """
    try:
        # Call find_hypotheses without any parameters to get all hypotheses
        hypotheses = hypothesis_ops.find_hypotheses()

        result = []
        for h in hypotheses:
            result.append({
                "id": h.id,
                "subject": {
                    "id": h.subject.id,
                    "name": h.subject.name
                },
                "relation": h.relation,
                "object": {
                    "id": h.object.id,
                    "name": h.object.name
                },
                "confidence": h.confidence
            })

        return {
            "success": True,
            "count": len(result),
            "hypotheses": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }


@mcp.tool()
async def breakdown_hypothesis(hypotheses: List[Hypothesis]) -> List[Hypothesis]:
    """
    Process a list of Hypothesis objects and return the same list.

    This tool is a simple pass-through that accepts Hypothesis objects and returns them.
    It can be used as a building block for more complex hypothesis processing pipelines.

    Args:
        hypotheses: A list of Hypothesis objects to process

    Returns:
        A dictionary containing the processed hypotheses (same as input)
    """
    try:
        result = []
        for h in hypotheses:
            result.append({
                "id": h.id,
                "subject": {
                    "id": h.subject.id,
                    "name": h.subject.name
                },
                "relation": h.relation,
                "object": {
                    "id": h.object.id,
                    "name": h.object.name
                },
                "confidence": h.confidence
            })

        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }


if __name__ == "__main__":
    # Initialize and run the server
    print("Starting Hypothesis MCP server...")
    mcp.run(transport='stdio')
