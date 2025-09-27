from fastapi import FastAPI, File, UploadFile, HTTPException
import uvicorn
import sys
import os

import database

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import processors
from models import (
    TextUploadRequest, 
    TextUploadResponse, 
    ImageUploadResponse, 
    ErrorResponse,
    ReportFeedbackResponse,
)


app = FastAPI()

@app.post("/upload/text", response_model=TextUploadResponse)
async def upload_text(request: TextUploadRequest):
    try:
        processors.process_text(request.text)
        return TextUploadResponse(
            message="Text uploaded successfully",
            text_length=len(request.text)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                message="Error processing text",
                error=str(e)
            ).model_dump()
        )

@app.post("/upload/image", response_model=ImageUploadResponse)
async def upload_image(image: UploadFile = File(...)):
    try:
        processors.process_image(image)
        return ImageUploadResponse(
            message="Image uploaded successfully",
            filename=image.filename,
            size=image.size,
            content_type=image.content_type
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                message="Error processing image",
                error=str(e)
            ).model_dump()
        )

@app.get("/feedback/report")
async def report_feedback():
    try:
        recent_feedback = database.get_most_recent_entry()
        print(recent_feedback)
        if recent_feedback is None:
            return ReportFeedbackResponse(
                message="",
                last_updated=0
            )

        return ReportFeedbackResponse(
            message=recent_feedback[0],
            last_updated=int(recent_feedback[1])
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                message="Error reporting feedback",
                error=str(e)
            ).model_dump()
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
