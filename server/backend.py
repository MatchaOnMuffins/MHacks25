import asyncio
import json
from typing import List, Literal, Dict
from pydantic import BaseModel, Field, ValidationError
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

from typing import Literal, Dict


# --- Load API key ---
load_dotenv(".env")
api_key = os.getenv("GEMINI_API_KEY")

# --- LLM Config ---
MODEL_NAME = "gemini-2.5-flash-preview-05-20"
llm = ChatGoogleGenerativeAI(model=MODEL_NAME, api_key=api_key)

# --- Prompts (functions that accept `text`) ---
from prompts.fluency_agent_prompt import fluency_agent_prompt
from prompts.prosody_agent_prompt import prosody_agent_prompt
from prompts.consideration_agent_prompt import consideration_agent_prompt
from prompts.pragmatics_agent_prompt import pragmatics_agent_prompt
from prompts.turn_taking_agent_prompt import turn_taking_agent_prompt

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

class SubAgentOutput(BaseModel):
    category: str
    rubric_scores: Dict[str, float] = Field(..., description="Individual characteristic scores for each rubric item (0-1)")
    what_went_right: str = Field(..., description="Positive aspects identified")
    what_went_wrong: str = Field(..., description="Negative aspects identified")
    how_to_improve: str = Field(..., description="Improvement guidance")
    prompt: str = Field(..., description="Prompt used for this sub-agent")

class SubAgentReport(BaseModel):
    category: str
    score: float
    rubric_scores: Dict[str, float]
    what_went_right: str
    what_went_wrong: str
    how_to_improve: str

class SynthesizerOutput(BaseModel):
    summary: str
    total_score: int

class FluencyOutput(BaseModel):
    filler_words: float = Field(..., ge=0.0, le=1.0, description="Magnitude of filler words like 'um', 'uh', 'like'")
    run_ons: float = Field(..., ge=0.0, le=1.0, description="Magnitude of run-on sentences or lack of clarity")
    wpm: float = Field(..., ge=0.0, le=1.0, description="Relative speech pace (too fast = closer to 1.0)")
    
    what_went_right: str = Field(..., description="Positive aspects of fluency")
    what_went_wrong: str = Field(..., description="Fluency issues detected")
    how_to_improve: str = Field(..., description="Guidance for improving fluency")
    
    prompt: str = Field(..., description="Prompt given to the model for context")

    @property
    def rubric_scores(self) -> Dict[str, float]:
        return {"filler_words": self.filler_words, "run_ons": self.run_ons, "wpm": self.wpm}


class ProsodyOutput(BaseModel):
    #category: Literal["PROSODY"]
    pace: float = Field(..., ge=0.0, le=1.0)
    pauses: float = Field(..., ge=0.0, le=1.0)
    volume_variance: float = Field(..., ge=0.0, le=1.0)
    what_went_right: str
    what_went_wrong: str
    how_to_improve: str
    prompt: str

    @property
    def rubric_scores(self) -> Dict[str, float]:
        return {"pace": self.pace, "pauses": self.pauses, "volume_variance": self.volume_variance}


class PragmaticsOutput(BaseModel):
    #category: Literal["PRAGMATICS"]
    answered_question: float = Field(..., ge=0.0, le=1.0)
    rambling: float = Field(..., ge=0.0, le=1.0)
    what_went_right: str
    what_went_wrong: str
    how_to_improve: str
    prompt: str

    @property
    def rubric_scores(self) -> Dict[str, float]:
        return {"answered_question": self.answered_question, "rambling": self.rambling}


class ConsiderationOutput(BaseModel):
    #category: Literal["CONSIDERATION"]
    hedging: float = Field(..., ge=0.0, le=1.0)
    acknowledgment: float = Field(..., ge=0.0, le=1.0)
    interruptions: float = Field(..., ge=0.0, le=1.0)
    what_went_right: str
    what_went_wrong: str
    how_to_improve: str
    prompt: str

    @property
    def rubric_scores(self) -> Dict[str, float]:
        return {"hedging": self.hedging, "acknowledgment": self.acknowledgment, "interruptions": self.interruptions}


class TimeBalanceOutput(BaseModel):
    #category: Literal["TIME_BALANCE"]
    interruption_ratio: float = Field(..., ge=0.0, le=1.0)
    speaking_share: float = Field(..., ge=0.0, le=1.0)
    what_went_right: str
    what_went_wrong: str
    how_to_improve: str
    prompt: str

    @property
    def rubric_scores(self) -> Dict[str, float]:
        return {"interruption_ratio": self.interruption_ratio, "speaking_share": self.speaking_share}


# --- Map categories to models ---
CATEGORY_MODELS = {
    "FLUENCY": FluencyOutput,
    "PROSODY": ProsodyOutput,
    "PRAGMATICS": PragmaticsOutput,
    "CONSIDERATION": ConsiderationOutput,
    "TIME_BALANCE": TimeBalanceOutput,
}


# --- Rubric Weights ---
RUBRIC_WEIGHTS = {
    "FLUENCY": {"filler_words":0.4, "run_ons":0.3, "wpm":0.3},
    "PROSODY": {"pace":0.4, "pauses":0.3, "volume_variance":0.3},
    "PRAGMATICS": {"answered_question":0.6, "rambling":0.4},
    "CONSIDERATION": {"hedging":0.4, "acknowledgment":0.3, "interruptions":0.3},
    "TIME_BALANCE": {"interruption_ratio":0.5, "speaking_share":0.5}
}

# --- 1. Router Agent ---
async def main_agent(input_text: str) -> RouterContext:
    system_prompt = (
        "You are a router agent. Determine which sub-agent categories are relevant for the input text.\n"
        "Categories:\n"
        "FLUENCY, PROSODY, PRAGMATICS, CONSIDERATION, TIME_BALANCE\n\n"
        "Each of the categories encompasses this: Detect if it fall into any category: FLUENCY: counts um/like, detects run-ons, WPM. PROSODY: pace, pauses, volume variance. PRAGMATICS: did you answer the question? did you ramble? CONSIDERATION: hedging, acknowledgment, interruptions. TIME_BALANCE: interruption ratio, speaking share."
        "Return JSON matching the RouterContext schema with 'subagents_to_call', each having 'category' and 'text_to_analyze'."
    )

    structured_llm = llm.with_structured_output(RouterContext)
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=input_text)]

    try:
        router_context: RouterContext = await structured_llm.ainvoke(messages)
        # Ensure each sub-agent gets the text
        for task in router_context.subagents_to_call:
            task.text_to_analyze = input_text
        return router_context
    except ValidationError as e:
        print("RouterContext parsing error:", e)
        return RouterContext(subagents_to_call=[])

# --- 2. Sub-Agent Runner ---
async def run_sub_agent(task: SubAgentTask) -> SubAgentReport:
    if task.category not in prompts or task.category not in CATEGORY_MODELS:
        return SubAgentReport(
            category=task.category,
            rubric_scores={},
            score=0.0,
            what_went_right="",
            what_went_wrong="No prompt/model defined",
            how_to_improve="Add a prompt and schema for this category"
        )

    prompt_text = prompts[task.category](task.text_to_analyze)

    model = CATEGORY_MODELS[task.category]
    structured_llm = llm.with_structured_output(model)

    try:
        output = await structured_llm.ainvoke([
            SystemMessage(content=prompt_text),
            HumanMessage(content=task.text_to_analyze)
        ])

        # calculate weighted score
        weights = RUBRIC_WEIGHTS.get(task.category, {})
        weighted_score = sum(output.rubric_scores.get(k, 0.0) * w for k, w in weights.items())
        weighted_score = min(max(weighted_score, 0.0), 1.0)

        return SubAgentReport(
            category=task.category,  # 👈 force category from router, not Gemini
            rubric_scores=output.rubric_scores,
            score=weighted_score,
            what_went_right=output.what_went_right,
            what_went_wrong=output.what_went_wrong,
            how_to_improve=output.how_to_improve
        )

    except Exception as e:
        return SubAgentReport(
            category=task.category,
            rubric_scores={},
            score=0.0,
            what_went_right="",
            what_went_wrong=f"Failed: {e}",
            how_to_improve="Retry or adjust prompt/input"
        )

# --- 3. Final Synthesizer ---
async def final_synthesizer(input_text: str, reports: List[SubAgentReport]) -> SynthesizerOutput:
    reports_json = json.dumps([r.dict() for r in reports], indent=2)
    system_prompt = "You are the final synthesizer agent. Combine all sub-agent reports into one coherent summary highlighting insights. Also give the average of all the scores."

    structured_llm = llm.with_structured_output(SynthesizerOutput)
    messages = [SystemMessage(content=system_prompt),
                HumanMessage(content=f"Input:\n{input_text}\n\nSub-agent reports:\n{reports_json}")]

    try:
        output: SynthesizerOutput = await structured_llm.ainvoke(messages)
        return output
    except ValidationError as e:
        print("Synthesizer parsing error:", e)
        return SynthesizerOutput(summary="Failed to synthesize final answer.", total_score=0.0)

# --- 4. Workflow ---
async def run_workflow(input_text: str):
    router_context = await main_agent(input_text)
    sub_agent_tasks = [run_sub_agent(task) for task in router_context.subagents_to_call]
    reports = await asyncio.gather(*sub_agent_tasks)
    final_summary = await final_synthesizer(input_text, reports)
    return {
        "sub_agent_reports": [r.dict() for r in reports],
        "final_answer": final_summary.summary,
        "total_score": final_summary.total_score
    }

# --- 5. EX Usage ---
async def main():
    #input_text = "ummm I like I am so nervous, I will interrupt you. Other person: I like to eat, Me: Shut up!"
    input_text = "“Hey, um, do you have any plans for the weekend? Not really, I was thinking maybe we could, like, go hiking or something. Hmm, I don’t know, I’ve been super busy. Maybe we could just, um, watch a movie instead? Yeah, that sounds good! We could, like, order pizza too. Perfect! Should we invite anyone else, or just us? Just us, I think. It’ll be more chill that way. Alright, cool. I’ll bring the snacks!”"
    result = await run_workflow(input_text)
    print("--- Sub-Agent Reports ---")
    print(json.dumps(result["sub_agent_reports"], indent=2)) #JSON of all the sub agents reports 
    print("\n--- Final Answer ---") 
    print(result["final_answer"]) #inCludes the summary

if __name__ == "__main__":
    asyncio.run(main())
