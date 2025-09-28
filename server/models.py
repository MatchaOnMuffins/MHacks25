from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TextUploadRequest(BaseModel):
    """Request model for text upload endpoint"""
    text: str = Field(..., min_length=1, description="Text content to process")
    secret_key: str = Field(..., description="Secret key to authenticate the request")
    timestamp: int = Field(..., description="Timestamp of the request")


class ImageUploadResponse(BaseModel):
    """Response model for image upload endpoint"""
    message: str
    filename: Optional[str] = None
    size: Optional[int] = None
    content_type: Optional[str] = None
    processed_at: datetime = Field(default_factory=datetime.now)


class TextUploadResponse(BaseModel):
    """Response model for text upload endpoint"""
    message: str
    text_length: Optional[int] = None
    processed_at: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """Error response model"""
    message: str
    error: str
    timestamp: datetime = Field(default_factory=datetime.now)


class SuccessResponse(BaseModel):
    """Generic success response model"""
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ReportFeedbackResponse(BaseModel):
    """Response model for feedback report endpoint"""
    message: str
    last_updated: int 