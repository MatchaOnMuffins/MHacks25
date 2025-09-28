def fluency_agent_prompt(text: str) -> str:
    return f"""
Analyze the following text for Filler & Fluency:

\"\"\"{text}\"\"\"

Output **ONLY JSON** with the following structure, using keys exactly as shown:

Rubric scores must be floats between 0.0 and 1.0.

You MUST be as concise as possible. Be specific and to the point.

{{
  "filler_words": 0,0
  "rubric_scores": {{
    "filler_words": <score 0-1 where you rank how many filler words were used in comparision to the overall text where 1 is filler words are 10% of the text>,
    "run_ons": <score 0-1>,
    "wpm": <score 0-1>
  }},
  "what_went_right": "",
  "what_went_wrong": "",
  "how_to_improve": "",
  "prompt": "{text}"
}}
"""
