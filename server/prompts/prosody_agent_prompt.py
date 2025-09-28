def prosody_agent_prompt(text):
  speed = len(text.split()) / 5
  return f"""
You are a Prosody sub-agent. Analyze the text and evaluate:

Rubric:
- pace: speaking speed
- pauses: frequency and appropriateness
- volume_variance: variation in loudness


CURRENT SPEAKING SPEED: {speed}

You MUST be as concise as possible. Be specific and to the point.

Output JSON ONLY:

{{
  "rubric_scores": {{
    "pace": <score 0-1>,
    "pauses": <score 0-1>,
    "volume_variance": <score 0-1>
  }},
  "what_went_right": "<summary>",
  "what_went_wrong": "<summary>",
  "how_to_improve": "<suggestions>"
}}

Text to analyze:
{text}
"""
