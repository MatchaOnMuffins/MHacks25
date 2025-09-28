import unittest
import asyncio
from backend import (
    FluencyOutput, ProsodyOutput, PragmaticsOutput,
    ConsiderationOutput, TimeBalanceOutput, run_workflow
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


class AsyncTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_run_workflow_scores(self):
        # Test GOOD_BALANCED
        result = await run_workflow(GOOD_BALANCED)
        self.assertGreaterEqual(result['total_score'], 0.8)
        self.assertLessEqual(result['total_score'], 1.0)

        # Test TOO_MANY_FILLERS
        result = await run_workflow(TOO_MANY_FILLERS)
        self.assertGreaterEqual(result['total_score'], 0.3)
        self.assertLessEqual(result['total_score'], 0.6)

        # Test RUN_ON_SENTENCES
        result = await run_workflow(RUN_ON_SENTENCES)
        self.assertGreaterEqual(result['total_score'], 0.4)
        self.assertLessEqual(result['total_score'], 0.7)

        # Test EXCESSIVE_PAUSES
        result = await run_workflow(EXCESSIVE_PAUSES)
        self.assertGreaterEqual(result['total_score'], 0.3)
        self.assertLessEqual(result['total_score'], 0.6)

        # Test MONOTONE
        result = await run_workflow(MONOTONE)
        self.assertGreaterEqual(result['total_score'], 0.3)
        self.assertLessEqual(result['total_score'], 0.6)

        # Test AGGRESSIVE
        result = await run_workflow(AGGRESSIVE)
        self.assertGreaterEqual(result['total_score'], 0.2)
        self.assertLessEqual(result['total_score'], 0.5)

        # Test LACK_CONSIDERATION
        result = await run_workflow(LACK_CONSIDERATION)
        self.assertGreaterEqual(result['total_score'], 0.2)
        self.assertLessEqual(result['total_score'], 0.5)

        # Test TIME_DOMINATE
        result = await run_workflow(TIME_DOMINATE)
        self.assertGreaterEqual(result['total_score'], 0.2)
        self.assertLessEqual(result['total_score'], 0.5)

        # Test NICE_BALANCE
        result = await run_workflow(NICE_BALANCE)
        self.assertGreaterEqual(result['total_score'], 0.8)
        self.assertLessEqual(result['total_score'], 1.0)


if __name__ == "__main__":
    unittest.main()