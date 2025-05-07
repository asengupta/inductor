"""
Hypothesis MCP Test

This script demonstrates how to use the Hypothesis MCP server to perform CRUD operations
on Hypothesis objects, HypothesisSubject, and HypothesisObject in Neo4J.
"""

import os
import asyncio
import json
import subprocess
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("./env/.env")

# Path to the MCP server script
MCP_SERVER_PATH = os.path.join(os.path.dirname(__file__), "agent", "hypothesis_mcp_server.py")

class HypothesisMCPClient:
    """A client for interacting with the Hypothesis MCP server."""

    def __init__(self):
        """Initialize the client."""
        self.process = None

    async def start_server(self):
        """Start the MCP server as a subprocess."""
        self.process = subprocess.Popen(
            ["python", MCP_SERVER_PATH],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        # Wait for the server to start
        await asyncio.sleep(1)

    async def stop_server(self):
        """Stop the MCP server."""
        if self.process:
            self.process.terminate()
            await asyncio.sleep(0.5)
            self.process = None

    async def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Call a tool on the MCP server.

        Args:
            tool_name: The name of the tool to call
            **kwargs: The arguments to pass to the tool

        Returns:
            The response from the tool
        """
        if not self.process:
            raise RuntimeError("Server not started")

        # Create the request
        request = {
            "jsonrpc": "2.0",
            "method": "mcp.call_tool",
            "params": {
                "name": tool_name,
                "params": kwargs
            },
            "id": 1
        }

        # Send the request
        request_str = json.dumps(request) + "\n"
        self.process.stdin.write(request_str)
        self.process.stdin.flush()

        # Read the response
        response_str = self.process.stdout.readline()
        response = json.loads(response_str)

        if "error" in response:
            raise RuntimeError(f"Error calling tool: {response['error']}")

        return response["result"]

async def run_test():
    """Run the test."""
    client = HypothesisMCPClient()

    try:
        print("Starting Hypothesis MCP server...")
        await client.start_server()

        print("\n=== Testing Subject Operations ===")

        # Create a subject
        print("\nCreating a subject...")
        earth_result = await client.call_tool(
            "create_subject",
            name="Earth",
            additional_properties={
                "type": "Planet",
                "diameter_km": 12742
            }
        )
        print(f"Result: {earth_result}")
        earth_id = earth_result["subject_id"]

        # Get the subject
        print("\nGetting the subject...")
        earth_get_result = await client.call_tool(
            "get_subject",
            subject_id=earth_id
        )
        print(f"Result: {earth_get_result}")

        # Update the subject
        print("\nUpdating the subject...")
        earth_update_result = await client.call_tool(
            "update_subject",
            subject_id=earth_id,
            additional_properties={
                "mass_kg": 5.97e24,
                "has_atmosphere": True
            }
        )
        print(f"Result: {earth_update_result}")

        # Get the updated subject
        print("\nGetting the updated subject...")
        earth_get_updated_result = await client.call_tool(
            "get_subject",
            subject_id=earth_id
        )
        print(f"Result: {earth_get_updated_result}")

        print("\n=== Testing Object Operations ===")

        # Create an object
        print("\nCreating an object...")
        sun_result = await client.call_tool(
            "create_object",
            name="Sun",
            additional_properties={
                "type": "Star",
                "diameter_km": 1392700
            }
        )
        print(f"Result: {sun_result}")
        sun_id = sun_result["object_id"]

        # Get the object
        print("\nGetting the object...")
        sun_get_result = await client.call_tool(
            "get_object",
            object_id=sun_id
        )
        print(f"Result: {sun_get_result}")

        # Update the object
        print("\nUpdating the object...")
        sun_update_result = await client.call_tool(
            "update_object",
            object_id=sun_id,
            additional_properties={
                "mass_kg": 1.989e30,
                "temperature_k": 5778
            }
        )
        print(f"Result: {sun_update_result}")

        # Get the updated object
        print("\nGetting the updated object...")
        sun_get_updated_result = await client.call_tool(
            "get_object",
            object_id=sun_id
        )
        print(f"Result: {sun_get_updated_result}")

        print("\n=== Testing Hypothesis Operations ===")

        # Create a hypothesis
        print("\nCreating a hypothesis...")
        hypothesis_result = await client.call_tool(
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
        print(f"Result: {hypothesis_result}")
        hypothesis_id = hypothesis_result["hypothesis_id"]

        # Get the hypothesis
        print("\nGetting the hypothesis...")
        hypothesis_get_result = await client.call_tool(
            "get_hypothesis",
            hypothesis_id=hypothesis_id
        )
        print(f"Result: {hypothesis_get_result}")

        # Update the hypothesis
        print("\nUpdating the hypothesis...")
        hypothesis_update_result = await client.call_tool(
            "update_hypothesis",
            hypothesis_id=hypothesis_id,
            relation="orbits_around",
            confidence=0.999,
            additional_properties={
                "last_verified": "2023-06-15"
            }
        )
        print(f"Result: {hypothesis_update_result}")

        # Get the updated hypothesis
        print("\nGetting the updated hypothesis...")
        hypothesis_get_updated_result = await client.call_tool(
            "get_hypothesis",
            hypothesis_id=hypothesis_id
        )
        print(f"Result: {hypothesis_get_updated_result}")

        # Find hypotheses
        print("\nFinding hypotheses by relation...")
        find_result = await client.call_tool(
            "find_hypotheses",
            relation="orbits_around"
        )
        print(f"Result: {find_result}")

        # Create another hypothesis with the same subject
        print("\nCreating another hypothesis with the same subject...")
        moon_result = await client.call_tool(
            "create_object",
            name="Moon",
            additional_properties={
                "type": "Natural Satellite",
                "diameter_km": 3474
            }
        )
        moon_id = moon_result["object_id"]

        moon_hypothesis_result = await client.call_tool(
            "create_hypothesis",
            subject="Moon",
            relation="orbits",
            object_="Earth",
            confidence=0.999,
            additional_properties={
                "source": "Astronomical observation",
                "verified": True
            }
        )
        print(f"Result: {moon_hypothesis_result}")
        moon_hypothesis_id = moon_hypothesis_result["hypothesis_id"]

        # Find all hypotheses
        print("\nFinding all hypotheses...")
        all_hypotheses_result = await client.call_tool(
            "find_hypotheses"
        )
        print(f"Result: {all_hypotheses_result}")

        # Clean up
        print("\n=== Cleaning Up ===")

        # Delete the hypotheses
        print("\nDeleting the hypotheses...")
        delete_earth_result = await client.call_tool(
            "delete_hypothesis",
            hypothesis_id=hypothesis_id,
            keep_subject_object=True
        )
        print(f"Result: {delete_earth_result}")

        delete_moon_result = await client.call_tool(
            "delete_hypothesis",
            hypothesis_id=moon_hypothesis_id,
            keep_subject_object=True
        )
        print(f"Result: {delete_moon_result}")

        # Delete the objects
        print("\nDeleting the objects...")
        delete_sun_result = await client.call_tool(
            "delete_object",
            object_id=sun_id
        )
        print(f"Result: {delete_sun_result}")

        delete_moon_result = await client.call_tool(
            "delete_object",
            object_id=moon_id
        )
        print(f"Result: {delete_moon_result}")

        # Delete the subject
        print("\nDeleting the subject...")
        delete_earth_result = await client.call_tool(
            "delete_subject",
            subject_id=earth_id
        )
        print(f"Result: {delete_earth_result}")

    finally:
        print("\nStopping Hypothesis MCP server...")
        await client.stop_server()

if __name__ == "__main__":
    asyncio.run(run_test())
