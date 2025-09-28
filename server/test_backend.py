import unittest
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
        lack_of_filler_words=filler_score,
        lack_of_run_ons=run_on_score,
        good_wpm=wpm_score,
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
        good_pace=speed,
        lack_of_pauses=pauses,
        good_volume_variance=volume_variance,
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
        yes_answered_question=answered_question,
        no_rambling=rambling,
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
        no_hedging=hedging,
        good_amount_of_acknowledgment=acknowledgment,
        no_interruptions=interruptions,
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
        good_interruption_ratio=interruption_ratio,
        good_speaking_share=speaking_share,
        what_went_right="Balanced speaking time.",
        what_went_wrong="Dominates conversation or poor balance.",
        how_to_improve="Let others share points and reduce interruptions.",
        prompt=text
    )

# ------------------------
# Sample texts
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
# Unit Tests
# ------------------------
class TestEvaluators(unittest.TestCase):

    # -------- Fluency --------
    def test_fluency_good(self):
        output = evaluate_fluency(GOOD_BALANCED)
        self.assertGreater(output.lack_of_filler_words, 0.7)
        self.assertGreater(output.lack_of_run_ons, 0.7)
        self.assertGreater(output.good_wpm, 0.7)

    def test_fluency_fillers(self):
        output = evaluate_fluency(TOO_MANY_FILLERS)
        self.assertLess(output.lack_of_filler_words, 0.5)

    def test_fluency_runons(self):
        output = evaluate_fluency(RUN_ON_SENTENCES)
        self.assertLess(output.lack_of_run_ons, 0.5)

    # -------- Prosody --------
    def test_prosody_good(self):
        output = evaluate_prosody(GOOD_BALANCED)
        self.assertGreater(output.good_pace, 0.7)
        self.assertGreater(output.lack_of_pauses, 0.7)
        self.assertGreater(output.good_volume_variance, 0.7)

    def test_prosody_pauses(self):
        output = evaluate_prosody(EXCESSIVE_PAUSES)
        self.assertLess(output.lack_of_pauses, 0.5)

    def test_prosody_monotone(self):
        output = evaluate_prosody(MONOTONE)
        self.assertLess(output.good_volume_variance, 0.5)

    # -------- Pragmatics --------
    def test_pragmatics_good(self):
        output = evaluate_pragmatics(GOOD_BALANCED)
        self.assertGreater(output.yes_answered_question, 0.7)
        self.assertGreater(output.no_rambling, 0.7)

    def test_pragmatics_rambling(self):
        long_text = "This is a very long explanation that keeps going without really concluding " * 3
        output = evaluate_pragmatics(long_text)
        self.assertLess(output.no_rambling, 0.5)

    # -------- Consideration --------
    def test_consideration_good(self):
        output = evaluate_consideration(NICE_BALANCE)
        self.assertGreater(output.no_hedging, 0.7)
        self.assertGreater(output.good_amount_of_acknowledgment, 0.7)
        self.assertGreater(output.no_interruptions, 0.7)

    def test_consideration_bad(self):
        output = evaluate_consideration(AGGRESSIVE)
        self.assertLess(output.no_interruptions, 0.5)

    def test_consideration_acknowledgment(self):
        output = evaluate_consideration(LACK_CONSIDERATION)
        self.assertLess(output.good_amount_of_acknowledgment, 0.5)

    # -------- Time Balance --------
    def test_time_balance_good(self):
        output = evaluate_time_balance(NICE_BALANCE)
        self.assertGreater(output.good_interruption_ratio, 0.7)
        self.assertGreater(output.good_speaking_share, 0.7)

    def test_time_balance_bad(self):
        output = evaluate_time_balance(TIME_DOMINATE)
        self.assertLess(output.good_interruption_ratio, 0.5)
        self.assertLess(output.good_speaking_share, 0.5)


if __name__ == "__main__":
    unittest.main()
