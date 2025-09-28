import unittest
from pydantic import BaseModel, Field
from typing import Dict
import random

# ---------------------------
# Output Models
# ---------------------------

class FluencyOutput(BaseModel):
    raw_filler_words: float = Field(..., ge=0.0, le=1.0)
    raw_run_ons: float = Field(..., ge=0.0, le=1.0)
    raw_wpm: float = Field(..., ge=0.0, le=1.0)

    what_went_right: str
    what_went_wrong: str
    how_to_improve: str
    prompt: str

    @property
    def filler_words(self) -> float:
        return 1.0 - self.raw_filler_words

    @property
    def run_ons(self) -> float:
        return 1.0 - self.raw_run_ons

    @property
    def wpm(self) -> float:
        return 1.0 - self.raw_wpm

    @property
    def rubric_scores(self) -> Dict[str, float]:
        return {
            "lack_of_filler_words": self.filler_words,
            "lack_of_run_ons": self.run_ons,
            "good_wpm": self.wpm
        }


class ProsodyOutput(BaseModel):
    raw_pace: float = Field(..., ge=0.0, le=1.0)
    raw_pauses: float = Field(..., ge=0.0, le=1.0)
    raw_volume_variance: float = Field(..., ge=0.0, le=1.0)
    raw_speed: float = Field(..., ge=0.0, le=1.0)

    what_went_right: str
    what_went_wrong: str
    how_to_improve: str
    prompt: str

    @property
    def pace(self) -> float:
        return 1.0 - self.raw_pace

    @property
    def pauses(self) -> float:
        return 1.0 - self.raw_pauses

    @property
    def volume_variance(self) -> float:
        return 1.0 - self.raw_volume_variance

    @property
    def speed(self) -> float:
        return 1.0 - self.raw_speed

    @property
    def rubric_scores(self) -> Dict[str, float]:
        return {
            "good_pace": self.speed,
            "lack_of_pauses": self.pauses,
            "good_volume_variance": self.volume_variance
        }


class PragmaticsOutput(BaseModel):
    raw_answered_question: float = Field(..., ge=0.0, le=1.0)
    raw_rambling: float = Field(..., ge=0.0, le=1.0)

    what_went_right: str
    what_went_wrong: str
    how_to_improve: str
    prompt: str

    @property
    def answered_question(self) -> float:
        return self.raw_answered_question

    @property
    def rambling(self) -> float:
        return 1.0 - self.raw_rambling

    @property
    def rubric_scores(self) -> Dict[str, float]:
        return {
            "yes_answered_question": self.answered_question,
            "no_rambling": self.rambling
        }


class ConsiderationOutput(BaseModel):
    raw_hedging: float = Field(..., ge=0.0, le=1.0)
    raw_acknowledgment: float = Field(..., ge=0.0, le=1.0)
    raw_interruptions: float = Field(..., ge=0.0, le=1.0)

    what_went_right: str
    what_went_wrong: str
    how_to_improve: str
    prompt: str

    @property
    def hedging(self) -> float:
        return 1.0 - self.raw_hedging

    @property
    def acknowledgment(self) -> float:
        return self.raw_acknowledgment

    @property
    def interruptions(self) -> float:
        return 1.0 - self.raw_interruptions

    @property
    def rubric_scores(self) -> Dict[str, float]:
        return {
            "no_hedging": self.hedging,
            "good_amount_of_acknowledgment": self.acknowledgment,
            "no_interruptions": self.interruptions
        }


class TimeBalanceOutput(BaseModel):
    raw_interruption_ratio: float = Field(..., ge=0.0, le=1.0)
    raw_speaking_share: float = Field(..., ge=0.0, le=1.0)

    what_went_right: str
    what_went_wrong: str
    how_to_improve: str
    prompt: str

    @property
    def interruption_ratio(self) -> float:
        return 1.0 - self.raw_interruption_ratio

    @property
    def speaking_share(self) -> float:
        return 1.0 - self.raw_speaking_share

    @property
    def rubric_scores(self) -> Dict[str, float]:
        return {
            "good_interruption_ratio": self.interruption_ratio,
            "good_speaking_share": self.speaking_share
        }


# ---------------------------
# Unit Tests
# ---------------------------

class TestAgentOutputs(unittest.TestCase):

    # Example sentences for testing different ranges
    def setUp(self):
        self.fluency_examples = [
            FluencyOutput(raw_filler_words=0.7, raw_run_ons=0.6, raw_wpm=0.5,
                          what_went_right="Some filler words", what_went_wrong="Some run-ons", how_to_improve="Speak slower", prompt="Example prompt"),
            FluencyOutput(raw_filler_words=0.3, raw_run_ons=0.4, raw_wpm=0.3,
                          what_went_right="Few filler words", what_went_wrong="Some run-ons", how_to_improve="Pace is medium", prompt="Example prompt"),
            FluencyOutput(raw_filler_words=0.1, raw_run_ons=0.0, raw_wpm=0.1,
                          what_went_right="Almost perfect", what_went_wrong="Minor issue", how_to_improve="Keep up", prompt="Example prompt")
        ]

        self.prosody_examples = [
            ProsodyOutput(raw_pace=0.8, raw_pauses=0.7, raw_volume_variance=0.6, raw_speed=0.5,
                          what_went_right="Bad pace", what_went_wrong="Bad pauses", how_to_improve="Adjust tone", prompt="Example"),
            ProsodyOutput(raw_pace=0.3, raw_pauses=0.4, raw_volume_variance=0.2, raw_speed=0.3,
                          what_went_right="Medium pace", what_went_wrong="Some variation", how_to_improve="Better", prompt="Example"),
            ProsodyOutput(raw_pace=0.0, raw_pauses=0.1, raw_volume_variance=0.0, raw_speed=0.0,
                          what_went_right="Excellent", what_went_wrong="", how_to_improve="", prompt="Example")
        ]

        self.pragmatics_examples = [
            PragmaticsOutput(raw_answered_question=0.3, raw_rambling=0.6,
                             what_went_right="Partially answered", what_went_wrong="Rambled some", how_to_improve="Focus answers", prompt="Example"),
            PragmaticsOutput(raw_answered_question=0.7, raw_rambling=0.3,
                             what_went_right="Mostly answered", what_went_wrong="Minimal rambling", how_to_improve="Keep concise", prompt="Example"),
            PragmaticsOutput(raw_answered_question=1.0, raw_rambling=0.0,
                             what_went_right="Perfect answer", what_went_wrong="", how_to_improve="", prompt="Example")
        ]

        self.consideration_examples = [
            ConsiderationOutput(raw_hedging=0.7, raw_acknowledgment=0.3, raw_interruptions=0.5,
                                what_went_right="Some hedging", what_went_wrong="Few acknowledgments", how_to_improve="Be clear", prompt="Example"),
            ConsiderationOutput(raw_hedging=0.3, raw_acknowledgment=0.7, raw_interruptions=0.2,
                                what_went_right="Medium hedging", what_went_wrong="Good acknowledgment", how_to_improve="Less interruptions", prompt="Example"),
            ConsiderationOutput(raw_hedging=0.0, raw_acknowledgment=1.0, raw_interruptions=0.0,
                                what_went_right="No hedging", what_went_wrong="", how_to_improve="", prompt="Example")
        ]

        self.timebalance_examples = [
            TimeBalanceOutput(raw_interruption_ratio=0.7, raw_speaking_share=0.5,
                              what_went_right="Interrupts sometimes", what_went_wrong="Speaks too much", how_to_improve="Balance speaking", prompt="Example"),
            TimeBalanceOutput(raw_interruption_ratio=0.3, raw_speaking_share=0.3,
                              what_went_right="Good ratio", what_went_wrong="Moderate speaking", how_to_improve="Fine tune", prompt="Example"),
            TimeBalanceOutput(raw_interruption_ratio=0.0, raw_speaking_share=0.1,
                              what_went_right="Perfect ratio", what_went_wrong="", how_to_improve="", prompt="Example")
        ]

    # ---------------------------
    # Range-based checks
    # ---------------------------
    def test_fluency_ranges(self):
        for f in self.fluency_examples:
            # filler words
            if f.raw_filler_words > 0.6:  # bad
                self.assertLess(f.filler_words, 0.5)
            elif 0.2 < f.raw_filler_words < 0.6:  # medium
                self.assertGreaterEqual(f.filler_words, 0.3)
                self.assertLessEqual(f.filler_words, 0.7)
            else:  # good
                self.assertGreater(f.filler_words, 0.7)

            # run-ons
            if f.raw_run_ons > 0.6:
                self.assertLess(f.run_ons, 0.5)
            elif 0.2 < f.raw_run_ons < 0.6:
                self.assertGreaterEqual(f.run_ons, 0.3)
                self.assertLessEqual(f.run_ons, 0.7)
            else:
                self.assertGreater(f.run_ons, 0.7)

            # wpm
            self.assertGreaterEqual(f.wpm, 0.0)
            self.assertLessEqual(f.wpm, 1.0)
                        
    def test_prosody_ranges(self):
        for p in self.prosody_examples:
            self.assertGreaterEqual(p.pace, 0.0)
            self.assertLessEqual(p.pace, 1.0)
            self.assertGreaterEqual(p.pauses, 0.0)
            self.assertLessEqual(p.pauses, 1.0)
            self.assertGreaterEqual(p.volume_variance, 0.0)
            self.assertLessEqual(p.volume_variance, 1.0)
            self.assertGreaterEqual(p.speed, 0.0)
            self.assertLessEqual(p.speed, 1.0)

    def test_pragmatics_ranges(self):
        for pr in self.pragmatics_examples:
            self.assertGreaterEqual(pr.answered_question, 0.0)
            self.assertLessEqual(pr.answered_question, 1.0)
            self.assertGreaterEqual(pr.rambling, 0.0)
            self.assertLessEqual(pr.rambling, 1.0)

    def test_consideration_ranges(self):
        for c in self.consideration_examples:
            self.assertGreaterEqual(c.hedging, 0.0)
            self.assertLessEqual(c.hedging, 1.0)
            self.assertGreaterEqual(c.acknowledgment, 0.0)
            self.assertLessEqual(c.acknowledgment, 1.0)
            self.assertGreaterEqual(c.interruptions, 0.0)
            self.assertLessEqual(c.interruptions, 1.0)

    def test_timebalance_ranges(self):
        for t in self.timebalance_examples:
            self.assertGreaterEqual(t.interruption_ratio, 0.0)
            self.assertLessEqual(t.interruption_ratio, 1.0)
            self.assertGreaterEqual(t.speaking_share, 0.0)
            self.assertLessEqual(t.speaking_share, 1.0)


if __name__ == "__main__":
    unittest.main()
