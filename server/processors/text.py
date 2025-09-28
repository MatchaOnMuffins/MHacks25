from database import add_entry
from backend import run_workflow

async def process_text(text: str):
    print(text)
    result = await run_workflow(text)
    print(result["final_answer"])
    add_entry(result["final_answer"])