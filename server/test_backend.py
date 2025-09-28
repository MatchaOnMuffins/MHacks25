from pydantic import BaseModel
from typing import Any, Dict
import re

# ---------------------------
# Data Models
# ---------------------------

class FluencyOutput(BaseModel):
    lack_of_filler_words: float
    lack_of_run_ons: float
    words_per_minute: float
    raw_filler_words: str
    raw_run_ons: str
    raw_wpm: str
    prompt: str

class ProsodyOutput(BaseModel):
    good_pace: float
    speed: float
    pauses: float
    volume_variance: float
    raw_speed: str
    raw_pace: str
    raw_pauses: str
    raw_volume_variance: str
    prompt: str

class PragmaticsOutput(BaseModel):
    yes_answered_question: float
    rambling: float
    raw_answered_question: str
    raw_rambling: str
    prompt: str

class TimeBalanceOutput(BaseModel):
    good_interruption_ratio: float
    speaking_share: float
    raw_interruption_ratio: str
    raw_speaking_share: str
    prompt: str

# ---------------------------
# Helper Functions
# ---------------------------

# Fluency helpers
def compute_filler_score(text: str) -> tuple[float, str]:
    fillers = re.findall(r"\b(um|uh|like|you know|so)\b", text, re.I)
    score = max(0, 1 - len(fillers)/10)  # arbitrary scoring
    return score, ', '.join(fillers) if fillers else "None"

def compute_runon_score(text: str) -> tuple[float, str]:
    sentences = re.split(r'[.!?]', text)
    runons = [s for s in sentences if len(s.split()) > 30]
    score = max(0, 1 - len(runons)/5)
    return score, ' | '.join(runons) if runons else "None"

def compute_wpm(text: str) -> tuple[float, str]:
    words = len(text.split())
    # Let's assume duration is 1 minute for simplicity
    score = words / 150  # normalized to 1 if 150 wpm
    return score, f"{words} words"

# Prosody helpers
def compute_speed(text: str) -> tuple[float, str]:
    words = len(text.split())
    speed = min(1.0, words / 200)
    return speed, f"{words} words/min"

def compute_pauses(text: str) -> tuple[float, str]:
    pauses = len(re.findall(r'[.,;!?]', text))
    score = max(0, 1 - pauses/20)
    return score, f"{pauses} pauses"

def compute_volume_variance(text: str) -> tuple[float, str]:
    # Dummy metric: more punctuation = more variation
    variance = min(1.0, len(re.findall(r'[.!?]', text)) / 10)
    return variance, f"{variance*100:.1f}%"

def compute_good_pace(text: str) -> tuple[float, str]:
    words = len(text.split())
    pace = max(0, 1 - abs(words - 150)/150)
    return pace, f"{words} words considered ideal 150"

# Pragmatics helpers
def check_answered_question(text: str) -> tuple[float, str]:
    answered = 1.0 if '?' not in text else 0.5
    return answered, "Answered question" if answered == 1.0 else "Unclear"

def check_rambling(text: str) -> tuple[float, str]:
    sentences = text.split('.')
    rambling_score = max(0, 1 - len(sentences)/10)
    raw_rambling = ' | '.join(sentences) if sentences else "None"
    return rambling_score, raw_rambling

# Time balance helpers
def compute_interruption_ratio(text: str) -> tuple[float, str]:
    # Dummy logic
    ratio = 0.8 if "interrupt" not in text else 0.2
    return ratio, f"Raw ratio {'0.8' if ratio==0.8 else '0.2'}"

def compute_speaking_share(text: str) -> tuple[float, str]:
    words = len(text.split())
    share = min(1.0, words / 200)
    return share, f"{words} words share"

# ---------------------------
# Evaluators
# ---------------------------

def evaluate_fluency(text: str) -> FluencyOutput:
    filler_score, filler_text = compute_filler_score(text)
    runon_score, runon_text = compute_runon_score(text)
    wpm_score, wpm_text = compute_wpm(text)
    
    return FluencyOutput(
        lack_of_filler_words=filler_score,
        lack_of_run_ons=runon_score,
        words_per_minute=wpm_score,
        raw_filler_words=filler_text,
        raw_run_ons=runon_text,
        raw_wpm=wpm_text,
        prompt=text
    )

def evaluate_prosody(text: str) -> ProsodyOutput:
    speed, speed_text = compute_speed(text)
    pauses, pauses_text = compute_pauses(text)
    volume_variance, volume_text = compute_volume_variance(text)
    good_pace, pace_text = compute_good_pace(text)
    
    return ProsodyOutput(
        good_pace=good_pace,
        speed=speed,
        pauses=pauses,
        volume_variance=volume_variance,
        raw_speed=speed_text,
        raw_pace=pace_text,
        raw_pauses=pauses_text,
        raw_volume_variance=volume_text,
        prompt=text
    )

def evaluate_pragmatics(text: str) -> PragmaticsOutput:
    answered_question, answered_text = check_answered_question(text)
    rambling, rambling_text = check_rambling(text)
    
    return PragmaticsOutput(
        yes_answered_question=answered_question,
        rambling=rambling,
        raw_answered_question=answered_text,
        raw_rambling=rambling_text,
        prompt=text
    )

def evaluate_time_balance(text: str) -> TimeBalanceOutput:
    interruption_ratio, interruption_text = compute_interruption_ratio(text)
    speaking_share, share_text = compute_speaking_share(text)
    
    return TimeBalanceOutput(
        good_interruption_ratio=interruption_ratio,
        speaking_share=speaking_share,
        raw_interruption_ratio=interruption_text,
        raw_speaking_share=share_text,
        prompt=text
    )

# ---------------------------
# Example Usage / Test
# ---------------------------
if __name__ == "__main__":
    sample_text = "Um, I think, you know, this is a sample text. It has several sentences to test the system."
    
    print(evaluate_fluency(sample_text))
    print(evaluate_prosody(sample_text))
    print(evaluate_pragmatics(sample_text))
    print(evaluate_time_balance(sample_text))
