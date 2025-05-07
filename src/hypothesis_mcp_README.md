# Hypothesis MCP Server

This module provides an MCP (Model-Control-Persistence) server with tools for creating Hypothesis objects, and updating and deleting HypothesisSubject and HypothesisObject in Neo4J.

## Features

- Create, read, update, and delete Hypothesis objects in Neo4J
- Create, read, update, and delete HypothesisSubject objects in Neo4J
- Create, read, update, and delete HypothesisObject objects in Neo4J
- Find hypotheses by subject, relation, object, or confidence range
- Find subjects and objects by name or properties
- Comprehensive error handling and validation
- JSON-RPC interface for easy integration with other systems

## Installation

1. Make sure you have Neo4J installed and running.
2. Install the required Python dependencies:

```bash
pip install neo4j python-dotenv mcp
```

## Configuration

The module uses environment variables for Neo4J connection details. Create a `.env` file in your project root with the following variables:

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

## Usage

### Starting the MCP Server

You can start the MCP server by running the `hypothesis_mcp_server.py` script:

```bash
python src/agent/hypothesis_mcp_server.py
```

This will start the server with the stdio transport, which allows you to communicate with it using JSON-RPC messages over standard input/output.

### Using the MCP Client

You can use the `HypothesisMCPClient` class from the `hypothesis_mcp_test.py` script to interact with the server:

```python
import asyncio
from hypothesis_mcp_test import HypothesisMCPClient

async def main():
    client = HypothesisMCPClient()
    
    try:
        # Start the server
        await client.start_server()
        
        # Call a tool
        result = await client.call_tool(
            "create_subject",
            name="Earth",
            additional_properties={
                "type": "Planet",
                "diameter_km": 12742
            }
        )
        print(f"Created subject: {result}")
        
    finally:
        # Stop the server
        await client.stop_server()

if __name__ == "__main__":
    asyncio.run(main())
```

### Available Tools

The MCP server provides the following tools:

#### Subject Operations

- `create_subject`: Create a new HypothesisSubject in Neo4j
- `get_subject`: Get a subject by its ID
- `update_subject`: Update a HypothesisSubject by its ID
- `delete_subject`: Delete a HypothesisSubject by its ID
- `find_subjects`: Find subjects matching the given criteria

#### Object Operations

- `create_object`: Create a new HypothesisObject in Neo4j
- `get_object`: Get an object by its ID
- `update_object`: Update a HypothesisObject by its ID
- `delete_object`: Delete a HypothesisObject by its ID
- `find_objects`: Find objects matching the given criteria

#### Hypothesis Operations

- `create_hypothesis`: Create a new Hypothesis in Neo4j
- `create_hypothesis_with_objects`: Create a new Hypothesis in Neo4j with detailed subject and object properties
- `get_hypothesis`: Get a hypothesis by its ID
- `update_hypothesis`: Update a hypothesis by its ID
- `delete_hypothesis`: Delete a hypothesis by its ID
- `find_hypotheses`: Find hypotheses matching the given criteria

### Examples

#### Creating a Subject

```python
result = await client.call_tool(
    "create_subject",
    name="Earth",
    additional_properties={
        "type": "Planet",
        "diameter_km": 12742
    }
)
subject_id = result["subject_id"]
```

#### Creating an Object

```python
result = await client.call_tool(
    "create_object",
    name="Sun",
    additional_properties={
        "type": "Star",
        "diameter_km": 1392700
    }
)
object_id = result["object_id"]
```

#### Creating a Hypothesis

```python
# Simple creation
result = await client.call_tool(
    "create_hypothesis",
    subject="Earth",
    relation="orbits",
    object_="Sun",
    confidence=0.99,
    additional_properties={
        "source": "Astronomical observation",
        "verified": True
    }
)
hypothesis_id = result["hypothesis_id"]

# Creation with detailed subject and object properties
result = await client.call_tool(
    "create_hypothesis_with_objects",
    subject_name="Earth",
    relation="orbits",
    object_name="Sun",
    confidence=0.99,
    subject_properties={
        "type": "Planet",
        "diameter_km": 12742
    },
    object_properties={
        "type": "Star",
        "diameter_km": 1392700
    },
    hypothesis_properties={
        "source": "Astronomical observation",
        "verified": True
    }
)
hypothesis_id = result["hypothesis_id"]
subject_id = result["subject_id"]
object_id = result["object_id"]
```

#### Getting a Hypothesis

```python
result = await client.call_tool(
    "get_hypothesis",
    hypothesis_id=hypothesis_id
)
hypothesis = result["hypothesis"]
```

#### Updating a Hypothesis

```python
result = await client.call_tool(
    "update_hypothesis",
    hypothesis_id=hypothesis_id,
    relation="orbits_around",
    confidence=0.999,
    additional_properties={
        "last_verified": "2023-06-15"
    }
)
```

#### Finding Hypotheses

```python
# Find by relation
result = await client.call_tool(
    "find_hypotheses",
    relation="orbits_around"
)
hypotheses = result["hypotheses"]

# Find by subject
result = await client.call_tool(
    "find_hypotheses",
    subject="Earth"
)
hypotheses = result["hypotheses"]

# Find by confidence range
result = await client.call_tool(
    "find_hypotheses",
    min_confidence=0.9,
    max_confidence=1.0
)
hypotheses = result["hypotheses"]
```

#### Deleting a Hypothesis

```python
# Delete a hypothesis but keep the subject and object nodes
result = await client.call_tool(
    "delete_hypothesis",
    hypothesis_id=hypothesis_id,
    keep_subject_object=True
)

# Delete a hypothesis and also delete the subject and object nodes if not used elsewhere
result = await client.call_tool(
    "delete_hypothesis",
    hypothesis_id=hypothesis_id,
    keep_subject_object=False
)
```

#### Updating a Subject

```python
result = await client.call_tool(
    "update_subject",
    subject_id=subject_id,
    name="Earth (Updated)",
    additional_properties={
        "mass_kg": 5.97e24,
        "has_atmosphere": True
    }
)
```

#### Deleting a Subject

```python
result = await client.call_tool(
    "delete_subject",
    subject_id=subject_id
)
```

#### Finding Subjects

```python
result = await client.call_tool(
    "find_subjects",
    name="Earth"
)
subjects = result["subjects"]
```

## Integration with LangGraph

The Hypothesis MCP server can be integrated with LangGraph using the `langchain_mcp_adapters` package. Here's an example of how to do this:

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import ToolNode

# Initialize the MCP client
mcp_client = MultiServerMCPClient(
    servers=[
        {
            "name": "hypothesis",
            "command": {
                "args": ["python", "src/agent/hypothesis_mcp_server.py"],
                "env": {"PYTHONPATH": "."}
            }
        }
    ]
)

# Get the MCP tools
mcp_tools = mcp_client.get_tools()

# Create a tool node in your graph
workflow.add_node("hypothesis_tool", ToolNode(mcp_tools, handle_tool_errors=True))
```

## Complete Example

See the `hypothesis_mcp_test.py` file for a complete example of how to use all the MCP tools.

## Error Handling

All tools return a dictionary with a `success` key that indicates whether the operation was successful. If `success` is `False`, the dictionary will also contain an `error` key with a description of the error.

```python
result = await client.call_tool(
    "get_hypothesis",
    hypothesis_id="non_existent_id"
)

if not result["success"]:
    print(f"Error: {result['error']}")
```

## Notes

- Each hypothesis consists of three nodes in Neo4J: a subject node, a relation node, and an object node.
- The subject and object nodes can be reused across multiple hypotheses.
- When deleting a hypothesis, you can choose whether to keep the subject and object nodes.
- Subject and object nodes cannot be deleted if they are used in any hypotheses.
