import asyncio
from src.perestroika.workflow import run_workflow

if __name__ == "__main__":
    """
    Entry point for running the perestroika workflow.
    This workflow calls the cmd_line_mcp server running in a separate process.
    """
    print("Starting perestroika workflow...")
    asyncio.run(run_workflow())
