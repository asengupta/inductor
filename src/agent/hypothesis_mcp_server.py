"""
Hypothesis MCP Server

This module provides an MCP server with tools for creating Hypothesis objects,
and updating and deleting HypothesisSubject and HypothesisObject in Neo4J.
"""

import os
from typing import Any, Optional

from dotenv import load_dotenv
from mcp.server import FastMCP

from src.domain.beta_bernoulli_belief import BetaBernoulliBelief, equally_likely
from src.domain.evidence import Evidence
from src.domain.hypothesis import Hypothesis
from src.domain.hypothesis_object import HypothesisObject
from src.domain.hypothesis_operations import HypothesisOperations
from src.domain.hypothesis_subject import HypothesisSubject
from src.domain.id_provider import UuidProvider
from src.domain.neo4j_operations import Neo4jOperations

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
async def crcrcrcrcrc(evidence_components: list[Evidence]) -> list[Evidence]:
    return evidence_components


@mcp.tool()
async def create_evidence_strategy(evidence_components: list[Evidence]) -> list[Evidence]:
    return evidence_components


@mcp.tool()
async def breakdown_hypothesis(hypotheses: list[Hypothesis]) -> list[Hypothesis]:
    return hypotheses


@mcp.tool()
async def create_hypothesis(subject: str, relation: str, object_: str, confidence: float = None) -> dict[str, Any]:
    """
    Create a new Hypothesis in Neo4j.

    Args:
        subject: The name of the subject
        relation: The relation between subject and object
        object_: The name of the object
        confidence: The confidence level (between 0 and 1) - deprecated, use belief instead

    Returns:
        A dictionary containing the ID of the created hypothesis
    """
    try:
        # Create a hypothesis using the create_from_strings method
        belief = equally_likely()
        hypothesis = Hypothesis.create_from_strings(
            subject=subject,
            relation=relation,
            object_=object_,
            belief=belief
        )

        # Save the hypothesis to Neo4J
        hypothesis_id = hypothesis_ops.create_hypothesis(hypothesis)

        return {
            "success": True,
            "hypothesis_id": hypothesis_id,
            "message": f"Created hypothesis: {subject} {relation} {object_} (belief: {belief})"
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
                                         confidence: float = None) -> dict[str, Any]:
    """
    Create a new Hypothesis in Neo4j with detailed subject and object properties.

    Args:
        subject_name: The name of the subject
        relation: The relation between subject and object
        object_name: The name of the object
        confidence: The confidence level (between 0 and 1) - deprecated, use belief instead

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
        belief = equally_likely()
        hypothesis = Hypothesis(
            subject=subject,
            relation=relation,
            object=object_,
            belief=belief
        )

        # Save the hypothesis to Neo4J
        hypothesis_id = hypothesis_ops.create_hypothesis(hypothesis)

        return {
            "success": True,
            "hypothesis_id": hypothesis_id,
            "subject_id": subject.id,
            "object_id": object_.id,
            "message": f"Created hypothesis: {subject_name} {relation} {object_name} (belief: {belief})"
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
async def get_hypothesis(hypothesis_id: str) -> dict[str, Any]:
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
                    "belief": hypothesis.belief.to_dict()
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
                            belief_alpha: Optional[int] = None,
                            belief_beta: Optional[int] = None) -> dict[str, Any]:
    """
    Update a hypothesis by its ID.

    Args:
        hypothesis_id: The ID of the hypothesis to update
        relation: The new relation (optional)
        belief_alpha: The new belief alpha parameter (optional)
        belief_beta: The new belief beta parameter (optional)

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

        if belief_alpha is not None and belief_beta is not None:
            hypothesis.belief = BetaBernoulliBelief(alpha=belief_alpha, beta=belief_beta)
        elif belief_alpha is not None:
            hypothesis.belief = BetaBernoulliBelief(alpha=belief_alpha, beta=hypothesis.belief.beta)
        elif belief_beta is not None:
            hypothesis.belief = BetaBernoulliBelief(alpha=hypothesis.belief.alpha, beta=belief_beta)

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
async def delete_hypothesis(hypothesis_id: str, keep_subject_object: bool = False) -> dict[str, Any]:
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
                          object_: Optional[str] = None, min_alpha: Optional[int] = None,
                          max_alpha: Optional[int] = None, min_beta: Optional[int] = None,
                          max_beta: Optional[int] = None, subject_id: Optional[str] = None,
                          object_id: Optional[str] = None) -> dict[str, Any]:
    """
    Find hypotheses matching the given criteria.

    Args:
        subject: Subject name to match (optional)
        relation: Relation to match (optional)
        object_: Object name to match (optional)
        min_alpha: Minimum alpha value for belief (optional)
        max_alpha: Maximum alpha value for belief (optional)
        min_beta: Minimum beta value for belief (optional)
        max_beta: Maximum beta value for belief (optional)
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
            min_alpha=min_alpha,
            max_alpha=max_alpha,
            min_beta=min_beta,
            max_beta=max_beta,
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
                "belief": h.belief.to_dict()
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
async def update_subject(subject_id: str, name: Optional[str] = None) -> dict[str, Any]:
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
async def delete_subject(subject_id: str) -> dict[str, Any]:
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
async def update_object(object_id: str, name: Optional[str] = None) -> dict[str, Any]:
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
async def delete_object(object_id: str) -> dict[str, Any]:
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
async def create_subject(name: str) -> dict[str, Any]:
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
async def create_object(name: str) -> dict[str, Any]:
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
async def get_subject(subject_id: str) -> dict[str, Any]:
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
async def get_object(object_id: str) -> dict[str, Any]:
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
                        properties: Optional[dict[str, Any]] = None) -> dict[str, Any]:
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
                       properties: Optional[dict[str, Any]] = None) -> dict[str, Any]:
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
async def create_multiple_hypotheses(hypotheses_data: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Create multiple Hypothesis objects at once.

    Args:
        hypotheses_data: A list of dictionaries, each containing data for a hypothesis:
            - subject: The name of the subject
            - relation: The relation between subject and object
            - object: The name of the object
            - belief: (Optional) A dictionary with alpha and beta values for the belief
              If not provided, equally_likely() will be used
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
                belief_data = hypo_data.get("belief")

                # Validate required fields
                if not subject or not relation or not object_:
                    failed_hypotheses.append({
                        "index": idx,
                        "error": "Missing required fields (subject, relation, object)"
                    })
                    continue

                # Create belief object
                if belief_data and isinstance(belief_data, dict):
                    alpha = belief_data.get("alpha")
                    beta = belief_data.get("beta")
                    if alpha is not None and beta is not None:
                        belief = BetaBernoulliBelief(alpha=alpha, beta=beta)
                    else:
                        belief = equally_likely()
                else:
                    belief = equally_likely()

                # Create a hypothesis using the create_from_strings method
                hypothesis = Hypothesis.create_from_strings(
                    subject=subject,
                    relation=relation,
                    object_=object_,
                    belief=belief
                )

                # Save the hypothesis to Neo4J
                hypothesis_id = hypothesis_ops.create_hypothesis(hypothesis)

                created_hypotheses.append({
                    "index": idx,
                    "hypothesis_id": hypothesis_id,
                    "subject": subject,
                    "relation": relation,
                    "object": object_,
                    "belief": belief.to_dict()
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
async def create_multiple_hypotheses_with_objects(hypotheses_data: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Create multiple Hypothesis objects at once with detailed subject and object properties.

    Args:
        hypotheses_data: A list of dictionaries, each containing data for a hypothesis:
            - subject_name: The name of the subject
            - relation: The relation between subject and object
            - object_name: The name of the object
            - belief: (Optional) A dictionary with alpha and beta values for the belief
              If not provided, equally_likely() will be used
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
                belief_data = hypo_data.get("belief")

                # Validate required fields
                if not subject_name or not relation or not object_name:
                    failed_hypotheses.append({
                        "index": idx,
                        "error": "Missing required fields (subject_name, relation, object_name)"
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

                # Create belief object
                if belief_data and isinstance(belief_data, dict):
                    alpha = belief_data.get("alpha")
                    beta = belief_data.get("beta")
                    if alpha is not None and beta is not None:
                        belief = BetaBernoulliBelief(alpha=alpha, beta=beta)
                    else:
                        belief = equally_likely()
                else:
                    belief = equally_likely()

                # Create hypothesis
                hypothesis = Hypothesis(
                    subject=subject,
                    relation=relation,
                    object=object_,
                    belief=belief
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
                    "belief": belief.to_dict()
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
async def get_all_hypotheses() -> dict[str, Any]:
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
                "belief": h.belief.to_dict()
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


if __name__ == "__main__":
    # Initialize and run the server
    print("Starting Hypothesis MCP server...")
    mcp.run(transport='stdio')
