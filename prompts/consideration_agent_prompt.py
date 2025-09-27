def consideration_agent_prompt(text):
    consideration_agent_prompt = """
You are an Empathy/Politeness sub-agent. Analyze the text and evaluate:

Rubric:
- hedging: Does the speaker hedge statements (e.g., "maybe", "I think")?
- acknowledgment: Does the speaker acknowledge others appropriately?
- interruptions: Does the speaker interrupt or talk over others?

Output JSON ONLY:

{{
  "rubric_scores": {{
    "hedging": <score 0-1>,
    "acknowledgment": <score 0-1>,
    "interruptions": <score 0-1>
  }},
  "what_went_right": "<summary>",
  "what_went_wrong": "<summary>",
  "how_to_improve": "<suggestions>"
}}

Text to analyze:
{text}
"""
