import asyncio
from deepgram import (
    DeepgramClient,
    PrerecordedOptions,
    FileSource,
)

import os
import base64
import json
from dotenv import load_dotenv

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

def transcribe_base64_audio(
    base64_audio: str,
    model: str = "nova-3",
    diarize: bool = True,
    filler_words: bool = True,
):
    if not DEEPGRAM_API_KEY:
        raise ValueError("DEEPGRAM_API_KEY is not set in the environment.")

    # Allow both raw base64 strings and data URLs like "data:audio/mp3;base64,..."
    if "," in base64_audio and "base64" in base64_audio[:64].lower():
        base64_audio = base64_audio.split(",", 1)[1]

    try:
        audio_bytes = base64.b64decode(base64_audio)
    except Exception as exc:
        raise ValueError("Invalid base64-encoded audio input.") from exc

    deepgram = DeepgramClient(DEEPGRAM_API_KEY)

    payload: FileSource = {
        "buffer": audio_bytes,
    }

    options = PrerecordedOptions(
        model=model,
        diarize=diarize,
        filler_words=filler_words,
    )

    response = deepgram.listen.rest.v("1").transcribe_file(payload, options)

    return json.loads(response.to_json())


def parse_speaker_transcript(deepgram_response: dict) -> str:
    try:
        words = deepgram_response["results"]["channels"][0]["alternatives"][0]["words"]
        
        if not words:
            return "No transcript available"
        speaker_segments = []
        current_speaker = None
        current_text = []
        
        for word_info in words:
            speaker = word_info.get("speaker", 0)
            word = word_info.get("word", "")
            if current_speaker is None:
                current_speaker = speaker
                current_text = [word]
            elif speaker == current_speaker:
                current_text.append(word)
            else:
                if current_text:
                    speaker_segments.append(f"Speaker {current_speaker}: {' '.join(current_text)}")
                current_speaker = speaker
                current_text = [word]
        
        if current_text and current_speaker is not None:
            speaker_segments.append(f"Speaker {current_speaker}: {' '.join(current_text)}")
        
        return "\n".join(speaker_segments)
        
    except (KeyError, IndexError, TypeError) as e:
        return f"Error parsing transcript: {e}"

async def transcribe_base64_audio_async(base64_audio: str):
    return await asyncio.to_thread(transcribe_base64_audio, base64_audio)

if __name__ == "__main__":
    with open("test.mp3", "rb") as file:
        base64_audio = base64.b64encode(file.read()).decode("utf-8")
    result = transcribe_base64_audio(base64_audio)
    print("Parsed Speaker Transcript:")
    print(parse_speaker_transcript(result))
