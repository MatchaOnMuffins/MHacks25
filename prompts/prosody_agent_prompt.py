def prosody_agent_prompt(text):
    prosody_agent_prompt = f"""
You are a Prosody sub-agent. Analyze the text and evaluate:

Rubric:
- pace: speaking speed
- pauses: frequency and appropriateness
- volume_variance: variation in loudness

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
