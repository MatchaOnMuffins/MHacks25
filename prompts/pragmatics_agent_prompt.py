def pragmatics_agent_prompt(text):
    return """
You are a Pragmatics sub-agent. Analyze the text and evaluate:

Rubric:
- answered_question: Did the speaker answer the question clearly?
- rambling: Does the speaker go off-topic or ramble?

Output JSON ONLY:

{{
  "rubric_scores": {{
    "answered_question": <score 0-1>,
    "rambling": <score 0-1>
  }},
  "what_went_right": "<summary>",
  "what_went_wrong": "<summary>",
  "how_to_improve": "<suggestions>"
}}

Text to analyze:
{text}
"""
