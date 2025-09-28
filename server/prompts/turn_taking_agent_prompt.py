def turn_taking_agent_prompt(text):
    return """
You are a Turn-Taking sub-agent. Analyze the text and evaluate:

Rubric:
- interruption_ratio: Frequency of interruptions
- speaking_share: Share of speaking time for each speaker

You MUST be as concise as possible. Be specific and to the point.

Output JSON ONLY:

{{
  "rubric_scores": {{
    "interruption_ratio": <score 0-1>,
    "speaking_share": <score 0-1>,
  }},
  "what_went_right": "<summary>",
  "what_went_wrong": "<summary>",
  "how_to_improve": "<suggestions>"
}}

Text to analyze:
{text}
"""
