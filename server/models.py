from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class TextUploadRequest(BaseModel):
    """Request model for text upload endpoint"""
    text: str = Field(..., min_length=1, description="Text content to process")


class ImageUploadResponse(BaseModel):
    """Response model for image upload endpoint"""
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    message: str
    filename: Optional[str] = None
    size: Optional[int] = None
    content_type: Optional[str] = None
    processed_at: datetime = Field(default_factory=datetime.now)


class TextUploadResponse(BaseModel):
    """Response model for text upload endpoint"""
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    message: str
    text_length: Optional[int] = None
    processed_at: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """Error response model"""
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    message: str
    error: str
    timestamp: datetime = Field(default_factory=datetime.now)


class SuccessResponse(BaseModel):
    """Generic success response model"""
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})
    
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
