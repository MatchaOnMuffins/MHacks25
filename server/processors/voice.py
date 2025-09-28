import json
import time
from transcribe_deepgram import parse_speaker_transcript, transcribe_base64_audio

from database import add_entry
from backend import run_workflow

async def process_voice(base64_audio: str, timestamp: int):
    print("Processing voice...")
    starting_time = int(time.time())
    transcription_result = transcribe_base64_audio(base64_audio)
    parsed_result = parse_speaker_transcript(transcription_result)
    print(parsed_result)
    result = await run_workflow(parsed_result)
    print(result["final_answer"])
    time_taken = int(time.time()) - starting_time
    print(f"Time taken: {time_taken} seconds")
    add_entry(result["final_answer"], json.dumps(result["sub_agent_reports"], indent=2), time_taken, parsed_result)
