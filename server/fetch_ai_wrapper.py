import os
import asyncio
from dotenv import load_dotenv
from backend import run_workflow

from uagents_adapter import LangchainRegisterTool, cleanup_uagent
from uagents_adapter.langchain import AgentManager

load_dotenv()

AGENTVERSE_API_KEY = os.getenv("AGENTVERSE_API_KEY")

# Wrap async function inside sync wrapper
async def speech_analysis_agent(query: str) -> str:
    try:
        result = await run_workflow(query)
        return result
    except Exception as e:
        return f"Error: {e}"

def main():
    manager = AgentManager()

    # Register the tool with Fetch.ai
    tool = LangchainRegisterTool()
    agent_info = tool.invoke({
        "agent_obj": speech_analysis_agent,
        "name": "speech_analysis_agent",
        "port": 8080,
        "description": "Analyzes speech transcripts across multiple communication categories",
        "api_token": AGENTVERSE_API_KEY,
        "mailbox": True
    })

    print("Agent registered:", agent_info)

    try:
        manager.run_forever()
    except KeyboardInterrupt:
        print("Shutting down speech_analysis_agent...")
        cleanup_uagent("speech_analysis_agent")
        print("Agent stopped.")

if __name__ == "__main__":
    main()
