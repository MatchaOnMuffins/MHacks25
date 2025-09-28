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
MODEL_NAME = "gemini-2.5-flash-lite"
llm = ChatGoogleGenerativeAI(model=MODEL_NAME, api_key=api_key)

MODEL_NAME_ROUTER = "gemini-2.5-flash"
llm_high = ChatGoogleGenerativeAI(model=MODEL_NAME_ROUTER, api_key=api_key)

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
    total_score: float

def ideal_score(value: float, ideal_min: float, ideal_max: float) -> float:
    """
    Normalize so that values inside [ideal_min, ideal_max] = 1.0,
    and fall off toward 0.0 the further they are outside that range.
    """
    if ideal_min <= value <= ideal_max:
        return 1.0
    # compute distance from nearest bound
    if value < ideal_min:
        diff = ideal_min - value
    else:
        diff = value - ideal_max
    # decay: every 0.3 away drops ~1 point
    return max(0.0, 1.0 - diff / 0.3)

# Fluency
"""class FluencyOutput(BaseModel):
    no_filler_words: float = Field(..., ge=0.0, le=1.0, description="Fraction of filler words relative to total words (lower is better)")
    no_run_ons: float = Field(..., ge=0.0, le=1.0, description="Fraction of run-on sentences (lower is better)")
    wpm: float = Field(..., ge=0.0, le=1.0, description="Relative speech pace: 0 = too slow, 1 = too fast")

    what_went_right: str
    what_went_wrong: str
    how_to_improve: str
    prompt: str

    @property
    def rubric_scores(self) -> Dict[str, float]:
        return {
            "filler_words": 1.0 - self.filler_words,
            "run_ons": 1.0 - self.run_ons,
            "wpm": ideal_score(self.raw_wpm, ideal_min=0.4, ideal_max=0.6),
        }

# Prosody
class ProsodyOutput(BaseModel):
    pace: float = Field(..., ge=0.0, le=1.0, description="0 = very slow, 1 = excessively fast")
    pauses: float = Field(..., ge=0.0, le=1.0, description="0 = pauses excessively, 1 = no pausing at all")
    volume_variance: float = Field(..., ge=0.0, le=1.0, description="0 = monotone/disruptive, 1 = ideal variation")
    speed: float
    what_went_right: str
    what_went_wrong: str
    how_to_improve: str
    prompt: str

    @property
    def rubric_scores(self) -> Dict[str, float]:
        return {
            "pace": ideal_score(self.raw_pace, ideal_min=0.4, ideal_max=0.6),
            "pauses": ideal_score(self.raw_pauses, ideal_min=0.4, ideal_max=0.6),
            "volume_variance": self.volume_variance,
            "speed": float
        }


# Pragmatics
class PragmaticsOutput(BaseModel):
    answered_question: float = Field(..., ge=0.0, le=1.0, description="0 = didn’t answer at all, 1 = fully answered")
    rambling: float = Field(..., ge=0.0, le=1.0, description="0 = rambled constantly, 1 = no rambling")

    what_went_right: str
    what_went_wrong: str
    how_to_improve: str
    prompt: str

    @property
    def rubric_scores(self) -> Dict[str, float]:
        return {
            "answered_question": self.answered_question,  # already ideal=1
            "rambling": self.rambling,                  # already ideal=1
        }


# Consideration
class ConsiderationOutput(BaseModel):
    hedging: float = Field(..., ge=0.0, le=1.0, description="0 = hedging all the time, 1 = no hedging")
    acknowledgment: float = Field(..., ge=0.0, le=1.0, description="0 = no acknowledgment, 1 = frequent acknowledgment")
    interruptions: float = Field(..., ge=0.0, le=1.0, description="Fraction of interruptions (lower is better)")

    what_went_right: str
    what_went_wrong: str
    how_to_improve: str
    prompt: str

    @property
    def rubric_scores(self) -> Dict[str, float]:
        return {
            "hedging": self.hedging,
            "acknowledgment": self.acknowledgment,
            "interruptions": 1.0 - self.interruptions,  # fewer interruptions = closer to 1
        }


# Time Balance
class TimeBalanceOutput(BaseModel):
    interruption_ratio: float = Field(..., ge=0.0, le=1.0, description="0 = always interrupts, 1 = never interrupts")
    speaking_share: float = Field(..., ge=0.0, le=1.0, description="0 = hogs all talk time, 1 = never speaks")

    what_went_right: str
    what_went_wrong: str
    how_to_improve: str
    prompt: str

    @property
    def rubric_scores(self) -> Dict[str, float]:
        return {
            "interruption_ratio": self.raw_interruption_ratio,  # already 1 = ideal
            "speaking_share": ideal_score(self.raw_speaking_share, ideal_min=0.4, ideal_max=0.6),
        }
        
        """

from pydantic import BaseModel, Field
from typing import Dict

# ---------------------------
# Fluency
# ---------------------------
class FluencyOutput(BaseModel):
    raw_filler_words: float = Field(
        ..., ge=0.0, le=1.0,
        description="Fraction of filler words relative to total words (0 = none, 1 = extreme; lower is better)"
    )
    raw_run_ons: float = Field(
        ..., ge=0.0, le=1.0,
        description="Fraction of run-on sentences (0 = none, 1 = extreme; lower is better)"
    )
    raw_wpm: float = Field(
        ..., ge=0.0, le=1.0,
        description="Relative words-per-minute deviation (0 = ideal, 1 = too fast/slow; lower is better)"
    )

    what_went_right: str
    what_went_wrong: str
    how_to_improve: str
    prompt: str

    @property
    def filler_words(self) -> float:
        """Higher = better (less filler words)"""
        return 1.0 - self.raw_filler_words

    @property
    def run_ons(self) -> float:
        """Higher = better (fewer run-ons)"""
        return 1.0 - self.raw_run_ons

    @property
    def wpm(self) -> float:
        """Higher = better (closer to ideal pace)"""
        return 1.0 - self.raw_wpm

    @property
    def rubric_scores(self) -> Dict[str, float]:
        return {
            "lack_of_filler_words": self.filler_words,
            "lack_of_run_ons": self.run_ons,
            "good_wpm": self.wpm
        }

# ---------------------------
# Prosody
# ---------------------------
class ProsodyOutput(BaseModel):
    raw_pace: float = Field(..., ge=0.0, le=1.0,
                            description="Speech pace deviation (0 = ideal, 1 = too fast/slow; lower is better)")
    raw_pauses: float = Field(..., ge=0.0, le=1.0,
                              description="Excessive pauses (0 = ideal, 1 = pauses too much; lower is better)")
    raw_volume_variance: float = Field(..., ge=0.0, le=1.0,
                                       description="Volume variation (0 = monotone, 1 = ideal variance; higher is better)")
    raw_speed: float = Field(..., ge=0.0, le=1.0,
                             description="Speech speed deviation (0 = ideal, 1 = too fast/slow; lower is better)")

    what_went_right: str
    what_went_wrong: str
    how_to_improve: str
    prompt: str

    @property
    def pace(self) -> float:
        """Higher = better (closer to ideal pace)"""
        return 1.0 - self.raw_pace

    @property
    def pauses(self) -> float:
        """Higher = better (fewer excessive pauses)"""
        return 1.0 - self.raw_pauses

    @property
    def volume_variance(self) -> float:
        """Higher = better (more ideal volume variation)"""
        return 1.0 - self.raw_volume_variance

    @property
    def speed(self) -> float:
        """Higher = better (closer to ideal speed)"""
        return 1.0 - self.raw_speed

    @property
    def rubric_scores(self) -> Dict[str, float]:
        return {
            "good_pace": self.speed,
            "lack_of_pauses": self.pauses,
            "good_volume_variance": self.volume_variance
        }

# ---------------------------
# Pragmatics
# ---------------------------
class PragmaticsOutput(BaseModel):
    raw_answered_question: float = Field(..., ge=0.0, le=1.0,
                                         description="How fully the question was answered (0 = not at all, 1 = fully answered; higher is better)")
    raw_rambling: float = Field(..., ge=0.0, le=1.0,
                                description="Amount of rambling (0 = rambled constantly, 1 = concise; higher is better)")

    what_went_right: str
    what_went_wrong: str
    how_to_improve: str
    prompt: str

    @property
    def answered_question(self) -> float:
        return self.raw_answered_question  # Higher = better

    @property
    def rambling(self) -> float:
        """Higher = better (less rambling)"""
        return 1.0 - self.raw_rambling

    @property
    def rubric_scores(self) -> Dict[str, float]:
        return {
            "yes_answered_question": self.answered_question,
            "no_rambling": self.rambling
        }

# ---------------------------
# Consideration
# ---------------------------
class ConsiderationOutput(BaseModel):
    raw_hedging: float = Field(..., ge=0.0, le=1.0,
                               description="Amount of hedging (0 = none, 1 = excessive; lower is better)")
    raw_acknowledgment: float = Field(..., ge=0.0, le=1.0,
                                      description="Frequency of acknowledgment (0 = none, 1 = frequent; higher is better)")
    raw_interruptions: float = Field(..., ge=0.0, le=1.0,
                                     description="Fraction of interruptions (0 = never interrupts, 1 = frequent; lower is better)")

    what_went_right: str
    what_went_wrong: str
    how_to_improve: str
    prompt: str

    @property
    def hedging(self) -> float:
        """Higher = better (less hedging)"""
        return 1.0 - self.raw_hedging

    @property
    def acknowledgment(self) -> float:
        """Higher = better (more acknowledgment)"""
        return self.raw_acknowledgment

    @property
    def interruptions(self) -> float:
        """Higher = better (fewer interruptions)"""
        return 1.0 - self.raw_interruptions

    @property
    def rubric_scores(self) -> Dict[str, float]:
        return {
            "no_hedging": self.hedging,
            "good_amount_of_acknowledgment": self.acknowledgment,
            "no_interruptions": self.interruptions
        }

# ---------------------------
# Time Balance
# ---------------------------
class TimeBalanceOutput(BaseModel):
    raw_interruption_ratio: float = Field(..., ge=0.0, le=1.0,
                                          description="Frequency of interrupting others (0 = never interrupts, 1 = frequent; lower is better)")
    raw_speaking_share: float = Field(..., ge=0.0, le=1.0,
                                      description="Fraction of speaking time (0 = ideal, 1 = dominates; lower is better)")

    what_went_right: str
    what_went_wrong: str
    how_to_improve: str
    prompt: str

    @property
    def interruption_ratio(self) -> float:
        """Higher = better (less interrupting)"""
        return 1.0 - self.raw_interruption_ratio

    @property
    def speaking_share(self) -> float:
        """Higher = better (balanced speaking share)"""
        return 1.0 - self.raw_speaking_share

    @property
    def rubric_scores(self) -> Dict[str, float]:
        return {
            "good_interruption_ratio": self.interruption_ratio,
            "good_speaking_share": self.speaking_share
        }


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
    "FLUENCY": {"lack_of_filler_words":0.4, "lack_of_run_ons":0.3, "good_wpm":0.3},
    "PROSODY": {"god_pace":0.5, "lack_of_pauses":0.3, "good_volume_variance":0.2},
    "PRAGMATICS": {"yes_answered_question":0.6, "no_rambling":0.4},
    "CONSIDERATION": {"no_hedging":0.4, "good_amount_of_acknowledgment":0.3, "no_interruptions":0.3},
    "TIME_BALANCE": {"good_interruption_ratio":0.5, "good_speaking_share":0.5}
}

#total number of words / 5 


def router_agent_prompt(input_text: str):
    return f"""
You are a router agent. Your task is to generate a workflow that calls all five categories of analysis, prioritizing them based on their prevalence in the input. For example, if the input text contains many filler words like um or uh, give FLUENCY the highest priority but still include the other categories in the workflow.

Categories and definitions:
	•	FLUENCY: counts “um/like,” detects run-ons, words per minute (WPM).
	•	PROSODY: pace, pauses, volume variance.
	•	PRAGMATICS: checks if the question was answered, or if the response rambled.
	•	CONSIDERATION: hedging, acknowledgment, interruptions.
	•	TIME_BALANCE: interruption ratio, speaking share.

Output requirements:
	•	Return JSON matching the RouterContext schema.
	•	The JSON must include a field subagents_to_call, which is a list of objects.
	•	Each object should have:
	•	"category": one of the five categories above.
	•	"text_to_analyze": the relevant portion of the input text.

Rules:
	•	If you cannot provide any meaningful analysis, return an empty list.
	•	Only return categories if they apply.
	•	Always rank categories by prevalence in the input.
    •	Be as concise as possible. Be specific and to the point.
    •	If the input text only contains something like "transcribing...", return an empty list.

Input text:

{input_text}
"""

# --- 1. Router Agent ---
async def main_agent(input_text: str) -> RouterContext:
    system_prompt = (
        "You are a router agent. Genenerate a workflow calling all of the 5 categories, where each category is given priority based on what you see as the most prevalance. For example, if I see a lot of ums and uhs, I would give priority to FLUENCY first in the workflow but I would also add the other agents to my workflow. \n"
        "Categories:\n"
        "FLUENCY, PROSODY, PRAGMATICS, CONSIDERATION, TIME_BALANCE\n\n"
        "Each of the categories encompasses this: FLUENCY: counts um/like, detects run-ons, WPM. PROSODY: pace, pauses, volume variance. PRAGMATICS: did you answer the question? did you ramble? CONSIDERATION: hedging, acknowledgment, interruptions. TIME_BALANCE: interruption ratio, speaking share."
        "Return JSON matching the RouterContext schema with 'subagents_to_call', each having 'category' and 'text_to_analyze'."
    )

    human_prompt = router_agent_prompt(input_text)

    structured_llm = llm.with_structured_output(RouterContext)
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)]

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


def final_synthesizer_prompt(input_text: str, reports: List[SubAgentReport]) -> str:
    return f"""
You are the final synthesizer agent. Combine all sub-agent reports into one coherent summary highlighting insights.

Input text: {input_text}
Sub-agent reports: {reports}

If the sub-agent reports are empty, return "No analysis", and only no analysis, and return 0.0 for the total score.

if the input text only contains something like "transcribing...", or is extremely short, 
return "No analysis", and only no analysis, and return 0.0 for the total score.

otherwise, return the total score, and perform a brief analysis of the input text and the sub-agent reports.
"""

# --- 3. Final Synthesizer ---
async def final_synthesizer(input_text: str, reports: List[SubAgentReport]) -> SynthesizerOutput:
    # Prepare JSON for LLM context
    reports_json = json.dumps([r.dict() for r in reports], indent=2)
    # System prompt only for summarization
    system_prompt = (
        "You are the final synthesizer agent. Combine all sub-agent reports into one coherent summary highlighting insights."
    )
    structured_llm = llm.with_structured_output(SynthesizerOutput)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=final_synthesizer_prompt(input_text, reports))
    ]
    try:
        # Let Gemini create the summary ONLY
        output: SynthesizerOutput = await structured_llm.ainvoke(messages)
        # Compute average score locally
        if reports:
            total_score = sum(r.score for r in reports) / len(reports)
        else:
            total_score = 0.0
        # Assign the local total_score
        output.total_score = round(total_score,2)
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
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
