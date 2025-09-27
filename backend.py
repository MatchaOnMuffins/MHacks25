import asyncio
import json
from typing import List, Literal
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage

# --- API Config ---
MODEL_NAME = "gemini-2.5-flash-preview-05-20"
GEMINI_API_KEY = "AIzaSyCt0VNKuwG5_j7Lt4FuVzFT1inK4fP1j8g"

# --- 1. Pydantic Models ---
class SubAgentTask(BaseModel):
    category: Literal["FLUENCY", "PROSODY", "PRAGMATICS", "CONSIDERATION", "TIME_BALANCE"]
    text_to_analyze: str

class RouterContext(BaseModel):
    subagents_to_call: List[SubAgentTask]

class SubAgentReport(BaseModel):
    category: str
    score: float = Field(ge=0.0, le=1.0)
    what_went_right: str
    what_went_wrong: str
    how_to_improve: str

# --- 2. Initialize LLM ---
llm = ChatGoogleGenerativeAI(model=MODEL_NAME, api_key=GEMINI_API_KEY)

# --- 3. Main Agent: Determine relevant sub-agents ---
async def main_agent(input_text: str) -> RouterContext:
    system_prompt = (
        "You are a router agent. Analyze the input text and decide which categories are relevant. "
        "Detect if it falls into any category:\n"
        "Filler & Fluency: counts 'um/like,' detects run-ons, WPM.\n"
        "Prosody: pace, pauses, volume variance.\n"
        "Pragmatics: did you answer the question? did you ramble?\n"
        "Empathy/Politeness: hedging, acknowledgment, interruptions.\n"
        "Turn-Taking (if 2+ speakers): interruption ratio, speaking share.\n\n"
        "Return JSON with 'subagents_to_call', each with 'category' and 'text_to_analyze'. "
        "Include only categories relevant to the input text."
    )
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=input_text)]

    response = await llm.ainvoke(messages)
    try:
        data = json.loads(response.content)
        return RouterContext(**data)
    except Exception as e:
        print("Error parsing main agent output:", e)
        return RouterContext(subagents_to_call=[])

# --- 4. Sub-Agent: Evaluate a category ---
async def run_sub_agent(task: SubAgentTask) -> SubAgentReport:
    prompt = (
        f"You are a specialized '{task.category}' sub-agent. "
        "Analyze the text and provide a structured JSON feedback with fields: "
        "score (0-1), what_went_right, what_went_wrong, how_to_improve."
    )
    messages = [SystemMessage(content=prompt), HumanMessage(content=task.text_to_analyze)]

    response = await llm.ainvoke(messages)
    try:
        data = json.loads(response.content)
        return SubAgentReport(**data)
    except Exception as e:
        # Fallback if LLM fails or returns invalid JSON
        return SubAgentReport(
            category=task.category,
            score=0.0,
            what_went_right="",
            what_went_wrong=f"Failed to process: {e}",
            how_to_improve="Retry or adjust input/prompt."
        )

# --- 5. Final Synthesizer: Aggregate sub-agent reports ---
async def final_synthesizer(input_text: str, reports: List[SubAgentReport]) -> str:
    reports_json = json.dumps([r.dict() for r in reports], indent=2)
    system_prompt = (
        "You are the final synthesizer agent. Take the original input and all structured "
        "sub-agent reports, then produce a cohesive, comprehensive answer. Highlight key insights."
    )
    messages = [SystemMessage(content=system_prompt),
                HumanMessage(content=f"Input:\n{input_text}\n\nSub-agent reports:\n{reports_json}")]
    response = await llm.ainvoke(messages)
    return response.content

# --- 6. Workflow ---
async def run_workflow(input_text: str):
    router_context = await main_agent(input_text)
    sub_agent_tasks = [run_sub_agent(task) for task in router_context.subagents_to_call]
    reports = await asyncio.gather(*sub_agent_tasks)
    final_answer = await final_synthesizer(input_text, reports)
    return {
        "sub_agent_reports": [r.dict() for r in reports],
        "final_answer": final_answer
    }

# --- 7. Example Usage ---
async def main():
    input_text = "Analyze the speech for filler words, pacing, empathy, and turn-taking. You suck uhhhhh I am so mean uhhhhh ummmm help me."
    result = await run_workflow(input_text)
    print("--- Sub-Agent Reports ---")
    print(json.dumps(result["sub_agent_reports"], indent=2))
    print("\n--- Final Answer ---")
    print(result["final_answer"])

if __name__ == "__main__":
    asyncio.run(main())
