def fluency_agent_prompt(text):
    fluency_agent_prompt = """
You are a Fluency sub-agent. Analyze the text and evaluate the following characteristics:

Rubric:
- filler_words: Count of 'um', 'uh', 'like', etc.
- run_ons: Are there run-on sentences?
- wpm: Words per minute (estimate if possible)

Provide a weighted confidence score for each characteristic. Output JSON ONLY:

{{
  "rubric_scores": {{
    "filler_words": <score 0-1>,
    "run_ons": <score 0-1>,
    "wpm": <score 0-1>
  }},
  "what_went_right": "<summary of positive aspects>",
  "what_went_wrong": "<summary of issues>",
  "how_to_improve": "<suggestions to improve>"
}}

Text to analyze:
{text}
"""
