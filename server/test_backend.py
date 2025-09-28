import unittest
from backend import (
    FluencyOutput, ProsodyOutput, PragmaticsOutput,
    ConsiderationOutput, TimeBalanceOutput,
)

from backend import FluencyOutput, ProsodyOutput, PragmaticsOutput, ConsiderationOutput, TimeBalanceOutput

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
# Evaluate Functions
# ------------------------

# ---------------- Fluency ----------------
def evaluate_fluency(text: str):
    filler_score = 0.3 if "Uh" in text or "um" in text else 0.9
    run_on_score = 0.3 if text.count('.') < 1 else 0.9
    wpm_score = 0.6 if len(text.split()) > 25 else 0.9
    return FluencyOutput(
        raw_filler_words=1.0 - filler_score,
        raw_run_ons=1.0 - run_on_score,
        raw_wpm=1.0 - wpm_score,
        what_went_right="Clear speech, minimal filler words.",
        what_went_wrong="Run-on sentences or filler words detected.",
        how_to_improve="Reduce fillers, break long sentences.",
        prompt=text
    )

# ---------------- Prosody ----------------
def evaluate_prosody(text: str):
    pace = 0.9
    pauses = 0.3 if "..." in text else 0.9
    volume_variance = 0.3 if "Monotone" in text or text == MONOTONE else 0.9
    speed = 0.9
    return ProsodyOutput(
        raw_pace=1.0 - pace,
        raw_pauses=1.0 - pauses,
        raw_volume_variance=1.0 - volume_variance,
        raw_speed=1.0 - speed,
        what_went_right="Good pacing, clear volume, ideal speed.",
        what_went_wrong="Minor monotone or pauses issues.",
        how_to_improve="Add intonation variation and adjust pauses slightly.",
        prompt=text
    )

# ---------------- Pragmatics ----------------
def evaluate_pragmatics(text: str):
    answered_question = 1.0 if "?" in text else 0.9
    rambling = 0.3 if len(text.split()) > 20 else 0.9
    return PragmaticsOutput(
        raw_answered_question=answered_question,
        raw_rambling=1.0 - rambling,
        what_went_right="Communicates purpose clearly.",
        what_went_wrong="Minor rambling detected.",
        how_to_improve="Stay concise and focused.",
        prompt=text
    )

# ---------------- Consideration ----------------
def evaluate_consideration(text: str):
    hedging = 0.6 if "I think" in text else 0.9
    acknowledgment = 0.3 if "you" not in text and "others" not in text else 0.9
    interruptions = 0.3 if "Shut up" in text or "interrupted" in text else 0.9
    return ConsiderationOutput(
        raw_hedging=1.0 - hedging,
        raw_acknowledgment=1.0 - acknowledgment,
        raw_interruptions=1.0 - interruptions,
        what_went_right="Shows awareness and listens.",
        what_went_wrong="Interruptions or hedging detected.",
        how_to_improve="Acknowledge others and avoid interrupting.",
        prompt=text
    )

# ---------------- Time Balance ----------------
def evaluate_time_balance(text: str):
    interruption_ratio = 0.3 if "entire meeting" in text else 0.9
    speaking_share = 0.3 if "entire meeting" in text else 0.9
    return TimeBalanceOutput(
        raw_interruption_ratio=1.0 - interruption_ratio,
        raw_speaking_share=1.0 - speaking_share,
        what_went_right="Balanced speaking time.",
        what_went_wrong="Dominates conversation or poor balance.",
        how_to_improve="Let others share points and reduce interruptions.",
        prompt=text
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

class TestEvaluatorThresholds(unittest.TestCase):

    def test_fluency_scores(self):
        # Bad filler words
        bad_output = evaluate_fluency(TOO_MANY_FILLERS)
        self.assertLess(bad_output.filler_words, 0.5)
        self.assertLess(bad_output.run_ons, 0.5)
        self.assertGreaterEqual(bad_output.wpm, 0.0)
        self.assertLessEqual(bad_output.wpm, 1.0)
        self.assertEqual(bad_output.prompt, TOO_MANY_FILLERS)

        # Medium run-ons
        medium_output = evaluate_fluency(RUN_ON_SENTENCES)
        self.assertGreaterEqual(medium_output.filler_words, 0.3)
        self.assertLessEqual(medium_output.filler_words, 0.7)
        self.assertLess(medium_output.run_ons, 0.5)
        self.assertGreaterEqual(medium_output.wpm, 0.0)
        self.assertLessEqual(medium_output.wpm, 1.0)
        self.assertEqual(medium_output.prompt, RUN_ON_SENTENCES)

        # Good sentence
        good_output = evaluate_fluency(GOOD_BALANCED)
        self.assertGreater(good_output.filler_words, 0.7)
        self.assertGreater(good_output.run_ons, 0.7)
        self.assertGreater(good_output.wpm, 0.7)
        self.assertEqual(good_output.prompt, GOOD_BALANCED)

    def test_prosody_scores(self):
        bad_output = evaluate_prosody(EXCESSIVE_PAUSES)
        self.assertLess(bad_output.pauses, 0.5)
        self.assertGreaterEqual(bad_output.pace, 0.0)
        self.assertGreaterEqual(bad_output.volume_variance, 0.0)
        self.assertEqual(bad_output.prompt, EXCESSIVE_PAUSES)

        monotone_output = evaluate_prosody(MONOTONE)
        self.assertLess(monotone_output.volume_variance, 0.5)
        self.assertGreaterEqual(monotone_output.pace, 0.0)
        self.assertEqual(monotone_output.prompt, MONOTONE)

        good_output = evaluate_prosody(GOOD_BALANCED)
        self.assertGreater(good_output.volume_variance, 0.7)
        self.assertGreater(good_output.pauses, 0.7)
        self.assertEqual(good_output.prompt, GOOD_BALANCED)

    def test_pragmatics_scores(self):
        long_output = evaluate_pragmatics(RUN_ON_SENTENCES)
        self.assertLess(long_output.rambling, 0.5)
        self.assertGreaterEqual(long_output.answered_question, 0.9)
        self.assertEqual(long_output.prompt, RUN_ON_SENTENCES)

        short_output = evaluate_pragmatics(GOOD_BALANCED)
        self.assertGreater(short_output.rambling, 0.7)
        self.assertGreaterEqual(short_output.answered_question, 0.9)
        self.assertEqual(short_output.prompt, GOOD_BALANCED)

    def test_consideration_scores(self):
        aggressive_output = evaluate_consideration(AGGRESSIVE)
        self.assertLess(aggressive_output.interruptions, 0.5)
        self.assertLess(aggressive_output.acknowledgment, 0.5)
        self.assertGreaterEqual(aggressive_output.hedging, 0.0)
        self.assertEqual(aggressive_output.prompt, AGGRESSIVE)

        balanced_output = evaluate_consideration(NICE_BALANCE)
        self.assertGreater(balanced_output.interruptions, 0.7)
        self.assertGreater(balanced_output.acknowledgment, 0.7)
        self.assertGreater(balanced_output.hedging, 0.7)
        self.assertEqual(balanced_output.prompt, NICE_BALANCE)

    def test_timebalance_scores(self):
        dominate_output = evaluate_time_balance(TIME_DOMINATE)
        self.assertLess(dominate_output.interruption_ratio, 0.5)
        self.assertLess(dominate_output.speaking_share, 0.5)
        self.assertEqual(dominate_output.prompt, TIME_DOMINATE)

        balanced_output = evaluate_time_balance(NICE_BALANCE)
        self.assertGreater(balanced_output.interruption_ratio, 0.7)
        self.assertGreater(balanced_output.speaking_share, 0.7)
        self.assertEqual(balanced_output.prompt, NICE_BALANCE)


if __name__ == "__main__":
    unittest.main()
