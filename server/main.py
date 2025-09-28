import asyncio
from fastapi import FastAPI, File, Query, UploadFile, HTTPException
import uvicorn
import sys
import os
import dotenv

dotenv.load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")


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

app = FastAPI(
    title="Speech Analysis API",
    description="AI-powered speech pattern and communication skills analysis system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

def authenticate_request(secret_key: str):
    if secret_key != SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid secret key")

@app.post("/upload/text", response_model=TextUploadResponse)
async def upload_text(request: TextUploadRequest):
    """
    Upload and analyze text for speech pattern evaluation.
    
    This endpoint accepts text input (typically speech transcripts) and processes it through
    a multi-agent AI system to analyze various aspects of communication skills.
    
    **Analysis Categories:**
    - **FLUENCY**: Detects filler words (um, uh, like), run-on sentences, and speech pace (WPM)
    - **PROSODY**: Analyzes pace, pauses, and volume variance in speech patterns
    - **PRAGMATICS**: Evaluates whether questions were answered and detects rambling
    - **CONSIDERATION**: Measures hedging, acknowledgment, and interruption patterns
    - **TIME_BALANCE**: Assesses interruption ratio and speaking time distribution
    
    **Processing Workflow:**
    1. Router Agent determines which analysis categories apply to the input
    2. Relevant Sub-Agents analyze specific aspects and provide scores (0-1 scale)
    3. Synthesizer Agent combines all reports into a coherent summary
    4. Results are stored in the database for later retrieval
    
    **Request Body:**
    - `text` (string, required): The text content to analyze (minimum 1 character)
    - `secret_key` (string, required): Secret key for authentication
    
    **Response:**
    - `message`: Success confirmation message
    - `text_length`: Length of the processed text
    - `processed_at`: Timestamp when the request was processed
    
    **Example Request:**
    ```json
    {
        "text": "Um, I think, like, the project went well. We had some interruptions but overall good results.",
        "secret_key": "your-secret-key"
    }
    ```
    
    **Example Response:**
    ```json
    {
        "message": "Text uploaded successfully",
        "text_length": 95,
        "processed_at": "2025-09-28T10:30:00"
    }
    ```
    
    **Error Responses:**
    - `403 Forbidden`: Invalid or missing secret key
    - `500 Internal Server Error`: Processing failed due to AI model issues or system errors
    
    **Note:** Processing happens asynchronously. Use the `/feedback/report` endpoint to retrieve analysis results.
    """
    authenticate_request(request.secret_key)
    
    try:
        asyncio.create_task(processors.process_text(request.text))
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
async def upload_image(image: UploadFile = File(...), secret_key: str = Query(...)):
    """
    Upload and process image files (currently a placeholder endpoint).
    
    This endpoint accepts image file uploads for future processing capabilities.
    Currently, the image processing functionality is not fully implemented and
    serves as a placeholder for potential future features such as:
    
    **Potential Future Features:**
    - Visual speech analysis from video frames
    - Gesture and body language analysis
    - Facial expression recognition during speech
    - Visual presentation skills evaluation
    
    **Current Implementation:**
    - Accepts any image file upload
    - Logs the file information
    - Returns basic file metadata
    - No actual image processing occurs
    
    **Supported File Types:**
    - Any file type accepted by FastAPI's UploadFile
    - Recommended: JPEG, PNG, GIF, WebP
    
    **Request:**
    - Multipart form data with image file
    - File parameter name: `image`
    
    **Response:**
    - `message`: Success confirmation message
    - `filename`: Original filename of the uploaded image
    - `size`: File size in bytes (if available)
    - `content_type`: MIME type of the uploaded file
    - `processed_at`: Timestamp when the request was processed
    
    **Example Response:**
    ```json
    {
        "message": "Image uploaded successfully",
        "filename": "presentation_screenshot.png",
        "size": 245760,
        "content_type": "image/png",
        "processed_at": "2025-09-28T10:30:00"
    }
    ```
    
    **Error Responses:**
    - `500 Internal Server Error`: File processing failed
    
    **Usage Example (curl):**
    ```bash
    curl -X POST "http://localhost:8000/upload/image" \
         -H "accept: application/json" \
         -H "Content-Type: multipart/form-data" \
         -F "image=@/path/to/your/image.png"
    ```
    """
    authenticate_request(secret_key)
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

@app.get("/feedback/report", response_model=ReportFeedbackResponse)
async def report_feedback():
    """
    Retrieve the most recent speech analysis feedback report.
    
    This endpoint returns the latest analysis results from the text processing workflow.
    After uploading text via `/upload/text`, the AI analysis system processes the input
    asynchronously and stores the results in a SQLite database. This endpoint retrieves
    the most recently completed analysis.
    
    **Analysis Report Contents:**
    The returned message contains a synthesized summary that may include:
    - Overall communication effectiveness assessment
    - Specific scores for different speech categories (0-1 scale)
    - Identified strengths in communication patterns
    - Areas for improvement with actionable recommendations
    - Detailed feedback on fluency, prosody, pragmatics, consideration, and time balance
    
    **Database Storage:**
    - Results are stored in SQLite database (`database/feedback.db`)
    - Each entry includes feedback text and Unix timestamp
    - Only the most recent entry is returned by this endpoint
    
    **Response Fields:**
    - `message`: The complete analysis feedback text (empty string if no data)
    - `last_updated`: Unix timestamp of when the analysis was completed (0 if no data)
    
    **Response Examples:**
    
    **With Data:**
    ```json
    {
        "message": "Analysis Summary: Your speech shows good fluency with minimal filler words (score: 0.8). However, there were several interruptions detected (score: 0.4). Consider practicing active listening and allowing others to complete their thoughts. Overall communication effectiveness: 7.2/10.",
        "last_updated": 1695902400
    }
    ```
    
    **No Data Available:**
    ```json
    {
        "message": "",
        "last_updated": 0
    }
    ```
    
    **Error Responses:**
    - `500 Internal Server Error`: Database access failed or system error
    
    **Usage Notes:**
    - This endpoint should be called after submitting text for analysis
    - Results may take several seconds to appear due to AI processing time
    - Only the most recent analysis is available; historical data is not exposed via API
    - Consider implementing polling or webhooks for real-time updates in production
    
    **Usage Example (curl):**
    ```bash
    curl -X GET "http://localhost:8000/feedback/report" \
         -H "accept: application/json"
    ```
    """
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
