import json
import time
from database import add_entry
from backend import run_workflow

async def process_text(text: str, timestamp: int):
    print(text)
    starting_time = int(time.time())
    result = await run_workflow(text)
    print(result["final_answer"])
    time_taken = int(time.time()) - starting_time
    print(f"Time taken: {time_taken} seconds")
    add_entry(result["final_answer"], json.dumps(result["sub_agent_reports"], indent=2), time_taken)
    