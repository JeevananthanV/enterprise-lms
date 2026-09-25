from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, ConfigDict


class ContentTypeEnum(str, Enum):
    TEXT = "TEXT"
    RICH_TEXT = "RICH_TEXT"
    VIDEO = "VIDEO"
    PDF = "PDF"
    TRANSCRIPT = "TRANSCRIPT"
    EXTERNAL_RESOURCE = "EXTERNAL_RESOURCE"


class VideoMetadata(BaseModel):
    video_url: str = Field(..., description="Object-storage reference or stream URL for video (e.g. s3://, https://)")
    duration_seconds: Optional[int] = Field(0, ge=0, description="Video duration in seconds")
    resolution: Optional[str] = Field("1080p", description="Video quality/resolution")
    provider: Optional[str] = Field("s3", description="Hosting provider: s3, gcs, vimeo, cdn, youtube, etc.")
    captions_url: Optional[str] = Field(None, description="URL to caption/subtitle track file")
    thumbnail_url: Optional[str] = Field(None, description="Video poster/thumbnail image URL")


class PdfMetadata(BaseModel):
    file_url: str = Field(..., description="Object-storage reference or secure CDN URL for document")
    file_name: str = Field(..., description="Display file name")
    file_size_bytes: Optional[int] = Field(None, ge=0, description="File size in bytes")
    page_count: Optional[int] = Field(None, ge=1, description="Number of pages")
    downloadable: bool = Field(True, description="Whether students can download the document")


class TranscriptData(BaseModel):
    language: str = Field("en", description="Language code (e.g., en, es, fr)")
    content: str = Field(..., description="Transcript text or WebVTT/SRT string")
    format: str = Field("text", description="Transcript format: text, vtt, srt")


class ExternalResource(BaseModel):
    title: str = Field(..., description="Resource display name")
    url: str = Field(..., description="External link URL")
    resource_type: str = Field("link", description="Resource type: link, repository, docs, tool")
    description: Optional[str] = Field(None, description="Brief resource overview")


class LessonContentBase(BaseModel):
    content_type: ContentTypeEnum = Field(ContentTypeEnum.TEXT, description="Content classification")
    body: Optional[str] = Field(None, description="Markdown, HTML, or raw text content")
    video_metadata: Optional[VideoMetadata] = None
    pdf_metadata: Optional[PdfMetadata] = None
    transcript: Optional[TranscriptData] = None
    external_resources: Optional[List[ExternalResource]] = Field(default_factory=list)
    custom_properties: Optional[Dict[str, Any]] = Field(default_factory=dict)


class LessonContentCreateRequest(LessonContentBase):
    pass


class LessonContentUpdateRequest(BaseModel):
    content_type: Optional[ContentTypeEnum] = None
    body: Optional[str] = None
    video_metadata: Optional[VideoMetadata] = None
    pdf_metadata: Optional[PdfMetadata] = None
    transcript: Optional[TranscriptData] = None
    external_resources: Optional[List[ExternalResource]] = None
    custom_properties: Optional[Dict[str, Any]] = None


class LessonContentResponse(BaseModel):
    id: str = Field(..., description="MongoDB Content Document ID")
    lesson_id: str = Field(..., description="PostgreSQL Lesson ID foreign reference")
    course_id: Optional[str] = Field(None, description="PostgreSQL Course ID reference")
    content_type: ContentTypeEnum
    body: Optional[str] = None
    video_metadata: Optional[VideoMetadata] = None
    pdf_metadata: Optional[PdfMetadata] = None
    transcript: Optional[TranscriptData] = None
    external_resources: List[ExternalResource] = Field(default_factory=list)
    custom_properties: Dict[str, Any] = Field(default_factory=dict)
    version: int = Field(1, description="Document revision version")
    is_published: bool = Field(False, description="Whether this content is published for students")
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
