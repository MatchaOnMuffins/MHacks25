def router_agent_prompt(text, categories):
    return f"""
You are a router agent responsible for dispatching your subagents, each of which is tied to a category out of: {categories}.

You MUST be as concise as possible. Be specific and to the point.

Your task:
1. Carefully read the input text: "{text}".
2. For each category, decide if it is present in the text:
   - **Fluency**: Look for filler words ("um", "like"), overly long sentences, or fast word-per-minute pace.
   - **Prosody**: Look for indicators of pace, pauses, or volume changes.
   - **Pragmatics**: Check if the speaker answered the question directly, or if they rambled.
   - **Consideration**: Look for hedging ("maybe", "I think"), acknowledgments ("yeah", "right"), or interruptions.
   - **Time-Balance** (if multiple speakers): Look for overlaps, interruptions, or imbalance in speaking time.

3. Output:
   - A list of the categories that apply.
   - For each selected category, specify which agent should be called in the format:
     CALL <Category> Agent
   - If none apply, output: "No category agents need to be called."

Example Output:
Categories Detected: [Filler & Fluency, Pragmatics]
Agents to Call:
CALL Filler & Fluency Agent
CALL Pragmatics Agent
"""
