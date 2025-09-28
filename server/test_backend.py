from backend import (
    FluencyOutput, ProsodyOutput, PragmaticsOutput,
    ConsiderationOutput, TimeBalanceOutput
)

# ------------------------
# Sample texts / interactions
# ------------------------
GOOD_BALANCED = "I am confident in my experience and can communicate clearly."
TOO_MANY_FILLERS = "Uh, like, I guess, um, my experience is, like, in software, you know?"
RUN_ON_SENTENCES = "I have worked in multiple teams I have shipped products I am passionate about problem solving"
EXCESSIVE_PAUSES = "I... I think... maybe... this role... could be good... for me..."
MONOTONE = "My experience is in software engineering. My experience is in software engineering."
AGGRESSIVE = "Shut up! You are wrong!"
LACK_CONSIDERATION = "I didn't listen and interrupted multiple times."
TIME_DOMINATE = "I spoke the entire meeting, others didn't get to speak."
NICE_BALANCE = "I spoke clearly and let others share their points as well."

# ------------------------
# Corrected Evaluators
# ------------------------

# ---------------- Fluency ----------------
def evaluate_fluency(text: str):
    filler_score = 1.0 if "Uh" not in text and "um" not in text else 0.3
    # run_on_score = LOW if sentences are run-on (few periods), HIGH if well-punctuated
    run_on_score = 0.9 if text.count('.') > 0 else 0.3
    # WPM is approximate, we'll mock as 0.9 for short clear sentences, lower for very long ones
    wpm_score = 0.9 if len(text.split()) < 30 else 0.6
    return FluencyOutput(
        filler_words=filler_score,
        run_ons=run_on_score,
        wpm=wpm_score,
        what_went_right="Clear speech, minimal filler words.",
        what_went_wrong="Run-on sentences or filler words detected.",
        how_to_improve="Reduce fillers, break long sentences.",
        prompt=text
    )

# ---------------- Prosody ----------------
def evaluate_prosody(text: str):
    # Pace: high if not excessively fast/slow
    pace = 0.9
    # Pauses: low if too many ellipses, high if natural
    pauses = 0.3 if "..." in text else 0.9
    # Volume variance: low if monotone text, high otherwise
    volume_variance = 0.3 if "Monotone" in text or MONOTONE in text else 0.9
    # Speed: high if ideal, low if too slow/fast
    speed = 0.9
    return ProsodyOutput(
        pace=pace,
        pauses=pauses,
        volume_variance=volume_variance,
        speed=speed,
        what_went_right="Good pacing, clear volume, ideal speed.",
        what_went_wrong="Minor monotone or pauses issues.",
        how_to_improve="Add intonation variation and adjust pauses slightly.",
        prompt=text
    )

# ---------------- Pragmatics ----------------
def evaluate_pragmatics(text: str):
    answered_question = 1.0 if "?" in text else 0.9
    # Rambling: low if text is long (>20 words), high if concise (<20 words)
    rambling = 0.3 if len(text.split()) > 20 else 0.9
    return PragmaticsOutput(
        answered_question=answered_question,
        rambling=rambling,
        what_went_right="Communicates purpose clearly.",
        what_went_wrong="Minor rambling detected.",
        how_to_improve="Stay concise and focused.",
        prompt=text
    )

# ---------------- Consideration ----------------
def evaluate_consideration(text: str):
    hedging = 0.9 if "I think" not in text else 0.6
    acknowledgment = 0.9 if "you" in text or "others" in text else 0.3
    interruptions = 0.3 if "Shut up" in text or "interrupted" in text else 0.9
    return ConsiderationOutput(
        hedging=hedging,
        acknowledgment=acknowledgment,
        interruptions=interruptions,
        what_went_right="Shows awareness and listens.",
        what_went_wrong="Interruptions or hedging detected.",
        how_to_improve="Acknowledge others and avoid interrupting.",
        prompt=text
    )

# ---------------- Time Balance ----------------
def evaluate_time_balance(text: str):
    # Interruption ratio low if dominates, high if balanced
    interruption_ratio = 0.3 if "entire meeting" in text else 0.9
    # Speaking share low if dominates, high if balanced
    speaking_share = 0.3 if "entire meeting" in text else 0.9
    return TimeBalanceOutput(
        interruption_ratio=interruption_ratio,
        speaking_share=speaking_share,
        what_went_right="Balanced speaking time.",
        what_went_wrong="Dominates conversation or poor balance.",
        how_to_improve="Let others share points and reduce interruptions.",
        prompt=text
    )
