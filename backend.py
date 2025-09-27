import asyncio
import json
from typing import List, Literal
from pydantic import BaseModel, Field, ValidationError
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

# --- API Config ---
MODEL_NAME = "gemini-2.5-flash-preview-05-20"

# --- Prompts Map ---
from prompts.fluency_agent_prompt import fluency_agent_prompt
from prompts.prosody_agent_prompt import prosody_agent_prompt
from prompts.consideration_agent_prompt import consideration_agent_prompt
from prompts.pragmatics_agent_prompt import pragmatics_agent_prompt
from prompts.turn_taking_agent_prompt import turn_taking_agent_prompt


# Add others when available
prompts = {
    "FLUENCY": fluency_agent_prompt,
    "PROSODY": prosody_agent_prompt,
    "PRAGMATICS": pragmatics_agent_prompt,
    "CONSIDERATION": consideration_agent_prompt,
    "TIME_BALANCE": turn_taking_agent_prompt
}


# --- Pydantic Models ---
class SubAgentTask(BaseModel):
    category: Literal["FLUENCY", "PROSODY", "PRAGMATICS", "CONSIDERATION", "TIME_BALANCE"]
    text_to_analyze: str

class RouterContext(BaseModel):
    subagents_to_call: List[SubAgentTask]

class SubAgentReport(BaseModel):
    category: str
    score: float = Field(ge=0.0, le=1.0)
    rubric_scores: dict = Field(default_factory=dict)  # characteristic: weighted score
    what_went_right: str
    what_went_wrong: str
    how_to_improve: str

# --- Initialize LLM ---
llm = ChatGoogleGenerativeAI(model=MODEL_NAME, api_key=GEMINI_API_KEY)

# --- 1. Router Agent ---
async def main_agent(input_text: str) -> RouterContext:
    system_prompt = (
        "You are a router agent. Determine which sub-agent categories are relevant to the input text. "
        "Categories:\n"
        "Filler & Fluency: counts 'um/like,' detects run-ons, WPM.\n"
        "Prosody: pace, pauses, volume variance.\n"
        "Pragmatics: did you answer the question? did you ramble?\n"
        "Empathy/Politeness: hedging, acknowledgment, interruptions.\n"
        "Turn-Taking (if 2+ speakers): interruption ratio, speaking share.\n\n"
        "Return JSON matching the RouterContext schema: 'subagents_to_call', each with 'category' and 'text_to_analyze'."
    )
    structured_llm = llm.with_structured_output(RouterContext)
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=input_text)]
    try:
        context_object = await structured_llm.ainvoke(messages)
        return context_object
    except ValidationError as e:
        print("Error parsing RouterContext:", e)
        return RouterContext(subagents_to_call=[])

# --- 2. Sub-Agent ---
async def run_sub_agent(task: SubAgentTask) -> SubAgentReport:
    if task.category not in prompts:
        return SubAgentReport(
            category=task.category,
            score=0.0,
            rubric_scores={},
            what_went_right="",
            what_went_wrong="No prompt defined for this category.",
            how_to_improve="Add a prompt for this category."
        )

    prompt_template = prompts[task.category]
    prompt = prompt_template.format(text=task.text_to_analyze)


    # Define rubric weights
    # Weights per sub-agent rubric characteristic
    RUBRIC_WEIGHTS = {
    "FLUENCY": {
        "filler_words": 0.4,
        "run_ons": 0.3,
        "wpm": 0.3
    },
    "PROSODY": {
        "pace": 0.4,
        "pauses": 0.3,
        "volume_variance": 0.3
    },
    "PRAGMATICS": {
        "answered_question": 0.6,
        "rambling": 0.4
    },
    "CONSIDERATION": {
        "hedging": 0.4,
        "acknowledgment": 0.3,
        "interruptions": 0.3
    },
    "TIME_BALANCE": {
        "interruption_ratio": 0.5,
        "speaking_share": 0.5
    }
}

    
    
    weights = rubric_weights.get(task.category, {})

    messages = [SystemMessage(content=prompt), HumanMessage(content=task.text_to_analyze)]
    try:
        response = await llm.ainvoke(messages)
        data = json.loads(response.content)
        # Calculate weighted score
        rubric_scores = {k: float(v) for k, v in data.get("rubric_scores", {}).items()}
        weighted_score = sum(rubric_scores.get(k, 0.0) * w for k, w in weights.items())
        weighted_score = min(max(weighted_score, 0.0), 1.0)

        return SubAgentReport(
            category=task.category,
            score=weighted_score,
            rubric_scores=rubric_scores,
            what_went_right=data.get("what_went_right", ""),
            what_went_wrong=data.get("what_went_wrong", ""),
            how_to_improve=data.get("how_to_improve", "")
        )
    except Exception as e:
        return SubAgentReport(
            category=task.category,
            score=0.0,
            rubric_scores={},
            what_went_right="",
            what_went_wrong=f"Failed to process: {e}",
            how_to_improve="Retry or adjust input/prompt."
        )

# --- 3. Final Synthesizer ---
async def final_synthesizer(input_text: str, reports: List[SubAgentReport]) -> str:
    reports_json = json.dumps([r.dict() for r in reports], indent=2)
    system_prompt = (
        "You are the final synthesizer agent. Combine all sub-agent reports into one comprehensive answer. "
        "Highlight insights from scores and rubric evaluations."
    )
    messages = [SystemMessage(content=system_prompt),
                HumanMessage(content=f"Input:\n{input_text}\n\nSub-agent reports:\n{reports_json}")]
    response = await llm.ainvoke(messages)
    return response.content

# --- 4. Workflow ---
async def run_workflow(input_text: str):
    router_context = await main_agent(input_text)
    sub_agent_tasks = [run_sub_agent(task) for task in router_context.subagents_to_call]
    reports = await asyncio.gather(*sub_agent_tasks)
    final_answer = await final_synthesizer(input_text, reports)
    return {"sub_agent_reports": [r.dict() for r in reports], "final_answer": final_answer}

# --- Example Usage ---
async def main():
    input_text = "Analyze the speech for filler words, pacing, empathy, and turn-taking. You ummm uhh like I am so nervous."
    result = await run_workflow(input_text)
    print("--- Sub-Agent Reports ---")
    print(json.dumps(result["sub_agent_reports"], indent=2))
    print("\n--- Final Answer ---")
    print(result["final_answer"])

if __name__ == "__main__":
    asyncio.run(main())
